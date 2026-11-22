# Per-filament Z offset (Filament settings → Advanced → Filament start G-code)

Absolute value, overrides the offset saved by the printer; nothing accumulates. Calibrate your own values
(see docs/z-offset.md). Values on this printer:

PLA:
```
SET_GCODE_OFFSET Z=0.05 MOVE=1
```

PETG:
```
SET_GCODE_OFFSET Z=0.12 MOVE=1
```

Keep the existing lines of the filament start G-code; add this as the last line.
