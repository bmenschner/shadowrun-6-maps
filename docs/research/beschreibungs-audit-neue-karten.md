# Beschreibungs-Audit der neuen Stadtkarten

Stand: 28. Juli 2026

Geprüfte Pakete:

- Seattle 2082
- Denver 2081
- Manhattan 2083
- Toronto 2080
- Hamburg 2080
- Rhein-Ruhr-Megaplex 2082

## Ergebnis

Alle sechs Pakete besitzen jetzt:

- ein editionsbezogenes Stadt- oder Regionsprofil;
- einen nicht leeren Beschreibungstext für jeden Ort;
- einen nicht leeren Beschreibungstext für jede Person und Gruppe;
- ein Dossier für jede schaltbare Stadt- oder Bezirksfläche;
- Quellenangaben mit Editionskennzeichnung;
- eine funktionierende Auflösung der Bezirksfläche auf die Detailkarte.

| Karte | Orte | Personen und Gruppen | Stadt-/Bezirksflächen | Nicht auflösbare Flächen |
|---|---:|---:|---:|---:|
| Seattle | 532 | 468 | 12 | 0 |
| Denver | 219 | 289 | 19 | 0 |
| Manhattan | 171 | 165 | 22 | 0 |
| Toronto | 147 | 188 | 8 | 0 |
| Hamburg | 409 | 87 | 13 | 0 |
| Rhein-Ruhr | 500 | 153 | 82 | 0 |

## Quellenprofil und Kartennachweis

Die Anwendung unterscheidet bewusst zwei Textarten:

- **Ortsprofil, Personendossier, Gruppendossier oder Bezirksprofil:** Aus dem
  zugeordneten Datenmaterial lässt sich eine belastbare inhaltliche
  Zusammenfassung bilden.
- **Kartennachweis oder Quellennachweis:** Name, Kategorie, Rolle oder
  Kartenposition sind belegt, aber das zugeordnete Material trägt keine
  hinreichend eigenständige Fließtextbeschreibung. Der Eintrag nennt deshalb
  nur die belegten Angaben und erfindet keine zusätzliche Lore.

Reine Nachweise im aktuellen Bestand:

| Karte | Orte | Personen und Gruppen |
|---|---:|---:|
| Seattle | 299 | 0 |
| Denver | 167 | 205 |
| Manhattan | 69 | 71 |
| Toronto | 0 | 0 |
| Hamburg | 0 | 0 |
| Rhein-Ruhr | 68 | 0 |

Die hohen Werte in Seattle stammen überwiegend aus dem vollständigen
Kartenregister. In Denver und Manhattan enthalten Karten- und
Abenteuerregister zahlreiche Namen beziehungsweise Rollen, für die im
zugeordneten Datensatz kein sicher abgrenzbares eigenes Dossier ermittelt
wurde. Diese Einträge bleiben vollständig suchbar und werden mit ihrem
konkreten Quellenfund angezeigt.

## Ergänzungen

- Für jede neue Karte wurde ein Stadtprofil mit Editionsumschaltung ergänzt.
- Hamburgs 13 Lore-Bezirke wurden mit ihren Flächen verknüpft.
- Im Rhein-Ruhr-Megaplex erhielten alle 82 kartierten Städte und Kommunen eine
  auswählbare Detailkarte. Für 67 zuvor nicht beschriebene Kommunen wurde ein
  ausdrücklich als Kartennachweis markiertes Stadtprofil ergänzt.
- Die 36 Begegnungsfiguren aus „36 RRPler“ erhielten eigenständige
  Kurzbeschreibungen statt eines gemeinsamen Platzhaltertextes.
- Die Flächeninteraktion unterstützt jetzt neben `lore-district` auch
  Lore-Kommunen, innere und äußere Lore-Bezirke, Inselbezirke,
  Militärbezirke und fremde Enklaven.

## Technische Prüfung

- Datenvalidator: 8 Stadtpakete, 2.476 Orte, 1.506 Personen und Gruppen.
- Globaler Suchindex: 3.982 Einträge.
- Browserprüfung aller sechs Karten: Stadtprofil sichtbar, Bezirkslayer
  geladen, keine JavaScript-Fehler.
- Stichprobe Rhein-Ruhr: Klick auf die Stadtfläche Bergisch Gladbach öffnet
  das zugehörige Stadtdossier.
- Stadtübergreifende Suche bleibt unabhängig von aktiver Karte und
  Editionslayer funktionsfähig.
