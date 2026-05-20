---
name: code-review-unity
description: >-
  Reviews Unity C# and related assets for correctness, Unity pitfalls, and
  project conventions. Use when the user asks for a code review, PR review,
  or feedback on Unity changes in this repo; also when auditing asmdef
  boundaries, UI Toolkit bindings, or migration safety.
---

# Unity code review (Cursor)

## When this skill applies

Use for reviews of Unity C#, `asmdef` layout, UI Toolkit / UXML, ScriptableObjects, scenes, and prefab-facing APIs. Cross-check changes against applicable Cursor rules under `.cursor/rules/` (see **Workspace rules as review gates** below).

## How to run the review in Cursor

1. Read the changed files (and callers/callees if the diff is narrow but behavior is wide).
2. Use **semantic search / grep** for duplicates, dead code, or unsafe patterns touched by the change.
3. Prefer **actionable** feedback tied to concrete lines or symbols; avoid generic style lectures already covered by the editor or formatter.
4. If behavior is unclear, say what assumption you are making instead of inventing certainty.

Do **not** assume a single AI product beyond Cursor Agent; instructions here are tooling-agnostic except where Cursor paths are named.

## Workspace rules as review gates

When `.cursor/rules/` defines architecture constraints (assemblies, UI Toolkit bindings, namespaces, etc.), read them and treat them as **mandatory gates** for changed paths they scope. **Do not duplicate rule text in this skill** — cite the rule file (path + section) when flagging violations.

If no relevant rules apply to the change, skip this gate unless the user supplies standards.

For `Assets/GridDungeon/**` C# or UXML in this workspace, enforce `.cursor/rules/griddungeon-assembly-structure.mdc`, including its **Code review checklist** section.

## Unity / C# checklist

Work through what applies to the diff size; skip irrelevant sections rather than forcing a template.

### Correctness and lifecycle

- **Unity null**: use Unity’s lifetime-aware checks for `UnityEngine.Object` where fake null matters; do not treat `== null` on Unity objects like pure managed references without reason.
- **Callbacks**: `OnDestroy` / `OnDisable` unregister listeners; coroutines and async completions cannot assume the object still exists.
- **Static state**: globals and caches respect domain reload and play mode exit; watch for leaks across entering/exiting play mode.
- **ScriptableObject**: no heavy per-frame mutation of shared assets unless intentional; mind editor vs runtime persistence and `OnEnable`/`Reset` expectations.

### Performance (only if hot path or allocation-heavy)

- Avoid per-frame allocations (LINQ in `Update`, boxing, unintended string churn).
- `GetComponent` in loops vs cached references; burst/Jobs/ECS only if the project uses them and the code is in that layer.

### Serialization and API surface

- Mark serialized fields consistently (`SerializeField`, `[SerializeReference]`, Odin, etc.) and keep defaults safe if assets are created in isolation.
- Public APIs and serialized shapes: additive changes where possible; call out migration risk for assets and scenes.

### Editor / conditional compilation

- Editor-only code behind `#if UNITY_EDITOR` or in an Editor asmdef; no editor types in runtime assemblies without guards.

### Tests and verification

- Note missing coverage for risky branches; suggest minimal play-mode or edit-mode tests when they would catch real failures.

## Feedback format

Group by severity so authors can triage:

- **Blocker**: correctness bug, regression, or violates mandatory workspace rules (e.g. assembly boundaries in `.cursor/rules/`).
- **Should fix**: maintainability, likely bug under edge cases, performance foot-gun in a hot path.
- **Nit / optional**: naming, small clarity wins, future refactors.

For each item: **what** is wrong, **where** (file/symbol or line range when known), and **why** it matters in Unity or under workspace rules.

## Out of scope unless asked

Rewriting large unrelated areas, reformatting unrelated files, or debating taste without tie-in to bugs, perf, or workspace rules.
