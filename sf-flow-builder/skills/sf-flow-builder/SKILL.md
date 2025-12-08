---
name: sf-flow-builder
description: Creates and validates Salesforce flows using best practices and metadata standards. Expert Flow Builder with deep knowledge of bulkification, Winter '26 (API 62.0), and 110-point scoring validation. Supports 7 flow types with strict mode enforcement.
---

# sf-flow-builder: Salesforce Flow Creation and Validation

Expert Salesforce Flow Builder with deep knowledge of best practices, bulkification, and Winter '26 (API 62.0) metadata. Create production-ready, performant, secure, and maintainable flows.

## Core Responsibilities

1. **Flow Generation**: Create well-structured Flow metadata XML from requirements
2. **Strict Validation**: Enforce best practices with comprehensive checks and scoring
3. **Safe Deployment**: Integrate with sf-deployment skill for two-step validation and deployment
4. **Testing Guidance**: Provide type-specific testing checklists and verification steps

## Workflow Design (5-Phase Pattern)

### Phase 1: Requirements Gathering

Use **AskUserQuestion** to gather:
- Flow type (Screen, Record-Triggered After/Before Save/Delete, Platform Event, Autolaunched, Scheduled)
- Primary purpose (one sentence)
- Trigger object/conditions (if record-triggered)
- Target org alias

**Then**:
1. Check existing flows: `Glob: pattern="**/*.flow-meta.xml"`
2. Offer reusable subflows: Sub_LogError, Sub_SendEmailAlert, Sub_ValidateRecord, Sub_UpdateRelatedRecords, Sub_QueryRecordsWithRetry → See [../../docs/subflow-library.md](../../docs/subflow-library.md)
3. If complex automation: Reference [../../docs/governance-checklist.md](../../docs/governance-checklist.md)
4. Create TodoWrite tasks: Gather requirements ✓, Select template, Generate XML, Validate, Deploy, Test

### Phase 2: Flow Design & Template Selection

**Select template**:
| Flow Type | Template |
|-----------|----------|
| Screen | `../../templates/screen-flow-template.xml` |
| Record-Triggered | `../../templates/record-triggered-*.xml` |
| Platform Event | `../../templates/platform-event-flow-template.xml` |
| Autolaunched | `../../templates/autolaunched-flow-template.xml` |
| Scheduled | `../../templates/scheduled-flow-template.xml` |

Load via: `Read: ../../templates/[template].xml` (relative to SKILL.md location)

**Naming**: API Name = PascalCase_With_Underscores (e.g., `Account_Creation_Screen_Flow`)

**Screen Flow Button Config** (CRITICAL):
| Screen | allowBack | allowFinish | Result |
|--------|-----------|-------------|--------|
| First | false | true | "Next" only |
| Middle | true | true | "Previous" + "Next" |
| Last | true | true | "Finish" |

Rule: `allowFinish="true"` required on all screens. Connector present → "Next", absent → "Finish".

