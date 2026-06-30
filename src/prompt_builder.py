import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATABASE = ROOT / "database"


def load_json(path: str | Path) -> dict[str, Any]:
    file_path = Path(path)
    if not file_path.is_absolute():
        file_path = ROOT / file_path

    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def resolve_record_path(collection: str, value: str) -> Path:
    """Resolve either a direct file path or a record id/stem inside database."""
    raw_path = Path(value)
    if raw_path.exists():
        return raw_path

    if not raw_path.is_absolute() and (ROOT / raw_path).exists():
        return ROOT / raw_path

    collection_dir = DATABASE / collection
    direct_json = collection_dir / f"{value}.json"
    if direct_json.exists():
        return direct_json

    for file_path in sorted(collection_dir.glob("*.json")):
        record = load_json(file_path)
        if value in {record.get("id"), file_path.stem}:
            return file_path

    raise FileNotFoundError(f"Could not find {collection} record: {value}")


def load_record(collection: str, value: str | None) -> dict[str, Any] | None:
    if not value:
        return None
    return load_json(resolve_record_path(collection, value))


def list_records(collection: str) -> list[dict[str, str]]:
    records = []
    for file_path in sorted((DATABASE / collection).glob("*.json")):
        record = load_json(file_path)
        records.append({
            "id": str(record.get("id", file_path.stem)),
            "name": str(record.get("name", file_path.stem.replace("_", " ").title())),
            "path": str(file_path.relative_to(ROOT)),
        })
    return records


def _camera_text(shot: dict[str, Any]) -> str:
    camera = shot.get("camera")
    if isinstance(camera, dict):
        parts = [
            camera.get("lens"),
            camera.get("height"),
            camera.get("pitch"),
            camera.get("distance"),
            f"subject ratio {camera.get('subject_ratio')}" if camera.get("subject_ratio") else None,
        ]
        return ", ".join([part for part in parts if part])
    return str(shot.get("camera_language", "natural commercial fashion lens language"))


def _brand_text(brand: dict[str, Any] | None, brand_note: str) -> str:
    if not brand:
        return brand_note

    visual_language = brand.get("visual_language", {})
    if isinstance(visual_language, dict):
        details = "; ".join(f"{key}: {value}" for key, value in visual_language.items())
    else:
        details = str(visual_language)

    avoid = brand.get("avoid", [])
    avoid_text = ", avoid " + ", ".join(avoid) if avoid else ""
    return f"{brand.get('name')}: {details}{avoid_text}"


def build_prompt(
    shot_path: str,
    scene_path: str,
    garment_description: str,
    brand_note: str = "professional fashion brand",
    pose_path: str | None = None,
    brand_path: str | None = None,
) -> str:
    shot = load_record("shots", shot_path)
    scene = load_record("scenes", scene_path)
    pose = load_record("poses", pose_path)
    brand = load_record("brands", brand_path)

    if not shot or not scene:
        raise ValueError("A shot and scene are required.")

    pose_direction = (
        pose.get("direction")
        if pose
        else shot.get("pose") or shot.get("model_direction") or "natural professional fashion pose"
    )
    purpose = shot.get("purpose") or shot.get("commercial_use") or shot.get("visual_goal")
    lighting = shot.get("lighting") or scene.get("lighting")
    scene_text = scene.get("environment") or scene.get("name")
    garment_focus = shot.get("garment_focus") or shot.get("styling_notes") or []
    if isinstance(garment_focus, list):
        garment_focus = ", ".join(garment_focus)

    lines = [
        "Professional fashion photography prompt:",
        f"- Garment: {garment_description}",
        f"- Shot: {shot.get('name')}",
        f"- Purpose: {purpose}",
        f"- Scene: {scene_text}",
        f"- Mood: {scene.get('mood', 'commercial fashion')}",
        f"- Pose: {pose_direction}",
        f"- Composition: {shot.get('composition', shot.get('prompt_notes', 'clean commercial composition'))}",
        f"- Garment focus: {garment_focus}",
        f"- Lighting: {lighting}",
        f"- Camera: {_camera_text(shot)}",
        f"- Brand style: {_brand_text(brand, brand_note)}",
    ]

    if shot.get("prompt"):
        lines.append(f"- Shot prompt notes: {shot['prompt']}")

    negative = shot.get("negative_prompt")
    if negative:
        lines.append(f"- Avoid: {negative}")

    return "\n".join(lines)


if __name__ == "__main__":
    print(
        build_prompt(
            "01_hero_low_angle",
            "urban_tiled_bus_stop",
            "oversized washed grey distressed hoodie and wide leg pants",
            brand_path="youth_streetwear",
            pose_path="02_confident_pocket_hand",
        )
    )

