# Kandidatenaudit – Städtewelle 2

Stand: 28. Juli 2026

## Umfang

Die zweite Städtewelle umfasst:

- San Francisco Metroplex
- Cheyenne
- Karlsruhe
- New Orleans
- Paris
- Montréal
- Neo-Tokio
- Washington FDC
- Los Angeles
- Bogotá
- Lagos
- Detroit
- Atlanta
- Portland
- Wien

Aus den vollständigen Textquellen wurden für diese Städte 1.181 Rohkandidaten
extrahiert. Jeder Kandidat wurde abschließend einer Entscheidung zugeordnet:

- 184 mit einem kanonischen Datensatz zusammengeführt
- 997 als Überschrift, Regelbegriff, OCR-Fragment, generischer Begriff,
  Dublette oder nicht ausreichend belegter Kandidat verworfen
- 0 offen

## Entscheidungen nach Stadt

| Stadt | Zusammengeführt | Verworfen | Offen |
|---|---:|---:|---:|
| Atlanta | 6 | 85 | 0 |
| Bogotá | 24 | 63 | 0 |
| Cheyenne | 27 | 79 | 0 |
| Detroit | 5 | 61 | 0 |
| Karlsruhe | 5 | 40 | 0 |
| Lagos | 18 | 80 | 0 |
| Los Angeles | 14 | 81 | 0 |
| Montréal | 0 | 20 | 0 |
| Neo-Tokio | 24 | 156 | 0 |
| New Orleans | 6 | 61 | 0 |
| Paris | 24 | 116 | 0 |
| Portland | 10 | 70 | 0 |
| San Francisco Metroplex | 17 | 60 | 0 |
| Washington FDC | 0 | 5 | 0 |
| Wien | 4 | 20 | 0 |

## Erzeugte Stadtpakete

| Stadt | Orte | Personen und Gruppen |
|---|---:|---:|
| San Francisco Metroplex | 6 | 11 |
| Cheyenne | 22 | 4 |
| Karlsruhe | 4 | 1 |
| New Orleans | 6 | 2 |
| Paris | 12 | 13 |
| Montréal | 1 | 0 |
| Neo-Tokio | 17 | 9 |
| Washington FDC | 1 | 0 |
| Los Angeles | 11 | 2 |
| Bogotá | 17 | 5 |
| Lagos | 13 | 5 |
| Detroit | 5 | 2 |
| Atlanta | 7 | 0 |
| Portland | 9 | 4 |
| Wien | 3 | 1 |

Die Quellenlage ist je Stadt unterschiedlich stark. Bei Montréal und
Washington FDC konnten beispielsweise nur belastbare Stadtprofile angelegt
werden. Fehlende Orte oder Personen wurden nicht durch Annahmen aufgefüllt.

## Reproduzierbarkeit

Die zweite Welle lässt sich mit folgenden Projektwerkzeugen nachvollziehen:

- `tools/extract_source_candidates.py`
- `tools/build_wave2_city_packages.py`
- `tools/review_source_candidates.py`
- `tools/import_archive_references.py`
- `tools/rebuild_search_index.py`
- `tools/validate_city_data.py`
