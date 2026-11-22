# Security and firmware updates

**EN** · [PL – wersja polska niżej](#polski)

## ADB root shell
QIDI's system image can run Android Debug Bridge (`usbdevice.service`) with a root shell on TCP port 5555
without a password (reported by qidi-q2-0204-tweaked for 01.01.02.04). Check and turn it off:

```
ssh qidi@PRINTER "systemctl is-active usbdevice"
ssh -t mks@PRINTER "sudo systemctl disable --now usbdevice.service"
```
QIDI's updates, recovery and reflash do not use it. Undo: `sudo systemctl enable --now usbdevice.service`.

## Blocking firmware updates
An update would overwrite the toolhead fix, patched Klipper files and probably custom macros.

1. Make the download folder immutable (as qidi-q2-0204-tweaked does):
   ```
   ssh -t mks@PRINTER 'ls -ld /home/qidi/download && sudo chattr +i /home/qidi/download && lsattr -d /home/qidi/download'
   ```
   Undo: `sudo chattr -i /home/qidi/download`.
2. Optional: block `public-cdn.qidimaker.com` for the printer's IP on your DNS filter / router.
3. Do not press the online update on the screen.

To update on purpose: unlock, update, then re-run `TWEAKED_THR_CHECK` and `q2_tweaks.py check`.

## Keep the printer on a trusted network
Moonraker/Fluidd have no login by default. Use a VPN (e.g. Tailscale) for remote access; do not expose ports.

---

# Polski

## Bezpieczeństwo i aktualizacje

### Powłoka root przez ADB
System QIDI może uruchamiać ADB (`usbdevice.service`) z powłoką root na porcie TCP 5555 bez hasła (zgłoszone
przez qidi-q2-0204-tweaked dla 01.01.02.04). Sprawdzenie i wyłączenie – polecenia wyżej. Aktualizacje, odzyskiwanie
i ponowne wgranie QIDI z tego nie korzystają. Cofnięcie: `sudo systemctl enable --now usbdevice.service`.

### Blokada aktualizacji
Aktualizacja nadpisałaby poprawkę głowicy, zmienione pliki Klippera i prawdopodobnie własne makra.
1. Ustaw folder pobierania jako niezmienny (`chattr +i /home/qidi/download`, polecenie wyżej). Cofnięcie: `sudo chattr -i /home/qidi/download`.
2. Opcjonalnie zablokuj `public-cdn.qidimaker.com` dla IP drukarki w filtrze DNS / routerze.
3. Nie naciskaj aktualizacji online na ekranie.

Celowa aktualizacja: odblokuj, zaktualizuj, potem ponownie `TWEAKED_THR_CHECK` i `q2_tweaks.py check`.

### Tylko zaufana sieć
Moonraker/Fluidd domyślnie nie mają logowania. Do dostępu zdalnego używaj VPN (np. Tailscale), nie wystawiaj portów.
