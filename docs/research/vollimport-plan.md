# Plan für den vollständigen Quellenimport

Stand: 28. Juli 2026

## Ziel

Der gesamte Bestand unter
`C:\Users\Privat\Documents\Shadowrun\txtexports` wird nachvollziehbar auf
kartenrelevante Daten geprüft. Relevante Inhalte werden in die vorhandenen
Stadtkarten oder in neue Stadtpakete übernommen.

**Vollständig** bedeutet dabei:

1. Jedes Quellenwerk ist im zentralen Quellenregister erfasst.
2. Doppelte Exporte, Übersetzungen und Kompilationen sind einem gemeinsamen
   Werk zugeordnet.
3. Für jede Quelle ist dokumentiert, welche Städte geprüft wurden.
4. Jeder Quellen-/Stadt-Abgleich besitzt einen abschließenden Status.
5. Jeder gefundene Kandidat wurde importiert, mit einem vorhandenen Eintrag
   zusammengeführt oder mit Begründung verworfen.
6. Alle Stadtpakete bestehen die technische und redaktionelle Prüfung.

Eine Volltextsuche oder ein einzelner Treffer gilt ausdrücklich nicht als
abgeschlossene Auswertung.

## Verbindlicher Datenumfang

Extrahiert werden:

- **Orte**: alle physischen, virtuellen, historischen und geografischen
  Kategorien
- **Personen**: Einzelpersonen und alle Personengruppen
- **Gruppen**: insbesondere Gangs, Syndikate, Crews, Teams, Kulte,
  Aktivistengruppen, Sicherheitskräfte und relevante Konzernabteilungen
- **Städte und Regionen**
- **Bezirke, Stadtteile, Sondergebiete und EXTER-Gebiete**
- **Ortsbeziehungen** zwischen Personen, Gruppen, Bezirken und Standorten
- **Editionsstände** SR1 bis SR6
- **Quellenangaben und belastbare Fundstellen**

Regelpassagen ohne benannte Orte, Personen oder Gruppen werden nicht in die
Karte übernommen, aber als geprüft und ohne Karteninhalt dokumentiert.

## Phase 1: Zentrales Quellenregister

Es wird ein maschinenlesbares Register für alle Quellenwerke angelegt. Die
Volltexte selbst werden nicht in das Repository kopiert.

Vorgesehene Felder:

- stabile Werk-ID
- Titel
- Edition
- Sprache
- Quellentyp: Regelwerk, Quellenband, Abenteuer, Roman, Handout, Karte,
  Nachrichtenmaterial oder Sonstiges
- offizieller beziehungsweise nichtoffizieller Status
- Varianten und Dateidubletten
- Inhalts-Hash
- logischer relativer Fundort
- deutsche oder englische Primärfassung
- bekannte Seiten- beziehungsweise Kapitelstruktur
- relevante Städte und Regionen

Nichtoffizielle Dateien, beispielsweise Fanstuff, werden nicht stillschweigend
ignoriert. Sie erhalten den Abschlussstatus `nichtoffiziell-ausgeschlossen`
und werden nicht mit offizieller Lore vermischt.

## Phase 2: Abdeckungsmatrix

Die Auswertung wird nicht nur pro Werk, sondern pro **Werk und Stadt**
geführt. Ein Werk kann beispielsweise für Berlin abgeschlossen, für Hamburg
aber noch offen sein.

Zulässige Abschlussstatus:

- `importiert`
- `zusammengeführt`
- `geprüft-ohne-relevanten-inhalt`
- `dublette`
- `übersetzung-eines-geprüften-werks`
- `nichtoffiziell-ausgeschlossen`
- `unlesbar-pdf-gegenprüfung-erforderlich`

Nicht zulässig für einen abgeschlossenen Lauf:

- `offen`
- `nur-volltexttreffer`
- `noch-zu-prüfen`

Zu jedem Status werden Datum, Prüflauf und kurze Begründung gespeichert.

## Phase 3: Quellen zerlegen und Kandidaten erfassen

Jedes Werk wird vollständig nach Kapiteln beziehungsweise Seitenblöcken
durchlaufen. Inhaltsverzeichnisse, Ortsregister, Personenregister,
Kartenlegenden und Abenteuer-NPC-Listen werden zusätzlich separat geprüft.

Für jeden Kandidaten werden zunächst gespeichert:

- Rohname und Aliasnamen
- Typ: Ort, Person, Gruppe, Bezirk, Stadt oder Region
- vermutete Stadt
- Edition
- Werk-ID
- Seite, Kapitel oder anderer belastbarer Locator
- kurzer lokaler Kontext
- mögliche Beziehungen zu vorhandenen Einträgen
- Qualitätsstufe der Fundstelle

