---
name: twilio-enterprise-knowledge
description: >
  Add knowledge retrieval to AI agents using Twilio's Enterprise Knowledge
  product. Enterprise Knowledge is a centralized, searchable repository of your
  organization's documents, websites, and content — FAQs, support policies,
  warranty terms, product catalogs. Current models don't have access to how you
  run your business today. Enterprise Knowledge gives agents a way to query this
  repository during a conversation and ground their responses in your actual
  approved source material. This skill covers provisioning a Knowledge Base and
  uploading knowledge sources from web URLs, PDFs, and raw text, and running
  semantic search to retrieve relevant chunks at runtime. Enterprise Knowledge is
  shared across your organization — it captures what your organization knows and
  how it is meant to run. It is distinct from Conversation Memory
  (twilio-customer-memory), which is scoped to individual end-customers and
  captures what you know about a specific person. The two are designed to be
  combined: enterprise content for business practices, customer memory for
  personalization.
---

## Overview

Enterprise Knowledge gives AI and human agents access to your organization's actual source material during a conversation — FAQs, warranty policies, support scripts, product catalogs. Models trained on general data don't know how your business operates today; Enterprise Knowledge closes that gap by letting agents query a searchable repository of your approved content and inject accurate, up-to-date answers rather than hallucinated ones.

```
Your content (web/PDF/text) → Knowledge Base → Indexed chunks
Agent query → Search → Ranked chunks → Inject into LLM prompt
```

Enterprise Knowledge is shared across your organization and captures institutional content: how your products work, what your policies say, what your agents are supposed to do. It is distinct from Conversation Memory, which is scoped to individual end-customers. The two are designed to be combined — enterprise content for accuracy and business practices, customer memory for personalization.

**Auth: Basic Auth** — `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN`.

---

## Prerequisites

- Twilio account with Enterprise Knowledge access (requires enablement)
  — New to Twilio? See `twilio-account-setup`
- `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` — see `twilio-iam-auth-setup`

---

## Quickstart

### Step 1 — Create a Knowledge Base

Knowledge Bases are containers for knowledge sources. Creation is async — returns 202, poll the `Location` header until `status: ACTIVE`.

**Python**
```python
import os, requests, time

account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]

res = requests.post(
    "https://memory.twilio.com/v1/ControlPlane/KnowledgeBases",
    auth=(account_sid, auth_token),
    json={
        "displayName": "product-docs",          # alphanumeric + hyphens only
        "description": "Product documentation for customer support agents"
    }
)

operation_url = res.headers["Location"]

# Poll until ready
while True:
    kb = requests.get(operation_url, auth=(account_sid, auth_token)).json()
    if kb.get("status") == "ACTIVE":
        kb_id = kb["id"]
        break
    if kb.get("status") == "FAILED":
        raise Exception("Knowledge Base creation failed")
    time.sleep(2)

print(kb_id)
```

**Node.js**
```javascript
const accountSid = process.env.TWILIO_ACCOUNT_SID;
const authToken = process.env.TWILIO_AUTH_TOKEN;
const authHeader = "Basic " + btoa(`${accountSid}:${authToken}`);

const res = await fetch("https://memory.twilio.com/v1/ControlPlane/KnowledgeBases", {
    method: "POST",
    headers: {
        "Authorization": authHeader,
        "Content-Type": "application/json",
    },
    body: JSON.stringify({
        displayName: "product-docs",
        description: "Product documentation for customer support agents",
    }),
});

const operationUrl = res.headers.get("Location");

let kbId;
while (true) {
    const kb = await fetch(operationUrl, {
        headers: { "Authorization": authHeader },
    }).then(r => r.json());
    if (kb.status === "ACTIVE") { kbId = kb.id; break; }
    if (kb.status === "FAILED") throw new Error("Knowledge Base creation failed");
    await new Promise(r => setTimeout(r, 2000));
}
```

### Step 2 — Add a Knowledge Source

Three source types: **Web** (crawl a URL), **File** (upload PDF/CSV/Markdown/text), **Text** (inline raw text).

#### Web source

