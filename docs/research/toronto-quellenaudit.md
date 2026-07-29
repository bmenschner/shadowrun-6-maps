# Quellenprüfung Toronto

Stand: 26. Juli 2026

## Prüfumfang

Der vollständige Textbestand unter `C:\Users\Privat\Documents\Shadowrun\txtexports` wurde editionsübergreifend nach Toronto durchsucht. Der Lauf fand 96 Dateien mit mindestens einer Toronto-Nennung. Doppelte deutsche/englische Exporte und verschiedene Scans desselben Werks wurden als ein Quellenwerk behandelt. Das SR6-Abenteuer `30 Nächte und 3 Tage` wurde zusätzlich Nacht für Nacht gegen Orte, Hauptdarsteller, benannte Nebenfiguren, Gangs, Kulte, Syndikate und Konzerne geprüft.

Aufgenommen werden:

- benannte Orte, Einrichtungen, Stadtteile und historische Ereignisse mit Toronto-Bezug;
- eigenständig benannte oder beschriebene Personen und Wesen;
- Gangs, Syndikate, Kulte, Firmen, Behörden, Teams und andere Personengruppen;
- ältere Editionsstände als zusätzliche Quellen- und Beschreibungsschalter desselben Objekts.

Nicht aufgenommen werden bloße Reise- oder Vergleichsnennungen, reine Weltkartenbeschriftungen, die U-Boot-Klasse `Toronto`, unbenannte Zufallsorte und Gegnerprofile sowie Personen, deren einzige Verbindung ein Flug über Toronto ist. Nicht hausgenau lokalisierbare, aber eindeutig einem Torontoer Teilraum zugeordnete Inhalte erhalten einen als angenähert gekennzeichneten Marker. Personen ohne belastbaren Standort bleiben in der vollständigen Personenliste suchbar, erhalten aber keinen erfundenen Ortsbezug.

## Verwendete Quellenwerke

| Edition | Quellenwerke | Verwendeter Inhalt |
| --- | --- | --- |
| SR1 | `Mercurial` | Hungerunruhen von 2048 |
| SR2 | `Target: UCAS`; `Underworld Sourcebook / Unterwelt-Quellenbuch`; `Prime Runners`; `Lone Star`; `Corporate Shadowfiles / Megakons`; `Super Tuesday`; `Portfolio of a Dragon / Portfolio eines Drachen` | Front, Organisationen, Konzernstandorte und historische Personen |
| SR3 | `Nordamerika in den Schatten / Shadows of North America`; `Target: Matrix / Brennpunkt Matrix`; `Dragons of the Sixth World / Drachen der 6. Welt`; `System Failure / Systemausfall`; `Threats 2`; `State of the Art: 2064` | Stadtprofil, Matrix, Medien, Konzerne, Kult und Personen |
| SR4 | `Jet Set`; `Sixth World Almanac / Almanach der Sechsten Welt`; `Emergence / Emergenz`; `Artifacts Unbound`; `SRM04-07: Burn`; `SRM04-12: Showcase`; `Corporate Guide / Konzerndossier` | Club, Stadtstand, Kult, Loge, Sport und Lone-Star-Vertrag |
| SR5 | `Shadowrun: Anarchy` | Rose Red |
| SR6 | `Toronto Poster 2080`; `30 Nächte und 3 Tage`; `Blackout / Cutting Black`; `Schlagschatten / Slip Streams`; `Konzerngewalten / Power Plays` | Karten, Lore-Distrikte, vollständige Kampagnenorte und -figuren, Blackout-, Magie- und Konzernbelege |

Alle 27 im Toronto-Paket registrierten Quellenwerke werden von mindestens einem Ort oder Dossier tatsächlich zitiert.

## Ergebnis

- 147 Orte;
- 188 Personen beziehungsweise Gruppen, davon 126 Einzelpersonen/Wesen und 62 Gruppen;
- acht Lore-Distrikte;
- 44 von 44 Einträgen der deutschen Toronto-Posterkarte;
- 30 von 30 Einträgen der Übersicht aus `30 Nächte`;
- keine doppelten IDs oder normalisierten Namensdubletten;
- alle Ortsbezüge der Personendossiers zeigen auf vorhandene Orte.

Editionsbelege überschneiden sich, weil ein gemeinsames Objekt mehrere Editionsstände besitzen kann:

| Inhalt | SR1 | SR2 | SR3 | SR4 | SR5 | SR6 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Orte | 1 | 4 | 5 | 4 | 0 | 136 |
| Personen/Gruppen | 0 | 10 | 9 | 9 | 1 | 162 |

Zu den neu geschlossenen SR6-Lücken gehören unter anderem St. Luke’s United, Thornhill Commons, CMC-Verteilzentrum, The Cluster, TTC-Schrottplatz, Old Yonge, The Purrfect Pet, Union Station, Silverthorn-Bibliothek und The People’s Bank sowie Helena Myrryr, Rennie Browser, Zennia, Togle, Mezcallus Negh, Blight, die Keepers, Tamanous und die South Cabbage Warlordz. Ältere Ergänzungen umfassen unter anderem Taylor Pauline, Arthur Vogel, die Magical Reform Society, Shadowland Toronto, Transys Neuronet America, Realm Beyond, Ice Princess, Rose Red und New Toronto Re.

## Lore-Grenzen

Die acht Distrikte folgen den Beschreibungen auf S. 11-17 von `30 Nächte und 3 Tage`. Die 140 heutigen Torontoer Referenzviertel wurden dafür überschneidungsfrei den Lore-Distrikten Downtown/Alt-Toronto, Toronto Islands, East York, Uptown, West End, Etobicoke, North York und Scarborough zugeordnet. Die Toronto Islands wurden aus dem kombinierten heutigen Waterfront-/Insel-Datensatz als eigene Fläche herausgelöst.

Thornhill wird entsprechend der Quelle North York zugerechnet, Markham Scarborough. Pearson Airport bleibt als westlicher Metroplex-Verkehrsknoten Etobicoke zugeordnet. Die separat schaltbare Ebene der heutigen Viertel behält ihre modernen Namen und dient ausschließlich der Orientierung.

## Technische Prüfung

Beide Detailkarten enthalten exakt ihre jeweiligen Marker-IDs. Der globale Suchindex wurde neu erzeugt und enthält nach dem werkweisen Vollaudit 5.343 stadtübergreifende Einträge. Die Suche enthält unabhängig vom aktiven Edition-Layer Namen, Aliasse, Beschreibungen, Rollen, Gruppen, Quellen und alle Editionsbeschreibungen. `tools/validate_city_data.py` bestätigt alle 75 Stadtpakete und den vollständigen Suchindex.

„Vollständig“ bezeichnet den aktuell verfügbaren offiziellen Quellenbestand nach den oben genannten Aufnahmeregeln. Künftige Kartenabgleiche können angenäherte Positionen präzisieren, ohne neue Dubletten zu erzeugen.
