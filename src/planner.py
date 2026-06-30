import json
import sys
import argparse
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATABASE = ROOT / "database"


CAMPAIGN_RULES = {
    "lookbook": {
        "shots": ["full", "three", "walk", "side", "seated", "detail"],
        "poses": ["walk", "three", "relaxed", "seated", "collar", "cuff"],
        "lenses": ["35mm", "50mm", "85mm"],
        "scenes": ["studio", "apartment", "gallery", "street", "rooftop"],
    },
    "campaign": {
        "shots": ["hero", "low", "campaign", "group", "silhouette"],
        "poses": ["confident", "sculptural", "group", "walk"],
        "lenses": ["24mm", "35mm", "50mm"],
        "scenes": ["rooftop", "gallery", "industrial", "black", "urban"],
    },
    "ecommerce": {
        "shots": ["front", "side", "back", "detail", "flat"],
        "poses": ["front", "side", "relaxed", "cuff"],
        "lenses": ["50mm", "85mm", "100mm"],
        "scenes": ["white", "studio"],
    },
    "social": {
        "shots": ["street", "walk", "detail", "hero"],
        "poses": ["walk", "leaning", "collar", "hair"],
        "lenses": ["24mm", "35mm", "50mm"],
        "scenes": ["street", "urban", "mirror", "rooftop"],
    },
}

GARMENT_RULES = {
    "denim": ["street", "walk", "detail", "urban", "35mm", "cuff"],
    "jacket": ["hero", "three", "back", "collar", "50mm", "gallery"],
    "blazer": ["three", "tailored", "gallery", "50mm", "minimal"],
    "dress": ["walk", "seated", "romantic", "85mm", "coastal"],
    "activewear": ["active", "performance", "lunge", "rooftop", "35mm"],
    "hoodie": ["street", "low", "pocket", "urban", "24mm"],
    "accessory": ["detail", "hand", "85mm", "macro", "luxury"],
}

SHOT_CATEGORY_RULES = {
    "walking": ["walk", "walking", "street style", "motion", "stride"],
    "back": ["back", "rear", "over shoulder"],
    "front": ["front", "hero", "full outfit", "commercial hero", "ecommerce"],
    "seated": ["seated", "sit"],
    "group": ["group"],
    "active": ["active", "performance", "lunge", "jump"],
    "flat_lay": ["flat lay", "product arranged"],
    "detail": ["detail", "close", "macro", "hand", "fabric", "accessory"],
}

POSE_COMPATIBILITY = {
    "detail": {
        "prefer": ["detail", "cuff", "collar", "hand", "waistband", "bag"],
        "avoid": ["walk", "lunge", "jump", "full", "floor", "group"],
    },
    "walking": {
        "prefer": ["walk", "walking", "stride", "profile"],
        "avoid": ["seated", "sit", "floor", "detail", "cuff"],
    },
    "back": {
        "prefer": ["over shoulder", "face away", "away from camera", "back mostly"],
        "avoid": ["front", "walk", "cuff", "hair", "back leg"],
    },
    "front": {
        "prefer": ["front", "relaxed", "pocket", "three", "confident", "ankle"],
        "avoid": ["cuff", "detail", "back", "floor", "hair"],
    },
    "seated": {
        "prefer": ["seated", "sit", "floor"],
        "avoid": ["walk", "lunge", "jump", "back"],
    },
    "group": {
        "prefer": ["group", "staggered"],
        "avoid": ["detail", "cuff", "face"],
    },
    "flat_lay": {
        "prefer": ["product", "not applicable"],
        "avoid": ["walk", "seated", "face", "hair", "lunge"],
    },
    "active": {
        "prefer": ["active", "lunge", "jump", "performance"],
        "avoid": ["seated", "floor", "cuff", "back"],
    },
}

LENS_COMPATIBILITY = {
    "detail": {
        "prefer": ["macro", "85mm", "100mm", "detail", "portrait"],
        "avoid": ["24mm", "wide"],
    },
    "walking": {
        "prefer": ["35mm", "50mm", "environmental"],
        "avoid": ["macro", "100mm"],
    },
    "back": {
        "prefer": ["50mm", "70mm", "commercial"],
        "avoid": ["macro", "24mm"],
    },
    "front": {
        "prefer": ["50mm", "35mm", "commercial", "environmental"],
        "avoid": ["macro", "100mm"],
    },
    "seated": {
        "prefer": ["50mm", "85mm", "portrait"],
        "avoid": ["24mm", "macro"],
    },
    "group": {
        "prefer": ["24mm", "35mm", "wide", "environmental"],
        "avoid": ["macro", "100mm"],
    },
    "flat_lay": {
        "prefer": ["35mm", "50mm", "commercial"],
        "avoid": ["85mm", "portrait"],
    },
    "active": {
        "prefer": ["35mm", "50mm", "environmental"],
        "avoid": ["macro", "100mm"],
    },
}

