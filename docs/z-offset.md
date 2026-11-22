# Z offset on the Q2

**EN** · [PL – wersja polska niżej](#polski)

## How it is stored
- The value lives in `saved_variables.cfg` as `z_offset` (not in `[probe]` / SAVE_CONFIG).
- `PRINT_START` sets the offset to **0** after homing (console: `Z offset = 0`), probes, makes the mesh and
  only then applies the saved value (`set_zoffset`, absolute `SET_GCODE_OFFSET Z=`). "Z offset = 0" in the
  log is therefore normal.
- `PRINT_END` / `CANCEL_PRINT` call `save_zoffset`, which stores the offset **active at the end of the print**.
- Babystepping on the screen changes the active offset **relative to the current one**, and the result is
  saved after the print. Two "+0.1" adjustments on two prints therefore end up as +0.2 – it looks like the
  values add up, but the screen simply shows 0 / the current step at each new print.

Check the real active offset during a print: `GET_POSITION` → `gcode base: ... Z:`.
Set it by hand (printer idle): `SAVE_VARIABLE VARIABLE=z_offset VALUE=0.06`. No restart needed.

Values like `1.3877787807814457e-17` or `0.10000000000000002` are floating point noise (= 0 / 0.1).

## Per-filament offset from OrcaSlicer
PLA liked more squish than PETG here (calibrated +0.035 vs +0.12). Instead of changing the printer value
for each material, put an **absolute** offset in each filament's *Advanced → Filament start G-code*:

```
SET_GCODE_OFFSET Z=0.05 MOVE=1    ; PLA
SET_GCODE_OFFSET Z=0.12 MOVE=1    ; PETG
```

- It runs after `PRINT_START`, so it overrides the saved value; nothing accumulates.
- It also runs at **every filament change** from the Box, so screen babysteps during a print are lost at the
  next change – adjust the profile instead.
- Prints not sliced in Orca use the saved value (whatever the last print left there).

## Calibrating
- Print a 50×50 mm square **2–3 layers high**, not a single layer: a one-layer test is first *and* top layer
  for Orca and does not look like the bottom of a real part (0.5 mm first-layer lines, 100% fill).
- Steps of 0.05, then 0.01–0.025.
- Good: lines slightly flattened, touching, smooth to the touch, faint line pattern visible, sharp edges.
  Too low: transparent/ridged lines, elephant foot, scraping. Too high: round lines with gaps.
- The brim is part of the first layer and uses the same offset. A thin brim with a good part bottom points to
  the mesh margin (see bed-leveling.md), not to the offset.

---

# Polski

## Offset Z na Q2

### Jak jest zapisywany
- Wartość jest w `saved_variables.cfg` jako `z_offset` (nie w `[probe]` / SAVE_CONFIG).
- `PRINT_START` po bazowaniu ustawia offset na **0** (konsola: `Z offset = 0`), mierzy, robi siatkę i dopiero
  potem wczytuje zapisaną wartość (`set_zoffset`, bezwzględne `SET_GCODE_OFFSET Z=`). „Z offset = 0” w logu jest normalne.
- `PRINT_END` / `CANCEL_PRINT` wywołują `save_zoffset`, które zapisuje offset **aktywny na końcu wydruku**.
- Korekta na ekranie zmienia offset **względem obecnego**, a wynik zapisuje się po wydruku. Dwie korekty „+0.1”
  na dwóch wydrukach dają +0.2 – wygląda, jakby się sumowało, ale ekran przy każdym wydruku pokazuje 0 / bieżący krok.

Prawdziwy aktywny offset w trakcie druku: `GET_POSITION` → `gcode base: ... Z:`.
Ręczne ustawienie (drukarka bezczynna): `SAVE_VARIABLE VARIABLE=z_offset VALUE=0.06`. Restart niepotrzebny.

Wartości typu `1.3877787807814457e-17` lub `0.10000000000000002` to szum zmiennoprzecinkowy (= 0 / 0.1).

### Offset dla każdego filamentu z OrcaSlicer
PLA potrzebowało większego docisku niż PETG (skalibrowane +0.035 vs +0.12). Zamiast zmieniać wartość w drukarce
przy każdej zmianie materiału, wpisz **bezwzględny** offset w *Ustawienia filamentu → Zaawansowane →
G-code startowy filamentu*:

```
SET_GCODE_OFFSET Z=0.05 MOVE=1    ; PLA
SET_GCODE_OFFSET Z=0.12 MOVE=1    ; PETG
```

- Wykonuje się po `PRINT_START`, więc nadpisuje zapisaną wartość; nic się nie sumuje.
- Wykonuje się też przy **każdej zmianie filamentu** z Boxa, więc korekty z ekranu w trakcie druku znikną przy
  następnej zmianie – poprawiaj profil.
- Wydruki spoza Orki używają wartości zapisanej (tej, którą zostawił ostatni wydruk).

### Kalibracja
- Drukuj kwadrat 50×50 mm o wysokości **2–3 warstw**, nie jedną warstwę: jednowarstwowy test jest dla Orki
  jednocześnie pierwszą i górną warstwą i nie wygląda jak spód prawdziwej części.
- Kroki 0.05, potem 0.01–0.025.
- Dobrze: linie lekko spłaszczone, stykają się, gładkie w dotyku, widoczny delikatny wzór, ostre krawędzie.
  Za nisko: przezroczyste/prążkowane linie, stopa słonia, skrobanie. Za wysoko: okrągłe linie ze szczelinami.
- Brim jest częścią pierwszej warstwy i ma ten sam offset. Cienki brim przy dobrym spodzie modelu wskazuje na
  margines siatki (bed-leveling.md), a nie na offset.
