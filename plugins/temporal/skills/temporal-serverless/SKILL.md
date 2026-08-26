---
name: temporal-serverless
description: 'Deploy and operate Temporal Workers on serverless compute (AWS Lambda) driven by the Worker Controller Instance (WCI). Use when the user mentions: "serverless worker", "Temporal serverless", "Worker Controller Instance", "WCI", "deploy Temporal worker on Lambda", "Lambda packaging", "Lambda timeout", "WCI inspection", "CloudFormation Temporal".'
version: 0.6.0
disable-model-invocation: true
---

# Skill: temporal-serverless

## Overview

This skill helps users deploy and operate Temporal Workers on serverless compute. Instead of a long-lived process, Temporal invokes the Worker on demand through the Worker Controller Instance (WCI); the Worker processes available Tasks and shuts down, scaling to zero when idle. The skill produces Worker code, deployment configuration, connection configs, and packaging steps for the chosen SDK, and walks users through troubleshooting when serverless Workers aren't picking up Tasks.

## Supported compute providers

| Cloud provider | Compute service | Support | Reference directory |
|---|---|---|---|
| AWS | Lambda | Supported — Public Preview, open to all Temporal Cloud customers | `references/aws-lambda/` |
| GCP | Cloud Run | Not supported | — |

Only a provider marked Supported is covered. If a request names another, say it is not supported and stop; do not adapt a supported provider's material to it. **Never let the provider be an unstated assumption:** when the request does not name one, it is confirmed in the step 1 questions, not silently defaulted.

Every supported provider's directory carries the same layout — `setup.md`, `iam.md`, `versioning.md`, `diagnostics.md`, `observability.md`, `self-hosted.md`. Paths below are written `references/<provider>/…`; substitute the directory from the table. Provider-specific commands, templates, permissions, and defaults live there — this file stays at the workflow level. When a step needs concrete commands, go to the reference file named at the end of that step.

**Public Preview is not GA.** The APIs are still evolving and may change: pin SDK and CLI versions for anything long-lived, and read the installed package's actual API surface rather than writing from memory.

## Deployment workflow

Follow these steps in order. Each step is provider-neutral; the concrete commands, templates, and options live in the reference file named at the end of the step.

**Open a new deployment with a plain-language summary of the run.** Before the step 1 questions, tell the user in a few sentences what is about to happen: that this creates real resources in their cloud account which cost money for as long as they exist; that you will ask about a handful of things, then show an exact list of what you are about to create and wait for approval, and that nothing is created before that approval; that the middle of the run is unattended; and that it ends with a Workflow they can watch execute, an inventory of everything created, and an offer to remove it all. Name the five stages below in ordinary words. Do not explain Temporal or serverless compute; keep it short enough to read at a glance.

**Lay it out as bullets, with the five stages as sub-bullets under "How it goes" — one stage per line, never chained into a single run-on bullet.** Follow this shape:

> Here's what's about to happen, before I ask anything:
>
> - This creates real resources in your cloud account — the compute unit that runs your Worker, roles, an infrastructure stack, logs. They're live and billable for as long as they exist.
> - **How it goes.** Five stages:
>   - **Scope** — a handful of questions, below.
>   - **Access** — check credentials and permissions on both sides, then show you an exact list of what I'm about to create and wait for your approval.
>   - **Build** — write, package, deploy the Worker.
>   - **Connect** — bind the Task Queue, set the version current.
>   - **Verify and hand back.**
> - Nothing gets created before you approve that list. After approval the middle stretch runs unattended.
> - At the end you get a Workflow you can watch execute, a full inventory of everything created, and an offer to remove it all.

**Write the summary provider-neutral, because at that point you do not know the provider.** It is one of the things step 1 asks. Say "your cloud account", never the name of a provider you have not been told. The same applies to the account, Namespace, and region: if a cheap read-only call has already told you (see step 1), name what you actually found; otherwise leave it out rather than filling it in with a plausible guess.

Skip the summary for troubleshooting, inspection, and configuration-change tasks. Someone whose Worker is not being invoked does not need an overview of a deployment they have already done.

**Then track the run on a checklist, and reprint it every time a step completes.** The eight steps group into the five stages below. Create one item per step, grouped under its stage, and build the checklist as soon as step 1's answers land, so items can name the confirmed provider and the agreed prefix instead of hedging.

