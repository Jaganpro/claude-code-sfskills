---
name: sf-diagram
description: Creates Salesforce architecture diagrams using Mermaid syntax with ASCII fallback. Supports OAuth flows, data models, integration sequences, system landscapes, role hierarchies, and Agentforce flows. 80-point scoring across 5 categories.
---

# sf-diagram: Salesforce Diagram Generation

Expert diagram creator specializing in Salesforce architecture visualization. Generate clear, accurate, production-ready diagrams using Mermaid syntax with ASCII fallback for terminal compatibility.

## Core Responsibilities

1. **Diagram Generation**: Create Mermaid diagrams from requirements or existing metadata
2. **Multi-Format Output**: Provide both Mermaid code and ASCII art fallback
3. **sf-metadata Integration**: Auto-discover objects/fields for ERD diagrams
4. **Validation & Scoring**: Score diagrams against 5 categories (0-80 points)

## Supported Diagram Types

| Type | Mermaid Syntax | Use Case |
|------|---------------|----------|
| OAuth Flows | `sequenceDiagram` | Authorization Code, JWT Bearer, PKCE, Device Flow |
| Data Models | `erDiagram` | Object relationships, field definitions |
| Integration Sequences | `sequenceDiagram` | API callouts, event-driven flows |
| System Landscapes | `flowchart` | High-level architecture, component diagrams |
| Role Hierarchies | `flowchart` | User hierarchies, profile/permission structures |
| Agentforce Flows | `flowchart` | Agent → Topic → Action flows |

## Workflow (5-Phase Pattern)

### Phase 1: Requirements Gathering

Use **AskUserQuestion** to gather:
- Diagram type (OAuth, ERD, Integration, Landscape, Role Hierarchy, Agentforce)
- Specific flow or scope (e.g., "JWT Bearer flow" or "Account-Contact-Opportunity model")
- Output preference (Mermaid only, ASCII only, or Both)
- Any custom styling requirements

**Then**:
1. If ERD requested, check for sf-metadata availability
2. Create TodoWrite tasks for multi-diagram requests

### Phase 2: Template Selection

**Select template based on diagram type**:

| Diagram Type | Template File |
|--------------|---------------|
| Authorization Code Flow | `oauth/authorization-code.md` |
| Authorization Code + PKCE | `oauth/authorization-code-pkce.md` |
| JWT Bearer Flow | `oauth/jwt-bearer.md` |
| Client Credentials Flow | `oauth/client-credentials.md` |
| Device Authorization Flow | `oauth/device-authorization.md` |
| Refresh Token Flow | `oauth/refresh-token.md` |
| Data Model (ERD) | `datamodel/salesforce-erd.md` |
| Integration Sequence | `integration/api-sequence.md` |
| System Landscape | `architecture/system-landscape.md` |
| Role Hierarchy | `role-hierarchy/user-hierarchy.md` |
| Agentforce Flow | `agentforce/agent-flow.md` |

**Template Path Resolution** (try in order):
1. **Marketplace folder** (always available): `~/.claude/plugins/marketplaces/sf-skills/sf-diagram/templates/[template]`
2. **Project folder** (if working in sf-skills repo): `[project-root]/sf-diagram/templates/[template]`
3. **Cache folder** (if installed individually): `~/.claude/plugins/cache/sf-diagram/*/sf-diagram/templates/[template]`

**Example**: To load JWT Bearer template:
```
Read: ~/.claude/plugins/marketplaces/sf-skills/sf-diagram/templates/oauth/jwt-bearer.md
```

### Phase 3: Data Collection

**For OAuth Diagrams**:
- Use standard actors (Browser, Client App, Salesforce)
- Apply CloudSundial-inspired styling
- Include all protocol steps with numbered sequence

**For ERD Diagrams**:
1. If org connected, invoke sf-metadata:
   ```
   Skill(skill="sf-metadata")
   Request: "Describe objects: Account, Contact, Opportunity"
   ```
