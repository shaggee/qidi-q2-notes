# Per-filament Z offset (Filament settings → Advanced → Filament start G-code)

**EN** · [PL – wersja polska niżej](#polski)

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

---

# Polski

## Offset Z dla każdego filamentu (Ustawienia filamentu → Zaawansowane → G-code startowy filamentu)

Wartość bezwzględna, nadpisuje offset zapisany w drukarce; nic się nie sumuje. Skalibruj własne wartości
(docs/z-offset.md). Na tej drukarce: PLA `Z=0.05`, PETG `Z=0.12` (polecenia wyżej). Zostaw istniejące linie
G-code startowego filamentu i dodaj to jako ostatnią linię.
