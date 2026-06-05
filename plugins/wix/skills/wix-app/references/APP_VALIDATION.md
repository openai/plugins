
# Wix App Validation

Validates Wix CLI applications through a four-step sequential workflow: package installation, TypeScript compilation check, build, and preview.

## Validation Workflow

Execute these steps sequentially. Stop and report errors if any step fails.

### Step 1: Package Installation

Ensure all dependencies are installed before proceeding with the build.

**Detect package manager:**
- Check for `package-lock.json` → use `npm`
- Check for `yarn.lock` → use `yarn`
- Check for `pnpm-lock.yaml` → use `pnpm`
- Default to `npm` if no lock file is found

**Run installation command:**

```bash
# For npm
npm install

# For yarn
yarn install

# For pnpm
pnpm install
```

**Success criteria:**
- Exit code 0
- All dependencies installed successfully
- No missing peer dependencies warnings (unless expected)
- `node_modules` directory exists and contains expected packages

**On failure:** Report the installation errors, [check the debug log](#debug-log-on-errors) for detailed diagnostics, and stop validation. Common issues:
- Network connectivity problems
- Corrupted lock files
- Version conflicts
- Missing Node.js or package manager

### Step 2: TypeScript Compilation Check

Run TypeScript compiler to check for type errors.

**Full project check:**
```bash
npx tsc --noEmit
```

**Targeted check (specific files/directories):**

When validating after implementing a specific extension, you can run TypeScript checks on just those files:

```bash
# Check specific directory
npx tsc --noEmit src/extensions/dashboard/pages/survey/**/*.ts src/extensions/dashboard/pages/survey/**/*.tsx

# Check dashboard pages only
npx tsc --noEmit src/extensions/dashboard/pages/**/*.ts src/extensions/dashboard/pages/**/*.tsx

# Check custom element widgets only
npx tsc --noEmit src/extensions/site/widgets/**/*.ts src/extensions/site/widgets/**/*.tsx

# Check dashboard modals only
npx tsc --noEmit src/extensions/dashboard/modals/**/*.ts src/extensions/dashboard/modals/**/*.tsx

# Check backend only
npx tsc --noEmit src/extensions/backend/**/*.ts
```

**When to use targeted checks:**
- After implementing a single extension (faster feedback)
- When debugging type errors in a specific area
- During iterative development

**When to use full project check:**
- Before final validation
- When changes affect shared types
- Before building/deploying

**Success criteria:**
- Exit code 0
- No TypeScript compilation errors
- All type checks pass

**On failure:** Report the specific TypeScript errors and stop validation. Common issues:
- Type mismatches between expected and actual types
- Missing type declarations for imported modules
- Incorrect generic type parameters
- Properties not existing on declared types
- Incompatible function signatures

### Step 3: Build Validation

Run the build command and check for compilation errors:

```bash
npx wix build
```

**Success criteria:**
- Exit code 0
- No TypeScript errors
- No missing dependencies

**On failure:** Report the specific compilation errors, [check the debug log](#debug-log-on-errors) for detailed diagnostics, and stop validation.

### Step 4: Preview Deployment

Start the preview server:

```bash
npx wix preview
```

**Success criteria:**
- Preview server starts successfully
- Preview URLs are generated (both site and dashboard)

**URL extraction:** Parse the terminal output to find both preview URLs. Look for patterns like:
- Site preview: `Site preview: https://...` or `Site URL: https://...`
- Dashboard preview: `Dashboard preview: https://...` or `Preview URL: https://...` or `Your app is available at: https://...`

Extract both URLs and provide them to the user for manual verification.

**On failure:** Report the preview startup errors, [check the debug log](#debug-log-on-errors) for detailed diagnostics, and stop validation.

## Validation Report

After completing all steps, provide a summary:

**Pass:**
- Dependencies: ✓ All packages installed successfully
- TypeScript: ✓ No compilation errors
- Build: ✓ Compiled successfully
- Preview: ✓ Running at [URL]

**Fail:**
- Identify which step failed
- Provide specific error messages
- Suggest remediation steps

## Debug Log on Errors

When a validation step fails (non-zero exit code, error output, or the CLI crashes/hangs), check `.wix/debug.log` in the project root for the full error trace. **Only read this file when errors occur** — skip it when steps pass or when the terminal output already makes the error clear (e.g. a straightforward TypeScript type error).

The `.wix/` directory is automatically created by the Wix CLI and contains internal configuration and log files. Don't edit it, but reading `debug.log` for troubleshooting is expected.

```
Read: .wix/debug.log

# If the file is large, read the last 100 lines for the most recent errors
Read: .wix/debug.log (with offset to the end)
```

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Package installation fails | Missing lock file, network issues, or corrupted node_modules | Delete `node_modules` and lock file, then reinstall |
| TypeScript compilation fails | Type mismatches, missing declarations, or incorrect types | Fix TypeScript errors shown in `npx tsc --noEmit` output |
| Build fails | TypeScript errors, missing dependencies, or internal CLI error | Fix TypeScript errors in source; for non-obvious failures, check `.wix/debug.log` |
| Preview fails to start | Port conflict, config issue, or internal CLI error | Check `wix.config.json`; if unclear, check `.wix/debug.log` for details |
| Console errors in preview | Runtime exceptions | Check browser console output |
| UI not rendering | Component errors | Review component code and imports |
| CLI error with no clear message | Truncated terminal output | Read `.wix/debug.log` for the full error trace and stack details |
| Mysterious failures after config change | Stale CLI state | Read `.wix/debug.log` to confirm, then delete `.wix/` and rebuild |
