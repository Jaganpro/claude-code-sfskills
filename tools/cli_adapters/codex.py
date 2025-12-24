"""
OpenAI Codex CLI adapter for sf-skills.

Codex CLI follows the Agent Skills standard with some naming conventions:
- Skills location: .codex/skills/{name}/
- templates/ → assets/ (Codex convention)
- docs/ → references/ (Codex convention)

Codex CLI has built-in skill creator and installer support.
"""

from pathlib import Path
from typing import Optional

from .base import CLIAdapter, SkillOutput


class CodexAdapter(CLIAdapter):
    """
    Adapter for OpenAI Codex CLI.

    Codex follows Agent Skills standard but uses different directory names:
    - assets/ instead of templates/
    - references/ instead of docs/
    """

    @property
    def cli_name(self) -> str:
        return "codex"

    @property
    def default_install_path(self) -> Path:
        """
        Default to project-level .codex/skills/ directory.

        Codex CLI checks:
        1. .codex/skills/{name}/ (repository scope)
        2. ~/.codex/skills/{name}/ (user scope)
        3. Built-in skills (lowest precedence)
        """
        cwd = Path.cwd()
        return cwd / ".codex" / "skills"

    @property
    def templates_dir_name(self) -> str:
        """Codex uses 'assets' instead of 'templates'."""
        return "assets"

    @property
    def docs_dir_name(self) -> str:
        """Codex uses 'references' instead of 'docs'."""
        return "references"

    def transform_skill_md(self, content: str, skill_name: str) -> str:
        """
        Transform SKILL.md for Codex CLI compatibility.

        Changes:
        - Remove Claude Code-specific syntax
        - Update directory references (templates → assets, docs → references)
        - Add Codex-specific usage section
        """
        # Apply common transformations
        content = self._common_skill_md_transforms(content)

        # Update directory references
        content = content.replace("templates/", "assets/")
        content = content.replace("docs/", "references/")
        content = content.replace("`templates`", "`assets`")
        content = content.replace("`docs`", "`references`")

        # Add Codex-specific section
        codex_section = f"""

---

## Codex CLI Usage

This skill is compatible with OpenAI Codex CLI. To use:

```bash
# Enable skills in Codex
codex --enable skills

# The skill is automatically loaded from .codex/skills/{skill_name}/

# To run validation scripts manually:
cd .codex/skills/{skill_name}/scripts
python validate_*.py path/to/your/file
```

### Directory Structure

Codex CLI uses slightly different directory names:
- `assets/` - Code templates (called `templates/` in Claude Code)
- `references/` - Documentation (called `docs/` in Claude Code)
- `scripts/` - Validation scripts

See `scripts/README.md` for validation script usage.
"""

        # Only add if not already present
        if "## Codex CLI Usage" not in content:
            content += codex_section

        return content

    def transform_skill(self, source_dir: Path) -> SkillOutput:
        """
        Transform skill for Codex CLI.

        Same as base implementation but bundling shared modules.
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
