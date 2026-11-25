# Latest Fluidd next to QIDI's Fluidd

**EN** · [PL – wersja polska niżej](#polski)

Status: ✅ Fluidd v1.38.1 working on the author's Q2 (2026-11-25), next to QIDI's Fluidd 1.30.5.

QIDI's Fluidd is a fork with the QIDI Box panel ("Material Control"), Box drying and QIDI extras.
Replacing it with upstream Fluidd would remove those. Instead, install upstream Fluidd in its own folder on another port.
QIDI's Fluidd stays on port 80 (and 10088), unchanged.

- Upstream Fluidd needs Moonraker v0.8.0-309 or newer. QIDI's Moonraker reports only API 1.4.0, but works.
- **No QIDI Box panel** in upstream Fluidd. Use QIDI's Fluidd (port 80) or HelixScreen for slots.
- Port 8080 is taken on the Q2 by a QIDI service, so the new Fluidd uses **8099**.
- Both Fluidd versions keep their settings in the same Moonraker database namespace (`fluidd`). Back it up first.

## Install
```bash
# 1. back up Fluidd settings
curl -s "http://127.0.0.1:7125/server/database/item?namespace=fluidd" -o ~/fluidd-db-backup.json
# 2. latest Fluidd into its own folder
cd /tmp && rm -rf fluidd-latest fluidd.zip
curl -fsSL https://github.com/fluidd-core/fluidd/releases/latest/download/fluidd.zip -o fluidd.zip
python3 -m zipfile -e fluidd.zip fluidd-latest
sudo rm -rf /home/mks/fluidd-latest && sudo mv fluidd-latest /home/mks/fluidd-latest
sudo chown -R --reference=/home/mks/fluidd /home/mks/fluidd-latest
# 3. nginx: copy of the Fluidd site on port 8099
sudo sed -e 's/listen 80;/listen 8099;/' -e '/listen 10088;/d' \
  -e 's#root /home/mks/fluidd;#root /home/mks/fluidd-latest;#' \
  -e 's#fluidd-access.log#fluidd-latest-access.log#; s#fluidd-error.log#fluidd-latest-error.log#' \
  -e '/helix-managed-remote-screen/d' \
  /etc/nginx/sites-available/fluidd | sudo tee /etc/nginx/sites-available/fluidd-latest >/dev/null
sudo ln -sf /etc/nginx/sites-available/fluidd-latest /etc/nginx/sites-enabled/fluidd-latest
sudo nginx -t && sudo systemctl reload nginx
```
Open `http://<printer-ip>:8099`. Update later: repeat step 2.

## Remove
```bash
sudo rm -f /etc/nginx/sites-enabled/fluidd-latest /etc/nginx/sites-available/fluidd-latest
sudo rm -rf /home/mks/fluidd-latest && sudo nginx -t && sudo systemctl reload nginx
```

---

# Polski

## Najnowszy Fluidd obok Fluidd od QIDI

Status: ✅ Fluidd v1.38.1 działa na Q2 autora (2026-11-25), obok Fluidd QIDI 1.30.5.

Fluidd od QIDI to fork z panelem QIDI Boxa („Kontrola Materiału”), suszeniem Boxa i dodatkami QIDI.
Zastąpienie go oficjalnym Fluidd usunęłoby te funkcje. Zamiast tego instalujemy oficjalny Fluidd w osobnym katalogu na innym porcie.
Fluidd QIDI zostaje bez zmian na porcie 80 (i 10088).

- Oficjalny Fluidd wymaga Moonrakera v0.8.0-309 lub nowszego. Moonraker QIDI podaje tylko API 1.4.0, ale działa.
- **Brak panelu QIDI Boxa** w oficjalnym Fluidd. Sloty ustawiaj we Fluidd QIDI (port 80) albo w HelixScreen.
- Port 8080 na Q2 zajmuje usługa QIDI, więc nowy Fluidd działa na porcie **8099**.
- Oba Fluidd trzymają ustawienia w tej samej przestrzeni bazy Moonrakera (`fluidd`). Najpierw zrób kopię.

Instalacja i usunięcie: polecenia w wersji angielskiej wyżej. Adres: `http://<ip-drukarki>:8099`. Aktualizacja: powtórz krok 2.
