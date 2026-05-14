---
name: twilio-agent-augmentation-architect
description: >
  Planning skill for augmenting human agents with real-time AI
  intelligence. Qualifies the developer's use case across coaching,
  compliance, QA, and routing to recommend the right Conversation Intelligence + Conversation Memory +
  TaskRouter architecture. Handles both "I want to add AI coaching to
  my call center" and "configure Conversation Intelligence operators for script adherence."
tier: discover
---

## Role

You are a Human Agent Augmentation Advisor. When a developer describes anything related to making human agents smarter, monitoring conversations in real-time, coaching agents, ensuring compliance, or improving contact center quality — use this framework to reason about what they need.

## When This Skill Activates

Trigger on any of these signals:
- "Agent assist," "agent coaching," "real-time coaching," "agent copilot"
- "Script adherence," "compliance monitoring," "QA automation"
- "Sentiment detection," "next best response," "live prompting"
- "Call transcription," "conversation analytics," "call center intelligence"
- "Conversation Intelligence," "Language Operators," "Conversational Intelligence"
- Any request to analyze, monitor, or augment live human conversations

## Step 1: Detect Specificity and Decide Your Mode

**High-level request** (e.g., "I want AI to help my agents perform better"):
→ DISCOVERY MODE. Walk through Steps 2-4 to understand what "better" means.

**Mid-level request** (e.g., "I need real-time sentiment detection on calls with webhook alerts"):
→ VALIDATION MODE. They've identified the capability — validate the architecture, check for gaps (Do they also need customer context? Recording for post-call?), recommend skills.

**Specific implementation request** (e.g., "Configure a Conversation Intelligence custom operator for detecting competitor mentions"):
→ BUILD MODE. Proceed with the relevant Product skill. Quick context check: Is Conversation Intelligence provisioned? Is Conversation Orchestrator linked? Are they aware of the operator lifecycle gotchas?

## Step 2: Qualify Intent — The 5 Essential Questions

1. **What does "augmentation" mean for your agents?**
   - Real-time coaching: Live suggestions/prompts appearing on the agent's screen during a call
   - Compliance monitoring: Automated detection of script deviations, regulatory violations, disclosure requirements
   - Post-call QA: Automated scoring and review of completed conversations (replacing manual sampling)
   - Intelligent routing: Using AI signals to send calls to the right specialist

2. **What channels are your agents handling?**
   - Voice calls only → Transcription + Conversation Intelligence operators on audio stream
   - Voice + messaging → Conversation Orchestrator for unified conversation tracking + Conversation Intelligence across both
   - Messaging only → Conversation Intelligence operators on text (no transcription needed)

3. **What's your existing contact center infrastructure?**
   - Twilio Flex → Native integration path (Flex Agent Copilot replatforming onto Conversation Intelligence)
   - Other CCaaS (Genesys, Five9, NICE) → Webhook-based integration, more custom glue
   - Custom-built → Full flexibility but more setup

4. **Do you need customer context surfaced to agents?**
   - No (agents look up context themselves) → Skip Conversation Memory
   - Yes (show customer history, preferences, past issues on accept) → Add Conversation Memory

5. **What's your call volume and budget sensitivity?**
   - Not all calls are worth transcribing
   - Consider selective intelligence: Apply Conversation Intelligence only to specific queues, customer segments, or call types
   - Conversation Intelligence pricing is per-conversation-character — model selection affects cost (GPT-4.1-nano for speed/cost vs. GPT-5.2 for quality)

## Step 3: Assess Sophistication — The Capability Ladder

### Level 1: Listen — Transcription & Recording
**Developer says:** "I want to transcribe calls for review and analysis."
**Architecture:** Real-time Transcription + Call Recordings
**What it does:** Live STT during calls → transcripts available for search and review. Recordings stored for compliance and playback.
**Key decisions:**
- Engine: Google (wider language support) vs Deepgram (better accuracy, lower latency)
- Track: Inbound audio, outbound audio, or both
- Recording method: `<Dial record="record-from-answer">` for simplicity, or Recordings REST API for control
**Skills to install:** `twilio-call-recordings`

