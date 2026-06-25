# mira-cursor-skills

Personal and project [Cursor Agent Skills](https://cursor.com/docs/skills) for Unity, Grid Dungeon, Blender/VRoid, and agent workflows.

## Skills (14)

### General / tooling

| Skill | Invoke | Purpose |
|-------|--------|---------|
| [csharpier-format](csharpier-format/) | `/csharpier-format` | Run [CSharpier](https://github.com/belav/csharpier) on `.cs` files |
| [code-review-unity](code-review-unity/) | `/code-review-unity` | Unity-focused code / PR review |
| [plastic-scm-diff-review](plastic-scm-diff-review/) | `/plastic-scm-diff-review` | Review pending Plastic SCM (UVCS) changes via `cm` |
| [pull-next-backlog-ticket](pull-next-backlog-ticket/) | — | Pull next item from GitHub Project backlog |

### Blender / VRoid

| Skill | Invoke | Purpose |
|-------|--------|---------|
| [blender-bone-remap](blender-bone-remap/) | — | Remap VRoid/VRM armature bones |
| [vroid-shapekey-remap](vroid-shapekey-remap/) | — | Rename VRoid `Fcl_*` shape keys |
| [vroid-vrm-blender-cleanup](vroid-vrm-blender-cleanup/) | — | VRoid/VRM Blender cleanup workflow |

### Grid Dungeon (Unity / UITK)

| Skill | Invoke | Purpose |
|-------|--------|---------|
| [prettier-uitk-format](prettier-uitk-format/) | — | Format `.uxml` / `.uss` with Prettier |
| [audit-centralized-ui-services](audit-centralized-ui-services/) | — | Audit UI against centralized-services spec |
| [audit-uitk-uss-class-toggles](audit-uitk-uss-class-toggles/) | — | Audit inline `style` vs USS class toggles |
| [validate-unity-meta](validate-unity-meta/) | — | Validate Unity `.meta` GUIDs |
| [visualize-uitk-uxml](visualize-uitk-uxml/) | — | ASCII UXML hierarchy diagrams |
| [stratum-floor-layout-check](stratum-floor-layout-check/) | — | S1 floor asset validation |
| [test-plan-grid-dungeon](test-plan-grid-dungeon/) | — | GitHub/PR test plan templates |

## Install

See [Cursor skills documentation](https://cursor.com/docs/skills) for global, per-project, and GitHub remote install options.

**Remote rule (GitHub):** `https://github.com/miramocha/mira-cursor-skills`

Restart Cursor or open a new Agent chat after install so skills are discovered.

## Updating

Pull this repo. If you linked skill folders, updates apply automatically; if you copied them, refresh from the latest checkout.

Maintainers can re-sync from upstream skill sources with `sync-skills.ps1` at the repo root.