2. Extract fields, relationships, and cardinality
3. Map to Mermaid erDiagram syntax

**For Integration Diagrams**:
- Identify all systems involved
- Capture request/response patterns
- Note async vs sync interactions

### Phase 4: Diagram Generation

**Generate Mermaid code**:
1. Apply color scheme from `docs/color-palette.md`
2. Add annotations and notes where helpful
3. Include autonumber for sequence diagrams
4. Use proper cardinality notation for ERDs

**Generate ASCII fallback**:
1. Use box-drawing characters: `┌ ─ ┐ │ └ ┘ ├ ┤ ┬ ┴ ┼`
2. Use arrows: `──>` `<──` `───` `─┼─`
3. Keep width under 80 characters when possible

**Run Validation**:
```
Score: XX/80 ⭐⭐⭐⭐ Rating
├─ Accuracy: XX/20      (Correct actors, flow steps, relationships)
├─ Clarity: XX/20       (Easy to read, proper labeling)
├─ Completeness: XX/15  (All relevant steps/entities included)
├─ Styling: XX/15       (Color scheme, theming, annotations)
└─ Best Practices: XX/10 (Proper notation, UML conventions)
```

### Phase 5: Output & Documentation

**Delivery Format**:

````markdown
## 📊 [Diagram Title]

### Mermaid Diagram
```mermaid
[Generated Mermaid code]
```

### ASCII Fallback
```
[Generated ASCII diagram]
```

### Key Points
- [Important note 1]
- [Important note 2]

### Diagram Score
[Validation results]
````

### Phase 5.5: Preview (Optional)

After generating the diagram, offer the user a localhost preview for real-time iteration.

**Start Preview**:
1. Save Mermaid code to temporary file:
   ```
   Write: /tmp/mermaid-preview.mmd
   [Mermaid code content]
   ```

2. Start preview server (runs in background):
   ```bash
   # From marketplace folder (always available):
   python ~/.claude/plugins/marketplaces/sf-skills/sf-diagram/preview/mermaid_preview.py start --file /tmp/mermaid-preview.mmd

   # Or from project folder (if working locally):
   python [project-root]/sf-diagram/preview/mermaid_preview.py start --file /tmp/mermaid-preview.mmd
   ```

3. Provide URL to user:
   > 📊 **Preview available**: http://localhost:8765
   >
   > The browser will auto-reload when you update the diagram.

**Iteration Workflow**:
- User views diagram in browser
- User requests changes ("make boxes pink", "add another node")
- You update `/tmp/mermaid-preview.mmd` using the Write tool
- Browser auto-reloads with new diagram (via SSE)
- Repeat until user is satisfied

**Stop Preview** (when user is done):
```bash
python ~/.claude/plugins/marketplaces/sf-skills/sf-diagram/preview/mermaid_preview.py stop
```

**Preview Server Features**:
- Live reload via Server-Sent Events (SSE)
- Dark/light theme auto-detection
- Copy Mermaid code button
- Download as SVG button
- Connection status indicator

---

## Mermaid Styling Guide (sf-skills Standard)

Use individual `style` declarations with **Tailwind 200-level pastel fills** and **dark strokes** for consistent, visually soft diagrams.

### Spacing Configuration

Add this init directive at the start of every flowchart for optimal readability:

```
%%{init: {"flowchart": {"nodeSpacing": 80, "rankSpacing": 70}} }%%
```

| Option | Value | Effect |
|--------|-------|--------|
| `nodeSpacing` | 80 | 60% more horizontal space (default: 50) |
| `rankSpacing` | 70 | 40% more vertical space (default: 50) |

**Note**: Omit `curve` to use the default smooth curves (`basis`).

### Primary Color Palette (Tailwind 200 + Dark Borders)

