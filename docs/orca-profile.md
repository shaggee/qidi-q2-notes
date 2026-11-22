# OrcaSlicer profile for the Q2 (quality without slow prints)

Starting point: QIDI's `0.20mm Standard @Qidi Q2` process. Names below are the English Orca names, with the
Polish UI name in brackets where it helps.

## The time trap

A first "quality" version (3 walls, Gyroid, wall order Inner/Outer/Inner, unlimited detours, slow outer wall)
turned a **16 h 23 min** print into **23 h 11 min**. Orca's legend (Preview → Line type) showed where:

| Feature | Before | After | Cause |
|---|---|---|---|
| Inner wall | 2h46 | 5h30 | 3 walls instead of 2 |
| Sparse infill | 5h15 | 7h36 | Gyroid: Klipper slows down on every curve (square corner velocity 8–9) |
| Travel | 1h41 | 2h34 | unlimited detours around walls |

Also: **Precise wall is ignored with Inner/Outer/Inner wall order** (Orca shows a warning).
Cross Hatch was slower than Grid on that model as well (7h00 vs 5h15).

Final result: **17 h 15 min**, with better seams and overhangs.

## Settings kept

### Quality
| Setting | Value | Why |
|---|---|---|
| Seam position | Aligned / Back | |
| Staggered inner seams | on | |
| Scarf joint seam | Contour, **Conditional scarf joint** on | invisible seam only where it cannot hide in a corner |
| Wipe inward | on (Expert) | wipe goes into the part, no scar next to the seam; needs *Wipe while retracting* |
| Wipe before external loop | on | |
| Arc fitting | **Disabled** | Klipper |
| Precise wall | on | works only with Inner/Outer, not Inner/Outer/Inner |
| Wall generator | Arachne | |
| Maximum wall resolution | 0.2 mm | smoother curves |
| Wall order | **Inner/Outer** | |
| Only one wall on top surfaces | on | |
| Avoid crossing walls | on, **max detour 100%** | fewer strings (PETG) without huge detours |
| Small area flow compensation | on (default model) | |
| Print unsupported walls last, extra perimeters on overhangs, reverse on even | on | |
| Reverse only internal perimeters | on, threshold 50% | |

### Strength
| Setting | Value | Why |
|---|---|---|
| Wall loops | **2** (3 only for strong parts) | 3rd wall cost ~3 h on a big print |
| Bottom shell layers | 4 | |
| Sparse infill pattern | **Grid** | fastest on Klipper; no real nozzle-catch problem with Z-hop |
| Apply gap fill | Top and bottom surfaces | no holes on top |

### Speed (PLA / PETG process)
| Setting | PLA | PETG |
|---|---|---|
| Outer wall | 120 mm/s | 80–100 mm/s |
| Inner wall | 200 | 150 |
| Sparse infill | 250 (capped by the filament's max volumetric speed) | same |
| Top surface | 100 | 60–80 |
| Gap infill | 60–100 | 60 |
| Slow down for curled perimeters | **off** (costs a lot of time on big parts) | off |

Accelerations after the accelerometer fix and a new input shaper calibration
(X 3hump_ei 93.2 Hz, Y mzv 47.2 Hz, suggested max ≈ 6000 mm/s²):

| Setting | Value |
|---|---|
| Normal printing | 6000 |
| Outer wall | 4000 |
| Inner wall | 5000 |
| Top surface | 3000 |

### Others
| Setting | Value | Why |
|---|---|---|
| Brim type | none for PLA; **Mouse ear** for large flat PETG parts | |
| Brim-object gap | 0.1 mm | |
| Brim follows compensated outline | **on** | without it the elephant-foot compensation (0.15) widens the real gap to ~0.35 mm and the brim does not touch the part |
| Support top Z distance | 0.25 mm (PETG), 0.2 (PLA) | |
| Support top interface spacing | 0.2 mm, 3 layers, ironing on | smoother underside over supports |

### Printer settings
- **Adaptive bed mesh margin: 10 mm.** With 0 the KAMP mesh covers only the model, so the brim and the purge
  line are printed on an unmeasured area (thin, transparent brim lines).
- **Max jerk X/Y = `square_corner_velocity` from printer.cfg** (8 on this printer).

## Filament profiles

### PLA (cool plate)
| Setting | Value |
|---|---|
| Nozzle | 210 °C |
| Bed (Cool Plate / Textured Cool Plate) | 45 / 40 °C (plate rating 30–50 °C) |
| Flow ratio, pressure advance, max volumetric speed, retraction | from calibration (see calibration.md) |
| Aux part fan | 40% (20% if big flat parts lift at the corners) |

### SUNLU PETG
| Setting | Value |
|---|---|
| Nozzle | 250 / 245 °C |
| Bed | 65 / 60 °C on the cool plate (rating 50–70 °C), glue stick as release agent |
| Flow ratio | 0.93 |
| Pressure advance | 0.07 |
| Max volumetric speed | 12–13 mm³/s |
| Retraction length | 0.4 mm (no stringing even at 0.2 in the test) |
| Fan max | 40%, overhangs/bridges 90% |
| Min print speed | 20 mm/s |

## Matte PLA note

Matte PLA changes sheen with speed: slower spots look glossier. Keep the outer wall speed even (small
perimeters 70–80% instead of 50%) if you see glossy patches on small details.
