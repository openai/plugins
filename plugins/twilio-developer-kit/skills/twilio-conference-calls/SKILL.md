---
name: twilio-conference-calls
description: >
  Build multi-party calls using Twilio Conference. Covers warm transfer,
  cold transfer, coaching (whisper), hold vs mute, participant modes, and
  supervisor barge. Use this skill for any contact center, support line,
  or scenario requiring transfers, holds, or multi-party calls.
---

## Overview

Conference is the foundation of contact center call handling. The key insight: **every call that might need a transfer should start as a Conference**, not a direct `<Dial>`. A Conference supports hold, transfer, coaching, and recording — a direct Dial does not.

```
Caller ──→ Conference Room ←── Agent
                  ↑
              Supervisor (coach mode: speaks to agent only)
```

**Contact center best practice:** Every multi-agent call should use Conference, not direct Dial.

---

## Prerequisites

- Twilio account with a voice-capable phone number — see `twilio-account-setup`
- `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` — see `twilio-iam-auth-setup`
- SDK: `pip install twilio` / `npm install twilio`
- For agent routing: TaskRouter — see `twilio-taskrouter-routing`

---

## Quickstart

**Step 1 — Put the inbound caller into a Conference**

When a call comes in, place the caller into a named Conference room.

**Python (Flask)**
```python
from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse

app = Flask(__name__)

@app.route("/voice", methods=["POST"])
def incoming_call():
    call_sid = request.form["CallSid"]
    response = VoiceResponse()
    dial = response.dial()
    dial.conference(
        f"room-{call_sid}",
        start_conference_on_enter=True,
        end_conference_on_exit=False,  # Keep conference alive when caller disconnects (for wrap-up)
        wait_url="http://twimlets.com/holdmusic?Bucket=com.twilio.music.classical",
        status_callback="https://yourapp.com/conference-events",
        status_callback_event="join leave",
        record="record-from-start"
    )
    return str(response)
```

**Node.js (Express)**
```node
app.post("/voice", (req, res) => {
    const callSid = req.body.CallSid;
    const response = new VoiceResponse();
    const dial = response.dial();
    dial.conference(
        `room-${callSid}`,
        {
            startConferenceOnEnter: true,
            endConferenceOnExit: false,
            waitUrl: "http://twimlets.com/holdmusic?Bucket=com.twilio.music.classical",
            statusCallback: "https://yourapp.com/conference-events",
            statusCallbackEvent: "join leave",
            record: "record-from-start",
        }
    );
    res.type("text/xml").send(response.toString());
});
```

**Step 2 — Connect an agent to the same Conference**

After TaskRouter assigns a worker, dial the agent into the conference:

> **Security:** Never interpolate untrusted user input into inline `twiml=` strings. Use the SDK's `VoiceResponse` builder for any dynamic content.

**Python**
```python
# Called from your assignment callback or agent connect logic
def connect_agent(conference_name, agent_phone):
    client.calls.create(
        to=agent_phone,
        from_="+15551234567",  # your Twilio number
        twiml=f'''<Response>
            <Dial>
                <Conference>{conference_name}</Conference>
            </Dial>
        </Response>''',
        status_callback="https://yourapp.com/agent-call-status"
    )
```

**Node.js**
```node
async function connectAgent(conferenceName, agentPhone) {
    await client.calls.create({
        to: agentPhone,
        from: "+15551234567",
        twiml: `<Response><Dial><Conference>${conferenceName}</Conference></Dial></Response>`,
        statusCallback: "https://yourapp.com/agent-call-status",
    });
}
```

---

## Key Patterns

### Warm Transfer

Put caller on hold → dial new agent into Conference → original agent briefs new agent → original agent drops.

**Python**
```python
def warm_transfer(conference_sid, original_agent_call_sid, new_agent_phone, conference_name):
    # Step 1: Put caller on hold (hold = hears music, can't hear agents)
    caller_participant = client.conferences(conference_sid) \
        .participants(caller_call_sid) \
        .update(hold=True)

    # Step 2: Dial new agent into the same conference
    client.calls.create(
        to=new_agent_phone,
        from_="+15551234567",
        twiml=f'<Response><Dial><Conference>{conference_name}</Conference></Dial></Response>',
        status_callback="https://yourapp.com/transfer-agent-status"
    )

    # Step 3: Original agent briefs new agent (caller is on hold, can't hear)
    # ... agents talk ...

    # Step 4: Take caller off hold
    client.conferences(conference_sid) \
        .participants(caller_call_sid) \
        .update(hold=False)

    # Step 5: Original agent leaves
    client.conferences(conference_sid) \
        .participants(original_agent_call_sid) \
        .update(status="completed")  # Removes from conference
```

### Cold Transfer

Simpler — just redirect the caller to a new agent without briefing.

**Python**
```python
def cold_transfer(conference_sid, original_agent_call_sid, new_agent_phone, conference_name):
    # Remove original agent
    client.conferences(conference_sid) \
        .participants(original_agent_call_sid) \
        .update(status="completed")

    # Dial new agent into conference
    client.calls.create(
        to=new_agent_phone,
        from_="+15551234567",
        twiml=f'<Response><Dial><Conference>{conference_name}</Conference></Dial></Response>'
    )
```

### Hold vs Mute

