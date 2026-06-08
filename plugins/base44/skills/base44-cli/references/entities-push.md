# base44 entities push

Push local entity definitions to Base44.

## Syntax

```bash
npx base44 entities push
```

## Authentication

**Required**: Yes. If not authenticated, you'll be prompted to login first.

## What It Does

1. Pushes all entities that exist in the `base44/entities` folder
2. Validates that entities exist in the folder
3. Displays the count of entities to be pushed
4. Uploads entities to the Base44 backend
5. Reports the results: created, updated, and deleted entities

## Prerequisites

- Must be run from a Base44 project directory
- Project must have entity definitions in the `base44/entities` folder

## Output

```bash
$ npx base44 entities push

Found 3 entities to push
Pushing entities to Base44...

Created: User, Post
Updated: Comment
Deleted: OldEntity

✓ Entities pushed successfully
```

## Entity Synchronization

The push operation synchronizes your local entity schema with Base44:

- **Created**: New entities that didn't exist in Base44
- **Updated**: Existing entities with modified schema or configuration
- **Deleted**: Entities that were removed from your local configuration

## Error Handling

If no entities are found in your project:
```bash
$ npx base44 entities push
No entities found in project
```

## Use Cases

- After defining new entities in your project
- When modifying existing entity schemas
- To sync entity changes before deploying
- As part of your development workflow when data models change

## Notes

- This command syncs the entity schema/structure, not the actual data
- Changes are applied to your Base44 project immediately
- Make sure to test entity changes in a development environment first
- Entity definitions are located in the `base44/entities/` directory