Diese Kandidaten liegen während der Bearbeitung in ignorierten Arbeitsdateien.
In die veröffentlichten JSON-Dateien gelangen nur geprüfte Zusammenfassungen
und strukturierte Quellenangaben.

## Phase 4: Dubletten- und Editionsabgleich

Vor jedem Import wird geprüft:

- identischer Name
- Schreibvarianten und Übersetzungen
- Aliasnamen
- gleiche Adresse oder gleiche Kartenposition
- gleiche Funktion und Zugehörigkeit
- zeitlicher beziehungsweise editionsbedingter Nachfolger
- Filiale gegenüber eigenständigem Ort
- Person gegenüber gleichnamigem Ort

Regeln:

- Ein real identischer Ort bleibt ein gemeinsamer Eintrag.
- Verschiedene Editionsbeschreibungen erscheinen in SR1–SR6-Reitern.
- Historische und aktuelle Zustände werden nur getrennt, wenn es tatsächlich
  verschiedene Orte oder Identitäten sind.
- Mehrere Filialen erhalten mehrere Marker, aber nur dann ein gemeinsames
  Dossier, wenn die Quelle sie als gleiche Organisation behandelt.
- Gruppen werden unter Personen mit `entity_type: group` geführt.
- Eine Quelle darf nicht mehreren ähnlich benannten Einträgen zugewiesen
  werden, wenn der Bezug nicht eindeutig ist.

Für stadtübergreifend auftretende Personen und Gruppen wird zusätzlich eine
kanonische interne Identität vorgesehen. Die Stadtpakete behalten ihre
lokalen `global_id`-Werte, können aber auf dieselbe kanonische Entität
verweisen.

## Phase 5: Beschreibungen und Quellenqualität

Jeder importierte Eintrag erhält:

- eine redaktionell vollständige Kurzbeschreibung
- eine ausführliche Beschreibung, sofern die Quelle genügend Material bietet
- strukturierte Quellen mit Werk-ID, Edition und Fundstelle
- getrennte Editionsbeschreibungen
- Kennzeichnung als Quellenauszug, Quellenzusammenfassung, Kartenangabe,
  historischer Bezug oder Quellennachweis

Beschädigte OCR-Fenster dürfen nicht als Fließtext erscheinen. Wenn TXT und
Seitenstruktur nicht ausreichen, wird das vorhandene PDF visuell geprüft.
Kann keine vollständige Passage hergestellt werden, bleibt nur ein klar
bezeichneter Quellennachweis.

## Phase 6: Geografische Zuordnung

Positionen erhalten eine dokumentierte Genauigkeitsklasse:

1. exakte Quellenadresse
2. erhaltenes heutiges Wahrzeichen
3. eindeutige Kartenposition
4. eindeutiger Straßenzug
5. Bezirk oder Stadtteil
6. nur Stadt bekannt
7. nicht georeferenziert

Es werden keine Koordinaten erfunden. Nicht genau platzierbare Einträge bleiben
in der Liste auffindbar und erhalten entweder `geometry: null` oder einen
sichtbar gekennzeichneten Bezirksbezug.

Grenzen werden erst geändert, wenn Text, Quellenkarte und geografische
Leitlinie gemeinsam geprüft sind. Der bestehende Grundsatz
`EXTER > Anarcho > Normal` und die überschneidungsfreie Flächenpartition
bleiben verbindlich.

## Phase 7: Bestehende Karten vollständig nachziehen

Die vorhandenen Karten werden zuerst abgeschlossen. Jede Karte erhält einen
eigenen Importlauf und Abnahmebericht.

### Arbeitsreihenfolge

1. **Berlin**
   - fehlende SR6-Abenteuer
   - fehlende ADL-, Plot- und Regionalbände
   - abschließende Dubletten- und Quellenprüfung
2. **Hamburg**
   - Hamburgpaket und Reiseführer
   - Abenteuer und Plotbände
   - Deutsche Bucht und Umland
3. **Seattle**
   - bislang fehlende Plot-, Unterwelt- und Kampagnenbände
   - erneuter Abgleich klassischer Orte und wiederkehrender Personen
4. **Denver**
   - Drachen-, Artefakt- und Plotquellen
5. **Manhattan**
   - fehlende Plot-, Konzern- und Abenteuerbände
6. **Toronto**
   - vollständiger Kontrolllauf trotz derzeit guter Abdeckung
7. **Rhein-Ruhr-Megaplex**
   - `Neonoir`, `Flüsternetze` und die noch nicht belegten Nebenquellen
8. **ADL**
   - vollständiger Neuaufbau aus den Deutschland- und Datapuls-Bänden
   - vorhandene Stadtkarten als verlinkte Unterkarten

Eine Karte wird erst als vollständig markiert, wenn ihre Werk-/Stadt-Matrix
keinen offenen Eintrag mehr enthält.

