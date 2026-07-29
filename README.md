# Shadowrun 6 Maps – interaktive PWA

Die veröffentlichte Hybrid-PWA ist unter **[bmenschner.github.io/shadowrun-6-maps](https://bmenschner.github.io/shadowrun-6-maps/)** erreichbar. Sie enthält 75 eigenständig ladbare Stadt- und Regionspakete mit insgesamt 3.399 Orten sowie 1.944 Personen oder Gruppen.

## Lizenzen und Fanprojekt

Der selbst entwickelte HTML-, CSS-, JavaScript- und Werkzeugcode steht unter
der [GNU General Public License Version 3 oder später](LICENSE)
(`GPL-3.0-or-later`). Eigene redaktionelle Beschreibungen, geografische
Rekonstruktionen, Koordinaten und Datenbankbestandteile stehen, soweit nicht
anders gekennzeichnet, unter
[CC BY-NC-SA 4.0](LICENSE-CONTENT.md).

Diese Lizenzen gelten nicht für Shadowrun, dessen Marken, Figuren, Orte,
Settingelemente oder Inhalte offizieller Publikationen. Ebenfalls ausgenommen
sind offizielle Logos, Grafiken, Illustrationen, Karten, Fankit-Inhalte,
Textauszüge und sonstige Inhalte Dritter. OpenStreetMap-Daten bleiben unter
der ODbL. Die Anwendung ist ein inoffizielles, unentgeltliches Fanprojekt und
wird von The Topps Company, Inc., Catalyst Game Labs oder Pegasus Spiele weder
herausgegeben noch unterstützt oder geprüft.

Die Anwendung dient als Karten- und Orientierungshilfe sowie als Quellen- und
Spielleitungsindex. Teile des umfangreichen Datenbestands wurden unter
menschlicher Anleitung mithilfe KI-basierter Werkzeuge recherchiert,
extrahiert, strukturiert, zusammengefasst, zugeordnet und georeferenziert.
Eine redaktionelle Prüfung hat nur stichprobenartig stattgefunden. Angaben
können deshalb unvollständig, veraltet, uneindeutig oder fehlerhaft sein und
sollten anhand der jeweils ausgewiesenen offiziellen Originalpublikationen
überprüft werden.

`index.html` ist die einzige reguläre Anwendung für GitHub Pages und die installierbare Hybrid-PWA. Sie lädt nur das gewählte Stadtpaket und speichert es anschließend für den Offlinebetrieb.

Die modulare PWA wird über die HTTPS-Adresse oder einen lokalen Webserver geöffnet, weil Browser externe JSON-Stadtpakete unter `file://` blockieren können. PWA-Installation, Service Worker und automatische Updates funktionieren nur über HTTPS oder einen lokalen Webserver. Für die Offline-Nutzung muss die Webapp mindestens einmal vollständig online geladen worden sein.

Für die lokale Vorschau genügt unter Windows ein Doppelklick auf `Karte-lokal-starten.cmd`. Das Startsymbol verwendet die vorhandene Ubuntu-WSL-Umgebung, startet den Kartenserver unter `http://127.0.0.1:8765/?dev=1` und öffnet die Karte automatisch im Standardbrowser. Der lokale Entwicklungsmodus umgeht alte PWA-Daten, deaktiviert für diese Vorschau den Service Worker und lädt die Stadtdateien immer direkt aus dem Projektordner. Läuft genau dieser Kartenserver bereits, wird nur die Karte geöffnet. Zum Beenden wird das minimierte Fenster **„Shadowrun Kartenserver“** geschlossen.

Über **„Online / Offline“** in der oberen Menüleiste wird die Kartenbasis ohne Seitenwechsel umgeschaltet. Online stehen OSM, die verstärkte CARTO-Beschriftung und ÜK50 zur Verfügung. Offline werden alle externen Kartenebenen entfernt und die eingebettete Shadowrun-Übersicht aktiviert; Zoom, Kartenposition, Auswahl, Marker, Personen, Suche, Grenzen und Detailkarten bleiben erhalten. Eine manuelle Offlinewahl wird gespeichert. Bricht bei gewähltem Onlinemodus die Verbindung ab, schaltet die App vorübergehend offline und kehrt nach Wiederherstellung automatisch online zurück.

Über **„App installieren“** lässt sich die GitHub-Pages-Ausgabe in unterstützten Browsern als eigenständige Anwendung installieren. Chromium-Browser öffnen den nativen Installationsdialog; auf iPhone und iPad zeigt die Karte die passende Home-Bildschirm-Anleitung. Der Service Worker trennt Anwendung, Laufzeitdaten und versionierte Stadtpakete. Für die gewählte Stadt werden Manifest, Orte, Personen, Grenzen, Beschriftungen und Offline-Kartenbasis gespeichert. Externe OSM-, CARTO- und ÜK50-Kacheln werden nicht für Offlinegebiete vorgeladen. Sobald eine neue App-Version bereitsteht, erscheint ein kontrollierter Aktualisierungshinweis.

Über **„Light / Dark“** in der oberen Menüleiste lässt sich die gesamte Oberfläche umschalten. Der Lightmode übernimmt die helle Papier-, Magenta-, Anthrazit-, Türkis- und Orange-Palette der Berlin-2080-Karten v06; der gewählte Modus bleibt beim nächsten Öffnen erhalten. Marker, Gebietsstatus, exterritoriale Flächen sowie die einzeln aktivierbaren Bezirks-, Stadtteil-, Umland- und Stadtgrenzen wechseln auf abgestimmte kontrastreiche Farben, ohne ihre Ebenenfunktion zu verlieren.

Mit **„Orte / Personen“** wechselt die Seitenleiste zwischen dem Standortkatalog und den Personen, Gangs, Syndikaten und sonstigen Gruppen der gewählten Stadt. Die Kategorie **„Gangs“** führt Gruppen mit Typ, Editionsbeschreibung und Quelle. Historische Beschreibungen werden im selben Dossier über die Editionsschalter neben späteren Quellenständen angeboten. Personen und Gruppen werden – soweit eindeutig belegt – mit bestehenden physischen oder virtuellen Orten und Stadtgebieten verbunden. Die optionale Ebene **„Personenbezüge“** hebt diese verknüpften Marker hervor und erzeugt keine zusätzlichen Standortmarker.

Die Suche arbeitet unabhängig vom gewählten Umschalter und durchsucht immer Orte und Personen gemeinsam. Der globale Suchindex ist stadtübergreifend: Ein Treffer aus einer anderen Stadt wechselt beim Öffnen automatisch in deren Stadtpaket. Direktlinks enthalten deshalb optional die Stadt, zum Beispiel `?city=berlin-2080&person=nakaira`.

Die Kartenauswahl zeigt zunächst die acht umfangreichsten **Hauptkarten** Seattle, Berlin, Rhein-Ruhr-Megaplex, Denver, Hamburg, Manhattan, Toronto und Chicago. Über **„Weitere Städte anzeigen“** werden die übrigen Karten alphabetisch eingeblendet. Die Option **„Weitere Städte dauerhaft“** im Funktionsmenü speichert diese erweiterte Ansicht. Das Einklappen betrifft ausschließlich die Kartenauswahl: Globale Suche, Direktlinks und sämtliche Stadtpakete bleiben vollständig verfügbar. Suchtreffer der aktuellen Karte stehen vor den Treffern aus anderen Städten.

Im Ebenenmenü lassen sich alle im gewählten Stadtpaket vorhandenen Spielversionen von **SR1** bis **SR6** getrennt ein- und ausblenden. Ein Ort oder eine Person, der beziehungsweise die in mehreren Editionen vorkommt, bleibt dabei ein gemeinsamer Listeneintrag und ein gemeinsamer Marker. Die Ebenen bestimmen nur die normale Karten- und Listenansicht; die Suche bleibt bewusst vollständig und macht auch einen Treffer aus einer ausgeblendeten Edition vorübergehend sichtbar.

In den Detailkarten stehen bei mehreren vorhandenen Editionen direkt über dem Quellenauszug Umschaltflächen wie **SR3 / SR4 / SR5 / SR6** bereit. Quellenangaben tragen die zugehörige Edition in Klammern. Wo eine Edition einen Eintrag zwar belegt, aber noch kein eigener Auszug hinterlegt ist, zeigt die Karte einen gekennzeichneten Quellennachweis statt einen Text aus einer anderen Edition als editionsspezifisch auszugeben.

## Quellenbasis

Für die Recherche stehen offizielle PDFs und durchsuchbare TXT-Exporte der Editionen SR1 bis SR6 zur Verfügung. Ergänzende Informationen aus Shadowhelix werden immer als externe Quelle gekennzeichnet. Die vollständige Quellenrangfolge und die verbindlichen Kennzeichnungsregeln stehen in [SOURCES.md](SOURCES.md).

Das zentrale Quellenregister `data/source-registry.json` ordnet derzeit
1.338 Dateien 1.060 logischen Werken zu und weist 247 exakte Dateidubletten
aus. `data/source-coverage.json` führt für 75 Städte und Regionen jeden
erkannten Werk-/Stadt-Bezug mit einem eindeutigen Prüfstatus. Der werkweise
Entitätsaudit umfasst 10.161 offizielle Beziehungen; keine davon ist noch
offen. Ein bloßer Volltexttreffer gilt ausdrücklich nicht als abgeschlossene
Auswertung.

Interne Import-, Audit-, Build- und Georeferenzierungswerkzeuge sowie die
zugehörige Arbeitsdokumentation werden getrennt vom öffentlichen
Anwendungsrepository verwaltet. Im öffentlichen Bestand verbleiben nur die
von der Web-App benötigten Datenpakete und die allgemein relevanten
Quellenregeln.

## Einheitliche Begriffe

- **Datenmaterial/Quellen** umfasst sämtliche vermerkten offiziellen PDFs, TXT-Extrakte und eindeutig gekennzeichneten externen Informationen aus Shadowhelix.
- **Orte** umfasst alle Kategorien von Karteneinträgen und geografischen Inhalten.
- **Personen** umfasst alle Personengruppen und personenbezogenen Einträge.

Diese Oberbegriffe werden einheitlich in der Projektdokumentation und bei der weiteren Bearbeitung verwendet.

## Mehrstadt-Architektur

`data/cities.json` ist das Stadtverzeichnis. Jede Stadt besitzt unter `data/STADT-ID/` ein eigenes Manifest sowie getrennte Dateien für Orte, Personen, Detailkarten, Gebietsstatus, Bezirke, Stadtteile, Umland, Stadtgrenze, Beschriftungen und Quellen. Schwere Bilder liegen unter `assets/cities/STADT-ID/` und werden nur bei Bedarf geladen. Die Online-PWA hält dadurch keine Stadtgeometrien mehr direkt in `index.html`.

Ein neues Stadtpaket wird in dieser Reihenfolge ergänzt:

1. Stadt in `data/cities.json` registrieren.
2. `manifest.json` mit Kartenmittelpunkt, Zoom, Grenzen und Dateiverweisen anlegen.
3. Orte als GeoJSON und Personen als JSON hinzufügen.
4. Bezirks-, Stadtteil-, Gebiets- und Umlandgrenzen ergänzen.
5. Offline-Kartenbasis und optionale Detailkarten unter `assets/cities/` ablegen.
6. Globalen Suchindex neu erzeugen und das vollständige Stadtpaket validieren.

Alle Orts- und Personenobjekte besitzen zusätzlich zu ihren bisherigen IDs eine stadtweit stabile `global_id`. Personenverknüpfungen werden beim Erzeugen gegen vorhandene Orte geprüft. Der Validator verhindert doppelte IDs, ungültige Koordinaten, fehlende Dateien und nicht auflösbare Personenbezüge.

Neue oder aktualisierte Stadtpakete werden intern aus den jeweiligen
Primärquellen erzeugt und als eigenständig ladbare JSON-, GeoJSON- und
WebP-Dateien veröffentlicht. Quellen werden einem Editionskatalog zugeordnet;
Orte und Personen erhalten strukturierte Quellen, Spielversionen und
editionsweise Beschreibungen. Neue Städte benötigen keine Änderungen am
Kartenlader oder an der Stadtwahl.

Chicago besitzt eine quellenabgeglichene Containment Zone zwischen Belmont Avenue, Harlem Avenue, 115th Street und Lake Michigan; der heutige Stadtumriss bleibt als geografischer Kontext sichtbar, ohne eine unbelegte äußere Chicagoland-Grenze zu erfinden. Hamburg folgt den Shadowrun-Bezirken Altona, Eimsbüttel, Nord, Neue Mitte, Big Willi, Wandsbek, Bergedorf, Harburg, Pinneberg, Kaltenkirchen, Stade, Stormarn und Lauenburg; die 2045 eingemeindeten Umlandgebiete sind Teil der Stadtgrenze. Der Rhein-Ruhr-Megaplex folgt 82 auf der offiziellen Revierübersicht benannten oder innerhalb ihres Umrisses liegenden Kommunen statt nur der heutigen Kernstädte. Dadurch bilden auch die Korridore nach Soest sowie zwischen Düsseldorf, Köln und Bonn eine zusammenhängende Fläche.

Heutige Verwaltungsdaten stammen aus [Click That Hood](https://github.com/codeforgermany/click_that_hood), dem [U.S. Census Bureau TIGERweb](https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Places_CouSub_ConCity_SubMCD/MapServer), amtlichen Washington-State-/King-County-Daten sowie für die Hamburger Umlandkreise aus [deutschlandGeoJSON](https://github.com/isellsoap/deutschlandGeoJSON). Sie dienen ausschließlich als präzise Linienbasis. Toronto, Denver, Manhattan und Seattle besitzen eigene Lore-Bezirksflächen; die heutigen Gemeinden beziehungsweise Viertel bleiben als getrennt schaltbare Orientierungsebene erhalten. Bei der ADL werden heutige Bundesländer nicht mehr als Allianzländer ausgegeben; bis zu einer flächengenauen Georeferenzierung der Lore-Karte bleibt die interne Allianzländer-Ebene leer.

Seattle 2082 trennt politische Bezirke, Sicherheitsstatus und Sondergebiete voneinander. Redmond und Puyallup liegen als Barrens-Layer über ihren regulären Stadtbezirken. Council Island einschließlich der belegten 200-Meter-Gewässerzone ist fremdes Staatsgebiet, Fort Lewis ein militärischer Sonderbezirk und der Seattle Underground eine überlagernde vertikale Ebene. Die künstlichen Outremer-Inseln Nikko, Tanjo und Thesis sind als EXTER-Flächen eingezeichnet. Die Bezirksflächen sind mit den benannten Flüssen, Seen, Stadtgrenzen und Siedlungskanten aus den SR5-/SR6-Karten und Distriktdossiers abgeglichen. Nur nicht publizierte ländliche Zwischenlinien bleiben ausdrücklich als modelliert gekennzeichnet; die Statusflächen sind geometrisch überschneidungsfrei.

Der Seattle-Inhaltsbestand verbindet die Bezirkskapitel von `Emerald City` mit den Ortsregistern von SR1 bis SR5. Das SR5-Metroplexregister wurde vollständig von Nr. 001 bis Nr. 359 extrahiert; alle 359 Quellenadressen besitzen einen geprüften heutigen Straßen- oder Lore-Anker. 262 dieser Kartenorte sind bereits in SR1/SR2, 213 in SR3 und 286 in SR4 belegt. Editionsübergreifend identische Objekte bleiben ein gemeinsamer Eintrag. Historische, später entfallene Quellenbuchorte bleiben als eigene Editionsstände auffindbar. Die künstlichen EXTER-Inseln Nikko, Tanjo und Thesis besitzen eigene anklickbare Gebietsdossiers mit Konzernzuordnung und SR6-Quellenbeleg. Zusätzlich sind klassische Seattle-Abenteuer von SR1 bis SR3, der SR2-Mobkrieg, die Renraku-Arkologie- und Deus-Kampagne, die vollständige vierte Seattle-Missionsstaffel, `Ruling the Queen City`, `DocWagon 19`, `The Seattle Gambit`, `Free Seattle` und die City-Edition-Kontakte als eigenständige Quellenstände erschlossen. Der Bestand umfasst damit 728 Orte und 511 Personen beziehungsweise Gruppen. Wiederkehrende Personen und Orte erhalten Editionsbeschreibungen im selben Dossier. Die Detailkarte zeigt je Edition einen eigenen Auszug oder einen gekennzeichneten Quellennachweis.

Denver wird als **Front Range Free Zone** und nicht nur als heutiger Stadtkern behandelt. Der Kartenbereich reicht deshalb bis Colorado Springs. Die Bezirksfläche ist in die 19 in `The Third Parallel` genannten Distrikte aufgeteilt. Wo heutige Gemeinde- oder Denver-Stadtteilgrenzen den Lore-Namen entsprechen, bilden diese die harte Außenkante; die übrigen Korridore folgen der relativen Quellenkartenlage. Die publizierte ungefähr einen Kilometer breite äußere DMZ ist als eigener umlaufender Ring gezeichnet; FRFZ und DMZ überlappen sich nicht. Der Bestand verbindet `Denver: The City of Shadows` (SR2), `Shadows of North America` und `Year of the Comet` (SR3), `Welcome to Denver`, die vollständige zweite Missionsstaffel, `Spy Games` und `Storm Front` (SR4), die Denver-Abenteuertrilogie (SR5) sowie `The Third Parallel` einschließlich aller 27 nummerierten Kartenorte (SR6). Er umfasst 232 Orte und 299 Personen beziehungsweise Gruppen. Gleich gebliebene Orte und Personen - etwa Cap’n Kludge/Kluge oder Elizabeth „Betty“ Kalheim - werden nicht doppelt angelegt, sondern über getrennte Editionsreiter belegt.

Manhattan verbindet `The Neo-Anarchist’s Guide to North America` (SR1), `Shadows of North America` (SR3), `The Rotten Apple: Manhattan`, `Konzernenklaven: Manhattan` und die vollständige dritte Missionsstaffel (SR4), `Gestohlene Seelen`, `Blutige Geschäfte` und `Krieg um Manhattan` (SR5) sowie das Stadt- und Kampagnenmaterial aus `Flüsternetze` (SR6). Die heutigen Viertel wurden zu 22 überschneidungsfreien Lore-Gebieten wie Newtown, Terminal, The Pit, The Towers und Battery City zusammengeführt; Roosevelt Island sowie Randall’s/Ward’s Islands bleiben eigene Gebiete. Manhattan wird vollständig als exterritoriale MDC-Jurisdiktion dargestellt; Governors Island ist darin ohne Überlappung als Ares-Gebiet ausgeschnitten. Alle 29 Einträge der offiziellen Flüsternetze-Karte sind mit dem großen Stadtplan verknüpft. Zusammen mit Bezirken, historischen Schauplätzen, Kampagnenorten, Personen, Syndikaten, Gangs, Sportteams und magischen Gesellschaften enthält das Paket 185 Orte und 172 Personen beziehungsweise Gruppen. Erhaltene heutige Wahrzeichen besitzen geographische Anker; fiktionale oder stark veränderte Schauplätze sind sichtbar als vorläufige Teilraumpositionen gekennzeichnet.

Die Quellenmatrix, Aufnahmeregeln und Editionszahlen für Denver und Manhattan wurden intern vollständig dokumentiert.

Toronto 2080 wird nach dem Stadtteilkapitel von `30 Nächte und 3 Tage` in acht Lore-Distrikte gegliedert: Downtown/Alt-Toronto, Toronto Islands, East York, Uptown, West End, Etobicoke, North York und Scarborough. Heutige Stadtteilgeometrien liefern nur die präzisen Linien; Namen, Zusammenfassung und Zuordnung folgen SR6. Alle acht technisch gültigen Distriktflächen sind als quellenabgeglichen gekennzeichnet. Der Inhaltsbestand verbindet die lokalen Belege aus 27 Quellenwerken von SR1 bis SR6 mit der vollständig einzeln geprüften Kampagne `30 Nächte und 3 Tage`. Er umfasst 147 Orte und 188 Personen beziehungsweise Gruppen. Alle 44 Einträge der deutschen Posterkarte und alle 30 Einträge der Kampagnenübersicht sind mit der großen Karte und dem Detailkartenarchiv verknüpft.

Hamburg 2080 umfasst den Metroplex einschließlich der eingemeindeten Umlandbezirke und die Deutsche Bucht. Die 13 Shadowrun-Bezirke Altona, Eimsbüttel, Nord, Neue Mitte, Big Willi, Wandsbek, Bergedorf, Harburg, Pinneberg, Kaltenkirchen, Stade, Stormarn und Lauenburg besitzen direkt anklickbare Namensdossiers. Kaltenkirchens Außenkante ist mit dem südwestlichen Kreis-Segeberg-Ausschnitt der offiziellen Hamburg-2080-Übersicht abgeglichen. Wildost und Sachsenwald sind als eigene Lore-Räume erschlossen. Der Bestand umfasst 413 Orte und 89 Personen beziehungsweise Gruppen: alle 309 nummerierten Einträge der offiziellen Gesamtkarte, 37 Wildost-Detailpunkte, 19 zusätzliche Innenstadtpunkte, Orte aus den Stadtständen SR1 bis SR4 sowie Küsten-, Piraten- und Konzernmaterial aus SR6. Die 21 kartierten Straßengangs, Matrixgangs, Syndikate, Umweltgruppen und Piratencrews werden unter Personen als Gruppen geführt und soweit belegt mit Orten verknüpft. Die vollständig exterritoriale Sardinenstadt besitzt eine eigene schaltbare, auf Jahnring/Stadtpark, Hebebrandstraße, Sengelmannstraße und die westliche Bürostadtkante zurückgezogene Fläche samt anklickbarem Dossier.

Der Rhein-Ruhr-Megaplex 2082 umfasst 506 Orte und 157 Personen beziehungsweise Gruppen. Vollständig übernommen wurden die 137 nummerierten Bochum-/Recklinghausen-Detailpunkte, die 46 nummerierten Ziele der Revierübersicht und sämtliche markierten Standorte der Neu-Essen-Detailkarte. Hinzu kommen Lore-Regionen, Orte und Machtspieler aus `Rhein-Ruhr-Megaplex` (SR4) und `Revierbericht 2082` (SR6) sowie die lokalen Abenteuerbestände aus `Budenzauber`, `Vendetta` und `Domino-Effekte`. 1.091 unterschiedliche TXT-Exporte wurden geprüft; 79 RRP-relevante Dateien lieferten zusätzliche Quellen- oder Editionsbeziehungen. Gleiche Entitäten bleiben gemeinsame Dossiers, Gangs und Syndikate stehen unter Personen.

Die Gebietsflächen bilden eine überschneidungsfreie Partition mit der verbindlichen Reihenfolge `EXTER > Anarcho > Normal`. **EXTER** liegt zusätzlich als eigenständiger, harter Layer in `exterritorial.geojson`; Anarcho- und Normalflächen folgen vollständig den Lore-Bezirks- und Umlandgrenzen und werden anschließend um die EXTER-Flächen beschnitten. Kartenpakete ohne belegte Anarchogebiete zeigen keinen grauen Status und blenden den entsprechenden Legendeneintrag aus. Straßen, Autobahnen und Bahntrassen werden im Zweifel vollständig dem Konzerngebiet zugeschlagen, die Grenze verläuft also an der konzernabgewandten Außenkante. Flughafenflächen erhalten zusätzlich eine plausible Sicherheitszone bis zur nächsten verteidigbaren Barriere.

Für den Rhein-Ruhr-Megaplex ist die in `Rhein-Ruhr-Megaplex` (SR4) eindeutig beschriebene S-K-Enklave Essen als gelb-orange Konzernfläche ausgeschnitten. Erfasst sind die vollständig benannten Stadtteile, die südlich der A40 liegenden Teile von Holsterhausen und Bergerhausen sowie der vollständig exterritoriale Flughafen Essen-Mülheim. Der Stand ist zusätzlich mit `Revierbericht 2082` (SR6) abgeglichen und überschneidungsfrei aus der Normalfläche ausgeschnitten. Die 82 Kommunalgeometrien sind mit der offiziellen Revierübersicht abgeglichen und dienen als schaltbare Linienbasis; die weißen Lore-Regionsnamen öffnen die zusammengefassten Bezirksdossiers.

Alle fünf Berliner EXTER-Gebiete sind nach diesem Verfahren quellenabgeglichen. Renrakusan basiert auf dem früheren Ortsteil Prenzlauer Berg mit seinen durch ÜK50 und Lore belegten Grenzkorridoren, darunter Ringbahn/A100, Bornholmer Straße, Wisbyer Straße und Ostseestraße. Die amtliche Grundgeometrie wird defensiv nach außen erweitert, damit angrenzende Straßen- und Bahnflächen vollständig zum Konzerngebiet gehören. Bei Z-IC Tegel folgen Flughafen und Verkehrskorridore Bernauer Straße, A111 und Kurt-Schumacher-Damm; der gesamte Tegeler See einschließlich Großem Malchsee wird beansprucht, während Alt-Tegel an der tatsächlichen Außenkante des Tegeler Forsts endet. Nur an der Dicken Marie liegt eine kleine, quellenbelegte Sicherheitszone im Wald. AGC Siemensstadt folgt der in SR4 und SR6 vollständig exterritorial beschriebenen Einheit aus Siemensstadt, Jungfernheide und Charlottenburg-Nord. Für AZT Schönwalde und S-K Tempelhof bleibt die offizielle v06-Außenkontur maßgeblich: Die Quellen bestätigen beim Aztechnology-Bezirk den Spandauer Forst und den Übergangsraum nach Spandau sowie bei S-K Flughafen, Verteidigungsring, Fliegerviertel, Alt-Tempelhof und die kontrollierten Neuköllner Wohngebiete bis zu den belegten Übergängen.

Über **„Detailkarten“** öffnet sich ein eingebettetes, zoombares Kartenarchiv mit:

- zehn Orts-, Gebäude- und Kiezplänen (Babylon, Hauergasse, Kasbah, Kellerclubs, Osramhöfe, Schrapnell, Emma-Goldman-Schulkiez, Spreeland Funpark, Blauer Engel und Vesuv),
- dem Bezirksplan von Renrakusan,
- dem Liniennetzplan der Berliner Magnetschwebebahnen,
- zwei hochauflösenden Berlin-Referenzkarten v06.

Zugehörige Ortspläne sind zusätzlich direkt am jeweiligen Marker verlinkt. Die allgemeine Kellerclub-Karte sowie Netz- und Referenzkarten liegen nur im Kartenarchiv, damit keine künstlichen oder doppelten Standortmarker entstehen. Ein bestimmter Plan kann auch über `?atlas=schluessel` geöffnet werden, zum Beispiel `?atlas=hauergasse`.

Der Standortkatalog enthält sämtliche nummerierten Einträge 001–430 der v06-Übersichts- und Detailkarten. Die 42 Einträge der Renrakusan-Einzelkarte wurden mit deren genaueren Positionen verknüpft; das zuvor fehlende Otogibanshi-Viertel (S9) ist ergänzt. Wiederholte Filialen der Kanagawa Komfort Hotels werden als fünf Kartenmarker unter einem gemeinsamen Listeneintrag dargestellt. Die alphabetische Seitenleiste zeigt den vollständigen Katalog ohne frühere Begrenzung auf 180 Zeilen. Einzelne Einträge lassen sich über `?marker=ID` direkt öffnen, beispielsweise `?marker=168`.

Für die Beschreibungen wurde der vollständige bereitgestellte SR6-Textkorpus mit 125 Dateien abgeglichen. 19 zuvor reine Kartenangaben besitzen nun redaktionell zusammengefasste Quellenbeschreibungen mit Buch- und Seitenverweis, darunter acht Renrakusan-Orte sowie weitere v06-Marker wie Goldstein, Juanita’s, das Bundeswehrkrankenhaus Berlin-Oranienburg und das Z-IC-Forschungsklinikum. Kartenangaben ohne eindeutig zuordenbaren Fließtext bleiben bewusst als solche gekennzeichnet.

## Hinweise

Dies ist ein inoffizielles, nichtkommerzielles Fanprojekt. Shadowrun und zugehörige Bezeichnungen sowie Inhalte der verwendeten Quellenbücher verbleiben bei den jeweiligen Rechteinhabern. Kartengrundlagen und Grenzdaten werden in der Anwendung den jeweiligen Anbietern zugeordnet, darunter OpenStreetMap-Mitwirkende, Geoportal Berlin und GeoBasis-DE/LGB.
