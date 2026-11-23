# qbdisplay - entry point for the QIDI Q2 (framebuffer display instead of a TJC display)
#
# Copyright (C) 2026  qidi-q2-notes contributors, with Claude (Anthropic)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See <https://www.gnu.org/licenses/>.
"""python3 -m qbdisplay.q2main -c ~/printer_data/config/qbdisplay.cfg

Same as qbdisplay/__main__.py, but the display is :class:`qbdisplay.fbdisplay.FbDisplay`.
Extra options in [display] (all optional):
  fb: /dev/fb0
  touch: /dev/input/event0
  touch_swap_xy: no
  touch_invert_x: no
  touch_invert_y: no
  max_fps: 10
"""

import argparse
import logging
import sys

from . import __version__
from . import fonts
from .app import App, subscribe_objects
from .config import Config
from .fbdisplay import FbDisplay
from .moonraker import make_client

log = logging.getLogger('qbdisplay')


def _opt(cfg, key, default, kind=str):
    try:
        if kind is bool:
            return cfg.getbool('display', key)
        if kind is int:
            return cfg.getint('display', key)
        return cfg.get('display', key)
    except Exception:
        return default


def main(argv=None):
    ap = argparse.ArgumentParser(prog='qbdisplay', description='qbdisplay for the QIDI Q2 (framebuffer)')
    ap.add_argument('-c', '--config', default=None, help='path to qbdisplay.cfg')
    ap.add_argument('-v', '--verbose', action='store_true')
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format='%(asctime)s %(levelname)s %(name)s: %(message)s')
    cfg = Config(args.config)
    fonts.set_monospace(cfg.getbool('display', 'monospace_fonts'))
    disp = FbDisplay(fb=_opt(cfg, 'fb', '/dev/fb0'),
                     touch=_opt(cfg, 'touch', '/dev/input/event0'),
                     swap_xy=_opt(cfg, 'touch_swap_xy', False, bool),
                     invert_x=_opt(cfg, 'touch_invert_x', False, bool),
                     invert_y=_opt(cfg, 'touch_invert_y', False, bool),
                     max_fps=_opt(cfg, 'max_fps', 10, int))
    log.info('qbdisplay %s (Q2 framebuffer)', __version__)
    app = App(cfg, disp, rpc=None, display=disp)
    disp.on_event = app.on_display_event
    disp.open()
    disp.init_display(cfg.getint('display', 'sleep_after'))
    disp.send('dim=%d' % max(10, min(100, cfg.getint('display', 'brightness'))))
    app.versions['display'] = 'Q2 framebuffer %dx%d' % (disp.width, disp.height)

    rpc = make_client(cfg, app.on_rpc_event, subscribe_objects(cfg), version=__version__)
    app.rpc = rpc
    app.connected = False
    rpc.start()
    try:
        app.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        rpc.stop()
        disp.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
