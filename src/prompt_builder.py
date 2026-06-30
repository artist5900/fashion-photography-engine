import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: str):
    with open(ROOT / path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_prompt(shot_path: str, scene_path: str, garment_description: str, brand_note: str = "streetwear editorial") -> str:
    shot = load_json(shot_path)
    scene = load_json(scene_path)
    camera = shot.get("camera", {})

    parts = [
        "Professional fashion photography",
        f"garment: {garment_description}",
        f"shot: {shot.get('name')}",
        f"purpose: {shot.get('purpose')}",
        f"camera: {camera.get('lens')} lens, {camera.get('height')}, {camera.get('pitch')}, {camera.get('distance')}",
        f"subject ratio: {camera.get('subject_ratio')}",
        f"pose: {shot.get('pose')}",
        f"scene: {scene.get('environment')}",
        f"lighting: {scene.get('lighting')}",
        f"style: {brand_note}",
        f"notes: {shot.get('prompt_notes')}"
    ]
    return ", ".join([p for p in parts if p])


if __name__ == "__main__":
    prompt = build_prompt(
        "database/shots/01_hero_low_angle.json",
        "database/scenes/urban_tiled_bus_stop.json",
        "oversized washed grey distressed hoodie and wide leg pants"
    )
    print(prompt)