**Reprint the whole checklist at each step boundary — not just the item that changed, and not a sentence saying the stage is done.** Mark finished items ✅, the one you are starting ⏳, and the rest ⬜. Use the bare marker with nothing in front of it — `✅ Confirm SDK`, not `- [x] Confirm SDK` — and put each item on its own line. A narrated "Access complete, now Build" is not a substitute: it says where you are but not what remains, and the user cannot see it without scrolling back to a checklist printed twenty commands ago. Reprint during Scope and Access too — those stages end in a user decision, and the reprint is what shows the decision landed and what it unblocked.

Where the harness has a todo list, use it *in addition to* the printed checklist, not instead of it. It is not part of the transcript the user reads back.

**Word each item as plain language about what happens, not as a compressed step title,** and name both sides concretely — the confirmed compute provider and Temporal, never "both sides." Follow this shape:

> **Scope**
> ✅ Confirm SDK (Go), compute provider (AWS Lambda), Namespace (`<ns>`), and naming prefix (`<prefix>`)
>
> **Access**
> ⏳ Check credentials and permissions on AWS and on Temporal, then show the exact list of resources to be created and wait for your approval
>
> **Build**
> ⬜ Write the Worker against the installed package's real API
> ⬜ Cross-compile, package, deploy the compute unit, wait for it to report ready
>
> **Connect**
> ⬜ Create the role Temporal assumes to invoke the Worker
> ⬜ Register the Worker Deployment Version, confirm the validation invocation bound the Task Queue, set it current
>
> **Verify and hand back**
> ⬜ Start a Workflow and confirm it executes, from both the Temporal side and the provider's logs
> ⬜ Deliver the inventory of everything created, then offer teardown

| Stage | Steps | Complete when |
|---|---|---|
| Scope | 1 | SDK, compute provider, Namespace, and naming prefix are all confirmed by the user. |
| Access | 2 | Compute provider and Temporal both authenticated, permissions confirmed, and the list of resources to create approved. |
| Build | 3–4 | The compute unit is deployed and reports ready, built for the architecture it runs on. |
| Connect | 5–6 | The Task Queue is bound and the version is current. |
| Verify and hand back | 7–8 | A Workflow completed, two independent signals agree, the inventory is delivered, and teardown has been offered. |

**A step is complete when its verification passed — not when its command exited zero.** Several commands in this workflow exit clean having done nothing: the traffic-shifting and key-revocation commands no-op when their confirmation prompt goes unanswered, and providers return from create and update calls while the resource is still settling. Check an item off against state you read back, not against an exit code. When a step's verification fails, say which step you are on and what it is blocked on rather than moving down the list.