| Feature | Hold | Mute |
|---------|------|------|
| Participant hears | Hold music | Everything (but can't speak) |
| Other participants hear | Nothing from held party | Nothing from muted party |
| Use when | Transfer briefing, agent lookup | Quick aside (agent mutes self to cough) |
| API | `hold=True` | `muted=True` |

```python
# Hold — plays music to the held participant
client.conferences(conf_sid).participants(participant_sid).update(hold=True)
client.conferences(conf_sid).participants(participant_sid).update(hold=False)

# Mute — silences the participant but they still hear
client.conferences(conf_sid).participants(participant_sid).update(muted=True)
client.conferences(conf_sid).participants(participant_sid).update(muted=False)
```

**Critical distinction:** Hold plays music. Mute just silences. Using mute when you mean hold exposes agent-side conversations to the caller.

### Coaching (Supervisor Whisper)

Supervisor joins the Conference and can speak to the agent only — the caller cannot hear the supervisor.

**Python**
```python
def add_coach(conference_sid, supervisor_phone, conference_name):
    """Add supervisor as coach — speaks to agent only, caller can't hear."""
    client.calls.create(
        to=supervisor_phone,
        from_="+15551234567",
        twiml=f'''<Response>
            <Dial>
                <Conference
                    coach="{agent_call_sid}"
                    statusCallback="https://yourapp.com/coach-events"
                >{conference_name}</Conference>
            </Dial>
        </Response>'''
    )
```

**Node.js**
```node
async function addCoach(conferenceSid, supervisorPhone, conferenceName, agentCallSid) {
    await client.calls.create({
        to: supervisorPhone,
        from: "+15551234567",
        twiml: `<Response>
            <Dial>
                <Conference coach="${agentCallSid}">${conferenceName}</Conference>
            </Dial>
        </Response>`,
    });
}
```

**Coach behavior:**
- Supervisor hears both caller and agent
- Supervisor can speak to agent only (caller cannot hear)
- Coach audio is NOT captured in conference recording — record separately if needed
- To switch from coach to barge (speak to everyone), update the participant

### Supervisor Barge

Supervisor joins and speaks to everyone — useful for escalation or takeover.

```python
def barge_in(conference_sid, supervisor_phone, conference_name):
    """Supervisor joins as full participant — everyone hears them."""
    client.calls.create(
        to=supervisor_phone,
        from_="+15551234567",
        twiml=f'<Response><Dial><Conference>{conference_name}</Conference></Dial></Response>'
    )
```

### Participant Management

```python
# List all participants in a conference
participants = client.conferences(conference_sid).participants.list()
for p in participants:
    print(f"CallSid: {p.call_sid}, Muted: {p.muted}, Hold: {p.hold}")

# Remove a participant
client.conferences(conference_sid).participants(call_sid).update(status="completed")

# End the entire conference
client.conferences(conference_sid).update(status="completed")
```

---

## Gotchas

### 1. Conference Requires 2+ Participants to "Exist"

A Conference with only one participant is in a waiting state. The single participant hears hold music. API calls to the Conference may behave unexpectedly until a second participant joins.

### 2. Coach Audio Not in Recording

Conference recordings capture the main audio mix only. Coach/whisper audio is NOT recorded. If you need to record coaching sessions for QA, add a separate recording on the supervisor's call leg.

### 3. endConferenceOnExit Behavior

If `endConferenceOnExit=True` for any participant, the conference ends when they leave — dropping all other participants. Set this carefully:
- Caller: Usually `False` (so agents can wrap up)
- Agent: Usually `False` (so caller can be transferred)
- Supervisor: Always `False`

### 4. Conference Name Is Account-Scoped

Conference names must be unique within your account at any given time. Use a unique identifier (like CallSid) in the name to prevent collisions:
```python
conference_name = f"room-{call_sid}"  # unique per call
```

---

## CANNOT

- **Cannot use `<Gather>` inside a Conference** — DTMF goes into the audio mix, not a handler. Gather before joining the conference.
- **Cannot rely on speaker events for app logic** — Speaker events fire too frequently to be actionable in real-time routing.
- **Cannot get post-flight participant data from REST API** — Completed conferences return empty participant lists. Use Voice Insights for historical data.
- **Coach audio is NOT in the conference recording** — Supervisor whisper audio is excluded from the recorded mix. Record the supervisor's call leg separately if needed.
- **Cannot filter Insights list endpoint by `processing_state`** — Must fetch by Conference SID directly.
- **Cannot use PII in `friendlyName`** — Compliance requirement, not just a suggestion.
- **Cannot create a conference with 0 call legs and get Insights data** — Insights requires at least 1 participant call attempt.
- **Cannot poll Insights immediately after conference end** — Takes 15-30+ minutes for data to appear, even for `in_progress` state.
- **Cannot exceed 250 participants per conference** — Hard limit
- **Cannot pre-add phone numbers to a conference** — Participants must be active calls
- **Cannot use a private URL for hold music** — Hold music URL must be publicly accessible
- **Cannot get per-participant recordings from conference recording** — Recording is per-conference (mono mixed). Use dual-channel recording for QA — see `twilio-call-recordings`

---

## Next Steps

- **Route calls to agents:** `twilio-taskrouter-routing`
- **Record calls:** `twilio-call-recordings`
- **IVR before conferencing:** `twilio-voice-twiml`
- **AI agent with escalation:** `twilio-voice-conversation-relay`
