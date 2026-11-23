# HelixScreen on the Q2 (recommended screen UI)

**EN** · [PL – wersja polska niżej](#polski)

[HelixScreen](https://github.com/prestonbrown/helixscreen) (GPL-3.0) is a touch UI for Klipper printers that
officially supports the QIDI Q2 on the printer's own screen: native 480×272 layouts, QIDI Box (slots, mapping,
load/unload, drying), power-loss recovery, print-start step tracking, Wi-Fi setup, calibrations. It replaces QIDI's
screen program (`qidi-client`) while installed. It supersedes the [qbdisplay_q2](../tools/qbdisplay_q2) prototype.

Status on the author's Q2: 🟡 installed (v1.0.11, 2026-11-23), Box detected; touch calibration and Box
load/unload not yet tested.

## Install (printer idle)
```
curl -sSL https://releases.helixscreen.org/install.sh | sh
```
Then the first-run wizard on the screen: touch calibration, language, network, connection `127.0.0.1:7125`,
model **QIDI Q2**. Uninstall (brings QIDI's screen back):
```
curl -sSL https://releases.helixscreen.org/install.sh | sh -s -- --uninstall
```

## What the installer said on the Q2
- `Failed to install power-off/reboot polkit rule` – Shutdown/Reboot buttons on the screen may be refused.
- `This Moonraker predates release_info.json asset_name support` – no update entry in Fluidd (on purpose: it
  could delete HelixScreen). Update in HelixScreen (*Settings → Updates*) or with `--update`.
- While it runs, QIDI Studio box sync, QIDI cloud and Box filament edits from QIDI's apps do not work.

## DRM vs framebuffer (screen preview in Fluidd)
On the Q2 HelixScreen picks **DRM** (`/dev/dri/card0` + GPU `renderD128`). Then `/dev/fb0` keeps the last QIDI
picture and [tools/screen_view](../tools/screen_view) shows that old image. Options:
- **Built-in screen sharing (preferred):** on the printer *Settings → Connection → Screen Sharing* → *Share Screen*
  (optionally *Allow Remote Control*). It adds a **HelixScreen Screen** webcam to Fluidd and
  `http://PRINTER/helixscreen/screen/`, works with DRM and can be clicked. Then remove `screen_view`.
- **Force framebuffer:** in `printer_data/config/helixscreen/helixscreen.env` the line exists commented out –
  uncomment it (`HELIX_DISPLAY_BACKEND=fbdev`), `sudo systemctl restart helixscreen`. `screen_view` then works.
  Checked on the author's Q2.

Check which one runs: `sudo ls -l /proc/$(pgrep -x helix-screen)/fd | grep -E "fb0|dri"` (wait ~15 s after a
restart – a launcher and a watchdog start first).

---

# Polski

## HelixScreen na Q2 (zalecany interfejs ekranu)

[HelixScreen](https://github.com/prestonbrown/helixscreen) (GPL-3.0) to interfejs dotykowy dla drukarek z Klipperem,
który oficjalnie obsługuje QIDI Q2 na ekranie drukarki: układy pod 480×272, QIDI Box (sloty, przypisania,
ładowanie/rozładowanie, suszenie), wznawianie po zaniku prądu, śledzenie kroków startu, ustawianie Wi-Fi,
kalibracje. Na czas instalacji zastępuje program ekranu QIDI (`qidi-client`). Zastępuje prototyp
[qbdisplay_q2](../tools/qbdisplay_q2). Brak języka polskiego (9 języków).

Status na Q2 autora: 🟡 zainstalowany (v1.0.11, 2026-11-23), Box wykryty; kalibracja dotyku i
ładowanie/rozładowanie Boxa jeszcze niesprawdzone.

Instalacja, deinstalacja i ostrzeżenia instalatora – polecenia i opis wyżej. Najważniejsze:
- przyciski Wyłącz/Restart na ekranie mogą nie działać (brak reguły polkit);
- aktualizacje przez HelixScreen (*Settings → Updates*) albo `--update`, nie przez Fluidd;
- w czasie działania nie działa synchronizacja Boxa w QIDI Studio, chmura QIDI i edycja filamentów z aplikacji QIDI.

**DRM czy framebuffer (podgląd we Fluidd):** na Q2 HelixScreen wybiera DRM, więc `/dev/fb0` trzyma ostatni obraz
QIDI i `screen_view` pokazuje stary ekran. Najlepiej włączyć wbudowane udostępnianie (*Settings → Connection →
Screen Sharing*) – kamera „HelixScreen Screen” we Fluidd, działa z DRM i da się klikać; potem usuń `screen_view`.
Albo wymuś framebuffer: w `helixscreen.env` odkomentuj `HELIX_DISPLAY_BACKEND=fbdev` i zrestartuj HelixScreen –
sprawdzone na Q2 autora.
