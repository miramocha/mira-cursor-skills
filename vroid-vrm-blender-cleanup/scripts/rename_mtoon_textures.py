"""
Rename VRM MToon 1.0 texture image datablocks and external PNGs under //textures/.
Run via MCP execute_blender_code or Blender Scripting workspace.

    audit = audit_mtoon_textures()
    apply_mtoon_texture_renames(audit["rename_map"])
    verify = verify_mtoon_textures()
"""

from __future__ import annotations

import os
import re
from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple

import bpy

COPY_EXTERNAL = False

GLOBAL_STEMS = {
    "Shader_NoneBlack": "mtoon_none_black",
    "Shader_NoneNormal": "mtoon_none_normal",
    "MatcapWarp": "mtoon_matcap_warp",
    "MatcapWarp_01": "mtoon_matcap_warp_face",
}

SLOT_SUFFIX = {
    "Mtoon1BaseColorTexture.Image": "base",
    "Mtoon1ShadeMultiplyTexture.Image": "shade",
    "Mtoon1NormalTexture.Image": "normal",
    "Mtoon1EmissiveTexture.Image": "emissive",
    "Mtoon1MatcapTexture.Image": "matcap",
    "Mtoon1RimMultiplyTexture.Image": "rim",
    "Mtoon1OutlineWidthMultiplyTexture.Image": "outline_width",
    "Mtoon1ShadingShiftTexture.Image": "shading_shift",
    "Mtoon1UvAnimationMaskTexture.Image": "uv_anim_mask",
}

LEGACY_IMAGE_PATTERNS = [
    re.compile(r"^Shader_"),
    re.compile(r"^MatcapWarp"),
    re.compile(r"^N\d{2}_"),
]

SEMANTIC_SUFFIXES = (
    "_base",
    "_normal",
    "_shade",
    "_emissive",
    "_matcap",
    "_rim",
    "_outline_width",
    "_shading_shift",
    "_uv_anim_mask",
)

TEXTURES_DIR_MARKER = os.sep + "textures" + os.sep


def material_slug(name: str) -> str:
    name = name.replace(" (Instance)", "")
    outline_match = re.match(r"MToon Outline \((.+)\)", name)
    if outline_match:
        inner = outline_match.group(1).replace(" (Instance)", "")
        return "outline_" + inner.lower()
    return name.lower()


def is_outline_material(name: str) -> bool:
    return name.startswith("MToon Outline")


def image_stem(img_name: str) -> str:
    if img_name in GLOBAL_STEMS:
        return img_name
    return re.sub(r"\.\d{3}$", "", img_name)


def global_target_name(img_name: str) -> Optional[str]:
    return GLOBAL_STEMS.get(image_stem(img_name))


def is_mtoon(mat: bpy.types.Material) -> bool:
    if not mat or not mat.use_nodes or not mat.node_tree:
        return False
    return any(n.name == "Mtoon1Material.Mtoon1Output" for n in mat.node_tree.nodes)


def iter_mtoon_materials() -> List[bpy.types.Material]:
    return [mat for mat in bpy.data.materials if is_mtoon(mat)]


def get_tex_image(mat: bpy.types.Material, node_name: str) -> Optional[bpy.types.Image]:
    node = mat.node_tree.nodes.get(node_name)
    if not node or node.type != "TEX_IMAGE":
        return None
    return node.image


def material_preference_score(mat_name: str) -> int:
    score = 0
    if "(Instance)" in mat_name:
        score += 100
    if not is_outline_material(mat_name):
        score += 50
    return score


def image_path_key(img: bpy.types.Image) -> str:
    if img.packed_file:
        return f"packed:{img.name}"
    abspath = bpy.path.abspath(img.filepath)
    if abspath:
        return os.path.normpath(abspath)
    return f"nopath:{img.name}"


def is_under_textures_dir(abspath: str) -> bool:
    if not abspath:
        return False
    normalized = os.path.normpath(abspath)
    return TEXTURES_DIR_MARKER in normalized.replace("/", os.sep)


def textures_blend_path(new_stem: str) -> str:
    return f"//textures/{new_stem}.png"


