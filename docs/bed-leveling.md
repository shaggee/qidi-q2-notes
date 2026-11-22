# Bed leveling on the Q2

**EN** · [PL – wersja polska niżej](#polski)

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
The print-start mesh (`BED_MESH_CALIBRATE PROFILE=kamp`) covers only the model area. The margin is set **on the
printer**, not in Orca: Fluidd → *Configuration* → `KAMP_Settings.cfg` → `variable_mesh_margin: 10`, then
Save & Restart. This keeps the brim and the purge line inside the measured area. (Orca's *Adaptive bed mesh*
margin has no effect here – the start G-code does not pass a mesh area to the printer.)

## Do not release the Z motors
With `M84` disabling `stepper_z`/`stepper_z1`, the two lead screws can drift and the bed tilts. The next
print start then scrubs the nozzle at Z−0.2/−1.5 on a tilted bed **before** `Z_TILT_ADJUST`, and z_tilt fails
with `No trigger on probe after full movement`. See [../macros/m84-keep-z.cfg](../macros/m84-keep-z.cfg).
If it already happened: power-cycle (PRINTER_INIT enables Z), `G28`, `Z_TILT_ADJUST`.

## Fluidd
- *Settings → Tool → Invert Z control*: **off**, otherwise the Z arrows move the bed the wrong way.
- *Settings → General / Dashboard*: enable the **Bed mesh** card to see the mesh (3D or flat view,
  "Flat surface" off to see the real shape, scale e.g. ±0.3 mm).
- Mesh range up to ~0.3 mm on this plate is fine; the mesh compensates it.

---

# Polski

## Poziomowanie stołu na Q2

Q2 ma **dwa niezależne silniki Z** (`[z_tilt]`) i cztery śruby stołu (można dodać `[screws_tilt_adjust]`).
Sondą jest dysza (czujnik nacisku).

### Kolejność
Stół ~50 °C, wygrzany 10 min, czysta dysza – polecenia jak w wersji angielskiej powyżej. Po regulacji śrub
sprawdź ponownie pierwszą warstwę (śruby zmieniają wysokość stołu).

### Tolerancja z_tilt
Fabryczne `retry_tolerance: 0.05` akceptowało różnicę 0.046 mm lewo/prawo. Z `retries: 5` i
`retry_tolerance: 0.02` drugi przebieg doszedł do 0.005 mm. Nie schodź poniżej 0.02 (`samples_tolerance` sondy).

### screws_tilt_adjust
Konfiguracja jak wyżej. Gwint M4: 00:15 ≈ 0.18 mm. Śruby poprawiają tylko **pochylenie**; wygięta płyta (wyższy
środek) zostaje i kompensuje ją siatka. Tu pełna siatka miała zakres ~0.25 mm, środek ~0.1–0.14 mm wyżej w osi Y – normalne.

### Margines KAMP
Siatka przy starcie wydruku (`BED_MESH_CALIBRATE PROFILE=kamp`) obejmuje tylko obszar modelu. Margines ustawia się
**na drukarce**, nie w Orce: Fluidd → *Configuration* → `KAMP_Settings.cfg` → `variable_mesh_margin: 10`, potem
Save & Restart. Dzięki temu brim i linia płukania są w zmierzonym obszarze. (Margines *adaptacyjnej siatki* w Orce
tu nic nie zmienia – G-code startowy nie przekazuje drukarce obszaru siatki.)

### Nie wyłączaj silników Z
Gdy `M84` wyłącza `stepper_z`/`stepper_z1`, dwie śruby mogą się przekręcić i stół się przechyla. Następny start
wydruku czyści dyszę na Z−0.2/−1.5 na przechylonym stole **przed** `Z_TILT_ADJUST`, a z_tilt kończy się błędem
`No trigger on probe after full movement`. Rozwiązanie: [../macros/m84-keep-z.cfg](../macros/m84-keep-z.cfg).
Jeśli już się stało: wyłącz i włącz drukarkę (PRINTER_INIT włącza Z), `G28`, `Z_TILT_ADJUST`.

### Fluidd
- *Settings → Tool → Invert Z control*: **wył.**, inaczej strzałki Z ruszają stołem w złą stronę.
- *Settings → General / Dashboard*: włącz kartę **Bed mesh**, żeby widzieć siatkę (widok 3D lub płaski).
- Zakres siatki do ~0.3 mm na tej płycie jest OK; siatka to kompensuje.
