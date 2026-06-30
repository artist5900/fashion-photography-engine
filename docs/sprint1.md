# Sprint 1 Summary

Sprint 1 finishes the first usable prompt generation system for Fashion Photography Engine.

## Shipped

- 20 pose definitions in `database/poses`
- 5 lens definitions in `database/lenses`
- 11 scene definitions in `database/scenes`
- 5 JSON brand style definitions in `database/brands`
- Request-file prompt builder in `src/prompt_builder.py`
- Example prompt request in `examples/example.json`
- README Quick Start for generating the first prompt

## Prompt Builder

The builder now combines:

- Shot
- Pose
- Lens
- Scene
- Brand
- Garment
- Optional model description

Run:

```bash
python3 src/prompt_builder.py examples/example.json
```

The command outputs one production-ready fashion photography prompt.

## Verification

Completed checks:

- All JSON files load successfully
- `python3 src/prompt_builder.py examples/example.json` outputs a complete production prompt
- Repository structure remains unchanged
- Sprint 1 work was committed in separate feature commits

