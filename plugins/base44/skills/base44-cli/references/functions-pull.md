# base44 functions pull

Pull deployed functions from Base44 to local files.

## Syntax

```bash
npx base44 functions pull [name]
```

## Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `[name]` | Function name to pull (pulls all if omitted) | No |

## Authentication

**Required**: Yes. If not authenticated, you'll be prompted to login first.

## What It Does

1. Fetches deployed functions from Base44
2. Filters to the specified function if `[name]` is provided
3. Writes function files to the local `functions/` directory (configured in `base44/config.jsonc`)
4. Reports each file as `written` (new/updated) or `unchanged`

## Examples

```bash
# Pull all deployed functions
npx base44 functions pull

# Pull a specific function
npx base44 functions pull process-order
```

## Output

```bash
$ npx base44 functions pull
✓ Functions fetched successfully
✓ Function files written successfully
✓ process-order              written
◆ send-notification          unchanged

✓ Pulled 2 functions to base44/functions
```

Single function:
```bash
$ npx base44 functions pull process-order
✓ Functions fetched successfully
✓ Function files written successfully
✓ process-order              written

✓ Pulled 1 function to base44/functions
```

## Error Handling

If the specified function is not found on remote:
```bash
$ npx base44 functions pull nonexistent
✓ Function "nonexistent" not found on remote
```

If no functions exist on remote:
```bash
$ npx base44 functions pull
✓ No functions found on remote
```

## Notes

- Files are written to the `functionsDir` configured in `base44/config.jsonc` (defaults to `functions/`)
- Files already matching remote content are skipped (reported as `unchanged`)
- This overwrites existing local function files with remote versions — commit local changes first
- Use `npx base44 functions deploy` to push local changes back to Base44
- Use `npx base44 functions list` to see what functions are deployed on remote
