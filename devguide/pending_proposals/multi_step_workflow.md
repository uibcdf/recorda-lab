---
summary: Evaluate preparation, fitting and evaluation through retained native references.
issue: uibcdf/recorda-lab#10
status: partial
opened: 2026-10-06
closed:
verification: reproduced
area: [scientific-workflow, native-references, standalone-acceptance]
blocked_by: []
supersedes: []
---

# Multi-step standalone workflow

## What

Qualify a dimensionless preparation → SciPy fit → residual evaluation workflow.
Ask whether recorded references support a useful independent account of the
observations and intermediate result consumed by each declared stage.

## How / evidence

The issue precedes implementation. The consumer, runner, producer-free inspector,
seventh usage notebook and acceptance tests are in the laboratory checkout.
See `../MULTI_STEP_WORKFLOW.md` for the scientific oracle, boundary coverage,
receipts, omission cases and fault scenarios. Source review/publication and
hosted CI remain separate from local qualification.

## Why

Individual calls, parent nesting and file hashes do not by themselves establish
scientific dependencies or scientific consistency. This experiment consolidates
the completed mechanisms against one explicit consumer question.

## Alternatives

Reuse the existing Recorda API and trial-specific manifests. A generic dependency
graph, new core schema or MOLI routing is unnecessary for this case.

## Acceptance criteria

- Direct/dormant/active calculations agree with a scalar closed-form OLS oracle.
- Native identity and exact references are preserved across scientific stages.
- Independent reading works with Recorda/stdlib only.
- Actual failure/retry, interruption, minimal capture and intermediate-file loss
  remain visible without rewriting execution outcomes.
- Scientific inconsistency is rejected even when byte receipts match.
- The notebook, governance, Ruff and relevant regressions execute with published
  tools, retaining exact local source/artifact evidence.

## Resolution

Local implementation and qualification complete: 112 passing paired tests and
four explicit Sabueso skips, six selected notebooks/45 cells including the new
seventh notebook. Published pytest-receptor 1.1.0 and Ruff 0.16.5 were used on
Linux Python 3.14.7; canonical governance checks pass. The paired receipt is
`../evidence/multi_step_workflow_linux_py314.json`. The implementation is published
for review in `uibcdf/recorda-lab#11`, paired with `uibcdf/recorda#13` documentation.
Routine PR CI and exact-source manual Jupyter/SciPy integration passed; published
gh-run-receptor 1.2.0 and native GitHub conclusions agree. See the separate
`../evidence/multi_step_workflow_hosted.json` receipt. Owner review/merge remains
pending; broader `uibcdf/recorda#1` and `uibcdf/recorda-lab#1` remain open.
