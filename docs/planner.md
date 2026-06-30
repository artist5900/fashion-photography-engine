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
3. Score shots, poses, lenses, and scenes against those keywords.
4. Combine the highest-ranking records into a readable shot plan.

This keeps the planner modular and ready to connect with Garment Parser and Prompt Builder later.