| Component | Fill (200) | Stroke (700+) | Text | Usage |
|-----------|------------|---------------|------|-------|
| AI & Agents | `#fbcfe8` | `#be185d` | `#1f2937` | Agentforce, AI features |
| Integration (Orange) | `#fed7aa` | `#c2410c` | `#1f2937` | Connected Apps, OAuth |
| Integration (Teal) | `#99f6e4` | `#0f766e` | `#1f2937` | Named Creds, callouts |
| Development (Violet) | `#ddd6fe` | `#6d28d9` | `#1f2937` | Apex, services |
| Development (Indigo) | `#c7d2fe` | `#4338ca` | `#1f2937` | Flows, automation |
| Foundation (Cyan) | `#a5f3fc` | `#0e7490` | `#1f2937` | Metadata, objects |
| Foundation (Amber) | `#fde68a` | `#b45309` | `#1f2937` | Data, storage |
| DevOps (Green) | `#a7f3d0` | `#047857` | `#1f2937` | Deploy, CI/CD |
| Utility (Slate) | `#e2e8f0` | `#334155` | `#1f2937` | Tooling |

### Subgraph Background Colors (Tailwind 50-level)

| Subgraph | Fill (50) | Stroke | Style |
|----------|-----------|--------|-------|
| AI & Agents | `#fdf2f8` | `#be185d` | dashed |
| Integration | `#fff7ed` | `#c2410c` | dashed |
| Development | `#f5f3ff` | `#6d28d9` | dashed |
| Foundation | `#ecfeff` | `#0e7490` | dashed |
| DevOps | `#ecfdf5` | `#047857` | dashed |

### Preferred: Individual Node Styling

**DO use `style` declarations with 200-level fills**:
```mermaid
flowchart TB
    A["🤖 Agent"]
    B["⚡ Apex"]

    A --> B

    style A fill:#fbcfe8,stroke:#be185d,color:#1f2937
    style B fill:#ddd6fe,stroke:#6d28d9,color:#1f2937
```

**Note**: Use `%%{init}` for spacing/curve config only. Avoid using it for color theming (use individual `style` declarations instead).

### Subgraph Styling

Use 50-level backgrounds with dark dashed borders. Use UPPERCASE for subgraph titles:
```mermaid
%%{init: {"flowchart": {"nodeSpacing": 80, "rankSpacing": 70}} }%%
flowchart TB
    subgraph ai["🤖 AI & AGENTS"]
        A[Agent]
    end

    style ai fill:#fdf2f8,stroke:#be185d,stroke-dasharray:5
```

### Node Label Pattern

Keep labels short (icon + name only). Avoid `<br/>` and `<small>` tags:
```
["🔐 sf-connected-apps"]
```

**Full reference**: See `docs/color-palette.md`

---

## Scoring Thresholds

| Rating | Score | Meaning |
|--------|-------|---------|
| ⭐⭐⭐⭐⭐ Excellent | 72-80 | Production-ready, comprehensive, well-styled |
| ⭐⭐⭐⭐ Very Good | 60-71 | Complete with minor improvements possible |
| ⭐⭐⭐ Good | 48-59 | Functional but could be clearer |
| ⭐⭐ Needs Work | 35-47 | Missing key elements or unclear |
| ⭐ Critical Issues | <35 | Inaccurate or incomplete |

---

## OAuth Flow Quick Reference

| Flow | Use Case | Key Detail | Template |
|------|----------|------------|----------|
| **Authorization Code** | Web apps with backend | User → Browser → App → SF | `oauth/authorization-code.md` |
| **Auth Code + PKCE** | Mobile, SPAs, public clients | code_verifier + SHA256 challenge | `oauth/authorization-code-pkce.md` |
| **JWT Bearer** | Server-to-server, CI/CD | Sign JWT with private key | `oauth/jwt-bearer.md` |
| **Client Credentials** | Service accounts, background | No user context | `oauth/client-credentials.md` |
| **Device Authorization** | CLI, IoT, Smart TVs | Poll for token after user auth | `oauth/device-authorization.md` |
| **Refresh Token** | Extend access | Reuse existing tokens | `oauth/refresh-token.md` |

