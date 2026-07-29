# Kandidatenaudit – Städtewelle 4

Stand: 28. Juli 2026

## Umfang

Die vierte Städtewelle umfasst die 33 verbleibenden Städte der
Werk-/Stadt-Matrix:

- Austin
- Baltimore
- Bangkok
- Brisbane
- Brüssel
- Buenos Aires
- Caracas
- Dallas/Fort Worth
- Dubai
- Dublin
- Havanna
- Johannesburg
- Kapstadt
- Las Vegas
- Lima
- Manaus
- Manila
- Melbourne
- Miami
- Nairobi
- Nürnberg
- Perth
- Phoenix
- Prag
- Salt Lake City
- San Diego-Tijuana
- Nuevo Santiago
- Sarajevo
- Singapur
- St. Louis
- Sydney
- Teheran
- Vancouver

Aus den vollständigen Textquellen wurden 684 Rohkandidaten extrahiert und
abschließend entschieden:

- 55 mit kanonischen Datensätzen zusammengeführt
- 629 als Überschrift, Regelbegriff, OCR-Fragment, generischer Begriff,
  Dublette oder nicht ausreichend lokal belegter Kandidat verworfen
- 0 offen

## Entscheidungen nach Stadt

| Stadt | Zusammengeführt | Verworfen | Offen |
|---|---:|---:|---:|
| Austin | 1 | 21 | 0 |
| Baltimore | 2 | 15 | 0 |
| Bangkok | 3 | 17 | 0 |
| Brisbane | 1 | 2 | 0 |
| Brüssel | 0 | 15 | 0 |
| Buenos Aires | 0 | 6 | 0 |
| Caracas | 6 | 33 | 0 |
| Dallas/Fort Worth | 3 | 27 | 0 |
| Dubai | 1 | 30 | 0 |
| Dublin | 4 | 37 | 0 |
| Havanna | 7 | 57 | 0 |
| Johannesburg | 1 | 4 | 0 |
| Kapstadt | 2 | 16 | 0 |
| Las Vegas | 4 | 59 | 0 |
| Lima | 3 | 6 | 0 |
| Manaus | 0 | 10 | 0 |
| Manila | 2 | 11 | 0 |
| Melbourne | 2 | 5 | 0 |
| Miami | 2 | 20 | 0 |
| Nairobi | 2 | 13 | 0 |
| Nürnberg | 0 | 6 | 0 |
| Perth | 1 | 11 | 0 |
| Phoenix | 0 | 38 | 0 |
| Prag | 0 | 28 | 0 |
| Salt Lake City | 0 | 5 | 0 |
| San Diego-Tijuana | 2 | 11 | 0 |
| Nuevo Santiago | 1 | 15 | 0 |
| Sarajevo | 0 | 12 | 0 |
| Singapur | 1 | 24 | 0 |
| St. Louis | 0 | 27 | 0 |
| Sydney | 2 | 14 | 0 |
| Teheran | 0 | 8 | 0 |
| Vancouver | 2 | 26 | 0 |

## Ergebnis

Alle Städte besitzen ein eigenständig ladbares Kartenpaket, ein
quellenbezogenes Stadtprofil und mindestens einen anklickbaren Lore-Bezugspunkt.
Stärkere Stadtquellen lieferten zusätzliche Orte, Personen und Gruppen. Bei
schwacher Quellenlage wurde der Datensatz nicht durch Vermutungen aufgefüllt.

Die vierte Welle ergänzte im historischen Vorlauf 69 Orte und 23 Personen
oder Gruppen. Nach dem anschließenden werkweisen Vollaudit umfasst der
Gesamtstand:

- 75 Stadtpakete
- 3.399 Orte
- 1.944 Personen oder Gruppen
- 5.343 stadtübergreifende Suchtreffer

## Reproduzierbarkeit

Die vierte Welle lässt sich mit folgenden Projektwerkzeugen nachvollziehen:

- `tools/extract_source_candidates.py`
- `tools/build_wave4_city_packages.py`
- `tools/review_source_candidates.py`
- `tools/import_archive_references.py`
- `tools/rebuild_search_index.py`
- `tools/validate_city_data.py`