1. **Scope the task.** Identify the SDK language (Go, Python, or TypeScript), the deployment target (Temporal Cloud or self-hosted — self-hosted has its own server prerequisites), the compute provider, and whether this is a new setup, a configuration change, or troubleshooting. Confirm the deployment target is compatible with the chosen provider — see "A Namespace on the target cloud provider is required" under Provider-neutral principles. Ensure a Temporal client/CLI is available and authenticated to the target. Each changes the specifics. → `references/concepts.md` for what the user is building; `references/<provider>/setup.md` for the compatibility and client-setup details.

   **Put the compute provider in that batch of questions as a confirmable default, not a free choice.** Pre-select the supported provider from the table above and carry its support status in the option's description. The user confirms rather than chooses, so it costs no extra turn, but the provider is never something they were assumed into. Skip the question only when the request already names a provider. Do not restate any of this in a paragraph before the questions; the option description is where it belongs.

   **Let the user pick the Namespace from a list; never make them retype one.** Namespace names are long and error-prone — a generated suffix on an account ID, `<name>-<suffix>.<account>`. Where control-plane access is available, `tcld namespace list` returns the full Namespace objects, so one call gives every name with its region — and a region ID is provider-prefixed (`aws-…`, `gcp-…`), so the same response tells you each Namespace's provider. Only the prefix carries meaning; the region itself imposes no constraint.

   Present it like this:

   - **Offer the eligible Namespaces as the options**, each labelled with its region.
   - **Summarize the ineligible ones in a single line** — "you also have 2 Namespaces on \<provider\>, which this skill does not support" — rather than listing them individually or hiding them. A user who knows they have a Namespace and cannot find it in the list concludes the tool is broken; one line keeps them informed and explains the constraint.
   - **Name the account you are listing from and confirm it is the intended one** before showing anything. A stale credential lists a real account that is not the one the user means to deploy into, and every option under it looks authoritative.
   - **If more Namespaces are eligible than the question format can hold, print the labelled list and ask the user to name one.** Do not silently show only the first few.

   This also settles the compute-provider answer, since a Namespace can only be served by compute on its own cloud provider — so a mismatch is caught here rather than at connection time, several steps later.

   **Degrade gracefully if `tcld` is not authenticated.** Ask the user for the Namespace name rather than stopping to fix the login — they can copy it from the Cloud UI, where it appears on the Namespace page and in the URL. Ask for its region in the same batch of questions: the name alone does not tell you the provider, and a mismatch missed here surfaces at connection time instead.

   **Never source a Namespace, account, or resource identifier from shell history.** History is stale by construction — it is full of last quarter's accounts — and reading it to guess a deployment target produces confident, wrong answers. Take identifiers from the user or from an authenticated API call, and nowhere else.

   **Agree a resource-naming prefix in this same batch of questions, and propose a default so the user can accept without thinking about it.** Assume the account and the Namespace are shared — unprefixed names like `temporal-serverless-worker` collide with, or quietly shadow, another team's deployment. Naming is not a late cosmetic choice you can patch on the provider side: the deployment name, build ID, and Task Queue are compiled into the Worker binary, so changing them after step 3 means editing code, rebuilding, repackaging, and cleaning up whatever was already created under the old names. Once agreed, apply the prefix to everything you create on both sides — compute unit, roles, infrastructure stacks, log groups, deployment name, and Task Queue.

   **The prefix you propose must be identifying** — derived from the user, their team, or the project. A generic word like `demo`, `test`, or `temporal` collides about as readily as no prefix at all, so never offer one as the safe choice.

   Offer exactly two options plus the free-text escape: the identifying prefix, and "no prefix" — some users genuinely own the account. Do not offer a second prefix string; the consequential choice is prefix versus none, and anything else goes in free text. When you offer "no prefix," say what it risks in the same breath: unprefixed names can collide with or shadow an existing deployment, and that surfaces as another team's Worker behaving oddly rather than as an error you will see.

2. **Confirm you can make the required changes — before making any.** Determine which credentials are available (for the compute provider and for Temporal) and confirm the active identity actually has permission to make the changes the task needs — creating or updating compute resources, creating roles, registering deployment versions. Verify *both* sides: the compute provider AND Temporal access. Do not run account-mutating commands and let them fail partway. **If access is missing or unconfirmed, stop and ask the user how they want to proceed** — extend their identity's permissions, have an administrator make the change and hand back the result, or generate the commands for the user to run under a privileged identity. Changing a user's cloud account is consequential; confirm authorization and the preferred method first. → `references/<provider>/iam.md` (exact permissions, compute-provider preflight) and `references/<provider>/setup.md` (Temporal connection preflight).

   **Classify an authentication failure before acting on it — "not signed in" and "not permitted" have different fixes.** A failed preflight does not automatically mean the bottom row of the table below. An absent or expired credential is usually recoverable in this session, in under a minute. A caller that resolves but is denied a specific action is a real permissions problem. Never collect credentials in the conversation: no interactive credential-configuration wizards, and never ask the user to paste access keys, API keys, or session tokens. → `references/<provider>/iam.md` (credential recovery).

   **Then ask the user which way they want to go, and do not choose for them:**

   - **Fix the CLI** — you run the login flow, surface the verification URL for them to open, wait for it to complete, re-run the preflight, and continue with full automation.
   - **Work in the browser** — the user makes the changes in the Cloud UI and their cloud provider's console while you give the instructions step by step, naming the exact path for each one, and they report the result back.

   Both paths reach the same end state, so present them as equals rather than as a preference and a fallback — every control-plane step in this workflow exists in the Cloud UI (see `references/<provider>/setup.md`). Ask once, then commit to the answer — do not re-offer the login at every subsequent step, and never start an identity-provider login as a silent side effect of a preflight.

   Adapt to what is available — the skill is valuable at every level:

   | Compute-provider access | Temporal access | Behavior |
   |---|---|---|
   | Authenticated | Authenticated | Full workflow — run commands, verify results, register deployment versions. |
   | Authenticated | None | Deploy compute infrastructure; walk the user through the Temporal steps in the Cloud UI, or generate the commands for them to run. |
   | None | Authenticated | Write Worker code and configs; walk the user through the compute steps in their provider's console, or generate the deploy commands; run Temporal commands and verify WCI state. |
   | None | None | Write Worker code, deploy templates, permission policies, connection configs, packaging scripts; provide all commands with placeholder values. |

   **Do not self-select a row.** Drop to a lower one only after the choice above has been put to the user and the browser path chosen, or the login attempted and failed. When you hand off a runbook, say the offer stands — if the user authenticates and comes back, take the work over rather than leaving them to run the steps by hand.

   **Before the first account-mutating command, list what you are about to create — with final names — and get approval.** Name the target account and region, then every resource: compute unit, execution role, infrastructure stack, log group, deployment name, and Task Queue. Say plainly that they are live and billable. This is the mirror of the inventory in step 8, and it is worth more here than there: it makes the naming prefix concrete while changing it is still free, and the deployment name, build ID, and Task Queue become expensive to change once step 3 compiles them into the Worker. Skip it only when nothing will be created — a troubleshooting or inspection task.

