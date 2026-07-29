#!/usr/bin/env python3
"""Build the Hamburg 2080 lore, place and people package.

The official SR5 Hamburg map is the authoritative inventory for the 309
numbered overview locations.  It is combined with the Wildost and Innenstadt
detail maps, district dossiers from Datapuls: Hamburg, older Hamburg chapters,
and the supplied SR6 material.  Locations without a surviving street-level
reference deliberately remain district-level approximations.
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

from build_us_city_content import CityCatalogue, city_edition, jitter, name_key, write_json


ROOT = Path(__file__).resolve().parents[1]
CITY_ID = "hamburg-2080"
CITY_DIR = ROOT / "data" / CITY_ID
CORPUS = Path("/mnt/c/Users/Privat/Documents/Shadowrun/txtexports")

DATAPULS = CORPUS / "Shadowrun 5/03 - Quellenbände/Shadowrun 5D - Datapuls Hamburg.txt"
SR1_HAMBURG = CORPUS / "Shadowrun 1/Shadowrun 1D - Deutschland in den Schatten.txt"
SR2_HAMBURG = CORPUS / "Shadowrun 2/Shadowrun 2D - Deutschland in den Schatten (searchable).txt"
SR3_HAMBURG = CORPUS / "Shadowrun 3/Shadowrun 3D - Deutschland in den Schatten II (searchable).txt"
SR4_HAMBURG = CORPUS / "Shadowrun 4/Shadowrun 4D - Schattenstädte (searchable).txt"
SR6_HAMBURG = CORPUS / "Shadowrun 6/shadowrun_6d_quellenbaende_text/Shadowrun 6D - HH Broschüre.txt"


BOOKS = [
    {"id": "dids-sr1", "title": "Deutschland in den Schatten", "edition": "SR1"},
    {"id": "dids-sr2", "title": "Deutschland in den Schatten", "edition": "SR2"},
    {"id": "dids2-sr3", "title": "Deutschland in den Schatten II", "edition": "SR3"},
    {"id": "schattenstaedte-sr4", "title": "Schattenstädte", "edition": "SR4"},
    {"id": "missions-hamburg-sr4", "title": "Missions Hamburg", "edition": "SR4"},
    {"id": "woelfe-st-pauli-sr4", "title": "Die Wölfe von St. Pauli", "edition": "SR4"},
    {"id": "datapuls-hamburg-sr5", "title": "Datapuls: Hamburg", "edition": "SR5"},
    {"id": "hamburg-map-sr5", "title": "Hamburgpaket – Karte", "edition": "SR5"},
    {
        "id": "hamburg-detail-maps-sr5",
        "title": "Hamburgpaket – Karten und Karteikarten",
        "edition": "SR5",
    },
    {
        "id": "hamburg-character-cards-sr5",
        "title": "Hamburg-Zusatzpack – Charakter-Karteikarten",
        "edition": "SR5",
    },
    {"id": "hamburg-guide-sr6", "title": "Hamburg – Venedig des Nordens", "edition": "SR6"},
    {
        "id": "piraten-bucht-sr6",
        "title": "Datapuls: Piraten der Deutschen Bucht",
        "edition": "SR6",
    },
]


ANCHORS = {
    "Hamburg": (53.5511, 9.9937),
    "Altona": (53.5550, 9.8800),
    "Eimsbüttel": (53.5840, 9.9550),
    "Nord": (53.6120, 10.0220),
    "Neue Mitte": (53.5520, 10.0020),
    "Big Willi": (53.5020, 9.9950),
    "Wandsbek": (53.6020, 10.1320),
    "Bergedorf": (53.4850, 10.2150),
    "Harburg": (53.4050, 9.9850),
    "Pinneberg": (53.6760, 9.7350),
    "Stade": (53.6000, 9.4700),
    "Stormarn": (53.7040, 10.3150),
    "Lauenburg": (53.5550, 10.5200),
    "Kaltenkirchen": (53.8500, 9.9950),
    "Wildost": (53.4760, 9.8950),
    "Hafen": (53.5300, 9.9700),
    "Sachsenwald": (53.5350, 10.3650),
    "Deutsche Bucht": (54.0500, 8.4500),
    "Norddeutscher Bund": (53.9000, 9.3000),
}


DISTRICTS = [
    (
        "Neue Mitte",
        "Die Schwarze Flut hat Hamburg-Mitte fast vollständig überformt. St. Pauli, Altstadt, St. Georg, Neue HafenCity, Neue Mitte-Ost und Hafen bilden einen wasserreichen Bezirk aus Fleeten, Brücken, Tourismus, Medien, Nachtleben und Hafenlogistik.",
        "Datapuls: Hamburg, S. 27–32",
    ),
    (
        "Altona",
        "Altona bewahrt seine offene, eigenwillige Identität. Das alternative alte Altona und Othmarschen, die Architektensiedlungen Bahrenfelds sowie die kriminell dominierten Hochhausgebiete Lurup und Osdorf liegen hier dicht beieinander.",
        "Datapuls: Hamburg, S. 33–35",
    ),
    (
        "Eimsbüttel",
        "Eimsbüttel steht stark unter dem Einfluss der DeMeKo und der Medienwirtschaft. Konzernhochhäuser, Stars, Journalisten, Hochschulen, Hagenbecks Tierpark und ein allgegenwärtiger Strom aus Werbung und Überwachung prägen den Bezirk.",
        "Datapuls: Hamburg, S. 36–39",
    ),
    (
        "Nord",
        "Nord wird von Alster und Konzernen bestimmt. Luxuslagen am Wasser, die vollständig exterritoriale Sardinenstadt, Konzernkliniken und Mini-Arkologien stehen dem alternativen Barmbek und seinen heruntergekommenen Fleeten gegenüber.",
        "Datapuls: Hamburg, S. 40–43",
    ),
    (
        "Stade",
        "Stade ist Hamburgs westlicher Industriebezirk. Petrochemie, Schwerindustrie, Pharma, Güterbahnhöfe und exterritoriale Werksflächen grenzen an verseuchte Elbmarschen, Wattsammlerkommunen und Operationsräume militanter Ökogruppen.",
        "Datapuls: Hamburg, S. 44–46",
    ),
    (
        "Harburg",
        "Harburg verbindet Klein-Russland und Vory-Einfluss mit modernen Wohnlagen, Wald, Heide und ländlichen Südgebieten. Ein massiver Schutzzaun trennt den Bezirk vom benachbarten Wildost.",
        "Datapuls: Hamburg, S. 47–49",
    ),
    (
        "Bergedorf",
        "Bergedorf umfasst die verbliebenen Vier- und Marschlande. Giftige Flutmarschen, billige Industrieflächen, Massenwohnanlagen, Terminalverkehr und zunehmende Ganggewalt machen den Bezirk zu einem angespannten Übergangsraum.",
        "Datapuls: Hamburg, S. 50–52",
    ),
    (
        "Lauenburg",
        "Lauenburg verbindet Sachsenwald, Ökoschamanismus, Seminarbetriebe, Agrar- und Lebensmittelindustrie sowie teure Landhausidylle. Hinter der grünen Kulisse arbeiten Schmidts, Schattenwirtschaft und lokale Machtzirkel.",
        "Datapuls: Hamburg, S. 53–54",
    ),
    (
        "Stormarn",
        "Stormarn ist der wohlhabendste und gepflegteste Bezirk des Plexes. Großhansdorf und Ahrensburg bilden abgeschirmte Luxuslagen mit privaten Sicherheitsdiensten, sauberen Seen, Parks und exklusiver Versorgung.",
        "Datapuls: Hamburg, S. 55–57",
    ),
    (
        "Wandsbek",
        "Wandsbek beherbergt Regierungsviertel, Rathaus, Gerichte und HanSec-Hauptquartier. Mittelschichtquartiere und Einkaufsachsen stehen dem dicht besiedelten, von Clans und Gangs geprägten Groß-Bramfeld gegenüber.",
        "Datapuls: Hamburg, S. 57–59",
    ),
    (
        "Kaltenkirchen",
        "Kaltenkirchen umfasst den Orbitalflughafen mit Lufthansa City, das dicht bebaute Norderstedt und den energieerzeugenden Nordosten. Flughafenökonomie, Vergnügungskomplexe und kritische Energieinfrastruktur bestimmen den Bezirk.",
        "Datapuls: Hamburg, S. 60–61",
    ),
    (
        "Pinneberg",
        "Pinneberg ist von Nordseeschlick, Klärwerken, Müllverarbeitung und Ersatznahrungsproduktion geprägt. Konzerninvestitionen, Tagelöhner, Wattsammler, Vory und lokale Gangs teilen sich den stark belasteten Bezirk.",
        "Datapuls: Hamburg, S. 62–64",
    ),
    (
        "Big Willi",
        "Big Willi ist Hamburgs schwer gesichertes Inselgefängnis. Doppelter Mauerwall, Hafenfortifikation, Straflinks, entnommene Ware und magieunterdrückende Medikamente machen die Anlage zu einem eigenen, brutalen Mikrokosmos.",
        "Datapuls: Hamburg, S. 75–78",
    ),
]


MAP_LEGEND = r"""
Ausgehen
1|Alsterbühne
2|ARA
3|Baikal
4|Black Velvet
5|Blankeneser Meile
6|Boudoir
7|Chez Marie
8|Chrome Club
9|Cirque Heloise
10|Courage
11|Deutsches Schauspielhaus
12|Die Weiße Schlange
13|Dollhouse
14|Doppel:U
15|Empire
16|Eroscenter
17|Evita Santa
18|Gala Musical-Theater
19|Glückspilz
20|Große Freiheit 36
21|Grüschtsch
22|Hangar
23|HanseDome
24|Lager 13
25|Laufhaus 13
26|Lebensmüde
27|Lust-Dungeon
28|Markthalle
29|Medeas Bunker
30|Minous Massage
31|Neue Staatsoper
32|Ohnsorg-Theater
33|Onboard
34|Pipipupy
35|Rising Tide
36|Salambo
37|Schmidts Tivoli
38|Sugarbabe Club
39|The Orchid Hamburg
40|TriBühne
41|Vollblut
42|Zerling Rush
Bars und Kneipen
43|Alster-Lounge
44|Baimaika
45|Bücherhalle
46|Butt
47|Café Möhrchen
48|Chapeau Claque
49|Chicken Palace
50|Kinkerlitzchen
51|Konkret
52|Kontor
53|Leonies Eck
54|Literaturcafé
55|Mission 6
56|Moorbek-Klause
57|Mottenstall
58|Nixenbar
59|Over the Top
60|Port Royal
61|Postamt
62|Postamt
63|Pussycat
64|Red Cloud
65|Schippbröök
66|Sebastian Falk
67|Sonderbar
68|Suzzana
69|Trotzdzemski
70|Walhalla
71|Wavebreaker
72|Wodny Bar
73|Zum Ausguck
74|Zum Tanzenden Einhorn
Einkaufen
75|Alsterpalast
76|Alte Eule
77|Anielski-Joop Catwalk
78|Aptekarka
79|Barkenthals
80|Blauer Klotz
81|Collectors Paradise
82|Der Talismann
83|Einkaufszentrum am Westring
84|Eltons Elektro-Allerlei
85|He-She-It
86|Hermetikum
87|Hurti-Kurti
88|Itzehoer Mitternacht-Markt
89|Joostlander
90|La Dolce Vita
91|Mundsburger Meile
92|Neo Eims Gallery
93|Nordstern-Mall
94|Organic Mind
95|Rohrbert
96|SchluScha
97|Skrapjard
98|Stefans Stotschnja
99|Stuffer-Plus Megamarkt Neuallermöhe-West
100|Szabladin
101|Ysops
102|Zaba & Nurek
Freizeit
103|Airbus-Arena
104|Alpen-Hütte
105|Aqua-Paradies
106|Best Buddies
107|Bramfelder Kampfzone
108|Combatbiking-Arena
109|Forever Young
110|Freys Sphären
111|Gestüt Pehmöller
112|Golfpark Sieker Grund
113|HafenCity Sport- und Jachthafen e.V.
114|Hagenbecks Tierpark
115|Mikkado
116|Narko Nora
117|Neo-Luna
118|Planten un Blomen
119|Rennbahn Osdorf
120|Seaweed
121|Stadtkrieg-Simulator
122|Stadtpark
123|Stalingrad
124|Trabrennbahn Bahrenfeld
125|Wandsbeker Schlossmarina
126|Wohlfühloase Alstertal
Hotels
127|Beautyfully
128|Haus Sachsenwald
129|Hotel Alsterblick
130|Hotel Alsterlauf
131|Hotel Atlantic
132|Hotel Escador
133|Hotel Hagenbeck
134|Northern-Star-Hotel
135|Sarghotel X44
136|Stormarnhaus
137|Utopia Kleckerwald
138|Vier Jahreszeiten
Konzerne
139|Admiralitätskollegium
140|Eftherlink
141|Airbus Aerials
142|Alxon Pharma
143|AquaDyne
144|Ares Entertainment ADL
145|Bankhaus MM Warburg & Co.
146|Bacardi
147|Beiersdorf
148|Blohm+Voss-Zentrale
149|BuMoNA
150|ByDesign
151|Charisma Associates
152|DeMeKo-Hauptquartier
153|Deutsche Erdölgesellschaft (Raffinerie)
154|Deutsche Erdölgesellschaft (Zentrale)
155|Evo Synthtech
156|Federated-Boeing
157|Group Trans
158|Hamburger Bankengruppe
159|HanSec-Hauptquartier
160|Hapag-Lloyd
161|HAZMAT-Kommandoposten Wildost
162|HAZMAT-Zentrale
163|HHMC-Zentrale
164|HiFlyer
165|Holsten-Brauerei AG
166|HSV AG
167|KITT
168|Knight-Errant-Zentrale
169|KondOrchid
170|Krupp Chemical
171|Krupp Manufacturing
172|Krupp Manufacturing
173|Krüss-Eppendorf
174|Lone Star Deutschland
175|Lotus Multimedia
176|Lufthansa
177|Lusiada
178|Mærsk
179|MCT Music
180|MediaSim/Deutsche Sendeanstalten
181|Messerschmitt-Kawasaki-Werk
182|NABS
183|NDR
184|Pensodyne
185|Plank Hoch- und Tiefbau
186|PsiAid-Zentrale
187|Regency MegaMedia
188|Regulus Transport Services
189|Royal Dutch Shell
190|Saab
191|Schmalbach-Nutritions-Zentrale
192|SeaGate-Arkologie
193|Shiawase Envirotech
194|Shiawase Logistics
195|Shiawase Mediatech
196|Spinrad Media/Spinrad Public Relations
197|Stellingen Genetics
198|StoreYou-Firmenzentrale
199|Stuffer-Plus-Zentrale
200|Sunrise Getränke AG
201|Swarovski-Joop
202|TransLad
203|Ultimum (Wolkenstadt)
204|Unilever
205|Veitbrunn
206|VWS
207|WasserKraft
208|Wolverine Security
209|Wuxing Prosperity
210|Yamatetsu Naval Technologies
Restaurants
211|Bliny (Zentrale)
212|Chagall
213|Die Basis
214|Katzky Schmatzky
215|Linden-Kantine
216|Max Stirner
217|Old School
218|Pinkerton
219|Restaurant Warschau
220|Taco-Temple-Restaurant
221|Unsere Frau am Hafen
Sightseeing
222|Alter Elbtunnel
223|Altes Rathaus
224|Ateliermuseum
225|Botanischer Garten Flottbek
226|Dauerausstellung Hamburg 2011
227|Fischauktionshalle
228|Gewürz- und Kaffeemuseum
229|Heiligengeistfeld
230|Heinrich-Hertz-Turm
231|Kunstausstellung Jessendiek
232|Marinemuseum
233|Museum für Kunst und Gewerbe
234|Neue Deichtorhallen
235|Planetarium
236|Speicherstadtmuseum
237|Tanzende Türme
238|Völkerkundemuseum
239|Zollmuseum
Sonstige Spots
240|Ahrensburger See
241|Allermöher Sperrgebiet
242|Alter Hau
243|Anleger Sechs – Big Willi
244|Attraktor
245|Bahnhof Blankenese-Rissen
246|Bernhard-Nocht-Institut für Tropenmedizin
247|Billstedter Bahnhof
248|Bisam
249|Bishorster Hallig
250|Body Arts
251|Brunaburg
252|Bundeswehrkrankenhaus
253|Bürostadt
254|Dallmayr-Siedlung
255|DeMeKo-Akademie
256|Destille Bimber-8
257|Die Tábor
258|Eucadoria-III
259|Feenteich
260|Feuertempel des Ordens der Ewigen Wiederkehr
261|Gemeindezentrum Barmbek-Süd
262|Hamburger Cruise Center
263|HanSec-Einsatzzentrum Bergedorf
264|Haus des Agwe
265|Haus des Wegs der Reinheit
266|Helmut-Schmidt-Universität
267|Hof Haspunde
268|Institut iPHOS
269|Itzstedt Energie
270|Kahn
271|Kesselhaus
272|Kirche St. Jonas
273|Kläranlage 19S
274|Kolmbachs Hof
275|Konzernklinikum Eppendorf
276|Mago-Cluster
277|Mandelzirkel
278|Maskospytal
279|Media Cluster Nord
280|Messebereich Hagenbecks Tierpark
281|Muschelmarkt
282|Narkotika
283|Neue Messe Hamburg
284|Neuengamme
285|Neuer Rathausmarkt
286|Ölhafen
287|Paplanje
288|Pollhof
289|ProSEX-Zentrale
290|Regierungsviertel
291|Rikus Tierpräparation
292|S-Bahntrasse
293|Schule der Fünf Chakren
294|Schwarzer Garten
295|Thelem Svetovid Rotenbek
296|Thelem-Svetovid-Institut
297|Versteck der Bagalutni
298|Villa Loco
299|Wattburg
300|Wedeler Insel
301|Yoginis Ashram-Haus
302|Zawodom
303|Zentrales Krankenhaus Hamburg
304|Zuflucht des Wegs der Reinheit
Verkehr
305|Frachtflughafen Fuhlsbüttel
306|Haiou-Frachtterminal
307|Neue Landungsbrücken
308|Orbitalflughafen Kaltenkirchen
309|Werksflughafen Stade
"""


CATEGORY_SUMMARIES = {
    "Ausgehen": "ist in der offiziellen Karte als Ort des Hamburger Nacht- und Kulturlebens verzeichnet",
    "Bars und Kneipen": "ist in der offiziellen Karte als Bar, Kneipe oder Treffpunkt verzeichnet",
    "Einkaufen": "ist in der offiziellen Karte als Einkaufs- oder Versorgungspunkt verzeichnet",
    "Freizeit": "ist in der offiziellen Karte als Freizeit- oder Sportort verzeichnet",
    "Hotels": "ist in der offiziellen Karte als Unterkunft verzeichnet",
    "Konzerne": "ist in der offiziellen Karte als Konzernstandort verzeichnet",
    "Restaurants": "ist in der offiziellen Karte als Restaurant oder gastronomischer Treffpunkt verzeichnet",
    "Sightseeing": "ist in der offiziellen Karte als Sehenswürdigkeit oder Kulturort verzeichnet",
    "Sonstige Spots": "ist in der offiziellen Karte als besonderer Schauplatz verzeichnet",
    "Verkehr": "ist in der offiziellen Karte als Verkehrsknoten verzeichnet",
}


SECTION_RANGES = {
    "Neue Mitte": (3018, 3483),
    "Altona": (3484, 3804),
    "Eimsbüttel": (3805, 4253),
    "Nord": (4254, 4625),
    "Stade": (4626, 4828),
    "Harburg": (4829, 5185),
    "Bergedorf": (5186, 5461),
    "Lauenburg": (5462, 5677),
    "Stormarn": (5678, 5911),
    "Wandsbek": (5912, 6176),
    "Kaltenkirchen": (6177, 6403),
    "Pinneberg": (6404, 6591),
    "Hafen": (7430, 7803),
    "Big Willi": (7804, 8040),
    "Wildost": (8972, 10362),
}


EXPLICIT_SCOPES = {
    "Sachsenwald": "Lauenburg",
    "Haus Sachsenwald": "Lauenburg",
    "Wildost": "Wildost",
    "Eucadoria-III": "Deutsche Bucht",
    "Mittelplate-A": "Deutsche Bucht",
    "Itzehoer Mitternacht-Markt": "Norddeutscher Bund",
    "Bishorster Hallig": "Pinneberg",
    "Wedeler Insel": "Altona",
    "Anleger Sechs – Big Willi": "Big Willi",
}


WILDOST_SPOTS = [
    ("Doppel:U", "Turiport", "Freilicht-Disko, die nur an wenigen Tagen im Jahr geöffnet ist."),
    ("Glückspilz", "Turiport", "Spielhölle im touristischen Zugang Wildosts."),
    ("Grüschtsch", "Turiport", "Bordell im Bereich Turiport."),
    ("Baimaika", "Katschera", "Aus Frachtcontainern errichtete Kneipe."),
    ("Kontor", "Bartertown", "Bar und lokaler Treffpunkt."),
    ("Literaturcafé", "Kutschenka", "Auf einem Hausboot eingerichtetes Café."),
    ("Port Royal", "Bartertown", "Spelunke im Handelsbereich."),
    ("Postamt", "Turiport", "Lokal im Umfeld des Touristenhafens."),
    ("Wodny Bar", "Turiport", "Kneipe im wassergeprägten Turiport."),
    ("Aptekarka", "Turiport", "Apotheke und Versorgungspunkt."),
    ("Der Talismann", "Kutschenka", "Geschäft für magische und ungewöhnliche Waren."),
    ("Hurti-Kurti", "Bartertown", "Großes Warenlager und improvisiertes Kaufhaus."),
    ("Rohrbert", "Katschera", "Geschäft in Katschera."),
    ("Skrapjard", "Skrapland", "Werkstatt für große Motoren und schwere Technik."),
    ("Stefans Stotschnja", "Skrapland", "Kleine Bootswerkstatt."),
    ("Szabladin", "Skrapland", "Auf Klingen spezialisiertes Geschäft."),
    ("Zaba & Nurek", "Katschera", "Ausrüster für Taucher und Wasseroperationen."),
    ("Narko Nora", "Bartertown", "Drogenhöhle in einer umgestürzten Fähre."),
    ("Seaweed", "Turiport", "Drogenhöhle in Turiport."),
    ("HAZMAT-Kommandoposten Wildost", "Wildost", "Grenzstation und Aufnahmebereich der HAZMAT."),
    ("Katzky Schmatzky", "Kutschenka", "Restaurant in Kutschenka."),
    ("Versteck der Bagalutni", "Katschera", "Hafen und Rückzugsort der Bagalutni."),
    ("Bisam", "Bartertown", "Arzt und medizinische Anlaufstelle."),
    ("Destille Bimber-8", "Bartertown", "Illegale Destille."),
    ("Die Tábor", "Katschera", "Ehemalige Autofähre und Hauptquartier der Likedeeler."),
    ("Kesselhaus", "Kutschenka", "Zentrale Wasserversorgung des Teilraums."),
    ("Kirche St. Jonas", "Kutschenka", "Kirche und Gemeinschaftsort."),
    ("Maskospytal", "Kutschenka", "Als Klinik genutztes Schiff."),
    ("Paplanje", "Kutschenka", "Kleiner öffentlicher Platz."),
    ("S-Bahntrasse", "Wildost", "Alte Bahntrasse, die nur bei Niedrigwasser zuverlässig befahrbar ist."),
    ("Schronisko Melinovac", "Katschera", "Verborgenes U-Boot-Versteck."),
    ("Schwarzer Garten", "Bartertown", "Überwucherter toxischer Flecken im Slum."),
    ("Wattburg", "Skrapland", "Improvisierter Wohnkomplex."),
    ("Weideflächen Kutschenka", "Kutschenka", "Weideflächen für die lokale Viehhaltung."),
    ("Zawodom", "Skrapland", "Zweigeschossige Containerkaserne."),
    ("Zuflucht des Wegs der Reinheit", "Turiport", "Öffentliche Zuflucht der Sekte Weg der Reinheit."),
    ("Wildost-Zugbrücke", "Wildost", "Zugbrücke über den Schiffskanal und wichtiger lokaler Engpass."),
]


INNER_CITY_SPOTS = [
    ("Marriott Hotel", "Hotels"),
    ("Plaisir", "Restaurants"),
    ("Ami Feather", "Einkaufen"),
    ("Xanadu Computer", "Einkaufen"),
    ("Kaufhof", "Einkaufen"),
    ("Weapons World", "Einkaufen"),
    ("RheinGold", "Einkaufen"),
    ("Metro-Saturn", "Einkaufen"),
    ("Swarovski-Joop", "Einkaufen"),
    ("A Whole New You", "Medizin"),
    ("MetaType", "Einkaufen"),
    ("L’Oréal Beauty Shop", "Einkaufen"),
    ("Zauberland", "Einkaufen"),
    ("Carrefour", "Einkaufen"),
    ("BuMoNA-Apotheke", "Medizin"),
    ("Yellow Point", "Dienstleistungen"),
    ("Sodalitas Universalis Hamburgensis", "Magie und Religion"),
    ("Restaurant Dallmayr", "Restaurants"),
    ("Wok Tsingtau", "Restaurants"),
]


LEGACY_PLACES = [
    # SR1: directory entries and districts from the first German Hamburg
    # chapter.  SR2 republishes the same city material, so both buttons are
    # intentionally attached to the shared location.
    ("Kömstube Dammeyer", "Harburg", "Bars und Kneipen", "SR1", "dids-sr1", "Deutschland in den Schatten", "S. 81", "Gepflegte Harburger Gaststube und diskreter Treffpunkt für Politik und Konzernmanagement."),
    ("Cross", "Harburg", "Bars und Kneipen", "SR1", "dids-sr1", "Deutschland in den Schatten", "S. 81", "Treffpunkt der Harburger Halbwelt, in dem Konflikte schnell handgreiflich werden."),
    ("Tingel", "Harburg", "Ausgehen", "SR1", "dids-sr1", "Deutschland in den Schatten", "S. 81", "Unterhaltungszentrum mit Arenen, Gladiatorenkämpfen, Simulationen und Cyberspace-Massenszenarien."),
    ("Moser", "Harburg", "Bars und Kneipen", "SR1", "dids-sr1", "Deutschland in den Schatten", "S. 81", "Als Kaffeehaus entworfenes Kellergewölbe und etablierter Orktreffpunkt."),
    ("Star Motel", "Wildost", "Hotels", "SR1", "dids-sr1", "Deutschland in den Schatten", "S. 81", "Heruntergekommene Absteige und Treffpunkt von Hovercraftbesatzungen und Piraten."),
    ("Bel Tibor", "Wildost", "Bars und Kneipen", "SR1", "dids-sr1", "Deutschland in den Schatten", "S. 81", "Raue Spelunke in Neu-Wulmstorf, deren Stammgäste häufig Big-Willi-Erfahrung besitzen."),
    ("Freimarkt „An den Docks“", "Wildost", "Einkaufen", "SR1", "dids-sr1", "Deutschland in den Schatten", "S. 81", "Samstäglicher Schwarzmarkt für Diebesgut und Waren aus Wildost."),
    ("Magischer Baum", "Harburg", "Restaurants", "SR1", "dids-sr1", "Deutschland in den Schatten", "S. 82", "Elfen vorbehaltenes Restaurant mit angeschlossenem Musikclub in Buchholz."),
    ("Hannos Piesel", "Harburg", "Bars und Kneipen", "SR1", "dids-sr1", "Deutschland in den Schatten", "S. 82", "Treffpunkt von Konzernangestellten, Ingenieuren und Naturwissenschaftlern in Jesteburg."),
    ("Ökotreff Schwarze Berge", "Harburg", "Organisationen", "SR1", "dids-sr1", "Deutschland in den Schatten", "S. 82", "Ehemaliges Forsthaus und Treffpunkt der Grünen Zellen sowie unabhängiger Umweltaktivisten."),
    ("Die Zecke", "Neue Mitte", "Ausgehen", "SR1", "dids-sr1", "Deutschland in den Schatten", "S. 83", "Kabarett auf der Musikinsel und in seinem Quellenstand eines der besten Hamburgs."),
    ("Reaktor", "Neue Mitte", "Ausgehen", "SR1", "dids-sr1", "Deutschland in den Schatten", "S. 83", "Rockclub in einer halb zerstörten Halle der Musikinsel."),
    ("Addis Grotte", "Neue Mitte", "Bars und Kneipen", "SR1", "dids-sr1", "Deutschland in den Schatten", "S. 83", "Ausweichkneipe für Gäste, die an den exklusiveren Musikinsel-Clubs scheitern."),
    ("Klönschnack", "Neue Mitte", "Bars und Kneipen", "SR1", "dids-sr1", "Deutschland in den Schatten", "S. 83", "Extrem laute Musikbar auf der Musikinsel."),
    ("Nonnenkloster", "Neue Mitte", "Bars und Kneipen", "SR1", "dids-sr1", "Deutschland in den Schatten", "S. 83", "Verschwiegene Kneipe in der Rathausstadt mit überwiegend elfischem Publikum."),
    ("Flip Flop", "Neue Mitte", "Ausgehen", "SR1", "dids-sr1", "Deutschland in den Schatten", "S. 83", "Musikclub am Gänsemarkt für wohlhabende Jugendliche und deren Nachahmer."),
    ("Schlesinger’s", "Neue Mitte", "Restaurants", "SR1", "dids-sr1", "Deutschland in den Schatten", "S. 83", "Nobelrestaurant auf einem Schwimmponton am Jungfernstieg."),
    ("Tolstoi", "Neue Mitte", "Restaurants", "SR1", "dids-sr1", "Deutschland in den Schatten", "S. 83", "Günstiges russisches Fast Food und Treffpunkt der Tretboottaxifahrer."),
    ("Cazz", "Neue Mitte", "Bars und Kneipen", "SR1", "dids-sr1", "Deutschland in den Schatten", "S. 83", "Cyberjazz-Lokal für Intellektuelle, Kunstszene und Szenegänger."),
    ("Scharfe Ecke", "Neue Mitte", "Soziales", "SR1", "dids-sr1", "Deutschland in den Schatten", "S. 83–84", "Obdachlosenasyl im Schilinskifleet und Anlaufpunkt für Neuankömmlinge."),
    ("Astra-Eck", "Neue Mitte", "Bars und Kneipen", "SR1", "dids-sr1", "Deutschland in den Schatten", "S. 84", "Neonazi-Kneipe in St. Georg mit einschlägiger Ausstattung."),
    ("Provianthöhle", "Neue Mitte", "Restaurants", "SR1", "dids-sr1", "Deutschland in den Schatten", "S. 84", "Günstiger Imbiss am Hansaplatz und gelegentlicher Rekrutierungsort für Runs."),
    ("Simsalasinn", "Neue Mitte", "Ausgehen", "SR1", "dids-sr1", "Deutschland in den Schatten", "S. 84", "Verwinkelter Rockclub in St. Georg, der sich durch drei Gebäude zieht."),
    ("Störtebeker", "Neue Mitte", "Bars und Kneipen", "SR1", "dids-sr1", "Deutschland in den Schatten", "S. 84", "Anarcho- und Hoverpiratenkneipe mit Frühwarnsystem und zahlreichen Fluchtwegen."),
    ("Café Macke", "Neue Mitte", "Bars und Kneipen", "SR1", "dids-sr1", "Deutschland in den Schatten", "S. 86", "Ehemalige Anarchokneipe auf der Reeperbahn, inzwischen stark touristisch geprägt."),
    ("Sacramento", "Neue Mitte", "Ausgehen", "SR1", "dids-sr1", "Deutschland in den Schatten", "S. 86", "Teurer Sexclub und Bordell unter Yakuza-Einfluss."),
    ("Crazy Action", "Neue Mitte", "Ausgehen", "SR1", "dids-sr1", "Deutschland in den Schatten", "S. 86", "Exklusiver Nachtclub für vermögende Gäste und extreme Shows."),
    ("Zarackzackzack", "Altona", "Bars und Kneipen", "SR1", "dids-sr1", "Deutschland in den Schatten", "S. 86", "Gehobene Rockkneipe und hilfreicher Erstkontakt für ortsfremde Runner."),
    # SR3 additions.
    ("End of the World", "Bergedorf", "Bars und Kneipen", "SR3", "dids2-sr3", "Deutschland in den Schatten II", "Freizeit und Vergnügen", "Kaschemme am verseuchten Elbwasser, die Magiebegabte und lebensmüde Gäste mit gefährlichen Illusionen anzieht."),
    ("Positronik", "Eimsbüttel", "Bars und Kneipen", "SR3", "dids2-sr3", "Deutschland in den Schatten II", "Freizeit und Vergnügen", "Studentenkneipe am Grindel mit Live-Musik und Kontakten zur magischen Akademie."),
    ("Soerensen & Friedrichs", "Altona", "Restaurants", "SR3", "dids2-sr3", "Deutschland in den Schatten II", "Freizeit und Vergnügen", "Gepflegtes Blankeneser Abendlokal für Hamburgs obere Zehntausend."),
    ("Podgorni", "Altona", "Bars und Kneipen", "SR3", "dids2-sr3", "Deutschland in den Schatten II", "Freizeit und Vergnügen", "Osteuropäische Kneipe mit Wodka, Musik und sehr eigener Form der Gastfreundschaft."),
    ("Lloyd-Webber-Audiodrom", "Altona", "Ausgehen", "SR3", "dids2-sr3", "Deutschland in den Schatten II", "Freizeit und Vergnügen", "Großer Altonaer Kulturkomplex mit sieben Konzertsälen."),
    ("Rickmer Rickmers Schiffstheater", "Hafen", "Ausgehen", "SR3", "dids2-sr3", "Deutschland in den Schatten II", "Freizeit und Vergnügen", "Schiffstheater im Hamburger Museumshafen."),
    ("Stader Institut für Parabiologie und -agronomie", "Stade", "Wissenschaft und Medizin", "SR3", "dids2-sr3", "Deutschland in den Schatten II", "Stade", "Von der AG Chemie unterstützte Forschungseinrichtung zur Revitalisierung verseuchter Marschgebiete."),
    # SR4 additions not present as separate numbers on the 2070er/2080er map.
    ("Dockers Club", "Hafen", "Ausgehen", "SR4", "schattenstaedte-sr4", "Schattenstädte", "Bars und Nachtclubs", "Industrieller Hafenclub für Straßenpublikum, Hafenarbeiter, Nachwuchsbands und Kontakte zu Harburger Gangs."),
    ("Kaiserkeller", "Neue Mitte", "Ausgehen", "SR4", "schattenstaedte-sr4", "Schattenstädte", "Große Freiheit 36", "Alternativer Clubbereich der Großen Freiheit 36 mit abgeschirmten VIP-Zonen."),
    ("Sea Cloud", "Neue Mitte", "Ausgehen", "SR4", "schattenstaedte-sr4", "Schattenstädte", "Hotel Atlantic", "Szeneclub im Hotel Atlantic."),
    ("Landhaus Scherrer", "Lauenburg", "Restaurants", "SR4", "schattenstaedte-sr4", "Schattenstädte", "Restaurants & Hotels", "Streng gesichertes Luxusrestaurant für Senat, Konzernelite und diskrete Gespräche."),
    ("Carla’s Damenwelt", "Nord", "Einkaufen", "SR4", "schattenstaedte-sr4", "Schattenstädte", "Alsterpalast", "Modegeschäft im Alsterpalast."),
    ("Der Container", "Hafen", "Ausgehen", "SR4", "schattenstaedte-sr4", "Schattenstädte", "Pit Fighting", "Ortswechselnde Pit-Fight-Veranstaltung auf entladenen Frachtern."),
    ("Chrome", "Neue Mitte", "Medizin", "SR4", "schattenstaedte-sr4", "Schattenstädte", "Cyber-Underground", "Design-Cyberware, Gliedmaßentuning und extremes Bodymodding mit Einbau vor Ort."),
    ("Krähennest", "Hamburg", "Matrix und Metaplanes", "SR4", "schattenstaedte-sr4", "Schattenstädte", "Virtuelle Orte", "Virtueller Piratenschiff-Treffpunkt der Hamburger Hackerszene und Nachfolger der Altona 7."),
    ("Narkow-Liste", "Hamburg", "Matrix und Metaplanes", "SR4", "schattenstaedte-sr4", "Schattenstädte", "Virtuelle Orte", "Verdeckte Matrix-Kopfgeldliste für Zielpersonen in Hamburg und darüber hinaus."),
    ("Billstedter Markt", "Neue Mitte", "Einkaufen", "SR4", "schattenstaedte-sr4", "Schattenstädte", "Schattenmärkte", "Zweimal monatlich betriebener neutraler Schwarzmarkt in den Tunneln unter dem Billstedter Bahnhof."),
    ("Fischmarkt", "Neue Mitte", "Einkaufen", "SR3", "dids2-sr3", "Deutschland in den Schatten II", "Innenstadt", "Traditionsmarkt an den Landungsbrücken und frühmorgendlicher Treffpunkt für Hehler, Schmidts und Piratenkontakte."),
    ("Senatsadministration", "Wandsbek", "Politik und Verwaltung", "SR4", "schattenstaedte-sr4", "Schattenstädte", "Öffentliche Einrichtungen", "Modernes, besonders gesichertes Verwaltungsgebäude des Hamburger Senats."),
    ("Hafenstraße", "Neue Mitte", "Stadtteile", "SR1", "dids-sr1", "Deutschland in den Schatten", "S. 85", "Abgeriegelte neoanarchistische Hochburg nahe St. Pauli mit schwer bewaffneten Bewohnern und verdeckten Zugängen."),
    ("St. Georg", "Neue Mitte", "Stadtteile", "SR3", "dids2-sr3", "Deutschland in den Schatten II", "Innenstadt", "Armer, metamenschlich und osteuropäisch geprägter Stadtteil mit Waffen-, BTL- und Taliskrämerhandel."),
    ("St. Pauli", "Neue Mitte", "Stadtteile", "SR3", "dids2-sr3", "Deutschland in den Schatten II", "Innenstadt", "Hamburgs Kiez und größter Nachtleben-, Rotlicht- und Unterweltschwerpunkt."),
    ("Neugraben und Neu Wulmstorf", "Wildost", "Stadtteile", "SR3", "dids2-sr3", "Deutschland in den Schatten II", "Ausgewählte Stadtteile", "Flutgeschädigter Süderelberaum mit Pontonsiedlungen, Piratenhäfen und dem historischen Kern von Wildost."),
    ("Sardinenstadt / City Nord", "Nord", "Stadtteile", "SR3", "dids2-sr3", "Deutschland in den Schatten II", "City Nord", "Dicht gepackte und weiträumig kontrollierte Konzernbürostadt; im SR5-Stand vollständig exterritorial."),
    ("Ohlsdorfer Friedhof", "Nord", "Magie und Gefahren", "SR3", "dids2-sr3", "Deutschland in den Schatten II", "Ohlsdorf", "Größter Parkfriedhof der Welt, Ghulgebiet und ausgedehnter unterirdischer Gefahrenraum."),
]


DEUTSCHE_BUCHT_SPOTS = [
    ("Helgoland", [7.8850, 54.1825], "Freier und strategisch bedeutender Inselstandort in der Deutschen Bucht."),
    ("Mittelplate-A", [8.7290, 54.0250], "Raffinerieplattform der AG Chemie und häufiges Ziel von Piraten und GreenWar."),
    ("Cuxhaven", [8.6940, 53.8610], "Küsten- und Hafenort am Ausgang der Elbe."),
    ("Wilhelmshaven", [8.1070, 53.5290], "Großer Marine- und Hafenstandort an der Deutschen Bucht."),
    ("Bremerhaven", [8.5800, 53.5390], "Hafenstadt und logistischer Knoten an der Wesermündung."),
    ("Emden", [7.2060, 53.3670], "Westlicher Hafenstandort am Rand der Deutschen Bucht."),
    ("Borkum", [6.6690, 53.5880], "Bewohnte ostfriesische Insel und Küstenbezugspunkt."),
    ("Juist", [7.0060, 53.6780], "Ostfriesische Insel im toxisch veränderten Wattenmeer."),
    ("Utersum", [8.4050, 54.7150], "Nördlicher Küstenort auf Föhr."),
    ("Brunsbüttel", [9.1340, 53.8950], "Hafen- und Schleusenort am Nord-Ostsee-Kanal."),
    ("Brokdorf", [9.3230, 53.8640], "Küstenstandort nordwestlich Hamburgs."),
    ("Itzehoe", [9.5170, 53.9250], "Piratenfreundlicher Hafen- und Werkstattstandort im Norddeutschen Bund."),
    ("Heide", [9.0950, 54.1960], "Küstennaher Hafen- und Versorgungsraum, den Piraten nur mit Vorsicht anlaufen."),
]


GANGS = [
    ("Fährleute", "Bergedorf", "Wassergang am Zollspiekerdeich und in den südöstlichen Elbräumen."),
    ("Hyänen", "Bergedorf", "Bikergang zwischen Bergedorf und Freihafen."),
    ("Kreeper", "Bergedorf", "Drogengang in Neuallermöhe."),
    ("Creatures", "Lauenburg", "Psycho-Punk-Gang im westlichen Lauenburg."),
    ("Oravs", "Kaltenkirchen", "Bikergang im Raum Norderstedt."),
    ("Alsterhaie", "Neue Mitte", "Orkgang im Stadtteil St. Georg."),
    ("Nice Guys", "Neue Mitte", "Thrillgang in der Neuen HafenCity."),
    ("Wasserratten", "Neue Mitte", "Jetski-Gang in den Kanälen zwischen Neuer Mitte und Hafen."),
    ("Desperado MC", "Stade", "Motorradclub und Straßenmacht in Stade."),
    ("Sons of Odin MC", "Stade", "Motorradclub im Bezirk Stade."),
    ("Horde", "Wandsbek", "Ork- und Trollgang im Groß-Bramfelder Ghetto."),
    ("Silverblades", "Altona", "Go-Gang im Raum Lurup."),
    ("Locas", "Altona", "Motorradgang in Osdorf."),
    ("Vier Nägel", "Pinneberg", "Gang in den nördlichen äußeren Gebieten Pinnebergs."),
    ("Black Pearls", "Pinneberg", "Gang in den westlichen äußeren Gebieten Pinnebergs."),
    ("Willis", "Harburg", "Gang ehemaliger Big-Willi-Häftlinge im Harburger Zentrum."),
    ("Abarotni", "Harburg", "Vory-nahe Vollstreckergang um den Blauen Klotz."),
    ("Hel-Rider", "Neue Mitte", "Viking-Gang auf dem Kiez."),
    ("Speeddolls", "Harburg", "Weibliche Fahrzeug- und Straßengang in Harburg."),
    ("Mad Aces", "Neue Mitte", "Likedeeler-nahe Gang auf dem Kiez."),
    ("Saman", "Altona", "Ethno-Gang im Altonaer Viertel."),
]


PEOPLE = [
    ("Myriam Hergeim alias Ceridwen", "Toxische Druidin und Schmidt", "GreenWar", "Big Willi", "Myriam Hergeim gehört zur höheren Führung von GreenWar. Nach ihrer Haft in Big Willi und dem Ausbruch während des Crashs 2.0 vermittelt sie in den 2080ern Operationen gegen Konzerne, Politik und den Weg der Reinheit."),
    ("Anna „Krysha“ Savochkina", "Lideri der Weißen Vory", "Lobatchevski-Vory", "Harburg", "Savochkina ist der verlängerte Arm des Avtoritet in Harburg, eine eiskalte Planerin mit sehr guten Verbindungen in die Hamburger Schatten."),
    ("Ulrike „Sermon“ Köhler", "Deckerin und Sysop", "Umbra-Cloud", "Hamburg", "Sermon ist eine erfahrene Deckerin und Tochter des Sandmanns. Sie arbeitet als Sysop der Umbra-Cloud und ist tief in Hamburgs Matrix- und Schattenszene vernetzt."),
    ("Snow-WT", "Technomancerin und Journalistin", "Hamburger Schattenszene", "Hamburg", "Snow-WT verbindet journalistische Recherche mit Technomancerfähigkeiten und verfolgt auch gefährliche Themen wie Tamanous-Verbindungen und Konzernintrigen."),
    ("Verena „Undine“ Glaser", "Hooderin und Wasserkämpferin", "Klabauterbund", "Stade", "Die orkische Hooderin Undine stammt aus einem verseuchten Arbeiterumfeld und gehört zur pragmatischen Fraktion des Klabauterbunds."),
    ("Warentester alias Klaas", "Chef der Likedeeler", "Likedeeler", "Die Tábor", "Der frühere Runner Warentester führt als Klaas die Hamburger Likedeeler und verbindet spektakuläre Einbruchserfahrung mit dem Schmuggelnetz der Waterkant."),
    ("Pater Michael", "Priester und Kampfsportlehrer", "Kirche St. Jonas", "Kirche St. Jonas", "Pater Michael ist eine prägende Vertrauensperson Wildosts. Er wirkt als Priester, Lehrer und Vermittler im Umfeld der Kirche St. Jonas."),
    ("Alien Queen", "Ikone des Cyber-Undergrounds", "Empire", "Empire", "Die Alien Queen ist eine legendäre Cyberfetischistin und Herrscherfigur der Hamburger Cyberszene; ihr Club Empire bleibt ihr wichtigster öffentlicher Bezugspunkt."),
    ("Lasse Petrovic", "Flottillenadmiral und HAZMAT-Kommandeur", "HAZMAT", "HAZMAT-Zentrale", "Petrovic ist der erfahrene militärische Kommandeur der Hamburger Zoll- und Marine-Schutztruppe HAZMAT."),
    ("Vesna Lyzhichko", "Bürgermeisterin und politische Führung", "Hamburger Senat", "Regierungsviertel", "Lyzhichko prägt die offizielle Hamburger Politik und besitzt als Bürgermeisterin nominellen Einfluss auf Senat und HAZMAT."),
    ("Anja Kahn", "Hamburger Politikerin", "Hamburger Bürgerschaft", "Regierungsviertel", "Anja Kahn gehört zu den in Datapuls Hamburg hervorgehobenen Akteurinnen der Hamburger Politik."),
    ("Laura Kowalski", "Wirtin und Schattenkontakt", "Sebastian Falk", "Sebastian Falk", "Die orkische Besitzerin des Sebastian Falk gilt als neutral, verschwiegen und als verlässliche Kontaktperson außerhalb der Likedeeler-Netze."),
    ("Jochen Hastenbruch", "Taliskrämer", "Hermetikum", "Hermetikum", "Der zwergische Betreiber des Hermetikums versorgt das Mago-Cluster und handelt neben Lehrmaterial auch mit Waren aus der juristischen Grauzone."),
    ("Abrahm Blomquist", "Unterweltunternehmer", "Glücksschwein", "Lauenburg", "Der finnische Zwerg führt eine verborgene Schweinefleischmafia und verdient an Ausbeutung, Buchfälschung, Fördermittelbetrug und erzwungenen Hofverträgen."),
    ("Glöckchen", "Freier Geist und Schmidt", "Hamburger Schatten", "Lauenburg", "Glöckchen ist ein freier Geist und einer der härteren Hamburger Schmidts; launisch, wohlhabend und für mehrere parallel eingesetzte Teams bekannt."),
    ("Janna Oolstedt", "Sozialsenatorin", "Hamburger Senat", "Lauenburg", "Oolstedt ist Hamburgs grüne Sozialsenatorin und lebt im Bezirk Lauenburg."),
    ("Mister Ming", "Lokaler Machtspieler", "Lauenburger Schatten", "Lauenburg", "Der als Mister Ming bekannte Akteur gehört zu den wichtigen Machtspielern Lauenburgs."),
    ("Mutter Gans", "Lokale Machtspielerin", "Lauenburger Szene", "Lauenburg", "Mutter Gans ist eine langjährig etablierte Machtfigur im ländlichen Hamburger Osten."),
    ("Thomas Darboven", "Vertreter alter Hamburger Familien", "Hanseatische Eliten", "Neue Mitte", "Darboven spricht für die traditionsbewussten alten Hamburger Familien und ihre Abgrenzung gegenüber jüngeren Machtgruppen."),
    ("Dewuschka", "Leitfigur Wildosts", "Wildost", "Wildost", "Dewuschka tritt als politische und gesellschaftliche Leitfigur des Wildoster Slums auf."),
    ("Jasmin Ibrahimoglu", "Geschäftsführerin", "HHMC", "HHMC-Zentrale", "Ibrahimoglu führt das Hamburg Harbour Management Center und damit einen zentralen Teil der Hafenlogistik."),
    ("Dr. Anneliese Sadowia", "Geschäftsführerin", "HanSec", "HanSec-Hauptquartier", "Sadowia ist Geschäftsführerin der HanSec und eine zentrale Figur des privatisierten Hamburger Sicherheitsapparats."),
]


SR6_PIRATES = [
    ("Hundshaie", "Piratencrew", "Störtebekers Erben", "Deutsche Bucht", "Kleine, schnelle Kapercrew auf der Skaad, die gezielte Überfälle in Küstennähe durchführt."),
    ("Kapitän Gebert", "Pirat und Kapitän", "Hundshaie", "Deutsche Bucht", "Gebert führt die Hundshaie und ihr umgebautes Schnellboot Skaad."),
    ("Schwarzes Blut", "Hoverpiratencrew", "Deutsche Bucht", "Deutsche Bucht", "Hoverpiratencrew, die ein gleichnamiges Fahrzeug für schnelle Überfälle im Watt einsetzt."),
    ("Rote Korsaren", "Piratenverband", "Proteus-nahe Operationen", "Deutsche Bucht", "Größere Piratengruppe, deren Entwicklung eng mit Kapitän Caligula und den Machtspielen auf der Doggerbank verbunden ist."),
    ("Kapitän Caligula", "Piratenkapitän", "Rote Korsaren", "Deutsche Bucht", "Caligula führt die Roten Korsaren mit impulsiver Härte und ausgeprägtem Gespür für Intrigen."),
    ("Rift Four", "Piratenhafen und Crewnetz", "Doggerbank", "Deutsche Bucht", "Aufgegebene Bohrinsel und befestigter Hafen mehrerer Crews am Nordrand der Doggerbank."),
    ("Neu-Gotland", "Piratennation", "Doggerbank", "Deutsche Bucht", "Freier Piratenhafen auf einer umbenannten Bohrinsel, der in einem pragmatischen Verhältnis zu Proteus steht."),
]


ADDITIONAL_PEOPLE = [
    ("Victor Lobatchevski", "SR4", "schattenstaedte-sr4", "Schattenstädte", "Lobatchevski-Syndikat", "Unterweltboss", "Lobatchevski-Syndikat", "Dollhouse", "Victor Lobatchevski ist eine Schlüsselfigur der Hamburger Vory und nutzt unter anderem das Dollhouse für Kontakte und Auftragsvergaben."),
    ("Carmen Vialetti", "SR4", "schattenstaedte-sr4", "Schattenstädte", "Medien und DeMeKo", "Star-Paparazza", "DeMeKo", "Große Freiheit 36", "Vialetti ist eine der bekanntesten Hamburger Medienjägerinnen und regelmäßiger Gast an prominenten Kiezschauplätzen."),
    ("Mahmut Amir", "SR4", "schattenstaedte-sr4", "Schattenstädte", "Große Freiheit 36", "Clubbesitzer", "Große Freiheit 36", "Große Freiheit 36", "Amir kaufte und erweiterte die Große Freiheit 36 und unterhält umstrittene Verbindungen nach Nordafrika."),
    ("Manuel Amitrang Achari", "SR4", "schattenstaedte-sr4", "Schattenstädte", "Hamburger Unterwelt", "Unterweltakteur", "Hamburger Unterwelt", "Neue Mitte", "Achari wird im Hamburger Unterweltkapitel als lokaler Machtspieler geführt."),
    ("Jürgen Brochewski", "SR4", "schattenstaedte-sr4", "Schattenstädte", "Harburg-Ghetto", "Vory-Akteur", "Vory", "Harburg", "Brochewski gehört zu den hervorgehobenen Vory-Akteuren im Harburger Ghetto."),
    ("Maksim Krylow", "SR4", "schattenstaedte-sr4", "Schattenstädte", "Harburg-Ghetto", "Vory-Akteur", "Vory", "Harburg", "Krylow gehört zu den hervorgehobenen Vory-Akteuren im Harburger Ghetto."),
    ("Wernher Julius Davids", "SR4", "schattenstaedte-sr4", "Schattenstädte", "Nordseegold", "Konzern- und Medienakteur", "Hamburger Wirtschaft", "Hamburg", "Davids ist eine in Schattenstädte hervorgehobene Figur der Hamburger Konzern- und Medienlandschaft."),
    ("Robert Keulen", "SR4", "schattenstaedte-sr4", "Schattenstädte", "Body Arts", "Bodymod-Künstler", "Body Arts", "Body Arts", "Keulen und seine Crew führen professionelle kosmetische und extreme Körpermodifikationen durch."),
    ("Kökinsei", "SR4", "schattenstaedte-sr4", "Schattenstädte", "Der Kahn", "Cyberdoc", "Der Kahn", "Kahn", "Kökinsei leitet die illegale Schattenklinik auf dem ehemaligen Luxusliner Ganesha."),
    ("Jannek Fat", "SR4", "schattenstaedte-sr4", "Schattenstädte", "Sugarbabe Club", "Clubbesitzer und Vermittler", "Sugarbabe Club", "Sugarbabe Club", "Fat nutzt den Sugarbabe Club als Vermittlungsstelle für illegale Geschäfte nach Mittel- und Ostasien."),
    ("Franek Kranz", "SR4", "schattenstaedte-sr4", "Schattenstädte", "Blauer Klotz", "Schwarzmarkthändler", "Likedeeler-Kontakte", "Blauer Klotz", "Kranz beschafft im Blauen Klotz ein ungewöhnlich breites Spektrum legaler und illegaler Waren."),
    ("Donna Francisca", "SR4", "schattenstaedte-sr4", "Schattenstädte", "Blauer Klotz", "Taliskrämerin", "Harburger Magieszene", "Blauer Klotz", "Donna Francisca betreibt im Blauen Klotz einen Taliskrämerladen und verfügt über Geisterkontakte."),
    ("Madame Heloise", "SR4", "schattenstaedte-sr4", "Schattenstädte", "Cirque Heloise", "Magische Schieberin", "Cirque Heloise", "Cirque Heloise", "Heloise führt den arkanen Zirkus und vermittelt magische Dienste an Hamburgs Straßenhexen und Schatten."),
    ("Mattis Berger", "SR3", "dids2-sr3", "Deutschland in den Schatten II", "End of the World", "Wirt und Illusionsmagier", "End of the World", "End of the World", "Berger würzt den Betrieb seiner Kaschemme mit gefährlich wirkenden Illusionen und echter Risikobereitschaft."),
    ("Sylvia Perkuhn", "SR3", "dids2-sr3", "Deutschland in den Schatten II", "Max Stirner", "Wirtin und Anarchokontakt", "Max Stirner", "Max Stirner", "Perkuhn betreibt das Max Stirner und kann Kontakte zu politisch aktiven Anarchisten vermitteln."),
    ("Carlo „Finger“ Patschke", "SR1", "dids-sr1", "Deutschland in den Schatten", "Sacramento, S. 86", "Clubpächter", "Yakuza-Umfeld", "Sacramento", "Patschke führt den Sexclub Sacramento und gilt im frühen Quellenstand als Yakuza-Mann."),
    ("Nadina Uschkow", "SR1", "dids-sr1", "Deutschland in den Schatten", "Star Motel, S. 81", "Motelbesitzerin und Piratenkontakt", "Hoverpiraten", "Star Motel", "Uschkow betreibt das Star Motel und besitzt erstklassige Verbindungen zu Hovercraftpiraten."),
    ("Sergius Hergeim", "SR1", "dids-sr1", "Deutschland in den Schatten", "Hamburger Chronik", "Druide und Umweltaktivist", "GreenWar-Vorgeschichte", "Hamburg", "Sergius Hergeim gehört zu den frühen prägenden Figuren des Hamburger radikalen Umweltmilieus."),
]


ORGANISATIONS = [
    ("Lobatchevski-Syndikat", "Organisiertes Verbrechen", "Harburg", "Russisch geprägtes Vory-Syndikat mit starken Positionen in Harburg, Drogenhandel, Sexgeschäft und Schmuggel."),
    ("Likedeeler", "Piraten- und Schmugglerbund", "Die Tábor", "Hamburger Schmuggler- und Piratenorganisation unter Warentester/Klaas mit weitreichenden Hafen- und Schattenkontakten."),
    ("Hamburg-Syndykat", "Polnisches Unterweltnetz", "Restaurant Warschau", "Von der Familie Olzewski geführtes Netzwerk mit Verbindungen zu lokalen polnischen Syndykats."),
    ("Hamburger Triaden", "Triadenverbund", "Hafen", "Mehrere chinesische Unterweltgruppen konkurrieren in Hafen, Glücksspiel, Schmuggel und Matrix um Einfluss."),
    ("Niederländische Penosen", "Unterweltnetz", "Hafen", "Niederländisch geprägte kriminelle Netzwerke mit Handels- und Schmuggelbezug zur Waterkant."),
    ("Russische Brüder", "Unterweltgruppe", "Harburg", "Weitere russische Unterweltakteure neben den dominierenden Vory-Strukturen."),
    ("Ältermänner", "Schattenregierung", "Hamburg", "Traditionsreiche, informelle Machtstruktur alter Hamburger Familien und Interessen."),
    ("Klabauterbund", "Ökoaktivisten und Hoverpiraten", "Stade", "Militante ökologische und maritime Organisation mit Stützpunkten im Süderelberaum und Aktionen gegen Hafen und Industrie."),
    ("Grüne Zellen", "Militante Umweltgruppe", "Harburg", "Dezentrale Umweltaktivisten mit Rückzugsräumen in den Harburger Bergen und Angriffszielen in Industriebezirken."),
    ("GreenWar", "Ökoterrororganisation", "Stade", "International operierende, gewaltbereite Ökoterrororganisation mit historisch starken Hamburger Bezügen."),
    ("Ahab", "Radikale Umweltfraktion", "Deutsche Bucht", "Maritime radikale Umweltfraktion mit Fokus auf Konzerne und toxische Nordseeaktivitäten."),
    ("Weg der Reinheit", "Sekte", "Wildost", "In Wildost aktive Reinheitssekte mit öffentlichen Zufluchten und eigener Infrastruktur."),
    ("Medusa", "Geheimorganisation", "Hamburg", "Verschwiegene Hamburger Fraktion mit eigenen Mitgliedern und verdeckten Zielen."),
    ("Mandelzirkel", "Voodoo-Gemeinde", "Mandelzirkel", "Altonaer Voodoo-Gemeinde mit Gemeinschaftshaus, Taliskrämer und diskreter medizinischer Versorgung."),
    ("Störtebekers Erben", "Piratenverbund", "Wildost", "Norddeutscher Piratenverbund mit historischen Wurzeln, Küstenbasen und spezialisierten Kapercrews."),
    ("Altona 7", "Matrixgang", "Krähennest", "Legendäre Hamburger Matrixgang; ihre Überlebenden werden mit dem Krähennest verbunden."),
    ("ARAbauken", "Matrixgang", "Eimsbüttel", "Matrixgang im Umfeld des Hamburger Unterhaltungs- und Mediengitters."),
    ("SPAMster", "Matrixgang", "Hamburg", "Matrixgang, die mit Spam, Loop-Strukturen und digitalem Vandalismus arbeitet."),
    ("Chinese Computer Connection", "Triaden-Matrixgang", "Hamburg", "Kleine, triadennahe Matrixgang mit toxischem Drei-C-Symbol."),
]


def normalized(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii").casefold()
    return re.sub(r"[^a-z0-9]+", "", value)


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8", errors="ignore").splitlines() if path.exists() else []


DP_LINES = read_lines(DATAPULS)
DP_SECTIONS = {
    scope: "\n".join(DP_LINES[start - 1 : end])
    for scope, (start, end) in SECTION_RANGES.items()
}
EDITION_TEXTS = [
    ("SR1", "dids-sr1", "Deutschland in den Schatten", SR1_HAMBURG, "Hamburg-Kapitel"),
    ("SR2", "dids-sr2", "Deutschland in den Schatten", SR2_HAMBURG, "Hamburg-Kapitel"),
    ("SR3", "dids2-sr3", "Deutschland in den Schatten II", SR3_HAMBURG, "Freistadt Hamburg"),
    ("SR4", "schattenstaedte-sr4", "Schattenstädte", SR4_HAMBURG, "Hamburg-Kapitel"),
    ("SR6", "hamburg-guide-sr6", "Hamburg – Venedig des Nordens", SR6_HAMBURG, "Reiseführer"),
]
EDITION_SECTION_RANGES = {
    # Restrict automatic cross-edition matches to the actual Hamburg
    # chapters.  Several source files contain the complete ADL or multiple
    # cities, where short venue names would otherwise create false matches.
    "SR1": (9600, 12426),
    "SR2": (8155, 10242),
    "SR3": (3882, 5060),
    "SR4": (14269, 19979),
}


def edition_source_text(edition: str, path: Path) -> str:
    section = EDITION_SECTION_RANGES.get(edition)
    if not section:
        return path.read_text(encoding="utf-8", errors="ignore")
    start, end = section
    return "\n".join(read_lines(path)[start - 1 : end])


NORMALIZED_EDITION_TEXTS = {
    edition: normalized(edition_source_text(edition, path))
    for edition, _, _, path, _ in EDITION_TEXTS
    if path.exists()
}


def parse_map_legend() -> list[tuple[int, str, str]]:
    category = ""
    result = []
    for raw in MAP_LEGEND.strip().splitlines():
        line = raw.strip()
        if "|" not in line:
            category = line
            continue
        number, name = line.split("|", 1)
        result.append((int(number), name.strip(), category))
    return result


def scope_for(name: str) -> str:
    if name in EXPLICIT_SCOPES:
        return EXPLICIT_SCOPES[name]
    needle = normalized(name)
    matches = [
        scope
        for scope, text in DP_SECTIONS.items()
        if needle and needle in normalized(text)
    ]
    if matches:
        # Specific district chapters precede the general Hafen/Wildost dossiers.
        return matches[0]
    low = name.casefold()
    fallback = [
        (("hafen", "landungsbrücken", "werft", "maersk", "mærsk", "hapag", "blohm"), "Hafen"),
        (("alster", "barmbek", "eppendorf", "mundsburg", "stadtpark", "fuhlsbüttel"), "Nord"),
        (("harburg", "russ", "bliny", "stalingrad"), "Harburg"),
        (("pinneberg", "klär", "westr", "watt"), "Pinneberg"),
        (("stade", "ölhafen"), "Stade"),
        (("kaltenkirchen", "lufthansa"), "Kaltenkirchen"),
        (("wandsbek", "bramfeld", "rathaus", "bundeswehr"), "Wandsbek"),
        (("bergedorf", "allermöh", "pollhof", "neuengamme"), "Bergedorf"),
        (("de meko", "demeko", "hagenbeck", "eims"), "Eimsbüttel"),
        (("altona", "blankenese", "bahrenfeld", "osdorf", "wedel"), "Altona"),
    ]
    for needles, scope in fallback:
        if any(needle in low for needle in needles):
            return scope
    return "Hamburg"


def map_summary(name: str, category: str, scope: str, number: int) -> str:
    core = CATEGORY_SUMMARIES[category]
    return f"{name} {core}. Der Ort trägt in der Gesamtübersicht die Nummer {number} und ist dem Bereich {scope} zugeordnet."


def edition_mentions(name: str) -> list[tuple[str, str, str, str]]:
    """Return older/newer core chapters that explicitly contain the name."""
    result = []
    needle = normalized(name)
    if len(needle) < 4:
        return result
    for edition, book_id, title, _, citation in EDITION_TEXTS:
        if needle in NORMALIZED_EDITION_TEXTS.get(edition, ""):
            result.append((edition, book_id, title, citation))
    return result


def add_main_map(catalogue: CityCatalogue) -> dict[int, int]:
    marker_ids: dict[int, int] = {}
    for number, name, category in parse_map_legend():
        scope = scope_for(name)
        anchor = ANCHORS.get(scope, ANCHORS["Hamburg"])
        scale = 0.07 if scope != "Hamburg" else 0.24
        coords = jitter(anchor, f"hamburg-main-map:{number}:{name}", scale=scale)
        catalogue.add_place(
            name,
            scope,
            "SR5",
            "hamburg-map-sr5",
            "Hamburgpaket – Karte",
            f"Kartenlegende Nr. {number}",
            category=category,
            summary=map_summary(name, category, scope, number),
            coordinates=coords,
            map_number=number,
        )
        marker_ids[number] = catalogue.places[name_key(name)]["properties"]["id"]
        for edition, book_id, title, citation in edition_mentions(name):
            if edition == "SR5":
                continue
            catalogue.add_place(name, scope, edition, book_id, title, citation)
    return marker_ids


def add_districts(catalogue: CityCatalogue) -> None:
    for name, summary, citation in DISTRICTS:
        catalogue.add_district_version(
            name,
            "SR5",
            "datapuls-hamburg-sr5",
            "Datapuls: Hamburg",
            citation,
            summary,
        )
        for edition, book_id, title, old_citation in edition_mentions(name):
            if edition == "SR5":
                continue
            catalogue.add_place(name, name, edition, book_id, title, old_citation)
        # Die weiße Bezirksbeschriftung und die Grenzfläche sind die
        # Interaktionselemente; ein zusätzlicher Punktmarker wäre redundant.
        catalogue.places[name_key(name)]["properties"]["map_marker"] = False
    for name, summary, citation in [
        (
            "Wildost",
            "Wildost ist Deutschlands größter Slum: ein wasser- und schlickdurchzogenes Labyrinth aus Wracks, Pontons, Containern und improvisierten Siedlungen. Der Teilraum beherbergt Schmuggler, Piraten, Flüchtige und eine eigenständige Viertelmillionenstadt ohne anerkannte Rechte.",
            "Datapuls: Hamburg, S. 89–103",
        ),
        (
            "Sachsenwald",
            "Der Sachsenwald ist Hamburgs größtes zusammenhängendes Wald- und Magiegebiet. Ökoschamanische Gruppen, erwachte Natur, Aussteiger, Konzernausflügler und verdeckte Operationen teilen sich den schwer kontrollierbaren Raum.",
            "Datapuls: Hamburg, S. 65–70",
        ),
    ]:
        catalogue.add_place(
            name,
            name,
            "SR5",
            "datapuls-hamburg-sr5",
            "Datapuls: Hamburg",
            citation,
            category="Umlandgebiete",
            summary=summary,
            coordinates=[ANCHORS[name][1], ANCHORS[name][0]],
        )


def add_detail_maps(catalogue: CityCatalogue) -> tuple[list[int], list[int]]:
    wildost_ids = []
    for name, subarea, summary in WILDOST_SPOTS:
        scope = "Wildost"
        coords = jitter(ANCHORS["Wildost"], f"wildost:{subarea}:{name}", scale=0.035)
        catalogue.add_place(
            name,
            scope,
            "SR5",
            "hamburg-detail-maps-sr5",
            "Hamburgpaket – Karten und Karteikarten",
            "Hamburgpaket – Wildost/Neue Mitte, Detaillegende",
            category=None,
            summary=f"{name} liegt im Wildoster Teilraum {subarea}. {summary}",
            coordinates=coords,
        )
        wildost_ids.append(catalogue.places[name_key(name)]["properties"]["id"])

    inner_ids = []
    for letter, (name, category) in zip("ABCDEFGHIJKLMNOPQRS", INNER_CITY_SPOTS):
        coords = jitter(ANCHORS["Neue Mitte"], f"innenstadt:{letter}:{name}", scale=0.025)
        catalogue.add_place(
            name,
            "Neue Mitte",
            "SR5",
            "hamburg-detail-maps-sr5",
            "Hamburgpaket – Karten und Karteikarten",
            f"Innenstadtplan, Kennung {letter}",
            category=category,
            summary=f"{name} ist im detaillierten Innenstadtplan mit der Kennung {letter} verzeichnet.",
            coordinates=coords,
        )
        inner_ids.append(catalogue.places[name_key(name)]["properties"]["id"])
    return list(dict.fromkeys(wildost_ids)), list(dict.fromkeys(inner_ids))


def add_legacy_places(catalogue: CityCatalogue) -> None:
    for name, scope, category, edition, book_id, title, citation, summary in LEGACY_PLACES:
        coords = jitter(ANCHORS.get(scope, ANCHORS["Hamburg"]), f"legacy:{edition}:{name}", scale=0.045)
        catalogue.add_place(
            name,
            scope,
            edition,
            book_id,
            title,
            citation,
            category=category,
            summary=summary,
            coordinates=coords,
        )
        if edition == "SR1":
            catalogue.add_place(
                name,
                scope,
                "SR2",
                "dids-sr2",
                "Deutschland in den Schatten",
                citation,
                category=category,
                summary=summary,
            )


def add_deutsche_bucht(catalogue: CityCatalogue) -> list[int]:
    ids = []
    for name, coords, summary in DEUTSCHE_BUCHT_SPOTS:
        catalogue.add_place(
            name,
            "Deutsche Bucht",
            "SR5",
            "hamburg-detail-maps-sr5",
            "Hamburgpaket – Karten und Karteikarten",
            "Karteikarte Deutsche Bucht",
            category="Umland und Küste",
            summary=summary,
            coordinates=coords,
            exact=True,
        )
        ids.append(catalogue.places[name_key(name)]["properties"]["id"])
    # SR6 updates for the two explicitly described strategic sites.
    for name, summary in [
        (
            "Mittelplate-A",
            "Die AG-Chemie-Raffinerieplattform verarbeitet die verbliebenen Vorkommen des Mittelplate-Felds und ist regelmäßig Ziel von Piraten und GreenWar.",
        ),
        (
            "Itzehoe",
            "Itzehoe entwickelt sich zu einem piratenfreundlichen Hafen mit besonders fähigen Schiffsbauern und Reparaturmöglichkeiten.",
        ),
    ]:
        catalogue.add_place(
            name,
            "Deutsche Bucht",
            "SR6",
            "piraten-bucht-sr6",
            "Datapuls: Piraten der Deutschen Bucht",
            "Datapuls: Piraten der Deutschen Bucht, S. 12 bzw. 18",
            summary=summary,
        )
    return ids


def add_people(catalogue: CityCatalogue) -> None:
    for name, role, affiliation, location, summary in PEOPLE:
        catalogue.add_person(
            name,
            "SR5",
            "hamburg-character-cards-sr5" if name.split()[0] in {"Myriam", "Anna", "Ulrike", "Snow-WT", "Verena", "Warentester", "Pater", "Alien", "Lasse"} else "datapuls-hamburg-sr5",
            "Hamburg-Zusatzpack – Charakter-Karteikarten" if name.split()[0] in {"Myriam", "Anna", "Ulrike", "Snow-WT", "Verena", "Warentester", "Pater", "Alien", "Lasse"} else "Datapuls: Hamburg",
            f"Dossier {name}",
            role=role,
            affiliation=affiliation,
            summary=summary,
            location_name=location,
        )

    for gang, scope, summary in GANGS:
        catalogue.add_person(
            gang,
            "SR5",
            "hamburg-detail-maps-sr5",
            "Hamburgpaket – Karten und Karteikarten",
            f"Gangkarte, {gang}",
            role="Hamburger Gang",
            affiliation=scope,
            summary=summary,
            entity_type="group",
            location_name=scope,
        )

    for name, role, affiliation, location, summary in SR6_PIRATES:
        entity_type = "person" if name.startswith("Kapitän") else "group"
        catalogue.add_person(
            name,
            "SR6",
            "piraten-bucht-sr6",
            "Datapuls: Piraten der Deutschen Bucht",
            f"Piraterie und sichere Häfen: {name}",
            role=role,
            affiliation=affiliation,
            summary=summary,
            entity_type=entity_type,
            location_name=location,
        )

    for (
        name,
        edition,
        book_id,
        title,
        citation,
        role,
        affiliation,
        location,
        summary,
    ) in ADDITIONAL_PEOPLE:
        catalogue.add_person(
            name,
            edition,
            book_id,
            title,
            citation,
            role=role,
            affiliation=affiliation,
            summary=summary,
            location_name=location,
        )
        if edition == "SR1":
            catalogue.add_person(
                name,
                "SR2",
                "dids-sr2",
                "Deutschland in den Schatten",
                citation,
                role=role,
                affiliation=affiliation,
                summary=summary,
                location_name=location,
            )

    for name, role, location, summary in ORGANISATIONS:
        catalogue.add_person(
            name,
            "SR5",
            "datapuls-hamburg-sr5",
            "Datapuls: Hamburg",
            f"Organisation: {name}",
            role=role,
            affiliation="Hamburg",
            summary=summary,
            entity_type="group",
            location_name=location,
        )
        # Explicit legacy mentions preserve edition switching without a
        # duplicated group entry.
        if name in {
            "Lobatchevski-Syndikat",
            "Likedeeler",
            "Klabauterbund",
            "GreenWar",
            "Störtebekers Erben",
            "Altona 7",
        }:
            catalogue.add_person(
                name,
                "SR4",
                "schattenstaedte-sr4",
                "Schattenstädte",
                f"Hamburg-Kapitel: {name}",
                entity_type="group",
            )
        if name in {"Klabauterbund", "Grüne Zellen", "Störtebekers Erben"}:
            catalogue.add_person(
                name,
                "SR1",
                "dids-sr1",
                "Deutschland in den Schatten",
                f"Hamburg-Kapitel: {name}",
                entity_type="group",
            )
            catalogue.add_person(
                name,
                "SR2",
                "dids-sr2",
                "Deutschland in den Schatten",
                f"Hamburg-Kapitel: {name}",
                entity_type="group",
            )
        if name in {"Klabauterbund", "Grüne Zellen", "Störtebekers Erben", "Altona 7"}:
            catalogue.add_person(
                name,
                "SR3",
                "dids2-sr3",
                "Deutschland in den Schatten II",
                f"Freistadt Hamburg: {name}",
                entity_type="group",
            )

    # Editionsübergreifende Kernfiguren: identische Akteure werden in einem
    # Dossier zusammengeführt, nicht als zweite Person angelegt.
    for name, edition, book_id, title, citation in [
        ("Myriam Hergeim alias Ceridwen", "SR4", "schattenstaedte-sr4", "Schattenstädte", "Ceridwen/Druidessa/Aconitae"),
        ("Vesna Lyzhichko", "SR4", "schattenstaedte-sr4", "Schattenstädte", "Bürgermeisterin Vesna Lyzhichko"),
        ("Alien Queen", "SR4", "schattenstaedte-sr4", "Schattenstädte", "Alien Queen"),
        ("Warentester alias Klaas", "SR4", "schattenstaedte-sr4", "Schattenstädte", "Likedeeler und Hamburger Schatten"),
        ("Lasse Petrovic", "SR4", "schattenstaedte-sr4", "Schattenstädte", "HAZMAT"),
        ("Myriam Hergeim alias Ceridwen", "SR1", "dids-sr1", "Deutschland in den Schatten", "Hamburger Chronik"),
        ("Myriam Hergeim alias Ceridwen", "SR2", "dids-sr2", "Deutschland in den Schatten", "Hamburger Chronik"),
    ]:
        catalogue.add_person(name, edition, book_id, title, citation)


def write_labels(catalogue: CityCatalogue) -> None:
    labels = []
    for name, _, _ in DISTRICTS:
        place = catalogue.places[name_key(name)]["properties"]
        lat, lon = ANCHORS[name]
        labels.append(
            {
                "name": name,
                "lat": lat,
                "lon": lon,
                "type": "district",
                "entity_id": place["id"],
            }
        )
    labels.extend(
        [
            {
                "name": "Wildost",
                "lat": ANCHORS["Wildost"][0],
                "lon": ANCHORS["Wildost"][1],
                "type": "outskirts",
                "entity_id": catalogue.places[name_key("Wildost")]["properties"]["id"],
            },
            {
                "name": "Sachsenwald",
                "lat": ANCHORS["Sachsenwald"][0],
                "lon": ANCHORS["Sachsenwald"][1],
                "type": "outskirts",
                "entity_id": catalogue.places[name_key("Sachsenwald")]["properties"]["id"],
            },
        ]
    )
    write_json(CITY_DIR / "labels.json", labels)


def write_district_boundaries(catalogue: CityCatalogue) -> None:
    path = CITY_DIR / "districts.geojson"
    districts = json.loads(path.read_text(encoding="utf-8"))
    for feature in districts["features"]:
        item = catalogue.places.get(name_key(feature["properties"].get("name", "")))
        if not item:
            continue
        props = item["properties"]
        feature["properties"].update(
            {
                "entity_id": props["id"],
                "description_preview": props["description_preview"],
                "description_full": props["description_full"],
                "editions": props["editions"],
                "sources": props["sources"],
            }
        )
    write_json(path, districts)


def write_exterritorial(catalogue: CityCatalogue) -> None:
    # City Nord/Sardinenstadt is explicitly described as completely
    # exterritorial. The polygon follows the recognizable office-city edge:
    # Jahnring/Stadtpark in the south, Hebebrandstraße in the north,
    # Sengelmannstraße in the east and the western office-block edge.
    feature = {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [10.0138, 53.6003],
                [10.0153, 53.6076],
                [10.0192, 53.6112],
                [10.0287, 53.6110],
                [10.0335, 53.6073],
                [10.0331, 53.6002],
                [10.0290, 53.5968],
                [10.0201, 53.5965],
                [10.0138, 53.6003],
            ]],
        },
        "properties": {
            "zone_type": "corporate",
            "label": "Exterritoriales Konzerngebiet · Sardinenstadt (City Nord)",
            "color": "#f1cf49",
            "source": "Datapuls: Hamburg, S. 40–41",
            "entity_id": catalogue.places[name_key("Sardinenstadt / City Nord")]["properties"]["id"],
            "status": "corporate",
            "topology": "disjoint",
            "basis": (
                "Vollständig exterritoriale Sardinenstadt; Außenkante entlang "
                "Jahnring/Stadtpark, Hebebrandstraße, Sengelmannstraße und "
                "westlicher Bürostadtkante"
            ),
            "boundary_review_status": "source-aligned",
            "boundary_review_label": (
                "Mit Datapuls Hamburg und den erkennbaren Straßen- und "
                "Blockkanten der City Nord abgeglichen"
            ),
            "description_preview": "Die Sardinenstadt ist ein dichtes Geflecht aus Konzernbüros und Wohnhochhäusern und laut Datapuls vollständig exterritorial.",
            "description_full": "Die Sardinenstadt, die frühere City Nord, ist vollständig exterritorial. Zugang und Bewegung unterliegen Konzernkontrollen; die dargestellte Außenkante folgt den heutigen Straßen- und Blockkanten der Bürostadt.",
            "sources": [
                {
                    "bookId": "datapuls-hamburg-sr5",
                    "title": "Datapuls: Hamburg",
                    "edition": "SR5",
                    "citation": "S. 40–41",
                    "purpose": "boundary",
                }
            ],
            "editions": ["SR5"],
        },
    }
    write_json(
        CITY_DIR / "exterritorial.geojson",
        {
            "type": "FeatureCollection",
            "name": "Hamburg exterritoriale Konzerngebiete",
            "topology": {
                "model": "exclusive-corporate-over-normal",
                "unresolved_overlap_area_degrees_squared": 0,
            },
            "features": [feature],
        },
    )


def write_atlas_marker_ids(
    main_ids: dict[int, int],
    wildost_ids: list[int],
    inner_ids: list[int],
    bucht_ids: list[int],
) -> None:
    atlas_path = CITY_DIR / "atlas.json"
    atlas = json.loads(atlas_path.read_text(encoding="utf-8"))
    by_key = {item["key"]: item for item in atlas}
    by_key["hamburg-gesamt"]["markerIds"] = list(dict.fromkeys(main_ids.values()))
    by_key["hamburg-wildost-neue-mitte"]["markerIds"] = wildost_ids
    by_key["hamburg-innenstadt"]["markerIds"] = inner_ids
    by_key["deutsche-bucht"]["markerIds"] = bucht_ids
    write_json(atlas_path, atlas)


def main() -> None:
    catalogue = CityCatalogue(
        CITY_ID,
        "Hamburg",
        ANCHORS["Hamburg"],
        ANCHORS,
        BOOKS,
    )
    hamburg_preview = (
        "Hamburg ist 2080 ein wasserreicher, eigenwilliger Metroplex aus Hafen, "
        "Medienmacht, Konzernbezirken, Umland und der Deutschen Bucht."
    )
    catalogue.set_city_profile(
        hamburg_preview,
        hamburg_preview + (
            " Die Schwarze Flut hat Küstenlinie und Stadtstruktur dauerhaft verändert. "
            "Dreizehn Lore-Bezirke, Wildost, Sachsenwald, Hafenwirtschaft, Piraterie, "
            "Syndikate und starke lokale Gegenkulturen machen Hamburg zu einem der "
            "wichtigsten Schattenzentren der ADL."
        ),
        {
            "SR1": city_edition(
                "SR1", "dids-sr1", "Deutschland in den Schatten", "Hamburg-Kapitel",
                "Hamburg ist eine von Hafen, Konzernen, Schmuggel und eigenständiger Stadtkultur geprägte ADL-Metropole.",
                "Der frühe Quellenstand beschreibt Hamburg als von Hafen, Konzernen, Schmuggel und eigenständiger Stadtkultur geprägte ADL-Metropole. Freie und kriminelle Netzwerke nutzen die besondere Lage zwischen Elbe und Nordsee.",
            ),
            "SR5": city_edition(
                "SR5", "datapuls-hamburg-sr5", "Datapuls: Hamburg", "Stadtprofil und Bezirke, S. 20–78",
                hamburg_preview,
                hamburg_preview + " Der Datapuls beschreibt dreizehn Bezirke mit stark unterschiedlichen Sicherheits-, Sozial- und Konzernstrukturen sowie Wildost als angrenzenden Sonderraum.",
            ),
            "SR6": city_edition(
                "SR6", "hamburg-guide-sr6", "Hamburg – Venedig des Nordens", "Hamburg-Stadtführer",
                "Hamburg bleibt ein Hafen-, Medien- und Schattenzentrum, dessen Wasserwege Stadtbild und Machtverhältnisse bestimmen.",
                "Hamburg bleibt ein Hafen-, Medien- und Schattenzentrum. Wasserwege, Hafenlogistik, Tourismus, Piraten der Deutschen Bucht und lokale Machtgruppen bestimmen Verkehr, Wirtschaft und Schattenarbeit.",
            ),
        },
    )
    main_ids = add_main_map(catalogue)
    add_districts(catalogue)
    wildost_ids, inner_ids = add_detail_maps(catalogue)
    add_legacy_places(catalogue)
    bucht_ids = add_deutsche_bucht(catalogue)
    add_people(catalogue)
    catalogue.finish(
        2080,
        "Hamburg umfasst den Metroplex und die Deutsche Bucht: 309 nummerierte Orte der Gesamtkarte, Detailpunkte aus Wildost und Innenstadt, Lore-Bezirke, Küstenorte, Personen, Gangs und Piratencrews. Editionsgleiche Einträge werden in gemeinsamen Dossiers zusammengeführt.",
        bounds=[[53.1, 6.45], [54.85, 11.4]],
        zoom=8,
    )
    write_labels(catalogue)
    write_district_boundaries(catalogue)
    write_exterritorial(catalogue)
    write_atlas_marker_ids(main_ids, wildost_ids, inner_ids, bucht_ids)


if __name__ == "__main__":
    main()
