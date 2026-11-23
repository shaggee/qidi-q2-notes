#!/usr/bin/env python3
# qbdisplay_q2.py - install qbdisplay (QIDI Plus4 display UI by CharlyBrownFR) on the QIDI Q2. PROTOTYPE.
#
#   sudo python3 qbdisplay_q2.py check      read only
#   sudo python3 qbdisplay_q2.py install    download + install (QIDI screen stays active)
#   sudo python3 qbdisplay_q2.py start      qbdisplay on the screen (stops qidi-client)
#   sudo python3 qbdisplay_q2.py stop       back to QIDI's screen
#   sudo python3 qbdisplay_q2.py log        last log lines
#   sudo python3 qbdisplay_q2.py uninstall
#
# Nothing is flashed. The service is NOT enabled at boot: after a reboot QIDI's screen is back.
import io
import os
import shutil
import subprocess
import sys
import tarfile
import urllib.request

UPSTREAM = "CharlyBrownFR/qbdisplay-plus4"
COMMIT = "4c97e38acc04849431b2b49bcb648ccf2d3f1b1e"      # 2026-11-21, qbdisplay 0.3.0
TARBALL = "https://codeload.github.com/%s/tar.gz/%s" % (UPSTREAM, COMMIT)
HERE = os.path.dirname(os.path.abspath(__file__))
FILES = os.path.join(HERE, "files")
RAW = "https://raw.githubusercontent.com/shaggee/qidi-q2-notes/main/tools/qbdisplay_q2/files/"
OURS = ["fbdisplay.py", "q2main.py", "pl.py", "qbdisplay-q2.cfg", "qbdisplay-q2.service"]
LIB = "/usr/local/lib/qbdisplay-q2"
UNIT = "/etc/systemd/system/qbdisplay-q2.service"
CFG = "/home/mks/printer_data/config/qbdisplay.cfg"


def sh(*cmd, check=False):
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def need_root():
    if os.geteuid() != 0:
        print("Run with sudo: sudo python3 %s %s" % (os.path.abspath(__file__), sys.argv[1]))
        sys.exit(1)


def ours(name):
    """Our file next to this script (files/...), else downloaded from the repository."""
    p = os.path.join(FILES, name)
    if os.path.exists(p):
        return open(p, "rb").read()
    with urllib.request.urlopen(RAW + name, timeout=30) as r:
        return r.read()


def check():
    ok = True

    def line(good, msg):
        nonlocal ok
        print(("  OK    " if good else "  FAIL  ") + msg)
        ok &= good
    try:
        size = open("/sys/class/graphics/fb0/virtual_size").read().strip()
        bpp = open("/sys/class/graphics/fb0/bits_per_pixel").read().strip()
        line(bpp == "32", "screen: %s, %s bit" % (size, bpp))
    except OSError as e:
        line(False, "screen: %s" % e)
    line(os.path.exists("/dev/input/event0"), "touch: /dev/input/event0")
    r = sh("python3", "-c", "import PIL; print(PIL.__version__)")
    line(r.returncode == 0, "PIL: %s" % (r.stdout.strip() or r.stderr.strip()[-80:]))
    r = sh("systemctl", "cat", "qidi-client.service")
    line(r.returncode == 0, "QIDI screen program: qidi-client.service")
    line(os.path.isdir("/home/mks/printer_data/config"), "config folder")
    avail = 0
    for l in open("/proc/meminfo"):
        if l.startswith("MemAvailable:"):
            avail = int(l.split()[1]) // 1024
    line(avail >= 120, "free memory: %d MB (need >= 120)" % avail)
    return ok


def install():
    need_root()
    print("Checks:")
    if not check():
        print("Nothing changed")
        return 1
    print("Downloading %s @ %s ..." % (UPSTREAM, COMMIT[:8]))
    with urllib.request.urlopen(TARBALL, timeout=120) as r:
        data = r.read()
    tmp = LIB + ".new"
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp)
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tf:
        for m in tf.getmembers():
            parts = m.name.split("/", 1)
            if len(parts) < 2 or not parts[1] or m.issym() or m.islnk() or ".." in parts[1].split("/"):
                continue
            if not (parts[1].startswith("qbdisplay/") or parts[1].startswith("tjc-projekt/")
                    or parts[1] in ("LICENSE", "README.md", "qbdisplay.example.cfg")):
                continue
            m.name = parts[1]
            tf.extract(m, tmp)
    for name in ("fbdisplay.py", "q2main.py", "pl.py"):
        with open(os.path.join(tmp, "qbdisplay", name), "wb") as f:
            f.write(ours(name))
    sh("chown", "-R", "root:root", tmp)
    sh("chmod", "-R", "go-w", tmp)
    shutil.rmtree(LIB, ignore_errors=True)
    os.rename(tmp, LIB)
    with open(UNIT, "wb") as f:
        f.write(ours("qbdisplay-q2.service"))
    os.chmod(UNIT, 0o644)
    if not os.path.exists(CFG):
        with open(CFG, "wb") as f:
            f.write(ours("qbdisplay-q2.cfg"))
        st = os.stat(os.path.dirname(CFG))
        os.chown(CFG, st.st_uid, st.st_gid)
        print("Config:", CFG)
    else:
        print("Config kept:", CFG)
    sh("systemctl", "daemon-reload")
    r = sh("python3", "-c", "import sys; sys.path.insert(0, %r); import qbdisplay.q2main" % LIB)
    print(("  OK    " if r.returncode == 0 else "  FAIL  ") + "import qbdisplay.q2main " + r.stderr.strip()[-200:])
    print("\nInstalled. QIDI's screen is unchanged.")
    print("Try it:  sudo python3 %s start" % os.path.abspath(__file__))
    return 0


def start():
    need_root()
    sh("systemctl", "start", "qbdisplay-q2.service")
    import time
    time.sleep(4)
    print(sh("systemctl", "is-active", "qbdisplay-q2.service", "qidi-client.service").stdout)
    return log()


def stop():
    need_root()
    sh("systemctl", "stop", "qbdisplay-q2.service")
    sh("systemctl", "start", "qidi-client.service")
    print(sh("systemctl", "is-active", "qbdisplay-q2.service", "qidi-client.service").stdout)
    return 0


def log():
    print(sh("journalctl", "-u", "qbdisplay-q2.service", "-n", "40", "--no-pager").stdout)
    return 0


def uninstall():
    need_root()
    stop()
    for p in (UNIT,):
        if os.path.exists(p):
            os.remove(p)
    shutil.rmtree(LIB, ignore_errors=True)
    sh("systemctl", "daemon-reload")
    print("Removed. Config left in place:", CFG)
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    fn = {"check": lambda: 0 if check() else 1, "install": install, "start": start,
          "stop": stop, "log": log, "uninstall": uninstall}.get(cmd)
    sys.exit(fn() if fn else print(__doc__ or "check | install | start | stop | log | uninstall") or 1)
