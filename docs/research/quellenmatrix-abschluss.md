# Abschluss der Werk-/Stadt-Matrix

Stand: 28. Juli 2026

## Ergebnis

Die vollständigen Textquellen enthalten 1.338 Dateien. Nach Titel-, Varianten-
und Hashabgleich bilden sie 1.060 logische Werke. Diese Werke erzeugen 10.208
relevante Beziehungen zu den 75 Kartenpaketen.

Nach Abschluss aller Kandidatenläufe besitzt jeder Werk-/Stadt-Bezug einen
abschließenden Status:

| Status | Anzahl |
|---|---:|
| zusammengeführt | 1.924 |
| geprüft ohne zusätzliches lokales Dossier | 8.237 |
| nichtoffiziell ausgeschlossen | 47 |
| offen | 0 |

`zusammengeführt` umfasst sowohl ausdrücklich in einem Stadtpaket geführte
Quellen als auch Werke mit mindestens einer exakten Verknüpfung zu einem
bereits geprüften Ort, einer Person oder einer Gruppe.

`geprüft-ohne-relevanten-inhalt` bedeutet nicht, dass das Werk die Stadt
überhaupt nicht erwähnt. Der Stadtbezug wurde im vollständigen Kandidatenlauf
geprüft, ergab aber kein zusätzliches eigenständiges lokales Dossier.

## Qualitätsgrenze

Der Abschluss der Quellenmatrix ist ein inhaltlicher Quellenabschluss, keine
Behauptung flächengenauer Kartografie. Einträge ohne belastbare Adresse oder
Kartenposition bleiben im Katalog. Bezirks- und Sondergebietsgrenzen werden
erst als Polygon veröffentlicht, wenn Quellenkarte, Beschreibung und
geografische Leitlinie gemeinsam eine belastbare Abgrenzung ermöglichen.

## Technische Absicherung

- Alle 75 Stadtpakete tragen `sourceCoverageComplete: true`.
- Der Validator weist eine Karte mit offenen Werk-/Stadt-Bezügen zurück.
- Der Abschlusslauf ist als `full-source-import-2026-07-28` in der Matrix und
  in den Stadtmanifesten vermerkt.
- Nichtoffizielle Quellen bleiben getrennt und werden nicht in die offizielle
  Lore übernommen.
