# HelixScreen on the Q2 (recommended screen UI)

**EN** · [PL – wersja polska niżej](#polski)

[HelixScreen](https://github.com/prestonbrown/helixscreen) (GPL-3.0) is a touch UI for Klipper printers that
officially supports the QIDI Q2 on the printer's own screen: native 480×272 layouts, QIDI Box (slots, mapping,
load/unload, drying), power-loss recovery, print-start step tracking, Wi-Fi setup, calibrations. It replaces QIDI's
screen program (`qidi-client`) while installed. It supersedes the [qbdisplay_q2](../tools/qbdisplay_q2) prototype.

Status on the author's Q2: ✅ v1.1.0-rc.3 working (2026-11-23): touch calibration done, Box slots show the
material and colour set in Fluidd. Box load/unload from the screen not yet tested.

**Use HelixScreen 1.1 or newer with the QIDI Box.** On 1.0.11 (stable) slots saved in the Box's new format
(`filament_slot0 = 'QFL81'`, `color_slot0 = ['060606']`) show as grey "--". 1.1 reads them. The stable
in-app updater does not offer 1.1 yet, so install it over SSH (settings are kept):
```bash
curl -sSL https://releases.helixscreen.org/install.sh -o /tmp/helix-install.sh
sudo sh /tmp/helix-install.sh --version v1.1.0-rc.3 --dry-run   # check the plan
sudo sh /tmp/helix-install.sh --version v1.1.0-rc.3
```
Then set **Settings > Updates > Update Channel > Beta**.

**Slot edits from HelixScreen:** it still saves numeric ids, which the Box firmware ignores, so Fluidd
showed "PLA Basic #FAFAFA". Install [helix_box_bridge](../tools/helix_box_bridge) to forward them as
`UPDATE_FILAMENT_INFORMATION`. Brands outside QIDI/Generic (e.g. eSun, Tecbears) can only be set in Fluidd.

**Tool mapping (T0–T3 labels):** these come from `value_t0..3` in `saved_variables.cfg`, set by the last
print's filament mapping. Back to 1:1 from the Fluidd console:
`SAVE_VARIABLE VARIABLE=value_t0 VALUE='"slot0"'` (and t1→slot1, t2→slot2, t3→slot3).

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

## Polish translation

A full Polish translation (`pl.yml`, all 6235 strings) is in [`helixscreen-pl/`](../helixscreen-pl/). Accepted upstream ([#2162](https://github.com/prestonbrown/helixscreen/pull/2162), cherry-picked into main and release/1.1): **Polish (Polski) is in the language list from HelixScreen 1.1.1.** A review of the strings the maintainer added later: [#2194](https://github.com/prestonbrown/helixscreen/pull/2194) (main) and [#2195](https://github.com/prestonbrown/helixscreen/pull/2195) (release/1.1, for 1.1.2).

---

# Polski

## HelixScreen na Q2 (zalecany interfejs ekranu)

[HelixScreen](https://github.com/prestonbrown/helixscreen) (GPL-3.0) to interfejs dotykowy dla drukarek z Klipperem,
który oficjalnie obsługuje QIDI Q2 na ekranie drukarki: układy pod 480×272, QIDI Box (sloty, przypisania,
ładowanie/rozładowanie, suszenie), wznawianie po zaniku prądu, śledzenie kroków startu, ustawianie Wi-Fi,
kalibracje. Na czas instalacji zastępuje program ekranu QIDI (`qidi-client`). Zastępuje prototyp
[qbdisplay_q2](../tools/qbdisplay_q2). Brak języka polskiego (9 języków).

Status na Q2 autora: ✅ v1.1.0-rc.3 działa (2026-11-23): kalibracja dotyku zrobiona, sloty Boxa pokazują
materiał i kolor ustawione we Fluidd. Ładowanie/rozładowanie Boxa z ekranu jeszcze niesprawdzone.

**Z QIDI Boxem używaj HelixScreen 1.1 lub nowszego.** W 1.0.11 (stabilnej) sloty zapisane w nowym formacie
Boxa (`filament_slot0 = 'QFL81'`, `color_slot0 = ['060606']`) są szare z „--”. Wersja 1.1 je odczytuje.
Aktualizacja w aplikacji na kanale stabilnym jeszcze jej nie proponuje, więc zainstaluj ją przez SSH
(ustawienia zostają):
```bash
curl -sSL https://releases.helixscreen.org/install.sh -o /tmp/helix-install.sh
sudo sh /tmp/helix-install.sh --version v1.1.0-rc.3 --dry-run   # sprawdź plan
sudo sh /tmp/helix-install.sh --version v1.1.0-rc.3
```
Potem ustaw **Ustawienia > Aktualizacje > Update Channel > Beta**.

**Zmiana slotów w HelixScreen:** nadal zapisuje numery, które firmware Boxa ignoruje, więc Fluidd pokazywał
„PLA Basic #FAFAFA”. Zainstaluj [helix_box_bridge](../tools/helix_box_bridge), który przekazuje je jako
`UPDATE_FILAMENT_INFORMATION`. Marki spoza QIDI/Generic (np. eSun, Tecbears) ustawisz tylko we Fluidd.

**Przypisanie narzędzi (etykiety T0–T3):** pochodzi z `value_t0..3` w `saved_variables.cfg` i ustawia je
mapowanie filamentów ostatniego wydruku. Powrót do 1:1 z konsoli Fluidd:
`SAVE_VARIABLE VARIABLE=value_t0 VALUE='"slot0"'` (oraz t1→slot1, t2→slot2, t3→slot3).

Instalacja, deinstalacja i ostrzeżenia instalatora – polecenia i opis wyżej. Najważniejsze:
- przyciski Wyłącz/Restart na ekranie mogą nie działać (brak reguły polkit);
- aktualizacje przez HelixScreen (*Settings → Updates*) albo `--update`, nie przez Fluidd;
- w czasie działania nie działa synchronizacja Boxa w QIDI Studio, chmura QIDI i edycja filamentów z aplikacji QIDI.

**DRM czy framebuffer (podgląd we Fluidd):** na Q2 HelixScreen wybiera DRM, więc `/dev/fb0` trzyma ostatni obraz
QIDI i `screen_view` pokazuje stary ekran. Najlepiej włączyć wbudowane udostępnianie (*Settings → Connection →
Screen Sharing*) – kamera „HelixScreen Screen” we Fluidd, działa z DRM i da się klikać; potem usuń `screen_view`.
Albo wymuś framebuffer: w `helixscreen.env` odkomentuj `HELIX_DISPLAY_BACKEND=fbdev` i zrestartuj HelixScreen –
sprawdzone na Q2 autora.

## Polskie tłumaczenie

Pełne polskie tłumaczenie (`pl.yml`, wszystkie 6235 tekstów) jest w [`helixscreen-pl/`](../helixscreen-pl/). Przyjęte przez autora ([#2162](https://github.com/prestonbrown/helixscreen/pull/2162), włączone do main i release/1.1): **język polski jest na liście od HelixScreen 1.1.1.** Przegląd tekstów dodanych później przez autora: [#2194](https://github.com/prestonbrown/helixscreen/pull/2194) (main) i [#2195](https://github.com/prestonbrown/helixscreen/pull/2195) (release/1.1, do 1.1.2).
