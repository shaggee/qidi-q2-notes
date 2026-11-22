#!/usr/bin/env python3
# q2_tweaks.py - manual install of selected fixes from qidi-q2-0204-tweaked
# (https://github.com/muchak1994-lpg/qidi-q2-0204-tweaked, GPL-3.0) on a Q2
# whose macros are already customised, without reflashing the firmware.
#
#   python3 q2_tweaks.py check     - read only: shows what would change
#   python3 q2_tweaks.py apply     - backs up each file, then applies
#   python3 q2_tweaks.py restore   - puts back the newest backup of each file
#
# Every change is a plain text replacement. A group is applied only if ALL its
# anchors are found exactly once; otherwise that group is skipped and nothing
# in it is touched. Already applied groups are recognised by their marker.
# Backups: <file>.q2tw-<date> next to each file.

import glob
import os
import shutil
import sys
import time

HOME = os.path.expanduser("~")
HERE = os.path.dirname(os.path.abspath(__file__))
EXTRAS = os.path.join(HOME, "klipper", "klippy", "extras")
MACROS_DIR = os.path.join(HOME, "printer_data", "config", "klipper-macros-qd")


def find_macro_file():
    for path in sorted(glob.glob(os.path.join(MACROS_DIR, "*.cfg"))):
        try:
            with open(path, encoding="utf-8") as f:
                if "[gcode_macro PRINT_START]" in f.read():
                    return path
        except Exception:
            pass
    return None


# ---------------------------------------------------------------- edits
PROBE_OLD = (
    "                gcmd.respond_info(\"Probe samples exceed tolerance. Retrying...\")\r\n"
    "                retries += 1\r\n"
    "                # 超过两次直接清零\r\n"
    "                if(retries == 1):\r\n"
    "                    self.mcu_probe.home_zero()\r\n"
    "                    retries = 0 \r\n"
    "                positions = []\r\n"
    "            # Retract\r\n"
    "            if len(positions) < sample_count:\r\n"
    "                toolhead.manual_move(\r\n"
    "                    probexy + [pos[2] + params['sample_retract_dist']],\r\n"
    "                    params['lift_speed'])\r\n")
PROBE_NEW = (
    "                gcmd.respond_info(\"Probe samples exceed tolerance. Retrying...\")\r\n"
    "                # q2-probe-retry-fix: the retry count is no longer reset and the load cell is\r\n"
    "                # re-zeroed after the nozzle has lifted off the bed (QIDI zeroed it pressed on the bed).\r\n"
    "                retries += 1\r\n"
    "                positions = []\r\n"
    "            # Retract\r\n"
    "            if len(positions) < sample_count:\r\n"
    "                toolhead.manual_move(\r\n"
    "                    probexy + [pos[2] + params['sample_retract_dist']],\r\n"
    "                    params['lift_speed'])\r\n"
    "                if not positions:\r\n"
    "                    toolhead.wait_moves()\r\n"
    "                    toolhead.dwell(0.05)\r\n"
    "                    self.mcu_probe.home_zero()\r\n"
    "                    toolhead.dwell(0.05)\r\n")

HEATER_OLD = "        self.next_pwm_time = pwm_time + 0.75 * MAX_HEAT_TIME\r\n"
HEATER_NEW = ("        self.next_pwm_time = pwm_time + (0.25 if 'heater_box' in self.name else 0.75)"
              " * MAX_HEAT_TIME  # q2-box-heater-keepalive (QIDI_Q2 issue #34)\r\n")

