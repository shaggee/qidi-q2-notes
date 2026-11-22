; OrcaSlicer -> Printer settings -> Machine G-code -> Machine start G-code
; Replaces QIDI's two fixed purge lines (after "G4 P3000") with a line 5 mm in front of the model,
; inside the adaptive mesh area (KAMP_Settings.cfg: variable_mesh_margin: 10).
; --- purge line 5 mm in front of the model ---
; PL: OrcaSlicer -> Ustawienia drukarki -> G-code maszyny -> Początkowy G-code. Zastępuje dwie stałe linie
; płukania QIDI (po "G4 P3000") linią 5 mm przed modelem, w obszarze siatki (KAMP_Settings.cfg: variable_mesh_margin: 10).
; Stock lines end with "G1 X154 Z-0.1" (nozzle 0.1 mm into the plate) - this one never goes below Z0.
; PL: fabryczne linie kończą się "G1 X154 Z-0.1" (dysza 0.1 mm w płytę) - ta nigdy nie schodzi poniżej Z0.
G1 X{min(200, max(5, first_layer_print_min[0]))} Y{max(2, first_layer_print_min[1] - 5)} F30000
G1 Z{initial_layer_print_height} F600
G1 X{min(200, max(5, first_layer_print_min[0])) + 20} E5 F1200
G1 X{min(200, max(5, first_layer_print_min[0])) + 60} E1.7 F2400
G1 Y{max(2, first_layer_print_min[1] - 5) + 0.6} F3000
G1 X{min(200, max(5, first_layer_print_min[0])) + 20} E1.7 F2400
G1 Z1 F600
