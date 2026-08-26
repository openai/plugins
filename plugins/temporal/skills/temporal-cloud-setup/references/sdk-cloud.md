# Per-SDK: Cloud-ready Sample Repo, Branch, Task Queue, and How It Connects

For the chosen SDK: clone the **`money-transfer-project-cloud-setup`** branch, install deps, then run the Worker and the starter. **The branch is pre-wired for Cloud — there is no connection edit.**

> **Note:** the clone + deps install are done by `scripts/provision.sh provision-and-scaffold`, and the Worker + starter run is done by `scripts/provision.sh run-workflow --sdk <sdk> --dir <repo_path>` — a single synchronous call that starts the Worker, waits until it's polling (Temporal API, not `ps`/`pgrep`), runs the starter, and stops the Worker. The per-SDK repo, task queue, and run commands below are the **source of truth the script encodes** — they are reference, not commands you run by hand.

How each branch connects: **all six SDKs load the named `cloud-setup` profile from `temporal.toml`** (env-config), so the key stays in the locked `0600` file — never in source, argv, or shell history. Step 6 writes that profile; nothing else is needed at run time. *(Verify the SDK's env-config symbol against current docs before relying on it.)*

All connection values come from the **`cloud-setup` profile** in the TOML written in Step 6 (never `default`):
- `address`  = the **namespace endpoint** = the handle + `.tmprl.cloud:7233`, e.g. `<namespace-handle>.tmprl.cloud:7233` (region-agnostic, works with API keys — **not** the regional `<region>.<provider>.api.temporal.io:7233`)
- `namespace` = `<namespace-handle>`
- `api_key`  = the one-time key

TLS is required for Temporal Cloud (the `cloud-setup` profile / env-config carries it). Worker and starter must use the **same task-queue name** (already set in the sample — do not change it).

## Quick table

| SDK | Repo (branch `money-transfer-project-cloud-setup`) | Task queue | Connects via |
|-----|------|-----------|--------------|
| Python | `money-transfer-project-template-python` | `TRANSFER_MONEY_TASK_QUEUE` | `cloud-setup` profile (env-config) |
| Go | `money-transfer-project-template-go` | `TRANSFER_MONEY_TASK_QUEUE` | `cloud-setup` profile (env-config) |
| TypeScript | `money-transfer-project-template-ts` | `money-transfer` | `cloud-setup` profile (env-config) |
| Java | `money-transfer-project-java` | `MONEY_TRANSFER_TASK_QUEUE` | `cloud-setup` profile (env-config) |
| .NET | `money-transfer-project-template-dotnet` | `MONEY_TRANSFER_TASK_QUEUE` | `cloud-setup` profile (env-config) |
| Ruby | `money-transfer-project-template-ruby` | `money-transfer` | `cloud-setup` profile (env-config) |

The per-SDK sections below give **install + run** commands. The connection code they show is **reference only** — the cloud branch already contains it; you do not edit it.

---

## Python

Install: `python3 -m venv env && source env/bin/activate && python -m pip install temporalio`

Connects via the `cloud-setup` profile (already in the branch — no edit): `ClientConfigProfile.load("cloud-setup")` → `Client.connect(**profile.to_client_connect_config())` (`temporalio.envconfig`), in `run_worker.py` and `run_workflow.py`.

Run (activate the venv in each shell): `source env/bin/activate && python run_worker.py` (Worker) then `source env/bin/activate && python run_workflow.py` (starter).

---

## Go

Install: `go version` (deps via `go.mod`).

Connects via the `cloud-setup` profile (already in the branch — no edit): `envconfig.LoadClientOptions(LoadClientOptionsRequest{ConfigFileProfile:"cloud-setup"})` → `client.Options` (`go.temporal.io/sdk/contrib/envconfig`), in `worker/main.go` and `start/main.go`.

Run: `go run worker/main.go` then `go run start/main.go`.

---

## TypeScript

Install: `npm install`.

Connects via the `cloud-setup` profile (already in the branch — no edit): `loadClientConnectConfig({profile:'cloud-setup'})` (`@temporalio/envconfig`) drives both `NativeConnection` (worker, `src/worker.ts`) and `Connection` (client, `src/client.ts`).

Run: `npm run worker` (= `ts-node src/worker.ts`) then `npm run client` (= `ts-node src/client.ts`). (Verified against the `money-transfer-project-cloud-setup` branch's `package.json`.)

---

## Java

Build: Maven (`pom.xml`); the run targets compile on demand.

Connects via the `cloud-setup` profile (already in the branch — no edit): `ClientConfigProfile.load(...setConfigFileProfile("cloud-setup"))` → `toWorkflowServiceStubsOptions()` / `toWorkflowClientOptions()` (`io.temporal.envconfig`), in `MoneyTransferWorker.java` and `TransferApp.java`.

Run (Maven, verified against the cloud-setup branch's `Makefile`): worker `mvn compile exec:java -Dexec.mainClass="moneytransferapp.MoneyTransferWorker"` (`make worker`), then starter `mvn compile exec:java -Dexec.mainClass="moneytransferapp.TransferApp"` (`make run`).

---

## .NET

Install: `dotnet --version`.

Connects via the `cloud-setup` profile (already in the branch — no edit): `ClientEnvConfig.LoadClientConnectOptions(new ProfileLoadOptions{Profile="cloud-setup"})` → `TemporalClientConnectOptions` (`Temporalio.Common.EnvConfig`), in `MoneyTransferWorker/Program.cs` and `MoneyTransferClient/Program.cs`.

Run: `dotnet run --project MoneyTransferWorker` then `dotnet run --project MoneyTransferClient`.

---

## Ruby

Install: `bundle install`.

Connects via the `cloud-setup` profile (already in the branch — no edit): `Temporalio::EnvConfig::ClientConfig.load_client_connect_options(profile:'cloud-setup')` → `Client.connect(*args, **kwargs)`, in `worker.rb` and `starter.rb`.

Run: `ruby worker.rb` then `ruby starter.rb`.

---

## Package managers & minimum versions

`scripts/provision.sh detect-tools --sdk <sdk>` reports which managers are **supported by the sample
AND installed**, picks a deterministic default (first available in preference order; the lockfile's
manager leads when one is committed), and flags version discrepancies. `install_cmd_for` /
`install-deps` in `provision.sh` are the single source of truth for the install commands below.

**Only Python and TypeScript ship a real manager choice.** This was confirmed by auditing the
`money-transfer-project-cloud-setup` branch of each sample repo (Step 0): the Python sample ships
**no** dependency manifest (`pip install temporalio` only — so `poetry` is not offered), and the
TypeScript sample commits `package-lock.json` (so `npm` leads). The other four SDKs are single-toolchain.

| SDK | Managers (default first) | Install command (per manager) |
|-----|--------------------------|-------------------------------|
| python | **pip**, uv | pip: `python3 -m venv env && . env/bin/activate && python -m pip install -q temporalio` · uv: `uv venv env && . env/bin/activate && uv pip install -q temporalio` |
| ts | **npm**, pnpm, yarn | npm: `npm install` · pnpm: `pnpm install` · yarn: `yarn install` |
| go | go | `go mod download` |
| java | maven | `mvn -q -DskipTests dependency:resolve` (the run targets also compile on demand) |
| dotnet | dotnet | `dotnet restore` |
| ruby | bundler | `bundle install` |

**Minimum versions (advisory — a shortfall is a `version-too-old` warning + remediation, never a hard block):**

| Tool | Min | Tool | Min |
|------|-----|------|-----|
| python3 | 3.8 | uv | 0.1 |
| node | 18 | npm | 8 |
| go | 1.21 | pnpm | 8 |
| java (JDK) | 8 | yarn | 1.22 |
| dotnet | 6.0 | maven | 3.6 |
| ruby | 3.0 | bundler | 2.0 |

Java reports its version with the legacy `1.8.x` scheme for JDK 8; `detect-tools` maps `1.N` to `N`
so JDK 8 is treated as 8 (not flagged below the JDK-11 line some tools assume — the Temporal Java
SDK supports JDK 8, so 8 is the intended floor).

## Notes

- If unsure of the exact env-config symbol for the installed SDK version, check the SDK's current "connect to Temporal Cloud" / env-config docs or the sample repo's README.
- The `address` is the namespace endpoint (`<namespace-handle>.tmprl.cloud:7233`) — built directly from the handle that `namespace create` returns, **not** the Web UI URL and **not** reconstructed via `namespace get -o json` (which returns empty on this prerelease). `scripts/provision.sh create-namespace` derives and returns it as `address`.