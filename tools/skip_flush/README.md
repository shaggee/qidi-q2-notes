# skip_flush – skip the Box flush when the slot did not change

**EN** · [PL – wersja polska niżej](#polski)

Applies [macros/print-start-skip-flush.md](../../macros/print-start-skip-flush.md) automatically: if the slot
the print needs (`value_tN`) is the one already loaded (`last_load_slot`), `PRINT_START` skips
`EXTRUSION_AND_FLUSH` (~75 s) and `CLEAR_NOZZLE` does its short purge instead (`PURGE=1`).

Status: 🟡 tested on a copy of the author's macro file (both branches rendered with Klipper's Jinja
delimiters, LF and CRLF, restore). Not yet confirmed on a running print.

Written for the "Superuser Macros: Just Faster Box" macro file; on other macro files the anchors may not
match – the script then changes nothing.

## Use (printer idle)
```
ssh mks@PRINTER
curl -sSLO https://raw.githubusercontent.com/shaggee/qidi-q2-notes/main/tools/skip_flush/skip_flush.py
python3 skip_flush.py check
python3 skip_flush.py apply
```
Then `FIRMWARE_RESTART` in Fluidd. Undo: `python3 skip_flush.py restore` + `FIRMWARE_RESTART`.

Check first that `saved_variables.cfg` stores slots in the same form, e.g. `last_load_slot = 'slot2'` and
`value_t0 = 'slot2'`.

Test: print twice from the same slot – the console shows `Same slot slot2 - skipping flush`.

---

# Polski

## skip_flush – pomija płukanie Boxa, gdy slot się nie zmienił

Wgrywa automatycznie zmianę z [macros/print-start-skip-flush.md](../../macros/print-start-skip-flush.md): jeśli
slot potrzebny do wydruku (`value_tN`) jest już załadowany (`last_load_slot`), `PRINT_START` pomija
`EXTRUSION_AND_FLUSH` (~75 s), a `CLEAR_NOZZLE` robi zamiast tego krótkie płukanie (`PURGE=1`).

Status: 🟡 sprawdzone na kopii pliku makr autora (obie gałęzie, LF i CRLF, przywracanie). Jeszcze niepotwierdzone
na prawdziwym wydruku.

Napisane pod plik makr „Superuser Macros: Just Faster Box”; przy innych makrach miejsca mogą się nie zgadzać –
wtedy skrypt niczego nie zmienia.

Użycie (drukarka bezczynna): polecenia wyżej (`curl`, `check`, `apply`), potem `FIRMWARE_RESTART` we Fluidd.
Cofnięcie: `python3 skip_flush.py restore` + `FIRMWARE_RESTART`.

Najpierw sprawdź, czy `saved_variables.cfg` zapisuje sloty tak samo, np. `last_load_slot = 'slot2'` i
`value_t0 = 'slot2'`. Test: dwa wydruki z tego samego slotu – w konsoli pojawi się `Same slot slot2 - skipping flush`.