```python
knowledge = requests.post(
    f"https://knowledge.twilio.com/v1/KnowledgeBases/{kb_id}/Knowledge",
    auth=(account_sid, auth_token),
    json={
        "name": "Product Documentation",
        "description": "Public product docs",
        "source": {
            "type": "Web",
            "url": "https://docs.example.com",
            "crawlDepth": 3,           # 1–10, default 2
            "crawlPeriod": "WEEKLY"    # WEEKLY | BIWEEKLY | MONTHLY | NEVER
        }
    }
).json()

knowledge_id = knowledge["id"]
```

#### File source (PDF, CSV, Markdown, TSV, plain text — max 16MB)

```python
# Step 1: Create the source — returns a presigned upload URL
knowledge = requests.post(
    f"https://knowledge.twilio.com/v1/KnowledgeBases/{kb_id}/Knowledge",
    auth=(account_sid, auth_token),
    json={
        "name": "Company Handbook",
        "source": {
            "type": "File",
            "fileName": "handbook.pdf",
            "fileSize": 2048576,
            "mimeType": "application/pdf"
        }
    }
).json()

knowledge_id = knowledge["id"]
upload_url = knowledge["source"]["importUrl"]   # presigned S3 URL

# Step 2: PUT file to presigned URL — no auth header, URL is already signed
with open("handbook.pdf", "rb") as f:
    requests.put(upload_url, data=f, headers={"Content-Type": "application/pdf"})
```

#### Text source (inline content, max 185,000 chars)

```python
knowledge = requests.post(
    f"https://knowledge.twilio.com/v1/KnowledgeBases/{kb_id}/Knowledge",
    auth=(account_sid, auth_token),
    json={
        "name": "Refund Policy",
        "source": {
            "type": "Text",
            "content": "Our refund policy: customers may return items within 30 days..."
        }
    }
).json()
```

### Step 3 — Wait for Processing

Knowledge sources are processed asynchronously. Poll until `status` is `COMPLETED`.

```python
def wait_for_knowledge(kb_id, knowledge_id):
    while True:
        k = requests.get(
            f"https://knowledge.twilio.com/v1/KnowledgeBases/{kb_id}/Knowledge/{knowledge_id}",
            auth=(account_sid, auth_token)
        ).json()
        if k["status"] == "COMPLETED":
            return k
        if k["status"] == "FAILED":
            raise Exception(f"Knowledge processing failed: {k}")
        time.sleep(3)

wait_for_knowledge(kb_id, knowledge_id)
```

Statuses: `SCHEDULED` → `QUEUED` → `PROCESSING` → `COMPLETED` / `FAILED`

### Step 4 — Search and Inject into LLM

**Python**
```python
results = requests.post(
    f"https://knowledge.twilio.com/v1/KnowledgeBases/{kb_id}/Search",
    auth=(account_sid, auth_token),
    json={
        "query": "How do I reset my password?",
        "top": 5,                              # max 20
        "knowledgeIds": [knowledge_id]         # optional — search specific sources
    }
).json()

chunks = "\n\n".join(c["content"] for c in results.get("chunks", []))

system_prompt = f"""You are a helpful support agent.

Relevant knowledge:
{chunks}

Answer the customer's question using only the above content."""
```

**Node.js**
```javascript
const results = await fetch(
    `https://knowledge.twilio.com/v1/KnowledgeBases/${kbId}/Search`,
    {
        method: "POST",
        headers: {
            "Authorization": authHeader,
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            query: userMessage,
            top: 5,
            knowledgeIds: [knowledgeId],
        }),
    }
).then(r => r.json());

const chunks = results.chunks.map(c => c.content).join("\n\n");
const systemPrompt = `You are a helpful support agent.\n\nRelevant knowledge:\n${chunks}`;
```

---

## Key Patterns

### Combine Enterprise Knowledge with Conversation Memory Recall

For the best agent responses, combine both: Enterprise Knowledge for company content, Recall for individual customer history.

**Python**
```python
# Run both in parallel
recall_res = requests.post(
    f"https://memory.twilio.com/v1/Services/{MEMORY_STORE_SID}/Profiles/{profile_id}/Recall",
    auth=(account_sid, auth_token),
    json={"query": user_query, "observationsLimit": 5}
)
search_res = requests.post(
    f"https://knowledge.twilio.com/v1/KnowledgeBases/{KB_ID}/Search",
    auth=(account_sid, auth_token),
    json={"query": user_query, "top": 3}
)

