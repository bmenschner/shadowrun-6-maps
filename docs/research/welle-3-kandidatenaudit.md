# Kandidatenaudit – Städtewelle 3

Stand: 28. Juli 2026

## Umfang

Die dritte Städtewelle umfasst:

- Kairo
- Metrópole
- Butte
- Casablanca-Rabat
- Vladivostok
- Zürich
- Leipzig-Halle
- Québec
- Bremen
- Hannover
- Istanbul
- Tenochtitlán
- Stuttgart

Aus den vollständigen Textquellen wurden 619 Rohkandidaten extrahiert und
abschließend entschieden:

- 134 mit kanonischen Datensätzen zusammengeführt
- 485 als Überschrift, Regelbegriff, OCR-Fragment, generischer Begriff,
  Dublette oder nicht ausreichend lokal belegter Kandidat verworfen
- 0 offen

## Entscheidungen nach Stadt

| Stadt | Zusammengeführt | Verworfen | Offen |
|---|---:|---:|---:|
| Bremen | 2 | 25 | 0 |
| Butte | 24 | 18 | 0 |
| Casablanca-Rabat | 21 | 27 | 0 |
| Hannover | 5 | 54 | 0 |
| Istanbul | 6 | 16 | 0 |
| Kairo | 27 | 100 | 0 |
| Leipzig-Halle | 6 | 22 | 0 |
| Metrópole | 10 | 38 | 0 |
| Québec | 6 | 34 | 0 |
| Stuttgart | 3 | 25 | 0 |
| Tenochtitlán | 8 | 33 | 0 |
| Vladivostok | 8 | 49 | 0 |
| Zürich | 8 | 44 | 0 |

## Erzeugte Stadtpakete

| Stadt | Orte | Personen und Gruppen |
|---|---:|---:|
| Kairo | 23 | 8 |
| Metrópole | 7 | 6 |
| Butte | 19 | 5 |
| Casablanca-Rabat | 20 | 5 |
| Vladivostok | 7 | 6 |
| Zürich | 9 | 4 |
| Leipzig-Halle | 10 | 4 |
| Québec | 5 | 3 |
| Bremen | 6 | 2 |
| Hannover | 8 | 4 |
| Istanbul | 6 | 3 |
| Tenochtitlán | 11 | 3 |
| Stuttgart | 6 | 5 |

Zusammen enthält die Welle 137 Orte und 58 Personen oder Gruppen. Sichere
Wahrzeichen und Bezirkszentren besitzen Kartenanker. Einträge ohne belastbare
Einzelposition bleiben im Katalog, damit die Karte keine Genauigkeit
vortäuscht.

## Reproduzierbarkeit

Die dritte Welle lässt sich mit folgenden Projektwerkzeugen nachvollziehen:

- `tools/extract_source_candidates.py`
- `tools/build_wave3_city_packages.py`
- `tools/review_source_candidates.py`
- `tools/import_archive_references.py`
- `tools/rebuild_search_index.py`
- `tools/validate_city_data.py`

