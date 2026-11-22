#!/usr/bin/env python3
# random_zhome.py - PRINT_START: re-home Z after Z_TILT_ADJUST at a random point within 10 mm of the
# plate centre instead of always at X135 Y135 (spreads nozzle-probe wear on the PEI).
# PL: PRINT_START: ponowne bazowanie Z po Z_TILT_ADJUST w losowym punkcie do 10 mm od środka zamiast
# zawsze w X135 Y135 (mniej wycierania PEI przez dyszę-sondę).
#
# Same rule as z-home-random-point from qidi-q2-0204-tweaked (GPL-3.0): random only with a fresh mesh
# every print (G29 k=1); with a saved mesh (k=0) it stays at the centre.
#
#   python3 random_zhome.py check     read only / tylko odczyt
#   python3 random_zhome.py apply     backup + change / kopia + zmiana
#   python3 random_zhome.py restore   newest backup back / przywraca najnowszą kopię
import glob, os, re, shutil, sys, time

CFG = os.path.expanduser("~/printer_data/config")
MARK = "q2-random-zhome"
PAT = re.compile(r"^( +)G1 X135 Y135 F(\d+)[^\n]*\n\1G28 Z[ \t]*\n", re.M)


def find():
    for p in sorted(glob.glob(CFG + "/*.cfg") + glob.glob(CFG + "/*/*.cfg")):
        try:
            if "[gcode_macro PRINT_START]" in open(p, encoding="utf-8", newline="").read():
                return p
        except Exception:
            pass


def section(text):
    a = text.index("[gcode_macro PRINT_START]")
    m = re.compile(r"^\[", re.M).search(text, a + 1)
    return a, (m.start() if m else len(text))


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    path = find()
    if not path:
        print("PRINT_START not found / nie znaleziono PRINT_START"); return 1
    print("File / plik:", path)
    if cmd == "restore":
        b = sorted(glob.glob(path + ".rzhome-*"))
        if not b:
            print("No backup / brak kopii"); return 1
        shutil.copy2(b[-1], path); print("Restored / przywrócono:", b[-1])
        print("Now / teraz: FIRMWARE_RESTART"); return 0
    raw = open(path, encoding="utf-8", newline="").read()
    crlf = "\r\n" in raw
    text = raw.replace("\r\n", "\n")
    if MARK in text:
        print("Already applied / już wgrane"); return 0
    a, b = section(text)
    body = text[a:b]
    hits = list(PAT.finditer(body))
    print("  'G1 X135 Y135 ... / G28 Z' in PRINT_START: %d (need 1 / potrzeba 1)" % len(hits))
    if len(hits) != 1:
        print("Nothing changed / nic nie zmieniono"); return 1
    m = hits[0]
    ind, feed = m.group(1), m.group(2)
    new = (
        "%s# %s: random point within 10 mm of the centre (fresh KAMP mesh follows); centre with a saved mesh\n"
        "%s{%% set q2_rz = 10 if printer['gcode_macro G29'].k|int == 1 else 0 %%}\n"
        "%sG1 X{135 + (range(-q2_rz, q2_rz + 1)|random)} Y{135 + (range(-q2_rz, q2_rz + 1)|random)} F%s\n"
        "%sG28 Z\n" % (ind, MARK, ind, ind, feed, ind))
    body = body[:m.start()] + new + body[m.end():]
    if cmd != "apply":
        print("Ready, run: python3 random_zhome.py apply / gotowe, uruchom apply"); return 0
    if not os.access(path, os.W_OK):
        print("No write permission / brak prawa zapisu. Run / uruchom:")
        print("  sudo HOME=%s python3 %s apply" % (os.path.expanduser("~"), os.path.abspath(__file__))); return 1
    text = text[:a] + body + text[b:]
    bak = path + ".rzhome-" + time.strftime("%Y%m%d-%H%M%S")
    shutil.copy2(path, bak)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text.replace("\n", "\r\n") if crlf else text)
    print("Applied / wgrane. Backup / kopia:", bak)
    print("Now / teraz: FIRMWARE_RESTART"); return 0


sys.exit(main())
