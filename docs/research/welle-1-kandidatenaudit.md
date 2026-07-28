# Kandidatenaudit – Städtewelle 1

Stand: 28. Juli 2026

## Umfang

Geprüft wurden die 1.652 automatisch extrahierten Rohkandidaten für Chicago,
Boston, Hongkong, London, München und Groß-Frankfurt. Die lokalen
Quellenkontexte liegen ausschließlich unter `source-data/` und werden nicht
veröffentlicht.

| Ergebnis | Anzahl |
| --- | ---: |
| mit einem kanonischen Dossier zusammengeführt | 265 |
| als Überschrift, Regel-/OCR-Fragment, generische Kategorie, Dublette oder nicht lokaler Treffer verworfen | 1.387 |
| offen | 0 |

## Ergebnis nach Stadt

| Stadt | Zusammengeführt | Verworfen | Offen |
| --- | ---: | ---: | ---: |
| Boston | 53 | 217 | 0 |
| Chicago | 64 | 427 | 0 |
| Groß-Frankfurt | 27 | 119 | 0 |
| Hongkong | 49 | 256 | 0 |
| London | 46 | 283 | 0 |
| München | 26 | 85 | 0 |

Die Zusammenführungen umfassen sowohl bereits vorhandene Dossiers als auch
64 in diesem Prüflauf neu angelegte kanonische Orte, Personen und Gruppen.
Falsch erkannte Entitätstypen wurden korrigiert. Kombinierte OCR-Spalten wie
`Garching Grünwald` und `Theatinerstraße Schrannenhalle` wurden in die
tatsächlich getrennten Dossiers aufgelöst.

## Kartenstand nach dem Import

| Stadt | Orte und Bezirke | Personen und Gruppen |
| --- | ---: | ---: |
| Chicago | 30 | 28 |
| Boston | 29 | 24 |
| Hongkong | 29 | 17 |
| London | 21 | 21 |
| München | 32 | 10 |
| Groß-Frankfurt | 28 | 4 |

Nicht belastbar einzeln positionierbare Orte bleiben mit `geometry: null` im
Katalog. Geografische Bezugspunkte wurden nur für Quellenadressen, erhaltene
Wahrzeichen und eindeutige Lore-Teilräume gesetzt.

## Reproduzierbarkeit

- `tools/build_wave1_city_packages.py` erzeugt die kuratierten Stadtpakete.
- `tools/review_source_candidates.py` dokumentiert Alias-, Typ- und
  Spaltentrennungen und schließt die lokale Warteschlange.
- `tools/import_archive_references.py` ergänzt weitere exakte
  Quellen-/Editionsbelege für die bestätigten Dossiers.
- `tools/rebuild_search_index.py` erzeugt den globalen Suchindex.
- `tools/validate_city_data.py` prüft alle Stadtpakete.

