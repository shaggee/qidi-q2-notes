# PRINT_START: skip the Box flush when the slot did not change

> **Verified** on the author's Q2 (2026-11-22): console showed `Same slot slot2 - skipping flush`, nozzle cleaning followed directly.
> Automatic version: [tools/skip_flush](../tools/skip_flush).

**EN** · [PL – wersja polska niżej](#polski)

Stock `PRINT_START` runs `EXTRUSION_AND_FLUSH` (~75 s) on every print. If the slot needed by the print is
already loaded (`last_load_slot` in `saved_variables`), the flush is pointless.

Edit `PRINT_START` in QIDI's macro file (`klipper-macros-qd/gcode_macro.cfg` or `gcode_macro.cfg`). Make a
backup first. Line names differ slightly between firmware versions – find the matching places.

1. At the top of the macro, after the other `{% set ... %}` lines:
   ```
   {% set sv = printer.save_variables.variables %}
   {% set target_slot = sv['value_t' ~ extruder]|default('') %}
   {% set same_slot = target_slot != '' and target_slot == sv.last_load_slot|default('none') %}
   ```
2. Replace the flush after `BOX_PRINT_START`:
   ```
   BOX_PRINT_START EXTRUDER={extruder} HOTENDTEMP={hotendtemp}
   M400
   {% if same_slot %}
       M118 Same slot {target_slot} - skipping flush
   {% else %}
       SET_PRINT_SUB_STATUS SUB_STATUS=flush_filament
       EXTRUSION_AND_FLUSH HOTEND={hotendtemp}
   {% endif %}
   ```
3. If the macro computes a `box_flushed` variable later, add `and not same_slot` to it:
   ```
   {% set box_flushed = printer.save_variables.variables.box_count >= 1 and printer["box_extras"] and printer.save_variables.variables.enable_box == 1 and not same_slot %}
   ```

The logic is simple, but check the first prints (console shows `Same slot slotN - skipping flush`).
Old filament residue in the nozzle is then purged only by the purge line – fine for the same spool, do a
manual flush after a long break with wet PETG.

---

# Polski

## PRINT_START: pomiń płukanie Boxa, gdy slot się nie zmienił

> **Sprawdzone** na Q2 autora (2026-11-22): konsola pokazała `Same slot slot2 - skipping flush`, zaraz po tym czyszczenie dyszy.
> Wersja automatyczna: [tools/skip_flush](../tools/skip_flush).

Fabryczny `PRINT_START` wykonuje `EXTRUSION_AND_FLUSH` (~75 s) przy każdym wydruku. Jeśli potrzebny slot jest już
załadowany (`last_load_slot` w `saved_variables`), płukanie nic nie daje.

Edytuj `PRINT_START` w pliku makr QIDI (zrób kopię). Nazwy linii mogą się trochę różnić między wersjami firmware.
1. Na początku makra dodaj trzy linie `{% set ... %}` (wyżej).
2. Zamień płukanie po `BOX_PRINT_START` na blok `{% if same_slot %}` (wyżej).
3. Jeśli makro dalej liczy `box_flushed`, dopisz do niego `and not same_slot`.

Sprawdź pierwsze wydruki (konsola pokaże `Same slot slotN - skipping flush`). Resztki w dyszy usuwa wtedy tylko
linia płukania – przy tej samej szpuli to wystarcza; po długiej przerwie z wilgotnym PETG przepłucz ręcznie.
