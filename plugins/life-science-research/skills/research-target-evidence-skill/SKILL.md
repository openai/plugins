---
name: research-target-evidence-skill
description: Produce bounded, source-backed evidence briefs for one or more biological targets, covering biology, therapeutic programs, human safety, preclinical evidence, and cross-target comparison. Use when a user asks for a target assessment, target comparison, translational evidence, program history, modality comparison, or human-versus-preclinical safety review and wants a fast primary-source research pass.
---

## Research Target Evidence

Use the bundled script exactly once for all requested targets. Let it plan,
deduplicate, globally pace, and batch requests across PubMed and
ClinicalTrials.gov.

Do not decompose the request into additional source calls unless the script
returns `ok=false` or the user explicitly asks for a deeper follow-up.

## Execution

For one target, run:

```bash
python scripts/research_target_evidence.py \
  --target "<target>" \
  --questions biology programs safety \
  --separate-human-preclinical
```

For a comparison, repeat `--target` in the same command:

```bash
python scripts/research_target_evidence.py \
  --target "<target 1>" \
  --target "<target 2>" \
  --target "<target 3>" \
  --mode compare \
  --questions biology programs safety \
  --separate-human-preclinical
```

Do not run one process per target. The shared process enforces global source
pacing, preserves landmark-program and evidence-class quotas, and emits a
single size-bounded JSON result.

## Synthesis

- Lead with the target-level conclusion and the largest uncertainty.
- Separate human evidence from preclinical evidence.
- For comparisons, use the same evidence axes for every target and finish with
  a compact comparison of validation, selectivity, safety, modality maturity,
  and uncertainty.
- Cover only modalities supported by the returned papers or trial records.
- Link each PMID as `[PMID <id>](https://pubmed.ncbi.nlm.nih.gov/<id>/)`.
- Link each trial as `[<NCT id>](https://clinicaltrials.gov/study/<NCT id>)`.
- Distinguish observed human toxicity from preclinical or theoretical risk.
- Treat registry adverse-event counts as non-attributed unless the record says
  otherwise.
- Preserve the returned limitations and current registry statuses.
- Report per-target errors or omitted evidence counts rather than silently
  treating a partial result as complete.
- Keep the answer concise enough that the evidence hierarchy remains visible.

The retrieval is bounded and relevance-ranked, not a systematic review. Check
the script's heuristic human/preclinical classification during synthesis. Do
not include retrieval telemetry in the user-facing brief unless requested.