3. **Author the Worker.** *Install the SDK's serverless Worker package before writing any code* — it is often shipped separately from the main SDK, with its own version line, so having the base SDK installed does not mean it is importable. Then read the installed package's actual API surface and write against that; these are Public Preview APIs that drift between versions, and generating code from memory costs a build cycle. Every Workflow must declare a versioning behavior (`Pinned` or `AutoUpgrade`), per-Workflow or as a Worker-level default — code without it fails at runtime. → `references/sdk-configuration.md` (package, install, entry point, tuned defaults) and `references/<provider>/setup.md` (install commands, API-inspection recipes, handler shape).

4. **Package and deploy the compute unit.** Build and package per SDK, deploy the compute unit, and set the invocation deadline high enough for the Worker to start, connect, register the Task Queue, and shut down gracefully. Match the build's target architecture to the deployed compute unit's — a mismatch fails only at invocation time, not at build time. After a create or update, wait for the compute unit to reach a ready state before the next step; providers return from these calls while the unit is still settling. → `references/<provider>/setup.md`.

5. **Grant Temporal permission to invoke the Worker.** Configure the compute provider's access so Temporal can invoke and inspect the Worker. This access is separate from the compute unit's own execution role — do not confuse the two. Two things to get right before you create anything: (a) this grant is **shared, account-wide infrastructure** that a previous deployment may already have created — look for an existing one and extend it to cover your new Worker rather than creating a parallel copy, and never delete or repurpose one you did not create without asking; (b) scope the grant so that *future* immutable builds are covered, not just today's — a grant pinned to one build breaks the next release in a way that surfaces later as an unrelated-looking invocation failure. → `references/<provider>/iam.md`.

6. **Register the Worker Deployment Version, verify the validation invocation, then set it current.** Create the Worker Deployment Version with the compute provider configured; the deployment name and build ID must exactly match the values in the Worker code. Creating it triggers one validation invocation — **check that it bound the Task Queue before going further.** If the Task Queue is bound, the permission grant, package, config, and deadline are all provably correct, and any later failure is downstream; if it is not, setting the version current will not fix it. Then set it current: through the UI this happens automatically, through the CLI it is a separate step, without which Tasks never route to the version. → `references/<provider>/setup.md`.

7. **Verify.** Start a Workflow on the Task Queue and confirm Temporal invokes the Worker — check the Workflow history in the Temporal UI and the compute provider's logs. If it does not progress, → `references/<provider>/diagnostics.md`.

8. **Hand back the inventory first; offer teardown as the closing note.** The order is inventory → offer, never the reverse. Close with what now exists — compute unit and published build identifiers, roles, infrastructure stacks, region, deployment name and build ID — and what the run actually did, including anything you worked around or deviated from. Say plainly that it is live and billable. These names are only knowable from the run that created them, and reconstructing them later means scanning the user's account.

   **Do not write a teardown script before the user asks for one.** Generating it unprompted buries the inventory under a file they did not request, and the inventory is what they need in order to decide. End with a single line — *"Let me know if you want a teardown script to remove these resources"* — and stop there. Write the script, or run the teardown, when they take you up on it. → `references/<provider>/setup.md` (Teardown).

## Working practices

