import argparse
import json
from pathlib import Path
from typing import Any

from prompt_builder import build_prompt

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: str | Path) -> dict[str, Any]:
    file_path = Path(path)
    if not file_path.is_absolute():
        file_path = ROOT / file_path
    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_text(path: str | Path, content: str) -> None:
    file_path = Path(path)
    if not file_path.is_absolute():
        file_path = ROOT / file_path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")


def recommendation_id(recommendation: dict[str, Any], field: str) -> str:
    value = recommendation.get(field, {})
    if not isinstance(value, dict) or not value.get("id"):
        raise ValueError(f"Recommendation {recommendation.get('rank')} is missing {field}.id")
    return str(value["id"])


def prompt_for_recommendation(plan: dict[str, Any], recommendation: dict[str, Any]) -> str:
    return build_prompt(
        shot_path=recommendation_id(recommendation, "shot"),
        pose_path=recommendation_id(recommendation, "pose"),
        lens_path=recommendation_id(recommendation, "lens"),
        scene_path=recommendation_id(recommendation, "scene"),
        brand_path=plan.get("request", {}).get("brand_style"),
        garment_description=str(plan.get("request", {}).get("garment", "")),
        output_format="paragraph",
    )


def markdown_for_plan(plan: dict[str, Any]) -> str:
    recommendations = plan.get("recommendations", [])
    if not isinstance(recommendations, list) or not recommendations:
        raise ValueError("Plan must include a non-empty recommendations list.")

    request = plan.get("request", {})
    lines = [
        "# Lookbook Production Prompts",
        "",
        f"Garment: {request.get('garment', 'unknown')}",
        f"Brand style: {request.get('brand_style', 'unknown')}",
        f"Campaign type: {request.get('campaign_type', 'unknown')}",
        "",
    ]

    for recommendation in recommendations:
        rank = recommendation.get("rank", "")
        shot = recommendation.get("shot", {})
        shot_name = shot.get("name", shot.get("id", "Unknown Shot"))
        reason = recommendation.get("reason", "")
        prompt = prompt_for_recommendation(plan, recommendation)

        lines.extend([
            f"## {rank}. {shot_name}",
            "",
            f"Reason: {reason}",
            "",
            "Prompt:",
            "",
            prompt,
            "",
        ])

    return "\n".join(lines).rstrip() + "\n"


def export_plan_to_prompts(plan_path: str | Path, output_path: str | Path) -> str:
    markdown = markdown_for_plan(load_json(plan_path))
    write_text(output_path, markdown)
    return markdown


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert a lookbook plan into production prompts.")
    parser.add_argument("plan", nargs="?", default="examples/lookbook_plan.json", help="Plan JSON file")
    parser.add_argument("--out", default="examples/lookbook_prompts.md", help="Output Markdown file")
    args = parser.parse_args()

    markdown = export_plan_to_prompts(args.plan, args.out)
    print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

