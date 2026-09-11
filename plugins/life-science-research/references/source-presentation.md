# Source Presentation Contract

This contract applies to every user-facing answer produced with the Life Science
Research plugin. Its governing rule is: **every substantive externally sourced
claim should remain traceable, but not every skill invocation needs a clickable
evidence link.** Keep structured provenance when it is available, then choose
the presentation that matches what the response actually contains.

## Choose the presentation by output mode

| Output mode | User-facing source behavior |
| --- | --- |
| Record or evidence lookup | Put the most specific authoritative link next to the claim or tightly related claim cluster it supports. |
| Search or result list | Link the reproducible query when useful and link only the individual records discussed materially; do not link every returned row by default. |
| Connectivity or schema check | Retain endpoint provenance in structured output or an optional source note, but do not present the endpoint as scientific evidence. |
| Source metadata or service status | Attribute the source once when the metadata matters. Do not invent a record link merely to make the source clickable. |
| Empty result or failed request | Name the attempted source and report the empty result or failure clearly. Do not imply evidentiary support or construct an unsupported record link. |
| Router or planner | Do not add example citations for the routing decision itself. Propagate only sources actually returned by downstream evidence work. |
| Local synthesis or derived analysis | Cite inputs that contributed evidence. Keep queried-but-empty sources in methods, provenance, or limitations rather than attaching them to a result claim. |
| Raw machine-readable output | Preserve the requested payload without injecting Markdown. Keep provenance outside the raw payload when needed. |

## Required behavior

1. For every substantive externally sourced claim, put a source link next to
   the claim or claim cluster it supports. A trailing list of databases that
   were checked is useful for completeness, but it does not replace
   claim-adjacent attribution when an evidence claim was made.
2. When an authoritative public record URL can be constructed, render stable
   publication IDs, accessions, trial IDs, variant IDs, pathway IDs, structure
   IDs, and dataset IDs as Markdown links instead of bare identifiers.
3. Prefer the source's canonical human-readable record page. If the source has
   no stable record page, use the sanitized request URL returned by the skill.
   When only an authoritative source URL is available, link the source name but
   leave the identifier as plain text. If none is available, name the source and
   identifier without inventing a link.
4. Use the `sources` entries returned by scripts as the provenance baseline.
   Preserve them even when an output mode does not call for an inline evidence
   link. Do not claim that a source supports information absent from its
   response.
5. Keep link density readable. One citation may support a tightly related group
   of claims, but each materially different evidence claim needs its own source.
6. Preserve raw JSON, XML, FASTA, CSV, and other explicitly requested
   machine-readable output. Do not inject Markdown into raw payloads.
7. Do not force a claim-adjacent link for routing, connectivity, schema-only,
   empty, or failed work. If useful, identify these sources in a concise
   `Sources checked`, methods, provenance, or limitations note.
8. Deduplicate repeated links in an optional final `Sources` list while keeping
   applicable claim-adjacent links in the body.

## Source-specific rules

Use the current skill's entry in `source-links.json` for display names,
authoritative home pages, canonical record URL templates, and fallback behavior.
Only use a template when its identifier type and required fields match the
record at hand. URL-encode substituted values and apply any transformation
named by the template. When no matching template exists, prefer the script's
sanitized `request_url`, then its authoritative `url` without presenting that
URL as a record-specific link.

## Synthesis rules

When several skills contribute to one answer:

- keep each applicable citation attached to the claim derived from that source;
- preserve source-specific disagreements instead of merging them into a single
  unsupported statement;
- link the primary record rather than a generic database home page whenever
  possible;
- distinguish evidence-contributing sources from sources that were queried but
  returned no relevant evidence; and
- do not create new evidence links that were not supplied by a downstream skill
  or defined in `source-links.json`.

The router itself does not seed an answer with sample citations. If downstream
protein and pathway lookups return substantive records, attach each returned
record link to the corresponding protein-function or pathway claim instead of
listing bare identifiers only at the end.
