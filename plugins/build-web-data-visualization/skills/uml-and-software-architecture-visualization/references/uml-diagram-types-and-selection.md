# UML Diagram Types and Selection

## Purpose

Use this reference to choose between formal UML 2.5.1 diagrams and UML-like alternatives. The goal is communicative fit: the diagram should answer one modeling question for one primary audience at one useful level of abstraction.

## Formal UML Families

### Structure Diagrams

- Class diagram: static domain or code structure, interfaces, inheritance, associations, dependencies, attributes, operations, constraints, and stereotypes.
- Object diagram: runtime or example snapshot of object instances and links.
- Package diagram: namespace, module, subsystem, layer, or dependency grouping.
- Component diagram: replaceable implementation units, provided/required interfaces, service boundaries, and component dependencies.
- Composite structure diagram: internal parts, ports, connectors, and collaborations inside a classifier.
- Deployment diagram: nodes, execution environments, artifacts, devices, and deployed topology.
- Profile diagram: UML extensions, stereotypes, tagged values, and domain-specific modeling profiles.

### Behavior Diagrams

- Use case diagram: actors, system boundary, goals, include/extend relationships, and requirements framing.
- Activity diagram: workflow, branching, parallelism, object/control flow, and partitions or swimlanes.
- State machine diagram: finite states, events, guards, actions, entry/exit behavior, and lifecycle rules.

### Interaction Diagrams

- Sequence diagram: ordered messages among lifelines, activation, fragments, asynchronous calls, returns, creation, and destruction.
- Communication diagram: object collaboration and numbered message flow where topology matters.
- Timing diagram: state or value changes along a time axis, duration constraints, and time-sensitive interaction.
- Interaction overview diagram: high-level control flow across interactions, usually as an activity-like overview.

## UML-Like Alternatives

- C4 system context/container/component/code: use for software architecture maps where audience and abstraction level matter more than formal UML notation.
- ERD or DBML: use for relational database structure, keys, constraints, cardinality, and schema documentation.
- BPMN: use for business processes with execution semantics, events, gateways, pools, and process interchange.
- Flowchart: use for lightweight control flow, operational procedures, or quick documentation without UML semantics.
- Swimlane diagram: use when ownership and handoff are the core question.
- Dependency or network diagram: use for package coupling, service topology, blast radius, data lineage, or graph exploration.
- Application structural diagram: use for layered, module, service, queue, storage, and external-system relationships when formal UML would add friction.

## Selection Heuristics

- If the question is "who talks to whom, in what order?", use a sequence diagram.
- If the question is "what states are possible and what events move between them?", use a state machine.
- If the question is "what work happens, who owns it, and where are the branches?", use activity, swimlane, or BPMN.
- If the question is "what are the major deployable parts?", use C4 container or deployment.
- If the question is "what code abstractions or domain classes exist?", use class or package.
- If the question is "what tables and relationships exist?", use ERD or DBML before UML class diagrams.
- If the question is "what does the system do for outside actors?", use use case only when actor goals are the point.
- If the question is "what depends on what?", use a dependency graph, package diagram, component diagram, or C4 view depending on abstraction level.

## Detail Controls

- Start with a context or overview before showing implementation detail.
- Keep one abstraction level per diagram unless the purpose is an explicit bridge.
- Label relationships with verbs, protocols, data names, or event names.
- Hide private methods, incidental fields, and generated members unless they answer the question.
- Use stereotypes and icons sparingly; they should clarify type or responsibility, not decorate.
- Prefer multiple small diagrams over one unreadable all-system diagram.
- Put source, scope, timestamp, and caveats near durable exported diagrams.

## Common Applications

- Architecture review: C4 context/container, deployment, component, dependency graph.
- API design: sequence, component, class/interface, state machine for protocols.
- Domain modeling: class diagram, object examples, ERD when persistence matters.
- Business analysis: use case, activity, swimlane, BPMN.
- Operations and infrastructure: deployment, network topology, application structure, runbook flowchart.
- Onboarding: C4 context/container, package/module dependency, selected class diagrams.
- Reverse engineering: package, dependency, class, component, ERD, or generated code-level diagrams.

## Anti-Patterns

- Using class diagrams as architecture diagrams when the audience needs deployable units.
- Using use case diagrams when a short actor-goal list would be clearer.
- Turning an entire codebase into one giant diagram.
- Mixing business process, deployment, database, and code detail in one view.
- Treating generated reverse-engineering diagrams as curated design documentation.
- Hiding the main relationship behind unlabeled arrows.
- Depending on color alone to distinguish relationship types.
- Maintaining hand-drawn code diagrams that drift from source truth.

## Source Anchors

- OMG UML 2.5.1: https://www.omg.org/spec/UML/2.5.1/About-UML
- C4 model: https://c4model.com/
- BPMN 2.0: https://www.omg.org/spec/BPMN/2.0/
