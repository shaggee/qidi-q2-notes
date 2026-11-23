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
import json
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
        self.filament_db = config.get(
            'filament_db',
            '/home/qidi/QIDI_Client/resource/filament_config/filament-0.4.json')
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
        logging.info('helix_box_bridge v2: active, list %s, base %s',
                     self.filas_path, self.filament_db)

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
        vendor = cur.get('vendor_str') or 'QIDI'
        color = cur.get('color') or 'FAFAFA'
        if ids.get('color', 0) > 0:
            if ids['color'] not in colors:
                raise ValueError('colour %d not in [colordict]' % ids['color'])
            color = colors[ids['color']]
        if ids.get('filament', 0) > 0:
            if ids['filament'] not in fila:
                raise ValueError('fila%d not in %s' % (ids['filament'], self.filas_path))
            name, ftype = fila[ids['filament']]
            vid = ids.get('vendor', 0)
            want_vendor = vendors.get(vid, 'Generic')
            logging.info('helix_box_bridge: slot %d now %r, Helix wants %s / %s (%s)',
                         slot, cur, want_vendor, name, ftype)
            if vid == 0 and ftype and ftype == cur.get('filament_type'):
                # Same material type and no brand picked: Helix re-sent the slot
                # (e.g. a colour-only edit), so keep the brand and product the Box has.
                pass
            else:
                vendor, filament = self._pick(want_vendor, name, ftype)
        return ("UPDATE_FILAMENT_INFORMATION SLOT=%d COLOR='%s' VENDOR='%s' FILAMENT='%s'"
                % (slot, color, vendor, filament))

    def _pick(self, vendor, name, ftype):
        """Return a (vendor, filament) pair that exists in the printer's filament base."""
        pairs = self._load_db()
        if not pairs:
            return vendor, name
        for v, f in ((vendor, name), (vendor, ftype), ('QIDI', name),
                     ('Generic', ftype)):
            if f and (v, f) in pairs:
                return v, f
        for (v, f), t in sorted(pairs.items()):
            if v == vendor and t == ftype:
                return v, f
        raise ValueError('no %s / %s (%s) in %s' % (vendor, name, ftype, self.filament_db))

    def _load_db(self):
        try:
            with open(self.filament_db, encoding='utf-8') as fh:
                data = json.load(fh)
        except Exception as e:
            logging.info('helix_box_bridge: filament base not read: %s', e)
            return {}
        pairs = {}
        for key, entry in data.items():
            if not isinstance(entry, dict):
                continue
            v = str(entry.get('filament_vendor') or '').strip()
            if v and key.startswith(v + ' '):
                pairs[(v, key[len(v) + 1:].strip())] = str(entry.get('type') or '')
        return pairs

    def _current(self, slot, eventtime):
        out = {}
        mcc = self.printer.lookup_object('multi_color_controller', None)
        if mcc is None or not hasattr(mcc, 'get_status'):
            return out
        box = mcc.get_status(eventtime).get('box', {})
        prefix = 'box%d_filament_info_%d_' % (slot // SLOTS_PER_BOX, slot % SLOTS_PER_BOX)
        for key in ('filament_str', 'vendor_str', 'filament_type'):
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
                    fila[int(sec[4:])] = (name, cp.get(sec, 'type', fallback='').strip())
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
