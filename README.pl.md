# QIDI Q2 – notatki, poprawki makr i narzędzia

[English](README.md) · **Polski**

Praktyczne notatki z ustawiania jednej drukarki QIDI Q2 (z QIDI Box) tak, żeby PLA i PETG wyglądały dobrze,
a druk nie był wolny, oraz małe, odwracalne zmiany w konfiguracji Klippera. Wszystko robione na jednej drukarce
z **już zmienionymi makrami**, więc przeczytaj przed skopiowaniem.

> **Projekt nieoficjalny.** Niezwiązany z QIDI. Zmiany w plikach drukarki na własne ryzyko. Rób kopie.

## Na czym sprawdzone

| | |
|---|---|
| Drukarka | QIDI Q2 + jeden QIDI Box |
| Firmware głowicy (THR) | 02.02.01.08 (`1d34b4b0`), bootloader `31f8344d` |
| MCU główne | 02.01.01.09 |
| Slicer | OrcaSlicer 2.5.0 / 2.6.0-dev (nightly) |
| Filamenty | SUNLU PETG, PLA (w tym matowe Tecbears), płyta cool plate |

## Zawartość

| Folder / plik | Co zawiera |
|---|---|
| [`docs/orca-profile.md`](docs/orca-profile.md) | Ustawienia OrcaSlicer z najlepszym stosunkiem jakości do czasu, z uzasadnieniem |
| [`docs/calibration.md`](docs/calibration.md) | Kolejność kalibracji (offset Z → przepływ → PA → maks. przepływ → retrakcja) i wyniki |
| [`docs/z-offset.md`](docs/z-offset.md) | Jak Q2 zapisuje offset Z, dlaczego „się sumuje” i offset per filament z Orki |
| [`docs/bed-leveling.md`](docs/bed-leveling.md) | `Z_TILT_ADJUST`, `SCREWS_TILT_CALCULATE`, pełna siatka, margines KAMP |
| [`docs/qidi-box.md`](docs/qidi-box.md) | Parametry ładowania/rozładowania Boxa odczytane z kodu QIDI (z wartościami fabrycznymi), czasy, nieudana próba przyspieszenia |
| [`docs/toolhead-accelerometer.md`](docs/toolhead-accelerometer.md) | Naprawa akcelerometru (383 → 1603 próbek/s) z hosta Linux, z prawdziwymi wynikami, i nowe wartości Input Shapera |
| [`docs/troubleshooting.md`](docs/troubleshooting.md) | Napotkane błędy i co znaczyły |
| [`docs/security-and-updates.md`](docs/security-and-updates.md) | Wyłączenie ADB (root bez hasła), blokada aktualizacji |
| [`macros/`](macros) | Zmiany w makrach jako małe, opisane fragmenty (nie całe pliki QIDI) |
| [`orca/`](orca) | Początkowy G-code (linia płukania przed modelem) i G-code filamentu (offset Z) |
| [`tools/q2_tweaks`](tools/q2_tweaks) | Skrypt wgrywający wybrane poprawki z qidi-q2-0204-tweaked na drukarkę ze zmienionymi makrami (check / apply / restore) |
| [`tools/box_trace`](tools/box_trace) | Moduł Klippera tylko do odczytu: zapisuje parametry czytane przez kod Boxa QIDI i wykonywany G-code |

Dokumenty w `docs/` są po angielsku, żeby mogła z nich korzystać szersza społeczność.

## Podziękowania i licencja

Zobacz [README.md](README.md). Licencja GPL-3.0. Pliki QIDI nie są dołączone.
