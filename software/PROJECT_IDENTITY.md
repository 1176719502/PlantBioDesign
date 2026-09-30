# Project Identity: BioDesign Studio

## 1. One-Sentence Definition

BioDesign Studio is a local-first documentation workspace for synthetic biology design records, pathway project notes, traceability review, and documentation-only export/import packages.

## 2. Current Product Identity

The current product identity is a Pathway Documentation Workspace.

BioDesign Studio should help users:

- Create and open local pathway documentation projects.
- Record pathway steps, project notes, review notes, and documentation quality checks.
- Link pathway steps to Expression Wizard design records.
- Review saved design records through the Design Library and Saved Designs surfaces.
- Save documentation snapshots of the local project state.
- Generate reports and traceability summaries for documentation review.
- Export and preview documentation-only project packages.
- Use duplicate guard and import preview flows before creating another local documentation project.

The earlier single-gene Expression Wizard MVP is retained as historical baseline work and as an active design record subflow. It should not be described as the whole product direction.

## 3. What the Project Is Not

BioDesign Studio is not:

- A wet-lab automation system.
- An experimental validation platform.
- A biological readiness approval system.
- A biological outcome prediction engine.
- A pathway optimization engine.
- A protocol generation system.
- An autonomous DBTL execution system.
- A full Benchling, SnapGene, LIMS, or biofoundry replacement.
- A CRISPR design, BLAST, flux simulation, or full plasmid editing platform.

Any feature that pushes the product toward one of these identities should be deferred unless a task explicitly opens that scope and preserves the documentation-only boundary.

## 4. Current Mainline Workflow

The product should be organized around the pathway project documentation lifecycle:

```text
Pathway Projects
-> Pathway Workspace
-> Pathway steps and project notes
-> Linked Expression Wizard design records
-> Documentation snapshots, reports, and traceability review
-> Documentation-only export package
-> Import package preview and duplicate guard
-> Local documentation project creation
```

### Pathway Projects

The user creates, selects, and opens local pathway documentation projects.

### Pathway Workspace

The user records pathway steps, project notes, test-record notes, review notes, linked artifacts, documentation snapshots, reports, and traceability review surfaces.

### Expression Wizard Design Record Subflow

Expression Wizard creates or reviews one expression design record. It can be launched from a pathway step when a gene-level design record is useful for the project documentation.

### Design Library / Saved Designs

Saved design records are local design snapshots for documentation review and reuse as references. They do not certify biological use.

### Documentation Snapshots

Documentation snapshots preserve the current Pathway Workspace project documentation state.

### Reports and Traceability

Reports, traceability summaries, and documentation quality checks help users review recorded project information and missing references.

### Export / Import Packages

Export packages and import previews are documentation-only project package flows. Import preview and duplicate guard checks should make local project creation explicit and reviewable.

## 5. Supporting Tools

Supporting tools may exist when they help users prepare, inspect, or document local design records.

Allowed supporting roles include:

- Sequence cleanup and preflight utilities.
- Basic sequence summaries.
- Codon usage preview where framed as a computational record.
- Parts registry records for local documentation.
- Case Library examples as design-record starting references.
- Structure, cloning, or lab-tool pages only as documentation aids with clear boundary copy.

Supporting tools should not become independent product centers that imply automation, prediction, optimization, or biological approval.

## 6. Historical MVP Context

The earlier v0.1 baseline focused on a single-gene Expression Wizard path:

```text
Gene Input
-> Sequence Preflight
-> Host & Elements
-> Expression Frame
-> Primer / Cassette Design
-> Review
-> Documentation Export
```

This history is useful for traceability and regression testing. In current product copy, describe this path as the Expression Wizard design record subflow or as historical MVP context where needed.

## 7. Where Agents Should Fit

Agents should be bounded, reviewable, and user-directed.

Appropriate assistive roles include:

- Explaining documentation gaps or review notes.
- Summarizing design-record context.
- Drafting report text for user review.
- Helping compare user-selected records.
- Guiding users across Pathway Projects, Pathway Workspace, Expression Wizard, Design Library, reports, traceability, and package previews.

Agents should not:

- Autonomously redesign constructs.
- Choose biological actions without user review.
- Replace deterministic review logic.
- Run wet-lab workflows.
- Generate protocols.
- Drive prediction, optimization, or biological approval.
- Trigger database, import/export schema, or report contract changes unless explicitly requested.

## 8. Criteria for Accepting a New Feature

A new feature should be accepted only if it passes these checks:

1. It supports the local documentation workspace identity.
2. It fits clearly into Pathway Projects, Pathway Workspace, Expression Wizard design records, Design Library, documentation snapshots, reports, traceability, package preview, or review notes.
3. It improves clarity, reviewability, traceability, or local documentation quality.
4. It can be implemented without database schema changes unless explicitly requested.
5. It can be implemented without import/export package schema changes unless explicitly requested.
6. It avoids wet-lab automation, prediction, optimization, protocol generation, and autonomous DBTL execution.
7. It produces user-facing copy that stays documentation-only.
8. It does not reinterpret primer risk, review status, or saved snapshots as biological approval.

If a proposed feature fails these checks, defer it to planning instead of adding it to the current product surface.

## Product Direction Rule

When in doubt, present BioDesign Studio as a local-first documentation workspace for pathway project records, linked design records, traceability review, and documentation-only package exchange.
