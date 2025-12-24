"""
OpenCode CLI adapter for sf-skills.

OpenCode supports the Agent Skills standard and looks for skills in:
- .opencode/skill/{name}/ (project-level)
- .claude/skills/{name}/ (also supported)
- ~/.opencode/skill/{name}/ (global)

OpenCode auto-discovers skills by traversing upward from the current
directory to the git worktree root.
"""

from pathlib import Path
from typing import Optional
import os

from .base import CLIAdapter, SkillOutput


class OpenCodeAdapter(CLIAdapter):
    """
    Adapter for OpenCode CLI.

    OpenCode natively supports the Agent Skills specification, so
    transformations are minimal. Main changes:
    - Remove Claude Code-specific syntax
    - Bundle shared modules with scripts
    - Generate scripts README for manual validation
    """

    @property
    def cli_name(self) -> str:
        return "opencode"

    @property
    def default_install_path(self) -> Path:
        """
        Default to project-level .opencode/skill/ directory.

        OpenCode checks multiple locations:
        1. .opencode/skill/ (project, preferred)
        2. .claude/skills/ (compatible with Claude Code)
        3. ~/.opencode/skill/ (global)
        """
        # Check if we're in a project with existing OpenCode config
        cwd = Path.cwd()
        opencode_path = cwd / ".opencode" / "skill"
        claude_path = cwd / ".claude" / "skills"

        # Prefer existing directory, otherwise default to .opencode/skill/
        if claude_path.exists():
            return claude_path
        return opencode_path

    def transform_skill_md(self, content: str, skill_name: str) -> str:
        """
        Transform SKILL.md for OpenCode compatibility.

        OpenCode is highly compatible with Claude Code, so changes are minimal:
        - Remove ${CLAUDE_PLUGIN_ROOT} variable (use relative paths)
        - Update Skill() syntax to OpenCode @skill format
        - Add OpenCode-specific footer with CLI commands
        """
        # Apply common transformations
        content = self._common_skill_md_transforms(content)

        # Add OpenCode-specific section at the end
        opencode_section = f"""

---

## OpenCode CLI Usage

This skill is compatible with OpenCode CLI. To use:

```bash
# The skill is automatically loaded when placed in .opencode/skill/{skill_name}/
# OpenCode will discover it and make it available in conversations.

# To manually invoke validation scripts:
cd .opencode/skill/{skill_name}/scripts
python validate_*.py path/to/your/file
```

### Validation Scripts

The `scripts/` directory contains Python validation scripts that can be run
manually after editing files. In Claude Code, these run automatically via
PostToolUse hooks.

See `scripts/README.md` for detailed usage instructions.
"""

        # Only add if not already present
        if "## OpenCode CLI Usage" not in content:
            content += opencode_section

        return content

    def transform_skill(self, source_dir: Path) -> SkillOutput:
        """
        Transform skill for OpenCode, bundling shared modules.

        Override to bundle shared/ modules into scripts/shared/
        for self-contained skill installation.
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
                # Also check for relative imports that might reference shared
                if "lsp_client" in content or "code_analyzer" in content:
                    return True
        return False

    def _bundle_shared_modules(self) -> dict:
        """
        Bundle shared modules into scripts/shared/ directory.

        Returns:
            Dict mapping relative path to content
        """
        modules = {}

        # Bundle lsp-engine
        lsp_dir = self.shared_dir / "lsp-engine"
        if lsp_dir.exists():
            for file_path in lsp_dir.rglob("*.py"):
                rel_path = file_path.relative_to(self.shared_dir)
                content = file_path.read_text(encoding='utf-8')
                # Rewrite imports to use local path
                content = self._rewrite_shared_imports(content)
                modules[str(rel_path)] = content

        # Bundle code_analyzer
        analyzer_dir = self.shared_dir / "code_analyzer"
        if analyzer_dir.exists():
            for file_path in analyzer_dir.rglob("*.py"):
                rel_path = file_path.relative_to(self.shared_dir)
                content = file_path.read_text(encoding='utf-8')
                content = self._rewrite_shared_imports(content)
                modules[str(rel_path)] = content

            # Also copy config files
            for file_path in analyzer_dir.rglob("*.yml"):
                rel_path = file_path.relative_to(self.shared_dir)
                modules[str(rel_path)] = file_path.read_text(encoding='utf-8')

            for file_path in analyzer_dir.rglob("*.xml"):
                rel_path = file_path.relative_to(self.shared_dir)
                modules[str(rel_path)] = file_path.read_text(encoding='utf-8')

        return modules

    def _rewrite_shared_imports(self, content: str) -> str:
        """
        Rewrite imports to use local shared/ path.

        Changes:
        - from shared.lsp_engine → from .shared.lsp_engine
        - import shared.code_analyzer → import .shared.code_analyzer
        """
        import re

        # Rewrite absolute imports to relative
        content = re.sub(
            r'from shared\.(\w+)',
            r'from .shared.\1',
            content
        )
        content = re.sub(
            r'import shared\.(\w+)',
            r'from . import shared.\1',
            content
        )

        return content
