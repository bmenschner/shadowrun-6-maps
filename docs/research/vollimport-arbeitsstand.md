# Vollimport – Abschlussstand

Stand: 29. Juli 2026

## Ergebnis

Der vollständige TXT-Bestand wurde als 1.338 Dateien inventarisiert und zu
1.060 logischen Werken zusammengeführt. Das Register weist 247 exakte
Dateidubletten, 1.057 offizielle und 3 nichtoffizielle Werke aus. Alle 75
Städte und Regionen besitzen ein eigenständig ladbares Datenpaket.

Der relationenbasierte Lauf `exhaustive-entity-audit-v2` ist abgeschlossen:

- 10.161 offizielle Werk-/Stadt-Beziehungen geprüft;
- 875 Beziehungen mit vollständig extrahierten oder verknüpften Dossiers;
- 9.286 Beziehungen ohne eigenständiges lokales Dossier;
- 0 offene offizielle Beziehungen;
- 47 nichtoffizielle Beziehungen getrennt ausgeschlossen.

Der veröffentlichte Gesamtbestand umfasst:

- 3.399 Orte;
- 1.944 Personen oder Gruppen;
- 5.343 stadtübergreifende Suchtreffer;
- 2.702 Ortsgeometrien;
- 697 bewusst nur im Katalog geführte Orte ohne erfundene Position.

## Neuentitätsprüfung

Der breite Extraktionslauf bewahrt unterschiedliche Textfassungen und mehrere
Fundstellen desselben Namens. Die Abschlussprüfung arbeitet pro Kandidat,
Werk und Stadt. Sie verlangt einen direkten Stadtbezug, einen stabilen
Eigennamen sowie echte Orts-, Personen- oder Gruppenmerkmale.

| Entscheidung | Orte | Personen | Gruppen | Gesamt |
|---|---:|---:|---:|---:|
| neues Dossier | 389 | 70 | 95 | 554 |
| vorhandenes Dossier | 15 | 6 | 0 | 21 |
| keine veröffentlichbare Entität | 843 | 1.756 | 803 | 3.402 |

Tabellenüberschriften, Regelbegriffe, Ausrüstungsprofile, Nachrichtenzeilen,
Indexfragmente, reine Vergleichsnennungen und mehrdeutige stadtübergreifende
Ortskandidaten werden nicht als Dossiers veröffentlicht. Varianten mit
Klammerzusätzen, abweichender Zeichensetzung oder übersetzten Amts- und
Straßenbezeichnungen werden vor dem Paketbau erneut zusammengeführt.

## Veröffentlichung

`tools/build_audit_supplement_inputs.py` erzeugt aus bestätigten
Entscheidungen ausschließlich paraphrasierte, veröffentlichbare
Supplement-Eingaben. `tools/build_source_supplements.py` verbindet diese mit
den vorhandenen Stadtpaketen. Das vollständige Supplement enthält
einschließlich der früheren Chicago-Ergänzung 389 Orte sowie 191 Personen
oder Gruppen.

Die lokalen Fundstellenkontexte unter `source-data/` werden nicht
veröffentlicht. Jede publizierte Entität enthält strukturierte Werk-, Editions-
und Fundstellenangaben. Fehlende Einzelpositionen bleiben ausdrücklich
ungeoreferenziert.

## Technische Abschlussprüfung

Der Validator bestätigt:

- alle 75 Stadtpakete und ihre referenzierten Dateien;
- eindeutige lokale und globale IDs;
- vollständige Editionsbeschreibungen und Quellenbelege;
- gültige Personen-/Ortsverknüpfungen;
- überschneidungsfreie Gebietsstatusflächen;
- vollständige Suchindexabdeckung;
- geschlossene Quellen- und Entitätsmatrix.

Der Abschluss ist reproduzierbar über:

1. `tools/finalize_proposed_dossiers.py`
2. `tools/complete_entity_audit.py`
3. `tools/build_audit_supplement_inputs.py`
4. `tools/build_source_supplements.py`
5. `tools/finalize_source_coverage.py`
6. `tools/rebuild_search_index.py`
7. `tools/validate_city_data.py`

Spätere Quellenfunde oder bessere Kartenpositionen werden als neue,
nachvollziehbare Ergänzung verarbeitet; sie ändern nicht rückwirkend die
Entscheidungsregeln dieses Audits.