CAMPAIGN_SCENE_COMPATIBILITY = {
    "lookbook": {
        "prefer": ["studio", "street", "urban", "gallery", "apartment", "rooftop"],
        "avoid": ["hotel", "mirror"],
    },
    "campaign": {
        "prefer": ["rooftop", "gallery", "industrial", "black", "urban", "coastal"],
        "avoid": ["fitting"],
    },
    "ecommerce": {
        "prefer": ["white", "studio", "colorama"],
        "avoid": ["street", "industrial", "hotel", "mirror"],
    },
    "social": {
        "prefer": ["street", "urban", "mirror", "rooftop", "apartment"],
        "avoid": ["white studio"],
    },
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_records(collection: str) -> list[dict[str, Any]]:
    records = []
    for path in sorted((DATABASE / collection).glob("*.json")):
        record = load_json(path)
        record["_path"] = str(path.relative_to(ROOT))
        records.append(record)
    return records


def load_record(collection: str, record_id: str | None) -> dict[str, Any] | None:
    if not record_id:
        return None
    for record in load_records(collection):
        if record_id in {record.get("id"), Path(record["_path"]).stem}:
            return record
    raise FileNotFoundError(f"Could not find {collection} record: {record_id}")


def text_blob(record: dict[str, Any]) -> str:
    values = []
    for key, value in record.items():
        if key.startswith("_"):
            continue
        if isinstance(value, dict):
            values.extend(str(item) for item in value.values())
        elif isinstance(value, list):
            values.extend(str(item) for item in value)
        else:
            values.append(str(value))
    return " ".join(values).lower()


def request_keywords(garment: str, campaign_type: str, brand: dict[str, Any] | None) -> list[str]:
    keywords = CAMPAIGN_RULES.get(campaign_type.lower(), CAMPAIGN_RULES["lookbook"]).copy()
    flat_keywords = keywords["shots"] + keywords["poses"] + keywords["lenses"] + keywords["scenes"]

    garment_text = garment.lower()
    for trigger, additions in GARMENT_RULES.items():
        if trigger in garment_text:
            flat_keywords.extend(additions)

    if brand:
        flat_keywords.append(str(brand.get("id", "")).replace("_", " "))
        flat_keywords.append(str(brand.get("name", "")).lower())
        best_for = brand.get("best_for", [])
        if isinstance(best_for, list):
            flat_keywords.extend(str(item).lower() for item in best_for)

    flat_keywords.extend(garment_text.replace("-", " ").split())
    return [keyword for keyword in flat_keywords if keyword]


def score_record(record: dict[str, Any], keywords: list[str]) -> int:
    blob = text_blob(record)
    score = 0
    for keyword in keywords:
        normalized = keyword.lower().replace("_", " ")
        if normalized and normalized in blob:
            score += 2 if " " in normalized else 1
    return score


def keyword_score(blob: str, keywords: list[str], weight: int) -> int:
    score = 0
    for keyword in keywords:
        normalized = keyword.lower().replace("_", " ")
        if normalized and normalized in blob:
            score += weight
    return score


def ranked_records(collection: str, keywords: list[str]) -> list[dict[str, Any]]:
    records = load_records(collection)
    return sorted(
        records,
        key=lambda record: (score_record(record, keywords), str(record.get("id", ""))),
        reverse=True,
    )


def classify_shot(shot: dict[str, Any]) -> str:
    fields = [
        shot.get("id"),
        shot.get("name"),
        shot.get("category"),
        shot.get("purpose"),
        shot.get("commercial_use"),
        shot.get("visual_goal"),
    ]
    blob = " ".join(str(field) for field in fields if field).lower().replace("_", " ")
    for category, keywords in SHOT_CATEGORY_RULES.items():
        if any(keyword in blob for keyword in keywords):
            return category
    return "front"


def compatibility_score(record: dict[str, Any], compatibility: dict[str, list[str]]) -> int:
    blob = text_blob(record)
    score = keyword_score(blob, compatibility.get("prefer", []), 8)
    score -= keyword_score(blob, compatibility.get("avoid", []), 12)
    return score


def choose_compatible_record(
    records: list[dict[str, Any]],
    keywords: list[str],
    compatibility: dict[str, list[str]],
    used_ids: set[str],
) -> dict[str, Any]:
    ranked = sorted(
        records,
        key=lambda record: (
            compatibility_score(record, compatibility),
            score_record(record, keywords),
            str(record.get("id", "")),
        ),
        reverse=True,
    )
    for record in ranked:
        record_id = str(record.get("id", ""))
        if record_id not in used_ids:
            used_ids.add(record_id)
            return record
    return ranked[0]


def pick(items: list[dict[str, Any]], index: int) -> dict[str, Any]:
    return items[index % len(items)]


def record_summary(record: dict[str, Any], fallback: str = "") -> str:
    return (
        record.get("name")
        or record.get("direction")
        or record.get("look")
        or record.get("environment")
        or fallback
    )


def lighting_for(shot: dict[str, Any], scene: dict[str, Any]) -> str:
    return str(shot.get("lighting") or scene.get("lighting") or "professional fashion lighting")


def plan_reason(
    shot: dict[str, Any],
    pose: dict[str, Any],
    lens: dict[str, Any],
    scene: dict[str, Any],
    campaign_type: str,
    garment: str,
) -> str:
    shot_goal = shot.get("purpose") or shot.get("visual_goal") or "supports the shot plan"
    shot_category = classify_shot(shot)
    return (
        f"Ranked for {campaign_type} as a {shot_category} shot because {shot.get('name')} supports this goal: "
        f"{str(shot_goal).lower()} {pose.get('name')} matches the shot type, "
        f"{lens.get('name')} fits the framing, and {scene.get('name')} supports the campaign mood for {garment}."
    )


def make_recommendation(
    rank: int,
    shot: dict[str, Any],
    pose: dict[str, Any],
    lens: dict[str, Any],
    scene: dict[str, Any],
    campaign_type: str,
    garment: str,
) -> dict[str, Any]:
    return {
        "rank": rank,
        "shot": {
            "id": shot.get("id"),
            "name": shot.get("name"),
            "path": shot.get("_path"),
        },
        "pose": {
            "id": pose.get("id"),
            "name": pose.get("name"),
            "direction": pose.get("direction"),
            "path": pose.get("_path"),
        },
        "lens": {
            "id": lens.get("id"),
            "name": lens.get("name"),
            "path": lens.get("_path"),
        },
        "scene": {
            "id": scene.get("id"),
            "name": scene.get("name"),
            "path": scene.get("_path"),
        },
        "lighting": lighting_for(shot, scene),
        "reason": plan_reason(shot, pose, lens, scene, campaign_type, garment),
    }


def build_plan(request: dict[str, Any]) -> dict[str, Any]:
    garment = str(request["garment"])
    campaign_type = str(request.get("campaign_type", "lookbook")).lower()
    brand = load_record("brands", request.get("brand_style"))
    count = int(request.get("count", 6))
    keywords = request_keywords(garment, campaign_type, brand)

    shots = ranked_records("shots", keywords)
    poses = load_records("poses")
    lenses = load_records("lenses")
    scenes = load_records("scenes")

    recommendations = []
    used_shots = set()
    used_poses: set[str] = set()
    used_scenes: set[str] = set()
    shot_index = 0
    while len(recommendations) < count and shot_index < len(shots) * 2:
        shot = pick(shots, shot_index)
        shot_index += 1
        if shot.get("id") in used_shots:
            continue
        used_shots.add(shot.get("id"))
        rec_index = len(recommendations)
        shot_category = classify_shot(shot)
        pose = choose_compatible_record(
            records=poses,
            keywords=keywords,
            compatibility=POSE_COMPATIBILITY.get(shot_category, POSE_COMPATIBILITY["front"]),
            used_ids=used_poses,
        )
        lens = choose_compatible_record(
            records=lenses,
            keywords=keywords,
            compatibility=LENS_COMPATIBILITY.get(shot_category, LENS_COMPATIBILITY["front"]),
            used_ids=set(),
        )
        scene = choose_compatible_record(
            records=scenes,
            keywords=keywords,
            compatibility=CAMPAIGN_SCENE_COMPATIBILITY.get(
                campaign_type,
                CAMPAIGN_SCENE_COMPATIBILITY["lookbook"],
            ),
            used_ids=used_scenes,
        )
        recommendations.append(
            make_recommendation(
                rank=rec_index + 1,
                shot=shot,
                pose=pose,
                lens=lens,
                scene=scene,
                campaign_type=campaign_type,
                garment=garment,
            )
        )

    return {
        "schema_version": "1.0",
        "request": {
            "garment": garment,
            "brand_style": request.get("brand_style"),
            "campaign_type": campaign_type,
            "count": count,
        },
        "brand": {
            "id": brand.get("id") if brand else None,
            "name": brand.get("name") if brand else None,
            "path": brand.get("_path") if brand else None,
        },
        "recommendations": recommendations,
    }


def load_request(path: str | Path) -> dict[str, Any]:
    request_path = Path(path)
    if not request_path.is_absolute():
        request_path = ROOT / request_path
    return load_json(request_path)


def write_json(path: str | Path, data: dict[str, Any]) -> None:
    output_path = Path(path)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Generate a ranked fashion photography shot plan.")
    parser.add_argument("request", help="Planner request JSON file")
    parser.add_argument("--out", help="Optional path to write the generated plan JSON")
    args = parser.parse_args(argv[1:])

    plan = build_plan(load_request(args.request))
    if args.out:
        write_json(args.out, plan)
    print(json.dumps(plan, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
