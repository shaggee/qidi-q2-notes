# QIDI Box on the Q2: what the code does and what can be tuned

**EN** · [PL – wersja polska niżej](#polski)

## Where the logic lives
`T_MANAGER`, `BOX_PRINT_START`, `E_LOAD`, `E_UNLOAD`, `CUT_FILAMENT`, `CLEAR_FLUSH`, `CLEAR_OOZE` are **not
macros**. They are compiled Cython modules in `~/klipper/klippy/extras/` (`box_extras.so`, `box_stepper.so`,
`multi_color_controller.so`, `box2base.so`, ...). `box.cfg` only holds pins and hardware.

In the firmware this printer runs, the module strings are zlib-compressed (Cython 3.2,
`CYTHON_COMPRESS_STRINGS`); decompressing the string table shows the embedded G-code, e.g. fixed
`G4 P5000` waits, `M109` heating in the unload/eject flows and purges like `G1 E100 F600`.
`multi_color_controller.so` implements a step flow (`EXT_HEAT`, `EXT_CUT`, `EXT_UNLOAD`, `EXT_LOAD`,
`EXT_WIPE`, `EXT_BITE`, `BOX_*`).

## Motion parameters
`box_stepper.so` reads its motion through `box_extras.get_value_by_key(key, default)`, which looks the key up
in `saved_variables`. The stock values below were captured with
[`tools/box_trace`](../tools/box_trace) (`BOX_TRACE REPORT=1` after a load/unload):

| Key | Stock | Meaning (as far as observed) |
|---|---|---|
| `load_hub_length_1` / `_speed` / `_accel` | 200 / 80 / 50 | spool → hub |
| `extruder_load_length_1` / `_speed` / `_accel` | 3000 / 10 / 50 | (stage not identified) |
| `extruder_load_length_2` / `_speed` / `_accel` | 660 / 100 / 300 | fast push through the tube |
| `extruder_load_length_3` / `_speed` / `_accel` | 350 / 10 / 50 | slow approach to the toolhead sensor |
| `exl_1` / `exl_1_speed` | 30 / 300 | extruder pull-back, part 1 |
| `exl_2` / `exl_2_speed` | 120 / 600 | extruder pull-back, part 2 |
| `extruder_unload_length_1` / `_speed` / `_accel` | -1200 / 100 / 50 | Box pulls back to the hub |
| `extruder_unload_length_2` / `_speed` / `_accel` | -260 / 80 / 50 | hub → park |
| `buffer_init_length_1` / `_2` | 3 / 6 | buffer |

### A speed-up that failed
Valve-Oil uses a 25 mm/s approach and a 55 mm `exl_2` on the Max 4 (same toolhead). On this Q2:

```
SAVE_VARIABLE VARIABLE=extruder_load_length_3_speed VALUE=20
SAVE_VARIABLE VARIABLE=exl_2 VALUE=60
```

led to `QDC_100_005_000_001` "The filament failed to enter the extruder" – the filament did not even reach
the slow stage. Most likely the shorter `exl_2` left the tip in the extruder gears while the Box pulled it
back, deforming it. **Restore the stock values** (above) if you try this; do not change two values at once;
on the Q2 I would leave both at stock.

## Print start timings (log, 9 prints)
| Phase | Time |
|---|---|
| Homing | 40–48 s |
| Box (`BOX_PRINT_START`) | 36–46 s, ~2 min when the slot changes |
| Flush (`EXTRUSION_AND_FLUSH`) | **~75 s on every print**, even with the same slot |
| Nozzle cleaning | 67–74 s |
| Bed temperature wait | ~14 s |
| Z tilt | 28–35 s |

Skipping the flush when the slot did not change saves ~55 s per print:
[../macros/print-start-skip-flush.md](../macros/print-start-skip-flush.md).

## Slots during a paused print
`RESUME` reloads the slot mapped to the current tool (`value_t0`, `value_t1`, ... in `saved_variables`),
not the filament you loaded by hand. To continue with another spool, put it **in the same slot**.
Changing the mapping during a pause (`SAVE_VARIABLE VARIABLE=value_t0 VALUE="'slot2'"`) was not verified.

## Cold unload / cut
The cut itself (`CUT_FILAMENT_1`) has no extruder move and works cold. The Box unload heats the nozzle
inside the closed code; Valve-Oil's cold unload wraps specific Max 4 / Plus 5 builds and does not apply to the
Q2. Lowering `min_extrude_temp` does not help and removes a safety check.

---

# Polski

## QIDI Box na Q2: co robi kod i co można stroić

### Gdzie jest logika
`T_MANAGER`, `BOX_PRINT_START`, `E_LOAD`, `E_UNLOAD`, `CUT_FILAMENT`, `CLEAR_FLUSH`, `CLEAR_OOZE` to **nie makra**,
tylko skompilowane moduły Cython w `~/klipper/klippy/extras/` (`box_extras.so`, `box_stepper.so`,
`multi_color_controller.so`, `box2base.so`, ...). `box.cfg` zawiera tylko piny i sprzęt.

W tym firmware napisy w modułach są skompresowane zlib (Cython 3.2); po dekompresji widać wbudowany G-code, np.
stałe czekanie `G4 P5000`, grzanie `M109` przy rozładunku i płukanie typu `G1 E100 F600`.
`multi_color_controller.so` realizuje przepływ kroków (`EXT_HEAT`, `EXT_CUT`, `EXT_UNLOAD`, `EXT_LOAD`, `EXT_WIPE`, ...).

### Parametry ruchu
`box_stepper.so` czyta ruch przez `box_extras.get_value_by_key(klucz, domyślna)`, która szuka klucza w
`saved_variables`. Wartości fabryczne w tabeli wyżej odczytano narzędziem [`tools/box_trace`](../tools/box_trace).

### Nieudane przyspieszenie
Valve-Oil na Max 4 (ta sama głowica) używa podejścia 25 mm/s i `exl_2` = 55 mm. Na tym Q2 ustawienie
`extruder_load_length_3_speed=20` i `exl_2=60` dało błąd `QDC_100_005_000_001` „The filament failed to enter the
extruder” – filament nie doszedł nawet do etapu zwalniania. Najpewniej krótsze `exl_2` zostawiło końcówkę w kołach
ekstrudera, gdy Box ją cofał, i ją zdeformowało. **Przywróć wartości fabryczne**, nie zmieniaj dwóch wartości naraz;
na Q2 zostawiłbym obie fabryczne.

### Czasy startu wydruku (log, 9 wydruków)
Bazowanie 40–48 s, Box 36–46 s (~2 min przy zmianie slotu), płukanie **~75 s przy każdym wydruku**, nawet z tym
samym slotem, czyszczenie dyszy 67–74 s, czekanie na stół ~14 s, Z tilt 28–35 s.
Pominięcie płukania przy niezmienionym slocie oszczędza ~55 s: [../macros/print-start-skip-flush.md](../macros/print-start-skip-flush.md).

### Sloty przy pauzie
`RESUME` ładuje slot przypisany do narzędzia (`value_t0`, `value_t1`, ... w `saved_variables`), a nie filament
włożony ręcznie. Żeby kontynuować inną szpulą, włóż ją **do tego samego slotu**. Zmiana przypisania w trakcie pauzy
(`SAVE_VARIABLE VARIABLE=value_t0 VALUE="'slot2'"`) nie była sprawdzona.

### Rozładunek na zimno / cięcie
Samo cięcie (`CUT_FILAMENT_1`) nie rusza ekstruderem i działa na zimno. Rozładunek Boxa grzeje dyszę w zamkniętym
kodzie; zimny rozładunek z Valve-Oil dotyczy konkretnych wersji Max 4 / Plus 5, nie Q2. Obniżanie
`min_extrude_temp` nie pomaga i usuwa zabezpieczenie.
