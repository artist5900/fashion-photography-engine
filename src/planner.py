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


def ranked_records(collection: str, keywords: list[str]) -> list[dict[str, Any]]:
    records = load_records(collection)
    return sorted(
        records,
        key=lambda record: (score_record(record, keywords), str(record.get("id", ""))),
        reverse=True,
    )


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
    return (
        f"Ranked for {campaign_type} because {shot.get('name')} supports this goal: "
        f"{str(shot_goal).lower()} {pose.get('name')} keeps the garment readable, "
        f"{lens.get('name')} fits the framing, and {scene.get('name')} supports the mood for {garment}."
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
    poses = ranked_records("poses", keywords)
    lenses = ranked_records("lenses", keywords)
    scenes = ranked_records("scenes", keywords)

    recommendations = []
    used_shots = set()
    shot_index = 0
    while len(recommendations) < count and shot_index < len(shots) * 2:
        shot = pick(shots, shot_index)
        shot_index += 1
        if shot.get("id") in used_shots:
            continue
        used_shots.add(shot.get("id"))
        rec_index = len(recommendations)
        recommendations.append(
            make_recommendation(
                rank=rec_index + 1,
                shot=shot,
                pose=pick(poses, rec_index),
                lens=pick(lenses, rec_index),
                scene=pick(scenes, rec_index),
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
