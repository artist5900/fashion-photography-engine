# Fashion Photography Engine v0.2.0

Version 0.2.0 is the first usable workflow release.

## Highlights

- Generate one production-ready prompt from structured shot, pose, lens, scene, brand, and garment inputs.
- Build ranked lookbook shot plans from a garment description, brand style, and campaign type.
- Validate planner quality to avoid obvious shot-pose mismatches.
- Export a complete shot plan into multiple production-ready Markdown prompts.
- Parse garment image paths and manifest notes into a structured `garment.json` schema.

## Completed Work

- Sprint 1: Prompt Builder
- Sprint 2: Photography Planner
- Sprint 3: Plan to Prompts Exporter

## Included

- `src/prompt_builder.py`
- `src/planner.py`
- `src/validate_plan.py`
- `src/plan_to_prompts.py`
- `src/garment_parser.py`
- `examples/lookbook_request.json`
- `examples/lookbook_plan.json`
- `examples/lookbook_prompts.md`
- `examples/garment_input.json`
- `examples/garment.json`
- `docs/garment_schema.md`
- `docs/planner.md`

## Notes

This release stays intentionally lightweight. It uses JSON databases and Python standard-library tools so contributors can inspect, extend, and run the project without setup friction.

Garment Parser v1 is rule-based and does not perform real image recognition yet. It establishes the schema and module boundary for a future vision backend.
