# Installing the changes

**EN** · [PL – wersja polska niżej](#polski)

Each change is independent – take only what you need. Status says what was actually confirmed on the
author's printer:

- ✅ **verified** – applied and working on the printer
- 🟡 **proposed** – written and reviewed, not yet confirmed on the printer

| Change | Status | Difficulty | Section |
|---|---|---|---|
| Per-filament Z offset (Orca) | ✅ | easy | [1](#1-orcaslicer-changes) |
| Orca profile settings | ✅ | easy | [1](#1-orcaslicer-changes) |
| Purge line in front of the model (Orca) | 🟡 | easy | [1](#1-orcaslicer-changes) |
| `z_tilt` tolerance | ✅ | easy | [3](#3-printercfg-changes) |
| `screws_tilt_adjust` | ✅ | easy | [3](#3-printercfg-changes) |
| `M84` keeping Z enabled | ✅ | medium | [4](#4-macro-changes) |
| `PAUSE` stepper message fix | 🟡 (cosmetic) | medium | [4](#4-macro-changes) |
| Skip flush on the same slot | 🟡 | advanced | [4](#4-macro-changes) |
| `q2_tweaks` (probe retry, Box heater, load temperature memory, THR check) | ✅ | easy (script) | [5](#5-tools) |
| `box_trace` | ✅ | easy | [5](#5-tools) |
| Toolhead accelerometer fix | ✅ | advanced, at your own risk | [docs/toolhead-accelerometer.md](docs/toolhead-accelerometer.md) |
| Block firmware updates | 🟡 | easy | [docs/security-and-updates.md](docs/security-and-updates.md) |
| ADB root shell off | 🟡 | easy | [docs/security-and-updates.md](docs/security-and-updates.md) |

## 0. Before you start

- Access: Fluidd (`http://PRINTER`) for config files and the console; SSH for tools
  (`ssh mks@PRINTER`, user with sudo).
- **Backup the whole config** (once, before any change):
  ```
  ssh mks@PRINTER 'cp -a ~/printer_data/config ~/config-backup-$(date +%F)'
  ```
  or in Fluidd: *Configuration* → select all files → *Download*.
- Make changes with the printer **idle** (not printing).
- After a `.cfg` change: *Save & Restart* in the Fluidd editor, or `FIRMWARE_RESTART` in the console.
- **Undo** anything: copy the file back from `~/config-backup-<date>/` and restart.

## 1. OrcaSlicer changes
Nothing on the printer changes, safest place to start.
1. **Per-filament Z offset** – [orca/filament-start-gcode.md](orca/filament-start-gcode.md). Calibrate your
   own value first ([docs/z-offset.md](docs/z-offset.md)).
2. **Profile settings** – [docs/orca-profile.md](docs/orca-profile.md). Save as your own preset
   (*Save as*), do not overwrite the system one.
3. **Purge line** – [orca/start-gcode-purge-line.gcode](orca/start-gcode-purge-line.gcode). In *Printer
   settings → Machine G-code → Machine start G-code* find QIDI's two purge lines after `G4 P3000` and
   replace them. Set *Adaptive bed mesh margin* to 10 mm.

## 2. Find your macro file
QIDI's macro file name differs between firmware versions and custom macro packs. Find the one with
`PRINT_START`:
```
ssh mks@PRINTER 'grep -l "gcode_macro PRINT_START" ~/printer_data/config/*.cfg ~/printer_data/config/*/*.cfg'
```
Typical results: `printer_data/config/gcode_macro.cfg` (stock) or
`printer_data/config/klipper-macros-qd/gcode_macro.cfg`. Open it in Fluidd (*Configuration*).

> The author's printer runs a customised macro pack ("Superuser Macros: Just Faster Box"). Stock QIDI macros
> look similar but not identical. Find the place by its content, not by line number. If you cannot find the
> exact line, skip that change.

## 3. printer.cfg changes
- **z_tilt** – in `printer.cfg`, section `[z_tilt]`, change only `retries` and `retry_tolerance`
  ([macros/z-tilt.cfg](macros/z-tilt.cfg)).
- **screws_tilt_adjust** – add the section from [macros/screws-tilt-adjust.cfg](macros/screws-tilt-adjust.cfg)
  to `printer.cfg` (if it is not there yet). Use: [docs/bed-leveling.md](docs/bed-leveling.md).

Save & Restart, then test: `G28`, `Z_TILT_ADJUST`.

## 4. Macro changes
In the macro file from step 2:
- **M84** – search for `[gcode_macro M84]`. Replace the whole section with
  [macros/m84-keep-z.cfg](macros/m84-keep-z.cfg). If there is no such section, add it at the end of the file.
  Test: `M84` in the console – X/Y are free, the bed (Z) stays locked.
- **PAUSE** – inside `[gcode_macro PAUSE]` search for `STEPPER='box_stepper '` and change that line as in
  [macros/pause-box-stepper.cfg](macros/pause-box-stepper.cfg). Only removes a confusing error message.
- **Skip flush** – [macros/print-start-skip-flush.md](macros/print-start-skip-flush.md). Only for users
  comfortable with Jinja macros; watch the first prints.

## 5. Tools
- **q2_tweaks** – [tools/q2_tweaks/README.md](tools/q2_tweaks/README.md). Run `check` first; it changes nothing
  and shows which groups fit your files.
- **box_trace** – [tools/box_trace/README.md](tools/box_trace/README.md). Diagnostic only.

## Getting the files onto the printer
From the folder where you downloaded/cloned this repository:
```
scp -r tools/q2_tweaks mks@PRINTER:~/
scp tools/box_trace/box_trace.py mks@PRINTER:~/klipper/klippy/extras/
```
Windows (PowerShell) works the same, run it **in the repository folder** (`cd` there first).

---

# Polski

## Instalacja zmian

Każda zmiana jest niezależna – bierz tylko to, czego potrzebujesz. Status mówi, co zostało faktycznie
potwierdzone na drukarce autora:

- ✅ **sprawdzone** – wgrane i działa na drukarce
- 🟡 **propozycja** – napisane i przejrzane, jeszcze niepotwierdzone na drukarce

| Zmiana | Status | Trudność | Sekcja |
|---|---|---|---|
| Offset Z dla każdego filamentu (Orca) | ✅ | łatwa | 1 |
| Ustawienia profilu Orca | ✅ | łatwa | 1 |
| Linia płukania przed modelem (Orca) | 🟡 | łatwa | 1 |
| Tolerancja `z_tilt` | ✅ | łatwa | 3 |
| `screws_tilt_adjust` | ✅ | łatwa | 3 |
| `M84` bez wyłączania Z | ✅ | średnia | 4 |
| Poprawka komunikatu w `PAUSE` | 🟡 (kosmetyka) | średnia | 4 |
| Pomijanie płukania przy tym samym slocie | 🟡 | zaawansowana | 4 |
| `q2_tweaks` | ✅ | łatwa (skrypt) | 5 |
| `box_trace` | ✅ | łatwa | 5 |
| Naprawa akcelerometru głowicy | ✅ | zaawansowana, na własne ryzyko | [docs/toolhead-accelerometer.md](docs/toolhead-accelerometer.md) |
| Blokada aktualizacji | 🟡 | łatwa | [docs/security-and-updates.md](docs/security-and-updates.md) |
| Wyłączenie ADB | 🟡 | łatwa | [docs/security-and-updates.md](docs/security-and-updates.md) |

### 0. Zanim zaczniesz
- Dostęp: Fluidd (`http://PRINTER`) do plików konfiguracji i konsoli; SSH do narzędzi (`ssh mks@PRINTER`, użytkownik z sudo).
- **Kopia całej konfiguracji** (raz, przed zmianami): polecenie `cp -a ...` wyżej albo we Fluidd:
  *Configuration* → zaznacz wszystkie pliki → *Download*.
- Zmiany rób, gdy drukarka **nie drukuje**.
- Po zmianie `.cfg`: *Save & Restart* w edytorze Fluidd albo `FIRMWARE_RESTART` w konsoli.
- **Cofnięcie**: skopiuj plik z `~/config-backup-<data>/` z powrotem i zrestartuj.

### 1. Zmiany w OrcaSlicer
Nic na drukarce się nie zmienia – najbezpieczniej zacząć tutaj.
1. **Offset Z dla filamentu** – [orca/filament-start-gcode.md](orca/filament-start-gcode.md). Najpierw skalibruj
   własną wartość ([docs/z-offset.md](docs/z-offset.md)).
2. **Ustawienia profilu** – [docs/orca-profile.md](docs/orca-profile.md). Zapisz jako własny profil (*Zapisz jako*),
   nie nadpisuj systemowego.
3. **Linia płukania** – [orca/start-gcode-purge-line.gcode](orca/start-gcode-purge-line.gcode). W *Ustawienia
   drukarki → G-code maszyny → Początkowy G-code* znajdź dwie linie płukania QIDI po `G4 P3000` i zamień je.
   Ustaw *Margines adaptacyjnej siatki* na 10 mm.

### 2. Znajdź swój plik makr
Nazwa pliku makr QIDI różni się między wersjami firmware i pakietami makr. Znajdź ten z `PRINT_START`
poleceniem `grep` wyżej. Typowo: `printer_data/config/gcode_macro.cfg` (fabryczny) albo
`printer_data/config/klipper-macros-qd/gcode_macro.cfg`. Otwórz go we Fluidd (*Configuration*).

> Drukarka autora ma zmieniony pakiet makr („Superuser Macros: Just Faster Box”). Fabryczne makra QIDI są
> podobne, ale nie identyczne. Szukaj miejsca po treści, nie po numerze linii. Jeśli nie znajdziesz dokładnie
> tej linii, pomiń tę zmianę.

### 3. Zmiany w printer.cfg
- **z_tilt** – w `printer.cfg`, sekcja `[z_tilt]`, zmień tylko `retries` i `retry_tolerance`
  ([macros/z-tilt.cfg](macros/z-tilt.cfg)).
- **screws_tilt_adjust** – dodaj sekcję z [macros/screws-tilt-adjust.cfg](macros/screws-tilt-adjust.cfg) do
  `printer.cfg` (jeśli jej nie ma). Użycie: [docs/bed-leveling.md](docs/bed-leveling.md).

Save & Restart, potem test: `G28`, `Z_TILT_ADJUST`.

### 4. Zmiany w makrach
W pliku makr z kroku 2:
- **M84** – znajdź `[gcode_macro M84]` i zastąp całą sekcję treścią z
  [macros/m84-keep-z.cfg](macros/m84-keep-z.cfg). Jeśli takiej sekcji nie ma, dodaj ją na końcu pliku.
  Test: `M84` w konsoli – X/Y są luźne, stół (Z) zostaje zablokowany.
- **PAUSE** – w `[gcode_macro PAUSE]` znajdź `STEPPER='box_stepper '` i zmień tę linię jak w
  [macros/pause-box-stepper.cfg](macros/pause-box-stepper.cfg). Usuwa tylko mylący komunikat błędu.
- **Pomijanie płukania** – [macros/print-start-skip-flush.md](macros/print-start-skip-flush.md). Tylko dla osób,
  które czują się pewnie z makrami Jinja; obserwuj pierwsze wydruki.

### 5. Narzędzia
- **q2_tweaks** – [tools/q2_tweaks/README.md](tools/q2_tweaks/README.md). Najpierw `check` – nic nie zmienia
  i pokazuje, które grupy pasują do Twoich plików.
- **box_trace** – [tools/box_trace/README.md](tools/box_trace/README.md). Tylko diagnostyka.

### Kopiowanie plików na drukarkę
Polecenia `scp` wyżej uruchom **w folderze z pobranym repozytorium** (najpierw `cd` do niego). Na Windows
(PowerShell) działa tak samo – ważne, żeby być w tym folderze, inaczej pliki trafią w inne miejsce.
