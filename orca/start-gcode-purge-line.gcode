; OrcaSlicer -> Printer settings -> Machine G-code -> Machine start G-code
; Replaces QIDI's two fixed purge lines (after "G4 P3000") with a line 5 mm in front of the model,
; inside the adaptive mesh area (set Adaptive bed mesh margin = 10 mm).
; --- purge line 5 mm in front of the model ---
; PL: OrcaSlicer -> Ustawienia drukarki -> G-code maszyny -> Początkowy G-code. Zastępuje dwie stałe linie
; płukania QIDI (po "G4 P3000") linią 5 mm przed modelem, w obszarze siatki (margines siatki 10 mm).
G1 X{min(200, max(5, first_layer_print_min[0]))} Y{max(2, first_layer_print_min[1] - 5)} F30000
G1 Z{initial_layer_print_height} F600
G1 X{min(200, max(5, first_layer_print_min[0])) + 20} E5 F1200
G1 X{min(200, max(5, first_layer_print_min[0])) + 60} E1.7 F2400
G1 Y{max(2, first_layer_print_min[1] - 5) + 0.6} F3000
G1 X{min(200, max(5, first_layer_print_min[0])) + 20} E1.7 F2400
G1 Z1 F600
