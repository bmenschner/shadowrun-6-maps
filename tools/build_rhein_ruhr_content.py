#!/usr/bin/env python3
"""Build the Rhein-Ruhr-Megaplex 2082 content package.

The catalogue combines the two official Revierbericht maps, the dedicated
SR4 and SR6 sourcebooks and exact-name references in the supplied SR1-SR5
German source corpus.  One real/lore entity receives one feature; later and
older source references become edition descriptions on that feature.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from build_us_city_content import CityCatalogue, city_edition, name_key, write_json


ROOT = Path(__file__).resolve().parents[1]
CITY_ID = "rhein-ruhr-2082"
CITY_DIR = ROOT / "data" / CITY_ID
CORPUS = Path("/mnt/c/Users/Privat/Documents/Shadowrun/txtexports")

CORE_FILES = {
    "SR1": CORPUS / "Shadowrun 1/Shadowrun 1D - Deutschland in den Schatten.txt",
    "SR2": CORPUS / "Shadowrun 2/Shadowrun 2D - Deutschland in den Schatten (searchable).txt",
    "SR3": CORPUS / "Shadowrun 3/Shadowrun 3D - Deutschland in den Schatten II (searchable).txt",
    "SR4": CORPUS / "Shadowrun 4/Shadowrun 4D - Rhein-Ruhr-Megaplex.txt",
    "SR5": CORPUS / "Shadowrun 5/03 - Quellenbände/Shadowrun 5D - Datapuls ADL.txt",
    "SR6": CORPUS / "Shadowrun 6/shadowrun_6d_quellenbaende_text/Shadowrun 6D - Revierbericht 2082.txt",
}

BOOKS = [
    {"id": "dids-sr1", "title": "Deutschland in den Schatten", "edition": "SR1"},
    {"id": "dids-sr2", "title": "Deutschland in den Schatten", "edition": "SR2"},
    {"id": "dids2-sr3", "title": "Deutschland in den Schatten II", "edition": "SR3"},
    {"id": "rrmp-sr4", "title": "Rhein-Ruhr-Megaplex", "edition": "SR4"},
    {"id": "datapuls-adl-sr5", "title": "Datapuls: ADL", "edition": "SR5"},
    {"id": "datapuls-komplett-sr5", "title": "Datapuls: ADL – Datapuls Komplett", "edition": "SR5"},
    {"id": "rrp-map-sr6", "title": "Revierbericht 2082 – Karte", "edition": "SR6"},
    {"id": "revierbericht-sr6", "title": "Revierbericht 2082", "edition": "SR6"},
    {"id": "vendetta-sr6", "title": "Vendetta", "edition": "SR6"},
    {"id": "domino-effekt-sr6", "title": "Domino-Effekt", "edition": "SR6"},
    {"id": "budenzauber-sr6", "title": "Budenzauber", "edition": "SR6"},
]

ANCHORS = {
    "Rhein-Ruhr-Megaplex": (51.4556, 7.0116),
    "Bonn": (50.7374, 7.0982),
    "Köln": (50.9375, 6.9603),
    "Leverkusen": (51.0459, 7.0192),
    "Bergisches Land": (51.1000, 7.2600),
    "Urbaner Niederrhein": (51.4200, 6.4500),
    "Mönchengladbach": (51.1805, 6.4428),
    "Krefeld": (51.3388, 6.5853),
    "Wesel": (51.6640, 6.6296),
    "Düsseldorf": (51.2277, 6.7735),
    "Duisburg": (51.4344, 6.7623),
    "Oberhausen": (51.4963, 6.8638),
    "Mülheim an der Ruhr": (51.4186, 6.8845),
    "Essen": (51.4556, 7.0116),
    "Neu-Essen": (51.4250, 7.0050),
    "Kettwig": (51.3622, 6.9414),
    "GlaBotKi": (51.5650, 6.9800),
    "Gelsenkirchen": (51.5177, 7.0857),
    "Bottrop": (51.5291, 6.9447),
    "Kirchhellen": (51.6050, 6.9220),
    "Bochum": (51.4818, 7.2162),
    "Hauerbrache": (51.5770, 7.2000),
    "Recklinghausen": (51.6141, 7.1979),
    "Dortmund": (51.5136, 7.4653),
    "Unna": (51.5378, 7.6897),
    "Hagen": (51.3671, 7.4633),
    "Sauerland": (51.2500, 7.7500),
    "Wuppertal": (51.2562, 7.1508),
    "Unter Tage": (51.5000, 7.1000),
    "Duisport": (51.4500, 6.7420),
    "Düsseldorf-Zentrum": (51.2250, 6.7800),
    "Schwarzer Souk": (50.9510, 6.9160),
    "Seelieviertel": (51.5220, 7.4590),
}


DISTRICTS = [
    ("Bonn", "Der südlichste Teil des Plexes umfasst das vergrößerte Bonn und Teile des Rhein-Sieg-Kreises. Bundesbehörden, internationale Organisationen und Stiftungen stehen einem schleichenden Verfall abseits der geförderten Inseln gegenüber.", "S. 23–26"),
    ("Köln", "Köln wird von Medien, Kirche, Ford, Knight Errant und einem dichten kriminellen Klüngel geprägt. Der Schwarze Souk in Ehrenfeld ist ein eigener Macht- und Schattenraum.", "S. 26–30"),
    ("Leverkusen", "Leverkusen und das Bergische Land stehen wirtschaftlich stark unter dem Einfluss der AG Chemie. Chemiepark, Entsorgung, Tourismus und Schattenlabore bestimmen das Gebiet.", "S. 30–34"),
    ("Urbaner Niederrhein", "Der urbane Niederrhein reicht über Krefeld, Mönchengladbach, Wesel und die dazwischenliegenden, teils entvölkerten Räume. Häfen, Schmuggel, Energieanlagen und Brachen prägen die Region.", "S. 34–35"),
    ("Düsseldorf", "Düsseldorf ist politische Hauptstadt des RRP, Finanzzentrum, Mode- und Medienstandort. Konzerninteressen, Yakuza und luxuriöse Innenstadtquartiere treffen auf abgeschirmte Randräume.", "S. 35–40"),
    ("Duisburg", "Duisburg wird vom Hafen und den dort konkurrierenden Konzernen dominiert. Westliche Kampfzonen, Crittergebiete, Biker und migrantisch geprägte Nachbarschaften bilden den Gegenpol.", "S. 40–43"),
    ("Oberhausen", "Oberhausen vereint Ruhrmetall, Industrie- und Klinikstandorte mit der Neuen Mitte, Freizeitwirtschaft und großen verwilderten Brachen.", "S. 43–45"),
    ("Mülheim an der Ruhr", "Mülheim verbindet ruhige Wohnlagen und Saeder-Krupp-Einfluss mit Luftschiffhafen, Broicher Schloss, Werkstätten und neuen gastronomischen Szenen.", "S. 45–48"),
    ("Essen", "Essen ist das politische und wirtschaftliche Herz von Lofwyrs Revier. Neu-Essen bildet eine hochgesicherte S-K-Enklave; nördliche Bezirke bleiben von Armut, Mafia und Industrie geprägt.", "S. 48–52 und 64–75"),
    ("GlaBotKi", "Gladbeck, Bottrop und Kirchhellen sind von struktureller Armut, Gangs, Bergbau, toxischen Altlasten und neuen magischen Funden bestimmt; Gelsenkirchen bildet den größeren urbanen Gegenpol.", "S. 52–56"),
    ("Bochum", "Bochum und Witten verbinden Hochschulen, Kliniken, Unterhaltung und Arkologien mit einer ausgedehnten Party- und Gangszene. Witten steht weitgehend unter S-K-Einfluss.", "S. 56–58"),
    ("Dortmund", "Dortmund und Unna werden von Arkologien, Logistik, Ruhruniversität, Militär und zahlreichen identitätsstiftenden Gangs geprägt.", "S. 58–61"),
    ("Hagen", "Hagen bildet das Tor zum verwilderten Sauerland. Fernuniversität, Burgen, ländliche Rückzugsräume, Schmuggel und erwachte Wildnis liegen eng beieinander.", "S. 61–64"),
    ("Wuppertal", "Wuppertal ist vertikal in Ebenen gegliedert: Talsohle und Unterstadt sind arm und gefährlich, höhere Ebenen dienen Verkehr, Konzernen und privilegiertem Wohnen.", "S. 75–78"),
    ("Unter Tage", "Stollen, alte Zechen, neue Förderanlagen und verborgene Siedlungen bilden einen eigenen, gefährlichen Raum unter dem Megaplex.", "S. 79–82"),
    ("Recklinghausen", "Die Sonderverwaltungszone Recklinghausen ist ein zersplitterter Raum aus Restverwaltung, Warlords, Zechenbetreibern, Gangs und der Hauerbrache.", "S. 82–86"),
    ("Schwarzer Souk", "Ehrenfeld und Neu-Ehrenfeld bilden das Machtzentrum der Grauen Wölfe. Der Schwarze Souk ist einer der größten Schwarzmärkte des Plexes.", "S. 86–87"),
    ("Seelieviertel", "Das Dortmunder Seelieviertel ist ein sichtbarer Anderwelten- und Feenbezirk mit eigenem Amt, Märkten, Türen und ungewöhnlichen Regeln.", "S. 87–89"),
    ("Duisport", "Duisport ist ein ausgedehnter Freihafen aus exterritorialen Konzernflächen, Zollzonen, automatisierten Terminals und informellen Treffpunkten.", "S. 89–92"),
    ("Düsseldorf-Zentrum", "Altstadt, Shopping- und Bankenviertel sowie Klein-Tokio bilden ein dichtes, hochpreisiges und stark überwachtes Zentrum.", "S. 92–93"),
]


MAP1 = r"""
001|B in B|Ausgehen|B
002|Bermudadreieck|Ausgehen|B
003|Bonifatius|Ausgehen|B
004|Flying Horse|Ausgehen|B
005|Golgatha|Ausgehen|H
006|Hexagon|Ausgehen|H
007|Jahrhunderthalle Bochum|Ausgehen|B
008|Not und Übel|Ausgehen|H
009|Karfunkel|Ausgehen|B
010|Leopolds|Ausgehen|B
011|Level Up|Ausgehen|B
012|Lloyd-Webber-Halle|Ausgehen|B
013|Riverdance|Ausgehen|B
014|Sahara|Ausgehen|B
015|Saruman|Ausgehen|B
016|Schauspielhaus Bochum|Ausgehen|B
017|Schliemann Theater|Ausgehen|B
018|Tief im Westen|Ausgehen|B
019|TolleTage|Ausgehen|B
020|Varieté Furiosa|Ausgehen|B
021|Babo Fat|Bars und Kneipen|B
022|Bei Trude|Bars und Kneipen|H
023|Bückmann-Stube|Bars und Kneipen|H
024|Elf’Ant|Bars und Kneipen|B
025|Fietes Stube|Bars und Kneipen|B
026|Geizhaus|Bars und Kneipen|B
027|King Louis’|Bars und Kneipen|H
028|Parole O|Bars und Kneipen|B
029|Ross & Reiter|Bars und Kneipen|B
030|Rubin|Bars und Kneipen|B
031|Sp’rit|Bars und Kneipen|H
032|Tropicano|Bars und Kneipen|B
033|1000 Nützlichkeiten|Einkaufen|B
034|Aggravex-Center|Einkaufen|B
035|Aldi-Real|Einkaufen|B
036|Bergknappen Tinkerhalle|Einkaufen|H
037|CeeBee’s Kurzwaren|Einkaufen|H
038|Crims’n’Tight|Einkaufen|H
039|Feder & Stahl|Einkaufen|B
040|Fischers Fritze|Einkaufen|H
041|Günnis Kiosk|Einkaufen|H
042|Kniftenharry|Einkaufen|H
043|Marco’s Tanke|Einkaufen|H
044|Onkel Ehrich|Einkaufen|B
045|Onyx-Center|Einkaufen|B
046|Ritschie Rauscher|Einkaufen|H
047|Schnitters Keller|Einkaufen|H
048|Stuffer-Plus Superkauf|Einkaufen|B
049|Vockenhof-Markt|Einkaufen|H
050|Golden Goal|Freizeit|B
051|Jumanji|Freizeit|B
052|Der Ring|Freizeit|H
053|Ruhrstadion|Freizeit|B
054|Schnorchelparadies|Freizeit|B
055|Shooter’s Palace|Freizeit|B
056|SnowWorld|Freizeit|B
057|Siegfriedklause|Freizeit|H
058|Tamago-No-Yamas|Freizeit|B
059|TowerEscape|Freizeit|B
060|WarOfChamps|Freizeit|B
061|Zeche Müser CrossGolf|Freizeit|B
062|Abdomen|Hotels|H
063|All-In Hotel|Hotels|B
064|Akindo Hotel|Hotels|B
065|Capsule Market|Hotels|B
066|Chavanne Hotel|Hotels|B
067|Chez Francois|Hotels|B
068|Hacienda Adventures|Hotels|B
069|Dragon Hostel|Hotels|B
070|Nachtigall|Hotels|H
071|Takaya Hostel|Hotels|B
072|Tucholsky Hotel|Hotels|B
073|EMC Logistikzentrum Bochum|Konzerne|B
074|Hochtief Maintenance Center|Konzerne|B
075|Krupp Manufacturing WBW 3|Konzerne|B
076|MCT Zentrallager BO|Konzerne|B
077|Opel Werk II Bochum-Laer|Konzerne|B
078|Ruhr-Nuklear Aufbereitung Herne|Konzerne|H
079|Ruhrstahl Kaltwalzwerk Bochum|Konzerne|B
080|Shiawase City Services|Konzerne|B
081|Shiawase Housing|Konzerne|B
082|AldiBurger City|Restaurants|B
083|AldiBurger West|Restaurants|B
084|AldiDöner|Restaurants|B
085|Astrids Asphaltmenü|Restaurants|H
086|Ècolo|Restaurants|B
087|HabEenHappen|Restaurants|B
088|Hochofen|Restaurants|H
089|Küfa la Revolution|Restaurants|B
090|Parkschlösschen|Restaurants|B
091|Die Rattenfängerin|Restaurants|H
092|Rosemaries|Restaurants|B
093|Trattoria Parma|Restaurants|B
094|Kyoto|Restaurants|B
095|0-Zone|Sightseeing|B
096|Deutsches Bergbaumuseum|Sightseeing|B
097|Century Gallery|Sightseeing|B
098|Hauer Ehrenmal|Sightseeing|H
099|Historisches Museum Bochum|Sightseeing|B
100|Horgardhaus|Sightseeing|B
101|Das Loch|Sightseeing|H
102|Planetarium|Sightseeing|B
103|Tierpark Bochum|Sightseeing|B
104|Yoshida Schrein|Sightseeing|B
105|ASH Stützpunkt Bochum-West|Sonstige Spots|B
106|Badawi MC|Sonstige Spots|H
107|Dr. Pein|Sonstige Spots|H
108|Elisabeth Krankenhaus|Medizin|H
109|Gaysundheitszentrum|Medizin|B
110|Grubenharry|Sonstige Spots|H
111|Hez Ereth|Sonstige Spots|H
112|Hez Hightower|Sonstige Spots|H
113|Hez Plamya|Sonstige Spots|H
114|Hez Rapha|Sonstige Spots|H
115|Hez Rookie|Sonstige Spots|H
116|Hez Unikl|Sonstige Spots|H
117|Intershop|Einkaufen|H
118|Justizzentrum|Sicherheit und Justiz|B
119|JVA Bochum|Sicherheit und Justiz|B
120|Die Kaiser-Tafel|Sonstige Spots|H
121|Killerheide|Sonstige Spots|H
122|Mitsuhama Public Health Hospital|Medizin|B
123|Neue Ruhrlandhalle|Freizeit|B
124|Reisebüro Konopke|Dienstleistungen|H
125|St. Elisabeth Hospital|Medizin|B
126|St. Josef Hospital|Medizin|B
127|St. Marien|Medizin|H
128|Südbad|Freizeit|H
129|Südfriedhof|Sightseeing|H
130|Uniklinik Bergmannsheil|Medizin|B
131|Zeche König Ludwig|Industrie und Infrastruktur|H
132|Zeche Recklinghausen|Industrie und Infrastruktur|H
133|Bahnhof Bochum Ehrenfeld|Verkehr|B
134|Bahnhof Bochum Hamme|Verkehr|B
135|Bahnhof Bochum West|Verkehr|B
136|Bahnhof Recklinghausen Süd|Verkehr|H
137|Bochum Hauptbahnhof|Verkehr|B
"""

REGIONAL = [
    (1, "Stadtkriegsgelände Wesel", "Wesel"),
    (2, "First-Up! Spielpunkt Hünxe", "Wesel"),
    (3, "Zeche Ewald", "Recklinghausen"),
    (4, "Halde Hoheward", "Recklinghausen"),
    (5, "Hauerbrache", "Hauerbrache"),
    (6, "AGC Entsorger Dinslaken Süd", "Urbaner Niederrhein"),
    (7, "Duisport", "Duisport"),
    (8, "Alter Zoo", "Duisburg"),
    (9, "Landschaftspark Nord", "Duisburg"),
    (10, "Schloss Oberhausen", "Oberhausen"),
    (11, "Kaisergarten mit Oberhausen", "Oberhausen"),
    (12, "Hafen Oberhausen", "Oberhausen"),
    (13, "Gasometer", "Oberhausen"),
    (14, "Tetraeder", "Bottrop"),
    (15, "Klinik Bergmannsheil", "Bochum"),
    (16, "ZOOM", "Gelsenkirchen"),
    (17, "Cranger Kirmes", "GlaBotKi"),
    (18, "Schloss Broich", "Mülheim an der Ruhr"),
    (19, "Messestadion Essen", "Essen"),
    (20, "Enklave Kettwig", "Kettwig"),
    (21, "Schloss Borbeck", "Essen"),
    (22, "Schloss Hugenpoet", "Kettwig"),
    (23, "Zeche Zollverein", "Essen"),
    (24, "Zeche Carl", "Essen"),
    (25, "Stadtkriegsgelände Essen", "Essen"),
    (26, "Bermudadreieck", "Bochum"),
    (27, "Jahrhunderthalle", "Bochum"),
    (28, "Westfalenhalle", "Dortmund"),
    (29, "Dortmunder U", "Dortmund"),
    (30, "Phönixsee", "Dortmund"),
    (31, "Westfalenpark", "Dortmund"),
    (32, "Düstermarkt", "Dortmund"),
    (33, "Seelieviertel", "Seelieviertel"),
    (34, "#156", "Dortmund"),
    (35, "Schattenkirmes Krefeld", "Krefeld"),
    (36, "Rheinkirmes", "Düsseldorf"),
    (37, "Uniklinikum Düsseldorf", "Düsseldorf"),
    (38, "Schloss Burg", "Bergisches Land"),
    (39, "Schloss Dyck", "Mönchengladbach"),
    (40, "Braunkohletagebau Garzweiler", "Mönchengladbach"),
    (41, "Kölner Dom", "Köln"),
    (42, "Schwarzer Souk", "Schwarzer Souk"),
    (43, "Stadtkriegsgelände Köln", "Köln"),
    (44, "KVB Hub Lövenich", "Köln"),
    (45, "Drachenfels", "Bonn"),
    (46, "Schlösser Augustusburg und Falkenlust", "Köln"),
]

ESSEN = {
    "Konzerne": "S-K Hauptarkologie;Nordturm;Westturm;Südturm;Ostturm;Messe Essen;Neu-Essener Verwaltungsgesellschaft;Wassergewinnung Essen;Agrargesellschaft Bertha Krupp;Draco Foundation;Flughafen Essen-Mülheim;Industriegebiet Neu-Halbach;Aerospace Campus;Degussa-Evonik;Hochtief",
    "Wohnen und Unterkunft": "Schloss Baldeney;Margarethenhöhe;Margarethe-Krupp-Seniorenresidenzkomplex;Krupp Excelsior;Schloss Hugenpoet;Albergo Pegaso",
    "Bildung und Forschung": "Essen Magic Campus;S-K Globetrotters;Max-Planck-Stadt;University of Applied Sciences;S-K Business School;Alfried Krupp Wissenschaftskolleg;Folkwang-Universität der Künste;Präsident Lofwyr Oberstufe für begabte Schüler;Alfried-Krupp-Klinik Rüttenscheid;Alfried-Krupp-Forschungsklinikum;Alfried-Krupp Spezialklinikum;Schloss Landsberg;Flothmann-Schule",
    "Dienstleistungen": "S-K World Mall;Diamant;Haarlekin",
    "Ausgehen": "The Psychedelic Dungeon;Majestix;Colorful;Arkadia;Zum Kranich;Club Drakonisch;Spielbank;Yachtclub;Radwhana;Karfunkel",
    "Freizeit": "Stadtwald;Museum Folkwang;Baldeneysee;Sports Center;S-K Centurios;S-K Cataphracts;Haus Oefte;Philharmonie;Krupp-Aalto-Theater;Roundhouse",
    "Sonstige Spots": "Essener Hauptbahnhof;S-K Ehrenfriedhof",
}

SR6_PLACES = {
    "Bonn": "Krupp Munitions;UN-Campus;Grenzschutzkommando Mitte;Museumsmeile;Rheinperle;Grandhotel & Spa Petersberg",
    "Leverkusen": "AGC Tower West;CHEMPARK;Entsorgungszentrum Leverkusen;Technologiefabrik Remscheid;Schattenlabore;AGC Erholhaus;Friedrich Bayer Forum;Neue Rathaus-Galerie Leverkusen;Grandhotel Schloss Bensberg;Schloss Lerbach",
    "Urbaner Niederrhein": "Energiepark Mönchengladbach;Der zweite Esel;Bude 9;Geismühle",
    "Düsseldorf": "Medienhafen;Festwiese;Grünes Düsseldorf;Heinrich-Heine-Campus und Uniklinikum;Kaiserswerth;Sunset Lounge;Le Dojo;Die Kurve",
    "Duisburg": "Ehemaliger Duisburger Zoo;Kampfzone Rheindamm;Werk Heimat;Mezze Ghulami;Der Schulhof;Kabul-Karate",
    "Oberhausen": "Neue Mitte 2.0;Ruhrmetall-Hauptsitz;Holten-Klinik;Tierklinik Oberhausen;Große Brache;Dümpten;Stern-Kaufhaus",
    "Mülheim an der Ruhr": "Luftschiffhafen;Design-Café Farbtier;Akame Soulfood",
    "Essen": "Kaisertrödel;Krupp-Gürtel;Vestas Pizza;Die Diele",
    "GlaBotKi": "Geisterbaustelle Kirchhellen;Schalke 04;Deroudier-Stiftung;Motorradmuseum Gelsenkirchen;Übernachtung Frau Behrs;Gewerbehof Bottrop;Manuel’s Eck;Bülow-Garagen",
    "Bochum": "Shiawase-Arkologie;Kirilenko-Ruhestandsarkologie;Biomechanomicon",
    "Dortmund": "Spellweavers-Arkologie;Reinoldikirche;Ghuldorf;Spielbank Hohensyburg;Zeche Hellweg;Flecktarn D;Akai Kotai;Nobili Civitate;Fernuniversität Hagen;Hohenlimburg;Gegen den Durst",
    "Wuppertal": "Wuppertal Ebene A;Wuppertal Ebene B;Wuppertal Ebene C;Wuppertal Ebene D",
    "Recklinghausen": "Marl",
    "Seelieviertel": "Seelietower;Feenamt;Rattenmarkt;Palette;Nordpol;Black Pigeon;Borsigplatz;Azizabrache;Russenhütte;Druidenbrache;Libellenbrache;Zum U-Turm;Feentüren;Anderwelten;Fleischnäher;Fleischflicker;Fleischformer",
    "Duisport": "Zollverwaltung;Pier 27 Ost;Luis’ Wurstbude",
    "Düsseldorf-Zentrum": "Altstadt Düsseldorf;Shoppingviertel Düsseldorf;Bankenviertel Düsseldorf;Klein-Tokio",
    "Rhein-Ruhr-Megaplex": "Ernas Frittenschmiede;Institut für Rechtsmedizin im Universitätsklinikum Düsseldorf;Schattenwerkstatt;FTS-Umschlagpunkt Hünxe;EinsZwo auf Ewald;Lösemittelwerk der AG Chemie;S-K-Prime-Horchposten;Blabla",
}

SR4_PLACES = [
    ("Schlossrestaurant Hugenpoet", "Kettwig"), ("Borbecker Dampfbierbrauerei", "Essen"),
    ("Cocktailbar Schirmchen", "Leverkusen"), ("Shamrock", "Wuppertal"),
    ("Topkes Grill", "Gelsenkirchen"), ("Novades", "Dortmund"), ("Café Nussbaum", "Mülheim an der Ruhr"),
    ("Lotosblatt", "Düsseldorf"), ("Grubengold", "Bochum"), ("Komm Rinn", "Urbaner Niederrhein"),
    ("Nordend", "Gelsenkirchen"), ("Wartburg", "Dortmund"), ("Bratheide", "GlaBotKi"),
    ("Cinopolis", "Düsseldorf"), ("Munz-Hallen", "Köln"), ("Centro", "Oberhausen"),
    ("KaiMai", "Duisburg"), ("Turbinenhalle", "Oberhausen"), ("KaRamm!!", "Bottrop"),
    ("Untergrund", "Dortmund"), ("WestNordWest", "Krefeld"), ("Geoastrale Halde Beckstraße", "Bottrop"),
    ("Sparkis", "Düsseldorf"), ("Haus Morp", "Düsseldorf"), ("Zeche Dahlbusch", "Gelsenkirchen"),
    ("Haus Harkorten", "Hagen"), ("JaNein", "Rhein-Ruhr-Megaplex"), ("Kruger-Anomalie", "Kirchhellen"),
    ("AR-Gamezone Dümpten", "Mülheim an der Ruhr"), ("Krämerei", "Dortmund"),
    ("Unkrautviertel", "Köln"), ("Autofriedhof Darius", "Bergisches Land"),
    ("Parkbasar", "GlaBotKi"), ("Grauer Flohmarkt", "Krefeld"), ("Steinerner Turm", "Dortmund"),
    ("Kunstsammlung des Landes NRR", "Düsseldorf"), ("Küppersmühle", "Duisburg"),
    ("Deutsche Arbeitsschutzausstellung", "Dortmund"), ("Zentrum für AR-Kunst", "Rhein-Ruhr-Megaplex"),
    ("Römisch-Germanisches Museum", "Köln"), ("Neue Ruhr-Universität", "Dortmund"),
    ("Interkonzernelles Forschungsinstitut West", "Dortmund"), ("Proteus Tower", "Dortmund"),
    ("Hauptfriedhof Dortmund", "Dortmund"), ("Zeche Nachtigall", "Bochum"),
    ("Nippon Kan", "Düsseldorf"), ("MediaDome", "Oberhausen"),
]

PEOPLE_SR6 = [
    ("Skadi Persson", "Schattenakteurin"), ("Saskia Janssen", "Lokale Akteurin"),
    ("Erzbischof Gabriel Hermann", "Kirchenvertreter"), ("Kevin Lorenz", "Lokaler Akteur"),
    ("Remy Peyrou", "Lokaler Akteur"), ("Vanadis Satu Hyvönen", "Erwachte Akteurin"),
    ("Abbey Kröll", "Lokale Akteurin"), ("Ebbo Deschamps", "Lokaler Akteur"),
    ("Heron Gonzales alias Schmiddi", "Schieber"), ("Nele Liefers", "Lokale Akteurin"),
    ("Vito Graf", "Lokaler Akteur"), ("Egon Frenzel", "Lokaler Akteur"),
    ("Mikku Kadenberger", "Lokaler Akteur"), ("Hans Swoboda", "Lokaler Akteur"),
    ("Dr. Fromm", "Mediziner"), ("Jan Perscheidt", "Lokaler Akteur"),
    ("Esther Paschulke", "Lokale Akteurin"), ("Erna", "Betreiberin von Ernas Frittenschmiede"),
    ("Sandra Matschke", "Rechtsmedizinerin"), ("Manfred Kreissler", "Lokaler Akteur"),
    ("Anna Schröder", "CEO Ford Motor ADL"), ("Markus Hofmann", "Knight-Errant-Leiter"),
    ("Ekrem „Baba“ Bozdogan", "Anführer der Grauen Wölfe"), ("Fatma „Gelincik“ Atatürk", "Unterweltakteurin"),
    ("Azra „Sahin“ Celik", "Unterweltakteurin"), ("Achim Dippels", "Betreiber des Schulhofs"),
    ("Sahmet Dippels", "Betreiberin des Schulhofs"),
]

RRP_36 = "Eschek;Pitter;Aaliyah;Jokep;Osaro Nkem;Gumpen-Lieke;Mottek;Meryem;Samara;Der Kaschubiak;Francesco „Finito“ Esposito;Bahira Dalal;Schambes;Marlene;Rys;(Talis-)Tünnes;Mamoru/Martin/Mömmes;Die schöne Aleyna;Liz;Jupp;Oschek;Herr Dietrich;Malik;Christine „Khukuri“ Kuhn;Doc Ammit;Baba Katili;De Ruude Jeck;Cheiron;Tilly;Mischkan;Ryuzaki;Persona;Sperber;Der Schäle Schäng;Katharizna;Canim".split(";")

RRP_36_DETAILS = {
    "Eschek": "Eschek ist ein gewaltbereiter Hooligan und angeheuerter Schläger aus dem Revier.",
    "Pitter": "Pitter ist ein ehemaliger Ganganführer mit Verbindungen zur Grubenwehr und in das Arbeitermilieu.",
    "Aaliyah": "Aaliyah ist eine junge Gangerin aus dem Umfeld der Norgoz Hez.",
    "Jokep": "Jokep ist ein neutraler Straßendoc, dessen Dienste von sehr unterschiedlichen Seiten genutzt werden.",
    "Osaro Nkem": "Osaro Nkem ist Jäger und Organhändler in den gefährlicheren Teilen des Plexes.",
    "Gumpen-Lieke": "Gumpen-Lieke ist eine bekannte Hooligan-Figur der regionalen Szene.",
    "Mottek": "Mottek ist ein Soldat des organisierten Verbrechens mit enger Bindung an das Revier.",
    "Meryem": "Meryem arbeitet als Schuldeneintreiberin und verfügt über entsprechende Kontakte und Druckmittel.",
    "Samara": "Samara ist eine erwachte Vermittlerin und Fixerin für ungewöhnliche Aufträge.",
    "Der Kaschubiak": "Der Kaschubiak ist ein professioneller Auftragsmörder.",
    "Francesco „Finito“ Esposito": "Francesco „Finito“ Esposito ist ein erfahrener Consigliere aus dem Mafiagefüge des Plexes.",
    "Bahira Dalal": "Bahira Dalal ist eine Satyrin und Zuhälterin mit eigenem Einflussbereich.",
    "Schambes": "Schambes ist Decker und Gamer mit Kontakten in die lokale Matrixszene.",
    "Marlene": "Marlene gehört zu den kampferprobten Autobahnkriegern des Reviers.",
    "Rys": "Rys ist Mechaniker und technischer Problemlöser für Fahrzeuge und improvisierte Ausrüstung.",
    "(Talis-)Tünnes": "(Talis-)Tünnes ist ein Taliskrämer und Ansprechpartner für magische Waren.",
    "Mamoru/Martin/Mömmes": "Mamoru, auch Martin oder Mömmes, ist ein junger Decker und angehender Shadowrunner.",
    "Die schöne Aleyna": "Die schöne Aleyna ist eine Hexe mit Kontakten in die magische Unterwelt.",
    "Liz": "Liz ist Sensoranalystin der Polizei und kann technische Überwachung auswerten.",
    "Jupp": "Jupp betreibt einen Kiosk und ist zugleich eine niedrigschwellige Informationsquelle im Viertel.",
    "Oschek": "Oschek ist ein Straßenpolizist mit praktischem Revierwissen.",
    "Herr Dietrich": "Herr Dietrich ist Ermittler des Metroplex-Sicherheitsdienstes.",
    "Malik": "Malik ist Scharfschütze und Angehöriger einer Spezialeinheit.",
    "Christine „Khukuri“ Kuhn": "Christine „Khukuri“ Kuhn ist eine ehemalige Polizistin und gefährliche Serienmörderin.",
    "Doc Ammit": "Doc Ammit ist ein ghulischer Straßendoc für Patienten, die reguläre Kliniken meiden müssen.",
    "Baba Katili": "Baba Katili ist eine kampferfahrene Soldatin aus dem Umfeld des KSK.",
    "De Ruude Jeck": "De Ruude Jeck ist ein legendärer Rigger des Rhein-Ruhr-Megaplexes.",
    "Cheiron": "Cheiron ist ein schwer bewaffneter Straßensamurai.",
    "Tilly": "Tilly ist eine Kampfsportadeptin und gefährliche Nahkämpferin.",
    "Mischkan": "Mischkan ist ein Prime-Agent im Dienst Saeder-Krupps.",
    "Ryuzaki": "Ryuzaki ist ein Sicherheitsmann aus dem Umfeld Mitsuhama Computer Technologies.",
    "Persona": "Persona ist eine transhumanistische Informationshändlerin.",
    "Sperber": "Sperber ist ein Elitesoldat aus dem Machtbereich Saeder-Krupps.",
    "Der Schäle Schäng": "Der Schäle Schäng ist ein Straßenschamane mit starken lokalen Bindungen.",
    "Katharizna": "Katharizna ist eine Hexe und Trickbetrügerin.",
    "Canim": "Canim ist ein junger Vampir, der eine eigene Gang um sich aufbaut.",
}

PEOPLE_SR4 = [
    ("Blue Chrome", "Waffen- und Ausrüstungsschieberin"),
    ("Cosmic", "Infoschieberin"), ("Wallace", "Magischer Schieber"),
    ("Tauscher", "Waffen- und Kunsttauschhändler"), ("Sascha Ludwig", "Betreiber des Leopolds"),
    ("Eddie Norg", "Betreiber von Grubengold"), ("Festus Klein", "Betreiber des Nordend"),
    ("Grummlich", "Sicherheitsmann des Nordend"), ("Han Sparkis", "Fokusmacher"),
    ("Darius Maschelski", "Betreiber des Autofriedhofs"), ("Metzler", "Leiter des Grauen Flohmarkts"),
    ("Cesar „Die Hüfte“ Ruiz", "Schattenakteur"), ("Martina Gehrke", "Lokale Akteurin"),
    ("Faith Panichart", "Lokale Akteurin"), ("Mateusz „Polacke“ Polanski", "Kriminalkommissar"),
    ("Klaus Meineke", "Polizeisergeant"), ("Luca Sattori", "Mafia-Consigliere"),
    ("Sandro „Locusta“ Filini", "Unterweltakteur"), ("Meriam Garnke „Staubbaronin“", "Lokale Machtspielerin"),
]

GROUPS = [
    ("Gelsenkirchen Pits", "Gang"), ("Desperados MC", "Motorradgang"),
    ("Haimons", "Dortmunder Gang"), ("Ancients im RRP", "Elfische Gang"),
    ("Ladon", "Gang"), ("Sons of Nihon", "Gang"), ("Viertes Reich", "Neonazi-Gang"),
    ("Phönix", "Gang"), ("Die Rammler", "Gang"), ("Walburgas Töchter", "Gang"),
    ("Spartakus’ Erben", "Gang"), ("Acids", "AGC-nahe Gang"), ("White Wolves", "Neonazi-Gang"),
    ("Graue Wölfe", "Kölner Unterweltgruppe"), ("Toxyc Spyryts", "Duisburger Gang"),
    ("Füchse", "Dortmunder Gang"), ("Kinder Gaias", "Magische Gruppe"),
    ("Blue Angels", "Magische Gruppe"), ("Faustianer", "Magische Gruppe"),
    ("Freier Kreis auf Schalke", "Adeptengruppe"), ("Gerresheimer Zirkel", "Magische Gruppe"),
    ("Kodde Fööt", "Magische Gruppe"), ("Ziesak-Kommune", "Magische Kommune"),
    ("Cosa Nostra", "Unterweltorganisation"), ("Trans-Germania", "Unterweltorganisation"),
    ("Troudalis", "Unterweltorganisation"), ("Yakuza", "Unterweltorganisation"),
    ("Kommando Konwacht", "Schattenorganisation"), ("Haldenritter", "Gruppe"),
]

SUPPLEMENTAL_PLACES = [
    # Budenzauber
    ("Engelmann & Kissinger (ENKI)", "Gelsenkirchen", "Budenzauber", "Kleinwildjagd"),
    ("Kiosk am Loch", "Gelsenkirchen", "Budenzauber", "Kleinwildjagd"),
    ("Freddys Garage", "Hauerbrache", "Budenzauber", "Einmal Hauerbrache und zurück"),
    ("Camillas illegales Brauhaus", "Duisport", "Budenzauber", "Auf dem Trockenen"),
    ("Lagerhaus der Likedeeler", "Duisport", "Budenzauber", "Auf dem Trockenen"),
    ("Kiosk Tanke", "GlaBotKi", "Budenzauber", "Auf dem Trockenen"),
    ("Puppenstube", "Bochum", "Budenzauber", "Auf dem Trockenen"),
    ("Kiosk Patal", "Bochum", "Budenzauber", "Auf dem Trockenen"),
    ("Hot ’n’ Tot", "Gelsenkirchen", "Budenzauber", "Auf dem Trockenen"),
    ("Früh & Spät", "Duisburg", "Budenzauber", "Auf dem Trockenen"),
    # Vendetta
    ("Friedrich-Ebert-Brücke", "Duisburg", "Vendetta", "Überfall am Rhein"),
    ("Ruhrport", "Duisport", "Vendetta", "Überfall am Rhein"),
    ("Troudalis-Arena", "Rhein-Ruhr-Megaplex", "Vendetta", "In der Höhle des Löwen"),
    ("Doppelpenthouse", "Düsseldorf", "Vendetta", "Die Brüder"),
    ("Vidattis Villa", "Rhein-Ruhr-Megaplex", "Vendetta", "Wolfszähne"),
    ("Endlager Sorgenfrei", "Dortmund", "Vendetta", "Leonardo"),
    ("Da Nina", "Duisburg", "Vendetta", "Leonardo"),
    ("L’Angelo Essen", "Essen", "Vendetta", "Pizzakrieg"),
    ("L’Angelo Mülheim", "Mülheim an der Ruhr", "Vendetta", "Pizzakrieg"),
    ("Sports Hotel", "Essen", "Vendetta", "Gastfreundschaft"),
    # Domino-Effekte
    ("Unter Tage – Schattenkneipe", "Unter Tage", "Domino-Effekt", "Disintegration"),
    ("Disianischer Ernter unter dem RRP", "Unter Tage", "Domino-Effekt", "Disintegration"),
]

SUPPLEMENTAL_PEOPLE = [
    # Budenzauber
    ("Jeremy Basler", "ENKI-Mitarbeiter", "Budenzauber", "Engelmann & Kissinger (ENKI)"),
    ("Björn Damm", "Budenbesitzer", "Budenzauber", "Kiosk am Loch"),
    ("Marianne Weber", "S-K-Innenrevision", "Budenzauber", "Neu-Essen"),
    ("Matthias Weber", "Ausreißer aus Neu-Essen", "Budenzauber", "Hauerbrache"),
    ("Jonathan Miller", "S-K-Unterhändler und FBV-Informant", "Budenzauber", "Neu-Essen"),
    ("Freddy", "Mechaniker", "Budenzauber", "Freddys Garage"),
    ("Trude", "Trinkhallenbesitzerin", "Budenzauber", "Bei Trude"),
    ("Rapha", "Berater der Hauerbrache", "Budenzauber", "Hez Rapha"),
    ("Camilla Schmitz", "Vorsitzende der freien Büdchen", "Budenzauber", "Camillas illegales Brauhaus"),
    ("Karl Gutmann", "Likedeeler", "Budenzauber", "Lagerhaus der Likedeeler"),
    ("Sophie Gutmann", "Likedeelerin", "Budenzauber", "Lagerhaus der Likedeeler"),
    ("Lukas van Groot", "Bordellteilhaber", "Budenzauber", "Puppenstube"),
    ("Thomas Levin", "Unterweltakteur", "Budenzauber", "Hot ’n’ Tot"),
    ("Tristan Pohl", "Bordellteilhaber", "Budenzauber", "Puppenstube"),
    ("Oma Paula", "Kioskbetreiberin", "Budenzauber", "Kiosk Tanke"),
    ("Schwarzer Kalle", "Bikerboss", "Budenzauber", "Kiosk Tanke"),
    ("Aina", "Anführerin des Dreifach Erleuchteten Ordens", "Budenzauber", "Gelsenkirchen"),
    # Vendetta
    ("Andrea DiMarco", "Adept und Unterhändler", "Vendetta", "Rhein-Ruhr-Megaplex"),
    ("Arnaud Burmer", "Aachener Mafia-Capo", "Vendetta", "Rhein-Ruhr-Megaplex"),
    ("Azra Celik", "Schmugglerin der Grauen Wölfe", "Vendetta", "Schwarzer Souk"),
    ("Cecilia „Cici“ Semenszato", "Begleittier Donna Michaelas", "Vendetta", "Rhein-Ruhr-Megaplex"),
    ("Chiara „Topo“ Bianchi-Gasperi", "Mafia-Deckerin", "Vendetta", "Rhein-Ruhr-Megaplex"),
    ("Costas Troudalis", "Mafia-Capo", "Vendetta", "Troudalis-Arena"),
    ("Der Dachs", "Waffenhändler", "Vendetta", "Unter Tage"),
    ("Don Lupo", "Don der Gasperi-Familie", "Vendetta", "Rhein-Ruhr-Megaplex"),
    ("Donna Michaela", "Mafia-Patrona", "Vendetta", "Rhein-Ruhr-Megaplex"),
    ("Francesco di Lauro", "Mafia-Berater", "Vendetta", "L’Angelo Essen"),
    ("Giacomo Gasperi alias Jacko", "Schamane und Schattentalker", "Vendetta", "Rhein-Ruhr-Megaplex"),
    ("Leonardo Gasperi", "Mafia-Capo", "Vendetta", "Endlager Sorgenfrei"),
    ("Marina", "Mafia-Kämpferin", "Vendetta", "Rhein-Ruhr-Megaplex"),
    ("Mario Esposito", "Mafia-Strategist", "Vendetta", "Rhein-Ruhr-Megaplex"),
    ("Matteo Rossi", "Mafia-Capo", "Vendetta", "Rhein-Ruhr-Megaplex"),
    ("Pietro Mancini", "Mafia-Champion", "Vendetta", "Rhein-Ruhr-Megaplex"),
    ("Raffaele Vidatti", "Anwalt Donna Michaelas", "Vendetta", "Vidattis Villa"),
    ("Ruhrork", "Schattentalker und RRP-Kenner", "Domino-Effekt", "Unter Tage – Schattenkneipe"),
    ("Al’Adhaa", "Disianische Magierin", "Domino-Effekt", "Disianischer Ernter unter dem RRP"),
]

SUPPLEMENTAL_GROUPS = [
    ("Dreifach Erleuchteter Orden der fünf Wege des Sterns", "Toxisch-hermetische Gruppe", "Budenzauber", "Gelsenkirchen"),
    ("Likedeeler am Duisport", "Schmugglergruppe", "Budenzauber", "Duisport"),
    ("Vereinigung der freien Büdchen Plex Mitte e. V.", "Büdchenverband", "Budenzauber", "Camillas illegales Brauhaus"),
    ("Höllnriderz", "Motorradgang", "Budenzauber", "Kiosk Tanke"),
    ("Gasperi-Familie", "Mafiafamilie", "Vendetta", "Rhein-Ruhr-Megaplex"),
    ("Semenszato-Fraktion", "Mafiafraktion", "Vendetta", "Rhein-Ruhr-Megaplex"),
]


def category_summary(name: str, category: str, scope: str) -> str:
    templates = {
        "Ausgehen": "Der Ort gehört laut offizieller Karte zum Nachtleben und Veranstaltungsangebot.",
        "Bars und Kneipen": "Die Karte führt den Ort als Bar, Kneipe oder Szenetreff.",
        "Einkaufen": "Der Ort ist als Einkaufs-, Handels- oder Versorgungsziel verzeichnet.",
        "Freizeit": "Der Ort ist ein Freizeit-, Sport- oder Veranstaltungsziel.",
        "Hotels": "Der Ort ist als Unterkunft oder Hotel verzeichnet.",
        "Konzerne": "Der Standort ist als Konzern- oder Industrieanlage ausgewiesen.",
        "Restaurants": "Der Ort ist als gastronomischer Betrieb verzeichnet.",
        "Sightseeing": "Der Ort ist ein markantes Kultur-, Erinnerungs- oder Besichtigungsziel.",
        "Medizin": "Der Standort dient medizinischer Versorgung oder Forschung.",
        "Verkehr": "Der Standort ist ein Verkehrsknoten des Megaplexes.",
    }
    return f"{name} liegt im Bereich {scope}. {templates.get(category, 'Der Standort ist im offiziellen Revierinventar verzeichnet')}"


def add_map_inventory(catalogue: CityCatalogue) -> tuple[list[int], list[int]]:
    detail_ids = []
    for row in MAP1.strip().splitlines():
        number, name, category, code = row.split("|")
        scope = "Hauerbrache" if code == "H" else "Bochum"
        catalogue.add_place(
            name, scope, "SR6", "rrp-map-sr6", "Revierbericht 2082 – Karte",
            f"Detailkarte Recklinghausen/Bochum, Nr. {number}",
            category=category, summary=category_summary(name, category, scope),
            map_number=int(number),
        )
        detail_ids.append(catalogue.places[name_key(name)]["properties"]["id"])

    regional_ids = []
    for number, name, scope in REGIONAL:
        catalogue.add_place(
            name, scope, "SR6", "rrp-map-sr6", "Revierbericht 2082 – Karte",
            f"Revierübersicht, Nr. {number}",
            summary=f"{name} ist auf der offiziellen Revierübersicht als besonderer Standort im Bereich {scope} markiert.",
            map_number=1000 + number,
        )
        regional_ids.append(catalogue.places[name_key(name)]["properties"]["id"])

    for category, names in ESSEN.items():
        for name in names.split(";"):
            scope = "Kettwig" if name in {"Schloss Hugenpoet", "Flughafen Essen-Mülheim"} else "Neu-Essen"
            catalogue.add_place(
                name, scope, "SR6", "rrp-map-sr6", "Revierbericht 2082 – Karte",
                f"Detailkarte Neu-Essen, {category}",
                category=category,
                summary=f"{name} ist in der offiziellen Neu-Essen-Detailkarte unter „{category}“ verzeichnet.",
                map_number=2000 + len(regional_ids),
            )
            regional_ids.append(catalogue.places[name_key(name)]["properties"]["id"])
    return detail_ids, list(dict.fromkeys(regional_ids))


def add_districts(catalogue: CityCatalogue) -> None:
    for name, summary, pages in DISTRICTS:
        catalogue.add_district_version(
            name, "SR6", "revierbericht-sr6", "Revierbericht 2082", pages, summary
        )
        catalogue.enrich_district(name, "SR6", summary)
        # The white lore label and, where available, the polygon are the
        # interaction target.  A second district circle would be redundant.
        catalogue.places[name_key(name)]["properties"]["map_marker"] = False


def polygon_center(geometry: dict) -> list[float]:
    coordinates = []

    def collect(value) -> None:
        if (
            isinstance(value, list)
            and len(value) >= 2
            and isinstance(value[0], (int, float))
            and isinstance(value[1], (int, float))
        ):
            coordinates.append((float(value[0]), float(value[1])))
            return
        if isinstance(value, list):
            for item in value:
                collect(item)

    collect(geometry.get("coordinates", []))
    if not coordinates:
        return [ANCHORS["Rhein-Ruhr-Megaplex"][1], ANCHORS["Rhein-Ruhr-Megaplex"][0]]
    west = min(point[0] for point in coordinates)
    east = max(point[0] for point in coordinates)
    south = min(point[1] for point in coordinates)
    north = max(point[1] for point in coordinates)
    return [(west + east) / 2, (south + north) / 2]


def add_municipality_profiles(catalogue: CityCatalogue) -> None:
    """Give every selectable lore municipality a non-invented city dossier."""

    districts = json.loads((CITY_DIR / "districts.geojson").read_text(encoding="utf-8"))
    aliases = {"Mülheim": "Mülheim an der Ruhr"}
    for feature in districts["features"]:
        map_name = feature["properties"].get("name", "").strip()
        if not map_name:
            continue
        dossier_name = aliases.get(map_name, map_name)
        key = name_key(dossier_name)
        if key in catalogue.places:
            continue
        summary = (
            f"{dossier_name} ist auf der offiziellen Revierübersicht als Stadt oder "
            "Kommune innerhalb des Rhein-Ruhr-Megaplexes verzeichnet."
        )
        catalogue.add_place(
            dossier_name,
            "Rhein-Ruhr-Megaplex",
            "SR6",
            "rrp-map-sr6",
            "Revierbericht 2082 – Karte",
            f"Revierübersicht: Stadt/Kommune {map_name}",
            category="Städte",
            summary=summary,
            coordinates=polygon_center(feature["geometry"]),
        )
        props = catalogue.places[key]["properties"]
        full = (
            f"{summary} Die Flächendarstellung folgt dem mit der offiziellen "
            "Shadowrun-Karte abgeglichenen Kommunenbestand. Die heutige "
            "Gemeindegeometrie dient ausschließlich als geografische Liniengrundlage; "
            "eine darüber hinausgehende eigene Stadtbeschreibung ist im zugeordneten "
            "Datenmaterial nicht eindeutig belegt."
        )
        props.update(
            {
                "map_marker": False,
                "description_kind": "Kartennachweis",
                "description_full": full,
                "description_has_more": True,
                "placement_note": "Flächenbezug der offiziellen Revierübersicht",
                "accuracy": "Lore-Kommune; heutige Grenze als Liniengrundlage",
            }
        )
        edition_data = props["edition_descriptions"]["SR6"]
        edition_data.update(
            {
                "kind": "Kartennachweis",
                "full": full,
                "hasMore": True,
                "hasExcerpt": False,
            }
        )


def add_sourcebook_places(catalogue: CityCatalogue) -> None:
    for scope, names in SR6_PLACES.items():
        for name in names.split(";"):
            catalogue.add_place(
                name, scope, "SR6", "revierbericht-sr6", "Revierbericht 2082",
                f"Rundgang durch den Plex / Für die Spielleitung: {name}",
                summary=f"{name} ist ein im Revierbericht beschriebener Schauplatz im Bereich {scope}.",
            )
    for name, scope in SR4_PLACES:
        catalogue.add_place(
            name, scope, "SR4", "rrmp-sr4", "Rhein-Ruhr-Megaplex",
            f"Brennpunkte und Ortslisten: {name}",
            summary=f"{name} ist ein im RRP-Quellenband beschriebener Treffpunkt oder Schauplatz im Bereich {scope}.",
        )


def add_people(catalogue: CityCatalogue) -> None:
    for name, role in PEOPLE_SR6:
        location = {
            "Erna": "Ernas Frittenschmiede",
            "Sandra Matschke": "Institut für Rechtsmedizin im Universitätsklinikum Düsseldorf",
            "Achim Dippels": "Der Schulhof",
            "Sahmet Dippels": "Der Schulhof",
            "Ekrem „Baba“ Bozdogan": "Schwarzer Souk",
        }.get(name)
        catalogue.add_person(
            name, "SR6", "revierbericht-sr6", "Revierbericht 2082",
            f"Personen und Machtspieler: {name}", role=role,
            summary=f"{name} wird im Revierbericht als {role} im Rhein-Ruhr-Megaplex geführt.",
            location_name=location,
        )
    for name in RRP_36:
        catalogue.add_person(
            name, "SR6", "revierbericht-sr6", "Revierbericht 2082", f"36 RRPler: {name}",
            role="Begegnungsfigur", summary=RRP_36_DETAILS[name],
        )
    for name, role in PEOPLE_SR4:
        location = {
            "Sascha Ludwig": "Leopolds", "Eddie Norg": "Grubengold",
            "Festus Klein": "Nordend", "Grummlich": "Nordend",
            "Han Sparkis": "Sparkis", "Darius Maschelski": "Autofriedhof Darius",
            "Metzler": "Grauer Flohmarkt", "Wallace": "Leopolds",
        }.get(name)
        catalogue.add_person(
            name, "SR4", "rrmp-sr4", "Rhein-Ruhr-Megaplex",
            f"Wichtige Personen im Plex: {name}", role=role,
            summary=f"{name} wird im RRP-Quellenband als {role} beschrieben.",
            location_name=location,
        )
    for name, role in GROUPS:
        location = {
            "Graue Wölfe": "Schwarzer Souk", "Füchse": "Krämerei",
            "Kinder Gaias": "Geoastrale Halde Beckstraße",
            "Desperados MC": "Duisburg", "Gelsenkirchen Pits": "Recklinghausen",
            "Haimons": "Dortmund",
        }.get(name)
        catalogue.add_person(
            name, "SR6", "revierbericht-sr6", "Revierbericht 2082",
            f"Gangs und Gruppen: {name}", role=role, entity_type="group",
            summary=f"{name} ist eine im Revierbericht belegte {role} im Rhein-Ruhr-Megaplex.",
            location_name=location,
        )


def add_supplemental_sources(catalogue: CityCatalogue) -> None:
    source_meta = {
        "Budenzauber": ("budenzauber-sr6", "Budenzauber"),
        "Vendetta": ("vendetta-sr6", "Vendetta"),
        "Domino-Effekt": ("domino-effekt-sr6", "Domino-Effekte"),
    }
    for name, scope, source_name, chapter in SUPPLEMENTAL_PLACES:
        book_id, title = source_meta[source_name]
        catalogue.add_place(
            name, scope, "SR6", book_id, title, chapter,
            summary=f"{name} ist ein konkret bespielter Schauplatz des SR6-Abenteuers „{title}“ im Bereich {scope}.",
        )
    for name, role, source_name, location in SUPPLEMENTAL_PEOPLE:
        book_id, title = source_meta[source_name]
        catalogue.add_person(
            name, "SR6", book_id, title, f"NSC-Dossier: {name}",
            role=role,
            summary=f"{name} ist im Abenteuer „{title}“ als {role} für den Rhein-Ruhr-Megaplex ausgearbeitet.",
            location_name=location,
        )
    for name, role, source_name, location in SUPPLEMENTAL_GROUPS:
        book_id, title = source_meta[source_name]
        catalogue.add_person(
            name, "SR6", book_id, title, f"Gruppendossier: {name}",
            role=role, entity_type="group",
            summary=f"{name} ist im Abenteuer „{title}“ als {role} im Rhein-Ruhr-Megaplex belegt.",
            location_name=location,
        )


def clean_source_title(path: Path) -> str:
    title = path.stem
    title = re.sub(r"^Shadowrun [1-6][DE]?\s*-\s*", "", title, flags=re.I)
    title = re.sub(r"\s*\((searchable|scan)\)\s*$", "", title, flags=re.I)
    title = re.sub(r"\s*\[[^]]+]\s*$", "", title)
    return title.strip()


def add_archive_cross_references(catalogue: CityCatalogue) -> dict:
    """Audit every unique text export and retain relevant exact-name links.

    This pass deliberately adds no marker from a mere isolated mention.  It
    enriches already verified RRP entities when a source contains at least
    four RRP-context terms.  Common district labels are excluded because city
    names in travel passages are not reliable local dossiers.
    """

    rrp_pattern = re.compile(
        r"Rhein[- ]Ruhr|Ruhrplex|Ruhrgebiet|\bRRP\b|Neu-Essen|Duisport",
        re.I,
    )
    edition_pattern = re.compile(r"Shadowrun ([1-6])(?:D|E)?(?:\b|/)", re.I)
    seen_hashes = set()
    audited = relevant = imported_files = links = 0
    registered = {(book["edition"], book["title"]): book["id"] for book in catalogue.books}

    place_lookup = {
        props["name"].casefold(): props
        for props in (feature["properties"] for feature in catalogue.places.values())
        if props["category"] != "Bezirke" and len(props["name"]) >= 6
    }
    person_lookup = {
        person["name"].casefold(): person
        for person in catalogue.people.values()
        if len(person["name"]) >= 6
    }
    names = sorted(set(place_lookup) | set(person_lookup), key=len, reverse=True)

    import hashlib

    for path in CORPUS.rglob("*.txt"):
        try:
            payload = path.read_bytes()
        except OSError:
            continue
        digest = hashlib.sha256(payload).digest()
        if digest in seen_hashes:
            continue
        seen_hashes.add(digest)
        audited += 1
        text = payload.decode("utf-8", errors="ignore")
        context_hits = len(rrp_pattern.findall(text))
        if context_hits < 4:
            continue
        match = edition_pattern.search(path.as_posix())
        if not match:
            continue
        edition = f"SR{match.group(1)}"
        relevant += 1
        lowered = text.casefold()
        # CPython's substring search is considerably faster for this workload
        # than a single enormous alternation regex over multi-megabyte books.
        matches = {name for name in names if name in lowered}
        if not matches:
            continue
        title = clean_source_title(path)
        book_id = registered.get((edition, title))
        if not book_id:
            stem = re.sub(r"[^a-z0-9]+", "-", title.casefold()).strip("-")[:60]
            book_id = f"archive-{edition.casefold()}-{stem}"
            registered[(edition, title)] = book_id
            catalogue.books.append({"id": book_id, "title": title, "edition": edition})
        file_links = 0
        for key in matches:
            props = place_lookup.get(key)
            if props and edition not in props["editions"]:
                catalogue.add_place(
                    props["name"], props["detail_map"], edition, book_id, title,
                    f"RRP-Kontextverweis: {props['name']}",
                )
                links += 1
                file_links += 1
            elif props and not any(source["bookId"] == book_id for source in props["sources"]):
                catalogue.add_place(
                    props["name"], props["detail_map"], edition, book_id, title,
                    f"RRP-Kontextverweis: {props['name']}",
                )
                links += 1
                file_links += 1
            person = person_lookup.get(key)
            if person and not any(source["bookId"] == book_id for source in person["sources"]):
                catalogue.add_person(
                    person["name"], edition, book_id, title,
                    f"RRP-Kontextverweis: {person['name']}",
                    entity_type=person["entity_type"],
                )
                links += 1
                file_links += 1
        if file_links:
            imported_files += 1
    return {
        "unique_text_exports": audited,
        "rrp_context_files": relevant,
        "files_with_imported_links": imported_files,
        "entity_source_links": links,
    }


def normalized_contains(text: str, name: str) -> bool:
    aliases = [name]
    aliases.extend(part.strip() for part in re.split(r"/| alias ", name, flags=re.I) if len(part.strip()) >= 4)
    return any(re.search(rf"(?<!\\w){re.escape(alias)}(?!\\w)", text, re.I) for alias in aliases)


def add_cross_edition_references(catalogue: CityCatalogue) -> None:
    metadata = {
        "SR1": ("dids-sr1", "Deutschland in den Schatten"),
        "SR2": ("dids-sr2", "Deutschland in den Schatten"),
        "SR3": ("dids2-sr3", "Deutschland in den Schatten II"),
        "SR4": ("rrmp-sr4", "Rhein-Ruhr-Megaplex"),
        "SR5": ("datapuls-adl-sr5", "Datapuls: ADL"),
        "SR6": ("revierbericht-sr6", "Revierbericht 2082"),
    }
    texts = {
        edition: path.read_text(encoding="utf-8", errors="ignore")
        for edition, path in CORE_FILES.items() if path.exists()
    }
    for feature in list(catalogue.places.values()):
        props = feature["properties"]
        for edition, text in texts.items():
            if edition in props["editions"] or not normalized_contains(text, props["name"]):
                continue
            book_id, title = metadata[edition]
            catalogue.add_place(
                props["name"], props["detail_map"], edition, book_id, title,
                f"RRP-Kapitel: {props['name']}",
            )
    for person in list(catalogue.people.values()):
        for edition, text in texts.items():
            if edition in person["editions"] or not normalized_contains(text, person["name"]):
                continue
            book_id, title = metadata[edition]
            catalogue.add_person(
                person["name"], edition, book_id, title,
                f"RRP-Kapitel: {person['name']}",
                entity_type=person["entity_type"],
            )
    # The first German city chapter was reprinted for SR2.  Preserve both
    # edition switches for identical material as agreed with the user.
    for feature in list(catalogue.places.values()):
        if "SR1" in feature["properties"]["editions"] and "SR2" not in feature["properties"]["editions"]:
            catalogue.add_place(
                feature["properties"]["name"], feature["properties"]["detail_map"],
                "SR2", "dids-sr2", "Deutschland in den Schatten",
                f"RRP-Kapitel (identischer SR1/SR2-Bestand): {feature['properties']['name']}",
            )
    for person in list(catalogue.people.values()):
        if "SR1" in person["editions"] and "SR2" not in person["editions"]:
            catalogue.add_person(
                person["name"], "SR2", "dids-sr2", "Deutschland in den Schatten",
                f"RRP-Kapitel (identischer SR1/SR2-Bestand): {person['name']}",
                entity_type=person["entity_type"],
            )


def write_labels_and_boundaries(catalogue: CityCatalogue) -> None:
    labels = []
    for name, _, _ in DISTRICTS:
        props = catalogue.places[name_key(name)]["properties"]
        lat, lon = ANCHORS[name]
        labels.append({"name": name, "lat": lat, "lon": lon, "type": "district", "entity_id": props["id"]})
    write_json(CITY_DIR / "labels.json", labels)

    district_path = CITY_DIR / "districts.geojson"
    districts = json.loads(district_path.read_text(encoding="utf-8"))
    municipality_aliases = {"Mülheim": "Mülheim an der Ruhr"}
    for feature in districts["features"]:
        name = feature["properties"].get("name", "")
        dossier = municipality_aliases.get(name, name)
        item = catalogue.places.get(name_key(dossier))
        if item:
            feature["properties"]["entity_id"] = item["properties"]["id"]
            feature["properties"]["description_preview"] = item["properties"]["description_preview"]
            feature["properties"]["description_full"] = item["properties"]["description_full"]
            feature["properties"]["editions"] = item["properties"]["editions"]
            feature["properties"]["sources"] = item["properties"]["sources"]
        feature["properties"]["boundary_review_status"] = "contextual"
        feature["properties"]["boundary_review_label"] = "Offizielle RRP-Karte abgeglichen; heutige Gemeindegeometrie nur als Liniengrundlage"
    write_json(district_path, districts)


def write_atlas(detail_ids: list[int], regional_ids: list[int]) -> None:
    path = CITY_DIR / "atlas.json"
    atlas = json.loads(path.read_text(encoding="utf-8"))
    by_key = {entry["key"]: entry for entry in atlas}
    by_key["rrm-recklinghausen-bochum"]["markerIds"] = detail_ids
    by_key["rrm-revieruebersichten"]["markerIds"] = regional_ids
    write_json(path, atlas)


def main() -> None:
    catalogue = CityCatalogue(
        CITY_ID, "Rhein-Ruhr-Megaplex", ANCHORS["Rhein-Ruhr-Megaplex"], ANCHORS, BOOKS
    )
    rrp_preview = (
        "Der Rhein-Ruhr-Megaplex ist 2082 ein zusammengewachsener Ballungsraum von "
        "Bonn bis Wesel und vom Niederrhein bis Dortmund und Hagen."
    )
    catalogue.set_city_profile(
        rrp_preview,
        rrp_preview + (
            " Alte Städte, Industrieachsen, Häfen, Brachen und Bergwerke bilden einen "
            "dichten urbanen Korridor. Saeder-Krupp und Neu-Essen prägen das Machtgefüge, "
            "während Kommunalpolitik, weitere Megakonzerne, Syndikate, Gangs und autonome "
            "Schattenräume um Einfluss ringen."
        ),
        {
            "SR1": city_edition(
                "SR1", "dids-sr1", "Deutschland in den Schatten", "Rhein-Ruhr-Kapitel",
                "Das Rhein-Ruhr-Gebiet ist ein aus Industrie, Städten und Verkehrsachsen zusammengewachsener Sprawl.",
                "Der frühe Quellenstand beschreibt das Rhein-Ruhr-Gebiet als aus Industrie, Städten und Verkehrsachsen zusammengewachsenen Sprawl. Konzernmacht, Umweltzerstörung, Arbeitermilieus und Schattenmärkte liegen dicht beieinander.",
            ),
            "SR4": city_edition(
                "SR4", "rrmp-sr4", "Rhein-Ruhr-Megaplex", "Gesamtprofil des Plexes",
                "Der Rhein-Ruhr-Megaplex ist ein polyzentrischer Industrieraum unter starkem Einfluss Saeder-Krupps.",
                "Der SR4-Stadtband beschreibt einen polyzentrischen Industrieraum aus Kommunen, Konzernstandorten und Brachen. Saeder-Krupp, Neu-Essen, organisierte Kriminalität und lokale Schattennetzwerke bestimmen das Machtgefüge.",
            ),
            "SR6": city_edition(
                "SR6", "revierbericht-sr6", "Revierbericht 2082", "Rundgang durch den Plex, S. 23–93",
                rrp_preview,
                rrp_preview + " Der Revierbericht gliedert ihn in regionale Stadtverbünde, besondere Bezirke wie Neu-Essen, Hauerbrache, Schwarzer Souk und Seelieviertel sowie eigene Räume unter Tage.",
            ),
        },
    )
    detail_ids, regional_ids = add_map_inventory(catalogue)
    add_districts(catalogue)
    add_municipality_profiles(catalogue)
    add_sourcebook_places(catalogue)
    add_people(catalogue)
    add_supplemental_sources(catalogue)
    add_cross_edition_references(catalogue)
    audit = add_archive_cross_references(catalogue)
    catalogue.finish(
        2082,
        "Vollinventar des Rhein-Ruhr-Megaplexes: offizielle Revier- und Detailkarten, Lore-Regionen, Neu-Essen, Orte, Personen, Gangs und Gruppen sowie gemeinsame Editionsdossiers aus SR1–SR6.",
        bounds=[[50.70, 6.10], [52.05, 8.20]],
        zoom=8,
    )
    write_labels_and_boundaries(catalogue)
    write_atlas(detail_ids, regional_ids)
    write_json(CITY_DIR / "source-audit.json", audit)


if __name__ == "__main__":
    main()
