# Rhein-Ruhr-Megaplex 2082 – Quellenaudit

## Umfang

Der Inhaltsbestand wurde gegen das gesamte unter `txtexports` bereitgestellte
TXT-Archiv der Editionen SR1 bis SR6 geprüft. Identische Dateien werden vor
dem Abgleich über SHA-256 zusammengeführt. Der reproduzierbare Lauf schreibt
seine Kennzahlen nach `data/rhein-ruhr-2082/source-audit.json`.

Beim aktuellen Lauf wurden 1.091 unterschiedliche Textdateien geprüft. 90
davon enthalten mindestens vier eindeutige Rhein-Ruhr-Kontextbegriffe. Aus 79
dieser Dateien konnten insgesamt 1.148 zusätzliche Quellenbeziehungen zu
bereits verifizierten Orten oder Personen hergestellt werden.

## Primäre Inventare

- `Revierbericht 2082 – Karte` (SR6): 137 nummerierte Standorte der
  Recklinghausen-/Bochum-Detailkarte, 46 nummerierte Ziele der
  Revierübersicht und sämtliche Einträge der Neu-Essen-Detailkarte.
- `Revierbericht 2082` (SR6): Lore-Regionen, Bezirksbeschreibungen, besondere
  Orte, Machtspieler, Gangs, magische Gruppen, Unterweltorganisationen,
  „36 RRPler“ und die Spielleitungsorte.
- `Rhein-Ruhr-Megaplex` (SR4): Ortslisten, Brennpunkte, Schattenmärkte,
  Gastronomie, Kultur, Industrie, Magie, Matrix sowie die wichtigen Personen
  des Plexes.
- `Deutschland in den Schatten` (SR1/SR2), `Deutschland in den Schatten II`
  (SR3) und `Datapuls: ADL` beziehungsweise `Datapuls Komplett` (SR5):
  historische Stadtstände und editionsspezifische Nachweise.
- `Budenzauber`, `Vendetta` und `Domino-Effekte` (SR6): konkret bespielte
  Abenteuerorte, Hauptfiguren und Gruppen im RRP.

Weitere Regel-, Abenteuer-, Konzern-, Unterwelt-, Regional- und
Matrixquellen werden automatisch auf exakte Namen bereits gesicherter
RRP-Einträge geprüft. Dadurch entstehen Editions- und Quellenreiter, aber
keine künstlichen Marker aus beiläufigen Reiseerwähnungen.

## Aufnahmeregeln

1. Ein Eintrag benötigt einen eindeutigen RRP-Bezug oder eine Markierung auf
   einer offiziellen RRP-Karte.
2. Identische Orte, Personen und Gruppen werden editionsübergreifend in einem
   Dossier zusammengeführt.
3. Das in SR1 und SR2 identische frühe Deutschland-Material wird mit beiden
   Editionen gekennzeichnet.
4. Eine bloße Erwähnung außerhalb eines RRP-Kontexts erzeugt keinen Marker.
5. Fiktionale oder nicht hausgenau lokalisierbare Orte werden auf den
   belegten Stadt- oder Teilraum angenähert und entsprechend gekennzeichnet.
6. Gangs, Syndikate und andere Gruppen werden unter **Personen** geführt und
   nach Möglichkeit mit einem bestehenden Ort oder Gebiet verknüpft.
7. Die Suche bleibt unabhängig von Editions- und Kategorieebenen vollständig.

## Geografie und Grenzen

Die offizielle Revierübersicht bestimmt den Umfang des Megaplexes. Die 82
benannten oder innerhalb des Umrisses liegenden heutigen Kommunen dienen nur
als präzise Linienbasis. Direkt anklickbare Lore-Dossiers bilden die
zusammengefassten Regionen Bonn, Köln, Leverkusen/Bergisches Land, urbaner
Niederrhein, Düsseldorf, Duisburg, Oberhausen, Mülheim, Essen, GlaBotKi,
Bochum/Witten, Dortmund/Unna, Hagen/Sauerland, Wuppertal, Unter Tage,
Recklinghausen/Hauerbrache, Schwarzer Souk, Seelieviertel, Duisport und
Düsseldorf-Zentrum.

Die großräumige Lage fiktionaler Ziele bleibt eine Teilraumzuordnung. Eine
spätere straßengenaue Verfeinerung ändert weder IDs noch Quellen- und
Editionsdossiers.
