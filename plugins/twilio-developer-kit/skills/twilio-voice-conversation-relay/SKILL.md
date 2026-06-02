---
name: twilio-voice-conversation-relay
description: >
  Build AI-powered voice agents using Twilio ConversationRelay. Handles
  real-time speech recognition (ASR), text-to-speech (TTS), and bidirectional
  audio streaming via WebSocket. Covers TwiML setup, WebSocket message types,
  LLM integration, streaming responses, and voice provider configuration. Use
  this skill to build voice bots, IVR replacements, or real-time AI voice
  assistants on Twilio calls.
---

## Overview

ConversationRelay connects Twilio's telephony layer to your app via a persistent WebSocket. Twilio handles ASR (speech-to-text) and TTS (text-to-speech); your app receives transcripts, calls an LLM, and sends text back for playback.

```
Caller ←→ Twilio (ASR/TTS) ←→ WebSocket ←→ Your App ←→ LLM
```

---

## Prerequisites

- Upgraded Twilio account with ConversationRelay access (requires onboarding)
  — New to Twilio? See `twilio-account-setup`
  — Start onboarding at: [Console > Voice > ConversationRelay](https://console.twilio.com/us1/voice/conversation-relay) — access is **not** instant
- A voice-capable Twilio phone number
- `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` — see `twilio-iam-auth-setup`
- WebSocket server reachable via `wss://` (TLS required)
- An LLM integration (OpenAI, Anthropic, etc.)
- For placing calls: see `twilio-voice-outbound-calls`

**Onboarding:** Complete via Console > Voice > ConversationRelay > Onboarding. Select TTS/ASR providers:
- **TTS:** Deepgram, Amazon Polly, Google Cloud TTS, ElevenLabs
- **ASR:** Deepgram, Google Cloud STT

---

## Quickstart

**Step 1 — Return TwiML pointing to your WebSocket server**

**Python (Flask)**
```python
from flask import Flask
from twilio.twiml.voice_response import VoiceResponse, Connect, ConversationRelay

app = Flask(__name__)

@app.route("/voice", methods=["POST"])
def voice():
    response = VoiceResponse()
    connect = Connect()
    connect.conversation_relay(
        url="wss://yourapp.com/ws/voice",
        welcome_greeting="Hello! How can I help you today?"
    )
    response.append(connect)
    return str(response)
```

**Node.js (Express)**
```node
const { VoiceResponse } = require("twilio").twiml;

app.post("/voice", (req, res) => {
    const response = new VoiceResponse();
    const connect = response.connect();
    connect.conversationRelay({
        url: "wss://yourapp.com/ws/voice",
        welcomeGreeting: "Hello! How can I help you today?",
    });
    res.type("text/xml").send(response.toString());
});
```

**Step 2 — Handle WebSocket events and respond with text**

**Python (websockets)**
```python
import asyncio, json, websockets

async def handle_call(websocket):
    async for message in websocket:
        event = json.loads(message)
        if event["type"] == "prompt":
            ai_response = await call_llm(event["voicePrompt"])
            await websocket.send(json.dumps({"type": "text", "token": ai_response, "last": True}))

async def main():
    async with websockets.serve(handle_call, "0.0.0.0", 8080):
        await asyncio.Future()

asyncio.run(main())
```

**Node.js (ws)**
```node
const WebSocket = require("ws");
const wss = new WebSocket.Server({ port: 8080 });

wss.on("connection", (ws) => {
    ws.on("message", async (data) => {
        const event = JSON.parse(data);
        if (event.type === "prompt") {
            const aiResponse = await callLLM(event.voicePrompt);
            ws.send(JSON.stringify({ type: "text", token: aiResponse, last: true }));
        }
    });
});
```

> **Security:** The `voicePrompt` field contains ASR-transcribed caller speech — it is untrusted external input. When passing to an LLM, isolate it as user input within a structured system prompt. Implement topic boundaries and output filtering to prevent the LLM from disclosing system instructions or speaking inappropriate content. ConversationRelay is a pure transport layer with no built-in content safety — any LLM output is spoken to the caller verbatim.

---

## Key Patterns

### WebSocket Message Types

**Received from Twilio:**

| Type | When | Key fields |
|------|------|-----------|
| `connected` | WebSocket opened | `callSid`, `streamSid` |
| `prompt` | User finished speaking | `voicePrompt` (transcript) |
| `interrupt` | User interrupted TTS | — |
| `dtmf` | User pressed keypad key | `digit` |
| `error` | An error occurred | `description` |

**Sent to Twilio:**

| Type | Purpose | Key fields |
|------|---------|-----------|
| `text` | Send TTS response | `token` (text), `last` (bool) |
| `interrupt` | Stop current TTS | — |
| `end` | Hang up the call | `reason` |

### Stream LLM Responses Token-by-Token

Lower latency by streaming as the LLM generates output — Twilio starts speaking before the full response is ready.

**Python**
```python
async for chunk in llm_stream:
    await websocket.send(json.dumps({"type": "text", "token": chunk, "last": False}))
await websocket.send(json.dumps({"type": "text", "token": "", "last": True}))
```

**Node.js**
```node
for await (const chunk of llmStream) {
    ws.send(JSON.stringify({ type: "text", token: chunk, last: false }));
}
ws.send(JSON.stringify({ type: "text", token: "", last: true }));
```

### Voice Configuration

**Python**
```python
connect.conversation_relay(
    url="wss://yourapp.com/ws/voice",
    voice="en-US-Neural2-F",
    language="en-US",
    transcription_provider="deepgram",
    speech_model="nova-2-phonecall",
    interrupt_by_dtmf=True,
)
```

**Node.js**
```node
connect.conversationRelay({
    url: "wss://yourapp.com/ws/voice",
    voice: "en-US-Neural2-F",
    language: "en-US",
    transcriptionProvider: "deepgram",
    speechModel: "nova-2-phonecall",
    interruptByDtmf: true,
});
```

---

## CANNOT

- **No raw audio access** — Text in, text out only. For raw audio, use `<Connect><Stream>` (Media Streams).
- **Cannot mix with Media Streams** — `<Connect><Stream>` and `<Connect><ConversationRelay>` are mutually exclusive on the same call. No error — one is silently ignored.
- **No custom STT/TTS engines** — Limited to Deepgram + Google (STT) and Deepgram + Amazon Polly + Google + ElevenLabs (TTS).
- **No mid-session voice/provider changes** — Voice and provider are set at TwiML time. Only `language` can be switched mid-session via WebSocket message.
- **No WebSocket auto-reconnection** — If the WebSocket drops, the call disconnects. Implement recovery via `<Connect action>` URL.
- **Voice only** — No SMS/messaging support. For omnichannel, use Conversation Orchestrator.
- **No built-in memory or context** — BYO conversation history and context management.
- **No LLM integration** — Pure transport layer. You bring your own LLM via the WebSocket server.
- **No server-side recording via REST API** — `record:true` on the Calls API is silently ignored. Must use `<Start><Recording>` before `<Connect>` in TwiML.
- **Not PCI compliant with Voice Intelligence v2** — Do not enable `intelligenceService` in PCI workflows.
- **ElevenLabs requires account enablement** — Accounts without ElevenLabs access get error 64101. Voice IDs (not human-readable names) are required.
- **Cannot use ConversationRelay without onboarding** — Not available immediately on a new account
- **Cannot use non-TLS WebSocket** — Server must be reachable via `wss://` (TLS required)
- **Cannot stream audio without `last: true`** — Twilio won't play audio until it sees a `last: true` token in the stream

---

## Next Steps

- **Place outbound calls:** `twilio-voice-outbound-calls`
- **Standard IVR without AI:** `twilio-voice-twiml`
