# box_trace – read-only tracing of the QIDI Box

**EN** · [PL – wersja polska niżej](#polski)

Shows which motion parameters the closed Box modules read from `saved_variables` (key, QIDI's default,
returned value) and, optionally, every G-code script with timestamps to time a filament change.
Changes nothing.

## Install
```
scp box_trace.py mks@PRINTER:~/klipper/klippy/extras/
```
Add to `printer.cfg`:
```
[box_trace]
```
Restart Klipper. Do a filament load/unload, then in the console:
```
BOX_TRACE REPORT=1     ; parameters read so far
BOX_TRACE SCRIPTS=1    ; log scripts to klippy.log (SCRIPTS=0 to stop)
```

## Remove
Delete the `[box_trace]` section and the file, restart Klipper.

Results on a Q2: see [docs/qidi-box.md](../../docs/qidi-box.md).

---

# Polski

## box_trace – podgląd działania QIDI Box (tylko odczyt)

Pokazuje, jakie parametry ruchu zamknięte moduły Boxa czytają z `saved_variables` (klucz, wartość domyślna QIDI,
zwrócona wartość) i opcjonalnie każdy skrypt G-code z czasem, żeby zmierzyć zmianę filamentu. Niczego nie zmienia.

Instalacja: skopiuj `box_trace.py` do `~/klipper/klippy/extras/`, dodaj `[box_trace]` do `printer.cfg`, zrestartuj
Klippera. Po załadowaniu/rozładowaniu filamentu: `BOX_TRACE REPORT=1` (parametry), `BOX_TRACE SCRIPTS=1`
(zapis skryptów do klippy.log, `SCRIPTS=0` wyłącza).

Usunięcie: skasuj sekcję `[box_trace]` i plik, zrestartuj Klippera. Wyniki: [docs/qidi-box.md](../../docs/qidi-box.md).
