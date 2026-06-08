# base44 agents push

Push local AI agent configurations to Base44. Agents are conversational AI assistants that can interact with users, access your app's entities, and call backend functions.

## Syntax

```bash
npx base44 agents push
```

## Authentication

**Required**: Yes. If not authenticated, you'll be prompted to login first.

## What It Does

1. Reads all agent files from the `base44/agents/` directory
2. Validates agent configurations
3. Displays the count of agents to be pushed
4. Uploads agents to the Base44 backend
5. Reports the results: created, updated, and deleted agents

## Prerequisites

- Must be run from a Base44 project directory
- Project must have agent definitions in the `base44/agents/` folder

## Output

```bash
$ npx base44 agents push

Found 2 agents to push
Pushing agents to Base44...

Created: support_agent
Updated: order_bot
Deleted: old_agent

✓ Agents pushed to Base44
```

## Agent Synchronization

The push operation synchronizes your local agents with Base44:

- **Created**: New agents that didn't exist in Base44
- **Updated**: Existing agents with modified configuration
- **Deleted**: Agents that were removed from your local configuration

**Warning**: This is a full sync operation. Agents removed locally will be deleted from Base44.

## Error Handling

If no agents are found in your project:
```bash
$ npx base44 agents push
No local agents found - this will delete all remote agents
```

If an agent has an invalid name:
```bash
$ npx base44 agents push
Error: Agent name must be lowercase alphanumeric with underscores
```

## Agent Configuration Schema

Each agent file should be a `.jsonc` file in `base44/agents/` with this structure:

```jsonc
{
  "name": "agent_name",              // Required: lowercase alphanumeric with underscores, 1-100 chars
  "description": "Brief description of what this agent does",  // Required: min 1 char
  "instructions": "Detailed instructions for the agent's behavior",  // Required: min 1 char
  "tool_configs": [                  // Optional: defaults to []
    // Entity tool - gives agent access to entity operations
    { "entity_name": "Task", "allowed_operations": ["read", "create", "update", "delete"] },
    // Backend function tool - gives agent access to a function
    { "function_name": "send_email", "description": "Send an email notification" }
  ],
  "whatsapp_greeting": "Hello! How can I help you today?"  // Optional
}
```

**Naming rules:**
- **Agent names** must match pattern: `/^[a-z0-9_]+$/` (lowercase alphanumeric with underscores only, 1-100 characters)
  - Valid: `support_agent`, `order_bot`, `task_helper`
  - Invalid: `Support-Agent`, `OrderBot`, `task helper`
- **Agent file names** must use underscores (matching the agent name)
  - Valid: `support_agent.jsonc`, `order_bot.jsonc`
  - Invalid: `support-agent.jsonc` (hyphens not allowed)
- **Entity names in `tool_configs`** must use PascalCase (matching the entity's `name` field)
  - Valid: `"entity_name": "Task"`, `"entity_name": "TeamMember"`
  - Invalid: `"entity_name": "task"`, `"entity_name": "team_member"`

**Required fields:**
- `name`: Required, must follow naming rules above
- `description`: Required, minimum 1 character
- `instructions`: Required, minimum 1 character
- `tool_configs`: Optional, defaults to empty array
- `whatsapp_greeting`: Optional

### Common Mistake: Wrong tool_configs Format

**WRONG** - Do NOT use `tools` with `type` and `entity`:
```jsonc
{
  "name": "my_agent",
  "tools": [                                    // ❌ WRONG
    { "type": "entity_query", "entity": "Task" }
  ]
}
```

**CORRECT** - Use `tool_configs` with `entity_name` and `allowed_operations`:
```jsonc
{
  "name": "my_agent",
  "tool_configs": [                             // ✅ CORRECT
    { "entity_name": "Task", "allowed_operations": ["read"] }
  ]
}
```

### Best Practices for Agent Instructions

When giving agents access to entities, be explicit in the instructions about using the tools:

```jsonc
{
  "name": "support_agent",
  "instructions": "You are a helpful support agent.\n\nIMPORTANT: You have access to customer data through entity tools. When users ask about their orders or account:\n1. ALWAYS use the Order entity tool to query their order history\n2. Use the Customer entity tool to look up account details\n3. Analyze the data and provide personalized responses\n\nAlways query the relevant entities first before answering questions about user data.",
  "tool_configs": [
    { "entity_name": "Order", "allowed_operations": ["read"] },
    { "entity_name": "Customer", "allowed_operations": ["read"] }
  ]
}
```

Without explicit instructions to use the entity tools, the agent may not proactively query user data when asked.

## Use Cases

- After defining new agents in your project
- When modifying existing agent configurations
- To sync agent changes before testing
- As part of your development workflow when agent behavior changes

## Notes

- This command syncs the agent configuration, not conversation data
- Changes are applied to your Base44 project immediately
- Make sure to test agent changes in a development environment first
- Agent definitions are located in the `base44/agents/` directory
- Use `base44 agents pull` to download agents from Base44
