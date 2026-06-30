# Sprint 2 Summary

Sprint 2 adds Garment Parser v1.

## Goal

Turn one or more garment product image paths into a structured `garment.json` that can later connect to Prompt Builder.

## Shipped

- Garment output schema in `docs/garment_schema.md`
- Modular parser in `src/garment_parser.py`
- Example parser input in `examples/garment_input.json`
- Example parser output in `examples/garment.json`
- Example image folder note in `examples/garment_images/README.md`
- README usage instructions

## Detected Fields

Garment Parser v1 outputs:

- category
- color
- material
- fit
- silhouette
- construction
- collar
- sleeve
- closure
- pocket
- texture
- distressing
- wash
- accessories

## Current Method

The v1 parser uses deterministic rules over image filenames and optional manifest notes. It does not use a vision model yet.

This keeps the module simple, auditable, and ready for a later image-recognition backend.

