# Creating Entities

Base44 entities are defined locally in your project and then pushed to the Base44 backend.

## Critical: File Naming

Entity files MUST use kebab-case naming: `{kebab-case-name}.jsonc`

| Entity Name | File Name |
|-------------|-----------|
| `Task` | `task.jsonc` |
| `TeamMember` | `team-member.jsonc` |
| `ActivityLog` | `activity-log.jsonc` |

WRONG: `TeamMember.jsonc`, `teamMember.jsonc`
RIGHT: `team-member.jsonc`

## Table of Contents

- [Creating Entities](#creating-entities)
  - [Entity Directory](#entity-directory)
  - [How to Create an Entity](#how-to-create-an-entity)
  - [Entity Schema Structure](#entity-schema-structure)
  - [Supported Field Types](#supported-field-types)
  - [Field Properties](#field-properties)
  - [Complete Example](#complete-example)
  - [Naming Conventions](#naming-conventions)
  - [Relationships Between Entities](#relationships-between-entities)
  - [Row Level Security (RLS)](#row-level-security-rls)
  - [Field Level Security (FLS)](#field-level-security-fls)
  - [Pushing Entities](#pushing-entities)

## Entity Directory

All entity definitions must be placed in the `base44/entities/` folder in your project root. Each entity is defined in its own `.jsonc` file.

Example structure:
```
my-app/
  base44/
    entities/
      user.jsonc
      product.jsonc
      order.jsonc
```

## How to Create an Entity

1. Create a new `.jsonc` file in the `base44/entities/` directory
2. Define your entity schema following the structure below
3. Push the changes to Base44 using the CLI

## Entity Schema Structure

Each entity file follows a JSON Schema-like structure:

```jsonc
{
  "name": "EntityName",       // PascalCase entity name
  "type": "object",           // Always "object"
  "properties": {
    // Define your fields here
  },
  "required": ["field1"]      // Array of required field names
}
```

### Common Mistake: Nested Schema Property

**WRONG** - Do NOT wrap properties in a `schema` object:
```jsonc
{
  "name": "Task",
  "description": "A task entity",
  "schema": {                    // ❌ WRONG - don't use nested "schema"
    "type": "object",
    "properties": { ... }
  }
}
```

**CORRECT** - Put `type` and `properties` at the top level:
```jsonc
{
  "name": "Task",
  "description": "A task entity",
  "type": "object",              // ✅ CORRECT - top level
  "properties": { ... }          // ✅ CORRECT - top level
}
```

This is a common mistake that will cause "Invalid schema: Schema must have a 'type' field" errors when pushing entities.

## Supported Field Types

### String

Basic text field:
```jsonc
{
  "title": {
    "type": "string",
    "description": "Task title"
  }
}
```

With format:
```jsonc
{
  "due_date": {
    "type": "string",
    "format": "date",
    "description": "Due date"
  }
}
```

Available formats: `date`, `date-time`, `time`, `email`, `uri`, `hostname`, `ipv4`, `ipv6`, `uuid`, `file`, `regex`, `richtext`

### String with Enum

Constrained to specific values:
```jsonc
{
  "status": {
    "type": "string",
    "enum": ["todo", "in_progress", "done"],
    "default": "todo",
    "description": "Current status"
  }
}
```

### Number

```jsonc
{
  "position": {
    "type": "number",
    "description": "Position for ordering"
  }
}
```

### Integer

For whole numbers only:
```jsonc
{
  "quantity": {
    "type": "integer",
    "description": "Item quantity",
    "minimum": 0,
    "maximum": 1000
  }
}
```

### Binary

For file/blob data:
```jsonc
{
  "attachment": {
    "type": "binary",
    "description": "File attachment"
  }
}
```

### Boolean

```jsonc
{
  "notify_on_change": {
    "type": "boolean",
    "default": true,
    "description": "Enable notifications"
  }
}
```

### Array of Strings

```jsonc
{
  "labels": {
    "type": "array",
    "items": { "type": "string" },
    "description": "Task labels/tags"
  }
}
```

### Array of Objects

```jsonc
{
  "attachments": {
    "type": "array",
    "description": "File attachments",
    "items": {
      "type": "object",
      "properties": {
        "name": { "type": "string" },
        "url": { "type": "string" },
        "type": { "type": "string" }
      }
    }
  }
}
```

## Field Properties

| Property      | Description                                                                              |
| ------------- | ---------------------------------------------------------------------------------------- |
| `type`        | Data type: `string`, `number`, `integer`, `boolean`, `array`, `object`, `binary`         |
| `description` | Human-readable description of the field                                                  |
| `enum`        | Array of allowed values (for strings)                                                    |
| `enumNames`   | Human-readable labels for enum values (same order as `enum`)                             |
| `default`     | Default value when not provided                                                          |
| `format`      | Format hint: `date`, `date-time`, `time`, `email`, `uri`, `hostname`, `ipv4`, `ipv6`, `uuid`, `file`, `regex`, `richtext` |
| `items`       | Schema for array items                                                                   |
| `properties`  | Nested properties for object types                                                       |
| `$ref`        | Reference to another schema definition                                                   |
| `minLength`   | Minimum string length                                                                    |
| `maxLength`   | Maximum string length                                                                    |
| `pattern`     | Regex pattern for string validation                                                      |
| `minimum`     | Minimum value for numbers                                                                |
| `maximum`     | Maximum value for numbers                                                                |
| `rls`         | Field-level security rules (see Field Level Security section)                            |

## Complete Example

Here's a complete entity definition for a Task:

```jsonc
{
  "name": "Task",
  "type": "object",
  "properties": {
    "title": {
      "type": "string",
      "description": "Task title"
    },
    "description": {
      "type": "string",
      "description": "Task description"
    },
    "status": {
      "type": "string",
      "enum": ["todo", "in_progress", "done"],
      "default": "todo",
      "description": "Current status of the task"
    },
    "board_id": {
      "type": "string",
      "description": "Board this task belongs to"
    },
    "assignee_email": {
      "type": "string",
      "description": "Email of assigned user"
    },
    "priority": {
      "type": "string",
      "enum": ["low", "medium", "high"],
      "default": "medium",
      "description": "Task priority"
    },
    "due_date": {
      "type": "string",
      "format": "date",
      "description": "Due date"
    },
    "labels": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Task labels/tags"
    }
  },
  "required": ["title"]
}
```

## Naming Conventions

- **Entity name**: Use PascalCase with alphanumeric characters only (e.g., `Task`, `TeamMember`, `ActivityLog`)
  - Must match pattern: `/^[a-zA-Z0-9]+$/`
  - Valid: `Task`, `TeamMember`, `Order123`
  - Invalid: `Team_Member`, `Team-Member`, `Team Member`
- **File name**: Use kebab-case matching the entity (e.g., `task.jsonc`, `team-member.jsonc`, `activity-log.jsonc`)
- **Field names**: Use snake_case (e.g., `board_id`, `user_email`, `due_date`)

## Relationships Between Entities

To create relationships between entities, use ID reference fields:

```jsonc
{
  "board_id": {
    "type": "string",
    "description": "Board this task belongs to"
  },
  "team_id": {
    "type": "string",
    "description": "Associated team ID"
  }
}
```

## Row Level Security (RLS)

Row Level Security (RLS) controls which records users can access based on their identity and attributes. RLS rules are defined per entity inside the `rls` field of the schema.

**Important:** If no RLS is defined, all records are accessible to all users.

### RLS Operations

RLS supports five operations:

| Operation | Description |
|-----------|-------------|
| `create` | Control who can add new records |
| `read` | Control who can view records |
| `update` | Control who can modify records |
| `delete` | Control who can remove records |
| `write` | Shorthand for `create`, `update`, and `delete` combined |

### Permission Values

Each operation accepts one of the following values:

1. **`true`** - Allow all users (including anonymous/unauthenticated)
2. **`false`** - Block all users
3. **Condition object** - Allow users matching the condition

### Template Variables

Use template variables to reference the current user's attributes:

| Template | Description |
|----------|-------------|
| `{{user.id}}` | The user's ID |
| `{{user.email}}` | The user's email |
| `{{user.role}}` | The user's role |
| `{{user.data.field_name}}` | Custom field from the user's `data` object |

### Built-in Entity Attributes

Every entity record has these built-in attributes available for RLS rules:

| Attribute | Description |
|-----------|-------------|
| `id` | Unique record identifier |
| `created_date` | Timestamp when record was created |
| `updated_date` | Timestamp when record was last updated |
| `created_by` | Email of the user who created the record |

### Rule Types

There are two condition types you can use:

**1. Entity-to-user comparison** - Compare record fields to the current user's values:
```jsonc
{
  "created_by": "{{user.email}}"
}
```

**2. User condition check** - Check user properties directly using `user_condition`:
```jsonc
{
  "user_condition": { "role": "admin" }
}
```

**Important notes:**
- `user_condition` only supports **simple equality** (e.g., `{ "role": "admin" }`)
- **Entity field filtering requires `data.` prefix:** Use `{ "data.fieldname": value }` to filter by entity field values
- For `data.*` field comparisons, you can use operators: `$in`, `$nin`, `$ne`, `$all`
- Logical operators `$or`, `$and`, `$nor` are available for combining conditions

⚠️ **For advanced RLS patterns and examples, see [rls-examples.md](rls-examples.md)**

### RLS Examples

**Owner-only access:**
```jsonc
{
  "created_by": "{{user.email}}"
}
```

**Department-based access:**
```jsonc
{
  "data.department": "{{user.data.department}}"
}
```

**Admin-only access:**
```jsonc
{
  "user_condition": { "role": "admin" }
}
```

**Complete RLS configuration:**
```jsonc
{
  "name": "Task",
  "type": "object",
  "properties": {
    "title": {
      "type": "string",
      "description": "Task title"
    },
    "status": {
      "type": "string",
      "enum": ["todo", "in_progress", "done"],
      "default": "todo"
    }
  },
  "required": ["title"],
  "rls": {
    "create": true,
    "read": { "created_by": "{{user.email}}" },
    "update": { "created_by": "{{user.email}}" },
    "delete": { "created_by": "{{user.email}}" }
  }
}
```

### Common RLS Patterns

**Public create, admin-only management (e.g., contact forms, waitlists):**
```jsonc
{
  "rls": {
    "create": true,
    "read": { "user_condition": { "role": "admin" } },
    "update": { "user_condition": { "role": "admin" } },
    "delete": { "user_condition": { "role": "admin" } }
  }
}
```

**Owner-only access:**
```jsonc
{
  "rls": {
    "create": true,
    "read": { "created_by": "{{user.email}}" },
    "update": { "created_by": "{{user.email}}" },
    "delete": { "created_by": "{{user.email}}" }
  }
}
```

**Logged-in users only:**
```jsonc
{
  "rls": {
    "create": { "user_condition": { "id": "{{user.id}}" } },
    "read": true,
    "update": { "created_by": "{{user.email}}" },
    "delete": { "created_by": "{{user.email}}" }
  }
}
```

### Limitations

- **user_condition is equality only:** `user_condition` only supports exact match (e.g., `{ "role": "admin" }`) - no operators
- **No comparison operators on user_condition:** `$gt`, `$lt`, `$regex`, `$expr`, `$where` are NOT supported for user conditions
- **No deeply nested templates:** Templates like `{{user.data.profile.department}}` may not work

**Supported operators:**
- **Logical operators:** `$or`, `$and`, `$nor` for combining multiple conditions
- **Field operators (for `data.*` fields only):** `$in`, `$nin`, `$ne`, `$all`
- **Entity field filtering:** Use `data.` prefix to filter by entity field values (e.g., `{ "data.status": "published" }` or `{ "data.completed": true }`)

⚠️ **See [rls-examples.md](rls-examples.md) for comprehensive RLS patterns and examples**

### Complex Access Patterns

For complex access patterns that require multiple conditions (e.g., "owner OR admin"), you have two options:

1. **Use the Base44 Dashboard UI** - The dashboard allows adding multiple rules per operation with OR logic
2. **Use separate entities** - Split data into multiple entities with different access rules
3. **Use backend functions** - Implement custom access logic in backend functions

## Field Level Security (FLS)

Field Level Security allows you to control access to individual fields within an entity. FLS rules are defined within each field's schema using the `rls` property.

### FLS Operations

FLS supports the same operations as entity-level RLS:

| Operation | Description |
|-----------|-------------|
| `create` | Control who can set this field when creating records |
| `read` | Control who can view this field |
| `update` | Control who can modify this field |
| `delete` | Control who can clear this field |
| `write` | Shorthand for `create`, `update`, and `delete` combined |

### FLS Example

```jsonc
{
  "name": "Employee",
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "description": "Employee name"
    },
    "salary": {
      "type": "number",
      "description": "Employee salary",
      "rls": {
        "read": { "user_condition": { "role": "hr" } },
        "update": { "user_condition": { "role": "hr" } }
      }
    },
    "department": {
      "type": "string",
      "description": "Department name"
    }
  },
  "required": ["name"]
}
```

In this example, only users with the `hr` role can read or update the `salary` field. All users with access to the entity can read/update other fields.

### FLS Notes

- If no field-level RLS is defined, the field inherits the entity-level RLS rules
- FLS rules follow the same condition format as entity-level RLS
- Use FLS for sensitive fields like salary, SSN, or internal notes

## Pushing Entities

The `entities push` command will push all entities that exist in the `base44/entities` folder.

```bash
npx base44 entities push
```

For more details on the push command, see [entities-push.md](entities-push.md).
