# Twilio Agent Connect

## Overview

Twilio Agent Connect (TAC) is a Python and TypeScript SDK that integrates third-party LLM agentic applications with Twilio's communication technologies. TAC provides middleware for identity resolution, memory/context management (via Conversation Memory), conversation orchestration (via Conversation Orchestrator), and multi-channel handling (Voice, SMS, RCS, WhatsApp, Chat).

**Key Architecture Principle**: TAC is not an agent runtime itself—it's middleware that enables existing LLM applications (OpenAI Agents SDK, Bedrock, LangChain, Microsoft Foundry, etc.) to leverage Twilio Conversations services.

## Product Context

### Core Twilio Conversations Services

TAC integrates with three core Twilio Conversations services:

1. **Conversation Memory (Memory Store)** - Persistent user context and memory management
   - Profile storage with traits and attributes
   - Observation and summary storage
   - Session history with full conversation context
   - Identity resolution (profile lookup by phone/email)

2. **Conversation Orchestrator** - Multi-channel conversation lifecycle management
   - Unified conversation API across all channels
   - Participant management
   - Communication routing
   - Conversation grouping and configuration

3. **Enterprise Knowledge** - Knowledge base integration
   - Semantic search across knowledge bases
   - RAG (Retrieval-Augmented Generation) support
   - Knowledge chunk retrieval with relevance scoring

### Supported Channels

TAC provides built-in support for:
- **Voice** - ConversationRelay (WebSocket-based real-time voice)
- **SMS** - Text messaging
- **RCS** - Rich Communication Services
- **WhatsApp** - WhatsApp Business messaging
- **Chat** - Web chat integrations

All channels support both inbound (customer-initiated) and outbound (agent-initiated) conversations.

### ConversationRelay-Only Mode

TAC supports a simplified "ConversationRelay-only" mode for getting started with voice conversations without requiring Conversation Orchestrator or Conversation Memory setup. This mode provides:
- TwiML generation
- WebSocket protocol handling
- Voice conversation lifecycle management
- Callback-based message processing

## Installation

### Python SDK

**Requirements**: Python 3.10+

```bash
# Using uv (recommended)
uv add git+https://github.com/twilio/twilio-agent-connect-python.git

# With server support (includes FastAPI and uvicorn for TACFastAPIServer)
uv add git+https://github.com/twilio/twilio-agent-connect-python.git --extra server

# Using pip
pip install git+https://github.com/twilio/twilio-agent-connect-python.git
pip install "git+https://github.com/twilio/twilio-agent-connect-python.git[server]"
```

### TypeScript SDK

**Requirements**: Node.js 22.13+

```bash
# Clone and build (not yet published to npm)
git clone https://github.com/twilio/twilio-agent-connect-typescript.git
cd twilio-agent-connect-typescript
npm install
npm run build
```

## Quick Start

### Multi-Channel Agent with OpenAI (Python)

```python
from dotenv import load_dotenv
from openai import AsyncOpenAI
from tac import TAC, TACConfig
from tac.adapters.openai import with_tac_memory
from tac.channels.sms import SMSChannel
from tac.channels.voice import VoiceChannel
from tac.server import TACFastAPIServer

load_dotenv()

tac = TAC(config=TACConfig.from_env())
voice_channel = VoiceChannel(tac)
sms_channel = SMSChannel(tac)
openai_client = AsyncOpenAI()

conversation_history = {}
SYSTEM_INSTRUCTIONS = (
    "You are a customer service agent speaking with a user over voice or SMS. "
    "Keep responses short and conversational — a sentence or two. "
    "Do not use markdown, asterisks, bullets, or emojis; your words will be "
    "spoken aloud or sent as plain text."
)

async def handle_message_ready(user_message, context, memory_response):
    conv_id = context.conversation_id

    if conv_id not in conversation_history:
        conversation_history[conv_id] = []
    conversation_history[conv_id].append({"role": "user", "content": user_message})

    # Inject conversation memory and profile into OpenAI client
    client = with_tac_memory(openai_client, memory_response, context)

    response = await client.responses.create(
        model="gpt-5.4-mini",
        instructions=SYSTEM_INSTRUCTIONS,
        input=conversation_history[conv_id]
    )

    llm_response = response.output_text
    conversation_history[conv_id].append({"role": "assistant", "content": llm_response})

    return llm_response

tac.on_message_ready(handle_message_ready)
TACFastAPIServer(tac=tac, voice_channel=voice_channel, messaging_channels=[sms_channel]).start()
```

