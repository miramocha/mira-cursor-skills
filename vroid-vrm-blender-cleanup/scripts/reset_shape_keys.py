"""
Reset all shape key values to 0 on a mesh object by object or mesh data name.
Run via MCP execute_blender_code or Blender Scripting workspace.

    report = reset_shape_keys("Face", dry_run=True)
"""

from __future__ import annotations

from typing import Optional

import bpy

DRY_RUN = True
DEFAULT_MESH_NAME = "Face"


def find_mesh_object(name: str) -> Optional[bpy.types.Object]:
    obj = bpy.data.objects.get(name)
    if obj and obj.type == "MESH":
        return obj

    for candidate in bpy.data.objects:
        if candidate.type == "MESH" and candidate.data and candidate.data.name == name:
            return candidate

    return None


def reset_shape_keys(mesh_name: str = DEFAULT_MESH_NAME, dry_run: bool = DRY_RUN) -> dict:
    obj = find_mesh_object(mesh_name)
    if obj is None:
        return {
            "phase": "C",
            "error": f'No mesh object found with object or mesh data name "{mesh_name}"',
        }

    shape_keys = obj.data.shape_keys
    if shape_keys is None:
        return {
            "phase": "C",
            "error": f'Object "{obj.name}" has no shape keys',
        }

    key_names = [kb.name for kb in shape_keys.key_blocks]
    count = len(key_names)

    if not dry_run:
        for key_block in shape_keys.key_blocks:
            key_block.value = 0.0

    return {
        "phase": "C",
        "dry_run": dry_run,
        "object_name": obj.name,
        "mesh_data_name": obj.data.name,
        "shape_key_count": count,
        "shape_keys": key_names,
    }


def run_phase_c(mesh_name: str = DEFAULT_MESH_NAME, dry_run: bool = DRY_RUN) -> dict:
    return reset_shape_keys(mesh_name=mesh_name, dry_run=dry_run)


if __name__ == "__main__":
    result = run_phase_c(mesh_name=DEFAULT_MESH_NAME, dry_run=DRY_RUN)
