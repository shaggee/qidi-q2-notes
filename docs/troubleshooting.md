# Errors met on the way

**EN** · [PL – wersja polska niżej](#polski)

| Message | Meaning / fix |
|---|---|
| `!! Malformed command 'SET_VELOCITY_LIMIT SQUARE_CORNER_VELOCITY=9 Z4 E4'` | OrcaSlicer 2.6.0-dev wrote Marlin-style jerk into a Klipper command (PA calibration). Remove ` Z4 E4` from the exported G-code. |
| `!! No trigger on probe after full movement` (at "Start tilt adjust") | The nozzle never touched the bed on one side. Here: Z motors had been released by `M84`, the bed tilted. Power-cycle, `G28`, `Z_TILT_ADJUST`; keep Z enabled ([macros/m84-keep-z.cfg](../macros/m84-keep-z.cfg)). Also clean the nozzle tip. |
| `Retrying homing (1/5) after error: No trigger on z after full movement` | Same family: dirty nozzle / oozing filament damping the load cell. |
| `probe ... z=5.83` then `Probe samples exceed tolerance. Retrying...` | A blob on the nozzle. See also `probe-retry-fix` in [tools/q2_tweaks](../tools/q2_tweaks). |
| `Code:QDE_004_013 Detected wrapping filament` | Filament wrap detection. Check the nozzle; false alarms are common with `noodle_sensitivity_level = 'HIGH'`. |
| Screen: `Defect detected in stir-fried noodles. QDC_500_005_005_002` | Mistranslated AI camera "spaghetti" alarm. Continue if the print is fine. Lower sensitivity: `SAVE_VARIABLE VARIABLE=noodle_sensitivity_level VALUE="'MEDIUM'"` (or disable: `enable_noodle_detection` 0). |
| `SET_STEPPER_ENABLE: Invalid stepper "box_stepper slot0"` | Printed by the `PAUSE` macro (harmless quoting bug, fix in [macros/pause-box-stepper.cfg](../macros/pause-box-stepper.cfg)). It means a pause happened; the cause is the line around it / on the screen. |
| `QDC_100_005_000_001 The filament failed to enter the extruder` | Here caused by changed Box motion values (see qidi-box.md). Restore stock values, cut the tip straight. |
| `idle_timeout: Timeout set to 259200.00 s` | The `PAUSE` macro extends the idle timeout to 72 h. Not an error. |
| Printer draws ~50 W idle after a print | Motors still enabled (+ board fan, which follows the Z steppers). `M84` drops it to ~30 W but see the Z warning above. |
| Filament oozes after stopping | Normal (hot nozzle). Dry PETG; during long pauses lower the nozzle temperature. |
| Brim does not touch the part | Brim gap + elephant-foot compensation; enable *Brim follows compensated outline*. |
| Brim thin / transparent, part bottom fine | Brim outside the KAMP mesh; `variable_mesh_margin: 10` in `KAMP/KAMP_settings.cfg`. |
| "Resume" unloads the filament I loaded and loads the old one | The print is bound to the slot mapping; put the new spool in the same slot. |
| Mark / scuff on the plate at the front edge, around X 154–158 | QIDI's stock Orca start G-code ends each of its two purge lines with `G1 X154 Z-0.1` + `G1 X158`: the nozzle goes 0.1 mm *below* the plate surface and drags 4 mm to break the strand. Change both to `G1 X154 Z0.1`, or use [orca/start-gcode-purge-line.gcode](../orca/start-gcode-purge-line.gcode). |
| Fluidd: *Internal server error* when saving a config file | The file (or its folder) belongs to `root`, Moonraker runs as `qidi` and cannot write it. Example: `config/KAMP/KAMP_settings.cfg`. Edit with `sudo` over SSH or `chown` the folder – see [bed-leveling.md](bed-leveling.md#kamp-mesh-margin). Check with `ls -la`. |
| Nozzle cleaning misses the holes at the rear of the plate (e.g. 1.5 mm towards the door) | `CLEAR_NOZZLE` uses fixed coordinates (`G1 X130 Y280`, then `Y281`, `Y283`), the same as QIDI's. First push the plate fully back against the pins. Find the right Y: `G28`, `G1 Z5`, `G1 X130 Y280`, `G1 Z1`, then `G1 Y281.5` etc. If the offset is the same after several `G28`, shift the three Y values in `CLEAR_NOZZLE` by it (author: +1.5 mm → `Y281.5`, `Y282.5`, `Y284.5`), with `sudo sed` and a backup – not by changing `position_endstop` (that moves the whole Y axis). If it varies, Y sensorless homing is the cause. |
| Fluidd: *Moonraker has failing components: mqtt*, *MQTT Connection Failed: Not authorized* | QIDI cloud client with an expired QIDI Link token. Not caused by HelixScreen. If you do not use QIDI Link, turn it off – see [security-and-updates.md](security-and-updates.md#turning-off-the-qidi-cloud-mqtt). |

---

# Polski

## Napotkane błędy

| Komunikat | Znaczenie / rozwiązanie |
|---|---|
| `!! Malformed command 'SET_VELOCITY_LIMIT ... Z4 E4'` | OrcaSlicer 2.6.0-dev wpisał jerk w stylu Marlina do polecenia Klippera (kalibracja PA). Usuń ` Z4 E4` z G-code. |
| `!! No trigger on probe after full movement` (przy „Start tilt adjust”) | Dysza nie dotknęła stołu po jednej stronie. Tu: `M84` wyłączył silniki Z, stół się przechylił. Wyłącz/włącz, `G28`, `Z_TILT_ADJUST`; trzymaj Z włączone ([macros/m84-keep-z.cfg](../macros/m84-keep-z.cfg)). Wyczyść też czubek dyszy. |
| `Retrying homing (1/5) after error: No trigger on z ...` | Ta sama rodzina: brudna dysza / wyciekający filament tłumi czujnik nacisku. |
| `Probe samples exceed tolerance. Retrying...` | Kulka plastiku na dyszy. Zobacz też `probe-retry-fix` w [tools/q2_tweaks](../tools/q2_tweaks). |
| `Code:QDE_004_013 Detected wrapping filament` | Wykrycie owinięcia filamentu. Sprawdź dyszę; fałszywe alarmy są częste przy czułości `'HIGH'`. |
| Ekran: `Defect detected in stir-fried noodles. QDC_500_005_005_002` | Źle przetłumaczony alarm „spaghetti” z kamery AI. Kontynuuj, jeśli wydruk jest OK. Niższa czułość: `SAVE_VARIABLE VARIABLE=noodle_sensitivity_level VALUE="'MEDIUM'"`. |
| `SET_STEPPER_ENABLE: Invalid stepper "box_stepper slot0"` | Wypisuje makro `PAUSE` (nieszkodliwy błąd cudzysłowów, poprawka w [macros/pause-box-stepper.cfg](../macros/pause-box-stepper.cfg)). Oznacza, że była pauza; przyczyna jest w liniach obok / na ekranie. |
| `QDC_100_005_000_001 The filament failed to enter the extruder` | Tu przez zmienione parametry Boxa (qidi-box.md). Przywróć wartości fabryczne, przytnij końcówkę prosto. |
| `idle_timeout: Timeout set to 259200.00 s` | `PAUSE` wydłuża timeout do 72 h. To nie błąd. |
| Drukarka bierze ~50 W po wydruku | Silniki nadal włączone (+ wentylator płyty, który zależy od silników Z). `M84` zmniejsza do ~30 W, ale uwaga na Z. |
| Filament wycieka po zatrzymaniu | Normalne przy gorącej dyszy. Wysusz PETG; przy długich pauzach obniż temperaturę dyszy. |
| Brim nie dotyka modelu | Odstęp brimu + kompensacja stopy słonia; włącz *Brim podąża za skompensowanym konturem*. |
| Brim cienki / przezroczysty, spód modelu OK | Brim poza siatką KAMP; `variable_mesh_margin: 10` w `KAMP/KAMP_settings.cfg`. |
| „Wznów” wyładowuje włożony filament i ładuje stary | Wydruk jest przypisany do slotu; włóż nową szpulę do tego samego slotu. |
| Ślad / otarcie na płycie przy przedniej krawędzi, około X 154–158 | Fabryczny G-code startowy QIDI w Orce kończy każdą z dwóch linii płukania `G1 X154 Z-0.1` + `G1 X158`: dysza schodzi 0.1 mm *poniżej* płyty i ciągnie 4 mm, żeby urwać nitkę. Zmień obie na `G1 X154 Z0.1` albo użyj [orca/start-gcode-purge-line.gcode](../orca/start-gcode-purge-line.gcode). |
| Fluidd: *Internal server error* przy zapisie pliku konfiguracji | Plik (lub folder) należy do `root`, a Moonraker działa jako `qidi` i nie może go zapisać. Przykład: `config/KAMP/KAMP_settings.cfg`. Edytuj przez SSH z `sudo` albo zmień właściciela folderu – zobacz [bed-leveling.md](bed-leveling.md). Sprawdzenie: `ls -la`. |
| Czyszczenie dyszy nie trafia w otwory z tyłu płyty (np. 1,5 mm w stronę drzwi) | `CLEAR_NOZZLE` ma stałe współrzędne (`G1 X130 Y280`, potem `Y281`, `Y283`), takie jak u QIDI. Najpierw dosuń płytę do kołków z tyłu. Znajdź właściwe Y: `G28`, `G1 Z5`, `G1 X130 Y280`, `G1 Z1`, potem `G1 Y281.5` itd. Jeśli przesunięcie jest takie samo po kilku `G28`, przesuń o nie trzy wartości Y w `CLEAR_NOZZLE` (u autora +1,5 mm → `Y281.5`, `Y282.5`, `Y284.5`) przez `sudo sed` z kopią – nie przez zmianę `position_endstop` (przesuwa całą oś Y). Jeśli się zmienia, winne jest bazowanie Y bez krańcówki. |
| Fluidd: *Moonraker ma niedziałające wtyczki: mqtt*, *MQTT Connection Failed: Not authorized* | Klient chmury QIDI z wygasłym tokenem QIDI Link. Nie powoduje tego HelixScreen. Jeśli nie używasz QIDI Link, wyłącz go – zobacz [security-and-updates.md](security-and-updates.md). |