### Multi-Channel Agent with OpenAI (TypeScript)

```typescript
import { config } from 'dotenv';
import OpenAI from 'openai';
import {
  TAC,
  TACConfig,
  VoiceChannel,
  SMSChannel,
  TACServer,
  MemoryPromptBuilder,
} from 'twilio-agent-connect';

config();

const openai = new OpenAI();
const tac = await TAC.create({ config: TACConfig.fromEnv() });
const voiceChannel = new VoiceChannel(tac);
const smsChannel = new SMSChannel(tac);

tac.registerChannel(voiceChannel);
tac.registerChannel(smsChannel);

const conversationHistory: Record<string, OpenAI.Chat.ChatCompletionMessageParam[]> = {};

const SYSTEM_INSTRUCTIONS =
  'You are a customer service agent speaking with a user over voice or SMS. ' +
  'Keep responses short and conversational — a sentence or two. ' +
  'Do not use markdown, asterisks, bullets, or emojis; your words will be ' +
  'spoken aloud or sent as plain text.';

tac.onMessageReady(async ({ conversationId, message, memory, session }) => {
  const convId = conversationId as string;

  if (!conversationHistory[convId]) {
    conversationHistory[convId] = [];
  }

  const memoryContext = MemoryPromptBuilder.build(memory, session);
  const systemPrompt = SYSTEM_INSTRUCTIONS + (memoryContext ? `\n\n${memoryContext}` : '');

  conversationHistory[convId].push({ role: 'user', content: message });

  const response = await openai.chat.completions.create({
    model: 'gpt-4o-mini',
    messages: [
      { role: 'system', content: systemPrompt },
      ...conversationHistory[convId],
    ],
  });

  const llmResponse = response.choices[0]?.message?.content ?? '';
  conversationHistory[convId].push({ role: 'assistant', content: llmResponse });

  return llmResponse;
});

const server = new TACServer(tac);
await server.start();
```

## Configuration

### Required Environment Variables

```bash
# Twilio Account Credentials
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_API_KEY=SKxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_API_SECRET=your_api_key_secret

# Conversation Configuration
TWILIO_CONVERSATION_CONFIGURATION_ID=conv_configuration_xxxx

# Phone Number
TWILIO_PHONE_NUMBER=+1234567890

# Server Configuration (for Voice)
TWILIO_VOICE_PUBLIC_DOMAIN=your-domain.ngrok.io
```

### Optional Memory Configuration

```bash
# Conversation Memory (optional)
TWILIO_MEMORY_STORE_ID=mem_service_xxxx
TWILIO_TRAIT_GROUPS=Contact,Preferences
```

## Cloud Platform Integrations

### AWS Integration

**Package**: `twilio-agent-connect-aws`

Connect AWS agent services to Twilio channels:

```bash
# With Strands SDK
pip install twilio-agent-connect-aws[strands,server]

# With Bedrock Agents
pip install twilio-agent-connect-aws[bedrock,server]

# With Bedrock AgentCore
pip install twilio-agent-connect-aws[agentcore,server]
```

**Features**:
- **StrandsConnector** - AWS Strands SDK integration with per-conversation agent isolation
- **BedrockConnector** - AWS Bedrock Agents (console-created agents)
- **BedrockAgentCoreConnector** - AWS Bedrock AgentCore (custom agent code deployment)

**Repository**: https://github.com/twilio/twilio-agent-connect-aws

### Microsoft/Azure Integration

**Package**: `twilio-agent-connect-microsoft` (formerly `tac-azure`)

Connect Microsoft Foundry agents to Twilio channels:

