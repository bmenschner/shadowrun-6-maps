# Vollimport – Arbeitsstand

Stand: 28. Juli 2026

## Abgeschlossene technische Grundlagen

- 1.338 TXT-Dateien vollständig inventarisiert
- 1.060 logische Werke nach Titel- und Hashabgleich
- 247 exakte Dateidubletten
- 1.057 offizielle und 3 nichtoffizielle Werke
- 75 Städte und Regionen in der Abdeckungsmatrix
- 10.208 relevante Werk-/Stadt-Bezüge
- lokale, nicht veröffentlichte Kandidatenwarteschlange
- Prüfung des Quellenregisters und der Abdeckungsmatrix im Stadtvalidator

Das Quellenregister enthält keine Volltexte. Die lokalen Kandidatenkontexte
liegen unter `source-data/` und werden von Git ignoriert.

## Importierte Teilbelege vorhandener Karten

Der erste Importlauf verknüpft ausschließlich bereits geprüfte Entitäten mit
exakten Fundstellen aus weiteren offiziellen Quellen. Neue Marker wurden
dabei nicht automatisch erzeugt.

| Stadtpaket | verknüpfte Werke | Ortsbelege | Personen-/Gruppenbelege |
| --- | ---: | ---: | ---: |
| Berlin | 146 | 584 | 627 |
| Hamburg | 112 | 1.166 | 316 |
| Seattle | 398 | 1.656 | 2.753 |
| Rhein-Ruhr-Megaplex | 8 | 34 | 17 |
| Toronto | 12 | 5 | 24 |
| Denver | 227 | 416 | 1.018 |
| Manhattan | 74 | 238 | 397 |
| ADL | 228 | 1.104 | 49 |
| Chicago | 68 | 56 | 109 |
| Boston | 21 | 22 | 31 |
| Hongkong | 20 | 38 | 8 |
| London | 11 | 11 | 29 |
| München | 5 | 18 | 5 |
| Groß-Frankfurt | 67 | 24 | 95 |

Die Belege liegen jeweils im selben PDF-Seitenblock wie der Stadtbezug. Bei
TXT-Dateien ohne Seitenmarker wird ein begrenzter Textblock verwendet. Die
Verknüpfungen erscheinen als zusätzliche Editions- und Quellenangaben im
bestehenden Dossier.

## Neuentitätsprüfung

Die fünf abgeschlossenen Prüfläufe umfassen sämtliche 75 Kartenpakete:

| Prüflauf | Rohkandidaten | Zusammengeführt | Verworfen | Offen |
|---|---:|---:|---:|---:|
| ursprüngliche acht Bestandskarten | 3.235 | 376 | 2.859 | 0 |
| Städtewelle 1 | 1.652 | 265 | 1.387 | 0 |
| Städtewelle 2 | 1.181 | 184 | 997 | 0 |
| Städtewelle 3 | 619 | 134 | 485 | 0 |
| Städtewelle 4 | 684 | 55 | 629 | 0 |
| **Gesamt** | **7.371** | **1.014** | **6.357** | **0** |

Die lokale Arbeitsdatei wird je Importwelle neu erzeugt. Die
Abschlussentscheidungen sind in den fünf Kandidatenaudits dokumentiert.

## Status der Werk-/Stadt-Matrix

- 1.924 Werk-/Stadt-Bezüge sind mit Stadtquellen oder exakten
  Entitätsnachweisen zusammengeführt.
- 8.237 Volltextnennungen wurden ohne zusätzliches eigenständiges lokales
  Dossier abgeschlossen.
- 47 nichtoffizielle Werk-/Stadt-Bezüge sind sichtbar ausgeschlossen.
- 0 Werk-/Stadt-Bezüge sind offen.

Alle 75 Stadtpakete sind mit `sourceCoverageComplete: true` markiert. Der
Validator prüft, dass diese Markierung nur bei vollständig geschlossener
Werk-/Stadt-Matrix zulässig ist.

