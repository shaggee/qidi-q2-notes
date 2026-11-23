# helix_box_bridge

Status: 🟡 proposed, tested only against a simulated Klipper (not yet on the printer).

## Problem
On Q2 firmware 1.1.x the QIDI Box (`multi_color_controller`) follows slot edits only when they arrive as
`UPDATE_FILAMENT_INFORMATION SLOT=0 COLOR='060606' VENDOR='QIDI' FILAMENT='PLA Basic'`.
The stock screen, QIDI Studio and the patched Fluidd Box panel send this command.
HelixScreen (v1.0.11) instead writes numeric ids with `SAVE_VARIABLE filament_slotN / color_slotN / vendor_slotN`.
The Box ignores those, so after an edit in HelixScreen, Fluidd shows every slot as "PLA Basic #FAFAFA".

## What the module does
It catches numeric `SAVE_VARIABLE` writes to `filament_slotN`, `color_slotN` and `vendor_slotN`.
It looks up the ids in `officiall_filas_list.cfg` and sends one `UPDATE_FILAMENT_INFORMATION` per slot.
- Fields HelixScreen did not send keep the Box's current value.
- A Generic (0) vendor keeps the current brand, so brands added to the printer's filament base survive.
- All other `SAVE_VARIABLE` calls run unchanged.

The module does not fix how HelixScreen *displays* slots saved by QIDI's UI (grey "--"). That needs a HelixScreen fix.

## Install
```bash
sudo curl -fsSL https://raw.githubusercontent.com/shaggee/qidi-q2-notes/main/tools/helix_box_bridge/helix_box_bridge.py \
  -o ~/klipper/klippy/extras/helix_box_bridge.py
```
Add this section to `printer.cfg`, then run `RESTART`:
```
[helix_box_bridge]
```
Check: `grep helix_box_bridge ~/printer_data/logs/klippy.log` should show `active`. After an edit in HelixScreen it shows `-> UPDATE_FILAMENT_INFORMATION ...`.

## Remove
Delete the `[helix_box_bridge]` section, run `RESTART`, then `sudo rm ~/klipper/klippy/extras/helix_box_bridge.py`.

---

# Polski

Status: 🟡 propozycja, przetestowana tylko na symulowanym Klipperze (jeszcze nie na drukarce).

## Problem
W firmware Q2 1.1.x QIDI Box (`multi_color_controller`) przyjmuje zmianę slotu tylko jako
`UPDATE_FILAMENT_INFORMATION SLOT=0 COLOR='060606' VENDOR='QIDI' FILAMENT='PLA Basic'`.
To polecenie wysyłają: fabryczny ekran, QIDI Studio i poprawiony panel Boxa we Fluidd.
HelixScreen (v1.0.11) zapisuje zamiast tego numery przez `SAVE_VARIABLE filament_slotN / color_slotN / vendor_slotN`.
Box je ignoruje, więc po zmianie w HelixScreen Fluidd pokazuje każdy slot jako „PLA Basic #FAFAFA”.

## Co robi moduł
Przechwytuje numeryczne zapisy `SAVE_VARIABLE` do `filament_slotN`, `color_slotN` i `vendor_slotN`.
Zamienia numery na nazwy według `officiall_filas_list.cfg` i wysyła jedno `UPDATE_FILAMENT_INFORMATION` na slot.
- Pola, których HelixScreen nie wysłał, zachowują obecną wartość z Boxa.
- Producent Generic (0) zostawia obecną markę, więc marki dodane do bazy filamentów drukarki zostają.
- Pozostałe wywołania `SAVE_VARIABLE` działają bez zmian.

Moduł nie naprawia *wyświetlania* w HelixScreen slotów zapisanych przez interfejs QIDI (szare „--”). To wymaga poprawki w HelixScreen.

## Instalacja
```bash
sudo curl -fsSL https://raw.githubusercontent.com/shaggee/qidi-q2-notes/main/tools/helix_box_bridge/helix_box_bridge.py \
  -o ~/klipper/klippy/extras/helix_box_bridge.py
```
Dodaj tę sekcję do `printer.cfg`, potem uruchom `RESTART`:
```
[helix_box_bridge]
```
Sprawdzenie: `grep helix_box_bridge ~/printer_data/logs/klippy.log` powinno pokazać `active`. Po zmianie w HelixScreen pojawi się `-> UPDATE_FILAMENT_INFORMATION ...`.

## Usunięcie
Usuń sekcję `[helix_box_bridge]`, uruchom `RESTART`, potem `sudo rm ~/klipper/klippy/extras/helix_box_bridge.py`.
