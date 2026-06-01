# Formats and Interchange

## Purpose

Use this reference when reading, writing, converting, embedding, or round-tripping UML and UML-like diagrams. Treat each format as a contract with different semantic depth, layout fidelity, and tool compatibility.

## Format Defaults

- XMI: formal XML Metadata Interchange for MOF/UML-style model exchange. Use when semantic model interchange matters. Preserve IDs and UUIDs. Expect vendor profiles, tool extensions, and partial loss when moving between modeling tools.
- UMLDI: UML Diagram Interchange metamodel. Use alongside UML XMI when diagram geometry and visual presentation need to travel with model semantics.
- PlantUML: practical text DSL for sequence, use case, class, object, activity, component, deployment, state, timing, ER, network, ArchiMate-like, and many non-UML diagrams. Good for docs, CI, and source control.
- Mermaid: lightweight Markdown-friendly diagrams for flowcharts, sequence, class, state, ER, C4, architecture, timeline, user journey, Gantt, and more. Good for documentation sites and quick web embeds.
- Graphviz DOT: graph description language and layout system. Use for dependency graphs, hierarchy, package/module maps, and generated static layouts.
- D2: declarative diagramming language with strong styling, themes, UML class support, tables, icons, and architecture diagrams.
- Structurizr DSL: model-as-code for C4. Prefer when multiple C4 views should come from one reusable architecture model.
- DBML: database markup language for schema diagrams, tables, columns, indexes, enums, notes, and relationships.
- BPMN XML: business process interchange with process semantics and diagram interchange. Use when process tooling or execution workflow matters.
- diagrams.net/draw.io: visual diagram files, often XML/mxfile based. Use for compatibility with visual editing workflows, but avoid treating the image layout as the only source of truth for generated systems.
- SVG/PNG/PDF: output formats, not semantic source formats. SVG is preferred for crisp docs and accessible text where tooling preserves it. PNG is safest for slides and office docs. PDF is useful for print or report pipelines.
- JSON graph model: use for product diagram surfaces. Include semantic node/edge types, source IDs, layout hints, and validation diagnostics instead of relying only on renderer-specific objects.

## Reading Rules

- Identify whether the input is semantic model, diagram source DSL, rendered output, or visual-editor artifact.
- Preserve source IDs, names, namespaces, stereotypes, tags, relationship labels, and cardinality.
- Record which relationships are explicit, inferred, generated, or omitted.
- Treat layout coordinates as hints unless the user asks for faithful reproduction.
- For XMI, inspect namespaces and vendor extensions before assuming OMG-pure UML.
- For diagrams.net files, distinguish shape text and connector geometry from true model semantics.

## Writing Rules

- Choose a source format that matches the maintenance workflow.
- Prefer source-backed text formats for docs and CI.
- Prefer JSON graph models when building interactive products that need filtering, editing, search, selection, or analytics.
- Keep rendered assets generated from source whenever possible.
- Include source metadata near the generated diagram: scope, date, generator, source files, schema version, and known omissions.
- Do not round-trip through PNG when a semantic or vector format is available.

## Conversion Strategy

- Formal model to docs: XMI/UMLDI -> normalized model -> PlantUML/Mermaid/DOT/SVG.
- Code to diagrams: source analysis -> normalized model -> PlantUML/Mermaid/DOT/interactive JSON.
- Database to ERD: SQL introspection or schema file -> DBML/Mermaid ER/PlantUML IE -> SVG/PNG/PDF.
- Architecture to C4: source inventory or user description -> Structurizr DSL -> C4 views and exports.
- BPMN workflows: BPMN XML when process semantics matter; Mermaid/PlantUML flow or activity diagrams when communication is the only goal.

## Interchange Risks

- XMI interoperability varies by tool, UML version, profiles, and vendor extensions.
- Mermaid and PlantUML syntaxes overlap in intent but are not equivalent.
- Graphviz DOT carries graph layout semantics, not UML semantics.
- Rendered SVG may contain text and groups, but rarely enough semantic model detail to reconstruct the source reliably.
- Auto-layout can change visual reading order; do not treat coordinates as stable test assertions unless fixed.

## Source Anchors

- OMG XMI: https://www.omg.org/spec/XMI
- OMG UML 2.5.1 machine-readable XMI and UMLDI: https://www.omg.org/spec/UML/2.5.1/About-UML
- PlantUML: https://plantuml.com/
- Mermaid syntax: https://mermaid.js.org/intro/syntax-reference
- Graphviz DOT language: https://graphviz.org/doc/info/lang.html
- D2: https://d2lang.com/
- Structurizr DSL: https://docs.structurizr.com/dsl
- DBML: https://dbml.dbdiagram.io/docs/
- BPMN 2.0: https://www.omg.org/spec/BPMN/2.0/
- Kroki: https://docs.kroki.io/kroki/
