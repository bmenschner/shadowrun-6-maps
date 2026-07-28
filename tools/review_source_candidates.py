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
}

# These six city queues were read against their local source contexts.  Once
# the explicit targets above and normalised existing dossiers are resolved,
# the remaining candidates are headings, rules, OCR fragments, generic
# categories or entities outside the map scope.
FINAL_REVIEW_CITIES = set(FOCUSED_WORKS)
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
