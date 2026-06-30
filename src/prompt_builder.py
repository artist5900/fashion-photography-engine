import json
import sys
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


def _join_items(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    if value is None:
        return ""
    return str(value)


def _clean_sentence(value: Any) -> str:
    return str(value or "").strip().rstrip(".")


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


def _lens_text(lens: dict[str, Any] | None, shot: dict[str, Any]) -> str:
    if not lens:
        return _camera_text(shot)

    parts = [
        lens.get("name"),
        lens.get("focal_length"),
        lens.get("look"),
        lens.get("camera_guidance"),
        lens.get("depth_of_field"),
    ]
    return ", ".join([_clean_sentence(part) for part in parts if part])


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
    lens_path: str | None = None,
    model_description: str = "professional fashion model",
    output_format: str = "paragraph",
) -> str:
    shot = load_record("shots", shot_path)
    scene = load_record("scenes", scene_path)
    pose = load_record("poses", pose_path)
    brand = load_record("brands", brand_path)
    lens = load_record("lenses", lens_path)

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
    composition = shot.get("composition", shot.get("prompt_notes", "clean commercial composition"))
    prompt_notes = shot.get("prompt")
    negative_notes = [shot.get("negative_prompt")]
    if lens and lens.get("avoid"):
        negative_notes.append("lens avoid: " + _join_items(lens.get("avoid")))

    sections = [
        f"Create a production-ready professional fashion photograph of {_clean_sentence(model_description)} wearing {_clean_sentence(garment_description)}.",
        f"Shot: {shot.get('name')} with the goal to {_clean_sentence(purpose).lower()}.",
        f"Pose: {_clean_sentence(pose_direction)}.",
        f"Lens and camera: {_clean_sentence(_lens_text(lens, shot))}.",
        f"Scene: {_clean_sentence(scene_text)}; surface: {_clean_sentence(scene.get('surface', 'clean production surface'))}; mood: {_clean_sentence(scene.get('mood', 'commercial fashion'))}.",
        f"Brand style: {_clean_sentence(_brand_text(brand, brand_note))}.",
        f"Composition: {_clean_sentence(composition)}.",
        f"Garment focus: {_clean_sentence(_join_items(garment_focus))}.",
        f"Lighting: {_clean_sentence(lighting)}.",
    ]

    if prompt_notes:
        sections.append(f"Additional shot notes: {_clean_sentence(prompt_notes)}.")

    negative_text = "; ".join([note for note in negative_notes if note])
    if negative_text:
        sections.append(f"Avoid: {_clean_sentence(negative_text)}.")

    if output_format == "bullets":
        return "Production-ready fashion photography prompt:\n- " + "\n- ".join(sections)
    return " ".join(sections)


def build_prompt_from_file(path: str | Path) -> str:
    request = load_json(path)
    return build_prompt(
        shot_path=request["shot"],
        pose_path=request.get("pose"),
        lens_path=request.get("lens"),
        scene_path=request["scene"],
        brand_path=request.get("brand"),
        garment_description=request["garment"],
        model_description=request.get("model", "professional fashion model"),
        brand_note=request.get("brand_note", "professional fashion brand"),
        output_format=request.get("output_format", "paragraph"),
    )


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: python src/prompt_builder.py examples/example.json", file=sys.stderr)
        return 2

    print(build_prompt_from_file(argv[1]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