def collect_assignments() -> List[dict]:
    assignments: List[dict] = []

    for mat in iter_mtoon_materials():
        mat_name = mat.name
        slug = material_slug(mat_name)

        base_img = get_tex_image(mat, "Mtoon1BaseColorTexture.Image")
        shade_img = get_tex_image(mat, "Mtoon1ShadeMultiplyTexture.Image")
        shared_lit_shade = (
            base_img is not None and shade_img is not None and base_img == shade_img
        )

        for node_name, suffix in SLOT_SUFFIX.items():
            if shared_lit_shade and node_name == "Mtoon1ShadeMultiplyTexture.Image":
                continue

            img = get_tex_image(mat, node_name)
            if img is None:
                continue

            role_suffix = suffix
            if shared_lit_shade and node_name == "Mtoon1BaseColorTexture.Image":
                role_suffix = "base"
            elif node_name == "Mtoon1ShadeMultiplyTexture.Image":
                role_suffix = "shade"

            assignments.append(
                {
                    "image": img,
                    "image_name": img.name,
                    "material": mat_name,
                    "material_slug": slug,
                    "node_name": node_name,
                    "suffix": role_suffix,
                    "is_outline": is_outline_material(mat_name),
                    "preference": material_preference_score(mat_name),
                    "path_key": image_path_key(img),
                    "packed": img.packed_file is not None,
                    "abspath": bpy.path.abspath(img.filepath) if img.filepath else "",
                }
            )

    return assignments


def propose_stem_for_group(group: List[dict]) -> str:
    global_name = None
    for row in group:
        target = global_target_name(row["image_name"])
        if target:
            global_name = target
            break
    if global_name:
        return global_name

    best = max(group, key=lambda row: (row["preference"], -row["is_outline"], row["material"]))
    return f"{best['material_slug']}_{best['suffix']}"


def resolve_unique_stem(desired: str, used: Set[str]) -> str:
    if desired not in used:
        used.add(desired)
        return desired

    index = 2
    while True:
        candidate = f"{desired}_{index:02d}"
        if candidate not in used:
            used.add(candidate)
            return candidate
        index += 1


def build_rename_map(assignments: List[dict]) -> Tuple[Dict[str, str], List[dict]]:
    by_path: Dict[str, List[dict]] = defaultdict(list)
    for row in assignments:
        by_path[row["path_key"]].append(row)

    used_stems: Set[str] = set()
    path_to_stem: Dict[str, str] = {}
    collisions: List[dict] = []

    for path_key, group in sorted(by_path.items(), key=lambda item: item[0]):
        desired = propose_stem_for_group(group)
        stem = resolve_unique_stem(desired, used_stems)
        if stem != desired:
            collisions.append(
                {
                    "path_key": path_key,
                    "desired": desired,
                    "resolved": stem,
                    "images": sorted({row["image_name"] for row in group}),
                }
            )
        path_to_stem[path_key] = stem

    image_to_stem: Dict[str, str] = {}
    rows: List[dict] = []
    seen_images: Set[str] = set()

    for path_key, group in by_path.items():
        stem = path_to_stem[path_key]
        materials = sorted({row["material"] for row in group})
        sample = group[0]
        new_path = textures_blend_path(stem)

        for row in group:
            image_to_stem[row["image_name"]] = stem
            if row["image_name"] in seen_images:
                continue
            seen_images.add(row["image_name"])
            rows.append(
                {
                    "old_image": row["image_name"],
                    "old_path": row["abspath"] or "(packed or empty)",
                    "new_image": stem,
                    "new_path": bpy.path.abspath(new_path) if row["abspath"] else new_path,
                    "used_by_materials": materials,
                    "packed": row["packed"],
                    "external_under_textures": is_under_textures_dir(row["abspath"]),
                }
            )

    return image_to_stem, rows


def audit_mtoon_textures() -> dict:
    materials = [mat.name for mat in iter_mtoon_materials()]
    assignments = collect_assignments()
    rename_map, rows = build_rename_map(assignments)

    table_lines = [
        "old_image | old_path | new_image | new_path | used_by_materials",
        "--- | --- | --- | --- | ---",
    ]
    for row in sorted(rows, key=lambda item: item["new_image"]):
        mats = ", ".join(row["used_by_materials"])
        table_lines.append(
            f"{row['old_image']} | {row['old_path']} | {row['new_image']} | {row['new_path']} | {mats}"
        )

    print("\n".join(table_lines))

    return {
        "phase": "B",
        "step": "audit",
        "dry_run": True,
        "mtoon_material_count": len(materials),
        "assignment_count": len(assignments),
        "rename_count": len(rows),
        "materials": materials,
        "rows": rows,
        "rename_map": rename_map,
        "table_markdown": "\n".join(table_lines),
    }


