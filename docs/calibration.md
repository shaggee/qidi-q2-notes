# Calibration (per filament)

Order that worked best:

1. **Z offset** (first layer) – see [z-offset.md](z-offset.md)
2. Temperature tower (optional, new filament)
3. **Flow ratio** – Orca *Calibration → Flow rate → YOLO (Recommended)*
4. **Pressure advance** – *Pattern* method, DDE
5. **Max volumetric speed**
6. **Retraction**

Flow first: the PA pattern judges corners, which depend on how much material comes out. If flow changes by
more than ~0.03 after PA was done, repeat PA in a narrow range.

## Flow ratio (YOLO)
- Judge the cooled top surfaces under side light and with a finger. Pick the smoothest square: no gaps
  between lines, no ridges, flat centre of the spiral.
- **New flow = current flow + value printed on the square** (e.g. 0.95 − 0.02 = 0.93).
- Write it in *Filament → Flow ratio* of the "Direct drive SF" variant tab.

## Pressure advance (Pattern)
| Filament | Start | End | Step | Result here |
|---|---|---|---|---|
| PETG | 0 (0.05 for a re-check) | 0.08 (0.09) | 0.005 | **0.07** |
| PLA | 0 | 0.06 | 0.005 | typically 0.02–0.04 |

Tick *Print numbers*, leave accelerations/speeds empty. Pick the sharpest corner with even line width.
Enable it in *Filament → Enable pressure advance*; otherwise the printer uses `pressure_advance` from
printer.cfg (0.032 here) for every filament.

## Max volumetric speed
- Start 10, end 25, step 1 mm³/s (PETG).
- Read the height where the wall turns **matte** (earliest sign), then
  `flow = start + height_mm × step`, minus ~10% (or 15–20% if you read it where gaps appear).
- PETG here: 13 → set 12.

## Retraction
- Range 0.2–1.2 mm, step 0.1 (the test tower is in Orca's Calibration menu).
- PETG here had **no strings even at 0.2**, set 0.4 mm as a margin. Lower is better than higher on PETG.
- If PETG strings later, dry it first (65 °C, 4–6 h) before increasing retraction.

## OrcaSlicer 2.6.0-dev quirk
The nightly once produced `SET_VELOCITY_LIMIT SQUARE_CORNER_VELOCITY=9 Z4 E4` in the PA test, which Klipper
rejects (`Malformed command`). Setting jerk Z/E to 0 did not help; removing ` Z4 E4` from the exported G-code
did. Later exports were fine. Check the exported file if a calibration print stops at the start.

## The calibration wizard shows N/A
The Bambu-style wizard ("Flow dynamics calibration") needs a printer agent connection; with a plain
Moonraker print host it only sends the file. Use the *Calibration* menu tests on the plate instead and read
the result yourself.
