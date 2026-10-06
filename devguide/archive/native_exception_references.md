---
summary: Adopt safe native exception references in the controlled Sabueso trial.
issue: uibcdf/recorda-lab#6
status: resolved
opened: 2026-10-06
closed: 2026-10-06
verification: reproduced
area: [laboratory, native-references, exception-provenance]
blocked_by: []
supersedes: []
---

## What and ownership

The original trial in `uibcdf/recorda-lab#5` manually retained ConnectorError's native
acquisition trace and linked it in the laboratory index. The core capability in
`uibcdf/recorda#7` now uses the existing exact-type session mapping to record a
safe reference on the failed operation. Preserve native ownership and source objects.

## Resolution and acceptance

Added exact ConnectorError registration to the trusted Sabueso adapters. The runner
and fourth notebook now handle errors normally; no explicit caller trace capture is
needed. The inspector reads exception.reference and also accepts historical
caller-owned indices. Native exception identity and full original acquisition_trace
remain preserved. Missing/changed exception-sidecar files are detected. Unregistered
errors remain explicit omissions; internal helper capture is not implied.

The complete local Recorda/Lab suite passed 65 tests, including four real-kernel
notebooks with 29 code cells. Core tests cover faulty callbacks and native cancellation.
Tested source hashes, interpreter, frozen scientific packages, exact commands and
notebook receipts are in `../evidence/exception_references_linux_py314.json`.
The consumed Recorda commit is `eabc4a6918bb3b03148b3b6989ccc780a52fb841`. The original 0.1.0 trial and its
evidence remain at Lab `84fec7dbac4daa63b976bee06882403bb734400c`.
The independent dummy and Sabueso/provider source are unchanged by this work.
No public scientific package, full workflow capture, MOLI routing or replay is claimed.
The separate pre-existing manual persistence-recovery limitation is `uibcdf/recorda#8`.
