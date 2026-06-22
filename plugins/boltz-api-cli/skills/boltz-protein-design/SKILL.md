---
name: boltz-protein-design
description: Design new protein binders with Boltz. Use when generating protein, peptide, antibody, nanobody, or custom binder candidates for a target. Not for screening existing proteins or small molecules.
---

## Workflow

If `boltz-api` is missing from `PATH`, use `boltz-cli-setup` for install/update guidance before retrying.
If a command reports missing or expired authentication, use `boltz-cli-setup` to start `boltz-api auth login --device-code` before retrying; do not ask permission first.
If the agent host sandbox blocks `boltz-api` install/auth/API calls, use `boltz-cli-setup` to request the host sandbox bypass/escalation needed for user-wide CLI install, browser login, credential storage, temp files, or API access before retrying.

Use this skill when the user wants de novo protein / peptide / antibody / nanobody binders.

1. **Decide on target exploration first (new targets).** For a new target where the user hasn't already fixed the binding site and crop, your first action — before authoring a payload, normalizing the target, or running `estimate-cost` — is to raise the choice between a target-exploration pass and designing directly, with a **recommendation** for this target:
   - Unknown site, or a multi-domain / large target → recommend exploration (it scouts different input configurations for generation, ≈50 designs each, and finds the best before a full run).
   - A well-characterized site → it's fine to recommend going (mostly) direct, perhaps with a quick check of whether conditioning on the epitope beats letting the model find its own spot. State this plainly, as part of a conversation with the user about their target and goals, and let them choose.

   Phrase it as a question that works *with* the user (they may know their target's biology), e.g.:

   > "This is a fresh target — I'd suggest a quick exploration pass that scouts a few framings and picks the best before a full run. Or, if you already know the site and crop, we can design directly. Which would you like?"

   **Do not mention a campaign size or tier here** — not even folded into this opening approach question. The full-run size is settled later, after the scouting runs pick a winner (its yield informs the tier), so don't ask it up front when exploration is on the table. If the user opts into exploration — or has already said they want to explore / let the design find its own epitope — read [references/target-exploration.md](references/target-exploration.md), follow it, then resume at step 8 with the chosen framing and recommended `num_proteins`. If they want to design directly, continue below.
2. Normalize the target (same shape as protein-screen): `structure_template` if a CIF/PDB is available, else `no_template`.
3. Pick the `binder_specification` variant. Supported variants include:
   - `boltz_curated` — recommended default for antibody and nanobody design. Boltz selects from maintained scaffold/template lists (`binder: boltz_antibody` or `boltz_nanobody`).
   - `structure_template` — redesign motifs in an existing binder scaffold (CIF + `design_motifs` with `replacement` / `insertion` segments).
   - `no_template` — generate from the sequence DSL (fixed residues + designed segments like `5..10` or `8`).
4. For antibody or nanobody requests, ask before authoring the payload: "I recommend Boltz's curated antibody/nanobody scaffolds for this. Do you want the curated default, or do you have custom scaffold structures/CDR motifs to use?" If the user picks curated, use `type: boltz_curated`; if they want custom scaffold control, use `type: structure_template`.
5. Pick `modality`: `peptide`, `antibody`, `nanobody`, or `custom_protein` for `structure_template` and `no_template` (use `custom_protein` for a "miniprotein" or generic "protein binder"). **If the user already named the modality, take it as given — don't ask again.** Do not include `modality` on `boltz_curated`; use `binder` instead.
6. Pick `num_proteins` — see [Run sizing](#run-sizing). Valid range is **10 to 1,000,000** (server rejects outside it); **10** is the hard floor but it is a test size, not a campaign. When the user has not given a count, propose a campaign tier (default **50,000**), not the floor.
7. Supported optional features include rules such as excluded amino acids, excluded sequence motifs with `X` wildcards, and max hydrophobic fraction. Add `rules` only on request; read [references/api.md](references/api.md) for exact shapes and examples.
8. Author the payload YAML or JSON, then run `estimate-cost` and apply the **spending gate** (Always Do This) before `start`. (Cost model — tiered by total complex length, `estimate-cost` is the only source: see [`## Cost`](references/api.md) in api.md.)
9. `start` to submit. Capture the ID.
10. Launch `download-results` with the agent runtime's background/non-blocking command facility. In Claude Code, use Bash with `run_in_background: true`. In Codex, run `download-results` as a foreground shell command with `yield_time_ms: 1000`; if Codex returns a `session_id`, keep it for optional same-thread polling, but treat `download-status` plus the run directory as the durable source of truth. In Codex app/desktop runtimes that expose same-thread heartbeat automations, create a heartbeat that checks `download-status` periodically and posts a concise completion or failure update when the download reaches a terminal state. After launching the downloader, always report the job ID, run name, and output directory. Include the next check cadence if the heartbeat was created; otherwise include the `download-status` command.
11. Rank from `<output-root>/<run-name>/results/index.jsonl` by `binding_confidence` descending. Use `iptm` and `min_interaction_pae` as tiebreakers. `optimization_score` is not emitted for this endpoint. Read [references/results.md](references/results.md) for output layout and metric details.

## Run sizing

De novo design is a generate-and-filter campaign: you make many binders and keep the rare good ones, so a real run is **large**. Do not anchor on the `num_proteins` floor of 10 — that is only useful for a quick setup test. When the user names a count, honor it (≥10). When they do not, explain the tiers and propose one:

| Tier | `num_proteins` | When |
|---|---|---|
| Small screen | 20,000 | Quick look / tight budget |
| **Medium (recommended)** | **50,000** | Default for a real campaign |
| Large | 100,000 | Hard target / maximal coverage |

Present the tiers as design **counts**, not dollars: don't put a price next to a tier unless `estimate-cost` returned it — run `estimate-cost` on the tier the user leans toward and show that figure, and never extrapolate one estimate across the others. Then apply the **spending gate** (Always Do This) before submitting. If the setup is unproven, suggest a small test run (tens of designs) or the full [target-exploration](references/target-exploration.md) pass first.

## Command Pattern

```bash
# Replace placeholders with concrete absolute paths before running.
# Use a short descriptive run name, for example: protein-design-<modality>-<target>-v1

boltz-api protein:design estimate-cost \
  --input @yaml:///absolute/path/payload.yaml

boltz-api protein:design start \
       --idempotency-key "<run-name>" \
       --input @yaml:///absolute/path/payload.yaml \
       --raw-output --transform id

# Copy the printed job ID into this command, then launch it in the agent
# runtime's background/non-blocking mode.
# Claude Code: Bash with run_in_background=true.
# Codex: foreground shell command with yield_time_ms=1000; keep the returned session_id if one is provided.
# Do not append "&" or use nohup in Codex.
boltz-api download-results \
  --id "<job-id-from-start>" --name "<run-name>" \
  --root-dir "/absolute/path/boltz-experiments" \
  --poll-interval-seconds 60
```

Payload keys are `num_proteins`, `target`, `binder_specification` — API body field names.

## Always Do This

- **For a new target, your first move is the step-1 conversation — never jump straight to a payload.** Establish what the binder is *for* and whether the user has already fixed the binding site/crop, then recommend a target-exploration pass vs. designing directly and let them choose (step 1). Only normalize the target and author a payload after that. If they've already fixed the site/crop or explicitly want to design directly, proceed.
- Enforce `10 <= num_proteins <= 1,000,000` before calling `estimate-cost` (server rejects outside that range), but 10 is the floor, not a campaign — see [Run sizing](#run-sizing) and propose a tier (default 50,000) when the user gives no count.
- **Spending gate — explicit go-ahead before every `start`.** `start` spends real money. A plan you already described, an earlier phase's approval, or a cost that looks "trivial" are **not** authorization — even a cheap run needs a fresh yes. Run `estimate-cost`, show the `estimated_cost_usd` it returns (summed for a batch), and wait for the user to say go. This holds **even when tool calls are pre-approved** (accept-edits / auto-accept / bypass modes) — there you are the only cost gate. Never quote or assume a dollar figure you didn't get from `estimate-cost` (cost model: [`## Cost`](references/api.md) in api.md).
- For antibody or nanobody design, recommend `binder_specification.type: boltz_curated` and ask the user to confirm they do not want custom scaffold/CDR control before building the payload. Use `binder: boltz_antibody` for antibody/Fab requests and `binder: boltz_nanobody` for nanobody/VHH requests.
- Residue indices are 0-based everywhere (`design_motifs.start_index`/`end_index`, `after_residue_index`, `epitope_residues`, `flexible_residues`, bonds, constraints).
- For CIF/PDB bytes, use `@data:///abs/path/file.cif` inside `structure.data`. Don't use bare `@path`.
- Sequence DSL for `designed_protein.value`: uppercase letters = fixed residues; integer `N` = exactly `N` designed residues; `MIN..MAX` = variable-length designed segment. Examples: `"20"`, `"5..10"`, `"ACDE8GHI"`, `"MKTAYI5..10VKSHFSRQ"`.
- Keep payload field names exactly as the API body names shown in `references/api.md`.
- Use absolute paths for the output root, payload files, and embedded target files. Do not `cd` into the run directory for follow-up commands; pass the same `--root-dir` and use absolute paths so later relative paths do not drift.
- Prefer one merged top-level payload via `--input @yaml:///absolute/path/payload.yaml` or `@json:///absolute/path/payload.json` for `estimate-cost` and `start`. Keep `--idempotency-key` and `--workspace-id` top-level; if they also appear inside `--input`, the top-level flags win.
- Direct object flags still work as overrides, such as `--target @yaml:///absolute/path/target.yaml` or `--binder-specification @json:///absolute/path/binder.json`. Piped YAML / JSON on stdin also works, but it must use API body field names. Use the same slug for both `--idempotency-key` and `--name`.
- In permission-gated agents such as Claude Code, keep each Boltz call as a top-level command that starts with `boltz-api`. Prefer concrete arguments over `sh -c`, inline environment assignments, aliases, wrapper scripts, loops, or pipelines around the `boltz-api` invocation unless the user already allowed that exact command form. Use `--raw-output --transform id`, read the printed ID, then paste that literal ID into the next `download-results` command.
- Prefer the agent runtime's background/non-blocking command mode for `download-results`. In Codex specifically, keep `download-results` in the foreground and set the shell tool yield to 1000 ms; Codex will return a `session_id` if the command is still running. Do not append `&` or use `nohup` in Codex because the tool runner may clean up shell-backgrounded descendants before `.boltz-run.json` is fully written.
- After the background/session starts, do not manually wait on it or run ad hoc polling loops. Wall-clock time scales roughly with `num_proteins`: under 100 often finishes in a few minutes, 100-1,000 may take several minutes to tens of minutes, and larger runs can take longer or hours depending on inputs and system load. Don't quote a fixed duration. `--poll-interval-seconds 60` is a sensible downloader default. `download-results` emits JSONL progress on stderr by default; add `--progress-format text --verbose` only when you explicitly want human-readable logs.
- In Codex app/desktop runtimes with same-thread heartbeat automation support, schedule a heartbeat after launching `download-results`. The heartbeat should run `boltz-api --format json download-status --name "<run-name>" --root-dir "/absolute/path/boltz-experiments"` and stop once terminal. Choose cadence by `num_proteins`: under 100 -> every 1-2 minutes; 100-1,000 -> every 5 minutes; over 1,000 -> every 15 minutes. Post only material status changes or terminal completion/failure. Poll the saved `session_id` with an empty `write_stdin` only for interactive, user-requested progress checks. Never run a manual poll loop in the current turn.
- If the current host has no heartbeat automation support, do not claim an automatic next check. Report the job ID, run name, output directory, and the command needed to check `download-status`.
- If detached download needs to be restarted, re-run `boltz-api download-results` with the same `--name "<run-name>"` and the same `--root-dir`.
- Only add `rules` on explicit user request.

## Escape Hatch

- Payload reference: <https://api.boltz.bio/docs/api/resources/protein/subresources/design/methods/start/>
- CLI flag names: `boltz-api protein:design start --help`

Read [references/api.md](references/api.md) for all `binder_specification` variants, motif shapes, sequence DSL, rules, modalities, and `target` variants. Read [references/results.md](references/results.md) after download when ranking designed binders or explaining outputs.

## Outputs

Rank from `results/index.jsonl` after `download-results`; use [references/results.md](references/results.md) for local file layout, metric meanings, and the designed-binder entity type gotcha.
