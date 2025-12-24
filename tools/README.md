# sf-skills Multi-CLI Installer

Install sf-skills to different agentic coding CLIs following the [Agent Skills open standard](https://agentskills.io).

## Supported CLIs

| CLI | Install Path | Description |
|-----|--------------|-------------|
| **OpenCode** | `.opencode/skill/{name}/` | Open-source Claude Code alternative |
| **Codex CLI** | `.codex/skills/{name}/` | OpenAI's coding CLI |
| **Gemini CLI** | `~/.gemini/skills/{name}/` | Google's Gemini-powered CLI |

> **Note:** Claude Code support remains via the native `.claude-plugin/` structure in each skill directory. This installer is for *other* CLIs.

## Quick Start

```bash
# Clone the repository
git clone https://github.com/Jaganpro/sf-skills
cd sf-skills

# Install all skills for OpenCode
python tools/installer.py --cli opencode --all

# Install specific skills for Gemini
python tools/installer.py --cli gemini --skills sf-apex sf-flow

# Auto-detect installed CLIs and install all skills
python tools/installer.py --detect --all
```

## Usage

```
usage: installer.py [-h] [--cli {opencode,codex,gemini}] [--detect]
                    [--skills SKILLS [SKILLS ...]] [--all]
                    [--target TARGET] [--force] [--list] [--list-clis]

Install sf-skills to different agentic coding CLIs

optional arguments:
  -h, --help            show this help message and exit
  --cli {opencode,codex,gemini}
                        Target CLI to install for
  --detect              Auto-detect installed CLIs
  --skills SKILLS [SKILLS ...]
                        Specific skills to install
  --all                 Install all available skills
  --target TARGET       Custom target directory for installation
  --force               Overwrite existing installations
  --list                List available skills
  --list-clis           List supported CLIs
```

## Examples

### List Available Skills

```bash
python tools/installer.py --list
```

Output:
```
Available Skills
================
  sf-apex              Salesforce Apex development with validation...
  sf-data              Salesforce data operations and SOQL queries...
  sf-deploy            Salesforce deployment automation...
  sf-flow              Salesforce Flow development...
  ...
```

### Install All Skills for OpenCode

```bash
python tools/installer.py --cli opencode --all
```

This installs to `.opencode/skill/` in your current directory.

### Install to Custom Location

```bash
python tools/installer.py --cli codex --target /path/to/project/.codex/skills/ --all
```

### Auto-Detect CLIs

```bash
python tools/installer.py --detect --all
```

Detects installed CLIs (OpenCode, Codex, Gemini) and installs skills to each.

### Force Reinstall

```bash
python tools/installer.py --cli gemini --all --force
```

Overwrites existing skill installations.

## What Gets Installed

Each installed skill contains:

```
{skill-name}/
├── SKILL.md           # Skill definition (transformed for target CLI)
├── scripts/           # Validation scripts (standalone)
│   ├── README.md      # Manual run instructions
│   ├── validate_*.py  # Validation scripts
│   └── shared/        # Bundled shared modules
├── templates/         # Code templates (or assets/ for Codex)
├── docs/              # Documentation (or references/ for Codex)
└── examples/          # Example files
```

### Key Transformations

| Source | OpenCode | Codex | Gemini |
|--------|----------|-------|--------|
| `SKILL.md` | `SKILL.md` | `SKILL.md` | `SKILL.md` |
| `.claude-plugin/*` | (skipped) | (skipped) | (skipped) |
| `hooks/scripts/*.py` | `scripts/*.py` | `scripts/*.py` | `scripts/*.py` |
| `templates/` | `templates/` | `assets/` | `templates/` |
| `docs/` | `docs/` | `references/` | `docs/` |
| `shared/*` | `scripts/shared/` | `scripts/shared/` | `scripts/shared/` |

## Running Validation Scripts

Unlike Claude Code (which runs hooks automatically), other CLIs require manual validation:

```bash
# Navigate to installed skill
cd .opencode/skill/sf-apex/scripts

# Run Apex validation
python validate_apex.py /path/to/MyClass.cls

# Run Flow validation
cd .opencode/skill/sf-flow/scripts
python validate_flow.py /path/to/MyFlow.flow-meta.xml
```

## CLI-Specific Notes

### OpenCode

- Looks for skills in `.opencode/skill/` (project) or `~/.opencode/skill/` (global)
- Also supports `.claude/skills/` for Claude Code compatibility
- Skills are auto-discovered on startup

### Codex CLI

- Uses different directory names: `assets/` instead of `templates/`, `references/` instead of `docs/`
- Enable skills with `codex --enable skills`
- Looks in `.codex/skills/` (project) or `~/.codex/skills/` (global)

### Gemini CLI

- Installs to `~/.gemini/skills/` (user scope) by default
- Can symlink with Claude Code: `ln -s ~/.gemini/skills/sf-apex ~/.claude/skills/sf-apex`
- Benefits from Gemini's 1M+ token context window

## Troubleshooting

### "No skills found in repository"

Make sure you're running from the sf-skills repository root:

```bash
cd /path/to/sf-skills
python tools/installer.py --list
```

### "Skill already exists"

Use `--force` to overwrite:

```bash
python tools/installer.py --cli opencode --skills sf-apex --force
```

### Scripts fail with import errors

Ensure shared modules are bundled. Reinstall with `--force`:

```bash
python tools/installer.py --cli opencode --all --force
```

### CLI not detected

The auto-detect feature checks for:
- OpenCode: `opencode` command or `~/.opencode/` directory
- Codex: `codex` command
- Gemini: `gemini` command or `~/.gemini/` directory

If your CLI is installed but not detected, use `--cli` explicitly.

## Contributing

To add support for a new CLI:

1. Create `tools/cli_adapters/{cli_name}.py`
2. Inherit from `CLIAdapter` base class
3. Implement required methods:
   - `cli_name` property
   - `default_install_path` property
   - `transform_skill_md()` method
4. Register in `tools/cli_adapters/__init__.py`

See existing adapters for examples.

## License

Same as the main sf-skills repository.
