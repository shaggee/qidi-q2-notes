# qbdisplay - framebuffer + evdev display driver for the QIDI Q2 (480x272, Goodix touch)
#
# Copyright (C) 2026  qidi-q2-notes contributors, with Claude (Anthropic)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See <https://www.gnu.org/licenses/>.
"""Drop-in replacement for :class:`qbdisplay.tjc.TjcDisplay` on the Q2.

qbdisplay draws an 800x480 UI as TJC commands. Here those commands are executed by
qbdisplay's own :class:`qbdisplay.sim.Simulator` into an 800x480 PIL image; a blit thread
scales it to the Q2 screen (uniform scale, black side bars) and writes it to /dev/fb0.
Touches are read from the Goodix input device and mapped back to 800x480, so the rest of
qbdisplay sees exactly the same events as from a TJC display.

Same public interface as TjcDisplay: open, close, init_display, send, send_now,
discard_pending, pending, flush, detect_baud, change_baud, on_event, baud, port.
"""

import fcntl
import logging
import os
import struct
import threading
import time

from PIL import Image

from .sim import Simulator
from .tjc import SystemEvent, TouchEvent

log = logging.getLogger(__name__)

UI_W, UI_H = 800, 480

# linux/input-event-codes.h
EV_SYN, EV_KEY, EV_ABS = 0x00, 0x01, 0x03
BTN_TOUCH = 0x14a
ABS_X, ABS_Y = 0x00, 0x01
ABS_MT_SLOT, ABS_MT_POSITION_X, ABS_MT_POSITION_Y, ABS_MT_TRACKING_ID = 0x2f, 0x35, 0x36, 0x39
EVENT_FMT = 'llHHi'                      # struct input_event (64-bit time)
EVENT_SIZE = struct.calcsize(EVENT_FMT)


def _ioc_abs(code):
    """EVIOCGABS(code): _IOR('E', 0x40 + code, struct input_absinfo) - 6 x int32."""
    return (2 << 30) | (24 << 16) | (ord('E') << 8) | (0x40 + code)


def abs_range(fd, code):
    try:
        buf = fcntl.ioctl(fd, _ioc_abs(code), bytes(24))
        _val, lo, hi = struct.unpack('6i', buf)[:3]
        if hi > lo:
            return lo, hi
    except OSError:
        pass
    return None


def _read_int(path, default=None):
    try:
        with open(path) as f:
            return int(f.read().replace(',', ' ').split()[0])
    except (OSError, ValueError, IndexError):
        return default


class _NoPort(object):
    """TjcDisplay has a serial port; __main__/app only call set_baud on it."""

    def set_baud(self, baud):
        pass