How to move through the workflow above.

- **Say what a command will do in your own text, above the command.** The user sees a collapsed "Ran 6 shell commands" in the transcript, not the commands themselves, so an unannounced batch is opaque at exactly the moments that matter. State it in one line before the tool call: what it does and to what — the resource, and the account or Namespace it touches.

  **The tool's own description field does not count.** It renders at the bottom of the command block, underneath the command it is describing, where the user has to go looking for it. The summary belongs above the block, as ordinary message text.

  **Set it apart on its own line so it is visibly not narrative prose** — bold, and nothing else on the line:

  > **Checking for the Temporal CLIs, AWS credentials, and which AWS account and Temporal account they resolve to**
  >
  > **Creating the invocation role Temporal assumes, with a generated External ID**

  For anything that creates, updates, or deletes, name the resource and the target account or Namespace explicitly — an approval prompt should arrive with its justification already on screen, not after it.
- **Read the current state instead of recalling it.** Check the installed package's API, the CLI's own `--help` for the flags you are about to pass, the compute unit's reported state, and the CLI version. Each of these has drifted in practice: a Public Preview SDK whose fields moved, a CLI too old to have the serverless subcommand at all, a resource that reports success while still settling.
- **Do not chain `cd` with commands that create or modify files.** A compound `cd <dir> && <write>` triggers a manual approval prompt no matter how the user's permissions are configured, so scaffolding a project this way asks for approval on every run. Use absolute paths, or the tool's own directory flag (`go -C <dir> …`), and rely on the shell's working directory persisting between calls — the `cd` buys nothing and costs a prompt. Keep the command count down for the same reason: one `go get` covering both packages beats two.
- **Verify each step before building the next on top of it.** Compile the Worker before packaging it, confirm the package's target architecture before uploading, wait for the compute unit to be ready before publishing a build, and confirm the Task Queue is bound before shifting traffic. Deployment failures here surface far from their cause — an architecture or dependency mismatch appears only at first invocation, and a first-invocation failure appears as "the Worker is never invoked", several steps later.
- **When something fails, read the actual error before changing anything.** Fetch the failure reason from the provider (deployment events, logs, status fields) and fix that. Do not retry the same command with variations, and do not start editing permissions or trust policies on the theory that the problem might be access — most first-invocation failures are not permission problems, and some failures are on Temporal's side and will reproduce no matter what you change.
- **Treat the user's account as shared and pre-existing.** Assume other deployments, roles, and stacks are already there. Look before creating, extend rather than duplicate, and never delete or repurpose something you did not create without asking. When you do work around existing infrastructure — a different name, a reused role — say so explicitly in your summary rather than leaving it as a silent deviation.
- **Confirm the end state from two independent signals.** A Workflow that completes in the Temporal UI *and* the Worker's own logs showing startup, Task Queue registration, and Task execution. One signal alone can mislead: a system Workflow that exists and is running proves nothing about invocation health, and a command that exits zero may have done nothing at all if it was waiting on a confirmation prompt.
- **Account for what you created.** Keep the inventory as you go rather than reconstructing it at the end, say plainly that the resources are live and billable, and offer to tear them down (step 8).

## Never create or manage the WCI

Temporal creates the WCI automatically once a Worker Deployment Version has a compute provider. You never create, start, or manage it. A WCI that exists or is running is *not* evidence that invocation works — it continue-as-news and keeps running even while its Activities fail. Diagnose from Temporal's own signals: read the WCI Workflow history and look for Activity failures. Do not enumerate compute resources across regions or scan the account to reverse-engineer state. → `references/concepts.md`, `references/<provider>/diagnostics.md`.

## Provider-neutral principles

Surface these early — they apply regardless of compute provider:

