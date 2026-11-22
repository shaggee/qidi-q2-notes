# q2_tweaks – selected fixes from qidi-q2-0204-tweaked, without reflashing

**EN** · [PL – wersja polska niżej](#polski)

For a Q2 whose macros are already customised. Ports a few changes from
[qidi-q2-0204-tweaked](https://github.com/muchak1994-lpg/qidi-q2-0204-tweaked) (GPL-3.0) as exact text
replacements.

| Group | What it does |
|---|---|
| `probe-retry-fix` | probe.py: correct retry handling when "Probe samples exceed tolerance" |
| `box-heater-keepalive` | heaters.py: Box heater fix (already present on some firmware builds) |
| `load-temp-memory` | remembers the temperature of the material left in the nozzle, so loading PLA after PETG pushes the PETG out hot enough (QIDI_Q2 #26). Adds `q2_fila_temp.cfg` and two `_REMEMBER_FILA_TEMP` calls in `PRINT_START` / `PRINT_END` |
| `thr-accel-check` | adds `TWEAKED_THR_CHECK` (read-only toolhead accelerometer / firmware check, see docs/toolhead-accelerometer.md) |

A group is applied only if **all** its anchors are found exactly once; otherwise it is skipped untouched.
LF and CRLF files are handled. Each changed file is backed up as `<file>.q2tw-<date>`.

## Use
Printer idle. Copy the folder to the printer (`scp -r q2_tweaks mks@PRINTER:~/`), then:

```
ssh mks@PRINTER
cd ~/q2_tweaks
python3 q2_tweaks.py check      # read only
python3 q2_tweaks.py apply
sudo systemctl restart klipper  # or FIRMWARE_RESTART in Fluidd
python3 q2_tweaks.py restore    # undo (newest backup of each file)
```

The `.cfg` files are copied to `~/printer_data/config/klipper-macros-qd/`. If your `printer.cfg` does not
include that folder with a wildcard, add `[include klipper-macros-qd/q2_fila_temp.cfg]` and
`[include klipper-macros-qd/q2_thr_check.cfg]`.

Tested on: Q2, firmware 1.1.x with QIDI Box, customised macro file (CRLF).

---

# Polski

## q2_tweaks – wybrane poprawki z qidi-q2-0204-tweaked bez wgrywania firmware

Dla Q2 z już zmienionymi makrami. Przenosi kilka zmian z
[qidi-q2-0204-tweaked](https://github.com/muchak1994-lpg/qidi-q2-0204-tweaked) (GPL-3.0) jako dokładne zamiany tekstu.

| Grupa | Co robi |
|---|---|
| `probe-retry-fix` | probe.py: poprawna obsługa ponowień przy „Probe samples exceed tolerance” |
| `box-heater-keepalive` | heaters.py: poprawka grzałki Boxa (w części wersji firmware już jest) |
| `load-temp-memory` | zapamiętuje temperaturę materiału w dyszy, więc ładowanie PLA po PETG wypycha PETG w odpowiednio wysokiej temperaturze (QIDI_Q2 #26) |
| `thr-accel-check` | dodaje `TWEAKED_THR_CHECK` (sprawdzenie akcelerometru i firmware głowicy, tylko odczyt) |

Grupa jest wgrywana tylko wtedy, gdy **wszystkie** jej miejsca zostaną znalezione dokładnie raz; inaczej jest
pomijana bez zmian. Obsługuje pliki LF i CRLF. Każdy zmieniony plik ma kopię `<plik>.q2tw-<data>`.

Użycie: drukarka bezczynna, skopiuj folder (`scp -r q2_tweaks mks@PRINTER:~/`), potem `check` (tylko odczyt),
`apply`, restart Klippera; `restore` cofa zmiany (polecenia wyżej). Pliki `.cfg` trafiają do
`~/printer_data/config/klipper-macros-qd/`; jeśli `printer.cfg` nie dołącza tego folderu przez `*`, dodaj
`[include ...]` dla obu plików.

Sprawdzone na: Q2, firmware 1.1.x z QIDI Box, zmieniony plik makr (CRLF).