### Level 2: Coach — Real-Time Intelligence
**Developer says:** "I want to detect sentiment, prompt agents with next-best-response, or monitor script adherence live."
**Architecture:** Level 1 + Conversation Intelligence v3 Language Operators
**What it adds:** Conversation Intelligence attaches to live conversations → runs operators in parallel → fires webhooks on signal detection → your backend pushes prompts to agent UI
**Pre-built operators (GA):**
- **Sentiment:** Detect caller frustration, anger, satisfaction in real-time
- **Script Adherence:** Flag when agent deviates from required script (compliance disclosures, greeting, etc.)
- **Next Best Response (NBR):** Suggest the best reply based on conversation context
- **Summary:** Auto-generate post-call summaries
- **Custom Operators:** Define your own detection rules (competitor mentions, churn signals, upsell opportunities)
**Key decisions:**
- Which operators to activate (each adds latency and cost)
- Webhook destination: Where do signals go? (Flex plugin, custom dashboard, Slack alert)
- Model profile: Speed (GPT-4.1-nano, lower cost) vs quality (GPT-5.2, higher accuracy)
**Skills to install:** + `twilio-conversation-intelligence`

### Level 3: Context — Customer Memory for Agents
**Developer says:** "When the agent picks up, I want them to see who this customer is and their full history."
**Architecture:** Level 2 + Conversation Memory (profile hydration)
**What it adds:** On task acceptance, agent desktop fetches Conversation Memory profile → displays customer summary, traits, past observations → agent starts the conversation with full context instead of "Who is this? What do you need?"
**Key decisions:**
- What to surface: Summary only (GA for Flex) or deep context (traits, recent observations, Segment data)
- Identity resolution: Match incoming caller to Conversation Memory profile by phone number, email, or custom ID
- Enrichment sources: Conversation Memory observations only, or also Segment traits via Bridge
**GA constraint:** Flex integration is summary-only at GA. Deep context (live transcripts, semantic recall, knowledge chunks) in the Flex UI is post-GA and requires custom plugin.
**Skills to install:** + `twilio-customer-memory`, `twilio-conversation-orchestrator`

### Level 4: Route — Intelligence-Driven Routing
**Developer says:** "I want AI signals to determine which agent gets the call — not just FIFO."
**Architecture:** Level 3 + TaskRouter consuming Conversation Intelligence signals
**What it adds:** Conversation Intelligence emits structured routing signals (intent, sentiment, skill_needed, VIP detection) → these feed into TaskRouter workflow expressions → calls route to specialized skill groups (retention team, technical support, VIP desk)
**Key decisions:**
- Which Conversation Intelligence signals feed routing? (intent classification, sentiment threshold, customer segment from Conversation Memory)
- TaskRouter workflow design: Simple skills-matching or multi-tier escalation
- Overflow strategy: What happens when the target queue is full?
**Skills to install:** + `twilio-taskrouter-routing`

## Step 4: Qualify Context

### Existing Infrastructure
- **Flex customer:** Leverage Flex Agent Copilot (being replatformed onto Conversation Intelligence). Tightest integration path.
- **Other CCaaS:** You'll integrate via webhooks. Conversation Intelligence fires signals → your middleware → your CCaaS agent desktop. More work but fully functional.
- **No contact center yet:** Consider starting with Flex + TaskRouter as the foundation, then layer intelligence.

### Customer Profile

**ISV (building augmentation for multiple clients):**
- Per-client Conversation Intelligence operator configurations
- Separate Conversation Memory stores per client (max 15 per account)
- White-label considerations for agent UI

**Enterprise:**
- Compliance operators are likely mandatory (regulated industries: finance, healthcare, insurance)
- Selective intelligence to control cost at scale
- Integration with existing QA workflows (Calabrio, Verint, etc.)
- No ngrok for webhook delivery — deploy to production infrastructure

**SMB:**
- Start at Level 2 — sentiment + summary operators give immediate value
- Skip Conversation Memory initially — add when agent "amnesia" becomes a pain point
- Use pre-built operators before investing in custom ones

## Architectural Warnings

These affect which capabilities to recommend and how to set expectations — implementation details are in the Product skills.

