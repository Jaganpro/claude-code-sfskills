# Simple FAQ Agent Example

A minimal working example of an Agentforce agent using Agent Script.

## Overview

This agent demonstrates the simplest possible Agentforce implementation:
- Pure LLM reasoning (no external actions)
- Single FAQ topic with clear instructions
- Proper topic navigation with labels and descriptions
- Session state tracking via variables
- Required linked variables for messaging context
- Escalation to human agent capability

## Files

```
simple-faq-agent/
├── Simple_FAQ_Agent.agent          # The agent definition
├── Simple_FAQ_Agent.bundle-meta.xml # Required metadata XML
└── README.md                        # This file
```

## Key Features

| Feature | Implementation |
|---------|----------------|
| Entry point | `start_agent topic_selector` with label |
| Main topic | `topic faq_handler` with label |
| Exit topic | `topic farewell` with label |
| Escalation | `topic escalation` with @utils.escalate |
| Linked Variables | `EndUserId`, `RoutableId`, `ContactId` |
| Mutable Variables | `user_question`, `conversation_topic`, `question_count` |
| Language | `en_US` default locale |

## Agent Structure

```
topic_selector (entry)
    ↓
faq_handler (main)
    ↓         ↓         ↓
topic_selector  farewell  escalation
(loop back)     (exit)    (human)
```

## Deployment

### 1. Copy to your Salesforce DX project

```bash
mkdir -p force-app/main/default/aiAuthoringBundles/Simple_FAQ_Agent
cp Simple_FAQ_Agent.agent force-app/main/default/aiAuthoringBundles/Simple_FAQ_Agent/
cp Simple_FAQ_Agent.bundle-meta.xml force-app/main/default/aiAuthoringBundles/Simple_FAQ_Agent/
```

### 2. Update the default_agent_user

Edit `Simple_FAQ_Agent.agent` and change `default_agent_user` to a valid user in your org:

```agentscript
config:
    developer_name: "Simple_FAQ_Agent"
    default_agent_user: "your.user@yourorg.salesforce.com"  # Change this!
    agent_label: "Simple FAQ Agent"
    description: "A minimal FAQ agent that answers common questions using AI"
```

### 3. Publish the agent

```bash
sf agent publish authoring-bundle --api-name Simple_FAQ_Agent --target-org your-org-alias
```

This command will:
- Validate the Agent Script syntax
- Create Bot, BotVersion, and GenAi metadata
- Deploy the AiAuthoringBundle to your org

### 4. Open in Agentforce Studio

```bash
sf org open agent --api-name Simple_FAQ_Agent --target-org your-org-alias
```

### 5. Activate when ready

```bash
sf agent activate --api-name Simple_FAQ_Agent --target-org your-org-alias
```

## Customization Ideas

### Add specific FAQ topics

```agentscript
variables:
    faq_category: mutable string
        description: "Category of FAQ (shipping, returns, billing)"

start_agent topic_selector:
    label: "Topic Selector"
    description: "Routes to appropriate FAQ category"

    reasoning:
        instructions: ->
            | Determine what category the user's question falls into.
        actions:
            shipping_faq: @utils.transition to @topic.shipping_faq
            returns_faq: @utils.transition to @topic.returns_faq
```

### Add an external action

```agentscript
topic order_lookup:
    label: "Order Lookup"
    description: "Looks up order status for customers"

    actions:
        get_order_status:
            description: "Look up order status"
            inputs:
                order_id: string
                    description: "Order ID"
            outputs:
                status: string
                    description: "Current status"
            target: "flow://Get_Order_Status"

    reasoning:
        instructions: ->
            | Help the user check their order status.
        actions:
            check_order: @actions.get_order_status
                with order_id=...
                set @variables.order_status = @outputs.status
```

## Validation

Run the validator to check the agent:

```bash
python3 ~/.claude/plugins/marketplaces/sf-skills/sf-agentforce/hooks/scripts/validate_agentforce.py Simple_FAQ_Agent.agent
```

Expected output:
```
Score: 100/100 ⭐⭐⭐⭐⭐ Excellent
├─ Structure & Syntax: 20/20 (100%)
├─ Topic Design: 20/20 (100%)
├─ Action Integration: 20/20 (100%)
├─ Variable Management: 15/15 (100%)
├─ Instructions Quality: 15/15 (100%)
└─ Security & Guardrails: 10/10 (100%)

✅ No issues found!
```

## Requirements

- API Version: 64.0+ (Summer '25 or later)
- Salesforce CLI: @salesforce/plugin-agent v1.25.0 or later
- Licenses: Agentforce (Default), Einstein Prompt Templates

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Agent not found" | Ensure sfdx-project.json exists in project root |
| "NEW AGENT USER not found" | Update `default_agent_user` to a valid org user |
| "Internal Error" | Try a different user or check org permissions |
| Syntax errors | Verify TAB indentation (consistent) and `instructions: ->` syntax |
| Missing commands | Run `sf plugins install @salesforce/plugin-agent@latest` |
