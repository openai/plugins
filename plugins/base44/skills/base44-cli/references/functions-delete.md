# base44 functions delete

Delete one or more deployed functions from Base44.

## Syntax

```bash
npx base44 functions delete <names...>
```

## Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `<names...>` | One or more function names to delete (comma-separated values also accepted) | Yes |

## Authentication

**Required**: Yes. If not authenticated, you'll be prompted to login first.

## What It Does

1. Takes one or more function names as arguments
2. Deletes each function from Base44 remotely
3. Reports success, not-found, or error for each function

## Examples

```bash
# Delete a single function
npx base44 functions delete process-order

# Delete multiple functions (space-separated)
npx base44 functions delete process-order send-notification

# Delete multiple functions (comma-separated)
npx base44 functions delete process-order,send-notification
```

## Output

Single function:
```bash
$ npx base44 functions delete process-order
◇ Deleting process-order...
✓ process-order deleted

└ Function "process-order" deleted
```

Multiple functions:
```bash
$ npx base44 functions delete process-order send-notification
◇ Deleting process-order...
✓ process-order deleted
◇ Deleting send-notification...
✓ send-notification deleted

└ 2/2 deleted
```

## Error Handling

If a function is not found on remote:
```bash
$ npx base44 functions delete nonexistent
✓ Function "nonexistent" not found
```

If no names are provided:
```bash
$ npx base44 functions delete
error: At least one function name is required
```

## Notes

- This command deletes functions from Base44 (remote only); it does not remove local files
- To remove a function and clean up remote state, delete the local files then use `npx base44 functions deploy --force`
- Not-found functions are reported without raising an error (exit 0 for single-function case)
- Comma-separated names are supported: `delete func1,func2` is equivalent to `delete func1 func2`
