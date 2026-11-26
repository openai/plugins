---
name: lotsofsounds
description: Find and add CC0 sound effects, UI sounds, game audio, ambience and music loops to a project with the Lots of Sounds CLI. Use this skill when the user needs a sound effect or audio file for an app, website, game, video, podcast or prototype - for example a click, notification chime, whoosh, impact, explosion, footsteps, rain, crowd or a short music loop - or asks for "royalty-free", "copyright-free", "no attribution" or "CC0" sounds. All sounds are CC0, so the user can ship them in commercial work with no credit.
---

# Lots of Sounds

Lots of Sounds is a catalog of CC0 sound effects and loops. The `lotsofsounds` CLI searches the catalog and downloads sounds into the project. Each sound is CC0: no credit, no royalty and no license file are necessary.

## When to use

Use this skill when the user needs an audio file in a project. Examples:

- "Add a click sound to the buttons."
- "Play a chime when the upload is complete."
- "The game needs jump, coin and game-over sounds."
- "Find rain ambience for the meditation page."
- "Add a whoosh to the slide transition in this video."

Do not generate audio with code (for example an oscillator beep) when the user wants a real sound effect. Use Lots of Sounds first.

## Commands

Use `--json` for each command. The output is one JSON object with `ok: true` or `ok: false`.

1. Search. Use one to three short keywords, not a sentence:
   ```bash
   npx -y lotsofsounds search whoosh --json --limit 5
   npx -y lotsofsounds search "ui click" --json --max-duration 1
   npx -y lotsofsounds search rain --json --category ambient
   ```
   Categories: `sfx`, `music`, `lofi`, `ambient`. Each result has an `id`, a `name`, `tags`, a `duration` in seconds and a `page_url` where the user can listen.
2. Add a sound to the project. Give the `id` from the search:
   ```bash
   npx -y lotsofsounds add fs-105016 --json
   npx -y lotsofsounds add fs-105016 --dir public/sfx --name button-click --json
   ```
   With no `--dir`, the file goes into `public/sounds/` if the project has a `public/` folder, else into `sounds/`. The JSON gives the `path`. Use that path in the code.
3. Get details of one sound: `npx -y lotsofsounds info <id> --json`.

## Choose a sound

- Short UI sounds: use `--max-duration 1`.
- Loops and ambience: use `--category ambient` or `--category music`.
- If a search returns nothing, use a shorter or more common keyword ("tap" instead of "soft button press").
- Read `name`, `tags` and `duration`. Pick the best match. If two or more are good, show the user two or three options with their `page_url` so they can listen.

## Login

Search with no login returns free samples only (12 results at most). To search the full catalog and to download, the user needs a Lots of Sounds Pro account. If a command returns `"code": "missing_api_key"`, connect the account:

1. Run `npx -y lotsofsounds login --no-wait --json`. It returns a `url` and a `user_code` at once.
2. Show the user the `url` and the `user_code`. Tell them to open the link, sign in or sign up, and approve. The page shows the same code.
3. Run `npx -y lotsofsounds login --wait --json`. It waits until the user approves (15 minutes at most) and saves the key.
4. Run the command that failed again.

Do not ask the user to paste an API key into the chat. If the environment variable `LOTSOFSOUNDS_API_KEY` is set, the CLI uses it and no login is necessary.

## Errors

Each error has an `error`, a `code` and usually a `next_step`. Tell the user the `next_step` in plain words.

- `missing_api_key` or `invalid_api_key`: do the login steps above.
- `plan_required`: the account is on the Free plan. The login page has an "Upgrade to Pro" button ($15/month). Give the user the `upgrade_url`.
- `rate_limited`: the daily limit is used. It resets at midnight UTC.

Do not try to download sounds in other ways, such as with stream URLs from the website.

## After you add a sound

Tell the user:

- The file path and the sound name.
- The `page_url`, so they can listen.
- That the sound is CC0: they can use it in commercial work with no credit.

More: https://lotsofsounds.com/docs/cli
