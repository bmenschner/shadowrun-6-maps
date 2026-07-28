# Quellenbasis

Für neue Orte, Personen, Städte, Organisationen und andere Lore-Inhalte werden ausschließlich die folgenden Quellen verwendet.

## 1. Offizielle Publikationen

Die vollständigen PDFs liegen lokal im übergeordneten Shadowrun-Ordner:

- Windows: `C:\Users\Privat\Documents\Shadowrun`
- relativ zum Projekt: `..`

Offizielle Publikationen sind die verbindliche Quelle. Quellenangaben nennen nach Möglichkeit Titel, Seite und Edition, zum Beispiel `Berlin 2080, S. 93 (SR6)`.

## 2. TXT-Exporte

Die durchsuchbaren Textextrakte der verfügbaren Publikationen liegen unter:

- Windows: `C:\Users\Privat\Documents\Shadowrun\txtexports`
- relativ zum Projekt: `../txtexports`

Die TXT-Dateien dienen zum Auffinden und Abgleichen von Informationen. Zitiert wird die zugrunde liegende Publikation, nicht der Dateiname des Textextrakts. Zweifelhafte OCR-Stellen, Seitenangaben und inhaltliche Widersprüche werden anhand des offiziellen PDFs geprüft.

### Zentrales Quellenregister

- `data/source-registry.json` enthält stabile Werk-IDs, Edition, Sprache,
  Quellentyp, offiziellen Status, logische Dateivarianten und Inhalts-Hashes.
- `data/source-coverage.json` führt den Prüfstatus pro Werk und Stadt.
- `source-data/` enthält lokale Extraktions- und Prüfkontexte und wird niemals
  veröffentlicht.
- Ein exakter Orts- oder Personenfund in einer Quelle ist ein Teilimport. Das
  Werk gilt erst als vollständig importiert, wenn auch alle neuen Kandidaten,
  Dubletten und Ausschlüsse redaktionell entschieden wurden.
- Nichtoffizielle Dateien werden im Register mit
  `nichtoffiziell-ausgeschlossen` dokumentiert und nicht mit offizieller Lore
  vermischt.

## 3. Shadowhelix