```bash
# With Agent Framework
pip install twilio-agent-connect-microsoft[agent-framework,server]

# With Voice Live
pip install twilio-agent-connect-microsoft[voice-live,server]
```

**Features**:
- **AgentFrameworkConnector** - Microsoft Agent Framework integration
  - Supports Foundry Hosted Agents, Foundry Prompt Agents, Azure OpenAI (Responses API, Chat Completions)
  - Pluggable session persistence (in-memory, file, Cosmos DB)
  - Memory context injection and lifecycle hooks
- **VoiceLiveConnector** - Voice Live API integration
  - Text-in / text-streaming-out over WebSocket
  - STT and TTS handled by Twilio ConversationRelay
  - Native interrupt handling via Voice Live `response.cancel`
  - Server-side conversation state management
  - Tool execution with async handlers

**Repository**: https://github.com/twilio/twilio-agent-connect-microsoft

## Key Features

### Memory Management

Automatic integration with Twilio Conversation Memory for persistent user context:
- Profile retrieval with traits
- Observation and summary storage
- Session history with full message context
- Automatic profile lookup by phone/email

### Conversation Lifecycle

Automatic tracking of conversation sessions and state:
- Multi-channel conversation initialization
- Participant management
- Conversation status tracking
- Graceful cleanup on conversation end

### Message Flow

1. **Webhook/Connection Received** - Twilio sends webhook (messaging) or WebSocket connection (voice)
2. **Channel Processing** - Channel validates and processes the incoming event
3. **Memory Retrieval** - TAC optionally retrieves user memories and profile from Conversation Memory
4. **Callback Invoked** - Your `on_message_ready` callback receives user message, context, and optional memory response
5. **Response Handling** - Your callback returns a response string that TAC routes to the appropriate channel

### Outbound Conversations

TAC supports agent-initiated conversations across all channels:
- Programmatic conversation creation
- Participant addition
- Message sending
- Full conversation lifecycle management

## Voice-Specific Features

### ConversationRelay Protocol

TAC handles the full ConversationRelay WebSocket protocol:
- TwiML generation for inbound calls
- WebSocket connection management
- Message parsing and validation
- Automatic conversation initialization
- Status callback handling

### Voice Live API (Microsoft Integration)

The Voice Live connector provides:
- Text-in / text-streaming-out interface
- STT (Speech-to-Text) handled by Twilio
- TTS (Text-to-Speech) handled by Twilio
- Server-side interrupt handling
- No local session management required

## Messaging-Specific Features

### SMS Channel

- Idempotency-based deduplication using Twilio's `i-twilio-idempotency-token` header
- Fire-and-forget webhook processing with immediate 200 response
- Automatic conversation initialization
- Profile retrieval per message

### Multi-Channel Support

TAC provides unified handling across SMS, RCS, WhatsApp, and Chat:
- Single `on_message_ready` callback for all channels
- Automatic channel detection and routing
- Per-channel response formatting

## Advanced Features

### Conversation Intelligence Integration

Process Conversation Intelligence operator results to create observations and summaries:

```python
from tac.core.config import ConversationIntelligenceConfig

config = TACConfig.from_env()
config.conversation_intelligence_config = ConversationIntelligenceConfig(
    configuration_id="your_ci_configuration_id",
    observation_operator_sid="LY...",
    summary_operator_sid="LY...",
)

@app.post("/ci-webhook")
async def ci_webhook_handler(request: Request):
    payload = await request.json()
    result = await tac.process_conversation_intelligence_event(payload)
    return result.model_dump()
```

### Custom Tools

TAC provides built-in tools for common operations:
- Memory recall
- Knowledge base search
- Studio Flow handoff (human escalation)
- Message sending

You can also create custom tools using the `@function_tool` decorator:

```python
from tac.tools import function_tool

@function_tool()
def send_email(recipient: str, subject: str, body: str) -> bool:
    """
    Sends an email to a recipient.

    Args:
        recipient: Email address
        subject: Email subject
        body: Email body

    Returns:
        True on success, False on failure
    """
    # Implementation here
    return True
```

