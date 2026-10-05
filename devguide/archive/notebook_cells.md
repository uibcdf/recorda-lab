---
summary: Qualify manual activation across real kernel cells and retain usage notebooks.
issue: uibcdf/recorda-lab#3
status: resolved
opened: 2026-10-05
closed: 2026-10-05
verification: reproduced
area: [laboratory, notebooks, acceptance]
blocked_by: []
supersedes: []
---

## Resolution

Retained two unexecuted source notebooks plus reusable real-kernel runners and
explicit regression tests. Every usage cell executes. Separate-cell activation,
top-level await, inherited-task ownership, uncaught native failure, controlled SIGINT
and kernel termination have checked journal outcomes. Native result ownership is
preserved; the dummy package is unchanged.

See `../NOTEBOOK_AND_PERFORMANCE.md`, `../evidence/notebook_linux_py314.json` and
Recorda's `devguide/evidence/notebook_performance_local.json` for exact environment,
commands, versions and hashes. Qualified locally on Linux Python 3.14.7 with
IPykernel 7.3.0 / jupyter-client 8.10.0. Other kernels/frontends, public support and
hosted CI remain unqualified. The broader laboratory and Recorda issues stay open.
