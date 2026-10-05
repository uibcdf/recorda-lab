---
summary: Measure dormant and active decorator cost with verified native results.
issue: uibcdf/recorda-lab#2
status: resolved
opened: 2026-10-05
closed: 2026-10-05
verification: measured
area: [laboratory, performance, acceptance]
blocked_by: []
supersedes: []
---

## Resolution

Implemented repeated direct, dormant, active-omission and active-reference comparison
for three deterministic workloads. Rotated seven repetitions, retained raw wall/CPU
observations, native fixtures/results, inspected event counts, journal sizes and hashes.
Session setup/finalization and correctness verification are excluded from call timing;
the production synchronous fsync writer is unchanged. Pytest checks artifact correctness
without noisy timing thresholds. Usage simulation is retained as a notebook.

See `../NOTEBOOK_AND_PERFORMANCE.md`, `../evidence/performance_linux_py314.json`
and Recorda's `devguide/evidence/notebook_performance_local.json`. Measurements are
local to this filesystem/interpreter and dummy workloads. Small dormant deltas fluctuate;
active recording adds milliseconds per operation and reference hashing scales with input.
Do not extrapolate to all scientific libraries or silently replace the reliability policy.
