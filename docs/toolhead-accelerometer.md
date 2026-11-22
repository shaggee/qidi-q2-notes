# Toolhead accelerometer fix (383 → 1603 samples/s), done from a Linux host

**EN** · [PL – wersja polska niżej](#polski)

QIDI's toolhead firmware THR 02.02.01.08 lacks Klipper commit 6269dda (LIS2DW FIFO), so the accelerometer
delivers ~390 samples/s instead of 1600 ([QIDI_Q2 #39](https://github.com/QIDITECH/QIDI_Q2/issues/39)) and
input shaper calibration sees only part of the vibrations.

This follows the procedure of
[qidi-q2-0204-tweaked – TOOLHEAD_ACCELEROMETER](https://github.com/muchak1994-lpg/qidi-q2-0204-tweaked/blob/main/docs/TOOLHEAD_ACCELEROMETER.md),
run from a Linux machine (Proxmox host) instead of Windows. **Rewriting the toolhead firmware is at your own
risk.** Read the original guide first. Replace `PRINTER` with the printer's IP. SSH user `mks` (sudo).

## 0. Check (read only)
Install the check from [`tools/q2_tweaks`](../tools/q2_tweaks) and run `TWEAKED_THR_CHECK` in the Fluidd
console. Continue only with all three:

```
Accelerometer: 383 samples/s instead of about 1600 - QIDI toolhead firmware bug (QIDI_Q2 #39).
A manual, optional fix exists for this bootloader and firmware ...
Toolhead firmware: 02.02.01.08, QIDI THR 02.02.01.08 (original) (1d34b4b0).
Bootloader: ... (31f8344d).
```
Then `TWEAKED_THR_CHECK SAVE=1` and download `config/q2_thr_backup/` from Fluidd.

## 1. Tools (on the Linux host)
```
mkdir -p ~/q2-thr && cd ~/q2-thr
curl -sSL -o flasher.tar.gz https://github.com/thelegendtubaguy/Valve-Oil/archive/ffb302997910b0a02ac8a18b6e23274109d208f2.tar.gz
tar -xzf flasher.tar.gz && mv Valve-Oil-ffb302997910b0a02ac8a18b6e23274109d208f2 flasher
curl -sSL -o lis2dw_patch.py https://raw.githubusercontent.com/rayaanatif/qidi-q2-accelerometer-fix/0e649671c9d56b7dc7200c0b8311265821082574/tools/lis2dw_patch.py
sha256sum flasher/scripts/flash_thr_firmware.py flasher/scripts/thr_bootloaders.py flasher/firmware/max4-thr-lis2dw-fifo-v1.json lis2dw_patch.py
```
Expected:
```
b68e3032bd22cb441f01648ec20dcfc8fe58cd822f9ae7cb81cca5679d9c6f0b  flasher/scripts/flash_thr_firmware.py
1169da4cc843d6bf67fa0d11ed8a46d4b0d7f69095ea8d46f007141ab0923918  flasher/scripts/thr_bootloaders.py
8619820de91730a37be0e67dd66d38b2671c01b1b7508a032c5ec11f417cd5e1  flasher/firmware/max4-thr-lis2dw-fifo-v1.json
016c11b1a57fc9f01914a8b04eb61cfee642d3dec09e678c5a29d935f7ae9df4  lis2dw_patch.py
```

## 2. Copy the flasher to the printer
```
ssh mks@PRINTER 'mkdir -p /tmp/q2_thr_tools'
scp -r flasher/scripts flasher/firmware mks@PRINTER:/tmp/q2_thr_tools/
ssh mks@PRINTER 'cd /tmp/q2_thr_tools && sha256sum scripts/flash_thr_firmware.py scripts/thr_bootloaders.py firmware/max4-thr-lis2dw-fifo-v1.json'
```

## 3. Stop Klipper and the screen program
```
ssh -t mks@PRINTER 'sudo systemctl stop qidi-client.service && sudo systemctl stop klipper.service; systemctl is-active klipper.service qidi-client.service'
```
→ `inactive` `inactive`. To start them again at any point:
```
ssh -t mks@PRINTER 'sudo systemctl start klipper.service; sleep 5; sudo systemctl start qidi-client.service; systemctl is-active klipper.service qidi-client.service'
```

## 4. Read the original firmware
```
ssh -t mks@PRINTER 'cd /tmp/q2_thr_tools && sudo /home/qidi/klippy-env/bin/python scripts/flash_thr_firmware.py snapshot --output-dir dist/thr-before --printer-idle-confirmed; echo EXIT_CODE=$?; sudo chown -R mks dist'
scp -r mks@PRINTER:/tmp/q2_thr_tools/dist/thr-before .
sha256sum thr-before/application.bin thr-before/bootloader.bin
```
Result here:
```
"application_sha256": "1d34b4b0142f2a2047f08c2fae59d827bcee0adbd1563b4bd1de311dff8b2d62"
"bootloader_sha256":   "31f8344db7b091df5429960bc9cd06065e2188c3b8092e43fb65eb3f2833723c"
EXIT_CODE=0
```
Keep `thr-before` – it is the way back.

## 5. Bootloader probe (erases nothing) and re-read
```
ssh -t mks@PRINTER 'cd /tmp/q2_thr_tools && sudo /home/qidi/klippy-env/bin/python scripts/flash_thr_firmware.py probe --backup-dir dist/thr-before --reset --printer-idle-confirmed; echo EXIT_CODE=$?'
```
→ `"bootloader_reply": "0102"`, `"erase_requested": false`, `EXIT_CODE=0`. Wait 15 s, then:
```
ssh -t mks@PRINTER 'cd /tmp/q2_thr_tools && sudo /home/qidi/klippy-env/bin/python scripts/flash_thr_firmware.py snapshot --output-dir dist/thr-after-probe --printer-idle-confirmed; echo EXIT_CODE=$?'
```
→ same two hashes.

## 6. Build the patched image from your own original
```
python3 lis2dw_patch.py patch thr-before/application.bin QD_Q2_THR_02.02.01.08_20260303_FIFO_v1.bin
sha256sum QD_Q2_THR_02.02.01.08_20260303_FIFO_v1.bin
scp QD_Q2_THR_02.02.01.08_20260303_FIFO_v1.bin mks@PRINTER:/tmp/q2_thr_tools/dist/
ssh mks@PRINTER 'sha256sum /tmp/q2_thr_tools/dist/QD_Q2_THR_02.02.01.08_20260303_FIFO_v1.bin'
```
→ `template B at 0xbfa`, `9d2360ba47ebd720dbef07a0a4ebaf26004360bca090997d7b4a118c41460ac9`.

## 7. Flash (the only step that changes the toolhead)
Do not power off or close the terminal until `EXIT_CODE` appears.
```
ssh -t mks@PRINTER 'cd /tmp/q2_thr_tools && sudo /home/qidi/klippy-env/bin/python scripts/flash_thr_firmware.py transfer --image dist/QD_Q2_THR_02.02.01.08_20260303_FIFO_v1.bin --backup-dir dist/thr-before --reset --recover-to-stock --printer-idle-confirmed --confirm-write; echo EXIT_CODE=$?'
```
Result here: `"transfer_acknowledged": true`, `"fell_back": false`, `EXIT_CODE=0`
(`"verified": false` at this point is expected – verification is the next step).
`EXIT_CODE=4` = write failed, original restored. `1` or `5` = stop, keep the printer on, ask for help.

## 8. Verify
```
ssh -t mks@PRINTER 'cd /tmp/q2_thr_tools && sleep 15 && sudo /home/qidi/klippy-env/bin/python scripts/flash_thr_firmware.py snapshot --output-dir dist/thr-after --printer-idle-confirmed; echo SNAP_EXIT=$?; sudo /home/qidi/klippy-env/bin/python scripts/flash_thr_firmware.py verify --image dist/QD_Q2_THR_02.02.01.08_20260303_FIFO_v1.bin --backup-dir dist/thr-after --original-backup-dir dist/thr-before; echo VERIFY_EXIT=$?; sudo chown -R mks dist'
scp -r mks@PRINTER:/tmp/q2_thr_tools/dist/thr-after .
```
→ `"verified": true`, application `9d2360ba…`, bootloader `31f8344d…`, `SNAP_EXIT=0`, `VERIFY_EXIT=0`.

## 9. Start services, check, re-calibrate
Start the services (step 3), then in Fluidd:
```
TWEAKED_THR_CHECK        -> Accelerometer: 1603 samples/s - OK. ... (9d2360ba)
G28
SHAPER_CALIBRATE         ; QIDI's SHAPER_CALIBRATE does not home by itself
SAVE_CONFIG
```
Clean up: `ssh -t mks@PRINTER 'sudo rm -rf /tmp/q2_thr_tools'`

## Input shaper before / after
| Axis | Before (383 samples/s) | After (1603 samples/s) | Suggested max accel |
|---|---|---|---|
| X | 3hump_ei 68.8 Hz | **3hump_ei 93.2 Hz** (smoothing 0.102) | 6200 |
| Y | mzv 42.2 Hz | **mzv 47.2 Hz** (vibrations 0.0%, smoothing 0.097) | 6600 |

A QIDI firmware update that ships a new toolhead firmware overwrites the fix – run `TWEAKED_THR_CHECK` after
any update.

---

# Polski

## Naprawa akcelerometru głowicy (383 → 1603 próbek/s) z hosta Linux

Firmware głowicy QIDI THR 02.02.01.08 nie ma poprawki Klippera 6269dda (FIFO LIS2DW), więc akcelerometr daje
~390 próbek/s zamiast 1600 ([QIDI_Q2 #39](https://github.com/QIDITECH/QIDI_Q2/issues/39)), a kalibracja Input Shapera
widzi tylko część drgań.

Procedura według [qidi-q2-0204-tweaked – TOOLHEAD_ACCELEROMETER](https://github.com/muchak1994-lpg/qidi-q2-0204-tweaked/blob/main/docs/TOOLHEAD_ACCELEROMETER.md),
wykonana z komputera z Linuxem (host Proxmox) zamiast Windows. **Wgrywanie firmware głowicy na własne ryzyko.**
Najpierw przeczytaj oryginalny opis. `PRINTER` zamień na IP drukarki. Użytkownik SSH `mks` (sudo).

Polecenia i oczekiwane wyniki są w wersji angielskiej powyżej (są identyczne). Kroki:

0. **Sprawdzenie (tylko odczyt):** `TWEAKED_THR_CHECK` w konsoli Fluidd; kontynuuj tylko, gdy pokazuje 383 próbek/s,
   firmware `1d34b4b0` i bootloader `31f8344d`. Potem `TWEAKED_THR_CHECK SAVE=1` i pobierz `config/q2_thr_backup/`.
1. **Narzędzia** na hoście: pobierz flasher Valve-Oil i `lis2dw_patch.py` z konkretnych commitów, sprawdź sumy SHA-256.
2. **Skopiuj flasher na drukarkę** i sprawdź sumy tam.
3. **Zatrzymaj Klippera i program ekranu** (`inactive` `inactive`).
4. **Odczytaj oryginalny firmware** (`thr-before`) – to jest droga powrotu, zachowaj go.
5. **Test bootloadera** (nic nie kasuje) i ponowny odczyt – te same sumy.
6. **Zbuduj poprawiony obraz z własnego oryginału** – suma `9d2360ba…`.
7. **Wgranie** (jedyny krok zmieniający głowicę). Nie wyłączaj zasilania i nie zamykaj terminala, dopóki nie
   pojawi się `EXIT_CODE`. `0` = OK; `4` = zapis się nie udał, przywrócono oryginał; `1` lub `5` = stop, drukarka
   włączona, poproś o pomoc.
8. **Weryfikacja:** `"verified": true`, aplikacja `9d2360ba…`, bootloader `31f8344d…`.
9. **Uruchom usługi**, `TWEAKED_THR_CHECK` → 1603 próbek/s, potem `G28`, `SHAPER_CALIBRATE` (QIDI nie bazuje
   sam), `SAVE_CONFIG`. Na koniec usuń `/tmp/q2_thr_tools`.

### Input Shaper przed / po
| Oś | Przed (383 próbek/s) | Po (1603 próbek/s) | Sugerowane maks. przysp. |
|---|---|---|---|
| X | 3hump_ei 68.8 Hz | **3hump_ei 93.2 Hz** | 6200 |
| Y | mzv 42.2 Hz | **mzv 47.2 Hz** | 6600 |

Aktualizacja QIDI z nowym firmware głowicy nadpisze poprawkę – po każdej aktualizacji uruchom `TWEAKED_THR_CHECK`.