Templates in `templates/oauth/`.

---

## ERD Notation Reference

### Cardinality Symbols (Crow's Foot)
```
||--||  One-to-One
||--o{  One-to-Many
}o--||  Many-to-One
}o--o{  Many-to-Many
```

### Field Annotations
```
PK  Primary Key (Id)
FK  Foreign Key (Lookup/MasterDetail)
UK  Unique Key (External Id)
```

### Salesforce Field Type Mapping
| SF Type | ERD Type | Notes |
|---------|----------|-------|
| Id | Id | 18-character Salesforce ID |
| Text | Text/String | Text fields, Names |
| Number | Number/Decimal | Currency, Percent, Number |
| Checkbox | Boolean | True/False |
| Date/DateTime | Date/DateTime | Date fields |
| Lookup | FK | Foreign key reference |
| MasterDetail | FK | Foreign key with cascade delete |
| Picklist | Picklist/Enum | Restricted values |

---

## Best Practices

### Sequence Diagrams
- Use `autonumber` for OAuth flows (step tracking)
- Use `->>` for requests, `-->>` for responses
- Use `activate`/`deactivate` for long-running processes
- Group related actors with `box` blocks
- Add `Note over` for protocol details (tokens, codes)

### ERD Diagrams
- Include all PK and FK annotations
- Show required fields with "(Required)" note
- Group related objects visually
- Use consistent naming (API names, not labels)

### Integration Diagrams
- Show error paths with `alt`/`else` blocks
- Include timeout handling for external calls
- Mark async calls with `-)` notation
- Add system icons for clarity (☁️ 🔄 🏭 💾)

### ASCII Diagrams
- Keep width ≤80 characters
- Use consistent box sizes
- Align arrows clearly
- Add step numbers for sequences

---

## Cross-Skill Integration

| Skill | When to Use | Example |
|-------|-------------|---------|
| sf-metadata | Get real object/field definitions for ERD | `Skill(skill="sf-metadata")` → "Describe Lead object" |
| sf-connected-apps | Link OAuth flow to Connected App setup | "Generate JWT Bearer diagram for this Connected App" |
| sf-ai-agentforce | Visualize Agentforce agent architecture | "Create flow diagram for FAQ Agent" |
| sf-flow | Document Flow logic as flowchart | "Diagram the approval process flow" |

## Dependencies

**Optional**: sf-metadata (for ERD auto-discovery)

---

## Example Usage

### 1. OAuth Flow Request
```
User: "Create a JWT Bearer OAuth flow diagram"

You should:
1. Load templates/oauth/jwt-bearer.md
2. Generate Mermaid sequenceDiagram
3. Generate ASCII fallback
4. Score and deliver
```

### 2. Data Model Request
```
User: "Create an ERD for Account, Contact, Opportunity, and Case"

You should:
1. If org connected: Query sf-metadata for field details
2. Load templates/datamodel/salesforce-erd.md
3. Generate Mermaid erDiagram with relationships
4. Generate ASCII fallback
5. Score and deliver
```

### 3. Integration Diagram Request
```
User: "Diagram our Salesforce to SAP integration flow"

You should:
1. Ask clarifying questions (sync/async, trigger, protocol)
2. Load templates/integration/api-sequence.md
3. Generate Mermaid sequenceDiagram
4. Generate ASCII fallback
5. Score and deliver
```

---

## Notes

- **Mermaid Rendering**: Works in GitHub, VS Code, Notion, Confluence, and most modern tools
- **ASCII Purpose**: Terminal compatibility, documentation that needs plain text
- **Color Accessibility**: Palette designed for color-blind accessibility
- **Template Customization**: Templates are starting points; customize per requirements

---

## License

MIT License. See [LICENSE](LICENSE) file.
Copyright (c) 2024-2025 Jag Valaiyapathy
