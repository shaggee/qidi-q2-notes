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
from . import updates

# Q2: look for QIDI Q2 firmware, not Plus4 (QIDI's version server path for the Q2 is unknown -> GitHub only)
updates.QIDI_VERSION_URLS = ()
updates.QIDI_GITHUB = 'QIDITECH/QIDI_Q2'

log = logging.getLogger('qbdisplay')


def setup_q2():
    """Q2 additions: Polish language (needs TTF rendering, so only with the framebuffer driver)."""
    from . import i18n
    from .pl import PL
    from .sim import load_pil_font
    from .ui import system as ui_system

    # --- language table, language list, "polski" -> pl, decimal comma
    i18n.TABLES['pl'] = PL
    if 'pl' not in dict(i18n.LANGUAGES):
        i18n.LANGUAGES = tuple(i18n.LANGUAGES) + (('pl', 'Polski'),)
    _normalize = i18n.normalize

    def normalize(lang):
        s = str(lang or '').strip().lower()
        if s.startswith('pol') or s.startswith('pl'):
            return 'pl'
        return _normalize(lang)
    i18n.normalize = normalize
    i18n.decimal = lambda text: text.replace('.', ',') if i18n.get_language() in ('de', 'pl') else text

    # --- Polish letters: TJC fonts are ISO-8859-1, but here text is drawn with the TTF fonts
    _sanitize = fonts.sanitize

    def sanitize(text):
        return ''.join(ch if 0x100 <= ord(ch) < 0x180 else _sanitize(ch) for ch in str(text))
    fonts.sanitize = sanitize

    _char_width = fonts.char_width
    _widths = {}

    def char_width(ch, fid):
        if ord(ch) < 256:
            return _char_width(ch, fid)
        key = (ch, fid)
        if key not in _widths:
            font = load_pil_font(fonts.FONTS[fid])
            try:
                w = font.getlength(ch)
            except AttributeError:
                w = font.getsize(ch)[0]
            _widths[key] = int(round(w)) + fonts.TRACKING.get(fid, 0)
        return _widths[key]
    fonts.char_width = char_width

    # --- language page: three rows, no note (the note would overlap the third row)
    def build_lang(self, frame):
        ctx = self.ctx
        cur = i18n.get_language()
        for i, (code, name) in enumerate(i18n.LANGUAGES):
            on = code == cur
            self._row(frame, 'r.lang.' + code, 52 + i * 84, name,
                      i18n._('aktiv') if on else i18n._('Antippen zum Wechseln'), toggle=on,
                      action=None if on else (lambda c=code: ctx.set_language(c)))
        if len(i18n.LANGUAGES) <= 2:
            self._row(frame, 'r.langnote', 220, i18n._('Hinweis'),
                      i18n._('Gilt sofort und bleibt nach einem Neustart erhalten.'))
    ui_system.SystemPage.build_lang = build_lang


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
    setup_q2()
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
