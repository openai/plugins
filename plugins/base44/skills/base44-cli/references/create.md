# base44 create

Creates a new Base44 project from a template. This command is framework-agnostic and can either scaffold a complete project or add Base44 configuration to an existing project.

## Critical: Non-Interactive Mode Required

ALWAYS provide both the project name AND `--path` flag. Without both, the command opens an interactive TUI which agents cannot use properly.

WRONG: `npx base44 create`
WRONG: `npx base44 create my-app`
RIGHT: `npx base44 create my-app -p ./my-app`

## Syntax

```bash
npx base44 create [name] --path <path> [options]
```

## Arguments & Options

| Argument/Option | Description | Required |
|--------|-------------|----------|
| `name` | Project name (positional argument) | Yes* |
| `-p, --path <path>` | Path where to create the project | Yes* |
| `-t, --template <id>` | Template ID (see templates below) | No |
| `--deploy` | Build and deploy the site (includes pushing entities) | No |
| `--no-skills` | Skip AI agent skills installation (skills are added by default) | No |

*Required for non-interactive mode. Both `name` and `--path` must be provided together.

## Template Selection (CRITICAL - Choose Appropriately)

**You MUST select the most appropriate template based on user requirements:**

| Template ID | When to Use | Example Scenarios |
|-------------|-------------|-------------------|
| `backend-and-client` | Creating a NEW full-stack web app from scratch | "Create a task app", "Build me a dashboard", "Make a SaaS app" |
| `backend-only` | Adding Base44 to an EXISTING project OR using a different framework (Next.js, Vue, Svelte, etc.) | "Add Base44 to my project", "I want to use Next.js", "I already have a frontend" |

**Default Choice:** When the user asks to "create an app" or "build a project" without specifying a particular framework, use `backend-and-client` to provide a complete, production-ready application with Vite + React + Tailwind.

## The `--path` Flag

- **For `backend-and-client` template (new projects):** Use a new subfolder path
  ```bash
  npx base44 create my-app -p ./my-app -t backend-and-client
  ```
- **For `backend-only` template (existing projects):** Use `-p .` in the current directory
  ```bash
  npx base44 create my-app -p .
  ```

## Workflow: Using `backend-only` with External Frameworks

**CRITICAL: The project folder MUST exist BEFORE running `base44 create` with `backend-only`**

The `backend-only` template only adds Base44 configuration files - it does NOT create a frontend. If you need a frontend with a specific framework:

```bash
# Step 1: Initialize the frontend project FIRST
npm create vite@latest my-app -- --template react  # or vue, svelte, etc.
# OR: npx create-next-app@latest my-app
# OR: any other framework's init command

# Step 2: Navigate into the created folder
cd my-app

# Step 3: Install Base44 CLI
npm install --save-dev base44

# Step 4: Add Base44 configuration
npx base44 create my-app -p .
```

**WARNING:** Do NOT:
- Create an empty folder manually, then try to run `npx create vite` inside it (will fail - folder exists)
- Run `base44 create` with `backend-only` expecting it to create a frontend (it won't)

**DO:**
- Run the external framework's init command FIRST (it creates its own folder)
- Then run `base44 create` inside that folder with `-p .`

## Examples

```bash
# RECOMMENDED: Create full-stack project (for new apps)
npx base44 create my-app -p ./my-app -t backend-and-client

# Create full-stack and deploy in one step
npx base44 create my-app -p ./my-app -t backend-and-client --deploy

# Add Base44 to EXISTING project (must be inside the project folder)
npx base44 create my-app -p .

# Add Base44 to existing project and deploy
npx base44 create my-app -p . --deploy

# Create without adding AI agent skills
npx base44 create my-app -p . --no-skills
```

## What It Does

1. Applies the selected template to the target path
2. Creates a `base44/` folder with configuration files
3. Registers the project with Base44 backend
4. Creates `base44/.app.jsonc` with the app ID
5. If `--deploy` is used:
   - Pushes any entities defined in `base44/entities/`
   - Runs install and build commands (for templates with frontend)
   - Deploys the site to Base44 hosting
