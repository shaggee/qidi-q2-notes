# skip_flush – skip the Box flush when the slot did not change

**EN** · [PL – wersja polska niżej](#polski)

Applies [macros/print-start-skip-flush.md](../../macros/print-start-skip-flush.md) automatically: if the slot
the print needs (`value_tN`) is the one already loaded (`last_load_slot`), `PRINT_START` skips
`EXTRUSION_AND_FLUSH` (~75 s) and `CLEAR_NOZZLE` does its short purge instead (`PURGE=1`).

Status: ✅ verified on the author's Q2 (2026-11-22): `Same slot slot2 - skipping flush` in the console,
nozzle cleaning right after. Also tested on a copy of the macro file (both branches, LF and CRLF, restore).

Written for the "Superuser Macros: Just Faster Box" macro file; on other macro files the anchors may not
match – the script then changes nothing.

## Use (printer idle)
```
ssh mks@PRINTER
curl -sSLO https://raw.githubusercontent.com/shaggee/qidi-q2-notes/main/tools/skip_flush/skip_flush.py
python3 skip_flush.py check
python3 skip_flush.py apply
```
If the file is not writable for your user, the script stops and prints
`sudo HOME=/home/mks python3 /tmp/skip_flush.py apply` (download to `/tmp` if your home folder is read-only).
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

Status: ✅ sprawdzone na Q2 autora (2026-11-22): `Same slot slot2 - skipping flush` w konsoli, zaraz po tym
czyszczenie dyszy. Testowane też na kopii pliku makr (obie gałęzie, LF i CRLF, przywracanie).

Napisane pod plik makr „Superuser Macros: Just Faster Box”; przy innych makrach miejsca mogą się nie zgadzać –
wtedy skrypt niczego nie zmienia.

Użycie (drukarka bezczynna): polecenia wyżej (`curl`, `check`, `apply`), potem `FIRMWARE_RESTART` we Fluidd.
Gdy plik nie jest zapisywalny dla Twojego użytkownika, skrypt się zatrzyma i podpowie
`sudo HOME=/home/mks python3 /tmp/skip_flush.py apply` (pobierz do `/tmp`, jeśli folder domowy jest tylko do odczytu).
Cofnięcie: `python3 skip_flush.py restore` + `FIRMWARE_RESTART`.

Najpierw sprawdź, czy `saved_variables.cfg` zapisuje sloty tak samo, np. `last_load_slot = 'slot2'` i
`value_t0 = 'slot2'`. Test: dwa wydruki z tego samego slotu – w konsoli pojawi się `Same slot slot2 - skipping flush`.
