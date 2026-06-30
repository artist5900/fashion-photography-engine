import json
import sys
from pathlib import Path
from typing import Any

import planner

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FIELDS = ["shot", "pose", "lens", "scene", "lighting", "reason"]

DETAIL_POSE_TERMS = ["detail", "cuff", "collar", "waistband", "bag"]
WALKING_POSE_TERMS = ["walk", "walking", "stride", "profile"]
BACK_POSE_TERMS = ["back", "over shoulder", "face away", "away from camera"]
SEATED_POSE_TERMS = ["seated", "sit", "floor"]


def load_json(path: str | Path) -> dict[str, Any]:
    file_path = Path(path)
    if not file_path.is_absolute():
        file_path = ROOT / file_path
    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def recommendation_label(index: int, recommendation: dict[str, Any]) -> str:
    rank = recommendation.get("rank", index + 1)
    shot = recommendation.get("shot", {}).get("id", "unknown-shot")
    return f"recommendation {rank} ({shot})"


def nested_text(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(nested_text(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(nested_text(item) for item in value)
    return str(value or "")


def has_any(text: str, terms: list[str]) -> bool:
    normalized = text.lower().replace("_", " ")
    return any(term in normalized for term in terms)


def load_shot_record(recommendation: dict[str, Any]) -> dict[str, Any]:
    shot = recommendation.get("shot", {})
    shot_id = shot.get("id")
    if not shot_id:
        return {}
    return planner.load_record("shots", str(shot_id)) or {}


def validate_required_fields(recommendation: dict[str, Any], label: str) -> list[str]:
    reasons = []
    for field in REQUIRED_FIELDS:
        if field not in recommendation or not recommendation.get(field):
            reasons.append(f"{label}: missing required field '{field}'.")
    return reasons


def validate_pairing(recommendation: dict[str, Any], label: str) -> list[str]:
    reasons = []
    shot_record = load_shot_record(recommendation)
    if not shot_record:
        reasons.append(f"{label}: cannot resolve shot record.")
        return reasons

    shot_category = planner.classify_shot(shot_record)
    pose_text = nested_text(recommendation.get("pose", {}))

    if shot_category == "front" and has_any(pose_text, DETAIL_POSE_TERMS):
        reasons.append(f"{label}: front shot uses a detail pose.")

    if shot_category == "detail" and has_any(pose_text, WALKING_POSE_TERMS):
        reasons.append(f"{label}: detail shot uses a walking pose.")

    if shot_category == "walking" and not has_any(pose_text, WALKING_POSE_TERMS):
        reasons.append(f"{label}: walking shot does not use a walking or motion pose.")

    if shot_category == "back" and not has_any(pose_text, BACK_POSE_TERMS):
        reasons.append(f"{label}: back shot does not use a back-facing pose.")

    if shot_category == "seated" and not has_any(pose_text, SEATED_POSE_TERMS):
        reasons.append(f"{label}: seated shot does not use a seated pose.")

    return reasons


def validate_plan(plan: dict[str, Any]) -> list[str]:
    recommendations = plan.get("recommendations")
    if not isinstance(recommendations, list) or not recommendations:
        return ["Plan must include a non-empty recommendations list."]

    reasons = []
    for index, recommendation in enumerate(recommendations):
        label = recommendation_label(index, recommendation)
        reasons.extend(validate_required_fields(recommendation, label))
        reasons.extend(validate_pairing(recommendation, label))
    return reasons


def main(argv: list[str]) -> int:
    plan_path = argv[1] if len(argv) > 1 else "examples/lookbook_plan.json"
    reasons = validate_plan(load_json(plan_path))

    if reasons:
        print("FAIL")
        for reason in reasons:
            print(f"- {reason}")
        return 1

    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
