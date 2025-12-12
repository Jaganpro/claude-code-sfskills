---
name: sf-deploy
description: Comprehensive Salesforce DevOps automation using sf CLI v2. Handles deployments, CI/CD pipelines, scratch orgs, and metadata management with built-in validation and error handling.
---

# sf-deploy: Comprehensive Salesforce DevOps Automation

Expert Salesforce DevOps engineer specializing in deployment automation, CI/CD pipelines, and metadata management using Salesforce CLI (sf v2).

## Core Responsibilities

1. **Deployment Management**: Execute, validate, and monitor deployments (metadata, Apex, LWC)
2. **DevOps Automation**: CI/CD pipelines, automated testing, deployment workflows
3. **Org Management**: Authentication, scratch orgs, environment management
4. **Quality Assurance**: Tests, code coverage, pre-production validation
5. **Troubleshooting**: Debug failures, analyze logs, provide solutions

---

## ⚠️ CRITICAL: Orchestration Order

**sf-metadata → sf-flow → sf-deploy → sf-data** (you are here: sf-deploy)

See `shared/docs/orchestration.md` (project root) for details.

**Deploy order WITHIN sf-deploy**: Objects/Fields → Permission Sets → Flows → Apex → Activate Flows

*Why*: Flows need fields, users need FLS, triggers may need active flows.

---

## 🔑 Key Insights for Deployment

### Always Use --dry-run First

```bash
# CORRECT: Validate before deploying
sf project deploy start --dry-run --source-dir force-app --target-org alias
sf project deploy start --source-dir force-app --target-org alias

# WRONG: Deploying without validation
sf project deploy start --source-dir force-app --target-org alias  # Risky!
```

### Deploy Permission Sets After Objects

**Common Error:**
```
Error: In field: field - no CustomObject named ObjectName__c found
```

**Solution:** Deploy objects first, THEN permission sets referencing them.

### Flow Activation (4-Step Process)

**Flows deploy as Draft by default.** Activation steps:
1. Deploy with `<status>Draft</status>`
2. Verify: `sf project deploy report --job-id [id]`
3. Edit XML: `Draft` → `Active`
4. Redeploy

**Why?** Draft lets you verify before activating; if activation fails, flow still exists.

**Common Errors**: "Flow is invalid" (deploy objects first) | "Insufficient permissions" (check Manage Flow) | "Version conflict" (deactivate old version)

### FLS Warning After Deployment

**⚠️ Deployed fields may be INVISIBLE without FLS!**

After deploying custom objects/fields:
1. Deploy Permission Set granting field access
2. Assign Permission Set to user: `sf org assign permset --name PermSetName --target-org alias`
3. Verify field visibility

---

## CLI Version (CRITICAL)

**This skill uses `sf` CLI (v2.x), NOT legacy `sfdx` (v1.x)**

| Legacy sfdx (v1) | Modern sf (v2) |
|-----------------|----------------|
| `--checkonly` / `--check-only` | `--dry-run` |
| `sfdx force:source:deploy` | `sf project deploy start` |

## Prerequisites

Before deployment, verify:
```bash
sf --version              # Requires v2.x
sf org list               # Check authenticated orgs
test -f sfdx-project.json # Valid SFDX project
```

## Deployment Workflow (5-Phase)

### Phase 1: Pre-Deployment Analysis

**Gather via AskUserQuestion**: Target org, deployment scope, validation requirements, rollback strategy.

**Analyze**:
- Read `sfdx-project.json` for package directories
- Glob for metadata: `**/force-app/**/*.{cls,trigger,xml,js,html,css}`
- Grep for dependencies

**TodoWrite tasks**: Validate auth, Pre-tests, Deploy, Monitor, Post-tests, Verify

### Phase 2: Pre-Deployment Validation

```bash
sf org display --target-org <alias>                    # Check connection
sf apex test run --test-level RunLocalTests --target-org <alias> --wait 10  # Local tests
sf project deploy start --dry-run --test-level RunLocalTests --target-org <alias> --wait 30  # Validate
```

### Phase 3: Deployment Execution

**Commands by scope**:
```bash
# Full metadata
sf project deploy start --target-org <alias> --wait 30

# Specific components
sf project deploy start --source-dir force-app/main/default/classes --target-org <alias>

# Manifest-based
sf project deploy start --manifest manifest/package.xml --target-org <alias> --test-level RunLocalTests --wait 30

# Quick deploy (after validation)
sf project deploy quick --job-id <validation-job-id> --target-org <alias>
```

Handle failures: Parse errors, identify failed components, suggest fixes.

### Phase 4: Post-Deployment Verification

```bash
sf project deploy report --job-id <job-id> --target-org <alias>
```

Verify components, run smoke tests, check coverage.

### Phase 5: Documentation

Provide summary with: deployed components, test results, coverage metrics, next steps.

See [examples/deployment-report-template.md](examples/deployment-report-template.md) for output format.

**Deployment Variants**: Production (full + RunAllTests), Hotfix (targeted + RunLocalTests), CI/CD (scripted + gates), Scratch (push source).

## CLI Reference

**Deploy**: `sf project deploy start [--dry-run] [--source-dir <path>] [--manifest <xml>] [--test-level <level>]`
**Quick**: `sf project deploy quick --job-id <id>` | **Status**: `sf project deploy report`
**Test**: `sf apex test run --test-level RunLocalTests` | **Coverage**: `sf apex get test --code-coverage`
**Org**: `sf org list` | `sf org display` | `sf org create scratch` | `sf org open`
**Metadata**: `sf project retrieve start` | `sf org list metadata --metadata-type <type>`

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| FIELD_CUSTOM_VALIDATION_EXCEPTION | Validation rule blocking | Deactivate rules or use valid test data |
| INVALID_CROSS_REFERENCE_KEY | Missing dependency | Include dependencies in deploy |
| CANNOT_INSERT_UPDATE_ACTIVATE_ENTITY | Trigger/validation error | Review trigger logic, check recursion |
| TEST_FAILURE | Test class failure | Fix test or code under test |
| INSUFFICIENT_ACCESS | Permission issue | Verify user permissions, FLS |

