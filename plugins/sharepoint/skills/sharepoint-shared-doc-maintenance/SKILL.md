---
name: sharepoint-shared-doc-maintenance
description: Maintain shared SharePoint strategy, roadmap, planning, or status documents from changing source documents. Use when the user wants cross-document synthesis, source-of-truth propagation, or targeted updates to a maintained shared document.
---

# SharePoint Shared Doc Maintenance

## Overview

Use this skill when the job is not just editing one document, but keeping a maintained shared document aligned with newer source documents. Optimize for finding the real delta and applying the smallest necessary patch.

## Core Workflow

1. Identify the maintained document.
2. Identify the likely source documents that feed it.
3. Compare timestamps so you know which sources changed after the maintained document's last update.
4. Fetch only the maintained document plus the changed source docs.
5. Extract the concrete delta:
   - timeline shifts
   - milestone changes
   - new risks
   - updated owners
   - revised launch dates
   - removed commitments
6. Decide whether the maintained document needs:
   - no change
   - a targeted insertion
   - a broader section rewrite
7. Apply the smallest edit that fully propagates the source change.
8. Re-fetch and verify that the maintained document now reflects the new source-of-truth details in the right section.

## Synthesis Rules

- Treat maintenance as a distinct workflow, not as generic document summarization.
- For roadmap and milestone maintenance, prefer concrete propagation over broad re-summarization.
- Use modification timestamps as a triage tool, not as proof of substantive change.
- For multi-document synthesis requests, verify the source set before writing. If the user asks for a consolidated strategy or a summary of all related materials, enumerate the source documents explicitly and verify that likely variants were not skipped.
- Even if you expect only one source to have changed, enumerate the source set so you do not miss a second updated input.

## Verification

- Verification should confirm both the new fact and its placement in the document.
- Do not stop at proving a changed year, date, or milestone appears somewhere. Confirm it appears in the roadmap, recommendations, timing discussion, or risk framing where readers would expect it.
- If the maintained document is already on a low-fidelity fallback format because of connector limits, favor precise content patches over broad structural rewrites.

## Recovery Notes

- Optimize for quick triage:
  - list likely source docs once
  - use modification times to narrow the fetch set
  - fetch only the maintained doc plus changed sources
  - extract the exact delta before editing
  - avoid rewriting unaffected sections
- If a changed source contains a strong explicit marker such as `UPDATE`, `TIMELINE CHANGED`, revised year ranges, or renamed milestones, treat that as a high-confidence propagation target.
