# helix_box_bridge.py - make HelixScreen slot edits reach the QIDI Box on Q2 firmware 1.1.x
#
# HelixScreen saves a slot edit as legacy numeric save_variables:
#     SAVE_VARIABLE VARIABLE=filament_slot0 VALUE=1
#     SAVE_VARIABLE VARIABLE=color_slot0 VALUE=2
#     SAVE_VARIABLE VARIABLE=vendor_slot0 VALUE=0
# The Box firmware (multi_color_controller) only follows edits made with
#     UPDATE_FILAMENT_INFORMATION SLOT=0 COLOR='060606' VENDOR='QIDI' FILAMENT='PLA Basic'
# (what the stock screen, QIDI Studio and the patched Fluidd Box panel send).
# Numeric writes leave the Box showing "PLA Basic #FAFAFA" in Fluidd.
#
# This module catches numeric SAVE_VARIABLE writes to filament_slotN / color_slotN /
# vendor_slotN, turns the ids into names with officiall_filas_list.cfg and sends one
# UPDATE_FILAMENT_INFORMATION per slot instead. Fields Helix did not send keep the
# Box's current value. Every other SAVE_VARIABLE runs unchanged.
#
# Install: copy to ~/klipper/klippy/extras/, add [helix_box_bridge] to printer.cfg, RESTART.
# Remove:  delete the [helix_box_bridge] section, RESTART.

import configparser
import logging
import os
import re

SLOT_VAR = re.compile(r'^(filament|color|vendor)_slot(\d+)$')
SLOTS_PER_BOX = 4


class HelixBoxBridge:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.reactor = self.printer.get_reactor()
        self.gcode = self.printer.lookup_object('gcode')
        cfg_dir = os.path.dirname(
            self.printer.get_start_args().get('config_file', '')) or \
            os.path.expanduser('~/printer_data/config')
        self.filas_path = config.get(
            'filas_list', os.path.join(cfg_dir, 'officiall_filas_list.cfg'))
        self.delay = config.getfloat('delay', 0.3, minval=0.05)
        self.pending = {}
        self.timer = None
        self.orig_save_variable = None
        self.printer.register_event_handler('klippy:connect', self._connect)

    def _connect(self):
        if 'SAVE_VARIABLE' not in self.gcode.ready_gcode_handlers and \
                'SAVE_VARIABLE' not in self.gcode.base_gcode_handlers:
            logging.info('helix_box_bridge: SAVE_VARIABLE not found, bridge off')
            return
        self.orig_save_variable = self.gcode.register_command('SAVE_VARIABLE', None)
        self.gcode.register_command(
            'SAVE_VARIABLE', self.cmd_SAVE_VARIABLE,
            desc='Save arbitrary variables to disk (helix_box_bridge: '
                 'numeric Box slot writes go to UPDATE_FILAMENT_INFORMATION)')
        logging.info('helix_box_bridge: active, list %s', self.filas_path)

    # ------------------------------------------------------------------
    def cmd_SAVE_VARIABLE(self, gcmd):
        name = gcmd.get('VARIABLE', '')
        value = gcmd.get('VALUE', '').strip()
        m = SLOT_VAR.match(name)
        if m is None or not value.isdigit():
            return self.orig_save_variable(gcmd)
        kind, slot = m.group(1), int(m.group(2))
        if slot >= 16:  # slot16 is the external rack spool, not a Box slot
            return self.orig_save_variable(gcmd)
        self.pending.setdefault(slot, {})[kind] = int(value)
        if self.timer is None:
            self.timer = self.reactor.register_timer(
                self._flush, self.reactor.monotonic() + self.delay)

    def _flush(self, eventtime):
        self.reactor.unregister_timer(self.timer)
        self.timer = None
        pending, self.pending = self.pending, {}
        tables = self._load_tables()
        for slot, ids in sorted(pending.items()):
            try:
                script = self._build(slot, ids, tables, eventtime)
            except Exception as e:
                logging.exception('helix_box_bridge: slot %d', slot)
                self.gcode.respond_info('helix_box_bridge: slot %d not updated: %s'
                                        % (slot, e))
                continue
            logging.info('helix_box_bridge: %r -> %s', ids, script)
            try:
                self.gcode.run_script(script)
            except Exception as e:
                self.gcode.respond_info('helix_box_bridge: %s failed: %s' % (script, e))
        return self.reactor.NEVER

    def _build(self, slot, ids, tables, eventtime):
        fila, colors, vendors = tables
        cur = self._current(slot, eventtime)
        filament = cur.get('filament_str') or 'PLA Basic'
        color = cur.get('color') or 'FAFAFA'
        vendor = cur.get('vendor_str') or 'QIDI'
        if ids.get('filament', 0) > 0:
            if ids['filament'] not in fila:
                raise ValueError('fila%d not in %s' % (ids['filament'], self.filas_path))
            filament = fila[ids['filament']]
        if ids.get('color', 0) > 0:
            if ids['color'] not in colors:
                raise ValueError('colour %d not in [colordict]' % ids['color'])
            color = colors[ids['color']]
        # Helix only knows the stock vendor list, so a Generic (0) write keeps the
        # brand the Box already has (e.g. one added to the printer's filament base).
        if ids.get('vendor', 0) > 0 and ids['vendor'] in vendors:
            vendor = vendors[ids['vendor']]
        return ("UPDATE_FILAMENT_INFORMATION SLOT=%d COLOR='%s' VENDOR='%s' FILAMENT='%s'"
                % (slot, color, vendor, filament))

    def _current(self, slot, eventtime):
        out = {}
        mcc = self.printer.lookup_object('multi_color_controller', None)
        if mcc is None or not hasattr(mcc, 'get_status'):
            return out
        box = mcc.get_status(eventtime).get('box', {})
        prefix = 'box%d_filament_info_%d_' % (slot // SLOTS_PER_BOX, slot % SLOTS_PER_BOX)
        for key in ('filament_str', 'vendor_str'):
            v = box.get(prefix + key)
            if isinstance(v, str) and v:
                out[key] = v
        c = box.get(prefix + 'color_rgb_str')
        if isinstance(c, (list, tuple)) and c:
            c = c[0]
        if isinstance(c, str) and c:
            out['color'] = c.lstrip('#').upper()
        return out

    def _load_tables(self):
        cp = configparser.RawConfigParser(strict=False, inline_comment_prefixes=(';',))
        cp.optionxform = str
        cp.read(self.filas_path, encoding='utf-8')
        fila, colors, vendors = {}, {}, {}
        for sec in cp.sections():
            if sec.startswith('fila') and sec[4:].isdigit():
                name = cp.get(sec, 'filament', fallback='').strip()
                if name:
                    fila[int(sec[4:])] = name
        if cp.has_section('colordict'):
            for k, v in cp.items('colordict'):
                if k.strip().isdigit() and v.strip():
                    colors[int(k)] = v.strip().lstrip('#').upper()
        if cp.has_section('vendor_list'):
            for k, v in cp.items('vendor_list'):
                if k.strip().isdigit() and v.strip():
                    vendors[int(k)] = v.strip()
        return fila, colors, vendors


def load_config(config):
    return HelixBoxBridge(config)
