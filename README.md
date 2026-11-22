# QIDI Q2 – notes, macro patches and tools

**EN** · [PL – wersja polska niżej](#polski)

Practical notes from tuning one QIDI Q2 (with a QIDI Box) for good-looking PLA and PETG prints without
making them slow, plus small, reversible changes to the printer's Klipper setup. Everything here was done
on a single printer with **already customised macros**, so read before copying.

> **Unofficial.** Not affiliated with QIDI. Changing printer files is at your own risk. Keep backups.

## Tested on

| | |
|---|---|
| Printer | QIDI Q2 + one QIDI Box |
| Toolhead (THR) firmware | 02.02.01.08 (`1d34b4b0`), bootloader `31f8344d` |
| Main MCU | 02.01.01.09 |
| Slicer | OrcaSlicer 2.5.0 / 2.6.0-dev nightly |
| Filaments | SUNLU PETG, generic / Tecbears PLA (matte), cool plate |

## Start here

**[INSTALL.md](INSTALL.md)** – what to apply, in which order, how to back up and undo, and which changes are verified on the printer.

## What is here

| Folder / file | Content |
|---|---|
| [`docs/orca-profile.md`](docs/orca-profile.md) | OrcaSlicer settings that gave the best quality-to-time ratio, with the reason for each |
| [`docs/calibration.md`](docs/calibration.md) | Calibration order (Z offset → flow → pressure advance → max flow → retraction) and the results |
| [`docs/z-offset.md`](docs/z-offset.md) | How the Q2 stores the Z offset, why it seems to "add up", and per-filament offsets from Orca |
| [`docs/bed-leveling.md`](docs/bed-leveling.md) | `Z_TILT_ADJUST`, `SCREWS_TILT_CALCULATE`, full mesh, KAMP margin |
| [`docs/qidi-box.md`](docs/qidi-box.md) | Box load/unload parameters read from QIDI's code (with the stock values), timings, a failed speed-up |
| [`docs/toolhead-accelerometer.md`](docs/toolhead-accelerometer.md) | Accelerometer fix (383 → 1603 samples/s) done from a Linux host, with real outputs, and the new input shaper values |
| [`docs/troubleshooting.md`](docs/troubleshooting.md) | Errors met on the way and what they meant |
| [`docs/security-and-updates.md`](docs/security-and-updates.md) | ADB root shell off, blocking firmware updates |
| [`macros/`](macros) | Macro changes as small, documented snippets (not whole QIDI files) |
| [`orca/`](orca) | Start G-code (purge line in front of the model) and filament start G-code (Z offset) |
| [`tools/q2_tweaks`](tools/q2_tweaks) | Script that applies selected fixes from qidi-q2-0204-tweaked to a printer with custom macros (check / apply / restore) |
| [`tools/skip_flush`](tools/skip_flush) | Script that makes `PRINT_START` skip the ~75 s Box flush when the slot did not change (check / apply / restore) |
| [`tools/hotend_fan`](tools/hotend_fan) | Hotend fan hysteresis and no false fan alarm on reheat (from qidi-q2-0204-tweaked; check / apply / restore) |
| [`tools/box_trace`](tools/box_trace) | Read-only Klipper module that logs the parameters the QIDI Box code reads, and the G-code it runs |

## Credits

- [qidi-q2-0204-tweaked](https://github.com/muchak1994-lpg/qidi-q2-0204-tweaked) (GPL-3.0): the fixes applied by
  `tools/q2_tweaks` and the toolhead accelerometer procedure.
- [Valve-Oil](https://github.com/thelegendtubaguy/Valve-Oil) (GPL-3.0): the toolhead flasher, ideas for Box tuning.
- [rayaanatif/qidi-q2-accelerometer-fix](https://github.com/rayaanatif/qidi-q2-accelerometer-fix) (GPL-3.0): `lis2dw_patch.py`.
- [Klipper](https://github.com/Klipper3d/klipper), [OrcaSlicer](https://github.com/OrcaSlicer/OrcaSlicer).
- Worked out together with Claude (Anthropic).

## License

GPL-3.0 (see [LICENSE](LICENSE)), because parts are derived from GPL-3.0 projects above.
QIDI's own files are not included.

---

# Polski

## QIDI Q2 – notatki, poprawki makr i narzędzia


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

## Od czego zacząć

**[INSTALL.md](INSTALL.md)** – co wgrać, w jakiej kolejności, jak zrobić kopię i cofnąć zmiany oraz które zmiany są sprawdzone na drukarce.

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
| [`tools/skip_flush`](tools/skip_flush) | Skrypt: `PRINT_START` pomija ~75 s płukania Boxa, gdy slot się nie zmienił (check / apply / restore) |
| [`tools/hotend_fan`](tools/hotend_fan) | Histereza wentylatora hotendu, bez fałszywego alarmu przy ponownym grzaniu (z qidi-q2-0204-tweaked; check / apply / restore) |
| [`tools/box_trace`](tools/box_trace) | Moduł Klippera tylko do odczytu: zapisuje parametry czytane przez kod Boxa QIDI i wykonywany G-code |

Każdy dokument ma najpierw wersję angielską, a pod nią polską.

## Podziękowania

- [qidi-q2-0204-tweaked](https://github.com/muchak1994-lpg/qidi-q2-0204-tweaked) (GPL-3.0): poprawki wgrywane przez `tools/q2_tweaks` i procedura naprawy akcelerometru.
- [Valve-Oil](https://github.com/thelegendtubaguy/Valve-Oil) (GPL-3.0): flasher głowicy, pomysły na strojenie Boxa.
- [rayaanatif/qidi-q2-accelerometer-fix](https://github.com/rayaanatif/qidi-q2-accelerometer-fix) (GPL-3.0): `lis2dw_patch.py`.
- [Klipper](https://github.com/Klipper3d/klipper), [OrcaSlicer](https://github.com/OrcaSlicer/OrcaSlicer).
- Opracowane razem z Claude (Anthropic).

## Licencja

GPL-3.0 (zobacz [LICENSE](LICENSE)), bo część pochodzi z projektów GPL-3.0 wymienionych wyżej. Pliki QIDI nie są dołączone.
