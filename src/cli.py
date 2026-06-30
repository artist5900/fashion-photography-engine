import argparse

from prompt_builder import build_prompt, list_records


def print_records(collection: str) -> None:
    for record in list_records(collection):
        print(f"{record['id']} - {record['name']} ({record['path']})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build fashion photography prompts.")
    parser.add_argument("--shot", help="Shot id or path")
    parser.add_argument("--scene", help="Scene id or path")
    parser.add_argument("--garment", help="Garment or outfit description")
    parser.add_argument("--pose", help="Optional pose id or path")
    parser.add_argument("--brand", help="Optional brand style id or path")
    parser.add_argument("--brand-note", default="professional fashion brand", help="Fallback brand note")
    parser.add_argument("--list", choices=["shots", "poses", "scenes", "brands"], help="List available records")
    args = parser.parse_args()

    if args.list:
        print_records(args.list)
        return

    missing = [name for name in ["shot", "scene", "garment"] if not getattr(args, name)]
    if missing:
        parser.error(f"Missing required arguments: {', '.join('--' + name for name in missing)}")

    print(
        build_prompt(
            shot_path=args.shot,
            scene_path=args.scene,
            garment_description=args.garment,
            brand_note=args.brand_note,
            pose_path=args.pose,
            brand_path=args.brand,
        )
    )


if __name__ == "__main__":
    main()