LTM_EDITS = [
    ("    {% set adaptive_mesh = printer[\"gcode_macro G29\"].k|int %}\n",
     "    {% set adaptive_mesh = printer[\"gcode_macro G29\"].k|int %}\n"
     "    _REMEMBER_FILA_TEMP SET={hotendtemp}  # q2-load-temp-memory: this print's material\n"),
    ("[gcode_macro PRINT_END]\ngcode:\n",
     "[gcode_macro PRINT_END]\ngcode:\n"
     "    _REMEMBER_FILA_TEMP  # q2-load-temp-memory: the last material's temperature\n"),
    ("rename_existing: BASE_CANCEL_PRINT\ngcode:\n",
     "rename_existing: BASE_CANCEL_PRINT\ngcode:\n"
     "    _REMEMBER_FILA_TEMP  # q2-load-temp-memory: the last material's temperature\n"),
    ("[gcode_macro M604]\ngcode:\n    DISABLE_ALL_SENSOR\n"
     "    {% set hotendtemp = params.S|default(250)|int %}\n"
     "    {% set mode = params.T|default(0)|int %}\n",
     "[gcode_macro M604]\ngcode:\n    DISABLE_ALL_SENSOR\n"
     "    {% set mode = params.T|default(0)|int %}\n"
     "    # q2-load-temp-memory (QIDI_Q2 #26): old material pushed out at its own temperature if hotter\n"
     "    {% set q2_new = params.S|default(250)|int %}\n"
     "    {% set q2_old = [printer.save_variables.variables.q2_fila_temp|default(0)|int, 350]|min %}\n"
     "    {% set q2_hot = [q2_new, q2_old]|max %}\n"
     "    {% set hotendtemp = q2_new if mode == 2 else q2_hot %}\n"),
    ("    {% elif mode ==1 %}      #尝试挤入\n        G92 E0\n",
     "    {% elif mode ==1 %}      #尝试挤入\n"
     "        {% if q2_hot > q2_new %}\n"
     "            M118 Old material is pushed out at {q2_hot} C\n"
     "            M109 S{q2_hot}\n"
     "        {% endif %}\n"
     "        G92 E0\n"),
    ("        SET_PRINT_SUB_STATUS SUB_STATUS=clean_filamenting\n"
     "        MOVE_TO_TRASH\n        M109 S{hotendtemp}\n",
     "        SET_PRINT_SUB_STATUS SUB_STATUS=clean_filamenting\n"
     "        MOVE_TO_TRASH\n"
     "        {% if q2_hot > q2_new %}\n"
     "            M104 S{q2_new}\n"
     "            TEMPERATURE_WAIT SENSOR=extruder MINIMUM={q2_new}\n"
     "        {% else %}\n"
     "            M109 S{hotendtemp}\n"
     "        {% endif %}\n"),
    ("        M400\n        M106 S0\n        M104 S0\n"
     "        SET_PRINT_MAIN_STATUS MAIN_STATUS=ready\n",
     "        M400\n        M106 S0\n        M104 S0\n"
     "        _REMEMBER_FILA_TEMP SET={q2_new}\n"
     "        SET_PRINT_MAIN_STATUS MAIN_STATUS=ready\n"),
    ("[gcode_macro M603]\ndescription: filament unlode\ngcode:\n"
     "    SET_PRINT_MAIN_STATUS MAIN_STATUS=filament_unload_7\n"
     "    DISABLE_ALL_SENSOR\n    {% set hotendtemp = params.S|default(250)|int %}\n",
     "[gcode_macro M603]\ndescription: filament unlode\ngcode:\n"
     "    SET_PRINT_MAIN_STATUS MAIN_STATUS=filament_unload_7\n"
     "    DISABLE_ALL_SENSOR\n"
     "    # q2-load-temp-memory (QIDI_Q2 #26): unload at the old material's temperature if it is higher\n"
     "    {% set q2_old = [printer.save_variables.variables.q2_fila_temp|default(0)|int, 350]|min %}\n"
     "    {% set hotendtemp = [params.S|default(250)|int, q2_old]|max %}\n"),
    ("    M118 Unload finish\n",
     "    _REMEMBER_FILA_TEMP SET={hotendtemp}\n    M118 Unload finish\n"),
]

GROUPS = [
    {"name": "probe-retry-fix", "marker": "q2-probe-retry-fix",
     "file": lambda: os.path.join(EXTRAS, "probe.py"),
     "edits": [(PROBE_OLD, PROBE_NEW)], "copies": []},
    {"name": "box-heater-keepalive", "marker": "q2-box-heater-keepalive",
     "file": lambda: os.path.join(EXTRAS, "heaters.py"),
     "edits": [(HEATER_OLD, HEATER_NEW)], "copies": []},
    {"name": "load-temp-memory", "marker": "q2-load-temp-memory",
     "file": find_macro_file, "edits": LTM_EDITS,
     "copies": [("q2_fila_temp.cfg", MACROS_DIR)]},
    {"name": "thr-accel-check", "marker": None, "file": None, "edits": [],
     "copies": [("q2_thr_check.py", EXTRAS), ("q2_thr_check.cfg", MACROS_DIR)]},
]


# ---------------------------------------------------------------- engine
def variants(old, new):
    """The same edit with LF and with CRLF line endings."""
    lf_old, lf_new = old.replace("\r\n", "\n"), new.replace("\r\n", "\n")
    yield old, new
    if lf_old != old:
        yield lf_old, lf_new
    yield lf_old.replace("\n", "\r\n"), lf_new.replace("\n", "\r\n")


