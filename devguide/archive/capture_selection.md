---
summary: Compare minimal and detailed capture for one unchanged dummy calculation.
issue: uibcdf/recorda-lab#8
status: resolved
opened: 2026-10-06
closed: 2026-10-06
verification: measured
area: [laboratory, capture, notebooks, performance]
blocked_by: []
supersedes: []
---

## Experiment and resolution

The existing independent dummy and consumer functions calculate mean 2.5 and
population variance 1.25 for [1,2,3,4]. Session policy changes selected boundaries
and payload groups once, with ordinary calls and native errors preserved.
The minimal mode records two scientific operations; detailed also records the
inspection calls and safe native references. No scientific provider was changed.

With eight inspection calls, the measured minimal journal has 2 operations,
6 events/fsyncs, 0 adapter calls and 2613 bytes; detailed has 10 operations,
32 events/fsyncs, 12 adapter calls and 14257 bytes in the qualified run.
Raw repeated wall/CPU measurements are retained without a speed threshold.
Timings include activation, execution, finalization and inspection in fixed mode
order, and are specific to this workload and filesystem.

The minimal mode intentionally loses input/output references. Explicit metadata
and configured coverage expose that loss. Excluded counts indicate invocation,
not completed work; missing finalization keeps them unknown. Session success
covers selected outcomes only. Native failures are checked in both modes, and
producer-free inspection needs only Recorda and stdlib. These are no replay or
public support claims.

The fifth notebook runs eight cells with start/stop across ordinary calls. All
89 paired local tests pass on Linux Python 3.14.7 with published pytest-receptor
1.1.0, including five notebooks (37 cells), SciPy and frozen-source Sabueso.
Read ../CAPTURE_SELECTION.md and ../evidence/capture_selection_linux_py314.json
for scope and source fingerprints. The core policy is owned by uibcdf/recorda#11.
