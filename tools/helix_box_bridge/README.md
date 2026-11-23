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
- The vendor + filament pair is matched to the printer's filament base (`/home/qidi/QIDI_Client/resource/filament_config/filament-0.4.json`). The Box silently ignores pairs it does not know (e.g. Tecbears + ABS Rapido).
- "Generic ABS" in HelixScreen becomes `VENDOR='Generic' FILAMENT='ABS'`.
- A colour-only edit (same material type, no brand picked) keeps the slot's brand and product, e.g. Tecbears PLA.
- Fields HelixScreen did not send keep the Box's current value.
- All other `SAVE_VARIABLE` calls run unchanged.

The module does not fix how HelixScreen *displays* slots saved by QIDI's UI (grey "--"). That needs a HelixScreen fix.

## Install
```bash
sudo curl -fsSL https://raw.githubusercontent.com/shaggee/qidi-q2-notes/main/tools/helix_box_bridge/helix_box_bridge.py \
  -o ~/klipper/klippy/extras/helix_box_bridge.py
```
Add this section to `printer.cfg`, then restart the Klipper service (`RESTART` alone keeps the old module code loaded):
```
[helix_box_bridge]
```
```bash
sudo systemctl restart klipper
```
After updating the .py file, also use `sudo systemctl restart klipper`.

Check: `grep helix_box_bridge ~/printer_data/logs/klippy.log` should show `v2: active`. After an edit in HelixScreen it shows `-> UPDATE_FILAMENT_INFORMATION ...`.

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
- Para producent + filament jest dopasowywana do bazy filamentów drukarki (`/home/qidi/QIDI_Client/resource/filament_config/filament-0.4.json`). Box po cichu ignoruje pary, których nie zna (np. Tecbears + ABS Rapido).
- „Generic ABS” w HelixScreen zamienia się na `VENDOR='Generic' FILAMENT='ABS'`.
- Zmiana samego koloru (ten sam typ materiału, bez wyboru marki) zostawia markę i produkt ze slotu, np. Tecbears PLA.
- Pola, których HelixScreen nie wysłał, zachowują obecną wartość z Boxa.
- Pozostałe wywołania `SAVE_VARIABLE` działają bez zmian.

Moduł nie naprawia *wyświetlania* w HelixScreen slotów zapisanych przez interfejs QIDI (szare „--”). To wymaga poprawki w HelixScreen.

## Instalacja
```bash
sudo curl -fsSL https://raw.githubusercontent.com/shaggee/qidi-q2-notes/main/tools/helix_box_bridge/helix_box_bridge.py \
  -o ~/klipper/klippy/extras/helix_box_bridge.py
```
Dodaj tę sekcję do `printer.cfg`, potem zrestartuj usługę Klippera (samo `RESTART` zostawia w pamięci stary kod modułu):
```
[helix_box_bridge]
```
```bash
sudo systemctl restart klipper
```
Po aktualizacji pliku .py też użyj `sudo systemctl restart klipper`.

Sprawdzenie: `grep helix_box_bridge ~/printer_data/logs/klippy.log` powinno pokazać `v2: active`. Po zmianie w HelixScreen pojawi się `-> UPDATE_FILAMENT_INFORMATION ...`.

## Usunięcie
Usuń sekcję `[helix_box_bridge]`, uruchom `RESTART`, potem `sudo rm ~/klipper/klippy/extras/helix_box_bridge.py`.