## Neu aufgebaute Kartenpakete

Die ADL-Übersicht enthält 23 Städte, Allianzländer und Sonderregionen sowie
drei zentrale Mitglieder der Bundesregierung. Editionsbeschreibungen reichen
von SR1 bis SR6. Die Marker sind regionale Bezugspunkte und behaupten keine
flächengenauen Lore-Grenzen.

Die erste neue Städtewelle ist als sechs getrennt ladbare Pakete umgesetzt:

| Stadt | Orte und Bezirke | Personen und Gruppen |
| --- | ---: | ---: |
| Chicago | 30 | 28 |
| Boston | 29 | 24 |
| Hongkong | 29 | 17 |
| London | 21 | 21 |
| München | 32 | 10 |
| Groß-Frankfurt | 28 | 4 |

Die Einträge stammen aus den jeweils stadtbezogenen Primärquellen. Eindeutig
erhaltene Wahrzeichen und Lore-Distrikte besitzen Kartenanker; nur auf
Stadtebene belegte Orte bleiben ohne erfundene Koordinate im Katalog. Die
Rohkandidaten dieser sechs Städte sind vollständig entschieden.

## Zweite Städtewelle

Die zweite Städtewelle wurde als fünfzehn getrennte Stadtpakete angelegt:

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

Für diese Welle wurden 1.181 Rohkandidaten vollständig entschieden. 184
Kandidaten wurden mit kanonischen Datensätzen zusammengeführt, 997 verworfen
und keiner blieb offen. Die Stadtpakete enthalten zusammen 134 Orte sowie 59
Personen oder Gruppen. Details enthält
`docs/research/welle-2-kandidatenaudit.md`.

## Dritte Städtewelle

Die dritte Städtewelle ergänzt dreizehn weitere Kartenpakete: Kairo,
Metrópole, Butte, Casablanca-Rabat, Vladivostok, Zürich, Leipzig-Halle,
Québec, Bremen, Hannover, Istanbul, Tenochtitlán und Stuttgart.

Alle 619 Rohkandidaten dieser Welle sind entschieden. 134 wurden mit
kanonischen Datensätzen zusammengeführt, 485 begründet verworfen und keiner
blieb offen. Die Pakete enthalten zusammen 137 Orte und 58 Personen oder
Gruppen. Details enthält `docs/research/welle-3-kandidatenaudit.md`.

## Vierte Städtewelle

Die vierte Städtewelle ergänzt die 33 verbleibenden Städte der
Werk-/Stadt-Matrix. Alle 684 Rohkandidaten wurden entschieden: 55 wurden mit
kanonischen Datensätzen zusammengeführt, 629 begründet verworfen und keiner
blieb offen.

Damit besitzen alle 75 erfassten Städte ein eigenständig ladbares Kartenpaket.
Der Gesamtstand umfasst 3.010 Orte, 1.753 Personen oder Gruppen und 4.763
stadtübergreifende Suchtreffer. Details enthält
`docs/research/welle-4-kandidatenaudit.md`.

## Nächste verbindliche Importreihenfolge

1. weitere Lore-Grenzflächen nur bei belastbarer Quellenkartografie ergänzen
2. neue Karten- und Quellenbestände nach demselben Auditverfahren importieren

Der Georeferenzierungs-Audit dokumentiert 2.702 sichtbare Punktgeometrien und
285 bewusst katalogisierte Einträge ohne erfundene Einzelposition. 68 Pakete
verwenden derzeit anklickbare Lore-Bezugspunkte statt nicht belegbarer
Grenzpolygone. Suche, Stadtpakete, Quellenmatrix, JavaScript und Offline-Cache
bestehen die Abschlussprüfung dieses Importstands.

Ein Stadtpaket gilt erst dann als vollständig, wenn keine offene
Werk-/Stadt-Prüfung und kein unbearbeiteter Kandidat mehr vorhanden ist.
