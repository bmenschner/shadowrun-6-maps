# Quellenprüfung Denver und Manhattan

Stand: 26. Juli 2026

## Ziel und Aufnahmeregeln

Für beide Stadtpakete wurden die verfügbaren TXT-Exporte unter `C:\Users\Privat\Documents\Shadowrun\txtexports` editionsübergreifend durchsucht. Die offiziellen PDFs im übergeordneten Shadowrun-Ordner dienen bei unklaren Seiten, Karten und OCR-Stellen als Gegenprüfung.

Aufgenommen werden:

- benannte Orte mit Stadt-, Bezirks- oder Teilraumbezug;
- benannte Personen mit eigenständiger Lore-Rolle;
- benannte Gangs, Syndikate, Organisationen und andere Personengruppen;
- benannte Abenteuerorte, sofern ein belastbarer Stadt- oder Bezirksbezug vorhanden ist;
- unterschiedliche Editionsstände als Quellen- und Beschreibungsreiter desselben Lore-Objekts.

Nicht als eigene Einträge aufgenommen werden:

- bloße Reise-, Vergleichs- oder Nachrichtenreferenzen ohne städtischen Inhalt;
- generische Gegner, Archetypen und reine Regelbeispiele;
- nicht benannte Gebäude, Firmenstellen oder Zufallsbegegnungen;
- dieselben Inhalte aus parallelen deutschen und englischen Dateien ein zweites Mal.

Fiktionale Orte ohne belastbare Straßenadresse erhalten einen als vorläufig erkennbaren Distriktanker. Personen ohne festen Ort bleiben über Liste und Suche erreichbar, erhalten aber keinen erfundenen Kartenpunkt.

## Denver / Front Range Free Zone

Geprüfter Quellenbestand:

| Edition | Quelle |
| --- | --- |
| SR2 | `Denver: The City of Shadows` |
| SR3 | `Shadows of North America`; `Year of the Comet` |
| SR4 | `Welcome to Denver`; `Shadowrun Missions Season 2`; `Spy Games`; `Storm Front` |
| SR5 | Denver-Abenteuertrilogie |
| SR6 | `The Third Parallel` einschließlich nummerierter Karte |

Ergebnis:

- 219 Orte;
- 289 Personen beziehungsweise Gruppen;
- 19 Lore-Distrikte;
- alle 27 nummerierten Einträge der SR6-Karte;
- keine doppelten Orts-, Personen- oder Gruppen-IDs;
- keine normalisierten Namensdubletten.

Editionsbelege:

| Inhalt | SR2 | SR3 | SR4 | SR5 | SR6 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Orte | 58 | 2 | 37 | 15 | 153 |
| Personen/Gruppen | 25 | 3 | 202 | 37 | 51 |

Der vorher nicht erschlossene Denver-Teil von `Spy Games` ergänzt insbesondere Stadtprofile, Machtspieler, Syndikate, deren Führungspersonal, Gangs und den Denver Data Haven. `Storm Front` ergänzt die Krise von 2074 als eigenen SR4-Stand; `Shadows of North America` und `Year of the Comet` schließen die SR3-Lücke.

## Manhattan

Geprüfter Quellenbestand:

| Edition | Quelle |
| --- | --- |
| SR1 | `The Neo-Anarchist’s Guide to North America` |
| SR3 | `Shadows of North America` |
| SR4 | `The Rotten Apple: Manhattan`; `Shadowrun Missions Season 3`; `Konzernenklaven: Manhattan` |
| SR5 | `Gestohlene Seelen / Stolen Souls`; `Blutige Geschäfte / Bloody Business`; `Krieg um Manhattan / Battle of Manhattan` |
| SR6 | `Flüsternetze` einschließlich nummerierter Karte |

Ergebnis:

- 171 Orte;
- 165 Personen beziehungsweise Gruppen;
- 22 überschneidungsfreie Lore-Distrikte;
- alle 29 nummerierten Einträge der SR6-Karte;
- die benannten Schauplätze der vollständigen dritten Missionsstaffel;
- keine doppelten Orts-, Personen- oder Gruppen-IDs;
- keine normalisierten Namensdubletten.

Editionsbelege:

| Inhalt | SR1 | SR3 | SR4 | SR5 | SR6 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Orte | 47 | 0 | 81 | 60 | 47 |
| Personen/Gruppen | 11 | 1 | 37 | 83 | 44 |

Die Ergänzung erschließt besonders das Manhattan-Kapitel aus SR1, die Konzernenklaven-Ergänzungen, alle Missionsschauplätze der dritten Staffel sowie die in `Gestohlene Seelen` beschriebenen Konzerne, Behörden, Wissenschaftler, Syndikate, neo-anarchistischen Zellen und Sportteams.

## Technische Prüfung

Der globale Suchindex wird nach dem Stadtaufbau neu erzeugt und durchsucht unabhängig von Stadt-, Kategorien- und Editions-Layern weiterhin sämtliche Orte und Personen. `tools/validate_city_data.py` prüft Stadtmanifest, Quellenkatalog, Koordinaten, Referenzen, IDs, Editionswerte, Dateien und die Vollständigkeit des Suchindex.

Die Prüfung dieses Stands ergibt insgesamt 2.498 Suchobjekte aus acht Stadtpaketen. Denver und Manhattan besitzen keine ID- oder normalisierten Namensdubletten.

## Verbleibende redaktionelle Unsicherheit

„Vollständig“ bedeutet hier vollständig nach den oben definierten Aufnahmeregeln und dem derzeit lokal verfügbaren Quellenarchiv. OCR-Fehler, abweichende Eigennamenschreibweisen und nur bildlich eingezeichnete, im Text nicht benannte Details können trotz Prüfung verbleiben. Solche Fälle werden bei späteren Karten- oder PDF-Abgleichen am bestehenden Datensatz ergänzt und nicht als zweiter Eintrag angelegt.
