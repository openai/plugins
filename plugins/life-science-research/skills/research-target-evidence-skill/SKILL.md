---
name: research-target-evidence-skill
description: Produce a bounded, source-backed evidence brief for a biological target, covering biology, therapeutic programs, human safety, and preclinical evidence. Use when a user asks for a target assessment, translational evidence, program history, modality comparison, or human-versus-preclinical safety review and wants a fast primary-source research pass.
---

## Research Target Evidence

Use the bundled script exactly once for the requested target. Let it plan,
deduplicate, pace, cache, and batch requests across PubMed and
ClinicalTrials.gov.

Do not decompose the request into additional source calls unless the script
returns `ok=false` or the user explicitly asks for a deeper follow-up.

## Execution

Extract the target and requested evidence axes, then run:

```bash
python scripts/research_target_evidence.py \
  --target "<target>" \
  --questions biology programs safety \
  --separate-human-preclinical
```

The script uses a six-hour response cache by default. Use `--cache-mode off`
when the user explicitly needs a fresh retrieval.

## Synthesis

- Lead with the target-level conclusion and the largest uncertainty.
- Separate human evidence from preclinical evidence.
- Cover only modalities supported by the returned papers or trial records.
- Link each PMID as `[PMID <id>](https://pubmed.ncbi.nlm.nih.gov/<id>/)`.
- Link each trial as `[<NCT id>](https://clinicaltrials.gov/study/<NCT id>)`.
- Distinguish observed human toxicity from preclinical or theoretical risk.
- Treat registry adverse-event counts as non-attributed unless the record says
  otherwise.
- Preserve the returned limitations and current registry statuses.
- Keep the answer concise enough that the evidence hierarchy remains visible.

The retrieval is bounded and relevance-ranked, not a systematic review. Check
the script's heuristic human/preclinical classification during synthesis. Do
not include retrieval telemetry in the user-facing brief unless requested.
