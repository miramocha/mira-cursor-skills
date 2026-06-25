# VRoid VRM Blender cleanup — examples

## Phase A — Material names

| Before | After |
|--------|-------|
| `N00_006_01_Shoes_01_CLOTH (Instance)` | `Shoes_01_CLOTH (Instance)` |
| `N00_000_01_Body_00_SKIN (Instance)` | `Body_00_SKIN (Instance)` |
| `MToon Outline (N00_000_Hair_00_HAIR_01 (Instance))` | `MToon Outline (Hair_00_HAIR_01 (Instance))` |

## Phase B — Material slugs (for texture naming)

| Material name | Slug |
|---------------|------|
| `Body_00_SKIN (Instance)` | `body_00_skin` |
| `MToon Outline (Face_00_SKIN (Instance))` | `outline_face_00_skin` |

## Phase B — Per-material textures

Material `Body_00_SKIN (Instance)` after Phase A:

| Old image stem | Slot | New name |
|----------------|------|----------|
| `..._10` (shared lit + shade) | base + shade | `body_00_skin_base` |
| `..._11` | normal | `body_00_skin_normal` |

## Phase B — Global placeholders

| Before | After |
|--------|-------|
| `Shader_NoneBlack` | `mtoon_none_black` |
| `Shader_NoneBlack.001` | `mtoon_none_black` (merged datablock) |
| `Shader_NoneNormal.001` | `mtoon_none_normal` |
| `MatcapWarp` | `mtoon_matcap_warp` |
| `MatcapWarp_01` | `mtoon_matcap_warp_face` |

## Phase B — Audit table row (illustrative)

```
old_image | old_path | new_image | new_path | used_by_materials
--- | --- | --- | --- | ---
Body_00_SKIN_11 | D:/avatar/textures/Body_00_SKIN_11.png | body_00_skin_normal | D:/avatar/textures/body_00_skin_normal.png | Body_00_SKIN (Instance)
Shader_NoneBlack.001 | D:/avatar/textures/Shader_NoneBlack.png | mtoon_none_black | D:/avatar/textures/mtoon_none_black.png | Body_00_SKIN (Instance), Face_00_SKIN (Instance), ...
```

## Phase B — Outline sharing parent textures

When `MToon Outline (Face_00_SKIN (Instance))` uses the same PNG filepath as `Face_00_SKIN (Instance)` for base color:

- Target: `face_00_skin_base` (parent slug wins via filepath dedupe)
- Not: `outline_face_00_skin_base`

## Phase C — Shape keys

```python
reset_shape_keys("Face", dry_run=False)
# → all key_blocks on object/mesh "Face" set to 0.0
```

## MCP dry-run snippet

```python
SKILL = r"C:\Users\miral\.cursor\skills\vroid-vrm-blender-cleanup\scripts"

exec(open(SKILL + r"\clean_vroid_material_names.py").read())
result = run_phase_a(dry_run=True)
```

```python
exec(open(SKILL + r"\rename_mtoon_textures.py").read())
result = audit_mtoon_textures()
```
