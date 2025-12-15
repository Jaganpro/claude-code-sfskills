# Testing & Validation Guide

This guide documents tested Agent Script patterns and common deployment issues based on systematic validation testing (December 2025).

## Deployment Methods

There are **two ways** to deploy Agentforce agents, each with **different capabilities and limitations**:

### ⚠️ CRITICAL: Method Comparison

| Aspect | GenAiPlannerBundle | AiAuthoringBundle |
|--------|-------------------|-------------------|
| Command | `sf project deploy start` | `sf agent publish authoring-bundle` |
| **Visible in Agentforce Studio** | ❌ NO | ✅ YES |
| Flow Actions (`flow://`) | ✅ Supported | ❌ NOT Supported |
| Escalation (`@utils.escalate`) | ✅ Supported | ❌ NOT Supported |
| Topic Transitions | ✅ Supported | ✅ Supported |
| Variables | ✅ No default required | ⚠️ Requires default value |
| API Version | v65.0+ required | v64.0+ |

**Choose your method based on requirements:**
- **Need visible agents in Agentforce Studio?** → Use AiAuthoringBundle (but limited features)
- **Need flow actions or escalation?** → Use GenAiPlannerBundle (but not visible in UI)

### Why Do These Limitations Exist?

The two deployment methods correspond to **two different authoring experiences**:

| Aspect | Script View | Canvas/Builder View |
|--------|-------------|---------------------|
| **Deployment** | GenAiPlannerBundle | AiAuthoringBundle |
| **Experience** | Full Agent Script syntax | Low-code visual builder |
| **Utility Actions** | Inherent to script (transition, set variables, escalate) | Not yet in @-mention resource picker |
| **Flow Actions** | Full support with `flow://` targets | Not yet integrated |
| **Variable Management** | Via Script view only | Low-code UI coming soon |

**Key Understanding:**
- Agent Script supports built-in **utility actions** (transition, set variables, escalate) that are **inherent to the script** but are NOT yet available in the Canvas view's @-mention resource picker
- This means these features can **only be added directly via Script view** (GenAiPlannerBundle)
- Salesforce is actively working on feature parity between the two experiences
- Future releases will add utility actions, flow actions, and variable management to the Canvas/Builder view

---

### 1. Metadata API (GenAiPlannerBundle)

Uses standard `sf project deploy start` with `genAiPlannerBundles/` directory.

**⚠️ IMPORTANT:** Agents deployed this way exist in org metadata but do **NOT appear in Agentforce Studio UI**!

```
force-app/main/default/genAiPlannerBundles/
└── My_Agent/
    ├── My_Agent.genAiPlannerBundle           # XML manifest
    └── agentScript/
        └── My_Agent_definition.agent         # Agent Script file
```

**XML Manifest:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<GenAiPlannerBundle xmlns="http://soap.sforce.com/2006/04/metadata">
    <description>Agent description</description>
    <masterLabel>Agent Label</masterLabel>
    <plannerType>Atlas__ConcurrentMultiAgentOrchestration</plannerType>
</GenAiPlannerBundle>
```

**Requirements:**
- `sourceApiVersion: "65.0"` in sfdx-project.json (v65+ required!)
- XML bundle file + Agent Script file in `agentScript/` subfolder

**Supported Features:**
- ✅ Flow actions with `target: "flow://FlowName"`
- ✅ Escalation with `@utils.escalate with reason="..."`
- ✅ Action input/output mapping with `with`/`set` syntax
- ✅ All variable types without default values

---

### 2. Agent Builder DX (AiAuthoringBundle)

Uses `sf agent publish authoring-bundle` with `aiAuthoringBundles/` directory.

**✅ Agents deployed this way ARE visible in Agentforce Studio!**

```
force-app/main/default/aiAuthoringBundles/
└── My_Agent/
    ├── My_Agent.bundle-meta.xml
    └── My_Agent.agent
```

**XML Manifest:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<AiAuthoringBundle xmlns="http://soap.sforce.com/2006/04/metadata">
  <bundleType>AGENT</bundleType>
</AiAuthoringBundle>
```

**Supported Features:**
- ✅ Topic transitions with `@utils.transition to @topic.name`
- ✅ Variables with default values
- ✅ Conditionals and template expressions
- ❌ Flow actions (causes "Internal Error")
- ❌ Escalation syntax `@utils.escalate with reason="..."` (causes SyntaxError)

**Variable Syntax Difference:**
```agentscript
# GenAiPlannerBundle (works without default)
user_name: mutable string
    description: "User's name"

# AiAuthoringBundle (REQUIRES default value)
user_name: mutable string = ""
    description: "User's name"
```

