"""
Google Gemini CLI adapter for sf-skills.

Gemini CLI supports Agent Skills via the skillz MCP server extension:
- Skills location: ~/.gemini/skills/{name}/
- Uses standard Agent Skills format (SKILL.md + scripts/)
- Can share skills with Claude Code (no copying needed)
"""

from pathlib import Path
from typing import Optional

from .base import CLIAdapter, SkillOutput


class GeminiAdapter(CLIAdapter):
    """
    Adapter for Google Gemini CLI.

    Gemini CLI follows the Agent Skills standard closely.
    Skills are installed to ~/.gemini/skills/ by default.
    """

    @property
    def cli_name(self) -> str:
        return "gemini"

    @property
    def default_install_path(self) -> Path:
        """
        Default to user-level ~/.gemini/skills/ directory.

        Gemini CLI looks for skills in:
        1. ~/.gemini/skills/{name}/ (user scope)
        2. Can also share with Claude Code's .claude/skills/
        """
        return Path.home() / ".gemini" / "skills"

    def transform_skill_md(self, content: str, skill_name: str) -> str:
        """
        Transform SKILL.md for Gemini CLI compatibility.

        Gemini CLI is highly compatible with Agent Skills standard,
        so minimal transformation is needed.
        """
        # Apply common transformations
        content = self._common_skill_md_transforms(content)

        # Add Gemini-specific section
        gemini_section = f"""

---

## Gemini CLI Usage

This skill is compatible with Google Gemini CLI. To use:

```bash
# Skills are installed to ~/.gemini/skills/{skill_name}/
# Gemini CLI automatically discovers and loads them.

# Restart Gemini CLI to load new skills
gemini

# To run validation scripts manually:
cd ~/.gemini/skills/{skill_name}/scripts
python validate_*.py path/to/your/file
```

### Features

Gemini CLI with this skill provides:
- Automatic skill discovery from ~/.gemini/skills/
- 1M+ token context window (Gemini 2.5 Pro)
- Built-in Google Search grounding
- MCP extensibility

### Shared Skills

You can share skills between Gemini CLI and Claude Code by symlinking:

```bash
ln -s ~/.gemini/skills/{skill_name} ~/.claude/skills/{skill_name}
```

See `scripts/README.md` for validation script usage.
"""

        # Only add if not already present
        if "## Gemini CLI Usage" not in content:
            content += gemini_section

        return content

    def transform_skill(self, source_dir: Path) -> SkillOutput:
        """
        Transform skill for Gemini CLI.

        Bundles shared modules for self-contained installation since
        Gemini skills are typically installed to user home directory.
        """
        # Get base transformation
        output = super().transform_skill(source_dir)

        # Bundle shared modules if scripts reference them
        if self._needs_shared_modules(output.scripts):
            shared_modules = self._bundle_shared_modules()
            for path, content in shared_modules.items():
                output.scripts[f"shared/{path}"] = content

        return output

    def _needs_shared_modules(self, scripts: dict) -> bool:
        """Check if any scripts import from shared/ modules."""
        for content in scripts.values():
            if isinstance(content, str):
                if "from shared" in content or "import shared" in content:
                    return True
                if "lsp_client" in content or "code_analyzer" in content:
                    return True
        return False

    def _bundle_shared_modules(self) -> dict:
        """Bundle shared modules for self-contained installation."""
        modules = {}

        # Bundle lsp-engine
        lsp_dir = self.shared_dir / "lsp-engine"
        if lsp_dir.exists():
            for file_path in lsp_dir.rglob("*.py"):
                rel_path = file_path.relative_to(self.shared_dir)
                content = file_path.read_text(encoding='utf-8')
                modules[str(rel_path)] = content

        # Bundle code_analyzer
        analyzer_dir = self.shared_dir / "code_analyzer"
        if analyzer_dir.exists():
            for file_path in analyzer_dir.rglob("*.py"):
                rel_path = file_path.relative_to(self.shared_dir)
                content = file_path.read_text(encoding='utf-8')
                modules[str(rel_path)] = content

            for file_path in analyzer_dir.rglob("*.yml"):
                rel_path = file_path.relative_to(self.shared_dir)
                modules[str(rel_path)] = file_path.read_text(encoding='utf-8')

            for file_path in analyzer_dir.rglob("*.xml"):
                rel_path = file_path.relative_to(self.shared_dir)
                modules[str(rel_path)] = file_path.read_text(encoding='utf-8')

        return modules
