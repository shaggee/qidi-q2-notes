# screen_view – the printer's touch screen as a camera in Fluidd

**EN** · [PL – wersja polska niżej](#polski)

A small service reads the printer's screen (`/dev/fb0`, 480×272) and serves it as a PNG on `127.0.0.1:8083`;
Fluidd's web server already forwards `/webcam4/` there. In Fluidd you add it as a camera – no Fluidd file is
changed. **Look only**: nothing is written to the screen, no touch. The screen is read only when a picture is
requested (≈2/s while the card is visible), memory limit 30 MB.

Service code (`q2_screen.py`, `q2-screen.service`): module `printer-screen-view` from
[qidi-q2-0204-tweaked](https://github.com/muchak1994-lpg/qidi-q2-0204-tweaked) (GPL-3.0), unchanged.
`screen_view.py` is the installer written here (checks first, Fluidd untouched). The original also adds a
button to Fluidd's menu by editing `index.html`; that part is not included.

Status: 🟡 checks matched the author's printer (480×272, 32 bit, `/webcam4/` → 8083 free). Not yet installed.

## Install
```
ssh mks@PRINTER
cd /tmp
for f in screen_view.py q2_screen.py q2-screen.service; do
  curl -sSLO https://raw.githubusercontent.com/shaggee/qidi-q2-notes/main/tools/screen_view/$f
done
sudo python3 screen_view.py check
sudo python3 screen_view.py install
```
Then in Fluidd: **Settings → Cameras → Add camera**: name `Printer screen`, type **MJPEG Adaptive**,
URL `/webcam4/?action=snapshot`, target FPS 2. The card appears on the dashboard.

Remove: `sudo python3 screen_view.py uninstall` and delete the camera in Fluidd.

---

# Polski

## screen_view – ekran dotykowy drukarki jako kamera we Fluidd

Mała usługa czyta ekran drukarki (`/dev/fb0`, 480×272) i udostępnia go jako PNG na `127.0.0.1:8083`; serwer WWW
Fluidd już przekierowuje tam `/webcam4/`. We Fluidd dodajesz to jako kamerę – żaden plik Fluidd nie jest zmieniany.
**Tylko podgląd**: nic nie trafia na ekran, bez dotyku. Ekran jest czytany tylko na żądanie (≈2/s, gdy karta jest
widoczna), limit pamięci 30 MB.

Kod usługi (`q2_screen.py`, `q2-screen.service`): moduł `printer-screen-view` z
[qidi-q2-0204-tweaked](https://github.com/muchak1994-lpg/qidi-q2-0204-tweaked) (GPL-3.0), bez zmian.
`screen_view.py` to instalator napisany tutaj (najpierw sprawdza, Fluidd bez zmian). Oryginał dodaje też przycisk
w menu Fluidd przez zmianę `index.html`; tej części tu nie ma.

Status: 🟡 sprawdzenie zgodne z drukarką autora (480×272, 32 bit, `/webcam4/` → wolny 8083). Jeszcze nie zainstalowane.

Instalacja: polecenia wyżej (`curl` trzech plików, `check`, `install`). Potem we Fluidd: **Settings → Cameras →
Add camera**: nazwa `Ekran drukarki`, typ **MJPEG Adaptive**, URL `/webcam4/?action=snapshot`, docelowe FPS 2.
Karta pojawi się na pulpicie.

Usunięcie: `sudo python3 screen_view.py uninstall` i usuń kamerę we Fluidd.
