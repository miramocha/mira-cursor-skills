# mira-cursor-skills

Personal [Cursor Agent Skills](https://cursor.com/docs/skills) for Unity, C#, and Plastic SCM workflows.

## Skills

| Skill | Invoke | Purpose |
|-------|--------|---------|
| [csharpier-format](csharpier-format/) | `/csharpier-format` | Run [CSharpier](https://github.com/belav/csharpier) on `.cs` files |
| [code-review-unity](code-review-unity/) | `/code-review-unity` | Unity-focused code / PR review |
| [plastic-scm-diff-review](plastic-scm-diff-review/) | `/plastic-scm-diff-review` | Review pending Plastic SCM (UVCS) changes via `cm` |

## Install (global — all projects)

Clone this repo, then link each skill into your Cursor skills directory:

```powershell
git clone https://github.com/miramocha/mira-cursor-skills.git
$skills = "$env:USERPROFILE\.cursor\skills"
New-Item -ItemType Directory -Force -Path $skills | Out-Null
$repo = "<path-to-clone>"  # e.g. D:\MiraGameDev\mira-cursor-skills

@("csharpier-format", "code-review-unity", "plastic-scm-diff-review") | ForEach-Object {
  cmd /c mklink /J "$skills\$_" "$repo\$_"
}
```

Restart Cursor or open a new Agent chat so skills are discovered.

## Install (per project)

Copy (or submodule) skill folders into your repo:

```text
your-project/
└── .cursor/
    └── skills/
        ├── csharpier-format/
        ├── code-review-unity/
        └── plastic-scm-diff-review/
```

## Install from GitHub in Cursor

1. **Cursor Settings** → **Rules**
2. **Add Rule** → **Remote Rule (GitHub)**
3. Enter: `https://github.com/miramocha/mira-cursor-skills`

See [Installing skills from GitHub](https://cursor.com/docs/skills#installing-skills-from-github).

## Updating

Pull the repo; junctions pick up changes automatically. If you copied files into `.cursor/skills/`, copy again or use junctions.
