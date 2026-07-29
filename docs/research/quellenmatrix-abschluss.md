# Werk-/Stadt-Matrix – abgeschlossener Entitätsaudit

Stand: 29. Juli 2026

Der Lauf `exhaustive-entity-audit-v2` hat sämtliche im Quellenregister
erkannten Werk-/Stadt-Beziehungen erneut geprüft. Anders als der
zurückgezogene Vorlauf unterscheidet er zwischen vorhandenen Dossiers,
veröffentlichbaren neuen Dossiers und begründet abgelehnten Struktur-,
Regel-, OCR-, Index- oder nichtlokalen Treffern.

## Abschlussstand

| Status | Anzahl |
|---|---:|
| offizielle Werk-/Stadt-Beziehungen | 10.161 |
| vollständig extrahiert oder mit Dossiers verknüpft | 875 |
| geprüft ohne eigenes lokales Dossier | 9.286 |
| offene offizielle Beziehungen | 0 |
| nichtoffizielle Beziehungen getrennt ausgeschlossen | 47 |

Alle 75 Stadtmanifeste tragen
`sourceCoverageComplete: true` und
`sourceEntityExtractionComplete: true`.

## Redaktionelle Dossierentscheidungen

Aus 3.977 positiven Neuentitätsvorschlägen wurden:

| Entscheidung | Orte | Personen | Gruppen | Gesamt |
|---|---:|---:|---:|---:|
| als neues Dossier bestätigt | 389 | 70 | 95 | 554 |
| mit vorhandenem Dossier zusammengeführt | 15 | 6 | 0 | 21 |
| begründet verworfen | 843 | 1.756 | 803 | 3.402 |

Der Veröffentlichungsbuilder führt anschließend Schreibvarianten und bereits
vorhandene Dossiers nochmals zusammen. Das vollständige Quellen-Supplement
enthält einschließlich der zuvor redaktionell geprüften Chicago-Ergänzung
389 Orte und 191 Personen oder Gruppen. Nicht belastbar positionierbare Orte
bleiben mit `geometry: null` im Katalog.

## Verbindliche Regeln

Eine Beziehung gilt nur als geschlossen, wenn:

1. jeder Kandidat als neues Dossier, vorhandenes Dossier oder begründete
   Nicht-Entität entschieden ist;
2. Edition, Werk und Fundstelle am übernommenen Dossier stehen;
3. gleiche Namen nicht automatisch Entscheidungen anderer Werke oder Städte
   erben;
4. Übersetzungen, OCR-Varianten und Klammerzusätze vor der Veröffentlichung
   nochmals dedupliziert werden;
5. aus einem Stadt- oder Teilraumbeleg keine Adresse oder Koordinate erfunden
   wird;
6. nichtoffizielle Quellen nicht mit dem offiziellen Bestand vermischt
   werden.

Die lokalen Quellenkontexte und Einzelentscheidungen liegen unter
`source-data/` und bleiben durch `.gitignore` vom veröffentlichten Repository
ausgeschlossen. Veröffentlicht werden nur redaktionelle Zusammenfassungen,
strukturierte Quellenangaben und die reproduzierbaren Prüfwerkzeuge.
