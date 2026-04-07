---
name: research-router-skill
description: Route broad or ambiguous life-sciences research requests to the right skills, normalize core entities, optionally parallelize independent evidence gathering with subagents when available, and synthesize a concise evidence-backed answer. Use when a user asks a general life-sciences question that could span multiple sources or analysis types.
---

## Research Router

Use this skill as the default orchestration layer for broad life-sciences research requests.

Do not use it for narrow single-source lookups when a more specific skill already matches the request cleanly.

## Primary Responsibility

Turn an open-ended research question into a small, defensible retrieval plan:

1. understand the research objective
2. normalize the main entities
3. select the minimum useful set of downstream skills
4. gather evidence
5. synthesize the answer for the user

The router owns the framing and the final synthesis. It should not dump raw source payloads unless the user explicitly asks for them.

## When To Use This Skill

Use this skill when any of the following are true:

- the user asks a broad question such as `what is known about ...`
- the question could require more than one evidence type
- the right source is unclear at the start
- the request mixes entities, for example gene plus disease, variant plus phenotype, protein plus ligand, or pathway plus dataset
- the user wants a synthesized answer rather than a single database lookup

## Research Task Classification

Start by classifying the request into one or more lanes:

- human genetics and variant interpretation
- locus-to-gene prioritization
- expression, tissue, or cell-type context
- pathway, network, or functional biology
- protein structure and mechanism
- chemistry, ligands, and pharmacology
- clinical, translational, or cancer evidence
- literature, preprints, and public dataset discovery
- metabolomics, proteomics, or microbiome context

Prefer 1 to 3 lanes. Only expand further if the user explicitly asks for a broad landscape review.

## Entity Normalization

Normalize the key entities before deep retrieval.

Common patterns:

- gene or protein: `ncbi-clinicaltables-skill`, `ensembl-skill`, `uniprot-skill`
- disease or phenotype: `efo-ontology-skill`, `opentargets-skill`
- variant: `clinvar-variation-skill`, `ensembl-skill`, cohort-specific PheWAS skills
- compound or metabolite: `chembl-skill`, `pubchem-pug-skill`, `chebi-skill`, `hmdb-skill`
- pathway or function: `reactome-skill`, `quickgo-skill`, `string-skill`
- accession or dataset identifier: `ncbi-datasets-skill`, `biostudies-arrayexpress-skill`, `pride-skill`, `metabolights-skill`

Do not start broad evidence collection until the important entities are stable enough to route correctly.

## Skill Selection Heuristics

Choose the smallest set of skills that can answer the question well.

Examples:

- target or disease evidence review:
  `opentargets-skill`, `gwas-catalog-skill`, `gtex-eqtl-skill`, `human-protein-atlas-skill`
- variant interpretation:
  `clinvar-variation-skill`, `gnomad-graphql-skill`, `ensembl-skill`, one or more cohort PheWAS skills
- locus-to-gene mapping:
  `locus-to-gene-mapper-skill`, or its component genetics skills when the user wants a custom workflow
- structure and mechanism:
  `alphafold-skill`, `rcsb-pdb-skill`, `uniprot-skill`, `reactome-skill`
- chemistry and pharmacology:
  `chembl-skill`, `bindingdb-skill`, `pubchem-pug-skill`, `pharmgkb-skill`
- clinical and translational:
  `clinicaltrials-skill`, `cbioportal-skill`, `civic-skill`
- literature and dataset discovery:
  `ncbi-entrez-skill`, `ncbi-pmc-skill`, `biorxiv-skill`, `biostudies-arrayexpress-skill`, `ncbi-datasets-skill`

Prefer direct lookups before expensive multi-step chains.

## Subagent And Parallelization Guidance

If Codex subagents are available, use them only when the work cleanly decomposes into independent lanes.

Good candidates for subagents:

- genetics, expression, structure, chemistry, and clinical evidence can be gathered independently for the same question
- multiple loci, variants, genes, compounds, or datasets need parallel comparison
- a broad landscape review requires separate evidence summaries before synthesis

Keep these steps with the coordinating agent:

- initial interpretation of the user request
- entity normalization and final scope decisions
- conflict resolution across evidence sources
- final synthesis and recommendation writing

Avoid subagents when:

- one specific skill already answers the question
- later steps depend tightly on earlier intermediate outputs
- the work is mostly identifier resolution or narrow follow-up lookup
- the extra coordination cost is likely to exceed the retrieval benefit

When delegating, give each subagent a bounded read-only objective such as one evidence family or one comparison unit. Each subagent should return:

- what it checked
- the key findings
- the main caveats
- which skills or sources it used
- any artifact paths it produced

The coordinating agent is responsible for reconciling overlaps, contradictions, and evidence gaps.

## Output Contract

Return a concise answer structured around the user's question, not around the tools.

Unless the user asks for a different format, include:

1. direct answer or working conclusion
2. key evidence by lane
3. main caveats or unresolved questions
4. recommended next analyses or follow-up lookups

If the task is exploratory, explicitly distinguish:

- evidence that supports a conclusion
- evidence that is only suggestive
- evidence that is missing or contradictory

## Operating Rules

- prefer concise source-backed synthesis over large raw dumps
- escalate to multi-skill workflows only when the question requires synthesis
- state important cohort, ancestry, assay, tissue, and study-design limitations
- do not overstate causality from association-only evidence
- if a downstream skill can answer the request directly, hand off to it instead of keeping the router in the foreground