---

## Test Matrix

| Level | Complexity | Features Tested | Status |
|-------|------------|-----------------|--------|
| 1 | Basic | system, config, single start_agent topic | ✅ Verified |
| 2 | Multi-topic | Multiple topics, @utils.transition routing | ✅ Verified |
| 3 | Variables | linked, mutable, language block, variable templates | ✅ Verified |
| 4 | Flow Actions | flow:// targets, inputs/outputs, @actions.* | ✅ Verified |
| 5 | Complex | All features + @utils.escalate, multi-action topics | ✅ Verified |

---

## Validated Working Syntax

### Minimal Working Agent (Level 1)

The simplest deployable agent - no variables, no actions:

```agentscript
system:
    instructions: "You are a friendly greeting agent. Keep responses short and helpful."
    messages:
        welcome: "Hello! How can I help you today?"
        error: "Sorry, I encountered an error."

config:
    developer_name: "Level1_SimpleAgent"
    default_agent_user: "user@example.com"
    agent_label: "Level 1 - Simple Agent"
    description: "Simplest agent test - single topic with greeting"

start_agent greeting:
    label: "Greeting"
    description: "Greets users and offers assistance"
    reasoning:
        instructions: ->
            | Greet the user warmly.
            | Ask how you can help them today.
```

### Agent with Multiple Topics (Level 2)

```agentscript
start_agent topic_selector:
    label: "Topic Selector"
    description: "Routes to topics"
    reasoning:
        instructions: ->
            | Determine what the user needs.
        actions:
            go_sales: @utils.transition to @topic.sales
            go_support: @utils.transition to @topic.support

topic sales:
    label: "Sales"
    description: "Handles sales inquiries"
    reasoning:
        instructions: ->
            | Answer sales-related questions.
        actions:
            go_support: @utils.transition to @topic.support

topic support:
    label: "Support"
    description: "Handles support inquiries"
    reasoning:
        instructions: ->
            | Answer support-related questions.
        actions:
            go_sales: @utils.transition to @topic.sales
```

### Agent with Variables (Level 3)

```agentscript
variables:
    # Linked variables (read-only from Salesforce context)
    EndUserId: linked string
        source: @MessagingSession.MessagingEndUserId
        description: "Messaging End User ID"
    RoutableId: linked string
        source: @MessagingSession.Id
        description: "Messaging Session ID"
    ContactId: linked string
        source: @MessagingEndUser.ContactId
        description: "Contact ID"

    # Mutable variables (can be modified by agent)
    user_name: mutable string
        description: "User's name"
    preference_count: mutable number
        description: "Number of preferences"
    has_preferences: mutable boolean
        description: "Whether user has preferences"

language:
    default_locale: "en_US"
    additional_locales: ""
    all_additional_locales: False
```

**Using Variables in Instructions:**
```agentscript
reasoning:
    instructions: ->
        | Greet the user by name: {!@variables.user_name}
        | Check their preference count: {!@variables.preference_count}
```

### Agent with Flow Action (Level 4)

```agentscript
topic account_lookup:
    label: "Account Lookup"
    description: "Looks up account information using Flow"

    actions:
        get_account:
            description: "Retrieves account information by ID"
            inputs:
                inp_AccountId: string
                    description: "The Salesforce Account ID to look up"
            outputs:
                out_AccountName: string
                    description: "The account name"
                out_Industry: string
                    description: "The account industry"
                out_IsFound: boolean
                    description: "Whether the account was found"
            target: "flow://Get_Account_Info"

    reasoning:
        instructions: ->
            | Ask the user for an Account ID if not provided.
            | Call the get_account action to look up the account.
            | Report the results to the user.
            | If not found, let them know and offer to try again.
        actions:
            lookup_account: @actions.get_account
                with inp_AccountId=...
                set @variables.account_name = @outputs.out_AccountName
                set @variables.account_industry = @outputs.out_Industry
                set @variables.account_found = @outputs.out_IsFound
```

### Complex Agent with Escalation (Level 5)

