---
summary: Exercise common reference checks and retained-file loss in a sixth notebook.
issue: uibcdf/recorda-lab#9
status: resolved
opened: 2026-10-06
closed: 2026-10-06
verification: reproduced
area: [laboratory, references, notebooks]
blocked_by: []
supersedes: []
---

## Experiment and resolution

The unchanged population-statistics dummy produces mean 2.5 and variance 1.25.
Two selected operations retain four reference occurrences to native input/result
files through an explicit full-key local index declaring SHA256. The sixth notebook
checks intact files, removes the input, adds a newline to output bytes and restores
both files. Matching hashes, missing input and altered bytes are distinguished
without changing the original succeeded execution status.

Separate records show available_unverified (no digest), unresolved (no indexed
identity), six payload-group omissions under minimal policy and actual child-process
interruption after durable operation start. Inspection works in an interpreter
without importing the dummy, NumPy, SciPy or Sabueso. Reports do not capture
paths, file contents or arbitrary I/O exception text.

reference_files.py adapts existing trial receipt indices to the common core checker.
SciPy and Sabueso inspectors retain their native manifest, model, Card, trace and
version-binding validation. Their reports add reference_checks. The original native
identity, file-loss, old exception-index and offline scientific regressions pass.
Provider sources and the dummy package are unchanged.

The complete local pair passes 112 tests (91 core, 21 Lab) on Linux Python 3.14.7
with published pytest-receptor 1.1.0. All six usage notebooks execute 45 code cells,
including SciPy and frozen-development-source Sabueso. Fingerprints match before/
after qualification. See ../REFERENCE_CHECKS.md and
../evidence/reference_checks_linux_py314.json for commands, sources and reports.
The core implementation is owned by uibcdf/recorda#12. No new tag, public package/
OS support, authenticated identity or replay claim follows from this experiment.
