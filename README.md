# Fashion Photography Engine

Fashion Photography Engine is an open-source prompt and shot-planning library for professional fashion photography.

The project helps creative teams, photographers, stylists, ecommerce brands, and AI image-generation builders turn a loose campaign idea into structured commercial shot plans and production-ready prompts.

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
2. Replace the product, brand, model, scene, and styling details.
3. Combine the shot definition with `templates/fashion_prompt_template.md`.
4. Use the final prompt for AI image generation or as a human production brief.

## Design Principles

- Professional enough for commercial work
- Simple enough for contributors
- Structured enough for future automation
- Flexible across ecommerce, campaign, editorial, and social content

## Roadmap

- Add pose, scene, lens, and brand-style databases
- Add complete example campaigns
- Add prompt-generation scripts
- Add validation for shot definition files
- Add style packs for ecommerce, luxury, streetwear, activewear, and beauty

## License

License to be added before public distribution.