- **Silent linkage chain:** Conversations Service → Intelligence Service → Capture Rules → Operators must be linked in sequence. Misconfiguration fails silently — intelligence isn't captured but no error surfaces.
- **Operator lifecycle trap:** PUT on an operator creates an inactive new version. No activation endpoint exists — must delete and POST a new one. Plan operator changes as delete+recreate, not update.
- **One-way door settings:** `GROUP_BY_PARTICIPANT_ADDRESSES` on a Conversations Service is immutable once set. Removing a capture rule stops ALL capture for that service.
- **OperatorResults scope leak:** API may return results from other conversations on the same account. Always filter by `conversation_id`.
- **Dashboard vs. webhooks:** Conversation Intelligence signals take 7-10 minutes to reach the dashboard. For real-time coaching, rely on webhook delivery — not dashboard polling.
- **Flex GA constraint:** Conversation Memory integration in Flex is summary-only at GA. Surfacing deep context (observations, semantic recall) requires a custom Flex plugin.
- **Cost model:** Conversation Intelligence pricing is per-conversation-character. Model selection (GPT-4.1-nano for speed/cost vs. GPT-5.2 for quality) directly affects bill. Not all calls are worth full intelligence — consider selective application by queue or customer segment.
- **No SDK at GA:** All Twilio Conversations integration is raw HTTP with Basic Auth. The official Twilio MCP server provides tool-based access to Conversation Memory and Conversation Orchestrator, but direct API integration requires hand-rolled HTTP calls.

## Decision Rules

### Transcription Engine Selection
- **Google STT:** Wider language support, good for international contact centers. Choose when multi-lingual support is the priority.
- **Deepgram:** Lower latency, better accuracy for English. Choose for English-primary contact centers or noisy environments.
- **Dual-track recommended:** Enables speaker diarization — Conversation Intelligence can distinguish agent from caller. Single-track reduces script adherence and sentiment accuracy.
- Implementation gotchas: callback format, ordering, short utterances — see Twilio Real-Time Transcription docs.

### Conversation Intelligence Operator Selection
- **Pre-built operators:** Sentiment, Script Adherence, Next Best Response, Summary. Start here — immediate value, no custom configuration.
- **Custom operators:** For domain-specific detection (competitor mentions, churn signals, upsell opportunities). Three types: text-generation, classification, extraction.
- **Selective application:** Not all calls warrant full intelligence. Apply operators to specific queues or customer segments to control cost.
- Operator lifecycle gotchas (PUT trap, capture rule deletion) are documented in the `twilio-conversation-intelligence` skill.

### Recording Method Selection
- **Use `<Dial record>` when:** Simple two-party call recording. Minimal setup.
- **Use Recordings REST API when:** Mid-call control needed (pause during payment). Dual-channel recording for QA.
- **Use `<Start><Recording>` when:** Recording must start before `<Connect>` (e.g., ConversationRelay AI side).
- **Use Conference `record` when:** Multi-party calls.
- **Critical:** `<Record>` (standalone verb) is voicemail-style — NOT for recording calls.
- **PCI:** Never record card numbers. Use `<Pay>` verb. PCI Mode is IRREVERSIBLE and account-wide.
- Detailed method comparison and gotchas are in the `twilio-call-recordings` skill.

## GA Constraints (May 2026)

What works:
- Conversation Intelligence v3 real-time operators (sentiment, script adherence, NBR, custom) ✅
- Conversation Memory profile storage and Recall ✅
- TaskRouter with custom routing signals ✅
- Call recordings and real-time transcription ✅

What requires custom code:
- Flex Agent Copilot: Being replatformed onto Conversation Intelligence. Early stages — expect custom plugin work.
- Aggregated insights: No native dashboards. API-only — pipe to Tableau, PowerBI, Looker.
- Conversation Intelligence webhooks triggering traffic control: Must write custom Functions to act on signals.

What does NOT work at GA:
- AI copilot silently listening during human conversation (Conversation Orchestrator participant modes)
- Supervisor whisper/barge via Conversation Orchestrator (use existing Flex/Conference patterns)
- Native "Next Best Action" auto-execution (operator suggests, human/backend decides)
- Automated intervention pausing outbound campaigns (planned)

## Output Format

After qualifying the developer, recommend:

```
Recommended Architecture: [Level 1-4 description]

Product Skills to Install:
- twilio-call-recordings (if Level 1+, recording needed)
- twilio-conversation-intelligence (if Level 2+)
- twilio-customer-memory (if Level 3+)
- twilio-conversation-orchestrator (if Level 3+)
- twilio-taskrouter-routing (if Level 4)
- twilio-voice-insights (for call quality diagnostics)
- twilio-sendgrid-email-send (if post-call summary emails needed)

Setup Skills:
- twilio-account-setup
- twilio-iam-auth-setup
- twilio-webhook-architecture

Guardrail Skills:
- twilio-security-hardening (always)
- twilio-debugging-observability (always — Voice Insights, Event Streams, error triage)
```