[Shadowhelix](https://shadowhelix.de/) darf ergänzend als externe Communityquelle verwendet werden. Jeder daraus übernommene oder abgeleitete Inhalt wird eindeutig mit **„Shadowhelix (extern)“**, dem direkten Artikellink und dem Abrufdatum gekennzeichnet.

Bei einem Widerspruch hat die offizielle Publikation Vorrang. Ein ausschließlich durch Shadowhelix belegter Inhalt darf nicht als offiziell bestätigt dargestellt werden.

## Redaktionelle Regeln

- Beschreibungen werden eigenständig zusammengefasst und nicht als längere Passagen übernommen.
- Editionen werden getrennt belegt; ein späterer Quellenstand ersetzt nicht automatisch frühere Editionsbeschreibungen.
- Nachweislich inhaltsgleiche Veröffentlichungen für mehrere Regeleditionen werden am selben Datensatz mit allen belegten Editionen geführt. Jede Ausgabe erhält dabei einen eigenen Quellenbeleg und Beschreibungsreiter.
- Derselbe Ort oder dieselbe Person bleibt editionsübergreifend ein gemeinsamer Datensatz, sofern es sich eindeutig um dasselbe Lore-Objekt handelt.
- Mehrfach vorhandene TXT- oder PDF-Ausgaben erzeugen keine doppelten Kartenobjekte.
- Gebietsgrenzen werden zuerst aus der offiziellen Lore-Karte übernommen und anschließend mit ausdrücklich genannten Straßen, Gewässern und Grenzbauwerken abgeglichen. Amtliche heutige Geometrien dienen als Linienbasis, ersetzen aber keine abweichende Lore-Angabe.
- Für zusätzliche Städte und Regionen stammen die heutigen Verwaltungsgeometrien aus dem öffentlichen Projekt [Click That Hood](https://github.com/codeforgermany/click_that_hood). Sie werden in den GeoJSON-Eigenschaften als geografische Linienbasis gekennzeichnet und gelten nicht als Lore-Quelle.
- Für Seattle dienen amtliche Küsten- und Verwaltungsgeometrien von King County GIS Open Data und Washington State ausschließlich als geografische Linienbasis. Bezirkszuordnung und Status folgen `Freiheit für Seattle` (SR6), `Emerald City` (SR6), der SR6-Posterkarte und der detaillierten SR5-Metroplexkarte.
- Der Seattle-Inhaltsbestand nutzt zusätzlich die Stadt- und Abenteuerquellen des lokalen SR1–SR6-Textarchivs. Klassische Abenteuer-Schauplätze erhalten nur dann einen Kartenpunkt, wenn eine Seattle-Bezirkszuordnung belegt ist; nicht straßengenaue Positionen sind in der Detailkarte ausdrücklich als vorläufige Bezirksanker markiert.
- Denver wird gemäß den offiziellen Publikationen als Front Range Free Zone bis Colorado Springs erfasst. `Denver: The City of Shadows` (SR2), `Shadows of North America` und `Year of the Comet` (SR3), `Welcome to Denver`, SRM02, `Spy Games` und `Storm Front` (SR4), die Denver-Abenteuertrilogie (SR5) sowie `The Third Parallel` und dessen Karte (SR6) werden als getrennte Editionsstände geführt. Heutige Ortsanker präzisieren nur die Lage; die wechselnden Sektoren und Distrikte folgen der jeweiligen Lore.
- Für Manhattan bilden `The Neo-Anarchist’s Guide to North America` (SR1), `Shadows of North America` (SR3), `The Rotten Apple: Manhattan`, SRM03 und `Konzernenklaven: Manhattan` (SR4), `Gestohlene Seelen`, `Blutige Geschäfte` und `Krieg um Manhattan` (SR5) sowie `Flüsternetze` und dessen nummerierte Karte (SR6) den stadtbezogenen Quellenbestand. Die heutige Inselgeographie ist nur Linien- und Positionsbasis; Konzernstadt-Bezirke, Wiederaufbau, Untergrund und Arkologien folgen den Publikationen.
- Für Toronto wurden alle 96 Dateien mit Toronto-Nennung im Textarchiv geprüft. 27 Quellenwerke von `Mercurial` (SR1) bis `Konzerngewalten` (SR6) liefern tatsächlich verwendete Belege; `30 Nächte und 3 Tage` wurde zusätzlich Nacht für Nacht auf Orte, Personen, Gangs und Organisationen abgeglichen. Die acht Lore-Distrikte und ihre Beschreibung folgen dem SR6-Stadtteilkapitel; heutige Torontoer Stadtteilgrenzen dienen nur als präzise Linienbasis. Die vollständige Matrix und die Ausschlussregeln stehen in `docs/research/toronto-quellenaudit.md`.
- Die 19 Denver-Distrikte folgen dem Stand von `The Third Parallel` (SR6). Amtliche TIGERweb-Gemeindegrenzen und heutige Denver-Stadtteile werden nur dort als harte Linie übernommen, wo Name und Quellenlage übereinstimmen. Die rund einen Kilometer breite äußere DMZ ist mangels vermessener Lore-Koordinaten als vorläufig georeferenzierter Arbeitsumriss ausgewiesen.
- Manhattan wird nach `The Rotten Apple` vollständig der extraterritorialen MDC-Jurisdiktion zugeordnet. Governors Island ist daraus geometrisch ausgeschnitten und separat Ares zugewiesen. Die Lore-Viertel werden aus den im Quellenband beschriebenen Teilräumen gebildet; heutige Viertelnamen bleiben ausschließlich in der Referenzebene sichtbar.
- Toronto wird als Metroplex aus Downtown/Alt-Toronto, Toronto Islands, East York, Uptown, West End, Etobicoke, North York und Scarborough modelliert. Die in den Quellen North York beziehungsweise Scarborough zugerechneten Orte Thornhill und Markham sowie Pearson Airport bleiben auch dann Teil des Inhaltsbestands, wenn ihre heutigen Verwaltungszuordnungen abweichen.
- Einmalige Abenteuerfiguren ohne eindeutig belegten festen Standort bleiben als Personen auffindbar, erhalten aber keinen künstlichen Personenmarker. Benannte Gangs, Syndikate und andere Personengruppen werden unter Personen geführt; generische Gegner- oder Regelprofile werden nicht als eigene Lore-Personen angelegt.
- Council Island, Fort Lewis, Outremer, Redmond/Puyallup Barrens und der Seattle Underground werden als voneinander unabhängige politische, Sicherheits- oder Sonderebenen modelliert. Der Untergrund und der Barrens-Status dürfen deshalb die Oberflächenbezirke nicht ersetzen.
- Die Hamburger Umlandkreise stammen ergänzend aus [deutschlandGeoJSON](https://github.com/isellsoap/deutschlandGeoJSON). Auch diese Geometrien sind nur die Linienbasis für die im offiziellen Hamburg-Kartenpaket und in `Datapuls Hamburg` belegten Shadowrun-Bezirke.
- Nicht durch eine offizielle Karte oder einen Quellentext belegte heutige Unterteilungen werden ausschließlich als **geografische Referenzgrenzen** angeboten. Sie dürfen weder in Beschriftung noch Tooltip als Shadowrun-Bezirk erscheinen.
- Die ADL-Ansicht zeigt keine heutigen Bundesländer als Allianzländer. Die interne Ebene bleibt leer, bis Norddeutscher Bund, Westphalen, Nordrhein-Ruhr, Hessen-Nassau, Groß-Frankfurt, Westrhein-Luxemburg, Badisch-Pfalz, Franken, Württemberg, Bayern, Trollrepublik Schwarzwald und die weiteren Lore-Gebiete flächengenau georeferenziert sind.
- Die ADL-Übersicht verwendet regionale Bezugspunkte für Allianzländer,
  Metropolregionen und Sondergebiete. Diese Punkte sind keine behaupteten
  Grenzmittelpunkte und ersetzen keine später georeferenzierten Lore-Flächen.
  Berlin, Hamburg und Rhein-Ruhr verweisen auf ihre eigenständigen
  Detailpakete, ohne deren Einzel-POIs in der ADL-Karte zu verdoppeln.
- Chicago wird aus `Bug City` (SR2), `Feral Cities` (SR4), `Mission Chicago`,
  `Schatten über Chicago` und `Chicago Chaos` (SR5) aufgebaut. Boston folgt
  `Lockdown` beziehungsweise `Sperrzone Boston` und den zugehörigen
  Abenteuern. Hongkong verwendet `Runner Havens` und `Hong Kong Neon
  Contrails (2050)`, London das `London Sourcebook` und `London Falling`,
  München `München Noir` und `Datapuls: München`, Groß-Frankfurt `Chrom &
  Dioxin` und `Datapuls Frankfurt`.
- Bei diesen neuen Karten besitzen Lore-Distrikte einen dokumentierten
  geografischen Bezugspunkt. Ein Einzelort ohne Adresse, erhaltenes
  Wahrzeichen oder eindeutige Quellenkartenposition bleibt mit
  `geometry: null` im Katalog. Er wird gesucht und angezeigt, erzeugt aber
  keinen irreführenden Marker.
- Bezeichnet die Lore ein vollständiges früheres Stadt- oder Ortsteilgebiet, wird dessen amtliche Geometrie als exakte Außengrenze verwendet; dies gilt derzeit für Renrakusan sowie AGC Siemensstadt einschließlich Siemensstätten.
- Für die Nordgrenze Renrakusans gilt `Netzgewitter`, S. 18-19, als zusätzlicher Detailbeleg: Pankow/Dreamland beginnt nördlich der Wisbyer Straße und wird dem Anarchogebiet zugeordnet. Die offizielle Berlin-2080-Übersicht weist auch Lichtenberg und Kreuzhain östlich beziehungsweise südöstlich von Renrakusan als anarchistisch aus.
- Gegensätzliche Gebietsstatus werden als exklusive Flächen modelliert; Normal-, Anarcho- und Konzerngebiete dürfen sich nicht flächig überlagern.
- Shadowiki wird nicht als Quelle verwendet.

Die tatsächlich für eine Stadt verwendeten Bücher und Nachweise werden zusätzlich im jeweiligen Stadtpaket unter `data/STADT-ID/sources.json` geführt.
