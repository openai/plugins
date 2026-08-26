---
name: box-legal-workflows
description: Shared building blocks for Box-based legal workflows — Box collaboration role definitions, Box AI usage boundaries (what AI must not decide), and reusable human-in-the-loop confirmation phrasings. Referenced by box-legal-workflows-ma, box-legal-workflows-intake, and box-legal-workflows-contract skills.
---

# Shared Legal Concepts

> **PREREQUISITE:** Read [Box foundation skill](../box/SKILL.md) for Box MCP authentication, tool selection, and base workflows.

Shared building blocks used by the legal skills (M&A, Intake, Contract Review): Box collaboration role definitions, the boundaries of where Box AI must not be the decision-maker, and reusable confirmation phrasings. Risk frameworks, metadata fields, workflows, and decision-transparency requirements live in the individual legal skills.

## Box capability references

Reach for these for the underlying Box tool mechanics rather than restating them here:

- `../box/references/collaboration.md` — collaborator role capabilities, shared links, and external-sharing rules
- `../box/references/ai-and-retrieval.md` — Box AI Q&A, extraction, and structured metadata tools, with pacing/limits/citations

---

## Box Collaboration Roles

**[CONFIRM: What permission level is appropriate?]**

For the full breakdown of each Box collaborator role (Co-owner, Editor, Viewer Uploader, Previewer Uploader, Viewer, Previewer, Uploader) and the exact capabilities each grants, see the role matrix in `../box/references/collaboration.md`. Use that matrix to determine which role fits a given collaborator, then have the human confirm the choice before granting access.

Apply least privilege: default to the most restrictive role that still lets the collaborator do their job, prefer specific folders over root access, and set expiration dates on external collaborations.

---

## Box AI Boundaries

Box AI informs; a human attorney decides. Do **NOT** use Box AI for:

- Final legal advice or decisions (human attorney only)
- Access-control decisions (human approves permissions)
- Client conflict checks (use the firm's conflict system)
- Privilege determinations (attorney judgment)
- Settlement negotiations or strategy

Box AI is appropriate for *informing* humans — completeness checks, risk-factor flagging, metadata extraction, contract comparison, and due-diligence Q&A — always with citations surfaced and a human making the final call.

For details on the Box AI tools available and how to use them, see `../box/references/ai-and-retrieval.md`.

---

## Common Confirmation Patterns

Reusable phrasings for the human-in-the-loop confirmations the legal skills require.

### Risk Rating
"Here are the factors I found: [...], with citations from Box. Under your firm's criteria, which rating applies?" (The agent presents facts; the firm's criteria and attorney determine the rating.)

### Permissions
"I'll grant [person] [role] access to [folder/file]. They can [permissions]. Proceed?"

### Routing
"Based on [practice area/risk/type], I recommend routing to [attorney]. Correct, or assign to someone else?"

### Document Completeness
"Firm requires: [list]. Found: [list]. Missing: [list]. Proceed with assessment?"

### Metadata Template
"Do you have a Box metadata template for [type]? If yes, scope and template key?"

### Thresholds
"What is your firm's threshold for [matter value/expiration alert/risk escalation]?"

### External Sharing
"Before sharing with [external party], confirm: (1) Permission level? (2) Folders? (3) Expiration? (4) Link or collaboration?"