### Adapter Pattern

TAC provides adapters for automatic memory injection into LLM runtimes:

**Python OpenAI Adapter**:
```python
from tac.adapters.openai import with_tac_memory

client = with_tac_memory(openai_client, memory_response, context)
# Memory and profile automatically injected into system messages
```

**TypeScript Memory Prompt Builder**:
```typescript
import { MemoryPromptBuilder } from 'twilio-agent-connect';

const memoryContext = MemoryPromptBuilder.build(memory, session);
const systemPrompt = SYSTEM_INSTRUCTIONS + `\n\n${memoryContext}`;
```

## Documentation Links

- **Quickstart Guide**: https://www.twilio.com/docs/platform/tac/quickstart
- **Overview Documentation**: https://www.twilio.com/docs/platform/tac/overview
- **Python SDK**: https://github.com/twilio/twilio-agent-connect-python
- **TypeScript SDK**: https://github.com/twilio/twilio-agent-connect-typescript
- **AWS Integration**: https://github.com/twilio/twilio-agent-connect-aws
- **Microsoft Integration**: https://github.com/twilio/twilio-agent-connect-microsoft

## Setup Wizard

TAC includes a web-based setup wizard to automatically create required Twilio services:

```bash
# Python SDK
git clone https://github.com/twilio/twilio-agent-connect-python.git
cd twilio-agent-connect-python
make setup  # Opens http://localhost:8080
```

The wizard creates:
- Conversation Memory store
- Conversation Configuration
- Generates `.env` file with all required credentials

## Common Use Cases

### Customer Support Agent

Build an AI-powered customer support agent with:
- Multi-channel support (voice, SMS, WhatsApp)
- Persistent customer memory and context
- Knowledge base integration
- Human handoff capability

### Outbound Campaign Agent

Create an agent that initiates conversations:
- Schedule outbound calls or messages
- Personalized messaging based on customer profile
- Conversation tracking and analytics

### Voice IVR Replacement

Replace traditional IVR with conversational AI:
- Natural language understanding
- Context-aware responses
- Seamless handoff to human agents

### Multi-Language Support

Build globally accessible agents:
- Automatic language detection
- Multi-language conversation memory
- Localized responses

## Best Practices

### Error Handling

TAC provides lenient error handling:
- Profile lookup failures fall back to Conversation Orchestrator API
- Memory retrieval failures continue without exceptions
- All errors logged with appropriate severity levels

### Performance Optimization

- Use immediate 200 responses for webhooks to prevent retries
- Enable conversation deduplication for high-traffic applications
- Leverage conversation grouping for related interactions

### Security

- Never commit API keys or tokens to version control
- Use environment variables for all credentials
- Implement webhook signature validation (Twilio SDK provides helpers)
- Use HTTPS for all webhook endpoints

### Testing

- Use ngrok for local webhook testing
- Test each channel independently before multi-channel deployment
- Implement logging for debugging webhook processing
- Use TAC's built-in logging with channel-specific logger names

## Troubleshooting

### Common Issues

**Memory not retrieving**:
- Verify `TWILIO_MEMORY_STORE_ID` is set
- Check profile_id is present in webhook data
- Enable DEBUG logging: `TWILIO_TAC_LOG_LEVEL=DEBUG`

**Voice not connecting**:
- Verify `TWILIO_VOICE_PUBLIC_DOMAIN` is accessible
- Check TwiML endpoint returns valid XML
- Ensure WebSocket endpoint is reachable
- Verify Conversation Configuration is active

**Duplicate messages**:
- Ensure webhook returns 200 immediately
- Verify idempotency token is passed to channel
- Check deduplication capacity is sufficient

**Channel isolation issues**:
- Verify each channel has distinct conversation sessions
- Check `configuration_id` filtering is enabled
- Ensure conversation status is properly tracked

## Version Requirements

- **Python SDK**: Python 3.10+
- **TypeScript SDK**: Node.js 22.13+
- **Twilio SDK**: twilio>=9.8.3

## License

MIT License - see repository LICENSE files for details.
