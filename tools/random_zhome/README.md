# random_zhome – random Z re-home point in PRINT_START

**EN** · [PL – wersja polska niżej](#polski)

The Q2 homes Z by pressing the nozzle on the plate. `z-home-random-point` (qidi-q2-0204-tweaked) already
randomises **Home All**, but the author's `PRINT_START` re-homes Z after `Z_TILT_ADJUST` always at the centre:
```
G1 X135 Y135 F12000
G28 Z
```
This script changes that move to a random point within 10 mm of the centre (X/Y 125–145), with the same rule:
random only with a fresh KAMP mesh every print (`G29 k=1`), centre with a saved mesh (`k=0`). The mesh is measured
right after this homing, so the first layer is unaffected.

Written for the "Superuser Macros: Just Faster Box" macro file (stock QIDI `PRINT_START` has no such re-home);
if the pattern is not found exactly once in `PRINT_START`, nothing is changed. Backup `<file>.rzhome-<date>`.

Status: 🟡 tested on a copy of the author's macro file (rendered with Klipper's Jinja delimiters for k=1 and k=0,
CRLF). Not yet on the printer.

## Use (printer idle)
```
cd /tmp
curl -sSLO https://raw.githubusercontent.com/shaggee/qidi-q2-notes/main/tools/random_zhome/random_zhome.py
python3 random_zhome.py check
python3 random_zhome.py apply        # if not writable, the script prints the sudo command
```
Then `FIRMWARE_RESTART`. Undo: `python3 random_zhome.py restore` + `FIRMWARE_RESTART`.

---

# Polski

## random_zhome – losowy punkt ponownego bazowania Z w PRINT_START

Q2 bazuje Z, dociskając dyszę do płyty. `z-home-random-point` (qidi-q2-0204-tweaked) losuje już punkt przy
**Home All**, ale `PRINT_START` autora po `Z_TILT_ADJUST` bazuje Z ponownie zawsze na środku (`G1 X135 Y135` +
`G28 Z`). Skrypt zmienia ten przejazd na losowy punkt do 10 mm od środka (X/Y 125–145), z tą samą zasadą: losowo
tylko przy świeżej siatce KAMP przy każdym wydruku (`G29 k=1`), na środku przy zapisanej siatce (`k=0`). Siatka jest
mierzona zaraz po tym bazowaniu, więc pierwsza warstwa na tym nie traci.

Napisane pod plik makr „Superuser Macros: Just Faster Box” (fabryczny `PRINT_START` QIDI nie ma tego bazowania);
jeśli wzorca nie ma dokładnie raz w `PRINT_START`, nic nie jest zmieniane. Kopia `<plik>.rzhome-<data>`.

Status: 🟡 sprawdzone na kopii pliku makr autora (renderowanie dla k=1 i k=0, CRLF). Jeszcze nie na drukarce.

Użycie (drukarka bezczynna): polecenia wyżej (`curl`, `check`, `apply`), potem `FIRMWARE_RESTART`.
Cofnięcie: `python3 random_zhome.py restore` + `FIRMWARE_RESTART`.