```agentscript
start_agent router:
    label: "Router"
    description: "Entry point that determines user intent and routes appropriately"
    reasoning:
        instructions: ->
            | Greet the user and determine their needs.
            | If they want to look up an account, go to account lookup.
            | If they have general questions, go to FAQ.
            | If they need a human, escalate.
        actions:
            go_account_lookup: @utils.transition to @topic.account_lookup
            go_faq: @utils.transition to @topic.faq
            escalate_human: @utils.escalate with reason="Customer requested human agent"

topic account_lookup:
    label: "Account Lookup"
    description: "Helps users find and view account information"

    actions:
        get_account:
            description: "Retrieves account information by ID"
            inputs:
                inp_AccountId: string
                    description: "The Salesforce Account ID to look up"
            outputs:
                out_AccountName: string
                    description: "The account name"
                out_Industry: string
                    description: "The account industry"
                out_IsFound: boolean
                    description: "Whether the account was found"
            target: "flow://Get_Account_Info"

    reasoning:
        instructions: ->
            | Ask for an Account ID if the user hasn't provided one.
            | Look up the account using the get_account action.
            | Share the results with the user.
            | Store the account name: {!@variables.account_name}
            | If they need help with something else, route them.
        actions:
            lookup: @actions.get_account
                with inp_AccountId=...
                set @variables.account_name = @outputs.out_AccountName
                set @variables.account_industry = @outputs.out_Industry
                set @variables.account_found = @outputs.out_IsFound
            go_faq: @utils.transition to @topic.faq
            go_router: @utils.transition to @topic.router
            escalate: @utils.escalate with reason="Customer needs account specialist"

topic faq:
    label: "FAQ"
    description: "Answers frequently asked questions"
    reasoning:
        instructions: ->
            | Answer common questions about accounts and services.
            | Use the customer's name if available: {!@variables.customer_name}
            | If they need account lookup, route to that topic.
            | If you cannot help, escalate to a human.
        actions:
            go_account_lookup: @utils.transition to @topic.account_lookup
            go_router: @utils.transition to @topic.router
            escalate: @utils.escalate with reason="Question requires human expertise"
```

---

## Common Deployment Errors & Solutions

### Error: "Internal Error, try again later"

**Causes:**
1. Invalid `default_agent_user` - user doesn't exist in org
2. User lacks Agentforce permissions
3. **Flow action (`flow://`) used in AiAuthoringBundle** ← Most common cause!
4. Transient server issue

**Solutions:**
```bash
# Verify user exists
sf data query --query "SELECT Id, Username FROM User WHERE Username = 'user@example.com'" --target-org [alias]

# If using flow:// target, you MUST use GenAiPlannerBundle instead
# (but agent won't be visible in Agentforce Studio)
sf project deploy start --metadata GenAiPlannerBundle --target-org [alias]
```

### ⚠️ Flow Actions in AiAuthoringBundle - NOT SUPPORTED

**Tested and confirmed (December 2025):** Flow actions (`flow://`) do NOT work with AiAuthoringBundle, even when:
- ✅ The Flow is deployed to the org
- ✅ The Flow is wrapped as a GenAiFunction (Agentforce Action)
- ✅ The GenAiFunction has proper input/output schemas

**All of these approaches fail:**

| Approach | Result |
|----------|--------|
| `target: "flow://MyFlow"` | ❌ Internal Error |
| `target: "flow://MyGenAiFunction"` (wrapped) | ❌ Internal Error |
| `target: "genAiFunction://MyGenAiFunction"` | ❌ Invalid action type |
| Action without target | ❌ Target is required |

**Workaround for visible agents needing Flow actions:**
1. Create the Flow in the org
2. Create a GenAiFunction (Agentforce Action) wrapping the Flow
3. Deploy the GenAiFunction via `sf project deploy start`
4. Create/edit the agent in **Agentforce Studio UI** (not Agent Script)
5. Add the action from the **Asset Library** in the UI

This is a platform limitation - the AiAuthoringBundle → GenAiPlannerBundle conversion does not support flow action binding.

### Error: "SyntaxError: Invalid system instructions"

**Cause:** Using pipe `|` syntax in `system.instructions`

**Wrong:**
```agentscript
system:
    instructions:
        | You are helpful.
```

**Correct:**
```agentscript
system:
    instructions: "You are helpful."
```

### Error: "Unexpected 'actions'"

**Cause:** Defining actions at top level instead of inside topics

**Wrong:**
```agentscript
actions:
    my_action:
        target: "flow://MyFlow"

topic my_topic:
    ...
```

**Correct:**
```agentscript
topic my_topic:
    actions:
        my_action:
            target: "flow://MyFlow"
    ...
```

### Error: "ValidationError: default agent user is required"

**Cause:** Missing `default_agent_user` field in config

**Solution:** Add the field:
```agentscript
config:
    developer_name: "My_Agent"
    default_agent_user: "user@example.com"  # Required!
    agent_label: "My Agent"
    description: "Description"
```

