# Kandidatenaudit – ursprüngliche Bestandskarten

Stand: 28. Juli 2026

## Umfang

Der erneute Kontrolllauf umfasst die acht Kartenpakete, die bereits vor den
vier neuen Städtewellen bestanden:

- ADL
- Berlin
- Denver
- Hamburg
- Manhattan
- Rhein-Ruhr-Megaplex
- Seattle
- Toronto

Der aktuelle Extraktor fand in den vollständigen Textquellen 3.235
Rohkandidaten. Der ältere Vorlauf mit 660 Treffern wurde dadurch vollständig
ersetzt.

- 376 Kandidaten wurden mit vorhandenen kanonischen Dossiers zusammengeführt.
- 2.859 Kandidaten wurden als Überschrift, Regelbegriff, OCR-Fragment,
  Dublette, Fehlklassifikation oder nicht ausreichend lokale Erwähnung
  verworfen.
- 0 Kandidaten blieben offen.

## Entscheidungen nach Karte

| Karte | Zusammengeführt | Verworfen | Offen |
|---|---:|---:|---:|
| ADL | 0 | 438 | 0 |
| Berlin | 18 | 255 | 0 |
| Denver | 105 | 459 | 0 |
| Hamburg | 43 | 247 | 0 |
| Manhattan | 43 | 196 | 0 |
| Rhein-Ruhr-Megaplex | 2 | 31 | 0 |
| Seattle | 163 | 1.223 | 0 |
| Toronto | 2 | 10 | 0 |

Für die ADL wurden keine neuen Kandidaten zusammengeführt, weil ihre
kanonischen Einträge bereits über die eigenständigen Stadtpakete und den
regionalen ADL-Katalog abgebildet werden. Reine Stadtnennungen, Kapitelzeilen
und allgemeine Regelbegriffe erzeugen keine zusätzlichen Dossiers.

## Reproduzierbarkeit

- `tools/extract_source_candidates.py`
- `tools/review_source_candidates.py`
- `tools/import_archive_references.py`
- `tools/rebuild_search_index.py`
- `tools/validate_city_data.py`
