---
name: csharpier-format
description: >-
  Formats C# source with CSharpier across a repo or selected paths. Use when the user asks to run CSharpier,
  format all .cs files, apply CSharpier, or fix C# formatting to match project style.
---

# CSharpier — format C# (all files)

## When to use

- User wants **all** `*.cs` files formatted, or a **directory / project** run through CSharpier.
- **Before handoff** or **before commit** when `.cs` is in scope (`format-before-handoff-and-commit.mdc`).

## Preconditions

- [CSharpier](https://github.com/belav/csharpier) is installed: **global** tool and/or **local** `dotnet tool` (manifest next to the repo).
- Run from the **repository root** that contains the code (for Unity: often the folder above `Assets`, e.g. `GridDungeonECS`), unless the user names a different root.

## Commands (pick what works in the environment)

1. **Local tool** — if `dotnet-tools.json` exists at repo root:

   ```bash
   dotnet tool restore
   dotnet csharpier format .
   ```

2. **Global tool on PATH** — common when the repo has **no** manifest (many Unity projects):

   ```bash
   csharpier format .
   ```

3. **Single file or subtree**:

   ```bash
   dotnet csharpier format path/to/File.cs
   csharpier format path/to/File.cs
   dotnet csharpier format Assets/SomeFolder
   csharpier format Assets/SomeFolder
   ```

`format .` recursively formats `.cs` files per [CSharpier configuration](https://csharpier.com/docs/Configuration) (e.g. `.csharpierrc`, `csharpier.yaml`, `.editorconfig`).

## Agent workflow

1. **Confirm root**: Prefer the workspace’s git/Plastic root (parent of `Assets` for Unity projects) so formatting matches CI/editor.
2. **Run** via Shell from that root:
   - If **`dotnet-tools.json`** is present: `dotnet tool restore` then `dotnet csharpier format .` (or scoped paths).
   - Else try **`dotnet csharpier format .`** once; if it fails (“Could not execute”, tool not found), run **`csharpier format .`** (global).
3. **If both fail**: report that `dotnet tool install csharpier --global` or adding a local tool (`dotnet new tool-manifest` + `dotnet tool install csharpier`) is required; do not silently substitute another formatter.
4. **Scope**: “Format all `.cs`” → `format .` from chosen root. Do not limit to `Assets` only unless the user asked to scope there.

## Notes

- CSharpier does not format `.uxml`, `.shader`, etc. — C# only.
- **Windows PowerShell** does not treat `&&` as a command separator on older versions. Use **`;`** or run **`Set-Location "d:\path\to\repo"; csharpier format .`** (or separate Shell invocations) instead of `cd path && csharpier …`.
