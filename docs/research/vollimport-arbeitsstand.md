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

## Offene Neuentitätsprüfung

Der erste Extraktionslauf für die damals vorhandenen acht Pakete ergab nach
mehreren Qualitätsfiltern 660 Kandidaten:

| Stadtpaket | Kandidaten |
| --- | ---: |
| ADL | 438 |
| Berlin | 45 |
| Denver | 34 |
| Hamburg | 19 |
| Manhattan | 53 |
| Rhein-Ruhr-Megaplex | 15 |
| Seattle | 49 |
| Toronto | 7 |

Die lokale Arbeitsdatei wird je Importwelle neu erzeugt; der aktuelle Lauf für
Chicago, Boston, Hongkong, London, München und Groß-Frankfurt enthält 1.652
weitere Rohkandidaten. Kandidaten sind noch keine Karteninhalte. Jeder Eintrag muss als neuer
Ort, neue Person oder Gruppe bestätigt, mit einem bestehenden Dossier
zusammengeführt oder begründet verworfen werden. OCR-Fehler und
fremdstädtische Nennungen dürfen nicht automatisch importiert werden.

## Status der Werk-/Stadt-Matrix

- 143 bereits kuratierte Quellenblöcke sind zusammengeführt.
- 47 nichtoffizielle Werk-/Stadt-Bezüge sind sichtbar ausgeschlossen.
- 6.818 Bezüge besitzen belastbare Volltexttreffer und bleiben offen.
- 3.200 Einzelbezüge benötigen eine redaktionelle Gegenprüfung.
- 1.397 Werk-/Stadt-Bezüge besitzen bereits einen dokumentierten Teilimport.

Keines der vierzehn Stadtpakete ist derzeit mit
`sourceCoverageComplete: true` markiert. Der Validator würde diese Markierung
ablehnen, solange offene Werk-/Stadt-Prüfungen bestehen.

## Neu aufgebaute Kartenpakete

Die ADL-Übersicht enthält 23 Städte, Allianzländer und Sonderregionen sowie
drei zentrale Mitglieder der Bundesregierung. Editionsbeschreibungen reichen
von SR1 bis SR6. Die Marker sind regionale Bezugspunkte und behaupten keine
flächengenauen Lore-Grenzen.

Die erste neue Städtewelle ist als sechs getrennt ladbare Pakete umgesetzt:

| Stadt | Orte und Bezirke | Personen und Gruppen |
| --- | ---: | ---: |
| Chicago | 20 | 14 |
| Boston | 17 | 10 |
| Hongkong | 17 | 5 |
| London | 18 | 12 |
| München | 24 | 6 |
| Groß-Frankfurt | 21 | 3 |

Die Einträge stammen aus den jeweils stadtbezogenen Primärquellen. Eindeutig
erhaltene Wahrzeichen und Lore-Distrikte besitzen Kartenanker; nur auf
Stadtebene belegte Orte bleiben ohne erfundene Koordinate im Katalog.

Der aktuelle Extraktionslauf für diese sechs Städte enthält 1.652
Rohkandidaten. Die obigen Entitäten sind der erste geprüfte Bestand. Die
übrigen Treffer bleiben offen, weil darunter Kapitelüberschriften,
Regelbegriffe, generische Gegnerprofile und beschädigte OCR-Zeilen vorkommen.
Sie werden nicht als scheinbar vollständige Lore-Objekte veröffentlicht.

## Nächste verbindliche Importreihenfolge

1. übrige Rohkandidaten der vorhandenen und neuen Karten entscheiden
2. Abschlussberichte für alle vierzehn vorhandenen Karten erzeugen
3. die erste Städtewelle um weitere sichere Entitäten und Grenzflächen
   vervollständigen
4. weitere Städte wellenweise nach Quellenstärke importieren

Ein Stadtpaket gilt erst dann als vollständig, wenn keine offene
Werk-/Stadt-Prüfung und kein unbearbeiteter Kandidat mehr vorhanden ist.
