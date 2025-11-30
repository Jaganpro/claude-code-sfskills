# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- GitHub Actions workflow for automated validation
- Video tutorials and demos
- Additional Salesforce skills (LWC, Apex testing)

---

## [1.0.0] - 2024-11-30

### Added - Initial Release

#### Repository Infrastructure
- **Installation Scripts**: Automated installation, upgrade, and uninstall scripts
  - `install.sh`: One-command installation with global/local options
  - `upgrade.sh`: Version upgrade with automatic backup
  - `uninstall.sh`: Clean removal with backup cleanup
- **Documentation**: Comprehensive README and contribution guidelines
  - Main README with badges, quick start, and architecture
  - CONTRIBUTING.md with detailed contribution workflow
  - This CHANGELOG.md for version tracking
- **License**: MIT License with proper copyright attribution

#### sf-deployment (v2.1.0)
- 5-phase deployment workflow for Salesforce metadata
- Modern `sf` CLI v2.x support with `--dry-run` flag
- Pre-deployment validation and testing
- Comprehensive error handling with actionable guidance
- CI/CD pipeline integration support
- Org management and authentication handling
- Test execution with code coverage tracking
- Production-ready with rollback guidance

**Key Features**:
- Deploy metadata with validation
- Dry-run deployments (check-only)
- Component-specific and manifest-based deployments
- Quick deploy after validation
- Automated test execution
- Deployment monitoring and reporting
- Common error detection and solutions

**Tools**: Bash, Read, Write, Edit, Grep, Glob, AskUserQuestion, TodoWrite

#### sf-flow-builder (v1.3.0)
- Expert Salesforce Flow creation with API 62.0 (Winter '26) support
- 5-phase guided workflow from requirements to deployment
- Strict validation mode with 0-100 scoring system
- Auto-bulkification and DML-in-loop detection
- Transform element usage for 30-50% performance gains
- Simulation mode for governor limit testing
- 7 flow types supported:
  - Screen Flows
  - Record-Triggered (After Save)
  - Record-Triggered (Before Save)
  - Record-Triggered (Before Delete)
  - Platform Event-Triggered
  - Autolaunched
  - Scheduled

**Key Features**:
- Interactive requirements gathering with AskUserQuestion
- Template-based flow generation
- Comprehensive validation (XML, metadata, best practices)
- Two-step deployment (validate, then deploy)
- Type-specific testing checklists
- Integration with sf-deployment skill
- Auto-Layout support (locationX/Y = 0)
- Fault path enforcement for DML operations

**Dependencies**: sf-deployment >=2.0.0

**Tools**: Bash, Read, Write, Edit, Glob, Grep, AskUserQuestion, TodoWrite, Skill, WebFetch

#### skill-builder (v2.0.0)
- Interactive skill creation wizard
- Bulk skill validation with parallel processing
- Dependency management with version constraints
- Terminal-based interactive editor for skill refinement
- Python validation scripts with virtual environment

**Key Features**:
- Step-by-step skill scaffolding
- YAML frontmatter validation
- Tool permission verification
- Template application
- Bulk validation across all installed skills
- Dependency tree visualization
- Circular dependency detection
- Real-time validation feedback
- Automatic backups on save

**Validation Capabilities**:
- YAML syntax checking
- Required field verification
- Tool name validation with suggestions
- Semantic version format checking
- Dependency constraint validation

**Tools**: Bash, Read, Write, Glob, Grep, AskUserQuestion

### Technical Details

#### Architecture
- Modular skill design with clear separation of concerns
- Explicit dependency management (sf-flow-builder → sf-deployment)
- Minimal tool permissions for security
- Production-ready error handling

#### Documentation
- Comprehensive inline documentation (15K-21K per skill)
- Phase-based workflow descriptions
- Error handling patterns with examples
- Troubleshooting quick references
- Best practices enforcement

#### Quality Assurance
- 100% validation pass rate on all skills
- Proper MIT licensing on all components
- Consistent authorship attribution
- Clean directory structures
- No deprecated or test files

### Installation

```bash
git clone https://github.com/your-github-username/claude-code-salesforce-skills.git
cd claude-code-salesforce-skills
./install.sh
```

### Breaking Changes
- None (initial release)

### Deprecations
- None (initial release)

### Security
- All skills request only necessary tool permissions
- No hardcoded credentials or sensitive data
- Safe bash script execution with input validation

### Known Issues
- skill-builder requires Python 3.8+ for validation scripts
- Salesforce skills require sf CLI v2.x
- Skills require Claude Code restart to load after installation

---

## Version History

### Version Numbering
- **MAJOR**: Breaking changes to skill APIs or frontmatter
- **MINOR**: New features, templates, or capabilities
- **PATCH**: Bug fixes, documentation updates

### Previous Versions
- No previous versions (initial release)

---

## Contributors

### Core Team
- **Jag Valaiyapathy** - Original author and maintainer

### Special Thanks
- Claude Code team for the amazing platform
- Salesforce community for Flow best practices
- Early testers and feedback providers

---

## Links
- [Repository](https://github.com/your-github-username/claude-code-salesforce-skills)
- [Issues](https://github.com/your-github-username/claude-code-salesforce-skills/issues)
- [Discussions](https://github.com/your-github-username/claude-code-salesforce-skills/discussions)
- [License](LICENSE)

---

**Note**: Replace `your-github-username` with your actual GitHub username when publishing.