### Error: Reserved word conflict

**Cause:** Using reserved words as input/output parameter names

**Reserved Words:**
- `description`
- `inputs`
- `outputs`
- `target`
- `label`
- `source`

**Solution:** Use prefixed alternatives:
```agentscript
# Wrong
inputs:
    description: string

# Correct
inputs:
    case_description: string
```

---

## Deployment Checklist

Before running `sf agent publish authoring-bundle`:

### Files (Metadata API - GenAiPlannerBundle)
- [ ] `.genAiPlannerBundle` XML file exists
- [ ] `.agent` file in `agentScript/` subfolder
- [ ] Both in `force-app/main/default/genAiPlannerBundles/[AgentName]/`
- [ ] `sourceApiVersion: "65.0"` or higher in sfdx-project.json

### Files (Agent Builder DX - authoring-bundle)
- [ ] `.bundle-meta.xml` file exists alongside `.agent`
- [ ] Both in `force-app/main/default/aiAuthoringBundles/[AgentName]/`

### Syntax
- [ ] TAB indentation recommended (or consistent spaces - never mix tabs and spaces)
- [ ] `developer_name` in config (not `agent_name`)
- [ ] `default_agent_user` set to valid org user
- [ ] `system.instructions` is single quoted string
- [ ] All topics have `label:` and `description:`
- [ ] `instructions: ->` has space before arrow
- [ ] No reserved words as input/output names

### Dependencies
- [ ] Target org has API v64.0+ (v65.0+ for GenAiPlannerBundle deploy)
- [ ] All Flows referenced by `flow://` are deployed
- [ ] All Apex classes referenced by Flows are deployed
- [ ] `default_agent_user` exists in org with Agentforce permissions

### Blocks Present
- [ ] `system:` block (first)
- [ ] `config:` block
- [ ] `variables:` block with linked variables
- [ ] `language:` block
- [ ] `start_agent topic_selector:` entry point
- [ ] At least one additional `topic:`

---

## CLI Commands Quick Reference

### Metadata API Deployment (GenAiPlannerBundle)

```bash
# Deploy agent using standard metadata deploy
sf project deploy start --source-dir force-app/main/default/genAiPlannerBundles/[AgentName] --target-org [alias]

# Deploy all agent bundles
sf project deploy start --metadata GenAiPlannerBundle --target-org [alias]

# Retrieve agent from org
sf project retrieve start --metadata "GenAiPlannerBundle:[AgentName]" --target-org [alias]
```

### Agent Builder DX (authoring-bundle)

```bash
# Validate before publish (optional)
sf agent validate authoring-bundle --api-name [AgentName] --target-org [alias]

# Publish agent
sf agent publish authoring-bundle --api-name [AgentName] --target-org [alias]

# Open in Agentforce Studio
sf org open agent --api-name [AgentName] --target-org [alias]

# Activate agent
sf agent activate --api-name [AgentName] --target-org [alias]
```

### Common Commands

```bash
# Deploy dependencies first
sf project deploy start --metadata Flow --target-org [alias]
sf project deploy start --metadata ApexClass --target-org [alias]

# List agents in org
sf org list metadata --metadata-type GenAiPlannerBundle --target-org [alias]
```

---

## CLI Validation Commands

### sf afdx agent validate

Validates Agent Script syntax before publishing. **RECOMMENDED** to run before every publish.

```bash
# Validate specific agent
sf afdx agent validate --api-name [AgentName] --target-org [alias]
```

**What It Checks:**
- Agent Script syntax validity
- Required blocks present (system, config, language)
- Variable declarations and references
- Topic transitions and action definitions

**Common Validation Errors:**

| Error | Cause | Fix |
|-------|-------|-----|
| `SyntaxError: Unexpected token` | Invalid syntax | Check indentation, colons, quotes |
| `ReferenceError: Unknown variable` | Variable not defined | Add to `variables:` block |
| `TypeError: Invalid type` | Wrong data type | Use valid type (string, number, boolean, etc.) |
| `ValidationError: Missing required field` | Missing config field | Add required field (e.g., `default_agent_user`) |

**Example Workflow:**
```bash
# 1. Validate first (catches errors early)
sf afdx agent validate --api-name My_Agent --target-org myorg

# 2. Only publish if validation passes
sf agent publish --api-name My_Agent --target-org myorg
```

---

## Agent Testing with sf agent test create

Create automated tests for your agent using YAML specifications.

### Test Spec YAML Structure

