---
name: twilio-cli-reference
description: >
  Twilio CLI reference for managing Twilio resources from the terminal.
  Covers installation, credential profiles, phone number provisioning,
  sending SMS and email, webhook configuration, local development with
  a tunneling service, debugging with watch and logs, serverless deployment, and
  plugin ecosystem. Use when the developer asks to "just do it",
  "set this up", "run a command", mentions "CLI", "command line", or
  "terminal", or when an AI agent can execute a task directly instead
  of writing application code.
---

## Overview

The Twilio CLI lets you manage Twilio resources, send messages, configure webhooks, and deploy serverless functions directly from the terminal. AI coding agents can use CLI commands to provision resources and test integrations without writing application code.

**Install:**

| Platform | Command |
|----------|---------|
| macOS | `brew tap twilio/brew && brew install twilio` |
| Windows | `scoop bucket add twilio-scoop https://github.com/twilio/scoop-twilio-cli && scoop install twilio-cli` |
| Linux (apt) | See `twilio-cli/getting-started/install` for repo setup, then `apt install twilio` |
| npm | `npm install -g twilio-cli` |

**Update:** `brew upgrade twilio` / `scoop update twilio-cli` / `npm install -g twilio-cli@latest`

---

## Authentication & Profiles

```bash
# First-time login — creates a local API key stored as a profile
twilio login

# Named profiles for multiple accounts
twilio profiles:create --account-sid ACxxx --auth-token xxx --profile staging
# Avoid --auth-token as a plain argument — it will be stored in shell history. Use TWILIO_AUTH_TOKEN env var instead.
twilio profiles:list
twilio profiles:use staging

# Run a single command against a different profile
twilio api:core:messages:list -p production

# Subaccount access
twilio api:core:messages:list --account-sid ACxxx_SUBACCOUNT
```

**Credential priority:** explicit `-p`/`--account-sid` flag > env vars (`TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`) > active profile.

---

## Phone Numbers

```bash
# Search available numbers (US local, area code 415)
twilio api:core:available-phone-numbers:local:list --country-code US --area-code 415

# Purchase a number
twilio api:core:incoming-phone-numbers:create --phone-number "+14155551234"

# List owned numbers
twilio phone-numbers:list

# Set webhooks on a number
twilio phone-numbers:update +14155551234 \
  --sms-url "https://example.com/sms" \
  --voice-url "https://example.com/voice"
```

---

## Send SMS

```bash
twilio api:core:messages:create \
  --from "+14155551234" \
  --to "+14155556789" \
  --body "Your order has shipped."

# List recent messages
twilio api:core:messages:list --to "+14155556789" --limit 10
```

---

## Send Email (SendGrid)

Requires `SENDGRID_API_KEY` environment variable.

```bash
# Configure defaults
twilio email:set --from "noreply@example.com" --subject "Default Subject"

# Send email
twilio email:send \
  --to "user@example.com" \
  --subject "Invoice attached" \
  --text "Please find your invoice." \
  --attachment ./invoice.pdf

# Pipe output as email body
ps aux | twilio email:send --to "ops@example.com" --subject "Process list"
```

---

## Webhook Development

```bash
# Set webhook URLs on a number
twilio phone-numbers:update +14155551234 --sms-url "https://your-tunnel-url.example.com/sms"

# Emulate webhook events locally (requires plugin)
twilio plugins:install @twilio-labs/plugin-webhook
twilio webhook:invoke http://localhost:3000/sms --type sms
```

**Local development:** The CLI rejects `localhost` URLs directly. Tunneling services such as ngrok are not bundled with twilio-cli. install one separately, then set the public tunnel URL as your webhook. 

** ngrok is NOT included in the CLI — install separately: npm install -g ngrok
  or via https://ngrok.com                                                      
  - Start tunnel: ngrok http 3000, then use the provided URL for webhook        
  configuration   
---

## Debugging & Monitoring

```bash
# Debug logging on any command (logs to stderr)
twilio api:core:messages:create --from +14155551234 --to +14155556789 --body "test" -l debug

# Real-time monitoring (requires plugin)
twilio plugins:install @twilio-labs/plugin-watch
twilio watch                    # stream debugger alerts, calls, messages in real time

# Output formatting
twilio api:core:messages:list -o json             # JSON output
twilio api:core:messages:list -o tsv              # tab-separated
twilio api:core:messages:list --properties sid,status,direction  # select columns
twilio api:core:messages:list --limit 200         # override default 50-record cap
```

---

## Serverless Deployment

```bash
twilio plugins:install @twilio-labs/plugin-serverless

# Create a new Functions project
twilio serverless:init my-project --template blank
cd my-project

# Local development
twilio serverless:start          # serves functions at localhost:3000

# Deploy to Twilio
twilio serverless:deploy
```

---

## Plugins

```bash
twilio plugins:install <package>
twilio plugins:list
twilio plugins:remove <package>
```

| Plugin | What it does |
|--------|-------------|
| `@twilio-labs/plugin-serverless` | Develop and deploy Twilio Functions and Assets |
| `@twilio-labs/plugin-dev-phone` | Test SMS/Voice without a real phone |
| `@twilio-labs/plugin-watch` | Real-time monitoring of debugger alerts, calls, messages |
| `@twilio-labs/plugin-token` | Generate client-side SDK tokens (Voice, Chat, Video) |
| `@twilio-labs/plugin-assets` | Upload static resources |
| `@twilio-labs/plugin-webhook` | Emulate webhook events for local testing |
| `@twilio-labs/plugin-flex` | Create, build, deploy Flex plugins |

---

## Regional & Edge Routing

```bash
# Login to a specific region
twilio login --region au1 --edge sydney

# Set edge globally
twilio config:set --edge=sydney

# Or via env vars
export TWILIO_REGION=au1
export TWILIO_EDGE=sydney
```

Supported: `au1`/`sydney`, `ie1`/`dublin`, `jp1`/`tokyo`. Each region uses a different Auth Token from your US1 credentials. Find yours in the Twilio Console under API keys & tokens, selecting your target region.

---

## Configuration

```bash
twilio config:list                          # show all settings
twilio config:set --edge=sydney             # set default edge
twilio config:set --require-profile-input   # prompt before using active profile
```

Config stored at `~/.twilio-cli/config.json`.

**Syntax notes:**
- Commands use spaces by default, using colon also works: `twilio api core messages create` = `twilio api:core:messages:create`
- `twilio [COMMAND] --help` for any command's options
- Multi-line: use `\` for line continuation

---

## CANNOT

- **Default list limit is 50 records** — always pass `--limit` for larger result sets.
- **API timeout is 30 seconds** — long-running operations may fail silently.
- **Cannot use localhost URLs for webhooks** — use a tunneling service, such as ngrok, installed separately.
- **No autocomplete on Windows** — only bash/zsh supported.
- ** ngrok is not bundled with twilio-cli**, install separately
- **Cannot send Twilio Email (comms API) via CLI** — `twilio email:send` uses SendGrid only. For Twilio Email, use the REST API directly.

---

## Next Steps

- **Account setup and API keys:** `twilio-account-setup`, `twilio-iam-auth-setup`
- **Webhook architecture and signature validation:** `twilio-webhook-architecture`
- **Debugging and observability:** `twilio-debugging-observability`
- **Send SMS via API/SDK:** `twilio-send-message`
- **SendGrid email setup:** `twilio-sendgrid-account-setup`
