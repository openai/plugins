# base44 eject

Download the code for an existing Base44 project to your local machine.

## Syntax

```bash
npx base44 eject [options]
```

## Options

| Option | Description | Required |
|--------|-------------|----------|
| `-p, --path <path>` | Path where to write the project | No |
| `--project-id <id>` | Project ID to eject (skips interactive selection) | No |
| `-y, --yes` | Skip confirmation prompts | No |

## What It Does

The `eject` command allows you to download the source code of a Base44 project that was created or managed through the platform:

1. Lists all ejectable projects (projects with managed source code)
2. Lets you select a project interactively (or specify via `--project-id`)
3. Downloads the project code to a local directory
4. Creates a new project as a copy (named "{Original Name} Copy")
5. Links the downloaded code to the new project
6. Creates `.env.local` with the new project ID
7. Optionally installs dependencies, builds, and deploys the project

## Examples

```bash
# Interactive mode - select project from list and specify path
npx base44 eject

# Specify the output path
npx base44 eject -p ./my-project

# Non-interactive - specify project ID and skip confirmations
npx base44 eject --project-id abc123 -p ./my-project -y
```

## Workflow

When you run `eject`:

1. **Project Selection**: Choose from available ejectable projects
2. **Path Selection**: Specify where to create the project (defaults to `./{project-name}` or `./` if current directory is empty)
3. **Download**: The project code is downloaded to the specified path
4. **New Project Creation**: A copy of the project is created in Base44 (e.g., "My App Copy")
5. **Linking**: The local code is linked to the new project
6. **Optional Deployment**: If the project has build commands configured, you'll be asked if you want to deploy
   - Runs the install command (e.g., `npm install`)
   - Runs the build command (e.g., `npm run build`)
   - Deploys all resources with `base44 deploy`

## Requirements

- Must be authenticated (run `npx base44 login` first)
- The project must be ejectable (have managed source code)

## Use Cases

- Download a project created through the Base44 dashboard
- Clone a managed project for local development
- Create a copy of an existing project to customize

## Notes

- The command creates a **new project** as a copy, preserving the original
- The new project will be named "{Original Name} Copy"
- The downloaded code is automatically linked to the new project
- If the current directory is empty, the default path is `./`
- If the current directory has files, the default path is `./{kebab-case-project-name}`
- Only projects with `isManagedSourceCode !== false` can be ejected
- If no ejectable projects exist, the command exits with "No projects available to eject."

## Related Commands

| Command | Description |
|---------|-------------|
| `base44 create` | Create a new Base44 project from a template |
| `base44 link` | Link an existing directory to a Base44 project |
| `base44 deploy` | Deploy all project resources |
