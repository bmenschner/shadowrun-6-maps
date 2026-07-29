#!/usr/bin/env python3
"""Make reproducible final decisions for positive source-dossier proposals.

The broad candidate extractor intentionally favors recall.  This pass favors
precision: a proposal is accepted only when its own heading and following
description identify a stable person, group or place.  Every rejected
proposal records a concrete structural reason.  The result remains below
``source-data`` until accepted dossiers are converted to publishable,
paraphrased supplements.
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

from review_source_candidates import CITY_ALIASES


ROOT = Path(__file__).resolve().parents[1]
PROPOSALS = ROOT / "source-data/proposed-dossiers.jsonl"
CANDIDATES = ROOT / "source-data/candidate-decisions.jsonl"
OUTPUT = ROOT / "source-data/final-dossier-decisions.jsonl"
SUMMARY = ROOT / "source-data/final-dossier-decisions-summary.json"
CITIES = ROOT / "data/cities.json"

PLACE_CUE = re.compile(
    r"\b(?:airport|arcology|arkologie|arena|bar|bazaar|bridge|building|"
    r"cafe|café|camp|casino|cemetery|center|centre|church|clinic|club|"
    r"complex|district|dock|dome|factory|fort|garden|harbor|haven|"
    r"headquarters|hospital|hotel|institute|island|lab|labor|market|"
    r"memorial|museum|park|plant|plaza|pub|restaurant|school|shop|"
    r"square|station|store|street|terminal|tower|university|vault|"
    r"warehouse|zone|castle|house|ranch|theater|theatre|bahnhof|bezirk|"
    r"flughafen|hafen|hauptquartier|"
    r"klinik|krankenhaus|markt|platz|straße|strasse|turm|universität|"
    r"viertel|werk)\b",
    re.I,
)
GROUP_CUE = re.compile(
    r"\b(?:agency|alliance|association|brotherhood|clan|collective|"
    r"boyz|company|corp(?:oration)?|crew|family|federation|force|foundation|gang|"
    r"cartel|gmbh|group|gumi|hive|hordes|industries|institute|league|lords|mafia|militia|movement|"
    r"nation|order|organization|organisation|party|rangers|society|syndicate|"
    r"services|studios|technologies|team|triad|union|vory|yakuza|aerospace|oil|"
    r"allianz|bund|familie|gruppe|gilde|konzern|"
    r"syndikat|triade)\b",
    re.I,
)
PERSON_ROLE = re.compile(
    r"\b(?:adept|agent|boss|captain|ceo|chairm[ae]n|commander|contact|"
    r"decker|detective|director|doctor|doktor|dragon|fixer|general|"
    r"hacker|journalist|kommissar|leader|leiter|mage|magician|manager|"
    r"mayor|bürgermeister|finanzminister|mr\.?\s+johnson|owner|president|professor|reporter|rigger|"
    r"runner|samurai|schieber|shaman|sprecher|technomancer|wirt)\b",
    re.I,
)
PROFILE_FIELD = re.compile(
    r"\b(?:age|alter|archetype|archetyp|background|connection|"
    r"current residence|metatype|metatyp|loyalty|loyalität|"
    r"personal life|personality|real name|role|sex|species|"
    r"status|type)\s*:",
    re.I,
)
LOCAL_STRUCTURE = re.compile(
    r"\b(?:based|befindet|headquartered|hauptquartier|home office|"
    r"located|liegt|residence|residiert|sitz|stationed|zentrale)\b",
    re.I,
)
RELATION = re.compile(
    r"\b(?:are|became|began|founded|has|have|is|leads?|operates?|owns?|"
    r"runs?|serves?|was|works?|comprise|comprises|consists?|betreibt|führt|gehört|gründete|hat|ist|"
    r"leitet|sind|war|wurde)\b",
    re.I,
)
PRONOUN = re.compile(r"\b(?:he|her|hers|him|his|she|er|ihr|ihre|ihm|ihn|sie)\b", re.I)
INTERSECTION = re.compile(
    r"\b(?:avenue|ave\.?|boulevard|blvd\.?|road|rd\.?|street|str(?:aße|asse)?|"
    r"way)\b.{0,40}(?:&|/|\band\b|\bund\b).{0,40}\b(?:avenue|ave\.?|"
    r"boulevard|blvd\.?|road|rd\.?|street|str(?:aße|asse)?|way)\b",
    re.I,
)
STRUCTURE_NOISE = re.compile(
    r"\b(?:abilities|abenteuer|adventure|air tactics|art director|"
    r"assistant editor|attributes|background|chapter|condition monitor|"
    r"contents|copyright|credits|damage|dice|editorial|equipment|"
    r"game information|game master|initiative|isbn|karma|legwork|limits|"
    r"mission|objectives|phase (?:one|two|three)|pitch|plot(?:line)?|production staff|"
    r"published by|publisher|rules|scene|skills|social tests|strategic stunts|"
    r"success description|table|tags|the job|trademark|weapons)\b",
    re.I,
)
EVENT_FRAGMENT = re.compile(
    r"\b(?:announces?|attack(?:s|ed)?|beginnt|eröffnet|explodes?|"
    r"declare|escapes?|found dead|having troubles|heist|killed|meldungen|news|schlägt zu|top meldungen|"
    r"fertigstellung|completion|"
    r"warns?|enforces?)\b",
    re.I,
)
GENERIC_NAME = re.compile(
    r"^(?:"
    r"about|background|chapter|city|contacts?|corporate presence|"
    r"current public perceptions|districts?|equipment|files|"
    r"game information|getting in(?:/| and )out|headquarters|history|"
    r"hotspots?|locations?|major cities|miscellaneous|name|overview|"
    r"page|people|places?|political organization|principal divisions|"
    r"scene|security|street art|street gangs|gangs|the job|the matrix|timeline|zone economics|"
    r"auf der straße|alternative schatten"
    r")$",
    re.I,
)
TRAILING_FRAGMENT = re.compile(
    r"\b(?:and|at|der|des|die|ein(?:e[rmns]?)?|for|from|in|of|the|to|und|von)$",
    re.I,
)
PERSON_NONNAME = re.compile(
    r"\b(?:action|airport|alliance|allianz|attack|awareness|branch|bridge|"
    r"building|cartel|casino|center|church|city|company|complex|conflict|"
    r"control|corporate|council|district|facility|files?|foundation|games?|"
    r"gang|government|headquarters|hospital|hotel|industries|institute|"
    r"labor|league|machine|magic|magie|market|meet|mission|motors|nation|"
    r"organization|park|party|phase|pitch|recognizing|safehouse|school|"
    r"security|services|society|sports|street|studios|syndicate|system|"
    r"tactics|team|technologies|tower|transport|union|university|virus|"
    r"warehouse|zone)\b",
    re.I,
)
GENERIC_PLACE = re.compile(
    r"^(?:at the .+|black market|bookstore/museum|building|building features|"
    r"coffee shop|company headquarters|complex and .+|complex forms|control room|"
    r"dragon headquarters|factory|factory vehicle|g guard tower|guard tower|"
    r"headquarters(?:/| and )?turf|hotel, searching|human .+|"
    r"community hospital|correctional institute|international airport|"
    r"communications center military node|factory towns|gang house|"
    r"international school|labor neighborhoods|main vault|manufacturing plant|"
    r"medical center|museum and zoo|museum entrance|name größe bezirk.*|"
    r"nation building|office complex|of the tower|playing the market|"
    r"prison complex|research lab|"
    r"am hafen|dem labor|development center|free zone|limited building space|"
    r"normales hotel host|office complex|restaurant hijinks|street art|"
    r"street cred|street rumors.*|über die stra(?:ss|ß)e|"
    r"recreation center|research center|safe house|the bridge.s condition|"
    r"the clinic|the train station|the zone|university ties|"
    r"where to shop|works headquarters|zone defense|zone isolated)$",
    re.I,
)
PLACE_TITLE_NOISE = re.compile(
    r"\b(?:activity|archetypes?|ausflug|beziehungen|closed|condition|"
    r"future|having troubles|hijinks|jobs?|knowledge|online|ratings?|"
    r"reputation|rumors?|shutdown|slang|still|stunts?|tags?|vigil)\b",
    re.I,
)
HEADING_PHRASE_NOISE = re.compile(
    r"^(?:baubeginn\b|bishop arrested\b|block war\b|capturing\b|"
    r"colombian subterfuge\b|despite\b|familiar faces$|fight night$|"
    r"flieht aus\b|general street gang knowledge\b|hightech-hafen\b|"
    r"increased drain$|killing\b|no more vacation$|pushing the envelope$|"
    r"restaurant wars$|scaling the\b|schauplätze\b|sternschutz am\b|"
    r"times square ball drop\b|vor der errichtung\b|zurück im spiel$)"
    r"|^(?:street magic|street-level players|new complex forms|"
    r"building prime runners|council island-schlagworte|"
    r"every other street corner|not a through street|"
    r"westin seattle hotel convention maps)$"
    r"|\b(?:name größe bezirk|opens rehab clinic|loses grant)\b",
    re.I,
)
GENERIC_FACILITY_NAME = re.compile(
    r"^(?:billiges|erstklassiges|familiäres|großes|kleines|large|medium|"
    r"mid-size|mittelgro(?:ss|ß)es|normales|sample|standard|typische[rs]?)\s+"
    r"(?:bar|casino|club|hotel|hospital|krankenhaus|restaurant|shop|store)\b",
    re.I,
)
GENERIC_GROUP = re.compile(
    r"^(?:all|both|corporate|executive|hard corps|large|low-level|private|"
    r"rapid response|response|scout|security|senior|swat)[ -]"
    r"|(?:gang members?|member|soldier|team leader|watcher)$"
    r"|^(?:both teams|food poisoning|konzern-gesundheit|low-level runners|"
    r"mafia families|nation/sector|private sicherheit)$",
    re.I,
)
PERSON_TITLE = re.compile(
    r"\b(?:activities|assistance|attack|aufhänger|burning|cast of shadows|"
    r"c-suites|connections?|corporation|current|decision|entscheidung|"
    r"emergenz|effects?|files?|food|games?|gro(?:ss|ß)e politik|"
    r"catalog|election day|information|loaded|map|movement|opposition|"
    r"report|rally|riding|shadowrun|stattgespräch|wissenswertes|"
    r"lohnende ziele|sag(?:'|’)s ihnen|sandmann-dateien|sicherheitsservice|"
    r"tag|tiger|unterwelt|who(?:'s|’s) who|wanzen)\b",
    re.I,
)
GENERIC_PERSON = re.compile(
    r"^(?:awakened magician|cash hermetic doctor|cybercom(?:-|\s)officer|"
    r"department of homicide|dissonant technomancers|dragon wasp queen|"
    r"field npcs|four corners residents|gangmitglied|head case .+|"
    r"lagos council members|male .+|medical group|mercenary|nexus personnel|"
    r"petty officer|project vulcan mages|protection specialist|"
    r"rikkis squad|rikki’s squad|sioux shadowrunners|staff officer|"
    r"technomancer sprite|toxischer schamane|watch commander|"
    r"weiblicher mensch)$",
    re.I,
)
ROLE_NAME = re.compile(
    r"^(?:(?:adl\s+)?finanzminister|bürgermeister|governor|gouverneur|"
    r"generalleutnant|general|dr\.?|doktor|prof\.?|professor|"
    r"president|präsident)\s+"
    r"[A-ZÄÖÜ][A-Za-zÀ-ÖØ-öø-ÿ'’.-]+"
    r"(?:\s+[A-ZÄÖÜ][A-Za-zÀ-ÖØ-öø-ÿ'’.-]+){1,4}$",
    re.I,
)
EQUIPMENT_CONTEXT = re.compile(
    r"\b(?:accuracy|availability|capacity|damage|device rating|handling|"
    r"höchstgeschwindigkeit|munition|sensor|signal|street index|vehicle|"
    r"waffe|weapon|drohne|drone)\b",
    re.I,
)


def fold(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    return value.encode("ascii", "ignore").decode("ascii").casefold()


def normalized(value: str) -> str:
    value = re.sub(r"\([^)]*\)", " ", value)
    return re.sub(r"[^a-z0-9]+", "", fold(value))


def load_existing_names() -> tuple[
    dict[str, dict[str, list[dict]]],
    dict[str, set[str]],
]:
    per_city: dict[str, dict[str, list[dict]]] = {}
    across: dict[str, set[str]] = defaultdict(set)
    for city in json.loads(CITIES.read_text(encoding="utf-8"))["cities"]:
        city_id = city["id"]
        manifest_path = ROOT / city["manifest"]
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        city_dir = manifest_path.parent
        entities: dict[str, list[dict]] = defaultdict(list)
        # Generated source supplements are outputs of this audit and must not
        # feed back into its canonical-name comparison on a later run.
        for field in ("places", "virtualPlaces", "historicalPlaces"):
            filename = manifest.get("files", {}).get(field)
            if not filename:
                continue
            for feature in json.loads(
                (city_dir / filename).read_text(encoding="utf-8")
            ).get("features", []):
                props = feature["properties"]
                for name in [props["name"], *(props.get("aliases") or [])]:
                    entities[normalized(name)].append({
                        "id": props["global_id"],
                        "name": props["name"],
                        "entityType": "place",
                    })
        for field in ("people", "historicalPeople"):
            filename = manifest.get("files", {}).get(field)
            if not filename:
                continue
            for person in json.loads(
                (city_dir / filename).read_text(encoding="utf-8")
            ):
                for name in [person["name"], *(person.get("aliases") or [])]:
                    entities[normalized(name)].append({
                        "id": person["global_id"],
                        "name": person["name"],
                        "entityType": person.get("entity_type", "person"),
                    })
        per_city[city_id] = entities
        for name_key in entities:
            if name_key:
                across[name_key].add(city_id)
    return per_city, across


def person_shape(name: str) -> bool:
    words = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ'’.-]+", name)
    if not 1 <= len(words) <= 5 or PERSON_NONNAME.search(name):
        return False
    connectors = {"de", "del", "der", "di", "du", "la", "van", "von"}
    significant = [word for word in words if fold(word.strip(".'’")) not in connectors]
    return bool(significant) and all(
        word[:1].isupper() or word.isupper()
        for word in significant
    )


def clean_description(value: str, name: str) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    pattern = re.compile(rf"^\s*{re.escape(name)}\s*", re.I)
    return pattern.sub("", value, count=1)


def search_text(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(char for char in value if not unicodedata.combining(char))
    return " " + re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip() + " "


def has_local_evidence(city_id: str, name: str, occurrence: dict, lead: str) -> bool:
    if occurrence.get("scope") == "work":
        return True
    aliases = CITY_ALIASES[city_id]
    folded_name = search_text(name)
    folded_lead = search_text(
        " ".join(
            (
                lead[:700],
                occurrence.get("context", "")[:700],
                occurrence.get("sourceFile", ""),
            )
        )
    )
    if any(
        f" {alias} " in folded_name or f" {alias} " in folded_lead
        for alias in aliases
    ):
        return True
    for alias in aliases:
        escaped = re.escape(alias)
        if re.search(
            rf"(?:headquarters|hauptquartier|hauptsitz|residence|wohnort|"
            rf"located|based|stationed|office|division|niederlassung|"
            rf"\bin\b|\bbei\b|\bnear\b|\bfrom\b).{{0,55}}\b{escaped}\b",
            folded_lead,
        ):
            return True
        if re.search(
            rf"\b{escaped}\b.{{0,55}}(?:headquarters|hauptquartier|"
            rf"resident|location|office|division|niederlassung)",
            folded_lead,
        ):
            return True
    return False


def target_in_name(city_id: str, name: str) -> bool:
    folded_name = search_text(name)
    return any(
        f" {alias} " in folded_name
        for alias in CITY_ALIASES[city_id]
    )


def names_other_city(city_id: str, name: str) -> bool:
    folded_name = search_text(name)
    return any(
        other_id != city_id
        and any(f" {alias} " in folded_name for alias in aliases)
        for other_id, aliases in CITY_ALIASES.items()
    ) and not target_in_name(city_id, name)


def decide_occurrence(
    city_id: str,
    name: str,
    proposed_type: str,
    occurrence: dict,
    across_city_names: dict[str, set[str]],
    proposal_cities: dict[str, set[str]],
) -> tuple[str, str, str]:
    description = occurrence.get(
        "descriptionContext",
        occurrence.get("context", ""),
    )
    body = clean_description(description, name)
    lead = body[:700]
    words = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9'’&.-]+", name)

    if (
        len(name) < 3
        or len(name) > 80
        or not words
        or len(words) > 8
        or GENERIC_NAME.fullmatch(name.strip())
        or TRAILING_FRAGMENT.search(name.strip())
        or re.search(r"\b(?:and|und)\s+(?:am|an|im|in|on|the)$", name, re.I)
    ):
        return "rejected", proposed_type, "Kein stabiler Eigenname"
    if (
        len(proposal_cities.get(normalized(name), set())) > 1
        and (proposed_type == "place" or PLACE_CUE.search(name) or INTERSECTION.search(name))
        and not target_in_name(city_id, name)
    ):
        return (
            "rejected",
            proposed_type,
            "Mehrdeutiger Ortskandidat wurde mehreren Städten zugeordnet",
        )
    other_existing_cities = across_city_names.get(normalized(name), set()) - {city_id}
    if other_existing_cities and city_id not in across_city_names.get(normalized(name), set()):
        return (
            "rejected",
            proposed_type,
            "Kanonische Entität ist bereits ausschließlich einer anderen Stadt zugeordnet",
        )
    if re.search(
        r"\b(?:ganger|guards?|patrons?|street sam|vault-wache)\b",
        name,
        re.I,
    ):
        return "rejected", proposed_type, "Rollen- oder Gegnerprofil statt Ortsdossier"
    if re.search(
        r"\b(?:feminismus|evokation|manipulationsmagie|procedures|"
        r"street grimoire|street gangs|music \(|north america and)\b",
        name,
        re.I,
    ):
        return "rejected", proposed_type, "Themen-, Quellen- oder Listenüberschrift"
    if names_other_city(city_id, name):
        return "rejected", proposed_type, "Der Name bezeichnet ausdrücklich eine andere Stadt"
    if not has_local_evidence(city_id, name, occurrence, lead):
        return "rejected", proposed_type, "Kein unmittelbarer lokaler Bezug dieser Entität"
    if STRUCTURE_NOISE.search(name):
        return "rejected", proposed_type, "Regel-, Ablauf-, Credit- oder Profilüberschrift"
    if GENERIC_PLACE.fullmatch(name.strip()):
        return "rejected", proposed_type, "Generische Orts- oder Gebäudeart statt Eigenname"
    if HEADING_PHRASE_NOISE.search(name):
        return "rejected", proposed_type, "Kapitel-, Meldungs- oder Szenenüberschrift statt Entität"
    if re.search(
        r"^(?:assistant district attorney|female human district attorney|"
        r"street dweller/|street hustler/|street shaman$)",
        name,
        re.I,
    ):
        return "rejected", proposed_type, "Generisches Rollenprofil statt Entität"
    if proposed_type == "person" and EQUIPMENT_CONTEXT.search(lead[:500]):
        return "rejected", proposed_type, "Ausrüstungs- oder Fahrzeugprofil statt Person"
    if (
        STRUCTURE_NOISE.search(lead[:180])
        and not PROFILE_FIELD.search(lead[:240])
        and not GROUP_CUE.search(name)
        and not PLACE_CUE.search(name)
    ):
        return "rejected", proposed_type, "Regel-, Ablauf-, Credit- oder Profilüberschrift"
    if EVENT_FRAGMENT.search(name) and not GROUP_CUE.search(name):
        return "rejected", proposed_type, "Nachrichten- oder Ereignisüberschrift statt Dossiername"
    if re.search(r"\b(?:mayor|president|seat)$", name, re.I):
        return "rejected", proposed_type, "Generische Amts- oder Funktionsbezeichnung"
    if re.search(r"[/|].*[/|]", name) or name.count(",") > 2:
        return "rejected", proposed_type, "Listen- oder Tabellenfragment"
    if normalized(name) in {"shadowrun", "catalystgamelabs", "fantasyproductionsgmbh"}:
        return "rejected", proposed_type, "Produktions- oder Systembegriff"

    name_place = bool(PLACE_CUE.search(name) or INTERSECTION.search(name))
    name_group = bool(GROUP_CUE.search(name))
    described_place = bool(
        LOCAL_STRUCTURE.search(lead)
        and re.search(r"\b(?:address|anlage|building|facility|gebäude|ort|place|site)\b", lead, re.I)
    )
    repeated_group = bool(
        re.match(
            rf"^(?:the|die|der|das)?\s*{re.escape(name)}\b",
            body,
            re.I,
        )
        and GROUP_CUE.search(lead[:280])
        and RELATION.search(lead[:280])
    )
    folded_name_key = normalized(name)
    name_words = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ'’.-]+", name)
    first_name_key = normalized(name_words[0]) if name_words else ""
    surname_key = normalized(name_words[-1]) if name_words else ""
    lead_key_window = normalized(lead[:220])
    repeats_person_name = bool(
        folded_name_key
        and folded_name_key in lead_key_window
        or (
            len(surname_key) >= 4
            and surname_key in lead_key_window
        )
        or (
            len(first_name_key) >= 4
            and first_name_key in lead_key_window
        )
    )
    relation_words = (
        r"(?:are|became|has|have|is|leads?|owns?|runs?|serves?|was|works?|"
        r"er|hat|ist|leitet|sie|war|wurde|he|she)"
    )
    mention_patterns = [
        re.escape(token)
        for token in (name, name_words[0] if name_words else "", name_words[-1] if name_words else "")
        if len(normalized(token)) >= 4
    ]
    bounded_person_relation = any(
        re.search(
            rf"\b{pattern}\b.{{0,120}}\b{relation_words}\b",
            lead,
            re.I,
        )
        for pattern in mention_patterns
    )
    person_profile_opening = bool(
        re.match(
            r"^(?:male|female|männlich|weiblich|human|mensch|elf|ork|"
            r"troll|dwarf|zwerg|dragon|drache|shapeshifter|gestaltwandler|"
            r"free spirit|freier geist|another important|"
            r"age\s*:|alter\s*:|archetype\s*:|archetyp\s*:|"
            r"background\s*:|metatype\s*:|metatyp\s*:)",
            lead,
            re.I,
        )
        or any(
            re.match(
                rf"^{pattern}\b.{{0,100}}\b{relation_words}\b",
                lead,
                re.I,
            )
            for pattern in mention_patterns
        )
    )
    person_identity_support = bool(
        PROFILE_FIELD.search(lead[:500])
        or PRONOUN.search(lead[:500])
        or PERSON_ROLE.search(lead[:500])
        or re.match(r"^\(?background\)?\b", lead, re.I)
    )
    described_person = bool(
        person_shape(name)
        and repeats_person_name
        and person_profile_opening
        and person_identity_support
        and (
            PROFILE_FIELD.search(lead[:500])
            or PRONOUN.search(lead[:500])
            or bounded_person_relation
        )
    )

    if ROLE_NAME.fullmatch(name.strip()):
        return "accepted", "person", "Name mit eindeutiger Amts- oder Berufsbezeichnung"
    if re.match(r"^(?:dr\.?|doktor|prof\.?)\s+", name, re.I):
        name_place = False
    if name_group and not name_place and (
        repeated_group
        or LOCAL_STRUCTURE.search(lead[:500])
        or target_in_name(city_id, name)
    ):
        proper = re.sub(GROUP_CUE, " ", name)
        if (
            len(re.sub(r"[^A-Za-zÀ-ÖØ-öø-ÿ0-9]+", "", proper)) >= 3
            and not GENERIC_GROUP.search(name)
        ):
            return "accepted", "group", "Benannte Organisation mit Gruppen- oder Strukturbeleg"
    if name_place and not GENERIC_PLACE.fullmatch(name.strip()):
        if (
            PLACE_TITLE_NOISE.search(name)
            or GENERIC_FACILITY_NAME.search(name)
            or name.rstrip().endswith("-")
            or re.search(r"\b(?:archetype|typische[rs]?)\s*/", name, re.I)
        ):
            return "rejected", proposed_type, "Generische Tabellen-, Karten- oder Ereignisbezeichnung"
        if INTERSECTION.search(name):
            return "accepted", "place", "Eindeutig bezeichnete Straßenkreuzung"
        if (
            LOCAL_STRUCTURE.search(lead[:500])
            or RELATION.search(lead[:500])
            or re.search(
                r"\b(?:address|adresse|at the corner|ecke|located at|"
                r"straße|street|avenue|road|district|bezirk)\b",
                lead[:500],
                re.I,
            )
        ):
            return "accepted", "place", "Stabiler Ortsname mit Orts- oder Adressbeleg"
    group_profile_opening = bool(
        re.match(
            r"^(?:(?:the|die|der|das)\s+)?(?:gang|group|gruppe|clan|"
            r"organization|organisation|syndicate|syndikat|triad|triade|"
            r"vory|yakuza)\b",
            lead,
            re.I,
        )
        or re.match(
            rf"^(?:the|die|der|das)?\s*{re.escape(name)}\b.{{0,140}}"
            rf"\b(?:group|gruppe|gang|organization|organisation|"
            rf"syndicate|syndikat|triad|vory|yakuza|is|are|ist|sind)\b",
            body,
            re.I,
        )
    )
    if repeated_group and group_profile_opening and not PRONOUN.search(lead[:220]):
        return "accepted", "group", "Beschreibung weist den Namen als Organisation aus"
    if (
        described_person
        and not PERSON_TITLE.search(name)
        and not GENERIC_PERSON.fullmatch(name.strip())
    ):
        return "accepted", "person", "Eigenname mit Rollen-, Biografie- oder Profilbeleg"

    if proposed_type == "place" and LOCAL_STRUCTURE.search(lead[:360]):
        return "accepted", "place", "Ortsname mit unmittelbarem Lagebeleg"
    return "rejected", proposed_type, "Kein belastbarer Entitätstyp im unmittelbaren Beschreibungstext"


def main() -> int:
    existing_names, across_city_names = load_existing_names()
    candidates = {
        row["candidateId"]: row
        for row in (
            json.loads(line)
            for line in CANDIDATES.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    }
    proposals = [
        json.loads(line)
        for line in PROPOSALS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    proposal_cities: dict[str, set[str]] = defaultdict(set)
    for proposal in proposals:
        proposal_cities[normalized(proposal["name"])].add(proposal["cityId"])
    output = []
    counts = Counter()
    per_city = Counter()
    for proposal in proposals:
        accepted_sources = []
        rejected_sources = []
        accepted_types = Counter()
        for candidate_id in proposal["candidateIds"]:
            candidate = candidates[candidate_id]
            for occurrence in candidate.get("occurrences", []):
                if not any(
                    source["workId"] == occurrence["workId"]
                    for source in proposal["sources"]
                ):
                    continue
                status, entity_type, reason = decide_occurrence(
                    proposal["cityId"],
                    proposal["name"],
                    proposal["entityType"],
                    occurrence,
                    across_city_names,
                    proposal_cities,
                )
                record = {
                    "candidateId": candidate_id,
                    "workId": occurrence["workId"],
                    "edition": occurrence["edition"],
                    "sourceFile": occurrence.get("sourceFile"),
                    "locator": occurrence["locator"],
                    "scope": occurrence.get("scope"),
                    "reason": reason,
                }
                if status == "accepted":
                    accepted_sources.append(record)
                    accepted_types[entity_type] += 1
                else:
                    rejected_sources.append(record)

        exact_targets = existing_names[proposal["cityId"]].get(
            normalized(proposal["name"]),
            [],
        )
        if accepted_sources and exact_targets:
            status = "merged"
            entity_type = exact_targets[0]["entityType"]
            reason = "Normalisierter Name oder Alias entspricht einem vorhandenen Dossier."
        elif accepted_sources:
            if INTERSECTION.search(proposal["name"]):
                entity_type = "place"
            elif GROUP_CUE.search(proposal["name"]):
                entity_type = "group"
            elif PLACE_CUE.search(proposal["name"]):
                entity_type = "place"
            else:
                entity_type = accepted_types.most_common(1)[0][0]
            status = "accepted"
            reason = (
                "Mindestens eine konkrete Fundstelle weist den stabilen Namen "
                "als eigenständige Lore-Entität aus."
            )
        else:
            entity_type = proposal["entityType"]
            status = "rejected"
            reason = (
                "Keine Fundstelle weist die Überschrift als eigenständige "
                "Person, Gruppe oder Ort aus."
            )
        row = {
            "cityId": proposal["cityId"],
            "name": proposal["name"],
            "entityType": entity_type,
            "status": status,
            "reason": reason,
            "acceptedSources": accepted_sources,
            "rejectedSources": rejected_sources,
            "candidateIds": proposal["candidateIds"],
        }
        if status == "merged":
            row["targetIds"] = sorted({target["id"] for target in exact_targets})
            row["targetNames"] = sorted({target["name"] for target in exact_targets})
        output.append(row)
        counts[(status, entity_type)] += 1
        per_city[(proposal["cityId"], status)] += 1

    OUTPUT.write_text(
        "".join(
            json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
            for row in output
        ),
        encoding="utf-8",
    )
    summary = {
        "schemaVersion": 1,
        "proposals": len(output),
        "decisions": {
            status: {
                entity_type: counts[(status, entity_type)]
                for entity_type in ("place", "person", "group")
                if counts[(status, entity_type)]
            }
            for status in ("accepted", "merged", "rejected")
        },
        "perCity": {
            city_id: {
                status: per_city[(city_id, status)]
                for status in ("accepted", "merged", "rejected")
                if per_city[(city_id, status)]
            }
            for city_id in sorted({row["cityId"] for row in output})
        },
        "published": False,
    }
    SUMMARY.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
