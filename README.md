# Fashion Photography Engine

Fashion Photography Engine is an open-source prompt and shot-planning library for professional fashion photography.

The project helps creative teams, photographers, stylists, ecommerce brands, and AI image-generation builders turn a loose campaign idea into structured commercial shot plans and production-ready prompts.

Current release: `v0.2.0`

## What This Project Does

- Defines reusable fashion photography shot types
- Turns creative direction into clear prompt ingredients
- Documents poses, scenes, brands, lenses, and production references
- Keeps prompts consistent across ecommerce, editorial, campaign, and lookbook work
- Provides a simple foundation for future generators, APIs, and creative tools

## Project Structure

```text
docs/               Project notes, release notes, and contribution guidance
database/
  shots/            Commercial fashion shot definitions
  poses/            Pose references and pose language
  scenes/           Scene and location references
  brands/           Brand-style references
  lenses/           Lens and camera-language references
src/                Future source code for generators and tooling
templates/          Prompt and shot-plan templates
examples/           Example shot plans and generated prompt sets
```

## Quick Start

No installation is required. The first builder uses only the Python standard library.

Run the visual app:

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app lets you enter a garment description, choose a brand style and campaign type, generate a ranked lookbook plan, generate prompts, and download the request, plan, and prompt files.

Generate a production-ready prompt from the included example:

```bash
python3 src/prompt_builder.py examples/example.json
```

List available shots:

```bash
python3 src/cli.py --list shots
```

List available poses, scenes, or brand styles:

```bash
python3 src/cli.py --list poses
python3 src/cli.py --list scenes
python3 src/cli.py --list brands
```

Generate a prompt:

```bash
python3 src/prompt_builder.py examples/example.json
```

The output is one production-ready fashion photography prompt combining garment, shot, pose, lens, scene, and brand-style guidance.

Convert a full lookbook plan into multiple production prompts:

```bash
python3 src/plan_to_prompts.py examples/lookbook_plan.json --out examples/lookbook_prompts.md
```

The exporter reads each recommendation in the plan and writes one Markdown prompt per ranked shot.

## Sprint 3

Sprint 3 converts a complete lookbook plan into multiple production-ready prompts.

```bash
python3 src/plan_to_prompts.py examples/lookbook_plan.json --out examples/lookbook_prompts.md
```

The output is saved to `examples/lookbook_prompts.md`.

## Garment Parser v1

Garment Parser v1 turns one or more garment product image paths into a structured `garment.json`.

Run the included example:

```bash
python3 src/garment_parser.py examples/garment_input.json --out examples/garment.json
```

Or pass image paths directly:

```bash
python3 src/garment_parser.py product_front.jpg product_back.jpg --out garment.json
```

The v1 parser uses filenames and optional manifest notes. It does not use a vision model yet; the output schema is designed so a future image model can plug in without changing the prompt-builder contract.

## Sprint 1

Sprint 1 adds the first usable prompt generation system:

- 10 additional shot definitions
- 20 pose definitions
- 10 scene definitions
- 5 brand style files
- 5 lens definitions
- Improved prompt builder
- Simple CLI for listing records and generating prompts

## v0.1 Scope

Version 0.1 ships the first practical foundation:

- Repository initialized
- Core folder structure added
- Ten commercial fashion shot definitions created
- A reusable prompt template added
- Basic documentation included

## Shot Definition Format

Each shot definition is stored as JSON and includes:

- `id`
- `name`
- `category`
- `commercial_use`
- `visual_goal`
- `composition`
- `model_direction`
- `styling_notes`
- `lighting`
- `camera_language`
- `prompt`
- `negative_prompt`

This format is intentionally simple so it can be read by humans, edited by contributors, and later consumed by scripts or applications.

## Example Use

1. Choose a shot definition from `database/shots/`.
2. Choose a pose, lens, scene, and brand style.
3. Add those IDs to an example JSON file.
4. Run `python3 src/prompt_builder.py examples/example.json`.
5. Use the final prompt for AI image generation or as a human production brief.

## Design Principles

- Professional enough for commercial work
- Simple enough for contributors
- Structured enough for future automation
- Flexible across ecommerce, campaign, editorial, and social content

## Roadmap

- Add style packs for ecommerce, luxury, streetwear, activewear, and beauty

## Milestone History

- Sprint 1: Prompt Builder
- Sprint 2: Photography Planner
- Sprint 3: Plan to Prompts Exporter

## Current Status

Fashion Photography Engine now supports a lightweight workflow from garment description to ranked shot plan to multiple production-ready prompts.

## License

License to be added before public distribution.
