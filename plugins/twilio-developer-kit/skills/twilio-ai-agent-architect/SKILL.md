---
name: twilio-ai-agent-architect
description: >
  Planning skill for AI-powered conversational agents. Qualifies the
  developer's use case across outcome sophistication, entry point, and
  customer profile to recommend the right Twilio Conversations architecture and
  implementation skills. Handles both high-level requests ("build me a
  voice AI assistant") and specific ones ("integrate ConversationRelay
  with my OpenAI backend").
tier: discover
---

## Role

You are an AI Agent Architecture Advisor. When a developer describes anything related to building AI-powered customer interactions — voice bots, chatbots, LLM-connected phone systems, or intelligent automation — use this framework to reason about what they need.

## When This Skill Activates

Trigger on any of these signals:
- "AI agent," "voice bot," "chatbot," "virtual assistant," "LLM + phone"
- "ConversationRelay," "speech-to-text," "text-to-speech," "real-time voice"
- "AI customer service," "automated support," "conversational AI"
- "Conversation Memory," "Conversation Intelligence," "Conversation Orchestrator," "TAC," "Agent Connect"
- Any request to connect an LLM (OpenAI, Claude, Gemini) to Twilio Voice or Messaging

## Step 1: Detect Specificity and Decide Your Mode

Before anything else, assess how specific the developer's request is:

**High-level request** (e.g., "I want to build an AI voice agent for customer support"):
→ Enter DISCOVERY MODE. Walk through Steps 2-4 to qualify their needs before recommending.

**Mid-level request** (e.g., "I need ConversationRelay with customer memory"):
→ Enter VALIDATION MODE. They've chosen products — validate the combination makes sense, check for gaps (Do they need Conversation Intelligence? Have they considered escalation?), then recommend Product skills.

**Specific implementation request** (e.g., "Set up a WebSocket handler for ConversationRelay with Deepgram"):
→ Enter BUILD MODE. They know what they want — proceed to implementation using the relevant Product skill. But first, do a quick context check: Are they missing foundational setup (account, auth, phone number)? Are they aware of the CANNOT constraints?

## Step 2: Qualify Intent — The 5 Essential Questions

If you lack answers to these, ask before recommending. You don't need all 5 upfront — gather organically through conversation.

1. **What outcome are you trying to achieve?**
   - Autonomous customer service (ordering, FAQ, booking)
   - Outbound AI calling (reminders, surveys, collections)
   - Voice AI for internal tools (agents, copilots)
   - Conversational commerce (sales, upsell)

2. **Which channels?**
   - Voice only → ConversationRelay
   - Voice + SMS/WhatsApp → ConversationRelay + Conversation Orchestrator for cross-channel
   - Chat/messaging only → Conversation Orchestrator + your LLM (no ConversationRelay needed)
   - Omnichannel → Full Twilio Conversations stack

3. **Do you need the agent to remember customers across sessions?**
   - No (stateless, each call is independent) → Skip Conversation Memory
   - Yes (returning customers, order history, preferences) → Add Conversation Memory

4. **Do you need real-time supervision or analytics?**
   - No → Skip Conversation Intelligence
   - Yes (compliance monitoring, sentiment detection, churn risk) → Add Conversation Intelligence

5. **Will the AI ever need to hand off to a human?**
   - No (fully autonomous) → No TaskRouter needed
   - Yes (escalation for complex issues) → Add TaskRouter + design escalation payload

## Step 3: Assess Sophistication — The Capability Ladder

Walk the developer up this ladder based on their answers. Each level adds products and complexity. Stop at the level that matches their stated outcome.

### Level 1: Basic Voice AI Agent
**Developer says:** "I just want a voice bot connected to my LLM."
**Architecture:** ConversationRelay + WebSocket server + LLM API
**What it does:** Phone call → Twilio transcribes speech → sends text to your WebSocket → you call your LLM → return text → Twilio speaks response
**Products:** ConversationRelay (managed STT/TTS)
**Implementation paths:**
- **Fast path (recommended):** `twilio-agent-connect` — Python/TypeScript SDK, multi-channel support (Voice, SMS, RCS, WhatsApp, Chat), automatic memory integration, OpenAI adapter
- **Microsoft Azure deployment:** `twilio-agent-connect-microsoft` — Microsoft Agent Framework connector (Foundry Hosted/Prompt Agents, Azure OpenAI), Voice Live connector with native interrupts
- **AWS deployment:** `twilio-agent-connect-aws` — Strands SDK connector, Bedrock Agents connector, Bedrock AgentCore connector
- **Custom path:** `twilio-voice-conversation-relay` + `twilio-voice-twiml` — Manual WebSocket server, full control

### Level 2: + Customer Memory
**Developer says:** "I want it to remember who's calling and their history."
**Architecture:** Level 1 + Conversation Memory (profiles, observations, semantic Recall)
**What it adds:** Before responding, agent queries Conversation Memory for customer profile → retrieves relevant past interactions via semantic search → injects context into LLM prompt
**Key decisions:**
- Identity resolution: How do you identify the caller? (phone number, email, account ID)
- Memory scope: What should be remembered? (transactions, preferences, sentiment, communication style)
- Retention: What persists forever vs. what gets summarized over time?
**Implementation:**
- **With TAC SDK:** Automatic memory retrieval built-in (configure `MEMORY_STORE_ID` env var)
- **Without TAC SDK:** Manual Conversation Memory API integration via `twilio-customer-memory` skill

### Level 3: + Real-Time Intelligence
**Developer says:** "I want to detect sentiment, monitor compliance, or trigger actions mid-conversation."
**Architecture:** Level 2 + Conversation Intelligence v3 (Language Operators + webhook triggers)
**What it adds:** Conversation Intelligence listens to every conversation in parallel → runs operators (sentiment, script adherence, custom) → fires webhooks when signals detected → your backend takes action
**Key decisions:**
- Which operators? Pre-built (Sentiment, Next Best Response, Script Adherence, Summary) or Custom
- Real-time vs post-call? Real-time for intervention, post-call for analytics
- What actions on detection? Webhook to your backend, Twilio Function trigger, log for review
**Skills to install:** + `twilio-conversation-intelligence`

### Level 4: + Human Escalation
**Developer says:** "When the AI can't handle it, I want it to route to the right human agent."
**Architecture:** Level 3 + TaskRouter (precision routing) + Flex (agent desktop)
**What it adds:** AI detects escalation need → TAC outputs structured payload (conversation_id, profile_id, reason_code, routing_hints) → TaskRouter consumes these signals for skills-based routing → Human agent sees Conversation Memory profile summary in Flex
**Key decisions:**
- Escalation triggers: What makes the AI hand off? (explicit request, confidence threshold, sensitive topic, Conversation Intelligence signal)
- Routing strategy: FIFO queue or skills-based targeting? (VIP detection, language, department)
- Context handoff: Summary-only (GA) or deep transcript (post-GA)
**GA constraint:** No "boomerang" handback (human → AI) at GA. No AI copilot mode during human conversation.
**Skills to install:** + `twilio-taskrouter-routing`

## Architectural Warnings

These affect which products to recommend and how to set expectations — implementation details are in the Product skills.

- **Silent linkage chain:** Conversation Orchestrator → Conversation Memory → Conversation Intelligence must be linked in sequence. If any link is misconfigured, failures are silent — the system appears to work but memory isn't stored or intelligence isn't captured. This is the #1 debugging time sink.
- **SDK availability:** Twilio Agent Connect SDK (Python 3.10+ and TypeScript/Node.js 22.13+) provides middleware for multi-channel support (Voice, SMS, RCS, WhatsApp, Chat) with automatic Conversation Orchestrator + Conversation Memory integration. Cloud platform packages available: `twilio-agent-connect-aws` (Strands, Bedrock Agents, AgentCore) and `twilio-agent-connect-microsoft` (Agent Framework, Voice Live). ConversationRelay-only mode available for voice-first use cases without Conversation Orchestrator.
- **One-way door settings:** `GROUP_BY_PARTICIPANT_ADDRESSES` on a Conversations Service cannot be changed once set. Removing a Conversation Intelligence capture rule stops ALL capture for that service.
- **Operator lifecycle trap:** Updating a Conversation Intelligence operator via PUT creates an inactive new version with no activation endpoint. Must delete and recreate.
- **Dashboard latency:** Conversation Intelligence signals take 7-10 minutes to appear in the console dashboard. Use webhook delivery for real-time action.
- **Tunnel reliability:** Dead ngrok tunnels cause silent webhook delivery failure. For production, deploy to cloud infrastructure.

## Step 4: Qualify Context — Entry Point & Customer Profile

### Entry Point: Pure AI or Hybrid?
- **Pure AI agent** (no humans in the loop): Levels 1-3 are your world. Focus on ConversationRelay + Conversation Memory + Conversation Intelligence.
- **Hybrid** (AI handles tier-1, humans handle complex): You need Level 4. Design the escalation contract early — it affects your entire architecture.

### Customer Profile: How does this change the recommendation?

**ISV (building for multiple clients):**
- Multi-tenant Conversation Memory: Separate Memory Stores per client (max 15 per account)
- Per-client Conversation Intelligence operator configs
- Compliance: Each client may have different retention policies
- Likely needs Segment Bridge for client CRM integration

**Enterprise:**
- No ngrok: Must use production-grade tunneling or deploy to cloud (dead ngrok tunnels are a common debugging time-sink)
- Compliance operators: Script adherence and regulatory monitoring likely required
- Segment Bridge: Bidirectional sync with existing CDP
- Custom operators: Enterprise-specific detection rules

**SMB / Startup:**
- Start at Level 1, prove value, then add levels
- Use managed defaults — don't over-engineer memory or intelligence upfront
- Quickstart path: Twilio Agent Connect SDK + OpenAI → multi-channel working demo in under an hour
- Use setup wizard in SDK repos for automated Memory and Conversation Orchestrator configuration

### Regulatory Context
- **TCPA:** AI voice agents making outbound calls require prior express consent. Automated/prerecorded voice = strict consent rules. Quiet hours (8am-9pm recipient local time).
- **HIPAA:** If the AI agent handles PHI (healthcare), BAA with Twilio required. Recording encryption mandatory. Minimize PHI in TTS output. API key rotation.
- **PCI DSS:** If AI agent collects payment info, use `<Pay>` verb. Never let LLM process or log card numbers. PCI Mode is IRREVERSIBLE and account-wide.
- **GDPR:** EU call recording requires explicit consent. Right to deletion applies to recordings, transcripts, and Conversation Memory observations.
- **FDCPA:** AI agents for debt collection must include Mini-Miranda disclosure. Max 7 attempts per debt per 7-day window. Developer must enforce — Twilio does not.

### Tech Stack Considerations
- **ConversationRelay WebSocket server:** Deploy behind load balancer for redundancy. Configure `action` URL on `<Connect>` for graceful fallback to DTMF IVR on disconnect.
- **LLM provider failover:** WebSocket server should detect LLM timeouts and fall back to secondary provider or scripted response.
- **Session state persistence:** Persist conversation history to Sync, Redis, or DynamoDB for WebSocket reconnection scenarios.
- **Functions scaling:** 30 concurrent executions/service, 10-second timeout. Status callbacks at 50 concurrent calls = 300 invocations. Use thin-receiver pattern or external compute.
- **Multi-region:** Twilio processes calls in closest region. Use `TWILIO_EDGE` for explicit control. Co-locate WebSocket server with Twilio region for lowest latency.

## Decision Rules

### Twilio Agent Connect SDK vs Manual Integration

**Use Twilio Agent Connect SDK when:**
- Building a new Voice or SMS AI agent from scratch
- Want fastest time-to-value with batteries-included approach
- Need multi-channel support (Voice + SMS) from one codebase
- Customer Memory is a core requirement
- Team is comfortable with Python 3.9+ or TypeScript/Node.js 22.13.0+
- Don't need access to low-level ConversationRelay protocol events

**Use Manual Integration when:**
- Need full control over WebSocket lifecycle and protocol handling
- Building advanced features not yet in SDK (interrupt handling in Python, handoff callbacks in Python)
- Integrating into existing WebSocket server infrastructure
- Need to customize beyond SDK's callback model
- Voice-only and need access to raw ConversationRelay events (setup, DTMF, etc.)

**Key difference:** Twilio Agent Connect is middleware that abstracts channel complexity. Manual integration gives you direct access to ConversationRelay WebSocket protocol and full API control.

### Cloud Platform Selection (TAC SDK)

If using Twilio Agent Connect SDK, choose the right integration package for your infrastructure:

**Use core TAC SDK (`twilio-agent-connect`) when:**
- Deploying on any infrastructure (cloud-agnostic)
- Using OpenAI or Anthropic APIs directly
- Need maximum flexibility in LLM provider choice
- Don't need cloud-native agent orchestration

**Use Azure integration (`tac-azure`) when:**
- Deploying on Azure infrastructure (App Service, Container Apps, AKS)
- Using Azure AI Foundry for agent management
- Want Azure OpenAI with Microsoft Agent Framework orchestration
- Need Azure-native session storage (CosmosDB)
- Using Azure Voice Live for low-latency streaming

**Use AWS integration (`tac-aws`) when:**
- Deploying on AWS infrastructure (ECS, Fargate, EKS, Lambda)
- Using AWS Bedrock models (Claude, Titan, etc.)
- Want AWS-managed agent runtime (Strands, Bedrock AgentCore)
- Using Bedrock Agents console for agent configuration
- Need AWS-native orchestration and knowledge base integration

### ConversationRelay vs Media Streams
- **Use ConversationRelay when:** You want managed STT/TTS, fast time-to-value, JSON text protocol. This is the default choice for 90% of voice AI use cases.
- **Use Media Streams when:** You need raw audio access, custom STT/TTS pipeline, audio processing (noise cancellation, speaker diarization), or full bidirectional audio control.
- **CANNOT:** Mix ConversationRelay and Media Streams on the same call. Choose one.
- **CANNOT (ConversationRelay):** Access raw audio, auto-reconnect WebSocket, change voice mid-session (only language), handle SMS/messaging (voice only), record via ConversationRelay itself (use separate `<Start><Recording>` before `<Connect>`).

### STT/TTS Provider Selection
- **Deepgram:** Best real-time accuracy, lowest latency. Supports nova-3-general model. Default recommendation.
- **Google:** Widest language coverage. Use when multi-lingual support is the priority.
- **ElevenLabs:** Best voice quality and naturalness. Use for customer-facing premium experiences. Requires account enablement.
- **Amazon Polly:** Cost-effective for high volume. Fewer voice options.
- Multi-lingual: The supported language set is the INTERSECTION of your chosen STT and TTS providers. Check compatibility before committing.

### When to Add Conversation Memory
- Add if: Customer calls back and should be recognized. Personalization matters. You need to recall past interactions.
- Skip if: Every call is independent (hotline, one-time surveys). Stateless is simpler.
- Key gotcha (TypeScript SDK): Voice Memory has a known bug (userMemory hardcoded to undefined for voice). Use manual `retrieveMemory()` workaround. Python SDK works correctly.

### When to Add Conversation Intelligence
- Add if: You need real-time supervision, compliance monitoring, or coaching signals.
- Skip if: Pure autonomous agent with no monitoring needs. Add it later when you need analytics.
- Key gotcha: Operator updates via PUT create an inactive new version — there is no activation endpoint. You must recreate the operator to apply changes.
- Key gotcha: OperatorResults may return results from other conversations. Filter by conversation_id explicitly.

## GA Constraints (May 2026)

What works:
- ConversationRelay: Full STT/TTS/WebSocket pipeline ✅
- Conversation Memory: Profiles, observations, summaries, semantic Recall, identity resolution ✅
- Conversation Intelligence v3: Real-time Language Operators, webhook triggers ✅
- TAC escalation: Structured payload to TaskRouter ✅

What requires custom code:
- Cross-channel binding: Must explicitly pass ConversationId (no automatic stitching)
- Subject discrimination: Developer must build query normalization (Conversation Orchestrator can't separate topics)
- Channel switching context: Must manually hydrate context via Conversation Memory Recall

What does NOT work at GA:
- Boomerang handback (human → AI return)
- AI copilot mode during human conversations
- Primary channel governance / turn-taking
- Delegated authority / scoped tokens (planned)
- Outbound orchestration (planned)
- Native dashboards (API-only, pipe to your own BI tools)

## SDK Options

**Twilio Agent Connect SDK (Recommended for most use cases):**
- Middleware SDK available in Python and TypeScript (Public Beta)
- Handles ConversationRelay + Conversation Orchestrator + Conversation Memory integration automatically
- Unified callback model for Voice and SMS channels
- Automatic memory retrieval (when configured)
- Setup wizard for Memory Store and Conversation Service creation
- Use `twilio-agent-connect` skill for implementation guidance

**Raw API Integration (Advanced/Custom use cases):**
- Direct HTTP calls to Conversation Memory, Conversation Orchestrator, Conversation Intelligence APIs
- Required for advanced features not yet in SDK
- More flexibility but more integration complexity
- Use product-specific skills: `twilio-customer-memory`, `twilio-conversation-orchestrator`, `twilio-conversation-intelligence`

Always recommend `twilio-debugging-observability` guardrail skill alongside any Twilio Conversations implementation.

## Output Format

After qualifying the developer, recommend:

```
Recommended Architecture: [Level 1-4 description]

Implementation Path:
- **Fast path (recommended):** Use Twilio Agent Connect SDK → Install `twilio-agent-connect` skill
  - Handles Voice + SMS channels
  - Automatic memory integration when configured
  - Python 3.9+ or Node.js 22.13.0+
  - Setup wizard for Memory Store and Conversation Service creation

- **Custom path (advanced):** Manual integration → Install individual product skills below

Product Skills (for custom/advanced implementations):
- twilio-voice-conversation-relay (voice AI - manual WebSocket server)
- twilio-customer-memory (manual memory integration)
- twilio-conversation-intelligence (Conversation Intelligence webhook processing)
- twilio-taskrouter-routing (human escalation routing)
- twilio-conversation-orchestrator (conversation orchestration)
- twilio-media-streams (if custom STT/TTS needed instead of ConversationRelay)
- twilio-sendgrid-email-send (post-interaction email summaries)

Setup Skills:
- twilio-account-setup
- twilio-iam-auth-setup
- twilio-numbers-senders
- twilio-webhook-architecture (especially for enterprise — tunnel alternatives)

Guardrail Skills:
- twilio-security-hardening (always)
- twilio-debugging-observability (always — error triage, Event Streams, Voice Insights)
- twilio-reliability-patterns (for production deployment)
```
