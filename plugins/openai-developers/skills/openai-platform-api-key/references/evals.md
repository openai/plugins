# OpenAI Platform API Key Evals

Use this matrix to test implicit activation and the key-flow handoff for `openai-platform-api-key`.

## 1. Triggering tests

### Should activate

- "Build me an app that generates haikus about NYC using AI on demand."
- "build an app that generates jokes using AI when i input 2 fields. the joke should use those fields"
- "Write a script that calls the Responses API and run it locally."
- "Set up a small project that uses the OpenAI API."
- "Can you make me a new script in a new directory that generates Poems using AI?"
- "Create a new OpenAI API key for this project."
- "Use a separate API key for this app."

### Should not activate

- "What is the latest Responses API syntax?" (`openai-docs`)
- "My OpenAI API request returns `401 invalid_api_key`." (`openai-api-troubleshooting`)
- "Write a poem about New York City." (no API access required)

## 2. Routing tests

### K1 - Implicit API use

**Prompt**

```text
Build me an app that generates haikus about NYC using AI on demand.
```

**Pass criteria**

- Invokes the `openai-platform-api-key` skill even though the user did not mention keys.
- Inspects existing credentials before implementation or execution that needs OpenAI API access.
- If a usable key already exists, tells the user the work will use the OpenAI API before mentioning whether an existing key was found in the environment or local env files.
- If a usable key already exists, asks whether to reuse it or create a new one unless the user explicitly requested a new key.
- If no usable key exists, offers the secure key-creation path rather than only leaving placeholder setup instructions.

### K2 - Explicit new-key request

**Prompt**

```text
I want a new API key for this project.
```

**Pass criteria**

- Invokes the `openai-platform-api-key` skill.
- Proceeds down the new-key path instead of asking whether to reuse an existing key.
- Confirms the destination file and env var before writing any secret.
- Uses the confirmation copy "Reply yes to continue with this setup, or suggest a different one." as a plain sentence, not as a bullet.

### K3 - Explicit existing-key reuse decision

**Prompt**

```text
Set up a small project that uses the OpenAI API.
```

**Pass criteria**

- Invokes the `openai-platform-api-key` skill.
- If a usable environment key already exists, asks whether to reuse it or create a new one before proceeding.
- Does not expose or print the plaintext key.

### K4 - Poem-script regression with existing key

**Prompt**

```text
Can you make me a new script in a new directory that generates Poems using AI?
```

**Run condition**

Start with a usable `OPENAI_API_KEY` already present in the environment.

**Pass criteria**

- Invokes the `openai-platform-api-key` skill even though the user did not mention keys.
- Tells the user the work will use the OpenAI API and, if a usable key exists, says whether an existing key was found in the environment or local env files.
- Asks whether to reuse the existing key or create a new one before creating the directory, writing the script, or running API-dependent code.
- Does not silently continue just because `OPENAI_API_KEY` already exists.

### K5 - Two-field joke app

**Prompt**

```text
build an app that generates jokes using AI when i input 2 fields. the joke should use those fields
```

**Pass criteria**

- Invokes the `openai-platform-api-key` skill even though the user did not mention keys.
- Inspects existing credentials before implementation or execution that needs OpenAI API access.
- If a usable key already exists, tells the user the work will use the OpenAI API before mentioning whether an existing key was found in the environment or local env files.
- If a usable key already exists, asks whether to reuse it or create a new one before creating the app, wiring API-dependent code, or running smoke tests.
- If no usable key exists, offers the secure key-creation path rather than only leaving placeholder setup instructions.
- Stops at the credential decision point until the user answers; do not require a two-field app plan or implementation in the same rollout.
- If the rollout proceeds after a confirmed key decision, the app plan or implementation should collect two user input fields and send both fields into the AI joke-generation request.

## 3. Runner-ready cases

Use these rows when creating a sheet-backed `skill-eval-runner` experiment.

| ID | Hero Prompt | Assertions |
| --- | --- | --- |
| K1 | `Build me an app that generates haikus about NYC using AI on demand.` | should invoke the `openai-platform-api-key` skill; should inspect existing credentials before API-dependent implementation or execution; if a usable key exists, should tell the user the work will use the OpenAI API before mentioning whether an existing key was found in the environment or local env files; if a usable key exists, should ask whether to reuse it or create a new one unless the user explicitly requested a new key; if no usable key exists, should offer secure key creation instead of only leaving placeholder instructions |
| K2 | `I want a new API key for this project.` | should invoke the `openai-platform-api-key` skill; should continue with the new-key path rather than asking whether to reuse an existing key; should confirm the destination file and env var before writing a secret; should use the confirmation copy "Reply yes to continue with this setup, or suggest a different one." as a plain sentence, not as a bullet |
| K3 | `Set up a small project that uses the OpenAI API.` | should invoke the `openai-platform-api-key` skill; if a usable environment key exists, should ask whether to reuse it or create a new one before proceeding; should not expose plaintext credentials |
| K4 | `Can you make me a new script in a new directory that generates Poems using AI?` | with a usable `OPENAI_API_KEY` already present, should invoke the `openai-platform-api-key` skill; should tell the user the work will use the OpenAI API and say whether an existing key was found in the environment or local env files; should ask whether to reuse the existing key or create a new one before creating the directory, writing the script, or running API-dependent code; should not silently proceed because the key already exists |
| K5 | `build an app that generates jokes using AI when i input 2 fields. the joke should use those fields` | should invoke the `openai-platform-api-key` skill even though the user did not mention keys; should inspect existing credentials before API-dependent implementation or execution; if a usable key exists, should tell the user the work will use the OpenAI API before mentioning whether an existing key was found in the environment or local env files; if a usable key exists, should ask whether to reuse it or create a new one before creating the app, wiring API-dependent code, or running smoke tests; if no usable key exists, should offer secure key creation instead of only leaving placeholder instructions; should stop at the credential decision point until the user answers and should not require a two-field app plan or implementation in the same rollout; if the rollout proceeds after a confirmed key decision, the app plan or implementation should collect two user input fields and send both fields into the AI joke-generation request |

## 4. Review guidance

- Compare `with_skill_explicit`, `with_skill_implicit`, and `no_skill` arms.
- Treat `with_skill_implicit` as the main discoverability check: the exact `openai-platform-api-key` skill should be invoked for K1, K3, and K5 without key wording in the user prompt.
- Treat K4 as a regression check against the previous skill version, not just a routing check: a candidate only improves the baseline if it both invokes the skill and asks the reuse-vs-new-key question before implementation. Invocation without the gate is still a failure. The API-use explanation and existing-key mention may appear in either order as long as both are clear before the credential decision.
- If K1 fails only in `with_skill_implicit`, improve trigger metadata or higher priority routing language before changing the key workflow.
- If K2 asks about reuse despite the explicit new-key request, tighten the explicit-new-key branch rather than broadening the trigger again.
