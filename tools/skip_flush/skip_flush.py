#!/usr/bin/env python3
# skip_flush.py - PRINT_START: skip the ~75 s Box flush when the needed slot is already loaded.
# PL: pomija ~75 s płukania Boxa w PRINT_START, gdy potrzebny slot jest już załadowany.
#
#   python3 skip_flush.py check     read only / tylko odczyt
#   python3 skip_flush.py apply     backup + change / kopia + zmiana
#   python3 skip_flush.py restore   newest backup back / przywraca najnowszą kopię
#
# Applied only if all 3 anchors are found exactly once. LF and CRLF files.
# Backup: <file>.skipflush-<date>.
import glob, os, shutil, sys, time

CFG = os.path.expanduser("~/printer_data/config")
MARK = "same_slot"

def find():
    for p in sorted(glob.glob(CFG + "/*.cfg") + glob.glob(CFG + "/*/*.cfg")):
        try:
            if "[gcode_macro PRINT_START]" in open(p, encoding="utf-8", newline="").read():
                return p
        except Exception:
            pass

A_OLD = '    {% set adaptive_mesh = printer["gcode_macro G29"].k|int %}\n'
A_NEW = A_OLD + (
    "    {% set sv = printer.save_variables.variables %}\n"
    "    {% set target_slot = sv['value_t' ~ extruder]|default('') %}\n"
    "    {% set same_slot = target_slot != '' and target_slot == sv.last_load_slot|default('none') %}\n")
B_OLD = ("            BOX_PRINT_START EXTRUDER={extruder} HOTENDTEMP={hotendtemp}\n"
         "            M400\n"
         "            SET_PRINT_SUB_STATUS SUB_STATUS=flush_filament\n"
         "            EXTRUSION_AND_FLUSH HOTEND={hotendtemp}\n")
B_NEW = ("            BOX_PRINT_START EXTRUDER={extruder} HOTENDTEMP={hotendtemp}\n"
         "            M400\n"
         "            {% if same_slot %}\n"
         "                M118 Same slot {target_slot} - skipping flush\n"
         "            {% else %}\n"
         "                SET_PRINT_SUB_STATUS SUB_STATUS=flush_filament\n"
         "                EXTRUSION_AND_FLUSH HOTEND={hotendtemp}\n"
         "            {% endif %}\n")
C_OLD = "printer.save_variables.variables.enable_box == 1 %}\n    CLEAR_NOZZLE"
C_NEW = "printer.save_variables.variables.enable_box == 1 and not same_slot %}\n    CLEAR_NOZZLE"
EDITS = [("A same_slot vars", A_OLD, A_NEW), ("B flush if/else", B_OLD, B_NEW), ("C box_flushed", C_OLD, C_NEW)]

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    path = find()
    if not path:
        print("PRINT_START not found / nie znaleziono PRINT_START"); return 1
    print("File / plik:", path)
    if cmd == "restore":
        b = sorted(glob.glob(path + ".skipflush-*"))
        if not b:
            print("No backup / brak kopii"); return 1
        shutil.copy2(b[-1], path); print("Restored / przywrócono:", b[-1]); return 0
    raw = open(path, encoding="utf-8", newline="").read()
    crlf = "\r\n" in raw
    text = raw.replace("\r\n", "\n")
    if MARK in text:
        print("Already applied / już wgrane"); return 0
    ok = True
    for name, old, new in EDITS:
        n = text.count(old)
        print(f"  {name}: {'OK' if n == 1 else 'NOT FOUND / NIE ZNALEZIONO' if n == 0 else f'{n}x - ambiguous'}")
        ok &= n == 1
    if not ok:
        print("Nothing changed / nic nie zmieniono"); return 1
    if cmd != "apply":
        print("Ready, run: python3 skip_flush.py apply / gotowe, uruchom apply"); return 0
    for _, old, new in EDITS:
        text = text.replace(old, new)
    bak = path + ".skipflush-" + time.strftime("%Y%m%d-%H%M%S")
    shutil.copy2(path, bak)
    open(path, "w", encoding="utf-8", newline="").write(text.replace("\n", "\r\n") if crlf else text)
    print("Applied / wgrane. Backup / kopia:", bak)
    print("Now / teraz: FIRMWARE_RESTART")
    return 0

sys.exit(main())