## Phase 8: Neue Städte

Nach Abschluss der bestehenden Karten werden neue Stadtpakete angelegt.

### Welle 1: größte und klarste Quellenbasis

- Chicago
- Boston
- Hongkong
- London
- München
- Frankfurt

### Welle 2: eigene Stadtquellen oder große Regionalkapitel

- San Francisco
- Cheyenne
- Karlsruhe
- New Orleans
- Paris
- Montreal
- Neo-Tokio
- Washington FDC
- Los Angeles
- Bogotá
- Lagos
- Detroit
- Atlanta
- Portland
- Wien

### Welle 3: kompakte Stadtquellen

- Kairo
- Metrópole
- Butte
- Casablanca-Rabat
- Vladivostok
- Zürich
- Leipzig-Halle
- Québec
- Bremen
- Hannover
- Istanbul
- Mexiko-Stadt/Tenochtitlán
- Stuttgart

### Welle 4: Städte mit mehreren belastbaren Kapiteln

Die verbleibenden Kandidaten aus
`docs/research/quellenabdeckung-alle-karten.md` werden nach Quellenstärke
abgearbeitet. Vor jeder neuen Karte wird entschieden, ob ein eigenständiges
Stadtpaket oder eine übergeordnete Regionalkarte sinnvoller ist.

## Phase 9: Daten- und Leistungsarchitektur

Die PWA lädt weiterhin nur die ausgewählte Stadt vollständig.

Um Suche und Offlinebetrieb bei vielen Städten stabil zu halten:

- bleiben Orte, Personen, Grenzen und Kartenbilder pro Stadt getrennt
- erhält jede Stadt einen eigenen leichten Suchindex
- enthält der globale Index nur Name, Alias, Kategorie, Edition, Stadt und ID
- werden vollständige Beschreibungen erst mit dem Stadtpaket geladen
- werden schwere Detailkarten ausschließlich bei Bedarf gespeichert
- bleiben Arbeits-, Rohtext- und Abdeckungsdateien außerhalb des PWA-Caches

Die Suche bleibt von Kategorie- und Editionsschaltern unabhängig.

## Phase 10: Erweiterte Prüfungen

`tools/validate_city_data.py` wird ergänzt um:

- jede Quellen-ID muss im zentralen Register existieren
- jede Edition benötigt eine passende Quelle
- keine Quelle ohne Fundstelle
- keine offenen Werk-/Stadt-Prüfungen bei einer als vollständig markierten
  Karte
- keine unbearbeiteten Extraktionskandidaten
- keine doppelten kanonischen Entitäten
- keine beschädigten oder abrupt endenden Quellenauszüge
- keine nichtoffiziellen Quellen ohne sichtbare Kennzeichnung
- keine ungültigen Personen-/Ortsbeziehungen
- keine überlappenden Gebietsstatusflächen

Zusätzlich erzeugt jeder Importlauf einen Differenzbericht:

- neue Orte
- neue Personen und Gruppen
- zusammengeführte Dubletten
- neue Editionsstände
- verworfene Kandidaten mit Begründung
- Quellenstatus vor und nach dem Lauf

## Phase 11: Entwicklungs- und Veröffentlichungsablauf

Die Arbeiten erfolgen in lokalen Inhaltsbranches.

1. Quellenregister und Importwerkzeuge
2. ein Branch pro bestehender Stadt
3. lokale Vorschau und Validator
4. Quellen- und Differenzbericht prüfen
5. fertige Stadt in den gemeinsamen Entwicklungsstand übernehmen
6. erst nach Abschluss eines stabilen Pakets nach `main` mergen
7. Stadt-`dataVersion`, Suchindex und Release-Hinweise aktualisieren
8. GitHub Pages erst aus dem geprüften `main` veröffentlichen

Ein App-Cache-Update ist nur notwendig, wenn sich die Oberfläche ändert.
Reine Inhaltsimporte verwenden die versionierten Stadtpakete.

## Abschlusskriterien des Gesamtimports

Der Gesamtimport ist erst abgeschlossen, wenn:

- alle rund 1.044 Quellenwerke klassifiziert sind
- alle 1.338 Dateien einem Werk oder einer Dublette zugeordnet sind
- kein relevanter Werk-/Stadt-Abgleich offen ist
- kein Extraktionskandidat unbearbeitet ist
- jede der acht vorhandenen Karten einen Abschlussbericht besitzt
- für alle 67 Stadtkandidaten eine dokumentierte Entscheidung vorliegt
- alle angelegten Stadtpakete technisch validiert sind
- globale Suche und lokale Stadtansicht geprüft wurden
- ein abschließender Quellenabdeckungsbericht keine stillen Lücken mehr zeigt
