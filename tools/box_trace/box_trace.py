# box_trace.py - read-only tracing of QIDI Box behaviour on the Q2
#
# Logs, without changing anything:
#   * every parameter the Box code reads through box_extras.get_value_by_key
#     (key, default passed by QIDI, value returned),
#   * optionally (BOX_TRACE SCRIPTS=1) every G-code script run through Klipper,
#     with a timestamp, so a filament change can be timed step by step.
#
# Install: copy to ~/klipper/klippy/extras/ and add [box_trace] to printer.cfg.
# Remove:  delete the [box_trace] section and restart Klipper.
#
# Console:
#   BOX_TRACE REPORT=1     - list parameters read so far
#   BOX_TRACE SCRIPTS=1    - start logging G-code scripts to klippy.log
#   BOX_TRACE SCRIPTS=0    - stop logging G-code scripts

import logging


class BoxTrace:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.reactor = self.printer.get_reactor()
        self.gcode = self.printer.lookup_object('gcode')
        self.scripts = False
        self.seen = {}
        self.printer.register_event_handler("klippy:ready", self._ready)
        self.gcode.register_command(
            'BOX_TRACE', self.cmd_BOX_TRACE,
            desc="Box tracing: BOX_TRACE REPORT=1 | SCRIPTS=0/1")

    # ------------------------------------------------------------------
    def _ready(self):
        self._wrap_lookup()
        self._wrap_scripts()

    def _wrap_lookup(self):
        extras = self.printer.lookup_object('box_extras', None)
        if extras is None:
            logging.info("box_trace: box_extras not found")
            return
        original = getattr(extras, 'get_value_by_key', None)
        if not callable(original):
            logging.info("box_trace: get_value_by_key not found")
            return

        def get_value_by_key(*args, **kwargs):
            value = original(*args, **kwargs)
            try:
                key = args[0] if args else kwargs.get('key', '?')
                default = args[1] if len(args) > 1 else kwargs.get('default')
                self.seen[str(key)] = (default, value)
                logging.info("box_trace: lookup %s default=%r -> %r",
                             key, default, value)
            except Exception:
                pass
            return value

        try:
            extras.get_value_by_key = get_value_by_key
            logging.info("box_trace: lookup tracing active")
        except Exception as e:
            logging.info("box_trace: cannot trace lookups: %s", e)

    def _wrap_scripts(self):
        for name in ('run_script_from_command', 'run_script'):
            original = getattr(self.gcode, name, None)
            if not callable(original):
                continue
            setattr(self.gcode, name, self._make_script_wrapper(name, original))
        logging.info("box_trace: script tracing ready (off until SCRIPTS=1)")

    def _make_script_wrapper(self, name, original):
        def wrapper(script, *args, **kwargs):
            if self.scripts:
                try:
                    logging.info("box_trace: %s t=%.3f %r", name,
                                 self.reactor.monotonic(), script)
                except Exception:
                    pass
            return original(script, *args, **kwargs)
        return wrapper

    # ------------------------------------------------------------------
    def cmd_BOX_TRACE(self, gcmd):
        scripts = gcmd.get_int('SCRIPTS', None, minval=0, maxval=1)
        if scripts is not None:
            self.scripts = bool(scripts)
        if gcmd.get_int('REPORT', 0):
            lines = ["%s: default=%r value=%r" % (k, d, v)
                     for k, (d, v) in sorted(self.seen.items())]
            gcmd.respond_info("Box parameters read:\n%s"
                              % ("\n".join(lines) or "none yet - load or unload a slot first"))
        gcmd.respond_info("box_trace: script logging %s"
                          % ("ON" if self.scripts else "OFF"))


def load_config(config):
    return BoxTrace(config)
