# Errors met on the way

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
| Brim thin / transparent, part bottom fine | Brim outside the KAMP mesh; set adaptive mesh margin 10 mm. |
| "Resume" unloads the filament I loaded and loads the old one | The print is bound to the slot mapping; put the new spool in the same slot. |