- **A Namespace on the target cloud provider is required.** A Serverless Worker runs only on the cloud provider that hosts its Temporal Cloud Namespace — there is no cross-cloud pairing. Confirm the user has a Namespace on the provider they intend to run compute on *before* building anything; without one, the work stops there and they need either a Namespace on that provider or a different provider. A mismatch is not caught at deploy time — it fails later, at connection time. **Regions do not have to match:** a Namespace in one region can drive a compute unit in another, so never tell a user to move or re-create a Namespace to line up regions.
- **Use `tcld` for every Temporal Cloud control-plane operation** — accounts, Namespaces, API keys, users, service accounts. Do not use the unified CLI's `temporal cloud …` subcommands for them. Worker Deployments and Workflows are *not* control-plane operations: they live on the Namespace frontend, have no `tcld` equivalent, and use `temporal worker deployment …`. → `references/<provider>/setup.md`.
- **Versioning behavior is mandatory.** Every Workflow needs `Pinned` or `AutoUpgrade`, or the Worker sets a default.
- **Deployment name and build ID must match exactly** between the Worker code and the Worker Deployment Version. A mismatch causes an invocation loop (Temporal invokes → Worker polls with the wrong version → Task not processed → invoke again). Signature: rapid repeated invocations with no Workflow progress.
- **Set the invocation deadline high enough.** Providers often default to a very short timeout. If the first invocation times out before the Worker registers the Task Queue, the binding is never created and the Worker is never invoked again. → `references/<provider>/setup.md` for the exact default.
- **Use an immutable, versioned build per Build ID in production.** Pointing the provider at a mutable "latest" target lets code change under in-flight Workflows and cause non-determinism errors, even for Pinned Workflows. Keep a 1-to-1 mapping between each Build ID and one immutable build. → `references/<provider>/versioning.md`.
- **Tune the timeout triple together for long-running Activities:** (1) worker stop timeout > longest Activity runtime, (2) shutdown deadline buffer > worker stop timeout + shutdown hook time, (3) invocation deadline > longest Activity runtime + shutdown deadline buffer. Raising one alone does not help. If the longest Activity exceeds half the maximum invocation deadline, recommend Activity Heartbeats. → `references/concepts.md`, `references/sdk-configuration.md`.
- **Eager Activities are always disabled** — serverless invocations don't maintain persistent connections. Don't suggest them as an optimization.
- **Activities are bounded by the invocation limit** (minus the shutdown deadline buffer); Workflow duration is unbounded and can span many invocations. Flag Activities that approach the provider's limit early. → `references/concepts.md`.
- **Mixed serverless + long-lived Workers on one Task Queue:** do not enable dynamic scaling on the long-lived Workers — the two groups can't coordinate scaling and will cause unnecessary invocations.
- **Secrets belong in a secret store**, not plaintext environment variables. Provider docs and quickstarts commonly pass the API key or TLS key as a plaintext environment variable; that is acceptable in a throwaway development walkthrough *only if you say so explicitly at the time*. Anything the user describes as production, shared, or long-lived gets the secret store, loaded at cold start. Either way, keep key material out of shell history and command echoes.
- **Both CLIs prompt for confirmation before mutating state, and their flags differ.** Setting the current or ramping version, and revoking an API key, all ask interactively; run non-interactively without the flag, the command exits having done nothing, which reads as success. `temporal worker deployment …` takes `--yes`; `tcld` takes the global `--auto_confirm`. Pass the right one in scripts, CI, and agent shells, and confirm the resulting state rather than trusting the exit code. → `references/<provider>/setup.md`.

## Troubleshooting

Start by determining whether the Worker is being invoked at all. Then, in priority order: (1) **Validate Connection** in the Temporal UI (Workers > Deployments > select > Actions > Validate Connection) — checks credentials, role assumption, and reachability in one step; (2) check whether the version's **Task Queue is bound** — if it is, invocation and Worker startup provably work and the fault is downstream, which rules out most of the surface in one command; (3) confirm the version is **current** (CLI-created versions are not automatic, and a confirmation-prompted command may have silently done nothing); (4) check the compute provider's logs for connection, auth, or TLS errors; (5) if rapid repeated invocations show no progress, check the deployment name/build ID match. Distinguish a Temporal-side failure (reproduces no matter what you change on the provider side) from a genuine user-permission problem before editing anything. → `references/<provider>/diagnostics.md`, `references/concepts.md`.

## Common Pitfalls

High-impact mistakes — warn the user proactively. Each is a symptom → cause → fix.

