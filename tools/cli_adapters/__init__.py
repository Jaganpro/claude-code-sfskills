"""
CLI Adapters for sf-skills Multi-CLI Installer.

This package provides adapters for transforming sf-skills to different
agentic coding CLI formats following the Agent Skills open standard.

Supported CLIs:
- OpenCode: .opencode/skill/{name}/ or .claude/skills/{name}/
- Codex CLI: .codex/skills/{name}/
- Gemini CLI: ~/.gemini/skills/{name}/
"""

from .base import CLIAdapter, SkillOutput
from .opencode import OpenCodeAdapter
from .codex import CodexAdapter
from .gemini import GeminiAdapter

# Registry of available adapters
ADAPTERS = {
    'opencode': OpenCodeAdapter,
    'codex': CodexAdapter,
    'gemini': GeminiAdapter,
}

__all__ = [
    'CLIAdapter',
    'SkillOutput',
    'OpenCodeAdapter',
    'CodexAdapter',
    'GeminiAdapter',
    'ADAPTERS',
]