def canonical_image_for_names(names: List[str]) -> bpy.types.Image:
    images = [bpy.data.images[n] for n in names if n in bpy.data.images]
    if not images:
        raise ValueError("no images found for merge")

    def sort_key(img: bpy.types.Image) -> Tuple[int, int, str]:
        stem = image_stem(img.name)
        is_dup = 1 if re.search(r"\.\d{3}$", img.name) else 0
        return (is_dup, -img.users, img.name)

    return sorted(images, key=sort_key)[0]


def reassign_image_nodes(old_img: bpy.types.Image, new_img: bpy.types.Image) -> int:
    if old_img == new_img:
        return 0

    count = 0
    for mat in bpy.data.materials:
        if not mat.use_nodes or not mat.node_tree:
            continue
        for node in mat.node_tree.nodes:
            if node.type == "TEX_IMAGE" and node.image == old_img:
                node.image = new_img
                count += 1
    return count


def apply_mtoon_texture_renames(rename_map: Dict[str, str]) -> dict:
    print("Reminder: save the .blend after apply.")

    path_to_old_images: Dict[str, List[str]] = defaultdict(list)
    for img_name, stem in rename_map.items():
        img = bpy.data.images.get(img_name)
        if not img:
            continue
        path_to_old_images[image_path_key(img)].append(img_name)

    disk_renames: List[dict] = []
    datablock_renames: List[dict] = []
    packed_only: List[str] = []
    outside_textures: List[str] = []
    merged: List[dict] = []

    stem_to_canonical: Dict[str, bpy.types.Image] = {}

    for path_key, img_names in path_to_old_images.items():
        canonical = canonical_image_for_names(img_names)
        stem = rename_map.get(canonical.name)
        if not stem:
            continue

        target_blend_path = textures_blend_path(stem)

        for img_name in img_names:
            img = bpy.data.images.get(img_name)
            if not img:
                continue

            old_name = img.name
            old_abspath = bpy.path.abspath(img.filepath) if img.filepath else ""

            if img.packed_file:
                packed_only.append(old_name)

            if old_abspath and not is_under_textures_dir(old_abspath):
                outside_textures.append(old_name)

            if (
                old_abspath
                and os.path.isfile(old_abspath)
                and is_under_textures_dir(old_abspath)
                and not img.packed_file
            ):
                new_abspath = bpy.path.abspath(target_blend_path)
                if old_abspath != new_abspath:
                    os.makedirs(os.path.dirname(new_abspath), exist_ok=True)
                    if os.path.isfile(new_abspath) and os.path.normpath(old_abspath) != os.path.normpath(
                        new_abspath
                    ):
                        pass
                    if not os.path.isfile(new_abspath):
                        os.rename(old_abspath, new_abspath)
                        disk_renames.append(
                            {"old": old_abspath, "new": new_abspath, "image": old_name}
                        )

            if img != canonical:
                nodes_updated = reassign_image_nodes(img, canonical)
                merged.append(
                    {
                        "from": img.name,
                        "to": canonical.name,
                        "nodes_updated": nodes_updated,
                    }
                )
                if img.users == 0:
                    bpy.data.images.remove(img)

        canonical = bpy.data.images.get(canonical.name)
        if not canonical:
            continue

        old_canonical_name = canonical.name
        if canonical.name != stem:
            canonical.name = stem
            datablock_renames.append({"old": old_canonical_name, "new": stem})

        canonical.filepath = target_blend_path
        stem_to_canonical[stem] = canonical

        if not canonical.packed_file and canonical.filepath:
            abspath = bpy.path.abspath(canonical.filepath)
            if os.path.isfile(abspath):
                try:
                    canonical.reload()
                except RuntimeError:
                    pass

    return {
        "phase": "B",
        "step": "apply",
        "dry_run": False,
        "disk_rename_count": len(disk_renames),
        "disk_renames": disk_renames,
        "datablock_rename_count": len(datablock_renames),
        "datablock_renames": datablock_renames,
        "packed_only_count": len(packed_only),
        "packed_only": sorted(set(packed_only)),
        "outside_textures_count": len(outside_textures),
        "outside_textures": sorted(set(outside_textures)),
        "merged_duplicate_count": len(merged),
        "merged_duplicates": merged,
        "copy_external": COPY_EXTERNAL,
    }


