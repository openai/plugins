# Life Science: Research Plugin

This plugin is a general life-sciences research layer for Codex. It packages a broad set of modular skills that can be composed to answer questions across human genetics, functional genomics, expression, pathway biology, protein structure, chemistry, clinical evidence, and public study discovery.

The goal is not to force every request through one fixed workflow. The goal is to help Codex understand the user's research question, normalize the relevant entities, choose the smallest useful set of skills, and synthesize a concise evidence-backed answer.

The plugin now includes a `research-router-skill` that should be treated as the default entrypoint for broad, ambiguous, or multi-step life-sciences research tasks.

## What This Plugin Should Do

When a user invokes this plugin, treat it as a general research copilot for life sciences:

1. Understand the research task.
   Determine whether the user is asking for gene or target background, variant interpretation, locus-to-gene prioritization, pathway context, expression profiling, structure lookup, chemistry or ligand evidence, clinical-trial landscape, literature discovery, or dataset discovery.
2. Normalize the core entities.
   Resolve the gene, protein, disease, phenotype, variant, compound, tissue, cell type, species, accession, or pathway identifiers before branching into downstream lookups.
3. Route to the right skills.
   Prefer the minimum number of skills needed to answer the question well. Use single-source lookups for focused questions and multi-skill chains only when the question requires synthesis.
4. Parallelize only when it helps.
   If the work breaks into independent evidence lanes and Codex subagents are available, use them for bounded parallel retrieval and analysis. Keep initial scoping, entity normalization, and final synthesis with the coordinating agent.
5. Cross-check evidence across sources.
   Where the answer matters, compare orthogonal evidence types instead of over-indexing on one source.
6. Synthesize for the user.
   Return a concise research answer with the key evidence, important caveats, and clear next steps. Save raw payloads only when the user asks for them.

## Research Patterns

This plugin is meant to support workflows like:

- target and gene background research
- variant interpretation and identifier resolution
- locus-to-gene prioritization
- cohort replication and PheWAS follow-up
- expression and tissue or cell-type context
- pathway and network interpretation
- protein, structure, and function lookup
- chemistry, ligand, and pharmacology research
- clinical, translational, and cancer evidence review
- literature, preprint, and public dataset discovery
- metabolomics, proteomics, and microbiome context gathering

## Entry Point

- `research-router-skill`: the default orchestration layer for broad life-sciences questions. It classifies the request, normalizes entities, selects downstream skills, decides whether parallel subagents are useful, and synthesizes the final answer.

## Skill Families

The plugin currently bundles 50 skills. The most useful way to think about them is by research area rather than as a flat list.

### Human Genetics And Variant Evidence

- `opentargets-skill`
- `gwas-catalog-skill`
- `clinvar-variation-skill`
- `gnomad-graphql-skill`
- `ensembl-skill`
- `eva-skill`
- `epigraphdb-skill`
- `genebass-gene-burden-skill`
- `gtex-eqtl-skill`
- `eqtl-catalogue-skill`
- `locus-to-gene-mapper-skill`
- `finngen-phewas-skill`
- `ukb-topmed-phewas-skill`
- `biobankjapan-phewas-skill`
- `tpmi-phewas-skill`

### Expression, Cell Context, And Functional Genomics

- `bgee-skill`
- `human-protein-atlas-skill`
- `cellxgene-skill`
- `encode-skill`
- `rnacentral-skill`

### Protein, Structure, Pathway, And Functional Biology

- `alphafold-skill`
- `rcsb-pdb-skill`
- `uniprot-skill`
- `string-skill`
- `quickgo-skill`
- `reactome-skill`
- `rhea-skill`

### Chemistry, Metabolites, And Pharmacology

- `bindingdb-skill`
- `chembl-skill`
- `pubchem-pug-skill`
- `chebi-skill`
- `pharmgkb-skill`
- `hmdb-skill`

### Clinical, Translational, And Disease Evidence

- `clinicaltrials-skill`
- `cbioportal-skill`
- `civic-skill`
- `ipd-skill`

### Literature, Search, And Public Study Discovery

- `ncbi-entrez-skill`
- `ncbi-pmc-skill`
- `biorxiv-skill`
- `biostudies-arrayexpress-skill`
- `ncbi-datasets-skill`
- `ncbi-blast-skill`
- `ncbi-clinicaltables-skill`

### Multi-Omics, Proteomics, And Specialized Data Sources

- `pride-skill`
- `proteomexchange-skill`
- `metabolights-skill`
- `mgnify-skill`
- `efo-ontology-skill`

## Recommended Query Strategy

For broad or ambiguous requests, route work in this order:

1. Clarify the objective from the user prompt.
   Is the user trying to explain biology, prioritize targets, interpret a variant, find public evidence, or discover studies and datasets?
2. Resolve identifiers and ontology terms first.
   Use entity-normalization and ontology skills before deeper evidence retrieval.
3. Pull evidence from the smallest relevant set of source families.
   For example:
   genetics plus expression for target prioritization
   structure plus chemistry for ligandability questions
   literature plus datasets for exploratory research
   clinical plus pharmacology for translational questions
4. Parallelize only if the evidence lanes are independent.
   Good examples include genetics versus expression, structure versus chemistry, or literature versus clinical evidence for the same question. Avoid parallelization for narrow lookups or tightly coupled chains where every step depends on the previous one.
5. Reconcile disagreements.
   Call out conflicts across datasets, ancestry limitations, tissue specificity, study design caveats, and evidence gaps.
6. End with a direct synthesis.
   Answer the user's actual question instead of returning an unsorted dump of source results.

## Subagent Guidance

When Codex subagents are available, use them as a retrieval and analysis accelerator, not as a replacement for core reasoning.

Use subagents when:

- the request spans multiple evidence families that can be gathered independently
- several genes, variants, compounds, or datasets need side-by-side comparison
- a broad research brief benefits from separate lane summaries before synthesis

Keep the coordinating agent responsible for:

- interpreting the user request
- defining scope and analysis lanes
- resolving identifiers and canonical entities
- reconciling conflicting evidence
- writing the final synthesis

Each subagent should receive a bounded objective and return concise findings, caveats, sources used, and any artifact paths. The final answer should present one integrated conclusion rather than a stack of disconnected sub-results.

## Example Prompts

- `Use Life Science: Research to summarize the public genetics and expression evidence linking IL6R to asthma.`
- `Find preprints, public datasets, and pathway context relevant to TREM2 in microglia.`
- `Map the most plausible causal genes at this inflammatory bowel disease locus and explain why.`
- `Summarize known structure, ligand, and pathway information for EGFR.`
- `Pull ClinicalTrials.gov, ChEMBL, and PharmGKB context for JAK inhibitors in alopecia areata.`
- `Find metabolomics and proteomics resources relevant to MASLD and PPARG.`
- `Interpret this variant using ClinVar, gnomAD, Ensembl, and cohort association evidence.`

## Operational Notes

The plugin does not require plugin-local app connectors or MCP servers. The bundled skills are self-contained under `plugins/life-science-research/skills/` and generally call their own scripts or public APIs directly.

This plugin should be treated as a routing and synthesis layer over those skills. A focused question may require only one skill. A broader research question may require a short multi-skill chain, and when the work splits naturally into independent lanes, optional subagent-assisted parallel analysis before final synthesis.
