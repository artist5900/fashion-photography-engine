import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

SCHEMA_VERSION = "1.0"
PARSER_NAME = "garment_parser_v1"

LIST_FIELDS = [
    "color",
    "material",
    "construction",
    "pocket",
    "texture",
    "distressing",
    "accessories",
]

GARMENT_FIELDS = [
    "category",
    "color",
    "material",
    "fit",
    "silhouette",
    "construction",
    "collar",
    "sleeve",
    "closure",
    "pocket",
    "texture",
    "distressing",
    "wash",
    "accessories",
]

SCALAR_FIELDS = [
    field for field in GARMENT_FIELDS
    if field not in LIST_FIELDS
]

RULES = {
    "category": {
        "jacket": ["jacket", "coat", "blazer", "parka", "trench"],
        "shirt": ["shirt", "blouse", "buttondown"],
        "hoodie": ["hoodie", "sweatshirt"],
        "pants": ["pants", "trousers", "jeans", "cargo"],
        "dress": ["dress", "gown"],
        "skirt": ["skirt"],
        "top": ["top", "tank", "tee", "tshirt", "t-shirt"],
    },
    "color": {
        "black": ["black", "charcoal"],
        "white": ["white", "ivory", "cream"],
        "grey": ["grey", "gray", "silver"],
        "blue": ["blue", "navy", "indigo"],
        "brown": ["brown", "tan", "camel"],
        "green": ["green", "olive", "khaki"],
        "red": ["red", "burgundy"],
        "pink": ["pink", "blush"],
        "yellow": ["yellow", "mustard"],
        "purple": ["purple", "lavender"],
    },
    "material": {
        "denim": ["denim", "jean"],
        "cotton": ["cotton", "canvas"],
        "wool": ["wool", "tweed"],
        "leather": ["leather", "suede"],
        "silk": ["silk", "satin"],
        "linen": ["linen"],
        "knit": ["knit", "ribbed"],
        "nylon": ["nylon", "technical", "shell"],
    },
    "fit": {
        "oversized": ["oversized", "relaxed"],
        "regular": ["regular", "classic"],
        "slim": ["slim", "fitted"],
        "cropped": ["cropped"],
        "wide": ["wide", "wideleg", "wide-leg"],
    },
    "silhouette": {
        "boxy": ["boxy"],
        "straight": ["straight"],
        "a-line": ["aline", "a-line"],
        "tailored": ["tailored", "structured"],
        "flowing": ["flowing", "fluid", "draped"],
        "voluminous": ["volume", "voluminous", "puff"],
    },
    "construction": {
        "panel seams": ["panel", "panels", "seam", "seams"],
        "structured shoulders": ["shoulder", "shoulders", "structured"],
        "pleats": ["pleat", "pleats", "pleated"],
        "rib trim": ["rib", "ribbed", "ribbing"],
        "lined interior": ["lined", "lining"],
    },
    "collar": {
        "point collar": ["point collar", "collar"],
        "lapel collar": ["lapel", "lapels"],
        "hood": ["hood", "hooded"],
        "crew neck": ["crewneck", "crew neck"],
        "v-neck": ["vneck", "v-neck"],
        "mock neck": ["mockneck", "mock neck"],
    },
    "sleeve": {
        "long sleeve": ["long sleeve", "long-sleeve", "longsleeve", "sleeve", "sleeves"],
        "short sleeve": ["short sleeve", "short-sleeve", "shortsleeve"],
        "sleeveless": ["sleeveless", "tank"],
        "puff sleeve": ["puff sleeve", "puffed"],
    },
    "closure": {
        "button front": ["button", "buttons", "buttoned"],
        "zip front": ["zip", "zipper", "zipped"],
        "pullover": ["pullover"],
        "wrap closure": ["wrap", "tie"],
        "open front": ["open front", "open-front"],
    },
    "pocket": {
        "chest pockets": ["chest pocket", "chest pockets"],
        "side pockets": ["side pocket", "side pockets"],
        "cargo pockets": ["cargo pocket", "cargo pockets"],
        "patch pockets": ["patch pocket", "patch pockets"],
        "welt pockets": ["welt pocket", "welt pockets"],
    },
    "texture": {
        "washed texture": ["washed", "wash"],
        "ribbed texture": ["ribbed", "rib"],
        "smooth texture": ["smooth"],
        "matte texture": ["matte"],
        "sheer texture": ["sheer"],
        "quilted texture": ["quilted", "quilt"],
    },
    "distressing": {
        "frayed edges": ["frayed", "fray"],
        "ripped distressing": ["ripped", "rip", "distressed"],
        "faded areas": ["faded", "fade"],
        "raw hem": ["raw hem", "raw-edge", "raw edge"],
    },
    "wash": {
        "washed black": ["washed black", "black washed"],
        "light wash": ["light wash", "light-wash"],
        "medium wash": ["medium wash", "mid wash"],
        "dark wash": ["dark wash", "dark-wash"],
        "acid wash": ["acid wash", "acid-wash"],
    },
    "accessories": {
        "belt": ["belt", "belted"],
        "chain": ["chain"],
        "scarf": ["scarf"],
        "hood drawcord": ["drawcord", "drawstring"],
        "metal hardware": ["hardware", "metal"],
    },
}


