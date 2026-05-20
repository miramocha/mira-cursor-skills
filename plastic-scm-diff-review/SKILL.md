---
name: plastic-scm-diff-review
description: >-
  Reviews pending or committed changes using Plastic SCM (Unity Version
  Control): resolves the Plastic workspace root, enumerates pending paths with
  cm status, reconstructs textual baselines with cm cat at the loaded
  changeset, and performs the same severity-triage code review workflow as the
  Unity project skill. Use when the user asks for a Plastic SCM diff review,
  UVCS review, cm-based review, or a review scoped to Plastic pending changes.
---

# Plastic SCM diff review (Cursor)

## When this skill applies

Use when reviewing **Plastic SCM / UVCS** work: pending workspace edits, pre-check-in review, or interpreting change lists gathered via **`cm`**. Combine with semantic search when the Plastic delta is narrow but behavior spans callers.

Do **not** assume tooling beyond Cursor Agent + Plastic **`cm`** CLI; optional Cursor Plastic extension UI is supplementary.

## How to run the review in Cursor

1. **Resolve the Plastic workspace root** (directory containing `.plastic/plastic.workspace`). Walk upward from the workspace folder open in Cursor until that file exists; run all **`cm`** commands from that root (or pass explicit paths per `cm help status`).
2. **Capture loaded revision**: run `cm status --header` and record the **`cs:N`** loaded in the workspace (for example `(cs:92 - head)` → baseline **`92`**).
3. **Enumerate Plastic-tracked deltas**: run `cm status --short --wrp` from the workspace root (add `--checkout`, `--changed`, etc., when filtering makes sense). Treat these paths as authoritative over incidental Git noise for Plastic-controlled trees.
4. **Build reviewable text for each pending text asset** (`.cs`, `.uxml`, `.uss`, `.shader`, `.asmdef`, `.json`, `.md`, …):
   - **Repository baseline at loaded changeset**: `cm cat "<wk-relative-path>#cs:N"` using the **`N`** from step 2.
   - **Working tree**: read the same path under the workspace root via Cursor file reads.
   - **Added paths**: baseline may not exist at **cs:N**; rely on status `--added` / machine-readable output and review the working tree as “new”.
   - **Deleted / moved / binary**: do not force a fake unified diff; summarize Plastic status and review metadata or Unity implications instead.
5. **Committed-only reviews** (optional): unified patches between changesets may use `cm patch <cs_spec> [<cs_spec>]` **when** Diff/Patch tools are configured per Plastic — if `cm patch` errors or hangs, fall back to **`cm cat`** per revision plus history (`cm history "<path>"`).
6. Prefer **actionable** feedback tied to symbols/lines; avoid generic lectures covered by analyzers/formatters.
7. If behavior is unclear, state assumptions instead of inventing certainty.

## Workspace rules as review gates

When this repository defines Cursor rules under `.cursor/rules/` (architecture, assemblies, UI Toolkit bindings, namespaces, etc.), read them and treat them as **mandatory gates** for any Plastic-changed paths they scope. **Do not duplicate rule text in this skill** — cite the rule file (path + section) when flagging violations.

If no relevant rules apply to the delta, skip this gate unless the user supplies standards.

## Unity / C# checklist

When the Plastic delta includes Unity/C#, apply the **Unity / C# checklist** section from the global **code-review-unity** skill (correctness/lifecycle, performance where relevant, serialization, editor guards, tests). Skip irrelevant bullets rather than forcing the full template.

## Feedback format

Group by severity so authors can triage:

- **Blocker**: correctness bug, regression, or violates mandatory workspace rules (e.g. assembly boundaries defined in `.cursor/rules/`).
- **Should fix**: maintainability, likely bug under edge cases, performance foot-gun in a hot path.
- **Nit / optional**: naming, small clarity wins, future refactors.

For each item: **what** is wrong, **where** (path/symbol or line range when known), and **why** it matters for Plastic/Unity/workspace rules.

## Out of scope unless asked

Rewriting large unrelated areas, reformatting unrelated files, or debating taste without tie-in to bugs, perf, or workspace rules.
