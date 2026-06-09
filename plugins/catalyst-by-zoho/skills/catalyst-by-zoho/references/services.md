# Catalyst Services Reference

## Table of Contents
1. [AppSail (PaaS Compute)](#appsail)
2. [Circuits (Workflow Orchestration)](#circuits)
3. [SmartBrowz (Headless Browser)](#smartbrowz)
4. [ConvoKraft (Conversational Bots)](#convokraft)
5. [Slate (Frontend Deployment)](#slate)
6. [Pipelines (CI/CD)](#pipelines)
7. [QuickML (Machine Learning)](#quickml)
8. [Signals (Event Bus)](#signals)
9. [Job Scheduling](#job-scheduling)
10. [Zia Services (AI/ML)](#zia-services)
11. [DevOps (Monitoring & Logs)](#devops)
12. [CodeLib (Pre-built Solutions)](#codelib)
13. [Tunneling (Local Dev Exposure)](#tunneling)
14. [Catalyst Tools (VS Code Extension)](#catalyst-tools)
15. [Zia AI Assistant (In-Console AI)](#zia-ai-assistant)

---

## AppSail

AppSail is Catalyst's PaaS (Platform-as-a-Service) for deploying full applications, as opposed to individual functions.

### When to use AppSail vs Functions
- **Functions**: Stateless, event-driven, auto-scaling, pay-per-execution. Best for APIs, webhooks, scheduled tasks.
- **AppSail**: Persistent server process with managed runtimes or custom Docker. Best for full web apps, long-running processes, WebSockets.

### Catalyst-Managed Runtimes
Pre-configured environments:
- **Node.js**: Express, Hapi, Koa, Fastify, Restify
- **Java**: Embedded Jetty, Spring MVC, Spring Boot
- **Python**: Flask, Django, Bottle, CherryPy, Tornado

### Custom Runtimes (Docker)
Deploy any language/framework as OCI container images:
- Go, Kotlin, Dart, Ruby, PHP, Deno, Bun, Rust — anything with a Dockerfile
- Push to Catalyst's Container Registry or pull from external registries

### AppSail project structure (Node.js + Express example)
```
appsail/
├── app.js                    # Main application file
├── package.json
├── catalyst-config.json      # AppSail configuration
└── node_modules/
```

### catalyst-config.json for AppSail
```json
{
  "name": "my-app",
  "stack": "node20",
  "command": "node app.js",
  "memory": 512,
  "port": 9000
}
```

The `port` must match what your app listens on. Catalyst routes traffic to this port.

### AppSail with Express.js
```javascript
// appsail/app.js
const express = require('express');
const catalyst = require('zcatalyst-sdk-node');

const app = express();
app.use(express.json());

const PORT = process.env.X_ZOHO_CATALYST_LISTEN_PORT || 9000;

app.get('/api/hello', (req, res) => {
  res.json({ message: 'Hello from AppSail!' });
});

app.get('/api/users', async (req, res) => {
  try {
    const catalystApp = catalyst.initialize(req);
    const zcql = catalystApp.zcql();
    const users = await zcql.executeZCQLQuery('SELECT * FROM Users LIMIT 50');
    res.json(users);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

Important: In AppSail, always use `process.env.X_ZOHO_CATALYST_LISTEN_PORT` as the port, with a fallback
for local development.

### AppSail with Docker (Custom Runtime)
```dockerfile
# Dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --production
COPY . .
EXPOSE 9000
CMD ["node", "app.js"]
```

### Deployment
```bash
# Deploy AppSail from CLI
catalyst deploy --only appsail

# For Docker-based deployment
catalyst appsail:deploy --docker
```

### AppSail Configurations
- **Instances**: 1-5 instances for auto-scaling
- **Memory**: 256MB to 2048MB per instance
- **Health checks**: Configure health check endpoints
- **Environment variables**: Set via console (see warning below)
- **Custom domains**: Map via Domain Mappings

### AppSail environment variables — Console only

**`app.yaml` environment variables are NOT applied at deploy time.** AppSail ignores them entirely.

The **only** way to set environment variables for AppSail is through the Catalyst Console:

> Catalyst Console → AppSail → \<service\> → Configuration → Environment Variables

This applies to all env vars including secrets, API keys, and table names. Do not rely on
`app.yaml`, `.env` files, or `catalyst-config.json` `env_variables` for AppSail services.

Note: For serverless Functions, `env_variables` in `catalyst-config.json` DO work and are
deployed with the function. This limitation is specific to AppSail.

### Slate + AppSail cross-origin issue

A Slate-hosted frontend calling AppSail APIs may get `"Unable to Fetch"` or `"Failed to fetch"`
errors due to Catalyst's auth layer on AppSail.

**Solution — serve the frontend from AppSail itself (same-origin):**

```javascript
const path = require('path');
const express = require('express');
const app = express();

// API routes first
app.get('/api/data', async (req, res) => { /* ... */ });

// Serve frontend static files
app.use(express.static(path.join(__dirname, 'public')));

// Catch-all: serve index.html for client-side routing
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});
```

Copy your frontend build output into `public/` inside the AppSail directory. Use relative
URLs in frontend code (`const API_BASE = ''`) so all API calls stay same-origin.
This eliminates both CORS and auth-layer issues without extra configuration.

### Slate + Serverless Functions cross-origin (WORKS — with correct setup)

Unlike AppSail, **Slate → Serverless Function cross-domain requests DO work** once configured correctly.
The Catalyst ZGS gateway handles CORS injection automatically.

**Required setup:**

1. **Add Slate domain to Authorized Domains** — Console → Authentication → Whitelisting →
   Authorized Domains → + Add Domain → add your Slate URL (e.g. `myapp.onslate.com`) → enable CORS toggle.
   This makes the gateway inject `Access-Control-Allow-Origin` on every response.

2. **Do NOT set CORS headers in your function code for production origins.** The gateway already
   injects them. If your Express code also sets `Access-Control-Allow-Origin`, the browser receives
   **duplicate headers** and rejects the response:
   ```
   The 'Access-Control-Allow-Origin' header contains multiple values
   'https://myapp.onslate.com, https://myapp.onslate.com', but only one is allowed.
   ```

3. **Only set CORS headers for localhost** (local dev — where no gateway is present):
   ```javascript
   // CORS for local development only — gateway handles production origins
   app.use((req, res, next) => {
     const origin = req.headers.origin || '';
     if (/^http:\/\/localhost(:\d+)?$/.test(origin)) {
       res.setHeader('Access-Control-Allow-Origin', origin);
       res.setHeader('Access-Control-Allow-Credentials', 'true');
       res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
       res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
       if (req.method === 'OPTIONS') return res.status(204).end();
     }
     next();
   });
   ```

4. **Use `generateAuthToken()` with the full function URL** — relative paths resolve to
   `onslate.com/server/...` (404). See `sdk-web.md` for the complete cross-domain pattern.

**Key rule: the gateway owns CORS headers for production origins. Express must not touch them.**

**What causes failures:**
- `cors()` middleware with explicit allowed list → gateway AND Express both set the header → duplicate → rejected
- `cors({ origin: true })` → reflects origin, duplicating the gateway injection
- `cors()` with `callback(new Error(...))` for non-localhost → returns HTML 500 error page instead of JSON

### Health checks and autoscaling

**Health check endpoint:**
AppSail pings your service periodically to verify it's healthy. Configure a health
check endpoint that returns HTTP 200:

```javascript
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok' });
});
```

Configure the health check path in Console → AppSail → service → Configuration → Health Check.

**Autoscaling:**
- Instances scale from 1 (min) to 5 (max)
- Scale-up triggers when instance utilization reaches **80%** of the configured threshold
- Scale-down happens automatically when load drops

**Graceful shutdown:** AppSail sends SIGTERM before killing instances. Handle it:

```javascript
process.on('SIGTERM', () => {
  console.log('Shutting down gracefully...');
  server.close(() => process.exit(0));
});
```

### Custom domain SSL

Catalyst provides free SSL certificates for custom domains, provisioned and renewed
automatically via Zoho's own Certificate Authority.

- **Renewal:** Automatic — no manual intervention required
- **Validation:** DNS-based (CNAME record must point to Catalyst)
- **Troubleshooting:** If SSL fails to provision or renew:
  1. Verify your DNS CNAME still points to the Catalyst domain
  2. Check Console → Domain Mapping for certificate status
  3. Allow up to 24 hours for DNS propagation after changes
  4. Contact Catalyst support if the certificate remains in a failed state

---

## Circuits

Visual workflow orchestration engine. Design multi-step workflows with drag-and-drop in the console.

### Key concepts
- **States**: Individual steps in a workflow (function execution, condition, wait, parallel)
- **Transitions**: Flow between states
- **Input/Output**: JSON data passed between states

### State types
1. **Function State**: Executes a Basic I/O function
2. **Condition State**: Branches based on conditions
3. **Wait State**: Pauses execution for a duration
4. **Parallel State**: Executes multiple branches simultaneously
5. **End State**: Terminates the circuit

### Error handling in Circuits
- **Retry**: Configure delay and number of attempts for failed states
- **Fallback**: Define a fallback state if retries are exhausted
- Custom error handlers supported for both Function and Circuit states

### Invoking a Circuit
```javascript
// From another function
const circuit = catalystApp.circuit();
const result = await circuit.execute(CIRCUIT_ID, {
  inputKey: 'inputValue'
});
// Circuit ID from Console → Serverless → Circuits → circuit details

// Via REST API
// POST /server/circuit/{circuit_id}/execute
// Body: { "inputKey": "inputValue" }
```

### Circuit use cases
- Multi-step data processing pipelines
- Approval workflows
- ETL (Extract, Transform, Load) processes
- Saga pattern for distributed transactions
- Sequential function orchestration with error handling

---

## SmartBrowz

Headless browser service for web automation, scraping, and document generation.

### Capabilities
- Web scraping and crawling (permitted websites only)
- Screenshot capture
- PDF generation from HTML templates
- Browser automation (form filling, clicking, navigation)
- Dynamic content rendering

### Browser automation with Puppeteer
SmartBrowz supports Puppeteer-like APIs for browser control:
```javascript
// In a Browser Logic function
module.exports = async (catalystApp, context, browserData) => {
  try {
    const input = JSON.parse(browserData.getArgument());
    const smartBrowz = catalystApp.smartBrowz();
    const browser = await smartBrowz.open();
    const page = await browser.newPage();

    await page.goto(input.url || 'https://example.com');
    const title = await page.title();
    const screenshot = await page.screenshot({ encoding: 'base64' });

    await browser.close();
    context.close();
  } catch (error) {
    console.error('SmartBrowz error:', error);
    context.close();
  }
};
```

The SmartBrowz API is Puppeteer-like. `browserData.getArgument()` provides
input data; `catalystApp.smartBrowz()` provides the browser automation client.

### Template-based document generation
Design HTML/CSS templates in the console, inject dynamic data, and generate PDFs or images.

---

## ConvoKraft

Build AI-powered conversational bots.

### Components
- **Bot Configuration**: Define bot personality, capabilities, and embedding settings
- **Tasks**: Define specific actions the bot can perform (e.g., "book appointment", "check status")
- **Business Logic**: Connect tasks to Catalyst functions for backend processing
- **Embedding**: Embed bots in web applications via JavaScript SDK

### How it works
1. Create a bot in Console → ConvoKraft
2. Define tasks — each task maps to a user intent
3. Connect tasks to Catalyst Functions that handle the backend logic
4. Embed the bot in your frontend using the JS SDK
5. Bot processes user messages, matches intents to tasks, executes functions

### Embedding a bot
```html
<script src="https://static.zohocdn.com/catalyst/sdk/js/convokraft.js"></script>
<script>
  catalyst.convokraft.init({
    botId: 'YOUR_BOT_ID',  // ← Get from Console → ConvoKraft → bot details
    position: 'bottom-right'
  });
</script>
```

### Pricing
- $0.0006 per message
- Free tier: 1,000 messages/month

---

## Slate

**Slate is the preferred frontend deployment service for all new Catalyst projects.** It supersedes legacy
Web Client Hosting with modern Git-based workflows and native framework support.

### Key features
- Native support for JavaScript frameworks (Next.js, React, Vue, Angular, Svelte)
- Git-based deployment (connect GitHub/GitLab repos)
- Automatic builds and deployments on push
- Preview deployments for branches
- Custom domain mapping
- Environment variables
- Server-side rendering (SSR) support for frameworks like Next.js
- ISR (Incremental Static Regeneration) support

### CLI workflow
```bash
catalyst slate:create                # Add an additional Slate app (interactive — asks framework + name + build config)
catalyst slate:link                  # Link existing local dir to Slate service (interactive)
catalyst slate:unlink                # Unlink a Slate app
catalyst serve --only slate          # Serve Slate app locally
catalyst deploy slate                # Deploy all Slate apps to Development
catalyst deploy slate -m "message"   # Deploy with a deployment message  
catalyst deploy --only slate:appname # Deploy a specific Slate app
catalyst deploy slate --production   # Deploy to Production
```

### Supported frameworks
- Next.js (with SSR support)
- React (Create React App, Vite)
- Vue.js
- Angular
- Svelte/SvelteKit
- Vanilla HTML/CSS/JS
- Any static site generator

### Slate — Manual setup (non-interactive)

`catalyst slate:link` is interactive-only and cannot be piped or scripted. For automated
or CI/CD environments, set up Slate manually:

1. Create `.catalyst/slate-config.toml` inside the client directory:
   ```toml
   framework = "static"
   deployment_name = "default"
   ```
2. Add Slate to `catalyst.json` with an **absolute** source path:
   ```json
   "slate": [{ "name": "my-frontend", "source": "/absolute/path/to/client" }]
   ```
3. Deploy with `catalyst deploy slate -m "deploy message"`.

Slate URL format: `https://<project-domain>.onslate.in`

---

## Pipelines

CI/CD service for automating build, test, and deployment workflows.

### Features
- YAML-based pipeline configuration
- Multi-stage pipelines (build → test → deploy)
- Integration with GitHub, GitLab, Bitbucket
- Environment-specific deployments
- Parallel job execution
- Artifact management
- Secret management

### Pipeline configuration example

```yaml
# .catalyst-pipeline.yml
name: deploy-pipeline
trigger:
  branches:
    - main

stages:
  - name: build
    steps:
      - run: npm install
      - run: npm test

  - name: deploy
    steps:
      - run: catalyst deploy --only functions
```

Configure in Console → Pipelines → connect your GitHub/GitLab/Bitbucket repository.
Pipelines run automatically on push to the configured branch.

---

## QuickML

No-code ML pipeline builder.

### Features
- Data connectors (CSV, databases, APIs)
- Data preprocessing (normalization, encoding, feature selection)
- Pre-built ML algorithms (classification, regression, clustering)
- Model training and evaluation
- Model deployment as API endpoints
- AutoML capabilities
- LLM/VLM token support (input/output tokens with per-million pricing)

All configuration is done through the visual console — no code required.

### Invoking a deployed model
```javascript
// From a Catalyst function — call a QuickML endpoint
const response = await fetch('https://your-quickml-endpoint-url', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ input_data: yourData })
});
```

---

## Signals

**Signals is the preferred mechanism for integrating Catalyst apps with other Zoho products** (CRM, Books,
Desk, People, Analytics, etc.) and for building event-driven architectures. It replaces the deprecated
Event Listeners with a far richer feature set.

### Architecture
Publishers emit events → Rules filter/transform/route → Targets receive and process.

### Core elements

**Publishers** — Sources that emit events:
- **Zoho Publishers**: Pre-built publishers from Zoho CRM, Books, Desk, Survey, Inventory, etc.
  Come with predefined events and schemas (e.g., CRM "Deal Closed" event).
- **Catalyst Publishers**: Built-in publishers from Catalyst Cloud Scale services — Authentication,
  Cache, Data Store, File Store, Stratus. Events fire on data changes automatically.
- **Custom Publishers**: Your own applications or third-party services. You provide the REST API URL
  that emits events. Schema can be generated from live event payloads (no manual schema creation).

**Rules** — Control how events flow from publisher to target:
- **Event filtering**: Filter events based on properties in the event payload (e.g., only deals > $10K)
- **Event transformation**: Three-pane visual editor to map/transform the event payload before delivery
- **Dispatch policy**: Choose between real-time delivery or batch delivery (scheduled collection)
- **Time To Live**: Configure how long undelivered events are retained
- **Retry policies**: Configure retry attempts and delays for failed deliveries
- **Consumer types**: Route to multiple targets from a single rule

**Targets** — Destinations that receive events:
- **Webhooks**: HTTP endpoints (external URLs). Configure headers, parameters, rate limits, and
  authentication via Connections.
- **Functions**: Catalyst Event Functions that process the event data
- **Circuits**: Catalyst Circuits workflows that orchestrate multi-step processing

### Setting up Signals (step by step)
1. Console → Signals → Add Publisher (choose Zoho, Catalyst, or Custom)
2. For Zoho/Catalyst publishers: events and schemas are pre-configured
3. For Custom publishers: provide REST API URL; optionally generate schema from live payload
4. Create a Webhook (if using external target) or use existing Functions/Circuits
5. Create a Rule: select publisher + event → configure filters → configure transformation →
   set dispatch policy → select target(s)
6. Monitor via Signals Dashboard and Logs

### Monitoring
- **Dashboard**: Overview of all rules, event counts, success/failure rates per rule
- **Logs**: Detailed execution logs per event delivery
- **Application Alerts**: Auto-trigger email alerts on delivery failures (integrated from DevOps)

### Real-world use cases
- **CRM deal automation**: CRM "Deal Closed" event → Function → create invoice in Zoho Books
- **Lead enrichment**: CRM "New Lead" event → Function → SmartBrowz scrape → update lead data
- **Order processing**: Custom app "Order Placed" event → Circuit → update inventory + send email
- **Feedback classification**: Website "Feedback" event → Function → Zia Text Analytics → store result
- **Cross-product sync**: Any Zoho product event → Function → sync data to Data Store/external DB

---

## Job Scheduling

Execute background jobs with managed job pools. Replaces the deprecated Cron service.

### Components
- **Job Pools**: Containers for grouping related jobs
- **Jobs**: Individual tasks submitted to a pool
- **Triggers**: Job Functions, Circuits, Webhooks, or AppSail services
- **Scheduling**: Predefined or dynamic cron expressions for scheduled job submission

### Submitting a job
```javascript
const jobScheduling = catalystApp.jobScheduling();
const pool = jobScheduling.pool(POOL_ID);
// Pool ID from Console → Job Scheduling → pool details

await pool.submitJob({
  input: JSON.stringify({ taskType: 'report', params: { month: 'January' } })
});
```

### Key advantages over deprecated Cron
- Multiple target types (not just Cron Functions)
- Job pools for organizing and grouping jobs
- Better tracking of job instances and execution history
- On-demand job submission in addition to scheduled

---

## Zia Services

AI/ML microservices you can call from your code.

### Available services
- **OCR**: Extract text from images and documents
- **Barcode Scanner**: Read barcodes and QR codes
- **Face Detection**: Detect faces in images
- **Image Moderation**: Check images for inappropriate content
- **Object Detection**: Identify objects in images
- **Text Analytics**: Sentiment analysis, keyword extraction, NER
- **AutoML**: Train custom ML models with your data
- **Prediction**: Make predictions using trained AutoML models

### OCR example
```javascript
const zia = catalystApp.zia();

// OCR from file
const result = await zia.extractOpticalCharacters({
  image: fileBuffer,     // Buffer or ReadStream
  modelType: 'OCR'       // or 'HANDWRITTEN'
});
console.log(result.text);
```

### Text Analytics example
```javascript
const zia = catalystApp.zia();

const sentiment = await zia.getTextAnalytics({
  document: 'I love this product! It works perfectly.',
  features: ['sentiment', 'keyword']
});
```

---

## DevOps

### Logs
View execution logs for all functions, AppSail, and other services.
- Log levels: INFO, WARNING, ERROR, DEBUG
- Filter by function, time range, status
- Available in the console under DevOps → Logs

### Application Performance Monitoring (APM)
- Execution time tracking
- Error rate monitoring
- Cold start analysis
- Resource utilization metrics
- Custom metrics via SDK

### Application Alerts
Configure email alerts for:
- Function failures
- Cron job failures
- Event Listener failures
- Signals delivery failures
- Custom threshold breaches

### GitHub Integration
Deploy functions directly from GitHub repositories:
- Connect your GitHub account in project settings
- Map repos to functions
- Auto-deploy on push to specific branches

### Debugging production failures

**Step 1 — Find the error in Logs:**
- Console → DevOps → Logs → select function name → filter by error level
- Each log entry includes a request ID and timestamp

**Step 2 — Correlate with APM:**
- Console → DevOps → APM → filter by the same time range
- APM shows execution time, memory usage, and error traces per function

**Step 3 — Set up Application Alerts:**
- Console → DevOps → Alerts → create alert for error rate thresholds
- Alerts can notify via email when error rate exceeds a configured percentage

**Tip:** Add structured logging in your functions:
```javascript
console.log(JSON.stringify({ requestId: req.headers['x-request-id'], action: 'createUser', status: 'success' }));
```
This makes log searching and filtering much easier in the DevOps console.

---

## Secrets Management

**Where to store secrets (API keys, tokens, passwords):**

| Method | Use for | Security level |
|--------|---------|---------------|
| Function `env_variables` in catalyst-config.json | Non-sensitive config | Low — visible in repo |
| Console → Function → Environment Variables | Secrets for Functions | Medium — not in repo |
| Console → AppSail → Environment Variables | Secrets for AppSail | Medium — not in repo |
| Connections | OAuth tokens for Zoho/third-party | High — auto-refresh, encrypted |

**Rules:**
- **Never commit secrets to git** — use `.gitignore` for any file containing keys
- **Never hardcode secrets in source code** — always use environment variables
- **Use Connections for OAuth tokens** — Catalyst handles refresh automatically
- **For CI/CD:** Pass secrets as pipeline environment variables, never in YAML files

For Functions, `env_variables` in `catalyst-config.json` are deployed with the function
and accessible via `process.env.VAR_NAME`. For sensitive values, set them in the Console
instead (Serverless → Function → Settings → Environment Variables) so they stay out of git.

Reminder: For AppSail, `app.yaml` env vars are NOT applied at deploy time. Always use
the Console for AppSail environment variables.

---

## CodeLib

Pre-packaged, installable microservice solutions.

### How it works
1. Browse available CodeLib solutions in the console
2. Install a solution into your project
3. The solution creates the necessary functions, tables, and configurations automatically
4. Customize the installed code as needed

### Examples of CodeLib solutions
- Zoho CRM Bulk Processor
- DataStore Analytics Sync
- Email notification services
- Webhook handlers

---

## Tunneling

Expose your local development server to the internet for webhook testing and Zoho integration debugging.

### When to use
- Testing Signals webhooks that need to reach your local machine
- Debugging Zoho product integrations that require a public callback URL
- Testing third-party webhook integrations locally

### How it works
1. Configure tunneling in Console → Settings → Tunneling
2. Generate a tunneling URL (public URL that routes to your local server)
3. Use `catalyst functions:shell` to start tunneling
4. External services can now reach your local functions via the tunneling URL

### Workflow
```bash
# Start local serve with tunneling
catalyst functions:shell
# Follow the prompts to start tunneling
# Use the generated URL for webhook/callback configuration
```

---

## Catalyst Tools

VS Code Extension for Catalyst development. Provides IDE-integrated project management and deployment.

### Features
- **Project Explorer**: Browse project structure, functions, and services directly in VS Code
- **Code Generation**: Generate function boilerplate, config files from the IDE
- **Deployment**: Deploy functions and services without leaving the editor
- **Command Palette**: Access all Catalyst CLI commands from VS Code command palette

### Installation
Search "Catalyst Tools" in VS Code Extensions marketplace and install.

---

## Zia AI Assistant

In-console AI assistant for code-related tasks. Available in the Catalyst web console.

### Capabilities
- **Code Converter**: Convert code between languages/frameworks
- **Code Generator**: Generate function code from natural language descriptions
- **Code Debugger**: Identify and explain bugs in your Catalyst code
- **Code Docs Generator**: Auto-generate documentation for your functions
- **Test Case Generator**: Generate test cases for your Catalyst functions

### OpenAI Integration
Catalyst supports configuring OpenAI as the backing model for the Zia AI Assistant.
Configure in Console → Settings → Integrations → OpenAI.
