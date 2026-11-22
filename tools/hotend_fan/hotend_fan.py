#!/usr/bin/env python3
# hotend_fan.py - hotend fan hysteresis and no false fan alarm on reheat (QIDI Q2).
# PL: histereza wentylatora hotendu i brak fałszywego alarmu wentylatora przy ponownym grzaniu.
#
# Port of the module "hotend-fan-hysteresis" from qidi-q2-0204-tweaked
# (https://github.com/muchak1994-lpg/qidi-q2-0204-tweaked, GPL-3.0), without its 02.04 checksum check:
# the two files are changed only if ALL anchors are found exactly once in BOTH files.
# PL: oba pliki są zmieniane tylko wtedy, gdy WSZYSTKIE miejsca znaleziono dokładnie raz w OBU plikach.
#
#   python3 hotend_fan.py check     read only / tylko odczyt
#   python3 hotend_fan.py apply     backup + change / kopia + zmiana
#   python3 hotend_fan.py restore   newest backups back / przywraca najnowsze kopie
#
# After apply/restore / po apply/restore:  sudo systemctl restart klipper
# (FIRMWARE_RESTART does not reload .py files / nie przeładowuje plików .py)
import glob
import os
import shutil
import sys
import time

EXTRAS = os.path.expanduser("~/klipper/klippy/extras")
MARK = "is_q2_hotend"
FILES = {'fan.py': [('        self.head_name = config.get_name().split()[0]\n        # Read config\n',
             '        self.head_name = config.get_name().split()[0]\n'
             '        self.is_q2_hotend = (\n'
             "            config.get_name().split() == ['heater_fan', 'hotend_fan']\n"
             "            and tuple(config.getlist('heater', ('extruder',))) == ('extruder',))\n"
             '        # Read config\n'),
            ('            if not extruder_target_temp > 0:\n                return self.reactor.NEVER\n',
             '            if not extruder_target_temp > 0:\n'
             '                if self.is_q2_hotend:\n'
             '                    # Resume checking RPM on reheat even at unchanged PWM.\n'
             '                    self.last_rpm_time = 0\n'
             '                    return eventtime + 1.\n'
             '                return self.reactor.NEVER\n'),
            ('                    self.last_rpm_time = 0  \n'
             '                    self.rpm_error = 0       \n'
             '            else:\n',
             '                    self.last_rpm_time = 0  \n'
             '                    # Keep a raised alarm until heater_fan handles the cutoff.\n'
             '                    if not (self.is_q2_hotend and self.rpm_error == 1):\n'
             '                        self.rpm_error = 0\n'
             '            else:\n'),
            ('            if(value == 0):\n'
             '                self.reactor.update_timer(self.rpm_watchdog_timer, self.reactor.NEVER)\n',
             '            if(value == 0):\n'
             '                if self.is_q2_hotend:\n'
             '                    self.last_rpm_time = 0\n'
             '                self.reactor.update_timer(self.rpm_watchdog_timer, self.reactor.NEVER)\n'),
            ('            elif(value != 0 and self.last_fan_value == 0):\n'
             "                if self.head_name == 'heater_fan':\n"
             "                    extruder = self.printer.lookup_object('toolhead').get_extruder()\n",
             '            elif(value != 0 and self.last_fan_value == 0):\n'
             "                if self.head_name == 'heater_fan' and not self.is_q2_hotend:\n"
             "                    extruder = self.printer.lookup_object('toolhead').get_extruder()\n")],
 'heater_fan.py': [('import logging\n\n', 'import logging\nimport math\n\n'),
                   ('        self.fan_speed = config.getfloat("fan_speed", 1., minval=0., maxval=1.)\n'
                    '        self.last_speed = 0.\n'
                    '    def handle_ready(self):\n',
                    '        self.fan_speed = config.getfloat("fan_speed", 1., minval=0., maxval=1.)\n'
                    '        self.last_speed = None if self.fan.is_q2_hotend else 0.\n'
                    '    def handle_ready(self):\n'),
                   ('        speed = 0.\n        for heater in self.heaters:\n',
                    '        speed = 0.\n'
                    '        threshold = self.heater_temp\n'
                    '        if self.fan.is_q2_hotend and self.last_speed != 0.:\n'
                    '            # On the first reading assume the hotend may still be cooling.\n'
                    '            threshold -= 5.\n'
                    '        for heater in self.heaters:\n'),
                   ('            current_temp, target_temp = heater.get_temp(eventtime)\n'
                    '            if target_temp or current_temp > self.heater_temp:\n'
                    '                speed = self.fan_speed\n',
                    '            current_temp, target_temp = heater.get_temp(eventtime)\n'
                    '            # The heater also returns zero when its temperature sample is stale.\n'
                    '            unknown_temp = self.fan.is_q2_hotend and (\n'
                    '                not math.isfinite(current_temp) or current_temp <= 0.)\n'
                    '            if target_temp or unknown_temp or current_temp > threshold:\n'
                    '                speed = self.fan_speed\n')]}


