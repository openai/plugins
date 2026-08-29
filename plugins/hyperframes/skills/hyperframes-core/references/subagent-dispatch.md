# Subagent dispatch — harness adapter

The video workflows (`product-launch-video` / `faceless-explainer` / `pr-to-video` / `motion-graphics` / `general-video`) describe subagent dispatch in harness-neutral verbs. This file maps those verbs to the primitives of whatever agent harness you are running on. Read it once per run, before the first dispatch; everything else in the workflows (dispatch packets, file artifacts, exit-code gates, Resume tables) is harness-independent and needs no translation.

## The contract (identical on every harness)

- **DISPATCH(role_file, dispatch_context)** — start one child agent whose prompt is the **full contents of the named `agents/<role>.md` file** followed by the `## Dispatch context` block from the workflow, copied **verbatim** (never digested or paraphrased). Every harness below accepts arbitrary task text, so this works everywhere; never rely on the child seeing your conversation, memory, or skills — the prompt and the files on disk are its entire world.
- **Parallel fan-out** — when a step says "start N workers in parallel", the workers are mutually independent (no ordering, no shared state beyond the filesystem). Run as many concurrently as your harness allows.
- **WAIT** — a step's completion criterion is always **the expected artifact existing on disk** (e.g. `compositions/<scene-id>.html`), never the harness's completion notification (some harnesses deliver results best-effort). After waiting, verify the artifacts; a missing artifact means that child failed — re-dispatch it once with the same prompt before surfacing an error.

## Concurrency cap → batching rule (cap never changes scope)

A harness concurrency limit **reduces parallelism, not work**: every scene still gets built, one scene per dispatch, with the available slots chewing through the full list.

- Harness queues excess children internally → submit **all N at once** and let the queue drain.
- Harness hard-caps active children → dispatch in **waves of the cap size**: start `cap` workers, wait for their artifacts, start the next wave, until all N scenes exist. Example: 9 scenes on a cap-3 harness = 3 waves of 3 — never drop scenes, never merge scenes into one worker to fit the cap.

## Primitive map

| Verb in the workflows            | Native worker/subagent support                                      | Headless CLI fallback                                                                        | Inline fallback                                                                 |
| -------------------------------- | ------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| DISPATCH                         | Start one worker with the role file + dispatch context as its prompt | Write the prompt to a file and start one child process per worker                             | Read the role file yourself and perform the worker pass serially                 |
| parallel fan-out                 | Submit workers concurrently up to the runtime's supported limit      | Start background child processes up to the local concurrency limit                             | Process one worker prompt at a time                                              |
| WAIT                             | Wait for worker completion, then verify artifacts on disk            | Wait for child processes to exit, then verify artifacts on disk                                | Verify each artifact before moving to the next worker                            |
| default concurrency              | Use the runtime default unless the user/workspace specifies a cap     | Use a conservative local cap; reduce it if the machine becomes resource constrained            | 1                                                                               |
| re-dispatch after a gate failure | Start a replacement worker with the same prompt + repair context     | Start a replacement child process with the same prompt + repair context                        | Re-run that role pass yourself with the same prompt + repair context             |

Runtime notes:

- If native worker/subagent execution requires explicit user approval, ask before the first dispatch. A skill instruction alone is not approval.
- Children must share the parent `PROJECT_DIR` filesystem. Remote or containerized children that cannot read/write the same project directory are not suitable for these workflows.
- If native subagents are unavailable or disabled, degrade down this ladder:
  1. Headless CLI children: write each child prompt to a file, start the CLI per worker as a background shell process (redirect stdin from /dev/null, output to a log), then collect artifacts from disk.
  2. Inline serial execution: do each role yourself, one at a time — read the role file, follow it with the dispatch context as if you were the child, finish, then return to the runbook. Load only one role's resources at a time (a scene's role file + its packet), and still run every per-role self-check before moving on.

## Vocabulary mapping (older phrasing you may meet in agent prompts)

- "in the same message" / "run in background" — read as "concurrently / as a background child"; apply your runtime's equivalent from the table.
- "Skill `X`" / "loaded with the Skill tool" — load skill X; on runtimes without a skill-loading tool, read `<skills-root>/X/SKILL.md` directly (the skills root is the directory containing this skill family; derive it from `SKILL_DIR` in your dispatch context).
- `Read` / `Write` / `Edit` / `Bash` — capability names (read file / write file / edit in place / run shell); map to your harness's tools.