### Flow-Specific Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "Element X is duplicated" | Elements not alphabetically ordered | Reorder Flow XML elements |
| "Element bulkSupport invalid" | Deprecated element (API 60.0+) | Remove `<bulkSupport>` |
| "Error parsing file" | Malformed XML | Validate XML syntax |

### Failure Response

1. Parse error output, identify failed components
2. Explain error in plain language
3. Suggest specific fixes with code examples
4. Provide rollback options if needed

## Best Practices

- **Always validate first**: Use `--dry-run` for production
- **Appropriate test levels**: RunLocalTests (deploy), RunAllTests (packages)
- **Code coverage**: >75% for production, >90% recommended
- **Use manifests**: `package.xml` for controlled deployments
- **Version control**: Commit before deploying, tag releases
- **Incremental deploys**: Small, frequent changes over large batches
- **Sandbox first**: Always test before production
- **Backup metadata**: Retrieve before major deployments
- **Quick deploy**: Use for validated changesets

## CI/CD Integration

Standard pipeline workflow:
1. Authenticate (JWT/auth URL)
2. Validate metadata
3. Static analysis (PMD, ESLint)
4. Dry-run deployment
5. Run tests + coverage check
6. Deploy if validation passes
7. Notify

See [examples/deployment-workflows.md](examples/deployment-workflows.md) for scripts.

## Edge Cases

- **Large deployments**: Split into batches (limit: 10,000 files / 39 MB)
- **Test timeout**: Increase wait time or run tests separately
- **Namespace conflicts**: Handle managed package issues
- **API version**: Ensure source/target compatibility

## Cross-Skill Dependency Checklist

**Before deploying, verify these prerequisites from other skills:**

| Dependency | Check Command | Required For |
|------------|---------------|--------------|
| **TAF Package** | `sf package installed list --target-org alias` | TAF trigger pattern (sf-apex) |
| **Custom Objects/Fields** | `sf sobject describe --sobject ObjectName --target-org alias` | Apex/Flow field references |
| **Trigger_Action__mdt** | Check Setup → Custom Metadata Types | TAF trigger execution |
| **Queues** | `sf data query --query "SELECT Id,Name FROM Group WHERE Type='Queue'"` | Flow queue assignments |
| **Permission Sets** | `sf org list metadata --metadata-type PermissionSet` | FLS for custom fields |

**Common Cross-Skill Issues:**

| Error Message | Missing Dependency | Solution |
|--------------|-------------------|----------|
| `Invalid type: MetadataTriggerHandler` | TAF Package | Install apex-trigger-actions package |
| `Field does not exist: Field__c` | Custom Field or FLS | Deploy field or create Permission Set |
| `No such column 'Field__c'` | Field-Level Security | Assign Permission Set to running user |
| `SObject type 'Object__c' not supported` | Custom Object | Deploy object via sf-metadata first |
| `Queue 'QueueName' not found` | Queue Metadata | Deploy queue via sf-metadata first |

### sf-ai-agentforce Integration

**When deploying for Agentforce agents:**
- sf-ai-agentforce MUST use sf-deploy for all Flow and Apex deployments
- Deploy order: Apex classes → Flows → then agent can use `flow://` targets
- Agent publishing uses `sf agent publish authoring-bundle` (NOT sf-deploy)

**Common Agentforce Deployment Pattern:**
```bash
# 1. sf-apex creates InvocableMethod class
# 2. sf-deploy deploys Apex
Skill(skill="sf-deploy")
Request: "Deploy ApexClass:CaseCreationService to [alias] with tests"

# 3. sf-flow creates Flow wrapper
# 4. sf-deploy deploys Flow
Skill(skill="sf-deploy")
Request: "Deploy Flow:Create_Support_Case to [alias]"

# 5. sf-ai-agentforce publishes agent (separate command)
sf agent publish authoring-bundle --api-name AgentName --target-org [alias]
```

---

## Deployment Script Template

Reusable multi-step deployment script: **[examples/deploy.sh](examples/deploy.sh)**

Deploys in order: Objects → Permission Sets → Apex (with tests) → Flows (Draft)

---

## Generate Package Manifest

**Auto-generate package.xml from source directory:**

```bash
# Generate from source
sf project generate manifest --source-dir force-app --name manifest/package.xml

# Generate for specific metadata types
sf project generate manifest \
    --metadata CustomObject:Account \
    --metadata ApexClass \
    --metadata Flow \
    --name manifest/package.xml

# Deploy using manifest
sf project deploy start --manifest manifest/package.xml --target-org alias
```

**When to use manifest vs source-dir:**

| Scenario | Use | Command |
|----------|-----|---------|
| Deploy everything | `--source-dir` | `sf project deploy start --source-dir force-app` |
| Deploy specific components | `--manifest` | `sf project deploy start --manifest package.xml` |
| CI/CD pipelines | `--manifest` | Controlled, reproducible deployments |
| Development iteration | `--source-dir` | Quick local changes |

---

## Notes

- **CLI**: Uses only `sf` (v2) with modern flag syntax
- **Auth**: Supports OAuth, JWT, Auth URL, web login
- **API**: Uses Metadata API (not Tooling API)
- **Async**: Use `--wait` to monitor; most deploys are async
- **Limits**: Be aware of Salesforce governor limits

---

## License

MIT License. See [LICENSE](LICENSE) file.
Copyright (c) 2024-2025 Jag Valaiyapathy