def plan_group(g):
    """Return (status, path, text, new_text, messages)."""
    msgs = []
    if g["file"] is None:
        return "copy-only", None, None, None, msgs
    path = g["file"]()
    if not path or not os.path.exists(path):
        return "missing", path, None, None, ["file not found"]
    with open(path, "rb") as f:
        text = f.read().decode("utf-8")
    if g["marker"] and g["marker"] in text:
        return "applied", path, text, None, msgs
    new_text = text
    ok = True
    for i, (old, new) in enumerate(g["edits"]):
        for o, n in variants(old, new):
            c = new_text.count(o)
            if c == 1:
                new_text = new_text.replace(o, n)
                break
        else:
            counts = [new_text.count(o) for o, _ in variants(old, new)]
            msgs.append("edit %d: anchor found %s times (need exactly 1)" % (i + 1, counts))
            ok = False
    return ("ready" if ok else "mismatch"), path, text, new_text, msgs


def copies_status(g):
    out = []
    for name, dest in g["copies"]:
        src = os.path.join(HERE, name)
        dst = os.path.join(dest, name)
        if not os.path.exists(src):
            out.append((name, "source missing next to q2_tweaks.py"))
        elif os.path.exists(dst):
            same = open(src, "rb").read() == open(dst, "rb").read()
            out.append((name, "already installed" if same else "different file exists (will back up and replace)"))
        else:
            out.append((name, "will be copied to %s" % dest))
    return out


def backup(path, stamp):
    dst = "%s.q2tw-%s" % (path, stamp)
    shutil.copy2(path, dst)
    return dst


def cmd_check():
    print("Macro file: %s\n" % (find_macro_file() or "NOT FOUND"))
    for g in GROUPS:
        status, path, _, _, msgs = plan_group(g)
        print("[%s] %s" % (g["name"], status))
        if path:
            print("    file: %s" % path)
        for m in msgs:
            print("    " + m)
        for name, st in copies_status(g):
            print("    %s: %s" % (name, st))
    print("\nNothing was changed. Run 'apply' to install the groups marked ready.")


def cmd_apply():
    stamp = time.strftime("%Y%m%d-%H%M%S")
    changed = False
    for g in GROUPS:
        status, path, text, new_text, msgs = plan_group(g)
        if status in ("mismatch", "missing"):
            print("[%s] SKIPPED: %s" % (g["name"], "; ".join(msgs) or status))
            continue
        if status == "ready":
            b = backup(path, stamp)
            with open(path + ".tmp", "wb") as f:
                f.write(new_text.encode("utf-8"))
            os.replace(path + ".tmp", path)
            print("[%s] applied (backup: %s)" % (g["name"], b))
            changed = True
        elif status == "applied":
            print("[%s] already applied" % g["name"])
        for name, dest in g["copies"]:
            src = os.path.join(HERE, name)
            dst = os.path.join(dest, name)
            if not os.path.exists(src):
                print("    %s: source missing, skipped" % name)
                continue
            if os.path.exists(dst):
                if open(src, "rb").read() == open(dst, "rb").read():
                    continue
                backup(dst, stamp)
            shutil.copy2(src, dst)
            print("    %s copied to %s" % (name, dest))
            changed = True
    if changed:
        print("\nDone. Turn the printer OFF and ON (a Klipper restart from Fluidd does not reload changed .py files).")
    else:
        print("\nNothing changed.")


def cmd_restore():
    targets = [os.path.join(EXTRAS, "probe.py"), os.path.join(EXTRAS, "heaters.py")]
    mf = find_macro_file()
    if mf:
        targets.append(mf)
    for path in targets:
        baks = sorted(glob.glob(path + ".q2tw-*"))
        if not baks:
            print("%s: no backup" % path)
            continue
        shutil.copy2(baks[-1], path)
        print("%s restored from %s" % (path, baks[-1]))
    for name, dest in (("q2_fila_temp.cfg", MACROS_DIR), ("q2_thr_check.cfg", MACROS_DIR),
                       ("q2_thr_check.py", EXTRAS)):
        p = os.path.join(dest, name)
        if os.path.exists(p):
            os.remove(p)
            print("%s removed" % p)
    print("\nTurn the printer OFF and ON.")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    {"check": cmd_check, "apply": cmd_apply, "restore": cmd_restore}.get(
        cmd, lambda: print(__doc__ or "use: check | apply | restore"))()
