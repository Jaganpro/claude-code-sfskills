# Salesforce Flow & DevOps Skills for Claude Code

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code](https://img.shields.io/badge/Claude-Code-blue.svg)](https://claude.ai/code)
[![Salesforce](https://img.shields.io/badge/Salesforce-Flow%20%26%20DevOps-00A1E0.svg)](https://www.salesforce.com/)

A comprehensive collection of professional Claude Code skills for Salesforce development, specializing in Flow automation and DevOps workflows.

## 🎯 Overview

This repository contains three powerful, production-ready skills that transform Claude Code into a Salesforce development powerhouse:

| Skill | Version | Description |
|-------|---------|-------------|
| **sf-deployment** | 2.1.0 | Comprehensive Salesforce DevOps automation for deployments, testing, and CI/CD |
| **sf-flow-builder** | 1.3.0 | Expert Salesforce Flow creation with validation and best practices enforcement |
| **skill-builder** | 2.0.0 | Interactive wizard for creating, validating, and managing Claude Code skills |

### 🌟 Key Features

#### sf-deployment
- ✅ Automated metadata deployments with validation
- ✅ CI/CD pipeline integration
- ✅ Pre-deployment validation (`--dry-run`)
- ✅ Comprehensive error handling and rollback guidance
- ✅ Support for modern `sf` CLI (v2.x)

#### sf-flow-builder
- ✅ 5-phase guided flow creation workflow
- ✅ Strict validation with scoring system (0-100)
- ✅ Auto-bulkification and performance optimization
- ✅ API 62.0 (Winter '26) metadata standard
- ✅ Transform element usage for 30-50% performance gains
- ✅ Simulation mode for governor limit testing

#### skill-builder
- ✅ Interactive skill creation wizard
- ✅ Bulk skill validation with comprehensive reporting
- ✅ Dependency management with version constraints
- ✅ Terminal-based interactive editor
- ✅ Python validation scripts with virtual environment

## 📦 Installation

### Quick Install (One Command)

```bash
# Clone repository
git clone https://github.com/your-github-username/claude-code-salesforce-skills.git
cd claude-code-salesforce-skills

# Install all skills globally (recommended)
./install.sh

# Or install in current project only
./install.sh --local
```

### Manual Installation

```bash
# Create skills directory
mkdir -p ~/.claude/skills

# Copy each skill
cp -r skills/sf-deployment ~/.claude/skills/
cp -r skills/sf-flow-builder ~/.claude/skills/
cp -r skills/skill-builder ~/.claude/skills/

# Setup Python environment for skill-builder
cd ~/.claude/skills/skill-builder
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements.txt
```

### Restart Claude Code

After installation, **restart Claude Code** to load the new skills.

## 🚀 Quick Start

### Creating a Salesforce Flow

```
You: Create a screen flow for account creation with validation
Claude: [Uses sf-flow-builder skill]
  ✓ Gathers requirements
  ✓ Selects appropriate template
  ✓ Generates flow with best practices
  ✓ Validates (strict mode)
  ✓ Deploys to your org
  ✓ Provides testing checklist
```

### Deploying Metadata

```
You: Deploy my Apex classes to sandbox with tests
Claude: [Uses sf-deployment skill]
  ✓ Validates org connection
  ✓ Runs pre-deployment checks
  ✓ Executes deployment with RunLocalTests
  ✓ Reports code coverage
  ✓ Provides post-deployment verification
```

### Creating a New Skill

```
You: Create a new Claude Code skill for Python code analysis
Claude: [Uses skill-builder skill]
  ✓ Interactive wizard collects requirements
  ✓ Scaffolds skill structure
  ✓ Validates YAML frontmatter
  ✓ Creates documentation
  ✓ Ready to customize
```

## 📚 Documentation

Each skill includes comprehensive documentation:

- **Main Documentation**: [README-MAIN.md](README-MAIN.md) (this file)
- **sf-deployment**: [skills/sf-deployment/README.md](skills/sf-deployment/README.md)
- **sf-flow-builder**: [skills/sf-flow-builder/README.md](skills/sf-flow-builder/README.md)
- **skill-builder**: [skills/skill-builder/README.md](skills/skill-builder/README.md)

### Additional Resources

- [Installation Guide](docs/INSTALLATION.md)
- [Usage Examples](docs/EXAMPLES.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Contributing Guidelines](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

## 🔄 Upgrading

To upgrade to the latest version:

```bash
cd claude-code-salesforce-skills
git pull origin main
./upgrade.sh
```

The upgrade script will:
- Create backups of existing skills
- Install new versions
- Preserve your Python virtual environment (for skill-builder)
- Show version changes

## 🗑️ Uninstallation

To remove all skills:

```bash
cd claude-code-salesforce-skills
./uninstall.sh
```

## 🛠️ Prerequisites

### Required
- **Claude Code**: Latest version
- **Salesforce CLI**: v2.x (`sf` command) for Salesforce skills

### Optional
- **Python 3.8+**: For skill-builder validation scripts
- **Git**: For version control and updates

### Verification

```bash
# Check Claude Code
claude --version

# Check Salesforce CLI
sf --version

# Check Python (optional)
python3 --version
```

## 🏗️ Architecture

### Skill Dependencies

```
sf-flow-builder (1.3.0)
  └─ depends on: sf-deployment (>=2.0.0) ✓

sf-deployment (2.1.0)
  └─ no dependencies (foundational skill)

skill-builder (2.0.0)
  └─ no dependencies (meta-skill)
```

### Tool Permissions

Each skill only requests the tools it needs:

- **sf-deployment**: Bash, Read, Write, Edit, Grep, Glob, AskUserQuestion, TodoWrite
- **sf-flow-builder**: Bash, Read, Write, Edit, Glob, Grep, AskUserQuestion, TodoWrite, Skill, WebFetch
- **skill-builder**: Bash, Read, Write, Glob, Grep, AskUserQuestion

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit with clear messages (`git commit -m 'Add amazing feature'`)
6. Push to your branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/your-github-username/claude-code-salesforce-skills.git
cd claude-code-salesforce-skills

# Install for testing
./install.sh --local

# Make changes to skills in skills/ directory

# Validate changes
cd skills/skill-builder/scripts
python3 bulk_validate.py
```

## 🐛 Issues & Support

- **Bug Reports**: [GitHub Issues](https://github.com/your-github-username/claude-code-salesforce-skills/issues)
- **Feature Requests**: [GitHub Issues](https://github.com/your-github-username/claude-code-salesforce-skills/issues)
- **Questions**: [GitHub Discussions](https://github.com/your-github-username/claude-code-salesforce-skills/discussions)

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2024-2025 Jag Valaiyapathy

## 🙏 Acknowledgments

- Built for the [Claude Code](https://claude.ai/code) ecosystem
- Designed for [Salesforce](https://www.salesforce.com/) developers
- Inspired by the need for production-ready, validated automation

## 🔗 Related Projects

- [Claude Code Documentation](https://docs.anthropic.com/claude/docs)
- [Salesforce CLI](https://developer.salesforce.com/tools/sfdxcli)
- [Salesforce Flow Documentation](https://help.salesforce.com/s/articleView?id=sf.flow.htm)

## 📊 Project Status

- ✅ **sf-deployment**: Stable, production-ready (v2.1.0)
- ✅ **sf-flow-builder**: Stable, active development (v1.3.0)
- ✅ **skill-builder**: Stable, feature-complete (v2.0.0)

## 🗺️ Roadmap

- [ ] Add GitHub Actions workflow for automated validation
- [ ] Create video tutorials and demos
- [ ] Add more Salesforce skills (LWC, Apex testing)
- [ ] Marketplace submission (when available)
- [ ] Integration with popular Salesforce DevOps tools

---

**Made with ❤️ for the Salesforce and Claude Code communities**

[⭐ Star this repository](https://github.com/your-github-username/claude-code-salesforce-skills) if you find it helpful!
