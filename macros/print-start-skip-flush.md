# PRINT_START: skip the Box flush when the slot did not change

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

Status: the logic is simple, but check the first prints (console shows `Same slot slotN - skipping flush`).
Old filament residue in the nozzle is then purged only by the purge line – fine for the same spool, do a
manual flush after a long break with wet PETG.
