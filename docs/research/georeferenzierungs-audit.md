# Georeferenzierungs-Audit des Vollimports

Stand: 29. Juli 2026

## Ergebnis

Die 75 Stadtpakete enthalten insgesamt:

- 3.399 Orts- und Bezirksdossiers
- 2.702 sichtbare Punktgeometrien
- 697 bewusst nicht gesetzte Punktgeometrien
- 169 bereits vorhandene Bezirks- oder Lore-Grenzflächen
- 8 vorhandene Stadt- oder Regionsgrenzen

## Bedeutung der Punktgeometrien

Die sichtbaren Punkte besitzen unterschiedliche Genauigkeitsklassen. Ein
Bezirkszentrum, ein regionaler Bezugspunkt oder eine vorläufige
Teilraumzuordnung wird nicht als exakte Adresse ausgegeben. Die
`accuracy`- und `placement_note`-Felder bleiben für diese Unterscheidung
verbindlich.

Die 697 Einträge mit `geometry: null` sind kein technischer Fehler. Für diese
Orte ist nur die Stadt oder ein Lore-Teilraum belastbar belegt. Sie bleiben
über Katalog und globale Suche vollständig erreichbar, ohne eine erfundene
Kartenposition vorzutäuschen.

## Grenzflächen

Die detaillierten Grenzflächen stammen bislang aus den Karten, für die
Quellenkarten und Beschreibungstexte bereits gemeinsam abgeglichen wurden.
68 Pakete besitzen noch keine freigegebene Distrikt-Grenzfläche. Dort werden
die Lore-Distrikte über beschriftete, anklickbare Bezugspunkte erschlossen.

Es werden keine modernen Verwaltungsgrenzen oder rechteckigen
Übersichtsflächen als vermeintliche Shadowrun-Grenzen veröffentlicht.
Zusätzliche Polygone folgen später nur bei belastbarer Quellenkartografie.
