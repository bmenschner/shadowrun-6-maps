#!/usr/bin/env python3
"""Create conservative dossier proposals from the manual source queue.

The output remains below ``source-data`` and is never published directly.
It is an auditable intermediate layer: only candidates with positive
person/group/place evidence are proposed, while every ambiguous heading stays
in the manual queue.
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "source-data/candidate-manual-review.jsonl"
OUTPUT = ROOT / "source-data/proposed-dossiers.jsonl"
SUMMARY = ROOT / "source-data/proposed-dossiers-summary.json"

PROFILE_ROLE_CUES = re.compile(
    r"\b(?:"
    r"human|elf|ork|troll|dwarf|changeling|shapeshifter|"
    r"decker|rigger|street samurai|shaman|mage|magician|adept|technomancer|"
    r"mr\.?\s+johnson|fixer|schieber|runner|kontakt|connection|"
    r"owner|besitzer(?:in)?|leader|führer(?:in)?|head|leiter(?:in)?|"
    r"president|präsident(?:in)?|mayor|bürgermeister(?:in)?|"
    r"detective|kommissar(?:in)?|doctor|doktor|street doc|straßendoc"
    r")\b",
    re.I,
)
PROFILE_STRUCTURE_CUES = re.compile(
    r"\b(?:"
    r"tags|background|metatype|metatyp|archetype|archetyp|"
    r"connection\s*[:(]|loyal(?:ty|ität)\s*[:(]|"
    r"initiative\s*:|condition monitor|zustandsmonitor|"
    r"(?:body|agility|reaction|strength|willpower|logic|intuition|charisma|edge)"
    r"\s*(?:\\d|:)|"
    r"(?:konstitution|geschicklichkeit|reaktion|stärke|willenskraft|logik|"
    r"intuition|charisma|edge)\s*(?:\\d|:)"
    r")\b",
    re.I,
)
PERSON_RELATION_CUES = re.compile(
    r"\b(?:"
    r"is|was|works?|runs?|leads?|owns?|serves?|acts?|heads?|"
    r"ist|war|arbeitet|führt|leitet|betreibt|gehört|dient|fungiert"
    r")\b",
    re.I,
)
PLACE_NAME_CUES = re.compile(
    r"\b(?:"
    r"airport|aerospaceport|arcology|arkologie|arena|bar|bazaar|bridge|"
    r"building|cafe|café|camp|casino|cemetery|center|centre|church|clinic|"
    r"club|complex|district|dock|dome|factory|fort|garden|grave|harbor|"
    r"haven|headquarters|hospital|hotel|institute|island|lab|labor|landing|"
    r"market|memorial|museum|park|pizzeria|plant|plaza|pub|restaurant|"
    r"school|shop|square|station|store|street|terminal|tower|university|"
    r"vault|warehouse|zone|"
    r"bahnhof|bezirk|flughafen|hafen|hauptquartier|klinik|krankenhaus|"
    r"markt|platz|straße|strasse|turm|universität|viertel|werk"
    r")\b",
    re.I,
)
GROUP_NAME_CUES = re.compile(
    r"\b(?:"
    r"agency|alliance|association|boyz|brotherhood|clan|collective|company|"
    r"corp(?:oration)?|crew|family|federation|foundation|gang|gmbh|group|"
    r"guild|gumi|hive|industries|league|mafia|militia|movement|nation|"
    r"organization|organisation|rangers|society|syndicate|team|triad|"
    r"union|vory|yakuza|"
    r"bund|familie|gruppe|gilde|konzern|syndikat|triade"
    r")\b",
    re.I,
)
GROUP_CONTEXT_CUES = re.compile(
    r"\b(?:"
    r"gang|group|organization|organisation|collective|company|corporation|"
    r"syndicate|mafia|yakuza|triad|militia|team|faction|fraktion|gruppe|"
    r"konzern|syndikat|gilde"
    r")\b",
    re.I,
)
PLACE_CONTEXT_CUES = re.compile(
    r"\b(?:"
    r"location|located|address|street|avenue|road|district|neighborhood|"
    r"building|facility|site|place|area|liegt|befindet|adresse|straße|"
    r"gebäude|anlage|gelände|ort|viertel|bezirk"
    r")\b",
    re.I,
)
NON_ENTITY = re.compile(
    r"\b(?:"
    r"abilities|ability|abenteuer|adventure|advantages?|agility|alignment|"
    r"amps?|armor|armour|art director|art staff|associate editor|attributes?|"
    r"ausrüstung|"
    r"background count|chapter|combat|condition monitor|contents?|credits?|"
    r"damage|developer|dice|edge|editor|equipment|fertigkeiten|gear|"
    r"hauptdarsteller|initiative|karma|legwork|mission|objectives?|"
    r"powers?|production|published by|publisher|qualities|rules?|scene|"
    r"skills?|spells?|street artist|street doc|street mage|street racer|"
    r"street samurai|table|tags|waffen|weapons?"
    r")\b",
    re.I,
)
LEADING_ACTION = re.compile(
    r"^(?:"
    r"befreie|beschaffe|bring|defeat|deliver|destroy|escape|find|found|get|help|"
    r"infiltrate|kill|killed|meet|protect|recover|rescue|retrieve|save|"
    r"steal|stop|take|track|verhindere|zerstöre"
    r")\b",
    re.I,
)
LEADING_NOISE = re.compile(
    r"^(?:"
    r"about|and|aufhänger|average|bes |die umliegenden|excerpt|for |für |"
    r"im |in |new .+ opens|wichtige orte|zur lage"
    r")",
    re.I,
)
ROLE_PARENTHETICAL = re.compile(
    r"\((?:"
    r"northside|southside|westside|eastside|the zone|zone|core|corridor|"
    r"haven|district|bezirk|stadtteil|"
    r"[^)]*(?:johnson|fixer|decker|rigger|mage|shaman|gang|lieutenant|"
    r"hitman|instructor|organlegger|runner|samurai|street artist)[^)]*"
    r")\)$",
    re.I,
)
GENERIC_ENTITY = re.compile(
    r"^(?:"
    r"airport|allies and enemies|arcology|association|bar|camp|club|"
    r"company|contact|contract|corporation|district|districts|gang|gangs|"
    r"group|headquarters|hospital|hotel|location|locations|market|"
    r"organization|people|place|places|restaurant|shop|street|team|tower|"
    r"unterwelt|viertel|bezirk|bezirke|orte|personen|schauplätze|syndikate"
    r")$",
    re.I,
)
DESCRIPTIVE_FRAGMENT = re.compile(
    r"\b(?:"
    r"and the|assistant district|der job|die heimat|ein(?:e|er|es)?|"
    r"eine?m?|former|from the|had|home of|in der|in die|located|"
    r"named|of the|that|the home|von der|with"
    r")\b",
    re.I,
)


def fold(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    return value.encode("ascii", "ignore").decode("ascii").casefold()


def name_key(value: str) -> str:
    value = re.sub(r"^(?:the|der|die|das)\s+", "", fold(value))
    return re.sub(r"[^a-z0-9]+", "", value)


def clean_name(value: str, city_name: str) -> str:
    value = re.sub(r"\s+", " ", value).strip(" .,:;")
    value = re.sub(r"^(?:[A-Z]\s*-\s*)", "", value)
    value = re.sub(
        rf"^(?:{re.escape(city_name)}[\s-]*maps?[\s-]*)",
        "",
        value,
        flags=re.I,
    )
    value = re.sub(
        rf"\s+{re.escape(city_name)}(?:\s+chaos)?$",
        "",
        value,
        flags=re.I,
    )
    value = ROLE_PARENTHETICAL.sub("", value).strip()
    if value.isupper() and len(value) > 3:
        value = value.title()
        value = value.replace("’S", "’s").replace("'S", "'s")
    return value


def stable_name(name: str) -> bool:
    words = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9'’&.-]+", name)
    if not 1 <= len(words) <= 7 or len(name) > 72:
        return False
    if LEADING_ACTION.search(name) or LEADING_NOISE.search(name) or NON_ENTITY.search(name):
        return False
    if GENERIC_ENTITY.fullmatch(name.strip()):
        return False
    if DESCRIPTIVE_FRAGMENT.search(name) and len(words) > 3:
        return False
    if name.count(",") > 1 or name.endswith(("ing", "ung")) and len(words) > 3:
        return False
    letters = [char for char in name if char.isalpha()]
    if len(letters) < 3:
        return False
    connectors = {
        "am", "an", "and", "auf", "bei", "da", "das", "de", "del", "den",
        "der", "des", "die", "do", "du", "for", "für", "im", "in", "la",
        "of", "the", "und", "van", "von", "zu", "zur", "&",
    }
    significant = [
        word.strip("()[]{}.,'’\"„“-/")
        for word in words
        if fold(word.strip("()[]{}.,'’\"„“-/")) not in connectors
    ]
    if any(
        word
        and word[0].isalpha()
        and not (word[0].isupper() or word.isupper())
        for word in significant
    ):
        return False
    return True


def looks_like_person_name(name: str) -> bool:
    return bool(
        re.fullmatch(
            r"(?:(?:Dr|Prof|Mr|Mrs|Ms|Captain|Major|Colonel|General)\.?\s+)?"
            r"[A-ZÄÖÜ][A-Za-zÀ-ÖØ-öø-ÿ'’.-]+"
            r"(?:\s+(?:[\"„“']?[A-ZÄÖÜ][A-Za-zÀ-ÖØ-öø-ÿ'’.-]+[\"”']?)){1,4}",
            name,
        )
    )


def classify(name: str, context: str, extracted_type: str) -> tuple[str, str] | None:
    lead = context[:900]
    if not stable_name(name):
        return None
    group_name = bool(GROUP_NAME_CUES.search(name))
    place_name = bool(PLACE_NAME_CUES.search(name))
    profile_role = bool(PROFILE_ROLE_CUES.search(lead))
    profile_structure = bool(PROFILE_STRUCTURE_CUES.search(lead))
    relation = bool(PERSON_RELATION_CUES.search(lead))
    person_name = looks_like_person_name(name)
    scoped_heading = bool(
        re.match(
            rf"^{re.escape(name)}\s*\([^)]{{2,45}}\)",
            lead,
            flags=re.I,
        )
    )
    one_word_profile = bool(
        re.fullmatch(r"[A-ZÄÖÜ][A-Za-zÀ-ÖØ-öø-ÿ'’.-]{2,32}", name)
        and profile_structure
        and profile_role
    )

    if (
        group_name
        and len(name_key(GROUP_NAME_CUES.sub("", name))) >= 3
        and not re.match(r"^(?:gang|group|team|association|corporation)\b", name, re.I)
    ):
        return "group", "Gruppen- oder Organisationsbezeichnung mit Quellenkontext"
    if place_name and len(name_key(PLACE_NAME_CUES.sub("", name))) >= 3:
        return "place", "Ortsbezeichnung mit geografischem oder baulichem Quellenkontext"
    if (
        extracted_type == "place"
        and scoped_heading
        and PLACE_CONTEXT_CUES.search(lead)
        and relation
    ):
        return "place", "Benannter Schauplatz mit Gebietszusatz und Ortsbeschreibung"
    if person_name and profile_structure and profile_role:
        return "person", "Eigenname mit Charakter- oder Kontaktprofil"
    if person_name and profile_role and relation:
        return "person", "Mehrteiliger Eigenname mit beschriebener Rolle"
    if (
        extracted_type == "person"
        and person_name
        and profile_structure
        and not PLACE_CONTEXT_CUES.search(name)
        and not GROUP_CONTEXT_CUES.search(name)
    ):
        return "person", "Mehrteiliger Personenname in einem strukturierten Profil"
    if one_word_profile:
        return "person", "Einwortname mit eindeutigem Charakterprofil"
    return None


def main() -> None:
    registry = json.loads((ROOT / "data/cities.json").read_text(encoding="utf-8"))
    city_names = {city["id"]: city["name"] for city in registry["cities"]}
    rows = [
        json.loads(line)
        for line in INPUT.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    proposals = {}
    for row in rows:
        city_id = row["cityId"]
        focused_occurrences = [
            occurrence
            for occurrence in row.get("occurrences", [])
            if occurrence.get("scope") in {"work", "chapter"}
        ]
        occurrences = (
            focused_occurrences
            if focused_occurrences
            else row.get("occurrences", [])
        )
        for occurrence in occurrences:
            name = clean_name(row["rawName"], city_names[city_id])
            result = classify(
                name,
                occurrence.get("descriptionContext", occurrence["context"]),
                row["entityType"],
            )
            if not result:
                continue
            entity_type, reason = result
            key = (city_id, name_key(name))
            current = proposals.get(key)
            source = {
                "workId": occurrence["workId"],
                "edition": occurrence["edition"],
                "sourceFile": occurrence.get("sourceFile"),
                "locator": occurrence["locator"],
            }
            if current is None:
                proposals[key] = {
                    "cityId": city_id,
                    "name": name,
                    "entityType": entity_type,
                    "reason": reason,
                    "sources": [source],
                    "candidateIds": [row["candidateId"]],
                    "status": "vorgeschlagen",
                }
            else:
                if source not in current["sources"]:
                    current["sources"].append(source)
                if row["candidateId"] not in current["candidateIds"]:
                    current["candidateIds"].append(row["candidateId"])
                if current["entityType"] != entity_type:
                    current["status"] = "typkonflikt"

    output = sorted(
        proposals.values(),
        key=lambda item: (item["cityId"], fold(item["name"])),
    )
    OUTPUT.write_text(
        "".join(
            json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n"
            for item in output
        ),
        encoding="utf-8",
    )
    counts = Counter(item["status"] for item in output)
    type_counts = Counter(
        item["entityType"] for item in output if item["status"] == "vorgeschlagen"
    )
    per_city = Counter(
        item["cityId"] for item in output if item["status"] == "vorgeschlagen"
    )
    summary = {
        "schemaVersion": 1,
        "proposals": len(output),
        "statuses": dict(sorted(counts.items())),
        "types": dict(sorted(type_counts.items())),
        "perCity": dict(sorted(per_city.items())),
        "published": False,
    }
    SUMMARY.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
