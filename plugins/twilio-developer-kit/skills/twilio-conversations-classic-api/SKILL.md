---
name: twilio-conversations-classic-api
description: >
  Build multi-channel messaging experiences using Twilio Conversations (classic) API.
  Covers creating conversations, adding participants (SMS, WhatsApp, chat),
  sending messages, and handling webhooks. Use this skill to manage persistent
  multi-party or multi-channel conversations beyond single-message SMS/WhatsApp.
---

## Overview

Conversations (classic) API provides persistent, multi-channel threads where participants on SMS, WhatsApp, and web chat can message together. Unlike single-message APIs, Conversations maintains history and supports multi-agent access.

**Note:** This is the Conversations (classic) API (v1).

---

## Prerequisites

- Twilio account with Conversations (classic) enabled
  — New to Twilio? See `twilio-account-setup`
  — Enable at: [Console > Conversations > Manage > Overview](https://console.twilio.com/us1/develop/conversations/manage/overview) > **Enable Conversations**
- Environment variables:
  - `TWILIO_ACCOUNT_SID`
  - `TWILIO_AUTH_TOKEN`
  — See `twilio-iam-auth-setup` for credential setup and best practices
- SDK: `pip install twilio` / `npm install twilio`
- For SMS/WhatsApp participants: a Twilio number assigned to a Conversations Service

---

## Setup: Create a Conversation Service (classic)

A Conversation Service is the parent configuration container for all your conversations in the classic API. You need one before creating conversations with SMS/WhatsApp participants.

**Python**
```python
import os
from twilio.rest import Client

client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])

# Create a Conversation Service
service = client.conversations.v1.services.create(
    friendly_name="Customer Support Service"
)
print(f"Service SID: {service.sid}")
```

**Node.js**
```node
const twilio = require("twilio");
const client = twilio(process.env.TWILIO_ACCOUNT_SID, process.env.TWILIO_AUTH_TOKEN);

// Create a Conversation Service
const service = await client.conversations.v1.services.create({
    friendlyName: "Customer Support Service"
});
console.log(`Service SID: ${service.sid}`);
```

**Next:** Assign your Twilio phone number to this service at [Console > Conversations > Manage > Services](https://console.twilio.com/us1/develop/conversations/manage/services) > Select your service > Add phone number.

---

## Quickstart

**Python**
```python
import os
from twilio.rest import Client

client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])

# Create a conversation (use default service or specify service_sid)
conversation = client.conversations.v1.conversations.create(
    friendly_name="Customer Support - Order #12345"
)

# Add an SMS participant
client.conversations.v1 \
    .conversations(conversation.sid) \
    .participants \
    .create(
        messaging_binding_address="+15558675310",
        messaging_binding_proxy_address="+15017122661"
    )

# Send a message
client.conversations.v1 \
    .conversations(conversation.sid) \
    .messages \
    .create(body="Hello! How can I help you today?", author="support-agent")
```

**Node.js**
```node
const twilio = require("twilio");
const client = twilio(process.env.TWILIO_ACCOUNT_SID, process.env.TWILIO_AUTH_TOKEN);

// Create a conversation (use default service or specify serviceSid)
const conversation = await client.conversations.v1.conversations.create({
    friendlyName: "Customer Support - Order #12345",
});

// Add an SMS participant
await client.conversations.v1
    .conversations(conversation.sid)
    .participants.create({
        messagingBindingAddress: "+15558675310",
        messagingBindingProxyAddress: "+15017122661",
    });

// Send a message
await client.conversations.v1
    .conversations(conversation.sid)
    .messages.create({ body: "Hello! How can I help you today?", author: "support-agent" });
```

---

## Key Patterns

### Add Participants by Channel

**WhatsApp participant — Python**
```python
client.conversations.v1 \
    .conversations(conversation.sid) \
    .participants \
    .create(
        messaging_binding_address="whatsapp:+15558675310",
        messaging_binding_proxy_address="whatsapp:+14155238886"
    )
```

**WhatsApp participant — Node.js**
```node
await client.conversations.v1
    .conversations(conversationSid)
    .participants.create({
        messagingBindingAddress: "whatsapp:+15558675310",
        messagingBindingProxyAddress: "whatsapp:+14155238886",
    });
```

**Chat participant (web/mobile) — Python**
```python
client.conversations.v1 \
    .conversations(conversation.sid) \
    .participants \
    .create(identity="user-123")
```

**Chat participant (web/mobile) — Node.js**
```node
await client.conversations.v1
    .conversations(conversationSid)
    .participants.create({ identity: "user-123" });
```

### Send Media (All Channels)

**Python**
```python
# Send a message with media
client.conversations.v1 \
    .conversations(conversation.sid) \
    .messages \
    .create(
        body="Check out this image!",
        author="support-agent",
        media_url="https://example.com/image.jpg"
    )

# Multiple media URLs (up to 10)
client.conversations.v1 \
    .conversations(conversation.sid) \
    .messages \
    .create(
        body="Here are the documents",
        author="support-agent",
        media_url=[
            "https://example.com/doc1.pdf",
            "https://example.com/doc2.pdf"
        ]
    )
```

**Node.js**
```node
// Send a message with media
await client.conversations.v1
    .conversations(conversationSid)
    .messages.create({
        body: "Check out this image!",
        author: "support-agent",
        mediaUrl: "https://example.com/image.jpg"
    });

// Multiple media URLs (up to 10)
await client.conversations.v1
    .conversations(conversationSid)
    .messages.create({
        body: "Here are the documents",
        author: "support-agent",
        mediaUrl: [
            "https://example.com/doc1.pdf",
            "https://example.com/doc2.pdf"
        ]
    });
```

Media must be publicly accessible URLs. Supported: JPG, PNG, GIF, PDF, vCard. Max 10 URLs per message. Works across all channels: SMS (as MMS), WhatsApp, and chat participants all receive media.

### Add Multiple Participants

**Python**
```python
# Add multiple SMS participants to a conversation
participant_numbers = [
    "+15558675310",
    "+15558675311",
    "+15558675312"
]

twilio_number = "+15017122661"

for phone_number in participant_numbers:
    client.conversations.v1 \
        .conversations(conversation.sid) \
        .participants \
        .create(
            messaging_binding_address=phone_number,
            messaging_binding_proxy_address=twilio_number
        )
```

**Node.js**
```node
// Add multiple SMS participants to a conversation
const participantNumbers = [
    "+15558675310",
    "+15558675311",
    "+15558675312"
];

const twilioNumber = "+15017122661";

for (const phoneNumber of participantNumbers) {
    await client.conversations.v1
        .conversations(conversationSid)
        .participants.create({
            messagingBindingAddress: phoneNumber,
            messagingBindingProxyAddress: twilioNumber
        });
}
```

### Fetch Message History

**Python**
```python
# Get all messages from a conversation
messages = client.conversations.v1 \
    .conversations(conversation.sid) \
    .messages \
    .list(limit=50)

for message in messages:
    print(f"{message.author}: {message.body}")
```

**Node.js**
```node
// Get all messages from a conversation
const messages = await client.conversations.v1
    .conversations(conversationSid)
    .messages
    .list({ limit: 50 });

messages.forEach(message => {
    console.log(`${message.author}: ${message.body}`);
});
```

### List Conversations

**Python**
```python
# List all conversations
conversations = client.conversations.v1.conversations.list(limit=20)

for conv in conversations:
    print(f"{conv.friendly_name} - {conv.sid}")

# Filter by state
active_conversations = client.conversations.v1.conversations.list(
    state="active",
    limit=20
)
```

**Node.js**
```node
// List all conversations
const conversations = await client.conversations.v1.conversations.list({ limit: 20 });

conversations.forEach(conv => {
    console.log(`${conv.friendlyName} - ${conv.sid}`);
});

// Filter by state
const activeConversations = await client.conversations.v1.conversations.list({
    state: "active",
    limit: 20
});
```

### Remove Participants

**Python**
```python
# Remove a participant by participant SID
client.conversations.v1 \
    .conversations(conversation.sid) \
    .participants(participant_sid) \
    .delete()

# Find and remove by phone number
participants = client.conversations.v1 \
    .conversations(conversation.sid) \
    .participants \
    .list()

for p in participants:
    if p.messaging_binding and p.messaging_binding.get("address") == "+15558675310":
        client.conversations.v1 \
            .conversations(conversation.sid) \
            .participants(p.sid) \
            .delete()
```

**Node.js**
```node
// Remove a participant by participant SID
await client.conversations.v1
    .conversations(conversationSid)
    .participants(participantSid)
    .remove();

// Find and remove by phone number
const participants = await client.conversations.v1
    .conversations(conversationSid)
    .participants
    .list();

for (const p of participants) {
    if (p.messagingBinding?.address === "+15558675310") {
        await client.conversations.v1
            .conversations(conversationSid)
            .participants(p.sid)
            .remove();
    }
}
```

### Close/Complete Conversations

**Python**
```python
# Close a conversation (marks it inactive)
client.conversations.v1 \
    .conversations(conversation.sid) \
    .update(state="closed")

# Delete a conversation completely
client.conversations.v1 \
    .conversations(conversation.sid) \
    .delete()
```

**Node.js**
```node
// Close a conversation (marks it inactive)
await client.conversations.v1
    .conversations(conversationSid)
    .update({ state: "closed" });

// Delete a conversation completely
await client.conversations.v1
    .conversations(conversationSid)
    .remove();
```

### Handle Incoming Messages (Webhook)

Configure at Console > Conversations > Manage > Global Webhooks.

> **Security:** Always validate the `X-Twilio-Signature` header in production to confirm requests originate from Twilio. See `twilio-webhook-architecture` for validation patterns.

**Python (Flask)**
```python
from twilio.request_validator import RequestValidator

@app.route("/conversations/webhook", methods=["POST"])
def conversations_webhook():
    validator = RequestValidator(os.environ["TWILIO_AUTH_TOKEN"])
    if not validator.validate(request.url, request.form, request.headers.get("X-Twilio-Signature", "")):
        return "", 403

    event_type = request.form.get("EventType")
    conversation_sid = request.form.get("ConversationSid")
    author = request.form.get("Author")

    if event_type == "onMessageAdded" and author != "support-agent":
        client.conversations.v1.conversations(conversation_sid).messages.create(
            body="Thanks — an agent will be with you shortly.",
            author="support-bot"
        )
    return "", 204
```

**Node.js (Express)**
```node
app.post("/conversations/webhook", async (req, res) => {
    const valid = twilio.validateRequest(
        process.env.TWILIO_AUTH_TOKEN,
        req.headers["x-twilio-signature"],
        `https://${req.headers.host}${req.originalUrl}`,
        req.body
    );
    if (!valid) return res.status(403).send("Forbidden");

    const { EventType, ConversationSid, Author } = req.body;
    if (EventType === "onMessageAdded" && Author !== "support-agent") {
        await client.conversations.v1
            .conversations(ConversationSid)
            .messages.create({ body: "Thanks — an agent will be with you shortly.", author: "support-bot" });
    }
    res.sendStatus(204);
});
```

---

## Advanced Context

### Message Delivery Status

Track message delivery through webhooks. Configure at Console > Conversations > Manage > Global Webhooks.

**Available delivery events:**
- `onMessageAdded` — Message created
- `onMessageUpdated` — Message status changed
- `onDeliveryUpdated` — Delivery receipt received (SMS/WhatsApp only)

**Python (Flask)**
```python
@app.route("/conversations/webhook", methods=["POST"])
def delivery_webhook():
    event_type = request.form.get("EventType")
    
    if event_type == "onDeliveryUpdated":
        delivery_status = request.form.get("DeliveryStatus")
        message_sid = request.form.get("MessageSid")
        print(f"Message {message_sid}: {delivery_status}")
        # Status values: sent, delivered, failed, undelivered
    
    return "", 204
