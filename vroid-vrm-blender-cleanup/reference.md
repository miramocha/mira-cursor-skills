# VRoid VRM Blender cleanup — reference

## Phase A — VRoid material prefix patterns

| Pattern | Example removed |
|---------|-----------------|
| `N\d{2}_\d{3}_\d{2}_` | `N00_006_01_`, `N00_000_01_` |
| `N\d{2}_\d{3}_[A-Za-z]+_\d{2}_` | `N00_000_Hair_00_` |

Phase A **does not** strip ` (Instance)` from material names. Phase B `material_slug()` strips it when computing texture names.

## Phase B — Find MToon materials

Walk `bpy.data.materials` where the node tree contains group node `Mtoon1Material.Mtoon1Output` (VRM Add-on MToon 1.0).

## MToon texture slots

| MToon node name | Suffix |
|-----------------|--------|
| `Mtoon1BaseColorTexture.Image` | `base` |
| `Mtoon1ShadeMultiplyTexture.Image` | `shade` (collapse to `base` if same image as lit) |
| `Mtoon1NormalTexture.Image` | `normal` |
| `Mtoon1EmissiveTexture.Image` | `emissive` |
| `Mtoon1MatcapTexture.Image` | `matcap` |
| `Mtoon1RimMultiplyTexture.Image` | `rim` |
| `Mtoon1OutlineWidthMultiplyTexture.Image` | `outline_width` |
| `Mtoon1ShadingShiftTexture.Image` | `shading_shift` |
| `Mtoon1UvAnimationMaskTexture.Image` | `uv_anim_mask` |

Skip slots with no image assigned. Empty rim / outline / matcap slots are normal.

## Material slug rules

1. Remove ` (Instance)` for slug computation only.
2. `MToon Outline (Face_00_SKIN (Instance))` → `outline_face_00_skin`
3. Otherwise lowercase material name: `Body_00_SKIN` → `body_00_skin`

Per-material unique textures: `{material_slug}_{suffix}.png`

## Global shared textures

Rename once; all materials keep pointing at the same image.

| Current stem(s) | New name |
|-----------------|----------|
| `Shader_NoneBlack`, `Shader_NoneBlack.001` | `mtoon_none_black` |
| `Shader_NoneNormal`, `Shader_NoneNormal.001` | `mtoon_none_normal` |
| `MatcapWarp` | `mtoon_matcap_warp` |
| `MatcapWarp_01` | `mtoon_matcap_warp_face` |

## Phase B execution phases

### Phase 1 — Audit (dry-run, no writes)

- Walk all MToon materials; collect `(image, material_slug, role_suffix, filepath)` per assigned slot.
- Build rename map:
  - Global stem match → global target name
  - Lit + shade same image → one `base` per material
  - Else → `{slug}_{suffix}`
- Dedupe by absolute filepath — `_02` and `_02.001` sharing same PNG → one target (prefer `(Instance)` material slug, non-outline).
- Detect collisions (two different files → same target name); append `_02` suffix if needed.
- Print table: `old_image | old_path | new_image | new_path | used_by_materials`
- **Stop for approval before Phase 2.**

### Phase 2 — Apply (after approval)

1. **Save .blend first.**
2. Per unique filepath under `//textures/`: `os.rename(old, new)` if file exists.
3. If packed (`img.packed_file`): skip disk rename; datablock rename is enough.
4. Paths outside project `textures/`: report; default datablock-only unless `COPY_EXTERNAL=True`.
5. Rename `bpy.data.images`; set `img.filepath = f"//textures/{new_name}.png"`.
6. Merge duplicates: reassign all `TEX_IMAGE` nodes from `.001` to canonical image; remove unused datablocks.
7. `img.reload()` where external files exist.

### Phase 3 — Verify

- Re-scan all MToon materials: every assigned `TEX_IMAGE` has valid image.
- No legacy names (`Shader_*`, `MatcapWarp*`, `N00_*`, trailing `_NN` stems) unless intentionally kept.
- Spot-check one body material (normal + base + globals).
- Report empty optional slots separately (not errors).
- Optional follow-up: **File → External Data → Unpack All Into Files** to write renamed PNGs when textures were packed.

## Edge cases

| Case | Policy |
|------|--------|
| Lit + shade same PNG | One `base` rename; both nodes keep same image |
| Outline mat shares parent textures | Same target as parent (`face_00_skin_base`), not `outline_*`, via filepath dedupe + non-outline preference |
| Empty texture slots | Skip |
| Name collision | Append numeric suffix (`_02`) + report |
| Files outside `//textures/` | Report in dry-run; datablock-only default |
| All textures packed in .blend | 0 disk renames expected; unpack optional follow-up |

## Phase C — Shape keys

- Match mesh by object name or mesh data name (default `Face`).
- Set every `key_blocks[].value` to `0.0`.
- Does not rename shape keys — use **vroid-shapekey-remap** for `Fcl_*` rename.

## Out of scope

- Renaming materials (except Phase A VRoid prefix strip)
- Changing MToon shader values
- VRM export re-test
- Bone rename (**blender-bone-remap**)
