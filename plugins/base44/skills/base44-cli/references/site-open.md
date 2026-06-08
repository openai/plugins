# base44 site open

Opens the published site in your default web browser.

## Syntax

```bash
npx base44 site open
```

## Authentication

**Required**: Yes. If not authenticated, you'll be prompted to login first.

## What It Does

1. Fetches the site URL from Base44
2. Opens the site in your default browser
3. Displays the site URL in the terminal

## Example

```bash
$ npx base44 site open

Site opened at https://my-app.base44.app
```

## Requirements

- Must be run from a linked Base44 project directory
- Must be authenticated (run `npx base44 login` first)
- Site must have been deployed at least once

## Notes

- The command will not open a browser in CI environments (when `process.env.CI` is set)
- Use this command to quickly view your deployed site
- The site URL is also displayed after deploying with `base44 site deploy` or `base44 deploy`
