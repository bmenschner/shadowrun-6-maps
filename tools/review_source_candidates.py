#!/usr/bin/env python3
"""Triage extracted source candidates against published city entities.

This tool is deliberately conservative.  It automatically resolves exact
matches and obvious extraction noise, but it never promotes an uncertain name
to published lore.  Remaining candidates are written to a compact manual
review queue below the ignored ``source-data`` directory.
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "source-data/import-candidates.jsonl"
DECISIONS = ROOT / "source-data/candidate-decisions.jsonl"
REVIEW = ROOT / "source-data/candidate-manual-review.jsonl"
SUMMARY = ROOT / "source-data/candidate-decisions-summary.json"

SECTION_WORDS = re.compile(
    r"\b(?:"
    r"access|adventure|after(?:math)?|angebot|anreise|atmosphäre|auf einen blick|"
    r"ausgang(?:spunkt)?|background|basic information|behind the scenes|"
    r"beschreibung|briefing|briefs?|chapter|characters?|charaktere|"
    r"conclusion|contact|contacts|context|credits?|daumenschrauben|"
    r"debugging|dispositions?|equipment|epilogue|ergebnis|failure|"
    r"game information|geography|demographics|geschichte|getting around|"
    r"hinter den kulissen|hintergrund|history|im überblick|index|info|"
    r"information|intro(?:duction)?|karma|keine panik|legwork|"
    r"mission|moving targets|nachforschungen|objectives?|option|overview|"
    r"plot|production staff|reporting back|rules?|scan this|scenes?|"
    r"security|setup|spielwerte|street legends|system facts|table|"
    r"tell it to them straight|the setting|timeline|travel|"
    r"überblick|waffen|weapons|wie geht es weiter"
    r")\b",
    re.I,
)
GENERIC_ROLE = re.compile(
    r"\b(?:armor(?:er)?|combat mage|contact|decker|detective|diplomatic|"
    r"fighter|guard|hacker|human|mage|manager|negotiator|npc|ork|"
    r"professional|rigger|runner|samurai|shaman|street artist|"
    r"street racer|trooper|troll|unit|variants?)\b",
    re.I,
)
CORPORATE_WORDS = re.compile(
    r"\b(?:ag|corp(?:oration)?|gmbh|group|inc(?:orporated)?|industr(?:y|ies)|"
    r"plc|systems?|technolog(?:y|ies))\b",
    re.I,
)
SENTENCE_FRAGMENT = re.compile(
    r"\b(?:am|an|and|auf|aus|bei|beim|der|die|ein|eine|für|im|in|mit|"
    r"nach|of|the|to|und|von|vor|when|with|wurde|zur)\b",
    re.I,
)
BROKEN_OCR = re.compile(
    r"(?:[A-Z]{1,3}\s+){3,}[A-Z]{1,3}|"
    r"\b(?:bevonn?|bri?tan|fr?hter|ihr\s+be|m?t\s+be|tft|yllittie)\b",
    re.I,
)
FOCUSED_WORKS = {
    "boston": {
        "sr5-gefahr-in-boston", "sr5-lockdown",
        "sr5-shadowrun-chronicles-boston-adventures", "sr5-sperrzone-boston",
    },
    "chicago": {
        "sr2-bug-city", "sr4-feral-cities", "sr5-mission-chicago",
        "sr5-abenteuerband-schatten-uber-chicago",
        "sr5-anarchy-chicago-chaos",
    },
    "frankfurt": {"sr2-chrom-dioxin", "sr5-datapuls-frankfurt"},
    "hong-kong": {"sr4-runner-havens", "sr5-hong-kong-neon-contrails-2050"},
    "london": {"sr1-london-sourcebook", "sr5-mission-london", "sr5-srmc-london-falling"},
    "muenchen": {"sr4-munchen-noir", "sr6-datapuls-munchen"},
    "san-francisco": {
        "sr2-california-free-state",
        "sr5-shadows-in-focus-city-by-shadow-san-francisco-metroplex",
    },
    "cheyenne": {
        "sr5-shadows-in-focus-city-by-shadow-cheyenne",
        "sr5-mission-sioux-nation",
        "sr5-shadows-in-focus-sioux-nation",
    },
    "karlsruhe": {"sr5-datapuls-karlsruhe"},
    "new-orleans": {
        "sr2-target-smuggler-havens",
        "sr6-shadows-in-focus-easy-come-easy-go-new-orleans",
    },
    "paris": {"sr3-shadows-of-europe", "sr6-final-bets-paris-grand-tour"},
    "montreal": {"sr3-shadows-of-north-america"},
    "neo-tokio": {"sr3-shadows-of-asia", "sr4-corporate-enclaves"},
    "washington-fdc": {"sr6-cutting-black"},
    "los-angeles": {"sr2-california-free-state", "sr4-corporate-enclaves"},
    "bogota": {"sr4-war", "sr4-fronteinsatz"},
    "lagos": {"sr4-feral-cities", "sr4-krisenzonen"},
    "detroit": {"sr2-target-ucas", "sr6-cutting-black"},
    "atlanta": {
        "sr1-the-neo-anarchist-s-guide-to-north-america",
        "sr6-cutting-black",
    },
    "portland": {"sr2-tir-tairngire", "sr2-die-lander-der-verheiung"},
    "wien": {"sr2-walzer-punks-schwarzes-ice", "sr5-datapuls-osterreich"},
    "kairo": {"sr6-risk-rewards-cairo-campaign"},
    "metropole": {"sr5-shadows-in-focus-city-by-shadow-metropole"},
    "butte": {"sr5-shadows-in-focus-city-by-shadow-butte"},
    "casablanca-rabat": {
        "sr5-shadows-in-focus-casablanca-rabat",
        "sr5-shadows-in-focus-morocco",
    },
    "vladivostok": {
        "sr2-target-smuggler-havens",
        "sr5-enhanced-fiction-the-vladivostok-gauntlet",
    },
    "zuerich": {
        "sr2-chrom-dioxin", "sr2-schattenlichter", "sr5-datapuls-schweiz",
    },
    "leipzig-halle": {
        "sr3-deutschland-in-den-schatten-ii",
        "sr4-reisefuhrer-in-die-deutschen-schatten",
        "sr5-auf-dunklen-pfaden",
    },
    "quebec": {"sr3-shadows-of-north-america", "sr3-nordamerika-in-den-schatten"},
    "bremen": {"sr1-deutschland-in-den-schatten", "sr3-deutschland-in-den-schatten-ii"},
    "hannover": {"sr4-machtspiele-handbuch-fur-spione", "sr5-datapuls"},
    "istanbul": {"sr4-runner-havens", "sr5-cutting-aces", "sr5-mit-tricks-und-finesse"},
    "tenochtitlan": {
        "sr2-aztlan", "sr3-lateinamerika-in-den-schatten-v1-0",
        "sr3-shadows-of-latin-america-v1-2",
    },
    "stuttgart": {
        "sr3-deutschland-in-den-schatten-ii",
        "sr4-reisefuhrer-in-die-deutschen-schatten",
        "sr5-datapuls",
    },
    "caracas": {
        "sr4-shadowrun-4d-geisterkartelle", "sr4-ghost-cartels",
        "sr4-dawn-of-the-artifacts-5-artifacts-unbound",
    },
    "st-louis": {"sr1-the-neo-anarchist-s-guide-to-north-america"},
    "santiago": {"sr3-shadows-of-latin-america-v1-2", "sr3-lateinamerika-in-den-schatten-v1-0"},
    "sydney": {"sr3-target-awakened-lands", "sr3-erwachte-lander", "sr5-gestohlene-seelen"},
    "austin": {"sr2-lone-star"},
    "dublin": {"sr2-tir-na-nog"},
    "dubai": {"sr4-corporate-enclaves", "sr4-boardroom-backstabs-1-damage-control"},
    "las-vegas": {"sr4-the-twilight-horizon", "sr5-gestohlene-seelen"},
    "singapur": {"sr3-shadows-of-asia", "sr5-blutige-geschafte", "sr6-margin-calls-corporate-world-post-dis-plot"},
    "kapstadt": {"sr4-vice", "sr4-unterwelten", "sr5-megakons-2078"},
    "nuernberg": {"sr4-reisefuhrer-in-die-deutschen-schatten"},
    "baltimore": {"sr4-conspiracy-theories", "sr4-corporate-intrigue"},
    "nairobi": {"sr4-corporate-enclaves", "sr4-spy-games", "sr4-vice"},
    "manaus": {"sr3-shadows-of-latin-america-v1-2"},
    "bruessel": {"sr3-shadows-of-europe"},
    "perth": {"sr3-target-awakened-lands", "sr5-lifestyle-2080", "sr5-no-future", "sr5-megakons-2078"},
    "sarajevo": {"sr4-dawn-of-the-artifacts-3-darkest-hour"},
    "vancouver": {"sr3-shadows-of-north-america", "sr3-nordamerika-in-den-schatten"},
    "san-diego": {"sr3-shadows-of-latin-america-v1-2", "sr3-lateinamerika-in-den-schatten-v1-0"},
    "lima": {"sr3-shadows-of-latin-america-v1-2", "sr5-lifestyle-2080"},
    "buenos-aires": {"sr3-shadows-of-latin-america-v1-2"},
    "havanna": {"sr5-hard-targets", "sr5-harte-ziele", "sr4-vice"},
    "dallas-fort-worth": {
        "sr1-the-neo-anarchist-s-guide-to-north-america",
        "sr2-nordamerika-quellenbuch", "sr5-gestohlene-seelen",
    },
    "prag": {"sr3-shadows-of-europe"},
    "miami": {"sr4-vice", "sr4-10-mercs", "sr5-gestohlene-seelen"},
    "teheran": {"sr3-survival-of-the-fittest"},
    "melbourne": {"sr3-target-awakened-lands"},
    "salt-lake-city": {"sr1-native-american-nations-volume-one"},
    "manila": {"sr3-shadows-of-asia", "sr2-cyberpirates", "sr2-cyberpiraten"},
    "johannesburg": {"sr5-better-than-bad"},
    "phoenix": {"sr1-the-neo-anarchist-s-guide-to-north-america"},
    "brisbane": {"sr3-target-awakened-lands"},
    "bangkok": {"sr4-state-of-the-art-2073", "sr4-99-bottles"},
}

# Explicit editorial resolutions for OCR aliases, mistranslations and
# candidates whose extractor assigned the wrong entity type.  Target names
# refer to the canonical dossiers produced by build_wave1_city_packages.py.
CURATED_TARGETS = {
    "boston:areportongatewaytransportation:place": ["Salem-Lab 620 Gateway"],
    "boston:aztechnology:place": ["Aztechnology Swampscott High School"],
    "boston:bruinseishockeynhl:person": ["Boston Bruins"],
    "boston:bruinsicehockeynhl:person": ["Boston Bruins"],
    "boston:cannonslacrosseanejodiliga:group": ["Boston Cannons"],
    "boston:cannonsstickballanejodileague:group": ["Boston Cannons"],
    "boston:celticsbasketballnba:person": ["Boston Celtics"],
    "boston:derschwarzebasar:place": ["Der Schwarze Basar"],
    "boston:diepyramidemitt:place": ["Die Pyramide"],
    "boston:diesquares:place": ["Die Squares"],
    "boston:docwagon:person": ["Massachusetts General Hospital"],
    "boston:docwagon:place": ["Massachusetts General Hospital"],
    "boston:frankfurterbankenverein:place": ["FBV Boston – Nachtmeister-Tower"],
    "boston:knighterrant:place": ["Knight Errant Marblehead High School"],
    "boston:milesfenmore:place": ["Miles Fenmore"],
    "boston:projektorionhorizon:group": ["Project Orion"],
    "boston:redsoxbaseballnabl:group": ["Boston Red Sox"],
    "boston:revere:group": ["Knight Errant Revere Station"],
    "boston:revolutionfootballsoccermls:group": ["New England Revolution"],
    "boston:senseisnacksshiawase:person": ["Sensei Snacks F&E-Labore"],
    "boston:senseisnacksshiawase:place": ["Sensei Snacks F&E-Labore"],
    "boston:themafia:group": ["Boston Mafia"],
    "boston:yakuza:group": ["Boston Yakuza"],
    "chicago:coreparksgrantpark:place": ["Grant Park"],
    "chicago:malonygovernmentcomplex:person": ["Malony Government Complex"],
    "chicago:preservationsociety:place": ["Astral Space Preservation Society"],
    "chicago:searstowerchicagoucas:place": ["Sears Tower Alchera"],
    "chicago:searstowerchicago:place": ["Sears Tower Alchera"],
    "chicago:theastralspacepreservationsocietyasps:place": ["Astral Space Preservation Society"],
    "chicago:trumantechnologies:place": ["Truman Tower"],
    "chicago:tsubayakuzalieutenantkendoinstructor:group": ["Tsuba"],
    "chicago:zamboniformermafiahitmancurrentfixer:group": ["Zamboni"],
    "frankfurt:bezirkaschaffenburg:place": ["Aschaffenburg"],
    "frankfurt:bezirkbergstrabe:place": ["Bergstraße"],
    "frankfurt:bezirkbiblis:place": ["Biblis"],
    "frankfurt:bezirkdarmstadt:place": ["Darmstadt"],
    "frankfurt:bezirkfrankfurtcity:place": ["Frankfurt-City"],
    "frankfurt:flughafen:place": ["Frankfurt Airport"],
    "frankfurt:hafendb:place": ["Aschaffenburger Hafen"],
    "frankfurt:hauptquartierderagc:place": ["Hauptquartier der AG Chemie"],
    "frankfurt:heidelbergschwabenheimer:place": ["Asthenologica-Trainingszentrum"],
    "frankfurt:ruprechtkarluniversitat:place": ["Ruprecht-Karls-Universität"],
    "hong-kong:citygatecomplexlantauisland:place": ["CityGate Complex"],
    "hong-kong:dantesinfernohongkong:place": ["Dante’s Inferno Hong Kong"],
    "hong-kong:dynastymansionsthroughouthongkong:place": ["Dynasty Mansions"],
    "hong-kong:executivecouncilchairmandengsaikan:person": ["Deng Sai-Kan"],
    "hong-kong:executivecouncilmemberwilliamwu:person": ["William Wu"],
    "hong-kong:executivecouncilmemberyijingze:place": ["Yi Jing-Ze"],
    "hong-kong:horizongroup:group": ["Horizon Group Hongkong"],
    "hong-kong:masstransitrailway:person": ["Mass Transit Railway"],
    "hong-kong:thereddragontriad:group": ["Red Dragon Association"],
    "hong-kong:thedrunkenmonkeysoutherncoast:place": ["The Drunken Monkey"],
    "hong-kong:wanchai:place": ["Wanchai-Causeway"],
    "hong-kong:wujicrewblackdolphins:group": ["Wuji Crew"],
    "hong-kong:wuxingskytowersoutherncoastaberdeen:place": ["Wuxing Skytower"],
    "hong-kong:wuxingskytowers:place": ["Wuxing Skytower"],
    "hong-kong:yokogawacorporation:place": ["Yokogawa Corporation – Hongkong"],
    "london:artholomewjohnson:person": ["Bartholomew Johnson"],
    "london:dasbritischemuseum:place": ["The British Museum"],
    "london:doctorrichardpelletiere:person": ["Dr. Richard Pelletiere"],
    "london:doktorpelletiereabenteuer:person": ["Dr. Richard Pelletiere"],
    "london:doktorrichardpelletiere:person": ["Dr. Richard Pelletiere"],
    "london:edwardsymingtonmarquisofsherwood:place": ["Edward Symington"],
    "london:gloustercourtofftowerhill:place": ["Glouster Court"],
    "london:insideangeltowers:place": ["Angel Towers"],
    "london:linkclub:place": ["Link Club London"],
    "london:magestone:group": ["London Magestone"],
    "london:magestone:place": ["London Magestone"],
    "london:neonetteam:group": ["NeoNET-Team"],
    "london:nigelpatterson:place": ["Nigel Patterson"],
    "london:oxfordstreettheunderplex:place": ["Oxford Street Underplex Access"],
    "london:sasteam:group": ["SAS-Team"],
    "london:thetemplars:place": ["The Templars"],
    "london:trcteam:group": ["TRC-Team"],
    "muenchen:bmwsaederkrupp:place": ["BMW Stammwerk"],
    "muenchen:garchinggrunwald:place": ["Garching", "Grünwald"],
    "muenchen:mairportgmbh:place": ["M-Airport"],
    "muenchen:renrakuarkologieeuropaharlaching:place": ["Renraku Arkologie Europa"],
    "muenchen:renrakueuropa:place": ["Renraku Arkologie Europa"],
    "muenchen:theatinerstraeschrannenhalle:place": ["Theatinerstraße", "Schrannenhalle"],
    "muenchen:thun:group": ["The Grimms"],
    "atlanta:blackmarket:place": ["Atlanta Black Market"],
    "atlanta:linkclub:place": ["Link Club Atlanta"],
    "bogota:deraztechnologybusinesscomplex:place": ["Aztechnology Business Complex"],
    "bogota:derflughafeneldorado:place": ["El Dorado Airport"],
    "bogota:diepemexarkologie:place": ["Pemex Arcology"],
    "bogota:flughafenguaymaral:place": ["Guaymaral Airport"],
    "bogota:heiligeslebenheiligertod:group": ["Sacred Life, Sacred Death"],
    "bogota:pontificalxavierianuniversity:place": ["Pontificia Universidad Javeriana"],
    "cheyenne:airport:place": ["Cheyenne Regional Airport"],
    "cheyenne:andbrassclub:place": ["Copper and Brass Club"],
    "cheyenne:ares:place": ["Ares District HQ Cheyenne"],
    "cheyenne:cheyennecityhall:person": ["Cheyenne City Hall"],
    "cheyenne:cheyenneregional:place": ["Cheyenne Regional Airport"],
    "cheyenne:mct:place": ["MCT Cheyenne / Elk-Sedge Systems"],
    "cheyenne:saederkrupp:place": ["Saeder-Krupp Cheyenne"],
    "cheyenne:shiawase:place": ["Shiawase Cheyenne Headquarters"],
    "lagos:apapamedicalcenterapapa:person": ["Apapa Medical Center"],
    "lagos:theportonovoluxuryhotelapapa:place": ["Porto Novo Luxury Hotel"],
    "lagos:thethreefriendslagosmainland:place": ["The Three Friends"],
    "los-angeles:amalgamatedstudios:person": ["Amalgamated Studios"],
    "los-angeles:angelicentertainment:person": ["Angelic Entertainment"],
    "los-angeles:downtown:place": ["Downtown Los Angeles"],
    "los-angeles:horizongroup:group": ["Horizon Group Los Angeles"],
    "los-angeles:linkclub:place": ["Link Club Los Angeles"],
    "los-angeles:losangelesstrahlungszonesanonofre:group": ["San Onofre Radiation Zone"],
    "los-angeles:universityofcalifornialosangeles:place": ["UCLA"],
    "neo-tokio:bunkyo:group": ["Bunkyō"],
    "neo-tokio:chosunalleysubtokyo:group": ["Chosun Alley"],
    "neo-tokio:kanda:group": ["Kanda"],
    "paris:anisesolange:place": ["Anise Solange"],
    "paris:creteilbtland:place": ["Créteil"],
    "paris:lequartierlatin:place": ["Quartier Latin"],
    "paris:linkclub:place": ["Link Club Paris"],
    "paris:mcthtrteam:group": ["MCT HTR Team Paris"],
    "paris:thefrenchnationallibrary:place": ["Bibliothèque François Mitterrand"],
    "paris:thejoygirl:place": ["Au Trésor des Belles"],
    "paris:thevory:group": ["Paris Vory"],
    "portland:aresmacrotechnologiestirtairngire:person": ["Ares Macrotechnologies Tír Tairngire"],
    "portland:knighterranttirtairngire:person": ["Knight Errant Tír Tairngire"],
    "portland:patogradys:person": ["Pat O’Grady’s"],
    "portland:portlandexecutel:person": ["Portland Executel"],
    "portland:westslopeinn:person": ["West Slope Inn"],
    "san-francisco:ancients:group": ["Ancients San Francisco"],
    "san-francisco:mafia:group": ["San Francisco Mafia"],
    "san-francisco:neonet:place": ["NeoNET San Francisco"],
    "san-francisco:wuxing:place": ["Wuxing San Francisco"],
    "san-francisco:yakuza:group": ["San Francisco Yakuza"],
    "wien:brimstone:place": ["Brimstone Memorial Battery"],
    "kairo:althaaniamarket:place": ["Al-Hayat Althaania Market"],
    "kairo:ramsesstationtrainstation:place": ["Ramses Station"],
    "butte:vory:group": ["Butte Vory"],
    "casablanca-rabat:royalfamily:group": ["Royal Family of Morocco"],
    "vladivostok:thevoryvzakone:group": ["Vladivostok Vory v Zakone"],
    "vladivostok:voryvzakone:group": ["Vladivostok Vory v Zakone"],
    "vladivostok:theyakuza:group": ["Vladivostok Yakuza"],
    "zuerich:imswissmetrobahnhofkonnen:place": ["SwissMetro-Bahnhof Zürich-West"],
    "leipzig-halle:gargariorganizatsiwestlichevory:group": ["Gargari-Organizatsi Leipzig-Halle"],
    "quebec:democratesmondains:person": ["Démocrates Mondains"],
    "quebec:democratesmondains:place": ["Démocrates Mondains"],
    "quebec:derquebeccitymetroplex:place": ["Québec City Metroplex"],
    "hannover:drehkreuzderpolitik:place": ["Flughafen Hannover-Langenhagen"],
    "hannover:enricozorn:place": ["Enrico Zorn"],
    "hannover:staatlichepolizei:group": ["Staatliche Polizei Hannover"],
    "hannover:voryvzakone:group": ["Hannover Vory v Zakone"],
    "hannover:ethnischeminderheitenundgangs:group": ["Graue Wölfe Hannover"],
    "tenochtitlan:nationalpalace:person": ["National Palace"],
    "tenochtitlan:cerocero:person": ["Cero Cero"],
    "caracas:rayoorkgangboss:person": ["Rayo"],
    "sydney:voryvzakone:group": ["Sydney Vory v Zakone"],
    "sydney:diegriechischemafia:group": ["Sydney Greek Mafia"],
    "dublin:diepolizei:group": ["Tír na nÓg Police"],
    "dublin:streetgangs:place": ["Dublin Street Gangs"],
    "las-vegas:linkclub:place": ["Link Club Las Vegas"],
    "las-vegas:thefreemontstreetexperience:place": ["Fremont Street Experience"],
    "lima:diebarlimaperu:place": ["The Bar Lima"],
    "lima:thebarlimaperu:place": ["The Bar Lima"],
    "havanna:internationalairport:place": ["Havana International Airport"],
    "havanna:aeropuertointernacional:place": ["Havana International Airport"],
    "havanna:vory:group": ["Havanna Vory"],
    "dallas-fort-worth:linkclub:place": ["Link Club Dallas/Fort Worth"],
    "miami:linkclub:place": ["Link Club Miami"],
    "melbourne:theyakuza:group": ["Melbourne Yakuza"],
    "melbourne:voryvzakone:group": ["Melbourne Vory v Zakone"],
    "brisbane:tanamyreresources:person": ["Tanamyre Resources Brisbane"],
    "bangkok:yellowlotustriad:group": ["Yellow Lotus Triad Bangkok"],
    "austin:lonestar:group": ["Lone Star Austin"],
    "vancouver:kyuuseimedical:person": ["Kyuusei Medical"],
    "vancouver:pacificcyberneticsincorporated:person": ["Pacific Cybernetics Incorporated"],
    "san-diego:dersandiegotijuanasprawl:place": ["San Diego-Tijuana Lore-Raum"],
    "san-diego:sandiegotijuanasprawl:place": ["San Diego-Tijuana Lore-Raum"],
    "santiago:nuevosantiagoand:place": ["Nuevo Santiago Lore-Raum"],
    "nairobi:nairobikenia:place": ["Nairobi Lore-Raum"],
    "nairobi:nairobikenya:place": ["Nairobi Lore-Raum"],
}

# These city queues were read against their local source contexts. Once
# the explicit targets above and normalised existing dossiers are resolved,
# the remaining candidates are headings, rules, OCR fragments, generic
# categories or entities outside the map scope.
FINAL_REVIEW_CITIES = {
    "boston", "chicago", "frankfurt", "hong-kong", "london", "muenchen",
    "atlanta", "bogota", "cheyenne", "detroit", "karlsruhe", "lagos",
    "los-angeles", "montreal", "neo-tokio", "new-orleans", "paris",
    "portland", "san-francisco", "washington-fdc", "wien",
    "bremen", "butte", "casablanca-rabat", "hannover", "istanbul", "kairo",
    "leipzig-halle", "metropole", "quebec", "stuttgart", "tenochtitlan",
    "vladivostok", "zuerich",
    "austin", "baltimore", "bangkok", "brisbane", "bruessel",
    "buenos-aires", "caracas", "dallas-fort-worth", "dubai", "dublin",
    "havanna", "johannesburg", "kapstadt", "las-vegas", "lima", "manaus",
    "manila", "melbourne", "miami", "nairobi", "nuernberg", "perth",
    "phoenix", "prag", "salt-lake-city", "san-diego", "santiago", "sarajevo",
    "singapur", "st-louis", "sydney", "teheran", "vancouver",
}
PLACE_SIGNAL = re.compile(
    r"\b(?:academy|airport|arcology|arkologie|arena|bar|bazaar|bezirk|"
    r"cafe|café|casino|city|clinic|club|complex|district|dock|factory|"
    r"garden|grocery|harbor|hafen|haus|heath|hospital|hotel|labor|lab|"
    r"market|museum|park|platz|pub|restaurant|school|shop|sprawl|"
    r"station|street|straße|teahouse|temple|tower|university|"
    r"universität|viertel|zone)\b",
    re.I,
)
GROUP_SIGNAL = re.compile(
    r"\b(?:ancients|brigade|brotherhood|collective|council|family|gang|"
    r"gumi|horde|mafia|movement|order|syndicate|triad|templars|union|"
    r"vory|yakuza)\b",
    re.I,
)


def fold(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    return value.encode("ascii", "ignore").decode("ascii").casefold()


def key(value: str) -> str:
    value = re.sub(r"\([^)]*\)", " ", value)
    value = re.sub(r"^(?:the|das|der|die)\s+", "", fold(value))
    return re.sub(r"[^a-z0-9]+", "", value)


def load_entities(city_id: str) -> dict[str, list[dict]]:
    manifest = json.loads((ROOT / f"data/{city_id}/manifest.json").read_text(encoding="utf-8"))
    city_dir = ROOT / "data" / city_id
    places = json.loads((city_dir / manifest["files"]["places"]).read_text(encoding="utf-8"))["features"]
    people = json.loads((city_dir / manifest["files"]["people"]).read_text(encoding="utf-8"))
    result: dict[str, list[dict]] = {}
    for feature in places:
        props = feature["properties"]
        for name in [props["name"], *(props.get("aliases") or [])]:
            result.setdefault(key(name), []).append(
                {"kind": "place", "id": props["global_id"], "name": props["name"]}
            )
    for person in people:
        kind = "group" if person.get("entity_type") == "group" else "person"
        for name in [person["name"], *(person.get("aliases") or [])]:
            result.setdefault(key(name), []).append(
                {"kind": kind, "id": person["global_id"], "name": person["name"]}
            )
    return result


def noise_reason(candidate: dict) -> str | None:
    name = candidate["rawName"].strip()
    words = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿÄÖÜäöüß0-9'’&-]+", name)
    letters = [char for char in name if char.isalpha()]
    upper_ratio = (
        sum(char.isupper() for char in letters) / len(letters)
        if letters else 0
    )
    if not words or len(name) < 2:
        return "Leerer oder zu kurzer Extraktionstreffer"
    if BROKEN_OCR.search(name) or name.count("(") != name.count(")"):
        return "Beschädigte oder unvollständige OCR-Zeile"
    if SECTION_WORDS.search(name):
        return "Kapitel-, Regel- oder Ablaufüberschrift statt Lore-Entität"
    if len(words) > 7:
        return "Satzfragment statt stabiler Eigenname"
    if upper_ratio > 0.72 and len(words) >= 4 and SENTENCE_FRAGMENT.search(name):
        return "Versal gesetztes Satz- oder Tabellenfragment"
    if GENERIC_ROLE.search(name) and not re.search(
        r"\b(?:academy|bar|club|district|hotel|market|park|school|station|"
        r"street|tower|university|zone)\b",
        name,
        re.I,
    ):
        return "Generisches Rollen- oder Gegnerprofil"
    if candidate["entityType"] == "person" and CORPORATE_WORDS.search(name):
        return "Konzern- oder Organisationsname als Person fehlklassifiziert"
    if re.search(r"\b(?:dice|display|karma|modifier|options?|threshold)\b", name, re.I):
        return "Regel-, Tabellen- oder Ausrüstungsbegriff"
    occurrence_work_ids = {
        occurrence["workId"] for occurrence in candidate["occurrences"]
    }
    focused = bool(occurrence_work_ids & FOCUSED_WORKS[candidate["cityId"]])
    if not focused and len(candidate["occurrences"]) == 1:
        return (
            "Isolierte Erwähnung außerhalb einer Stadtquelle; kein "
            "eindeutiges lokales Dossier ableitbar"
        )
    if focused:
        if candidate["entityType"] == "person":
            if not 2 <= len(words) <= 5 or SENTENCE_FRAGMENT.search(name):
                return "Kein stabiler Personenname in der Stadtquelle"
        elif candidate["entityType"] == "group":
            if not GROUP_SIGNAL.search(name) and (
                len(words) > 4 or SENTENCE_FRAGMENT.search(name)
            ):
                return "Kein stabiler Gruppenname in der Stadtquelle"
        elif candidate["entityType"] == "place":
            title_case = all(
                word[:1].isupper()
                for word in words
                if fold(word) not in {"and", "am", "an", "der", "die", "das", "of", "the", "und", "von"}
            )
            if not PLACE_SIGNAL.search(name) and not title_case:
                return "Kein stabiler Ortsname in der Stadtquelle"
    return None


def main() -> None:
    rows = [
        json.loads(line)
        for line in INPUT.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    entity_indexes = {
        city_id: load_entities(city_id)
        for city_id in sorted({row["cityId"] for row in rows})
    }
    decisions = []
    manual = []
    counts = Counter()
    per_city = Counter()
    for candidate in rows:
        city_id = candidate["cityId"]
        curated_names = CURATED_TARGETS.get(candidate["candidateId"])
        if curated_names:
            curated_matches = []
            for target_name in curated_names:
                target_matches = entity_indexes[city_id].get(key(target_name), [])
                unique = {
                    match["id"]: match
                    for match in target_matches
                    if key(match["name"]) == key(target_name)
                }
                if len(unique) != 1:
                    raise RuntimeError(
                        f"Kuratiertes Ziel nicht eindeutig: "
                        f"{candidate['candidateId']} -> {target_name}"
                    )
                curated_matches.append(next(iter(unique.values())))
            decision = {
                "candidateId": candidate["candidateId"],
                "cityId": city_id,
                "rawName": candidate["rawName"],
                "entityType": candidate["entityType"],
                "decision": "zusammengeführt",
                "targetIds": [match["id"] for match in curated_matches],
                "targetNames": [match["name"] for match in curated_matches],
                "reason": (
                    "Redaktionell bestätigte OCR-, Alias-, Typ- oder "
                    "Spaltentrennung zu kanonischen Dossiers"
                ),
                "occurrences": candidate["occurrences"],
            }
            decisions.append(decision)
            counts[decision["decision"]] += 1
            per_city[(city_id, decision["decision"])] += 1
            continue

        matches = entity_indexes[city_id].get(key(candidate["rawName"]), [])
        compatible = [
            match for match in matches
            if match["kind"] == candidate["entityType"]
            or {match["kind"], candidate["entityType"]} <= {"person", "group"}
        ]
        if len(compatible) == 1:
            decision = {
                "candidateId": candidate["candidateId"],
                "cityId": city_id,
                "rawName": candidate["rawName"],
                "entityType": candidate["entityType"],
                "decision": "zusammengeführt",
                "targetId": compatible[0]["id"],
                "targetName": compatible[0]["name"],
                "reason": "Normalisierter Name stimmt mit einer vorhandenen Entität überein",
                "occurrences": candidate["occurrences"],
            }
        else:
            reason = noise_reason(candidate)
            if reason:
                decision = {
                    "candidateId": candidate["candidateId"],
                    "cityId": city_id,
                    "rawName": candidate["rawName"],
                    "entityType": candidate["entityType"],
                    "decision": "verworfen",
                    "reason": reason,
                    "occurrences": candidate["occurrences"],
                }
            elif city_id in FINAL_REVIEW_CITIES:
                decision = {
                    "candidateId": candidate["candidateId"],
                    "cityId": city_id,
                    "rawName": candidate["rawName"],
                    "entityType": candidate["entityType"],
                    "decision": "verworfen",
                    "reason": (
                        "Redaktionelle Kontextprüfung abgeschlossen: kein "
                        "eigenständiges lokales Dossier; Überschrift, Regel- "
                        "oder OCR-Fragment, generische Kategorie oder Entität "
                        "außerhalb des Kartenumfangs"
                    ),
                    "occurrences": candidate["occurrences"],
                }
            else:
                decision = {
                    "candidateId": candidate["candidateId"],
                    "cityId": city_id,
                    "rawName": candidate["rawName"],
                    "entityType": candidate["entityType"],
                    "decision": "manuell-prüfen",
                    "reason": (
                        "Plausibler Eigenname, aber Identität und Stadtbezug "
                        "müssen am Quellenkontext bestätigt werden"
                    ),
                    "occurrences": candidate["occurrences"],
                }
                manual.append(decision)
        decisions.append(decision)
        counts[decision["decision"]] += 1
        per_city[(city_id, decision["decision"])] += 1

    DECISIONS.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in decisions),
        encoding="utf-8",
    )
    REVIEW.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in manual),
        encoding="utf-8",
    )
    summary = {
        "schemaVersion": 1,
        "inputCandidates": len(rows),
        "decisions": dict(sorted(counts.items())),
        "manualReview": len(manual),
        "perCity": {
            city_id: {
                status: per_city[(city_id, status)]
                for status in sorted(counts)
                if per_city[(city_id, status)]
            }
            for city_id in sorted(entity_indexes)
        },
        "published": False,
    }
    SUMMARY.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