customer_history = "\n".join(o["content"] for o in recall_res.json().get("observations", []))
knowledge_chunks = "\n\n".join(c["content"] for c in search_res.json().get("chunks", []))

system_prompt = f"""Customer history:
{customer_history}

Relevant documentation:
{knowledge_chunks}"""
```

### Refresh Stale Web Sources

Re-crawl a web source without changing its config:

```python
requests.patch(
    f"https://knowledge.twilio.com/v1/KnowledgeBases/{kb_id}/Knowledge/{knowledge_id}?refresh=true",
    auth=(account_sid, auth_token),
    json={}
)
# Returns 202 — source re-queued for processing
```

### Filter Search to Specific Sources

When your knowledge base has multiple sources (scripts, FAQs, policies), target search to the relevant one:

```python
results = requests.post(
    f"https://knowledge.twilio.com/v1/KnowledgeBases/{kb_id}/Search",
    auth=(account_sid, auth_token),
    json={
        "query": "cancellation policy",
        "top": 5,
        "knowledgeIds": [policy_knowledge_id]
    }
).json()
```

Omit `knowledgeIds` to search across all sources in the knowledge base.

### Inspect Processed Chunks

To audit what got indexed from a source:

```python
chunks = requests.get(
    f"https://knowledge.twilio.com/v1/KnowledgeBases/{kb_id}/Knowledge/{knowledge_id}/Chunks",
    auth=(account_sid, auth_token),
    params={"pageSize": 50}
).json()

for chunk in chunks["chunks"]:
    print(chunk["content"][:100])
```

---

## CANNOT

- **Cannot add sources before Knowledge Base is active** — Creation is async (returns 202). Poll `Location` header until `status: ACTIVE`.
- **Cannot use one host for all operations** — Management is on `memory.twilio.com`; sources and search are on `knowledge.twilio.com`. Wrong host returns 404.
- **Cannot include auth header when uploading to presigned URL** — `importUrl` is already signed. Adding your auth header will fail.
- **Cannot use expired presigned URLs** — `uploadExpiration` is typically 1 hour. Upload promptly.
- **Cannot search before processing completes** — Web crawl and file indexing are async (seconds to minutes). Poll status first.
- **Cannot use high crawl depth without performance impact** — `crawlDepth` 1–10, default 2. Higher depths dramatically increase processing time.
- **Cannot exceed 16MB per file upload** — Hard limit
- **Cannot exceed 185,000 characters per text source** — Hard limit
- **Cannot retrieve more than 20 search results per query** — `top-K` max is 20
- **Cannot use spaces or underscores in `displayName`** — Alphanumeric and hyphens only (`^[a-zA-Z0-9-]+$`)
- **Cannot use Knowledge for customer-specific context** — Knowledge is shared across all customers. Use `twilio-customer-memory` for per-customer context.
- **Cannot retry FAILED sources** — Delete and recreate. No retry endpoint. Check chunk count after `COMPLETED` to verify extraction.

---

## Next Steps

- **Per-customer context:** `twilio-customer-memory` — combine with Enterprise Knowledge for full agent context (company knowledge + individual customer history)
- **Conversation Intelligence operators with enterprise context:** `twilio-conversation-intelligence` — feed Enterprise Knowledge chunks into Conversation Intelligence operators to give them business context. Examples:
  - **Script Adherence:** index your approved call scripts as a knowledge source; the operator can evaluate agent compliance against the retrieved script for the current conversation type
  - **Custom upsell classifier:** index product offers, pricing tiers, or eligibility rules; a custom classification operator can use retrieved offer details to detect upsell opportunities mid-conversation
  - **Next Best Response:** retrieved policy or FAQ chunks injected alongside the operator prompt improve suggestion quality
- **Wire into a voice AI agent:** `twilio-voice-conversation-relay`
- **TAC SDK integration:** `twilio-agent-connect`
- **Debug integration issues:** `twilio-debugging-observability`
