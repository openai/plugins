# Meeting Prep Dashboard Pack

Use this pack only when the user explicitly requests a standardized dashboard, reusable dashboard template, or structured payload-driven render for Public Equity Investing meeting prep. Ordinary substantive or explicitly requested HTML meeting briefs should use the flexible standalone HTML live-meeting brief in `../SKILL.md` instead.

## Producer Role

`meeting-prep` owns meeting objective, context synthesis, question prioritization, evidence requests, safety/circulation posture, and follow-up logic. `dashboard-builder` owns the shared HTML shell, module rendering, responsive layout, citation behavior, and validation.

## Recommended Payload

- `mode`: `meeting_prep`
- `layout`: `single_page` for reusable prep packets unless the user explicitly requests tabs
- `hero.callout`: what decision or information the meeting must unlock
- `snapshot`: meeting type, audience, objective, highest-impact question, top evidence gap, follow-up owner/status if known
- `snapshot`: include explicit mode such as `management_ir`, `expert_call`, `pm_internal_review`, `sell_side_call`, `earnings_call`, `investor_day`, `portfolio_watchlist_review`, or `model_review`
- `sources`: prompt/user artifacts first, connected-app context only when actually available, then filings, market data, research artifacts, and assumptions
- Raw JSON, Markdown notes, CSV exports, and run logs are support/audit material unless the user explicitly asks for them.

## Tabs And Modules

1. `meeting-frame`
   - `decision_box`: objective, one-sentence investor stance, desired decision, opening frame, and what would make the meeting successful
   - `metric_tiles`: meeting type, audience, date/window if known, issuer/security, confidence, key source gap
   - For a standardized live-meeting dashboard, place the compact conversation-flow object before detailed question modules.
2. `must-know-context`
   - `executive_summary`: concise context pack with only the known facts, assumptions, and why-now framing needed for the meeting plan
   - `cards`: likely agenda, decision frame, risks to avoid, and circulation/safety notes
3. `questions`
   - `question_list`: three or four must-ask questions ranked by decision impact with concise why-it-matters, listen-for, evasive-answer follow-up, model/thesis implication, and evidence-request fields; place secondary questions in `If Time Permits`
4. `pushbacks-actions`
   - `table`: likely pushbacks, suggested responses, what not to ask/say, evidence support, and follow-up owner/timing when available
   - `timeline`: follow-up actions, commitments, dependencies, and review dates
5. `open-gaps`
   - `missing_evidence`: missing sources, meeting details, model files, prior notes, market data, or evidence requests

The source tab is normally generated from top-level `sources`.

## Required Evidence

- Production dashboard payloads must include `metadata.payload_stage: "production"`, `mode`, `layout`, `hero`, non-empty `snapshot`, `sources`, `metadata.freeze_time`, `metadata.source_posture`, `metadata.readiness_label`, `metadata.readiness_posture`, `metadata.decision_context`, and `metadata.citation_policy: "strict"`.
- Use `metadata.payload_stage: "draft"` or `"support"` with `metadata.citation_policy: "warn"` only for internal support payloads; final HTML/XLSX/chat handoffs must keep gaps visible and must not claim PM-ready, client-ready, committee-ready, external, or publication-ready status.
- Cite every verified fact, metric, meeting date/time, claim from prior artifacts, and source-backed context item.
- Label assumptions and connector availability. Do not imply calendar, email, Slack, Drive, market-data, or research connectors are available unless they are.
- Use `metadata.citation_policy: "strict"` for production dashboards.

## Do Not

- Do not modify source artifacts unless the user asks.
- Do not include internal strategy, restricted information, or trading intent in external-clean materials without explicit direction.
- Do not make raw JSON, Markdown notes, or CSV sidecars the lead user-facing artifact unless explicitly requested.
- Do not turn a live meeting plan into an earnings deep dive or render a long list of equally weighted questions.

## QA Checks

- Validate with `skills/public-equity-investing/internal-support/dashboard-builder/scripts/validate_payload.py`.
- Confirm objective, facts versus assumptions, source gaps, ranked questions, evidence requests, pushbacks, and follow-ups are visible.
- Confirm circulation-sensitive content is labeled or removed for external-facing prep.
