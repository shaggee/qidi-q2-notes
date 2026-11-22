# Security and firmware updates

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
