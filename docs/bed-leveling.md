# Bed leveling on the Q2

The Q2 has **two independent Z motors** (`[z_tilt]`) and four bed screws (`[screws_tilt_adjust]` can be
added). The nozzle is the probe (load cell).

## Order
Bed at ~50 °C, soaked 10 min, nozzle clean:

```
G28
Z_TILT_ADJUST
G28 Z
SCREWS_TILT_CALCULATE        ; adjust screws, repeat until all < 00:05
G28
Z_TILT_ADJUST
G28 Z
BED_MESH_CALIBRATE PROFILE=default
SAVE_CONFIG
```

Then re-check the first layer (screws change the bed height).

## z_tilt tolerance
Stock `retry_tolerance: 0.05` accepted a 0.046 mm left/right difference. With

```
[z_tilt]
retries: 5
retry_tolerance: 0.02
```

the second pass reached 0.005 mm. Do not go below 0.02 (the probe's own `samples_tolerance`).

## screws_tilt_adjust
```
[screws_tilt_adjust]
horizontal_move_z: 10
screw_thread: CW-M4
speed: 50
screw1: 30,30
screw1_name: front left
screw2: 240,30
screw2_name: front right
screw3: 240,240
screw3_name: rear right
screw4: 30,240
screw4_name: rear left
```
M4 thread: 00:15 ≈ 0.18 mm. Screws only fix **tilt**; a bowed plate (centre higher) stays and is handled by
the mesh. Here the full mesh range was ~0.25 mm with the centre ~0.1–0.14 mm higher in Y – normal.

## KAMP mesh margin
The print-start mesh covers only the model area. Set *Printer → Basic information → Adaptive bed mesh
margin = 10 mm* in Orca so the brim and the purge line are inside the measured area.

## Do not release the Z motors
With `M84` disabling `stepper_z`/`stepper_z1`, the two lead screws can drift and the bed tilts. The next
print start then scrubs the nozzle at Z−0.2/−1.5 on a tilted bed **before** `Z_TILT_ADJUST`, and z_tilt fails
with `No trigger on probe after full movement`. See [../macros/m84-keep-z.cfg](../macros/m84-keep-z.cfg).
If it already happened: power-cycle (PRINTER_INIT enables Z), `G28`, `Z_TILT_ADJUST`.