class FbDisplay(object):

    def __init__(self, fb='/dev/fb0', touch='/dev/input/event0', on_event=None,
                 swap_xy=False, invert_x=False, invert_y=False,
                 backlight='/sys/class/backlight/backlight', max_fps=10):
        self.fb_path = fb
        self.touch_path = touch
        self.on_event = on_event or (lambda ev: None)
        self.swap_xy, self.invert_x, self.invert_y = swap_xy, invert_x, invert_y
        self.backlight = backlight
        self.min_frame = 1.0 / max(1, max_fps)
        self.baud = 0
        self.port = _NoPort()
        self.sim = Simulator(width=UI_W, height=UI_H)
        self._lock = threading.Lock()
        self._dirty = False
        self._last_cmd = 0.0
        self._running = False
        self._threads = []
        self._fb = None
        self._touch_fd = None
        self._sleep_after = 0
        self._last_touch = time.time()
        self._asleep = False
        self._brightness = 100
        # screen geometry (filled in open())
        self.width, self.height, self.stride = 480, 272, 480 * 4
        self.scale, self.off_x, self.off_y = 0.0, 0, 0
        self.out_w, self.out_h = 480, 272
        self.touch_x = self.touch_y = None

    # -- life cycle ----------------------------------------------------------
    def open(self):
        base = '/sys/class/graphics/' + os.path.basename(self.fb_path) + '/'
        try:
            with open(base + 'virtual_size') as f:
                w, h = [int(v) for v in f.read().strip().split(',')]
            self.width, self.height = w, h
        except (OSError, ValueError):
            pass
        bpp = _read_int(base + 'bits_per_pixel', 32)
        if bpp != 32:
            raise RuntimeError('framebuffer is %d bit, only 32 bit is supported' % bpp)
        self.stride = _read_int(base + 'stride', self.width * 4)
        self.scale = min(self.width / float(UI_W), self.height / float(UI_H))
        self.out_w, self.out_h = int(round(UI_W * self.scale)), int(round(UI_H * self.scale))
        self.off_x, self.off_y = (self.width - self.out_w) // 2, (self.height - self.out_h) // 2
        log.info('framebuffer %s %dx%d stride %d -> UI %dx%d at +%d+%d',
                 self.fb_path, self.width, self.height, self.stride,
                 self.out_w, self.out_h, self.off_x, self.off_y)
        self._fb = open(self.fb_path, 'r+b', buffering=0)
        try:
            self._touch_fd = os.open(self.touch_path, os.O_RDONLY)
            self.touch_x = abs_range(self._touch_fd, ABS_MT_POSITION_X) or abs_range(self._touch_fd, ABS_X)
            self.touch_y = abs_range(self._touch_fd, ABS_MT_POSITION_Y) or abs_range(self._touch_fd, ABS_Y)
            log.info('touch %s x=%s y=%s swap=%s inv=%s/%s', self.touch_path, self.touch_x,
                     self.touch_y, self.swap_xy, self.invert_x, self.invert_y)
        except OSError as e:
            log.error('touch device %s: %s (display only)', self.touch_path, e)
            self._touch_fd = None
        self._set_backlight(self._brightness)
        self._running = True
        for fn in (self._blitter, self._reader):
            t = threading.Thread(target=fn, daemon=True)
            t.start()
            self._threads.append(t)
        self.on_event(SystemEvent('ready'))

    def close(self):
        self._running = False
        if self._touch_fd is not None:
            try:
                os.close(self._touch_fd)
            except OSError:
                pass
        if self._fb is not None:
            try:
                self._fb.close()
            except OSError:
                pass

    # -- TjcDisplay compatibility -------------------------------------------
    def detect_baud(self, candidates=None):
        return 0

    def change_baud(self, new_baud, persist=False):
        return True

    def init_display(self, sleep_after=0):
        self._sleep_after = int(sleep_after or 0)

    def send(self, cmd):
        name, _, rest = cmd.partition(' ')
        if name.startswith('dim='):
            try:
                self._brightness = max(1, min(100, int(name[4:])))
                if not self._asleep:
                    self._set_backlight(self._brightness)
            except ValueError:
                pass
            return
        if name.startswith('sleep='):
            self._go_sleep() if name.endswith('1') else self._wake()
            return
        with self._lock:
            self.sim.execute(cmd)
            self._dirty = True
            self._last_cmd = time.time()

    send_now = send

    def discard_pending(self):
        pass

    def pending(self):
        return 0

    def flush(self, timeout=5.0):
        self._blit()

    # -- output ------------------------------------------------------------------
    def _blitter(self):
        last = 0.0
        while self._running:
            time.sleep(0.015)
            if not self._dirty or self._asleep:
                continue
            now = time.time()
            # wait until a render burst is over, but never longer than one frame
            if now - self._last_cmd < 0.02 and now - last < self.min_frame:
                continue
            last = now
            try:
                self._blit()
            except Exception:
                log.exception('blit failed')
                time.sleep(1)

    def _blit(self):
        with self._lock:
            img = self.sim.img.copy()
            self._dirty = False
        if (self.out_w, self.out_h) != (UI_W, UI_H):
            img = img.resize((self.out_w, self.out_h), Image.LANCZOS)
        if self.off_x or self.off_y or (self.out_w, self.out_h) != (self.width, self.height):
            frame = Image.new('RGB', (self.width, self.height), (0, 0, 0))
            frame.paste(img, (self.off_x, self.off_y))
            img = frame
        data = img.convert('RGBA').tobytes('raw', 'BGRA')
        row = self.width * 4
        if self.stride != row:
            pad = bytes(self.stride - row)
            data = b''.join(data[i:i + row] + pad for i in range(0, len(data), row))
        self._fb.seek(0)
        self._fb.write(data)

    def _set_backlight(self, percent):
        if not self.backlight:
            return
        mx = _read_int(os.path.join(self.backlight, 'max_brightness'))
        if not mx:
            return
        val = 0 if percent <= 0 else max(1, int(round(mx * percent / 100.0)))
        try:
            with open(os.path.join(self.backlight, 'brightness'), 'w') as f:
                f.write(str(val))
        except OSError as e:
            log.debug('backlight: %s', e)

    def _go_sleep(self):
        if not self._asleep:
            self._asleep = True
            self._set_backlight(0)
            self.on_event(SystemEvent('sleep'))

    def _wake(self):
        if self._asleep:
            self._asleep = False
            self._set_backlight(self._brightness)
            self.on_event(SystemEvent('wake'))

    # -- touch -------------------------------------------------------------------
    def _map(self, rx, ry):
        """Raw touch -> screen pixels -> 800x480 UI coordinates."""
        def norm(v, rng, size):
            if not rng:
                return float(v)
            lo, hi = rng
            return (v - lo) * (size - 1) / float(hi - lo)
        if self.swap_xy:
            rx, ry = ry, rx
            rngx, rngy = self.touch_y, self.touch_x
        else:
            rngx, rngy = self.touch_x, self.touch_y
        sx, sy = norm(rx, rngx, self.width), norm(ry, rngy, self.height)
        if self.invert_x:
            sx = self.width - 1 - sx
        if self.invert_y:
            sy = self.height - 1 - sy
        ux = (sx - self.off_x) / self.scale
        uy = (sy - self.off_y) / self.scale
        return int(max(0, min(UI_W - 1, ux))), int(max(0, min(UI_H - 1, uy)))

    def _reader(self):
        if self._touch_fd is None:
            while self._running:
                self._idle_check()
                time.sleep(1)
            return
        x = y = 0
        down = False
        changed_btn = None
        import select
        while self._running:
            r, _, _ = select.select([self._touch_fd], [], [], 1.0)
            if not r:
                self._idle_check()
                continue
            try:
                data = os.read(self._touch_fd, EVENT_SIZE * 64)
            except OSError:
                time.sleep(0.5)
                continue
            for i in range(0, len(data) - EVENT_SIZE + 1, EVENT_SIZE):
                _s, _us, etype, code, value = struct.unpack(EVENT_FMT, data[i:i + EVENT_SIZE])
                if etype == EV_ABS:
                    if code in (ABS_MT_POSITION_X, ABS_X):
                        x = value
                    elif code in (ABS_MT_POSITION_Y, ABS_Y):
                        y = value
                    elif code == ABS_MT_TRACKING_ID and value == -1 and down:
                        changed_btn = False
                    elif code == ABS_MT_TRACKING_ID and value >= 0 and not down:
                        changed_btn = True
                elif etype == EV_KEY and code == BTN_TOUCH:
                    changed_btn = bool(value)
                elif etype == EV_SYN and changed_btn is not None:
                    pressed, changed_btn = changed_btn, None
                    if pressed == down:
                        continue
                    down = pressed
                    self._last_touch = time.time()
                    ux, uy = self._map(x, y)
                    if self._asleep:
                        if pressed:
                            self._wake()
                        self.on_event(TouchEvent(ux, uy, pressed, True))
                        continue
                    self.on_event(TouchEvent(ux, uy, pressed, False))

    def _idle_check(self):
        if self._sleep_after > 0 and not self._asleep \
                and time.time() - self._last_touch > self._sleep_after:
            self._go_sleep()
