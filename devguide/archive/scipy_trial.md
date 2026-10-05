---
summary: Exercise real SciPy fitting with native references and visible failed attempts.
issue: uibcdf/recorda-lab#4
status: resolved
opened: 2026-10-05
closed: 2026-10-05
verification: reproduced
area: [laboratory, scientific-usability, external-library]
blocked_by: []
supersedes: []
---

## Resolution

Added a caller-local decorated alias of `scipy.optimize.curve_fit`, dimensionless
inputs/model, narrow native-reference adapters, an actual failed attempt/successful
retry, alternate solver and independent least-squares oracle. Native return/exception
identities and unchanged inputs are checked. Metadata identifies the actual SciPy
callable/version. The dummy, external modules and core runtime are unchanged.

Retained an eight-cell notebook with fit/residual SVG export, scientific environment,
optional manual Conda CI lane and Recorda/stdlib-only receipt inspector. Removed or
changed files fail inspection. Changed registered arrays are omitted instead of
referencing obsolete data; unknown/full-output contracts are explicitly omitted.

See `../SCIPY_TRIAL.md`, `../evidence/scipy_linux_py314.json` and Recorda's
`devguide/evidence/scipy_local.json` for local commands, packages, tests and hashes.
Broader Recorda/laboratory issues remain open. General research workflows, other result
formats, generic verification/replay and hosted/public support remain unqualified.
Sabueso is the next semantic experiment.