```yaml
# agent-tests.yaml
testCases:
  - name: "Order Status Check"
    utterance: "What is my order status?"
    expectedTopic: "order_management"
    expectedActions:
      - "get_order_status"

  - name: "Escalation Request"
    utterance: "I want to speak to a human"
    expectedTopic: "escalation"
    expectedActions:
      - "escalate"

  - name: "FAQ Question"
    utterance: "What are your business hours?"
    expectedTopic: "faq"
    expectedActions: []  # No actions expected

  - name: "Account Lookup"
    utterance: "Can you look up account 001ABC123?"
    expectedTopic: "account_lookup"
    expectedActions:
      - "get_account"
    expectedVariables:
      account_id: "001ABC123"
```

### Test Spec Properties

| Property | Type | Description |
|----------|------|-------------|
| `name` | String | Test case name for identification |
| `utterance` | String | User input to test |
| `expectedTopic` | String | Expected topic the agent should route to |
| `expectedActions` | List | Actions that should be invoked |
| `expectedVariables` | Object | Variables that should be set (optional) |

### Running Tests

```bash
# Create tests from spec file
sf agent test create --spec-file ./tests/agent-tests.yaml --target-org [alias]
```

---

## Agent Preview Testing

Preview allows testing agent behavior before production deployment.

### Preview Modes

| Mode | Command | Use When |
|------|---------|----------|
| **Simulated** | `sf agent preview --api-name X` | Apex/Flows not deployed, testing logic |
| **Live** | `sf agent preview --api-name X --use-live-actions --client-app Y` | Integration testing with real data |

### Simulated Mode (Default)

- LLM simulates action responses based on descriptions
- No actual Apex/Flow execution
- Safe for testing - no org data changes
- Good for rapid iteration on agent design

```bash
# Simulated mode
sf agent preview --api-name My_Agent --target-org myorg
```

### Live Mode

- Uses actual Apex/Flows in org
- Requires connected app setup
- Agent must be active
- Tests end-to-end functionality

```bash
# Live mode
sf agent preview --api-name My_Agent --use-live-actions --client-app MyAgentApp --target-org myorg
```

### Preview with Debug Output

Save conversation transcripts and response files for debugging:

```bash
sf agent preview --api-name My_Agent --output-dir ./preview-logs --apex-debug --target-org myorg
```

**Output Files:**
- `transcript.json` - Conversation record with all messages
- `responses.json` - Full API messages with internal details

### Debugging Preview Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "No active agents found" | Agent not activated | Run `sf agent activate` first |
| "Connected app not found" | Not linked to CLI user | Run `sf org login web --client-app` |
| Preview hangs | Action taking too long | Use `--apex-debug`, check SOQL limits |
| Actions not executing | Actions not deployed | Deploy Apex/Flows before preview |

**See `docs/agent-preview-guide.md`** for complete preview setup including connected app configuration.

---

## Testing Best Practices

1. **Validate Early**: Run `sf afdx agent validate` before every publish
2. **Start Simple**: Begin with Level 1 (no actions) to verify basic syntax
3. **Deploy Dependencies First**: Flows and Apex must exist in org before agent publish
4. **Test in Simulated Mode First**: Use simulated preview for rapid iteration
5. **Validate Incrementally**: Test each feature addition before combining
6. **Check User Permissions**: Ensure `default_agent_user` has Agentforce permissions
7. **Use Explicit Errors**: If publish fails with "Internal Error", check dependencies first
8. **Save Transcripts**: Use `--output-dir` to capture test sessions for review
9. **Test Edge Cases**: Include unexpected inputs in test specs to validate guardrails
10. **Automate Tests**: Use `sf agent test create` for regression testing

---

## Complete Testing Workflow

```bash
# 1. Validate Agent Script syntax
sf afdx agent validate --api-name My_Agent --target-org myorg

# 2. Deploy dependencies (Apex, Flows)
sf project deploy start --metadata ApexClass,Flow --target-org myorg

# 3. Publish agent
sf agent publish --api-name My_Agent --target-org myorg

# 4. Preview in simulated mode (quick iteration)
sf agent preview --api-name My_Agent --target-org myorg

# 5. Activate agent
sf agent activate --api-name My_Agent --target-org myorg

# 6. Preview in live mode (integration testing)
sf agent preview --api-name My_Agent --use-live-actions --client-app MyApp --target-org myorg

# 7. Run automated tests
sf agent test create --spec-file ./tests/agent-tests.yaml --target-org myorg
```

---

*Last Updated: December 2025*
*Based on systematic testing with SF CLI v2.115.15 and API v65.0*
