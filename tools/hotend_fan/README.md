# hotend_fan – hotend fan hysteresis, no false fan alarm on reheat

**EN** · [PL – wersja polska niżej](#polski)

Port of `hotend-fan-hysteresis` from [qidi-q2-0204-tweaked](https://github.com/muchak1994-lpg/qidi-q2-0204-tweaked)
(GPL-3.0) as a standalone script, without its firmware 02.04 checksum check.

**Problem:** the hotend fan (`[heater_fan hotend_fan]`, 50 °C) switches on/off around 50 °C with no hysteresis,
and a reheat while the fan is running can raise a false fan alarm (the RPM watchdog is not re-armed).

**Change** (`klippy/extras/fan.py`, `heater_fan.py`, only for the Q2 hotend fan; every other fan is unchanged):
- the fan switches off 5 °C below the switch-on point (45 °C instead of 50 °C);
- the fan also runs when the hotend temperature is unknown (stale reading);
- the RPM check restarts correctly after a reheat, and a raised alarm is not cleared by mistake.

Both files are changed only if **all 9 anchors** are found exactly once. LF and CRLF files. Backups
`<file>.hfan-<date>`.

Status: 🟡 tested on QIDI's public Q2 Klipper source (all anchors, compiles, LF/CRLF, restore).
Not yet on the author's printer.

## Use (printer idle)
```
ssh mks@PRINTER
cd /tmp
curl -sSLO https://raw.githubusercontent.com/shaggee/qidi-q2-notes/main/tools/hotend_fan/hotend_fan.py
python3 hotend_fan.py check
python3 hotend_fan.py apply          # if not writable, the script prints the sudo command
sudo systemctl restart klipper       # FIRMWARE_RESTART does not reload .py files
```
Undo: `python3 hotend_fan.py restore` + `sudo systemctl restart klipper`.

Check: heat the nozzle to 200 °C, set it to 0 – the fan keeps running down to ~45 °C (before: ~50 °C).
No "fan" error on a reheat while the fan is still running.

---

# Polski

## hotend_fan – histereza wentylatora hotendu, bez fałszywego alarmu przy ponownym grzaniu

Moduł `hotend-fan-hysteresis` z [qidi-q2-0204-tweaked](https://github.com/muchak1994-lpg/qidi-q2-0204-tweaked)
(GPL-3.0) jako osobny skrypt, bez sprawdzania sumy kontrolnej firmware 02.04.

**Problem:** wentylator hotendu (`[heater_fan hotend_fan]`, 50 °C) włącza się i wyłącza w okolicy 50 °C bez
histerezy, a ponowne grzanie przy pracującym wentylatorze może dać fałszywy alarm wentylatora.

**Zmiana** (`klippy/extras/fan.py`, `heater_fan.py`, tylko dla wentylatora hotendu Q2; inne wentylatory bez zmian):
- wentylator wyłącza się 5 °C niżej, niż się włącza (45 °C zamiast 50 °C);
- wentylator pracuje też, gdy temperatura hotendu jest nieznana (nieaktualny odczyt);
- kontrola obrotów startuje poprawnie po ponownym grzaniu, a zgłoszony alarm nie jest kasowany przez pomyłkę.

Oba pliki zmieniane są tylko wtedy, gdy znaleziono **wszystkie 9 miejsc** dokładnie raz. Pliki LF i CRLF.
Kopie `<plik>.hfan-<data>`.

Status: 🟡 sprawdzone na publicznym źródle Klippera QIDI dla Q2 (wszystkie miejsca, kompilacja, LF/CRLF,
przywracanie). Jeszcze nie na drukarce autora.

Użycie (drukarka bezczynna): polecenia wyżej (`curl`, `check`, `apply`, `sudo systemctl restart klipper` –
`FIRMWARE_RESTART` nie przeładowuje plików .py). Cofnięcie: `python3 hotend_fan.py restore` + restart Klippera.

Sprawdzenie: nagrzej dyszę do 200 °C, ustaw 0 – wentylator pracuje do ~45 °C (wcześniej ~50 °C). Brak błędu
wentylatora przy ponownym grzaniu, gdy wentylator jeszcze się kręci.