```

**Node.js (Express)**
```node
app.post("/conversations/webhook", (req, res) => {
    const { EventType, DeliveryStatus, MessageSid } = req.body;
    
    if (EventType === "onDeliveryUpdated") {
        console.log(`Message ${MessageSid}: ${DeliveryStatus}`);
        // Status values: sent, delivered, failed, undelivered
    }
    
    res.sendStatus(204);
});
```

### Conversation Attributes (Metadata)

Store custom metadata on conversations (order IDs, customer info, tags).

**Python**
```python
# Set attributes when creating
conversation = client.conversations.v1.conversations.create(
    friendly_name="Customer Support - Order #12345",
    attributes='{"order_id": "12345", "priority": "high", "customer_tier": "gold"}'
)

# Update attributes on existing conversation
client.conversations.v1 \
    .conversations(conversation.sid) \
    .update(attributes='{"order_id": "12345", "status": "resolved"}')

# Read attributes
conv = client.conversations.v1.conversations(conversation.sid).fetch()
import json
attrs = json.loads(conv.attributes)
print(f"Order ID: {attrs['order_id']}")
```

**Node.js**
```node
// Set attributes when creating
const conversation = await client.conversations.v1.conversations.create({
    friendlyName: "Customer Support - Order #12345",
    attributes: JSON.stringify({ orderId: "12345", priority: "high", customerTier: "gold" })
});

