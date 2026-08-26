# Fictional Salesforce Sample Records

This file contains hand-authored fictional demo records. It is not a Salesforce export, connector response, live CRM search, or real customer dataset.

## Portfolio Summary

| Rank | Account | Opportunity | Motion | Stage | Account owner | Primary contact | Current posture |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Northstar Health | $420,000 | Expansion | Security review | Riley Morgan | Jordan Lee, VP Clinical Operations | Executive decision pending |
| 2 | Atlas Manufacturing | $680,000 | Expansion | Commercial alignment | Riley Morgan | Morgan Ellis, Chief Digital Officer | Investment committee next Tuesday |
| 3 | Solstice Financial | $310,000 | Expansion | Pilot conversion | Riley Morgan | Dana Kim, SVP Advisor Operations | Executive pilot review Friday |
| 4 | Redwood Retail | $185,000 | Renewal and expansion | Renewal review | Riley Morgan | Avery Brooks, VP Retail Operations | Renewal checkpoint Monday |
| 5 | BluePeak Logistics | $265,000 | New logo | Executive decision | Riley Morgan | Cameron Ruiz, Chief Operating Officer | Rollout owner unconfirmed |
| 6 | Harbor Technologies | $235,000 | New logo | Stakeholder mapping | Riley Morgan | Quinn Foster, Director of Engineering | Executive sponsor unconfirmed |
| 7 | Meridian University | $160,000 | Expansion | Budget planning | Riley Morgan | Sofia Martinez, AVP Digital Strategy | Funding window not open |
| 8 | Juniper Bio | $205,000 | New logo | Technical validation | Riley Morgan | Harper Wells, VP Research Operations | Architecture review in progress |
| 9 | Ember Energy | $390,000 | Expansion | Procurement hold | Riley Morgan | Blair Hughes, Director Operational Excellence | Customer purchasing freeze |
| 10 | Lattice Public Sector | $520,000 | New logo | Active internal coordination | Riley Morgan | Jamie Carter, Deputy Director Digital Services | Another seller owns current outreach |

## Northstar Health Opportunity Detail

- Fictional opportunity name: Northstar Health — FY{{fiscal_year}} Governed Workflow Expansion.
- Annual recurring opportunity value: $420,000.
- Current stage: Security review.
- Forecast close date: {{next_thursday}}; resolve from the user's current local date.
- Current customer footprint: 1,200 pilot users.
- Proposed deployment footprint: approximately 4,500 employees.
- Executive sponsor: Jordan Lee, Vice President of Clinical Operations.
- Security decision-maker: Casey Patel, Director of Information Security.
- Account owner: Riley Morgan.
- Solutions engineer: Priya Shah.
- Open CRM next step: validate the original pilot goals and unresolved customer uptime feedback before the Thursday decision meeting; address supporting audit and retention questions.
- Current Salesforce `NextStep`: Validate pilot success and open uptime feedback before the decision meeting.
- Current forecast category: Best Case.
- Current deal note: Pilot-readiness and uptime questions pending before expansion decision.
- Current decision criteria: Pilot success and Security review required.
- Current risk: Customer uptime feedback pending validation.
- Post-meeting review posture: prepare a field-level proposal grounded in the Northstar transcript; preserve `StageName`, `Amount`, `CloseDate`, forecast category, and owner until a supported business event and explicit user approval justify a change.
- Forecast posture: plausible expansion decision; not signed, closed, or guaranteed.

### Current Fictional Opportunity Fields Before Meeting Follow-up

These are illustrative current values for the completed-meeting update preview, not a real Salesforce record or a verified schema.

| Field | Current fictional value |
| --- | --- |
| `Id` | `DEMO-NORTHSTAR-OPPORTUNITY` — fictional placeholder; never use for a live write |
| `Name` | Northstar Health — FY{{fiscal_year}} Governed Workflow Expansion |
| `Amount` | $420,000 |
| `StageName` | Security review |
| `CloseDate` | {{next_thursday}} |
| `NextStep` | Validate pilot success and open uptime feedback before the decision meeting. |
| `Decision_Criteria_Purchase_Process__c` | Pilot success and Security review required. |
| `Risks_and_Asks__c` | Customer uptime feedback pending validation. |
| `Manager_Notes__c` | Pilot-readiness and uptime questions pending before expansion decision. |
| Forecast category | Best Case; final buying decision and security approval are not confirmed. |

Meeting-driven update logic lives in `../crm-update-rules.md`. Keep opportunity amount, current stage, close date, forecast category, and ownership unchanged unless customer-backed evidence and a separate approved live action justify them.

## Atlas Manufacturing Opportunity Detail

- Fictional opportunity name: Atlas Manufacturing — FY{{fiscal_year}} Multi-Plant Governed Operations Expansion.
- Annual recurring opportunity value: $680,000.
- Current stage: Commercial alignment.
- Account owner: Riley Morgan.
- Executive sponsor: Morgan Ellis, Chief Digital Officer.
- Implementation stakeholder: Taylor Reed.
- Documented commercial milestone: the investment committee meets Tuesday, with preparation scheduled Monday.
- Open qualification gap: exact services scope and implementation ownership are not yet confirmed.

## Solstice Financial Opportunity Detail

- Fictional opportunity name: Solstice Financial — FY{{fiscal_year}} Advisor Operations Pilot Conversion.
- Annual recurring opportunity value: $310,000.
- Current stage: Pilot conversion.
- Account owner: Riley Morgan.
- Executive sponsor: Dana Kim, SVP Advisor Operations.
- Technology-risk reviewer: Reese Bennett.
- Documented commercial milestone: Friday executive pilot review.
- Open qualification gap: role-based access for advisor and operations groups.

## Harbor Technologies Stakeholder Change

- Fictional opportunity name: Harbor Technologies — FY{{fiscal_year}} Engineering Knowledge Platform.
- Fictional opportunity value: $235,000.
- Technical champion: Quinn Foster, Director of Engineering.
- Former executive sponsor: Elena Torres.
- Replacement executive sponsor: not yet identified.
- Outreach posture: no new executive sequence until ownership and an approved path are confirmed.
