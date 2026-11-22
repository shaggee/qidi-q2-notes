#!/usr/bin/env python3
# screen_view.py - install the "printer screen view" service: the printer's touch screen as a camera in Fluidd.
# PL: instaluje usługę "podgląd ekranu drukarki": ekran dotykowy drukarki jako kamera we Fluidd.
#
# Service code (q2_screen.py, q2-screen.service) from qidi-q2-0204-tweaked, module printer-screen-view
# (https://github.com/muchak1994-lpg/qidi-q2-0204-tweaked, GPL-3.0). LOOK ONLY: nothing is written to the
# screen, no touch. Listens on 127.0.0.1:8083 only; nginx serves it as /webcam4/?action=snapshot.
# Fluidd's files are NOT changed - you add the picture as a camera in Fluidd's settings.
#
#   sudo python3 screen_view.py check       read only / tylko odczyt
#   sudo python3 screen_view.py install
#   sudo python3 screen_view.py uninstall
import os
import re
import shutil
import subprocess
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = "/usr/local/lib/q2-screen"
LIB = LIB_DIR + "/q2_screen.py"
UNIT = "/etc/systemd/system/q2-screen.service"
NGINX_DIRS = ["/etc/nginx/sites-enabled", "/etc/nginx/conf.d", "/etc/nginx/sites-available"]
PORT = 8083


def fb_ok():
    try:
        size = open("/sys/class/graphics/fb0/virtual_size").read().strip()
        bpp = open("/sys/class/graphics/fb0/bits_per_pixel").read().strip()
    except OSError as e:
        return False, "screen not readable / ekran nieczytelny: %s" % e
    return bpp == "32", "screen / ekran: %s, %s bit" % (size, bpp)


def nginx_ok():
    """True if location /webcam4/ proxies to 127.0.0.1:8083 (directly or through an upstream)."""
    texts = []
    for d in NGINX_DIRS:
        if os.path.isdir(d):
            for n in sorted(os.listdir(d)):
                p = os.path.join(d, n)
                if os.path.isfile(p):
                    try:
                        texts.append(open(p, encoding="utf-8", errors="replace").read())
                    except OSError:
                        pass
    allt = "\n".join(texts)
    m = re.search(r"location\s+/webcam4/\s*\{(.*?)\}", allt, re.S)
    if not m:
        return False, "nginx: no 'location /webcam4/' / brak 'location /webcam4/'"
    pp = re.search(r"proxy_pass\s+http://([^/;\s]+)", m.group(1))
    if not pp:
        return False, "nginx: /webcam4/ has no proxy_pass / brak proxy_pass"
    target = pp.group(1)
    if target in ("127.0.0.1:%d" % PORT, "localhost:%d" % PORT):
        return True, "nginx: /webcam4/ -> %s" % target
    up = re.search(r"upstream\s+%s\s*\{(.*?)\}" % re.escape(target), allt, re.S)
    if up and re.search(r"server\s+(127\.0\.0\.1|localhost):%d\b" % PORT, up.group(1)):
        return True, "nginx: /webcam4/ -> upstream %s -> 127.0.0.1:%d" % (target, PORT)
    return False, "nginx: /webcam4/ -> %s, not 127.0.0.1:%d / nie 127.0.0.1:%d" % (target, PORT, PORT)


def port_state():
    out = subprocess.run(["ss", "-ltnp"], capture_output=True, text=True).stdout
    lines = [l for l in out.splitlines() if ":%d " % PORT in l]
    if not lines:
        return "free"
    return "ours" if "python" in " ".join(lines) and os.path.exists(UNIT) else "taken"


def fetch(url):
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            data = r.read()
            return data[:8] == b"\x89PNG\r\n\x1a\n", len(data)
    except Exception as e:
        return False, str(e)


def check():
    ok = True
    for good, msg in (fb_ok(), nginx_ok()):
        print(("  OK    " if good else "  FAIL  ") + msg)
        ok &= good
    st = port_state()
    print(("  OK    " if st != "taken" else "  FAIL  ") + "port %d: %s" % (PORT, st))
    ok &= st != "taken"
    for name in ("q2_screen.py", "q2-screen.service"):
        present = os.path.exists(os.path.join(HERE, name))
        print(("  OK    " if present else "  FAIL  ") + "%s next to this script / obok skryptu" % name)
        ok &= present
    return ok


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd in ("install", "uninstall") and os.geteuid() != 0:
        print("Run with sudo / uruchom przez sudo: sudo python3 %s %s" % (os.path.abspath(__file__), cmd))
        return 1
    if cmd == "uninstall":
        subprocess.run(["systemctl", "disable", "--now", "q2-screen.service"])
        for p in (UNIT, LIB):
            if os.path.exists(p):
                os.remove(p)
                print("removed / usunięto:", p)
        if os.path.isdir(LIB_DIR) and not os.listdir(LIB_DIR):
            os.rmdir(LIB_DIR)
        subprocess.run(["systemctl", "daemon-reload"])
        print("Done / gotowe. Remove the camera in Fluidd too / usuń też kamerę we Fluidd.")
        return 0
    print("Checks / sprawdzenie:")
    if not check():
        print("Nothing changed / nic nie zmieniono")
        return 1
    if cmd != "install":
        print("Ready, run: sudo python3 screen_view.py install / gotowe, uruchom install")
        return 0
    os.makedirs(LIB_DIR, exist_ok=True)
    shutil.copy(os.path.join(HERE, "q2_screen.py"), LIB)
    os.chmod(LIB, 0o755)
    shutil.copy(os.path.join(HERE, "q2-screen.service"), UNIT)
    os.chmod(UNIT, 0o644)
    subprocess.run(["systemctl", "daemon-reload"], check=True)
    subprocess.run(["systemctl", "enable", "--now", "q2-screen.service"], check=True)
    subprocess.run(["systemctl", "restart", "q2-screen.service"], check=True)
    import time
    time.sleep(2)
    for url in ("http://127.0.0.1:%d/?action=snapshot" % PORT, "http://127.0.0.1/webcam4/?action=snapshot"):
        good, info = fetch(url)
        print(("  OK    " if good else "  FAIL  ") + "%s -> %s" % (url, "PNG %s bytes" % info if good else info))
    print("\nFluidd: Settings -> Cameras -> Add camera / Dodaj kamerę:")
    print("  Name / Nazwa: Printer screen")
    print("  Stream type / Typ: MJPEG Adaptive   (or / lub: HTTP page / Snapshot)")
    print("  Stream URL / Snapshot URL: /webcam4/?action=snapshot")
    print("  Target FPS: 2")
    return 0


sys.exit(main())
