# box_trace – read-only tracing of the QIDI Box

Shows which motion parameters the closed Box modules read from `saved_variables` (key, QIDI's default,
returned value) and, optionally, every G-code script with timestamps to time a filament change.
Changes nothing.

## Install
```
scp box_trace.py mks@PRINTER:~/klipper/klippy/extras/
```
Add to `printer.cfg`:
```
[box_trace]
```
Restart Klipper. Do a filament load/unload, then in the console:
```
BOX_TRACE REPORT=1     ; parameters read so far
BOX_TRACE SCRIPTS=1    ; log scripts to klippy.log (SCRIPTS=0 to stop)
```

## Remove
Delete the `[box_trace]` section and the file, restart Klipper.

Results on a Q2: see [docs/qidi-box.md](../../docs/qidi-box.md).
