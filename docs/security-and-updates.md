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

## Turning off the QIDI cloud (MQTT)
Fluidd: *Moonraker has failing components: mqtt* / *MQTT Connection Failed: Not authorized*.
QIDI's Moonraker always loads its cloud client (`components/mqtt.so`, broker `8.149.135.149:8883`), whatever `moonraker.conf` says.
When the QIDI Link account token expires, the broker refuses it and the warning stays.
If you do not use QIDI Link, comment out the two lines in `server.py` that force-load it (backup kept). Verified on the author's Q2 (2026-11-23): `failed: []`, no warnings.
```bash
F=/home/mks/moonraker/moonraker/server.py
sudo cp -a $F $F.bak-mqtt
sudo sed -i "s/^\(\s*\)\(cfg_sections\.\(discard\|add\)('mqtt')\)/\1# \2  # QIDI cloud off/" $F
sudo chown --reference=$F.bak-mqtt $F
grep -n "QIDI cloud off" $F          # 2 lines
sudo systemctl restart moonraker
```
Undo: `sudo cp -a $F.bak-mqtt $F && sudo systemctl restart moonraker`. A QIDI firmware update restores the file, so the change has to be done again.
QIDI also loads `frp_manager` (a remote-access tunnel); it is left on here.

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

### Wyłączenie chmury QIDI (MQTT)
Fluidd: *Moonraker ma niedziałające wtyczki: mqtt* / *MQTT Connection Failed: Not authorized*.
Moonraker od QIDI zawsze ładuje klienta chmury (`components/mqtt.so`, broker `8.149.135.149:8883`), niezależnie od `moonraker.conf`.
Gdy wygaśnie token konta QIDI Link, broker go odrzuca i ostrzeżenie zostaje na stałe.
Jeśli nie używasz QIDI Link, zakomentuj dwie linie w `server.py`, które go wymuszają (z kopią zapasową). Sprawdzone na Q2 autora (2026-11-23): `failed: []`, brak ostrzeżeń.
Polecenia jak w wersji angielskiej wyżej. Cofnięcie: `sudo cp -a $F.bak-mqtt $F && sudo systemctl restart moonraker`. Aktualizacja firmware QIDI przywraca plik, więc zmianę trzeba wtedy powtórzyć.
QIDI ładuje też `frp_manager` (tunel zdalnego dostępu); tu zostaje włączony.

### Tylko zaufana sieć
Moonraker/Fluidd domyślnie nie mają logowania. Do dostępu zdalnego używaj VPN (np. Tailscale), nie wystawiaj portów.
