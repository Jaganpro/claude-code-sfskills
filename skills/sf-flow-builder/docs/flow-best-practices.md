# Salesforce Flow Best Practices Guide

> **Version**: 2.0.0
> **Last Updated**: December 2025
> **Applies to**: All flow types (Screen, Record-Triggered, Scheduled, Platform Event, Autolaunched)

This guide consolidates best practices for building maintainable, performant, and secure Salesforce Flows.

---

## Table of Contents

1. [Flow Element Organization](#1-flow-element-organization)
2. [Using $Record in Record-Triggered Flows](#2-using-record-in-record-triggered-flows)
3. [Query Optimization](#3-query-optimization)
4. [When to Use Subflows](#4-when-to-use-subflows)
5. [Three-Tier Error Handling](#5-three-tier-error-handling)
6. [Multi-Step DML Rollback Strategy](#6-multi-step-dml-rollback-strategy)
7. [Transaction Management](#7-transaction-management)
8. [Screen Flow UX Best Practices](#8-screen-flow-ux-best-practices)
9. [Bypass Mechanism for Data Loads](#9-bypass-mechanism-for-data-loads)
10. [Flow Activation Guidelines](#10-flow-activation-guidelines)
11. [Variable Naming Conventions](#11-variable-naming-conventions)

---

## 1. Flow Element Organization

Structure your flow elements in this sequence for maintainability:

| Order | Element Type | Purpose |
|-------|--------------|---------|
| 1 | Variables & Constants | Define all data containers first |
| 2 | Start Element | Entry conditions, triggers, schedules |
| 3 | Initial Record Lookups | Retrieve needed data early |
| 4 | Formula Definitions | Define calculations before use |
| 5 | Decision Elements | Branching logic |
| 6 | Assignment Elements | Data preparation/manipulation |
| 7 | Screens (if Screen Flow) | User interaction |
| 8 | DML Operations | Create/Update/Delete records |
| 9 | Error Handling | Fault paths and rollback |
| 10 | Ending Elements | Complete flow, return outputs |

### Why This Order Matters

- **Readability**: Reviewers can follow the logical flow
- **Maintainability**: Easy to locate elements by function
- **Debugging**: Errors trace back to predictable locations

---

## 2. Using $Record in Record-Triggered Flows

When your flow is triggered by a record change, use `$Record` to access field values instead of querying the same object again.

### Anti-Pattern (Avoid)

```
Trigger: Account record updated
Step 1: Get Records → Query Account where Id = {!$Record.Id}
Step 2: Use queried Account fields
```

**Problems**:
- Wastes a SOQL query (you already have the record!)
- Adds unnecessary complexity
- Can cause timing issues with stale data

### Best Practice

```
Trigger: Account record updated
Step 1: Use {!$Record.Name}, {!$Record.Industry} directly
```

**Benefits**:
- Zero additional SOQL queries
- Always has current field values
- Simpler, more readable flow

### When You DO Need to Query

Query the trigger object only when you need:
- Related records (e.g., Account's Contacts)
- Fields not included in the trigger context
- Historical comparison (`$Record__Prior`)

---

## 3. Query Optimization

### Use 'In' and 'Not In' Operators

When filtering against a collection of values, use `In` or `Not In` operators instead of multiple OR conditions.

**Best Practice**:
```
Get Records where Status IN {!col_StatusValues}
```

**Avoid**:
```
Get Records where Status = 'Open' OR Status = 'Pending' OR Status = 'Review'
```

### Always Add Filter Conditions

Every Get Records element should have filter conditions to:
- Limit the result set
- Improve query performance
- Avoid hitting governor limits

### Use getFirstRecordOnly

When you expect a single record (e.g., looking up by unique ID), enable `getFirstRecordOnly`:
- Improves performance
- Clearer intent
- Simpler variable handling

### Avoid storeOutputAutomatically

When `storeOutputAutomatically="true"`, ALL fields are retrieved and stored:

**Risks**:
- Exposes sensitive data unintentionally
- Impacts performance with large objects
- Security issue in screen flows (external users see all data)

**Fix**: Explicitly specify only the fields you need in the Get Records element.

---

## 4. When to Use Subflows

Use subflows for:

### 1. Reusability
Same logic needed in multiple flows? Extract it to a subflow.
- Error logging
- Email notifications
- Common validations

### 2. Complex Orchestration
Break large flows into manageable pieces:
- Main flow orchestrates
- Subflows handle specific responsibilities
- Easier to test individually

### 3. Permission Elevation
When a flow running in user context needs elevated permissions:
- Main flow runs in user context
- Subflow runs in system context for specific operations
- Maintains security while enabling functionality

### 4. Organizational Clarity
If your flow diagram is unwieldy:
- Extract logical sections into subflows
- Name subflows descriptively
- Document the orchestration pattern

### Subflow Naming Convention

Use the `Sub_` prefix:
- `Sub_LogError`
- `Sub_SendEmailAlert`
- `Sub_ValidateRecord`
- `Sub_BulkUpdater`

---

## 5. Three-Tier Error Handling

Implement comprehensive error handling at three levels:

### Tier 1: Input Validation (Pre-Execution)

**When**: Before any DML operations
**What to Check**:
- Null/empty required values
- Business rule prerequisites
- Data format validation

**Action**: Show validation error screen or set error output variable

### Tier 2: DML Error Handling (During Execution)

**When**: On every DML element (Create, Update, Delete)
**What to Do**:
- Add fault paths to ALL DML elements
- Capture `{!$Flow.FaultMessage}` for context
- Include record IDs and operation type in error messages

**Action**: Route to error handler, prepare for rollback

### Tier 3: Rollback Handling (Post-Failure)

**When**: After a DML failure when prior operations succeeded
**What to Do**:
- Delete records created earlier in the transaction
- Restore original values if updates failed
- Log the failure for debugging

**Action**: Execute rollback, notify user/admin

### Error Message Best Practice

Include context in every error message:
```
"Failed to create Contact for Account {!rec_Account.Id}: {!$Flow.FaultMessage}"
"Update failed on Opportunity {!rec_Opportunity.Id} during {!var_CurrentOperation}"
```

---

## 6. Multi-Step DML Rollback Strategy

When a flow performs multiple DML operations, implement rollback paths.

### Pattern: Primary → Dependent → Rollback Chain

#### Step 1: Create Primary Record (e.g., Account)
- On success → Continue to step 2
- On failure → Show error, stop flow

#### Step 2: Create Dependent Records (e.g., Contacts, Opportunities)
- On success → Continue to step 3
- On failure → **DELETE primary record**, show error

#### Step 3: Update Related Records
- On success → Complete flow
- On failure → **DELETE dependents, DELETE primary**, show error

### Implementation Pattern

```
1. Create Account → Store ID in var_AccountId
2. Create Contacts → On fault: Delete Account using var_AccountId
3. Create Opportunities → On fault: Delete Contacts, Delete Account
4. Success → Return output variables
```

### Error Message Pattern

Use `errorMessage` output variable to surface failures:
```
"Failed to create Account: {!$Flow.FaultMessage}"
"Failed to create Contact: {!$Flow.FaultMessage}. Account rolled back."
```

---

## 7. Transaction Management

### Understanding Flow Transactions

- All DML in a flow runs in a **single transaction** (unless using async)
- If any DML fails, **all changes roll back automatically**
- Use this to your advantage for data integrity

### Save Point Pattern

For complex multi-step flows where you need manual rollback control:

1. Create primary records
2. Store IDs of created records in a collection
3. Create dependent records
4. On failure → Use stored IDs for manual rollback

### Transaction Limits to Consider

| Limit | Value |
|-------|-------|
| DML statements per transaction | 150 |
| SOQL queries per transaction | 100 |
| Records retrieved by SOQL | 50,000 |
| DML rows per transaction | 10,000 |

### Document Transaction Boundaries

Add comments in flow description:
```
TRANSACTION: Creates Account → Creates Contact → Updates related Opportunities
```

---

## 8. Screen Flow UX Best Practices

### Progress Indicators

For multi-step flows (3+ screens):
- Use Screen component headers to show "Step X of Y"
- Consider visual progress bars for long wizards
- Update progress on each screen transition

### Button Design

#### Naming Pattern
Use: `Action_[Verb]_[Object]`
- `Action_Save_Contact`
- `Action_Submit_Application`
- `Action_Cancel_Request`

#### Button Ordering
1. **Primary action** first (Submit, Save, Confirm)
2. **Secondary actions** next (Save Draft, Back)
3. **Tertiary/Cancel** last (Cancel, Exit)

### Navigation Controls

#### Standard Navigation Pattern

| Button | Position | When to Show |
|--------|----------|--------------|
| Previous | Left | After first screen (if safe) |
| Cancel | Left | Always |
| Next | Right | Before final screen |
| Finish/Submit | Right | Final screen only |

#### When to Disable Back Button

Disable "Previous" when returning would:
- Cause duplicate record creation
- Lose unsaved complex data
- Break transaction integrity
- Confuse business process state

### Screen Instructions

For complex screens, add instruction text at the top:
- Use Display Text component
- Keep instructions concise (1-2 sentences)
- Highlight required fields or important notes

Example: "Complete all required fields (*) before proceeding."

### Performance Tips

- **Lazy Loading**: Don't load all data upfront; query as needed per screen
- **Minimize Screens**: Each screen = user wait time; combine where logical
- **Avoid Complex Formulas**: In screen components (impacts render time)
- **LWC for Complex UI**: Consider Lightning Web Components for rich interactions

---

## 9. Bypass Mechanism for Data Loads

When loading large amounts of data, flows can cause performance issues. Implement a bypass mechanism using Custom Metadata.

### Setup Pattern

#### Step 1: Create Custom Metadata Type

Create `Flow_Bypass_Settings__mdt` with fields:
- `Bypass_Flows__c` (Checkbox)
- `Flow_API_Name__c` (Text) - optional, for granular control

#### Step 2: Add Decision at Flow Start

Add a Decision element as the first step after Start:

**Condition**: `{!$CustomMetadata.Flow_Bypass_Settings__mdt.Default.Bypass_Flows__c} = true`
- **If true** → End flow early (no processing)
- **If false** → Continue normal processing

### Use Cases

- Data migrations
- Bulk data loads via Data Loader
- Integration batch processing
- Initial org setup/seeding

### Best Practice

- Document which flows support bypass
- Ensure bypass is disabled after data load completes
- Consider logging when bypass is active

---

## 10. Flow Activation Guidelines

### When to Keep Flows in Draft

- During development and testing
- Before user acceptance testing (UAT) is complete
- When dependent configurations aren't deployed yet

### Deployment Recommendation

1. Deploy flows as **Draft** initially
2. Validate in target environment
3. Test with representative data
4. Activate only after verification
5. Keep previous version as backup before activating new version

### Scheduled Flow Considerations

Scheduled flows run automatically without user interaction:
- Test thoroughly before activation
- Verify schedule frequency is correct
- Ensure error notifications are configured
- Monitor first few executions

---

## 11. Variable Naming Conventions

Use consistent prefixes for all variables:

| Prefix | Purpose | Example |
|--------|---------|---------|
| `var_` | Regular variables | `var_AccountName` |
| `col_` | Collections | `col_ContactIds` |
| `rec_` | Record variables | `rec_Account` |
| `inp_` | Input variables | `inp_RecordId` |
| `out_` | Output variables | `out_IsSuccess` |

### Why Prefixes Matter

- **Clarity**: Immediately understand variable type
- **Debugging**: Easier to trace values in debug logs
- **Maintenance**: New developers understand intent quickly
- **Consistency**: Team-wide standards reduce confusion

### Element Naming

For flow elements (decisions, assignments, etc.):
- Use `PascalCase_With_Underscores`
- Be descriptive: `Check_Account_Type` not `Decision_1`
- Include context: `Get_Related_Contacts` not `Get_Records`

---

## Quick Reference Checklist

- [ ] Use `$Record` instead of querying trigger object
- [ ] Add filters to all Get Records elements
- [ ] Enable `getFirstRecordOnly` when expecting single record
- [ ] Disable `storeOutputAutomatically` (specify fields explicitly)
- [ ] Add fault paths to all DML operations
- [ ] Implement rollback for multi-step DML
- [ ] Use variable naming prefixes (`var_`, `col_`, `rec_`, etc.)
- [ ] Add progress indicators to multi-screen flows
- [ ] Test with bulk data (200+ records)
- [ ] Keep flows in Draft until fully tested

---

## Related Documentation

- [Orchestration Guide](./orchestration-guide.md) - Parent-child and sequential patterns
- [Subflow Library](./subflow-library.md) - Reusable subflow templates
- [Testing Guide](./testing-guide.md) - Comprehensive testing strategies
- [Governance Checklist](./governance-checklist.md) - Security and compliance
- [XML Gotchas](./xml-gotchas.md) - Common XML pitfalls