// Update attributes on existing conversation
await client.conversations.v1
    .conversations(conversationSid)
    .update({ attributes: JSON.stringify({ orderId: "12345", status: "resolved" }) });

// Read attributes
const conv = await client.conversations.v1.conversations(conversationSid).fetch();
const attrs = JSON.parse(conv.attributes);
console.log(`Order ID: ${attrs.orderId}`);
```

### Participant Attributes (Metadata)

Store metadata on individual participants (role, name, account info).

**Python**
```python
# Set attributes when adding participant
client.conversations.v1 \
    .conversations(conversation.sid) \
    .participants \
    .create(
        messaging_binding_address="+15558675310",
        messaging_binding_proxy_address="+15017122661",
        attributes='{"name": "John Doe", "role": "customer", "account_id": "A123"}'
    )

# Update participant attributes
client.conversations.v1 \
    .conversations(conversation.sid) \
    .participants(participant_sid) \
    .update(attributes='{"role": "vip_customer", "satisfaction": "high"}')
```

**Node.js**
```node
// Set attributes when adding participant
await client.conversations.v1
    .conversations(conversationSid)
    .participants.create({
        messagingBindingAddress: "+15558675310",
        messagingBindingProxyAddress: "+15017122661",
        attributes: JSON.stringify({ name: "John Doe", role: "customer", accountId: "A123" })
    });