def is_legacy_image_name(name: str) -> bool:
    if name in GLOBAL_STEMS.values():
        return False
    stem = image_stem(name)
    if stem in GLOBAL_STEMS:
        return False
    if any(pattern.search(name) for pattern in LEGACY_IMAGE_PATTERNS):
        return True
    if re.search(r"_\d{2}$", name):
        if any(name.endswith(suffix) for suffix in SEMANTIC_SUFFIXES):
            return False
        if re.search(
            r"_(base|normal|shade|emissive|matcap|rim|outline_width|shading_shift|uv_anim_mask)_\d{2}$",
            name,
        ):
            return False
        return True
    return False


def verify_mtoon_textures() -> dict:
    assignments = collect_assignments()
    broken: List[dict] = []
    legacy: List[str] = []
    empty_optional: List[dict] = []

    optional_slots = {
        "Mtoon1RimMultiplyTexture.Image",
        "Mtoon1OutlineWidthMultiplyTexture.Image",
        "Mtoon1MatcapTexture.Image",
        "Mtoon1EmissiveTexture.Image",
        "Mtoon1ShadingShiftTexture.Image",
        "Mtoon1UvAnimationMaskTexture.Image",
    }

    for mat in iter_mtoon_materials():
        for node_name in SLOT_SUFFIX:
            node = mat.node_tree.nodes.get(node_name)
            if not node or node.type != "TEX_IMAGE":
                continue
            img = node.image
            if img is None:
                if node_name in optional_slots:
                    empty_optional.append({"material": mat.name, "slot": node_name})
                continue

            if is_legacy_image_name(img.name):
                legacy.append(f"{mat.name} :: {img.name}")

            if img.filepath and not img.packed_file:
                abspath = bpy.path.abspath(img.filepath)
                if abspath and not os.path.isfile(abspath):
                    broken.append(
                        {
                            "material": mat.name,
                            "image": img.name,
                            "path": abspath,
                        }
                    )

    body_spot_check = None
    for mat in iter_mtoon_materials():
        slug = material_slug(mat.name)
        if "body" in slug and not is_outline_material(mat.name):
            body_spot_check = {
                "material": mat.name,
                "slug": slug,
                "base": getattr(get_tex_image(mat, "Mtoon1BaseColorTexture.Image"), "name", None),
                "normal": getattr(get_tex_image(mat, "Mtoon1NormalTexture.Image"), "name", None),
                "shade": getattr(get_tex_image(mat, "Mtoon1ShadeMultiplyTexture.Image"), "name", None),
            }
            break

    packed_count = sum(1 for img in bpy.data.images if img.packed_file)
    external_count = sum(
        1
        for img in bpy.data.images
        if img.filepath and not img.packed_file and is_under_textures_dir(bpy.path.abspath(img.filepath))
    )

    return {
        "phase": "B",
        "step": "verify",
        "broken_path_count": len(broken),
        "broken_paths": broken,
        "legacy_name_count": len(legacy),
        "legacy_names": sorted(set(legacy)),
        "empty_optional_slot_count": len(empty_optional),
        "empty_optional_slots": empty_optional,
        "body_spot_check": body_spot_check,
        "packed_image_count": packed_count,
        "external_under_textures_count": external_count,
        "ok": len(broken) == 0,
    }


def run_phase_b(step: str = "audit", rename_map: Optional[Dict[str, str]] = None) -> dict:
    if step == "audit":
        return audit_mtoon_textures()
    if step == "apply":
        if rename_map is None:
            rename_map = audit_mtoon_textures()["rename_map"]
        return apply_mtoon_texture_renames(rename_map)
    if step == "verify":
        return verify_mtoon_textures()
    return {"error": f"unknown step: {step}"}


if __name__ == "__main__":
    result = audit_mtoon_textures()
