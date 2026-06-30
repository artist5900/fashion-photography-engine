# Photography Planner

The Photography Planner creates a complete shot plan instead of a single prompt.

It uses the existing database records for shots, poses, lenses, scenes, and brand styles. It does not duplicate database content inside the planner output.

## Input

The planner accepts a JSON request:

```json
{
  "garment": "oversized black washed denim jacket with button front and chest pockets",
  "brand_style": "youth_streetwear",
  "campaign_type": "lookbook",
  "count": 6
}
```

Required fields:

- `garment`
- `brand_style`
- `campaign_type`

Optional field:

- `count`, default `6`

## Output

The planner returns a ranked list of shot recommendations.

Each recommendation includes:

- `shot`
- `pose`
- `lens`
- `scene`
- `lighting`
- `reason`

## Usage

```bash
python3 src/planner.py examples/lookbook_request.json
```

The command prints a JSON shot plan to stdout.

Write the plan to a file:

```bash
python3 src/planner.py examples/lookbook_request.json --out examples/lookbook_plan.json
```

## Method

Planner v1 uses a simple scoring model:

1. Load records from the existing databases.
2. Build keywords from garment description, brand style, and campaign type.
3. Score shots against those keywords.
4. Classify each selected shot as front, walking, back, detail, seated, group, flat lay, or active.
5. Choose a compatible pose and lens for that shot category.
6. Choose a scene that fits the campaign type.
7. Combine the matched records into a readable shot plan.

## Compatibility Rules

Planner matching is intentionally lightweight, but it prevents obvious mismatches:

- Hero/front shots prefer relaxed, pocket, three-quarter, or confident standing poses.
- Detail shots prefer cuff, collar, hand, waistband, bag, or other close-detail poses.
- Walking shots prefer walking, stride, or profile walking poses.
- Back shots prefer back-facing or over-shoulder poses.
- Detail shots prefer macro or portrait-detail lenses; front and back shots prefer clean commercial lenses.
- Campaign type influences scene selection, so ecommerce stays studio-oriented while lookbook and campaign plans can use richer locations.

This keeps the planner modular and ready to connect with Garment Parser and Prompt Builder later.