// Update participant attributes
await client.conversations.v1
    .conversations(conversationSid)
    .participants(participantSid)
    .update({ attributes: JSON.stringify({ role: "vip_customer", satisfaction: "high" }) });
```

---

## Limits

| Limit | Value |
|-------|-------|
| Participants per conversation | 1,000 |
| Messages per conversation | Unlimited (older messages may be archived) |
| Message retention | Configurable (default: indefinite) |

---

## CANNOT

- **Cannot add SMS participants without a Twilio number** — Number must be assigned to a Conversations (classic) Service
- **Cannot send WhatsApp messages outside the 24-hour window** — Subject to service window rules. See `twilio-whatsapp-send-message`
- **Cannot use chat participants without Access Tokens** — Client-side SDK auth required. See `twilio-iam-auth-setup`
- **Cannot use WhatsApp Groups API** — Deprecated April 2020. Use Conversations (classic) API instead.
- **Conversations v1 (classic) is in maintenance mode** — Consider Conversations v2 API for new projects with enhanced features and scalability.

---

## Next Steps

- **WhatsApp setup and rules:** `twilio-whatsapp-send-message`
- **SMS setup:** `twilio-sms-send-message`
- **Access Tokens for chat clients:** `twilio-iam-auth-setup`
- **Webhook security:** `twilio-webhook-architecture`