def plan():
    out, ok = {}, True
    for name, edits in FILES.items():
        path = os.path.join(EXTRAS, name)
        if not os.path.exists(path):
            print("  %s: NOT FOUND / brak pliku (%s)" % (name, path))
            ok = False
            continue
        raw = open(path, encoding="utf-8", newline="").read()
        crlf = "\r\n" in raw
        text = raw.replace("\r\n", "\n")
        if MARK in text:
            print("  %s: already applied / już wgrane" % name)
            out[name] = (path, None, crlf)
            continue
        new = text
        for i, (old, rep) in enumerate(edits, 1):
            n = new.count(old)
            state = "OK" if n == 1 else ("NOT FOUND / nie znaleziono" if n == 0 else "%dx" % n)
            print("  %s edit %d: %s" % (name, i, state))
            if n == 1:
                new = new.replace(old, rep)
            else:
                ok = False
        out[name] = (path, new, crlf)
    if ok and len([v for v in out.values() if v[1] is None]) == 1:
        print("  Only one file already patched / tylko jeden plik wgrany - run restore first / najpierw restore")
        ok = False
    return ok, out


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    print("Klipper extras:", EXTRAS)
    if cmd == "restore":
        for name in FILES:
            p = os.path.join(EXTRAS, name)
            b = sorted(glob.glob(p + ".hfan-*"))
            if b:
                shutil.copy2(b[-1], p)
                print("Restored / przywrócono:", b[-1])
            else:
                print("%s: no backup / brak kopii" % name)
        print("Now / teraz: sudo systemctl restart klipper")
        return 0
    ok, out = plan()
    if not ok:
        print("Nothing changed / nic nie zmieniono")
        return 1
    todo = {k: v for k, v in out.items() if v[1] is not None}
    if not todo:
        print("Already applied / już wgrane")
        return 0
    if cmd != "apply":
        print("Ready, run: python3 hotend_fan.py apply / gotowe, uruchom apply")
        return 0
    for name, (path, new, crlf) in todo.items():
        if not os.access(path, os.W_OK) or not os.access(os.path.dirname(path), os.W_OK):
            print("No write permission / brak prawa zapisu:", path)
            print("  sudo HOME=%s python3 %s apply" % (os.path.expanduser("~"), os.path.abspath(__file__)))
            return 1
    stamp = time.strftime("%Y%m%d-%H%M%S")
    for name, (path, new, crlf) in todo.items():
        shutil.copy2(path, path + ".hfan-" + stamp)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8", newline="") as f:
            f.write(new.replace("\n", "\r\n") if crlf else new)
        shutil.copymode(path, tmp)
        os.replace(tmp, path)
        print("Applied / wgrane: %s (backup / kopia: %s.hfan-%s)" % (path, name, stamp))
    print("Now / teraz: sudo systemctl restart klipper")
    return 0


sys.exit(main())