def load_json(path: str | Path) -> dict[str, Any]:
    file_path = Path(path)
    if not file_path.is_absolute():
        file_path = ROOT / file_path
    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def normalize_text(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[_\-./]+", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def image_view(path: str) -> str:
    text = normalize_text(Path(path).stem)
    for view in ["front", "back", "side", "detail"]:
        if view in text:
            return view
    return "unknown"


def source_image(path: str) -> dict[str, Any]:
    raw_path = Path(path)
    resolved = raw_path if raw_path.is_absolute() else ROOT / raw_path
    return {
        "path": path,
        "view": image_view(path),
        "exists": resolved.exists(),
    }


def match_values(field: str, text: str) -> list[str]:
    matches = []
    for value, keywords in RULES[field].items():
        if any(keyword in text for keyword in keywords):
            matches.append(value)
    return matches


def empty_garment() -> dict[str, Any]:
    garment: dict[str, Any] = {}
    for field in GARMENT_FIELDS:
        garment[field] = [] if field in LIST_FIELDS else "unknown"
    return garment


def parse_garment(image_paths: list[str], notes: str = "") -> dict[str, Any]:
    combined_text = normalize_text(" ".join(image_paths + [notes]))
    garment = empty_garment()

    for field in LIST_FIELDS:
        garment[field] = match_values(field, combined_text)

    for field in SCALAR_FIELDS:
        matches = match_values(field, combined_text)
        if matches:
            garment[field] = matches[0]

    confidence = "medium" if notes else "low"

    return {
        "schema_version": SCHEMA_VERSION,
        "source_images": [source_image(path) for path in image_paths],
        "garment": garment,
        "parser": {
            "name": PARSER_NAME,
            "method": "filename_and_manifest_rules",
            "confidence": confidence,
            "notes": [
                "No vision model is used in v1.",
                "Fields are inferred from image filenames and optional manifest notes.",
            ],
        },
    }


def parse_manifest(path: str | Path) -> dict[str, Any]:
    manifest = load_json(path)
    images = manifest.get("images", [])
    if not isinstance(images, list) or not images:
        raise ValueError("Manifest must include a non-empty images array.")
    return parse_garment([str(image) for image in images], notes=str(manifest.get("notes", "")))


def write_output(data: dict[str, Any], output_path: str | Path) -> None:
    file_path = Path(output_path)
    if not file_path.is_absolute():
        file_path = ROOT / file_path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse garment image paths into garment.json.")
    parser.add_argument("inputs", nargs="+", help="Image paths or one JSON manifest with an images array")
    parser.add_argument("--out", default="garment.json", help="Output garment JSON path")
    args = parser.parse_args()

    if len(args.inputs) == 1 and args.inputs[0].endswith(".json"):
        result = parse_manifest(args.inputs[0])
    else:
        result = parse_garment(args.inputs)

    write_output(result, args.out)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