1. **Deployment name / build ID mismatch → invocation loop.** *Symptom:* rapid, repeated invocations with no Workflow progress. *Cause:* the name or build ID in the Worker code doesn't match the Worker Deployment Version, so the Worker polls with the wrong version, the Task isn't processed, and Temporal invokes again. *Fix:* make the values in code exactly match the version configuration.
2. **Version not set as current.** A version created through the CLI is not automatically current; without it, Tasks don't route to the version and the Worker is never invoked. *Fix:* set it current as a separate step (the UI does this automatically).
3. **Failed first invocation.** When a version is created, the WCI invokes the Worker once to validate. If that invocation fails — missing env vars, bad TLS/auth config, missing dependencies, or an invocation deadline too short for the Worker to start and register the Task Queue — the Worker never connects, never polls, the binding is never created, and the Worker is never automatically invoked again. *Fix:* diagnose by manually invoking the compute unit, and confirm the invocation deadline is set high.
4. **Confusing the two roles.** The compute unit's execution role (grants the function permission to run) is separate from the access Temporal uses to invoke it. Never describe one as the other. → `references/<provider>/iam.md`.
5. **Timeout tuning mismatch.** Raising only the shutdown deadline buffer makes the Worker stop polling earlier but gives in-flight Activities no more time; raising only the worker stop timeout doesn't make it stop polling earlier, so the provider may terminate the Worker first. *Fix:* tune the three values together (see the timeout triple above).
6. **Mutable "latest" build reference in production.** Pointing the provider at a mutable/unqualified target means the code changes on every redeploy; deploying replay-unsafe code then causes non-determinism errors for in-flight Workflows, even Pinned ones. *Fix:* publish an immutable versioned build and keep a 1-to-1 mapping between each Build ID and one build. → `references/<provider>/versioning.md`.
7. **Re-creating shared permission infrastructure that already exists.** *Symptom:* the infrastructure deployment fails outright and rolls back, or it succeeds and leaves a second, redundant grant behind. *Cause:* the permission grant Temporal assumes is account-wide with a fixed default name, so a previous serverless deployment already owns it. *Fix:* check whether it exists and what owns it *before* creating; extend the existing one to cover the new Worker, and fall back to a distinctly named parallel one only when the existing infrastructure is not yours to change — saying why when you do. A failed-and-rolled-back deployment must be deleted before the name can be reused; a successful one is live infrastructure and must not be. → `references/<provider>/iam.md`.
8. **Invoke permission scoped to a single build.** *Symptom:* the deployment works, then the *next* release cannot be invoked, with an error that looks like a connection or configuration problem rather than a permissions one. *Cause:* the grant named one immutable build, and the new release is a different resource. *Fix:* scope the grant to cover the base resource and all its published builds. → `references/<provider>/iam.md`.

## Routing to reference files

Most questions need 2–3 reference files.

| User intent | Reference file(s) |
|---|---|
| What is a Serverless Worker / the WCI? How do invocation and autoscaling work? What are the constraints? Serverless vs long-lived Workers? | `references/concepts.md` |
| Deploy a Serverless Worker (happy path): write code, package, deploy, register + set-current version, verify, tear down. | `references/<provider>/setup.md` (+ `references/concepts.md`) |
| Operator permissions and preflight; execution role vs Temporal invocation role; CloudFormation (Cloud + self-hosted). | `references/<provider>/iam.md` |
| Update or redeploy; version the build, use a qualified ARN, roll back. | `references/<provider>/versioning.md` (+ `references/concepts.md`) |
| Self-hosted server enablement (dynamic config, WCI, server AWS credentials). | `references/<provider>/self-hosted.md` (+ `references/<provider>/iam.md`) |
| SDK-specific options and tuned defaults, which package to install and how it is distributed, imports, versioning-behavior configuration, connection config (TOML, env vars). Reduce cold start / pre-bundle Workflow code. | `references/sdk-configuration.md` |
| Add OpenTelemetry observability, collector config, tracing. | `references/<provider>/observability.md` |
| Worker not invoked, Workflows not progressing, inspect the WCI. | `references/<provider>/diagnostics.md` (+ `references/concepts.md`) |
| Long-running Activities and timeout relationships. Isolate Activities from resource exhaustion. | `references/concepts.md` (+ `references/sdk-configuration.md`) |

## Out of Scope

- **General SDK development patterns** (Workflows, Activities, signals, queries, Worker Versioning concepts): see `skill-temporal-developer`.
- **Traditional Worker tuning** (slot suppliers, tuners, poller autoscaling, resource-based tuning): see `skill-temporal-workertuning`.
- **Temporal Cloud administration** (Namespaces, users, certificates, billing): see `skill-temporal-ops`.
- **CLI command reference** (beyond the serverless-specific flags): see `skill-temporal-cli`.
