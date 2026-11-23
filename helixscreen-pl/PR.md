## i18n(pl): add Polish translation

This PR adds `translations/pl.yml`, a complete Polish translation of all 6235 keys in `en.yml`.

**About the translation**
- I'm a native Polish speaker and use HelixScreen on a QIDI Q2 with the QIDI Box. AI tools helped with the draft, and I reviewed the terminology against the UI.
- Placeholders (`%d`, `%s`, `%zu`, `{}`, `{0}`, `{:.1f}`, `%1$d` …) and leading or trailing spaces are kept as they are in the source.
- The 29 keys that `ru.yml` writes as plural mappings have Polish `one` / `few` / `many` / `other` forms.
- Hardware terms follow common Polish 3D-printing usage: *dysza* (nozzle), *stół* (bed), *głowica* (toolhead), *tor* (lane), *gate*, *bazowanie* (homing), *siatka stołu* (bed mesh), *płukanie* (purge).
- Klipper and slicer names (`SAVE_CONFIG`, `PRINT_START`, Orca setting names, Happy Hare values such as `exact` / `material` / `next`) are left in English.

**Checks run**
- `scripts/check_translation_files.py --fix --base none`: clean (Weblate shape).
- `scripts/check_translation_format_specifiers.py`: clean.
- `scripts/check_translation_packs_fresh.py`: OK.

**Not included: code registration (needs a maintainer)**
- Add `pl` / "Polski" to the language list (`system_settings_manager.cpp`, language chooser), plus `locale_formats.cpp` and `region_defaults.cpp` (DMY, 24h, `pl_PL.UTF-8`).
- `i18n_plural.cpp` needs a Polish rule, which is the CLDR `pl` rule:
  ```cpp
  if (code == "pl") {
      const uint64_t mod10 = n % 10;
      const uint64_t mod100 = n % 100;
      if (n == 1) return PluralCategory::One;
      if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) return PluralCategory::Few;
      return PluralCategory::Many;
  }
  ```
- The Polish letters ą ć ę ł ń ó ś ź ż are in Latin Extended-A, which the fonts already cover.

I'm happy to fix wording in review or to help keep the file up to date later, for example via Weblate.

---

## i18n(pl): dodanie polskiego tłumaczenia

Ten PR dodaje plik `translations/pl.yml` z pełnym polskim tłumaczeniem wszystkich 6235 kluczy z `en.yml`. Odmiana liczebników (one/few/many/other) jest zrobiona dla 29 kluczy z liczbą mnogą. Rejestrację języka w kodzie zostawiam opiekunom projektu (szczegóły powyżej).

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01HkGJTnPmxP26LtqpdXeY9P