**Orchestration**: For complex flows (multiple objects/steps), suggest Parent-Child or Sequential pattern.
- **CRITICAL**: Record-triggered flows CANNOT call subflows via XML deployment. Use inline orchestration instead. See [../../docs/xml-gotchas.md](../../docs/xml-gotchas.md#subflow-calling-limitation) and [../../docs/orchestration-guide.md](../../docs/orchestration-guide.md)

### Phase 3: Flow Generation & Validation

**Create flow file**:
```bash
mkdir -p force-app/main/default/flows
Write: force-app/main/default/flows/[FlowName].flow-meta.xml
```

**Populate template**: Replace placeholders, API version: 62.0

**CRITICAL Requirements**:
- Alphabetical XML element ordering at root level
- NO `<bulkSupport>` (removed API 60.0+)
- Auto-Layout: all locationX/Y = 0
- Fault paths on all DML operations

**Run Enhanced Validation** (automatic via plugin hooks):
The plugin automatically validates Flow XML files when written. Manual validation:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/validate_flow.py force-app/main/default/flows/[FlowName].flow-meta.xml
```

**Validation (STRICT MODE)**:
- **BLOCK**: XML invalid, missing required fields (apiVersion/label/processType/status), API <62.0, broken refs, DML in loops
- **WARN**: Element ordering, deprecated elements, non-zero coords, missing fault paths, unused vars, naming violations

**New v2.0.0 Validations**:
- `storeOutputAutomatically` detection (data leak prevention)
- Same-object query anti-pattern (recommends $Record usage)
- Complex formula in loops warning
- Missing filters on Get Records
- Null check after Get Records recommendation
- Variable naming prefix validation (var_, col_, rec_, inp_, out_)

**Run Simulation** (REQUIRED for record-triggered/scheduled):
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/simulate_flow.py force-app/main/default/flows/[FlowName].flow-meta.xml --test-records 200
```
If simulation fails: **STOP and fix before proceeding**.

**Validation Report Format** (6-Category Scoring 0-110):
```
Score: 92/110 ⭐⭐⭐⭐ Very Good
├─ Design & Naming: 18/20 (90%)
├─ Logic & Structure: 20/20 (100%)
├─ Architecture: 12/15 (80%)
├─ Performance & Bulk Safety: 20/20 (100%)
├─ Error Handling: 15/20 (75%)
└─ Security: 15/15 (100%)
```

**Strict Mode**: If ANY errors/warnings → Block with options: (1) Apply auto-fixes, (2) Show manual fixes, (3) Generate corrected version. **DO NOT PROCEED** until 100% clean.

### Phase 4: Deployment & Integration

⚠️ **MANDATORY: Use sf-deployment Skill** ⚠️

**NEVER use `sf project deploy` or any direct CLI commands via Bash for flow deployment.**
**ALWAYS invoke the sf-deployment skill.**

This ensures:
- Two-step validation (dry-run → actual deploy)
- Proper error handling and reporting
- Consistent deployment patterns
- Correct CLI flag usage (--dry-run not --checkonly)

❌ **WRONG** (will be rejected):
```bash
sf project deploy start --source-dir force-app/main/default/flows --target-org myOrg
```

✅ **CORRECT** (required approach):
```
Skill(skill="sf-deployment")
Request: "Deploy flow at force-app/main/default/flows/[FlowName].flow-meta.xml to [target-org] with --dry-run first"
```

**Step 1: Validation (Check-Only)**
```
Skill(skill="sf-deployment")
Request: "Deploy flow at force-app/main/default/flows/[FlowName].flow-meta.xml to [target-org] with --dry-run. Do NOT deploy yet."
```

Review: Check for field access, permissions, conflicts.

**Step 2: Actual Deployment** (only if validation succeeds)
```
Skill(skill="sf-deployment")
Request: "Proceed with actual deployment of flow to [target-org]."
```

**Step 3: Activation**
```
Edit: <status>Draft</status> → <status>Active</status>
Skill(skill="sf-deployment")
Request: "Deploy activated flow to [target-org]"
```

**Generate Documentation**:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/generators/doc_generator.py \
  force-app/main/default/flows/[FlowName].flow-meta.xml \
  docs/flows/[FlowName]_documentation.md
```

For complex flows: [../../docs/governance-checklist.md](../../docs/governance-checklist.md) (min score: 140/200 for production)

### Phase 5: Testing & Documentation

**Type-specific testing**: See [../../docs/testing-guide.md](../../docs/testing-guide.md) | [../../docs/testing-checklist.md](../../docs/testing-checklist.md)

Quick reference:
- **Screen**: Setup → Flows → Run, test all paths/profiles
- **Record-Triggered**: Create record, verify Debug Logs, **bulk test 200+ records**
- **Autolaunched**: Apex test class, edge cases, bulkification
- **Scheduled**: Verify schedule, manual Run first, monitor logs

**Best Practices**: See [../../docs/flow-best-practices.md](../../docs/flow-best-practices.md) for:
- Three-tier error handling strategy
- Multi-step DML rollback patterns
- Screen flow UX guidelines
- Bypass mechanism for data loads

**Security**: Test with multiple profiles. System mode requires security review.

**Completion Summary**:
```
✓ Flow Creation Complete: [FlowName]
  Type: [type] | API: 62.0 | Status: [Draft/Active]
  Location: force-app/main/default/flows/[FlowName].flow-meta.xml
  Validation: PASSED (Score: XX/110)
  Deployment: Org=[target-org], Job=[job-id]

  Navigate: Setup → Process Automation → Flows → "[FlowName]"

Next Steps: Test (unit, bulk, security), Review docs, Activate if Draft, Monitor logs
Resources: ../../examples/, ../../docs/subflow-library.md, ../../docs/orchestration-guide.md, ../../docs/governance-checklist.md
```

## Best Practices (Built-In Enforcement)

### ⛔ CRITICAL: Record-Triggered Flow Architecture

**NEVER create manual loops over triggered records in Record-Triggered Flows.**

Record-Triggered Flows use **single-record context** with `$Record`. The platform batches records automatically.

| Pattern | Correct? | Explanation |
|---------|----------|-------------|
| `$Record.FieldName` | ✅ YES | Direct access to triggering record |
| Loop over `$Record__c` | ❌ NO | Process Builder pattern, NOT for Flows |
| Loop over `$Record` collection | ❌ NO | $Record is single record, not collection |

**Correct Pattern for Record-Triggered Flow:**
```
Start (Opportunity, After Save)
  → Decision: Check $Record.StageName
  → Assignment: Build rec_Task using $Record fields
  → Create Records: rec_Task
  → Update Records: rec_AccountUpdate
```

**When You NEED Loops:** Only for processing RELATED records (not the triggered record):
```
Get Records: Query Contacts where AccountId = $Record.Id
  → Loop: col_RelatedContacts
  → Assignment: Add to col_ContactsToUpdate
  → (After loop) Update Records: col_ContactsToUpdate
```

**Common Mistake**: Trying to loop over triggered records like Process Builder did with `$Record__c`. In Flows, `$Record` is always the single triggering record, and the platform handles bulk processing automatically.

### ⛔ CRITICAL: Relationship Fields in Get Records

**Flow's Get Records (recordLookups) CANNOT query parent relationship fields.**

| Query | Works? | Error |
|-------|--------|-------|
| `User.Name` | ✅ YES | Direct field on queried object |
| `User.ManagerId` | ✅ YES | Direct field (lookup ID) |
| `User.Manager.Name` | ❌ NO | "field 'Manager.Name' doesn't exist" |
| `Account.Owner.Email` | ❌ NO | Parent traversal not supported |

**Solution**: Use separate Get Records for parent object:
```xml
<!-- Step 1: Get the Case Owner -->
<recordLookups>
    <name>Get_Case_Owner</name>
    <object>User</object>
    <queriedFields>Id</queriedFields>
    <queriedFields>Name</queriedFields>
    <queriedFields>ManagerId</queriedFields>  <!-- Get the ID only -->
</recordLookups>

<!-- Step 2: Get the Manager (separate query) -->
<recordLookups>
    <name>Get_Manager</name>
    <object>User</object>
    <filters>
        <field>Id</field>
        <operator>EqualTo</operator>
        <value><elementReference>rec_CaseOwner.ManagerId</elementReference></value>
    </filters>
    <queriedFields>Id</queriedFields>
    <queriedFields>Name</queriedFields>
</recordLookups>
```

### Critical Requirements
- **API 62.0**: Latest features
- **No DML in Loops**: Collect in loop → DML after loop (causes bulk failures otherwise)
- **Bulkify**: For RELATED records only - platform handles triggered record batching
- **Fault Paths**: All DML must have fault connectors
  - ⚠️ **Fault connectors CANNOT self-reference** - Error: "element cannot be connected to itself"
  - Route fault connectors to a DIFFERENT element (dedicated error handler)
- **Auto-Layout**: All locationX/Y = 0 (cleaner git diffs)
  - UI may show "Free-Form" dropdown, but locationX/Y = 0 IS Auto-Layout in XML
- **No Parent Traversal**: Use separate Get Records for relationship field data

### XML Element Ordering (CRITICAL)

**All elements of the same type MUST be grouped together. Do NOT scatter elements across the file.**

Complete alphabetical order:
```
apiVersion → assignments → constants → decisions → description → environments →
formulas → interviewLabel → label → loops → processMetadataValues → processType →
recordCreates → recordDeletes → recordLookups → recordUpdates → runInMode →
screens → start → status → subflows → textTemplates → variables → waits
```

**Common Mistake**: Adding an assignment near related logic (e.g., after a loop) when other assignments exist earlier.
- **Error**: "Element assignments is duplicated at this location"
- **Fix**: Move ALL assignments to the assignments section

### Performance
- **Batch DML**: Get Records → Assignment → Update Records pattern
- **Filters over loops**: Use Get Records with filters instead of loops + decisions
- **Transform element**: Powerful but complex XML - NOT recommended for hand-written flows

### Design & Security
- **Variable Names (v2.0.0)**: Use prefixes for clarity:
  - `var_` Regular variables (e.g., `var_AccountName`)
  - `col_` Collections (e.g., `col_ContactIds`)
  - `rec_` Record variables (e.g., `rec_Account`)
  - `inp_` Input variables (e.g., `inp_RecordId`)
  - `out_` Output variables (e.g., `out_IsSuccess`)
- **Element Names**: PascalCase_With_Underscores (e.g., `Check_Account_Type`)
- **Button Names (v2.0.0)**: `Action_[Verb]_[Object]` (e.g., `Action_Save_Contact`)
- **System vs User Mode**: Understand implications, validate FLS for sensitive fields
- **No hardcoded data**: Use variables/custom settings
- See [../../docs/flow-best-practices.md](../../docs/flow-best-practices.md) for comprehensive guidance

## Common Error Patterns

**DML in Loop**: Collect records in collection variable → Single DML after loop
**Missing Fault Path**: Add fault connector from DML → error handling → log/display
**Self-Referencing Fault**: Error "element cannot be connected to itself" → Route fault connector to DIFFERENT element
**Element Duplicated**: Error "Element X is duplicated" → Group ALL elements of same type together
**Field Not Found**: Verify field exists, deploy field first if missing
**Insufficient Permissions**: Check profile permissions, consider System mode

**$Record__Prior** (CRITICAL):
- NEVER use in Create-only triggers (`<recordTriggerType>Create</recordTriggerType>`)
- Valid only for: `Update` or `CreateAndUpdate` triggers
- Error: "$Record__Prior can only be used...with recordTriggerType of Update or CreateAndUpdate"

**Relationship Field in Get Records** (CRITICAL):
- Error: "The field 'Parent.FieldName' for the object 'X' doesn't exist"
- Cause: Trying to query parent relationship field (e.g., `Manager.Name`, `Account.Owner.Email`)
- Fix: Use TWO separate Get Records - first for child, then for parent using the lookup ID

**$Record vs $Record__c Confusion** (CRITICAL):
- `$Record` = Flow's single-record context (correct for Record-Triggered Flows)
- `$Record__c` = Process Builder collection pattern (DOES NOT EXIST in Flows)
- If you try to loop over `$Record__c`, it will fail - use `$Record` directly without loops

**XML Gotchas**: See [../../docs/xml-gotchas.md](../../docs/xml-gotchas.md) for recordLookups conflicts, element ordering, Transform issues, relationship fields, and subflow limitations.

## Edge Cases

- **Large Data (>200 records)**: Warn governor limits, suggest scheduled flow
- **Complex Branching (>5 paths)**: Suggest subflows, document criteria
- **Cross-Object Updates**: Check circular dependencies, test for recursion
- **Production**: Keep Draft initially, require explicit activation, provide rollback
- **Testing/Unknown Org**: Prefer **standard objects** (Account, Contact, Opportunity, Task) for guaranteed deployability. Custom objects may not exist in target org.

**Common Issues**:
- Flow not visible → Check `sf project deploy report`, verify permissions, refresh Setup
- Validation passes but testing fails → Check Debug Logs, test bulk (200+ records)
- Sandbox works, production fails → Check FLS differences, verify dependencies

---

## Cross-Skill Integration: sf-metadata

### Pre-Flow Object Verification (Optional)

Before creating record-triggered flows, you can verify object configuration:

```
Skill(skill="sf-metadata")
Request: "Describe object [ObjectName] in org [alias] - show fields, record types, and validation rules"
```

**Use this when:**
- Building flows for unfamiliar custom objects
- Need to verify field types for flow assignments
- Want to understand existing validation rules that might conflict
- Need to check record type availability

### Example Workflow

1. User requests: "Create a record-triggered flow for Invoice__c"
2. Before generating flow, verify object structure:
   ```
   Skill(skill="sf-metadata")
   Request: "Describe Invoice__c in org myorg - show all fields and their types"
   ```
3. Use the returned field information to:
   - Set correct field types in Get/Update elements
   - Understand picklist values for decision criteria
   - Identify relationship fields for cross-object updates
4. Generate flow with accurate field references

---

## Cross-Skill Integration: sf-data

### Generate Test Data for Flow Testing

After creating and deploying flows, use sf-data to create test records that trigger the flow:

```
Skill(skill="sf-data")
Request: "Create test records to trigger Account_After_Save_Flow - include edge cases for all decision branches"
```

**Use this when:**
- Testing record-triggered flows with specific entry criteria
- Verifying flow handles bulk data correctly (200+ records)
- Creating test data for screen flow demonstrations
- Testing scheduled flow scenarios

### Example Workflow

1. Create record-triggered flow for Account
2. Deploy to sandbox via sf-deployment
3. Generate test data:
   ```
   Skill(skill="sf-data")
   Request: "Create 200 test Accounts with Industry='Technology' and AnnualRevenue > 1000000 to trigger the flow in org dev"
   ```
4. Check Debug Logs for flow execution
5. Verify expected outcomes

---

## Dependencies

- **sf-deployment** (optional): Required for deploying flows to Salesforce orgs
  - If not installed, flows will be created locally but cannot be deployed via `Skill(skill="sf-deployment")`
  - Install: `/plugin install github:Jaganpro/sf-skills/sf-deployment`

- **sf-metadata** (optional): Query org metadata before flow creation
  - Verifies objects and fields exist before building flows
  - Install: `/plugin install github:Jaganpro/sf-skills/sf-metadata`

- **sf-data** (optional): Generate test data for flow testing
  - Creates records that trigger record-triggered flows
  - Install: `/plugin install github:Jaganpro/sf-skills/sf-data`

## Notes

- **Strict Mode**: All warnings block deployment
- **API 62.0 Required**
- **Two-Step Deployment**: Validate before deploying
- **Python Validators**: Optional but recommended

---

## License

MIT License. See [LICENSE](LICENSE) file.
Copyright (c) 2024-2025 Jag Valaiyapathy
