# Garment Schema

Garment Parser v1 outputs a single `garment.json` document for one product or look.

The parser is designed to accept one or more product image paths now, and later connect to a vision model without changing the downstream prompt builder contract.

## Top-Level Shape

```json
{
  "schema_version": "1.0",
  "source_images": [],
  "garment": {},
  "parser": {}
}
```

## Fields

### `schema_version`

String version for the output schema. Current value: `1.0`.

### `source_images`

Array of source image records.

Each record:

```json
{
  "path": "examples/garment_images/black_denim_jacket_front.jpg",
  "view": "front",
  "exists": false
}
```

Allowed `view` values:

- `front`
- `back`
- `side`
- `detail`
- `unknown`

### `garment`

Structured garment description.

```json
{
  "category": "jacket",
  "color": ["black"],
  "material": ["denim"],
  "fit": "oversized",
  "silhouette": "boxy",
  "construction": ["panel seams", "structured shoulders"],
  "collar": "point collar",
  "sleeve": "long sleeve",
  "closure": "button front",
  "pocket": ["chest pockets"],
  "texture": ["washed texture"],
  "distressing": ["frayed edges"],
  "wash": "washed black",
  "accessories": []
}
```

Required garment keys:

- `category`
- `color`
- `material`
- `fit`
- `silhouette`
- `construction`
- `collar`
- `sleeve`
- `closure`
- `pocket`
- `texture`
- `distressing`
- `wash`
- `accessories`

When the parser cannot detect a value, use `unknown` for scalar fields and `[]` for list fields.

### `parser`

Metadata about how the garment was parsed.

```json
{
  "name": "garment_parser_v1",
  "method": "filename_and_manifest_rules",
  "confidence": "low",
  "notes": [
    "No vision model is used in v1.",
    "Fields are inferred from image filenames and optional manifest notes."
  ]
}
```

## Design Notes

Garment Parser v1 is intentionally simple:

- It does not claim visual recognition accuracy.
- It produces a stable schema for downstream prompt generation.
- It keeps source image references attached for auditability.
- It can later be upgraded to use image embeddings or a multimodal model while preserving the same output shape.

