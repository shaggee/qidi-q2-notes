# Changelog

## 2026-11
- Initial version: Orca profile notes, calibration, Z offset, bed leveling, QIDI Box analysis,
  toolhead accelerometer fix log, troubleshooting, security/update blocking.
- Macros: M84 keeping Z, PAUSE stepper fix, z_tilt tolerance, screws_tilt_adjust, PRINT_START same-slot flush skip.
- Orca: purge line in front of the model, per-filament Z offset.
- Tools: q2_tweaks, box_trace.
- All documents bilingual: English first, Polish below.
- INSTALL.md with verified/proposed status, backups and undo; PETG override and layer-change retraction notes; Fluidd tips; skip-flush marked untested.
- tools/skip_flush: automatic install of the same-slot flush skip.
- Troubleshooting: plate scuff from QIDI's stock purge lines (`Z-0.1`).
- KAMP mesh margin: real file `config/KAMP/KAMP_settings.cfg` (root-owned, Fluidd save error), SSH fix; margin was 1.
- Purge line in front of the model verified on the printer.
- tools/hotend_fan: hotend fan hysteresis (port of hotend-fan-hysteresis).
- tools/screen_view: printer screen as a Fluidd camera (service from printer-screen-view).
- tools/random_zhome: random Z re-home point after Z_TILT_ADJUST in PRINT_START.

---

# Polski

## 2026-11
- Pierwsza wersja: profil Orca, kalibracja, offset Z, poziomowanie stołu, analiza QIDI Box, opis naprawy
  akcelerometru głowicy, błędy, bezpieczeństwo i blokada aktualizacji.
- Makra: M84 bez wyłączania Z, poprawka PAUSE, tolerancja z_tilt, screws_tilt_adjust, pomijanie płukania przy tym samym slocie.
- Orca: linia płukania przed modelem, offset Z dla każdego filamentu.
- Narzędzia: q2_tweaks, box_trace.
- Wszystkie dokumenty dwujęzyczne: najpierw angielski, pod spodem polski.
- INSTALL.md ze statusem sprawdzone/propozycja, kopiami i cofaniem; uwagi o nadpisaniach PETG i retrakcji przy zmianie warstwy; wskazówki Fluidd; pomijanie płukania oznaczone jako niesprawdzone.
- tools/skip_flush: automatyczne wgrywanie pomijania płukania przy tym samym slocie.
- Błędy: otarcie płyty przez fabryczne linie płukania QIDI (`Z-0.1`).
- Margines siatki KAMP: właściwy plik `config/KAMP/KAMP_settings.cfg` (należy do root, błąd zapisu we Fluidd), zmiana przez SSH; było 1.
- Linia płukania przed modelem sprawdzona na drukarce.
- tools/hotend_fan: histereza wentylatora hotendu (port hotend-fan-hysteresis).
- tools/screen_view: ekran drukarki jako kamera we Fluidd (usługa z printer-screen-view).
- tools/random_zhome: losowy punkt ponownego bazowania Z po Z_TILT_ADJUST w PRINT_START.
