---
summary: Evaluate native Sabueso source outcomes and diagnostic associations per Card attempt.
issue: uibcdf/recorda-lab#15
status: resolved
opened: 2026-10-07
closed: 2026-10-07
verification: measured
area: [diagnostics, sabueso, native-references]
blocked_by: []
supersedes: []
---

# Native Sabueso diagnostic trial

## What

A Card was returned: which requested sources were incomplete or failed, which
native Sabueso diagnostics were delivered, and to which attempt do they belong?
Follow the completed association mechanics in uibcdf/recorda-lab#14 and the
architectural decision in uibcdf/recorda#15.

## How / evidence

The issue precedes this report. Freeze clean Sabueso
`68dac8f8bfc35944f5b6dd59aca8cb2a2819388d`, without its concurrent uncommitted work.
Use actual public protein-card construction, frozen attributed UniProt P60174 data
and explicitly fictional enrichment transport fixtures, with source connections
forbidden. Sabueso's own source outcome handling emits its native diagnostics.

## Why

A succeeded call is distinct from complete source information. Native Card
quality/source evidence and conditional diagnostic observation answer different
questions. Retain ownership rather than infer scientific quality from a code.

## Alternatives

Compare native Card/source records, reviewed native SMonitor events and bounded
selected associations via existing explicit operation/reference APIs. Broader
core automatic attachment or provider redesign requires separately owned evidence.

## Acceptance criteria

Independent expected outcomes for complete, partial, failed-source and retry
cases; exact native results/errors; safe bounded observation and missing/changed
references; reader without producers; installed source/dependency hashes,
published receptors and actual appropriate hosted checks.

## Resolution

Local installed qualification passes 380 tests/four historical Sabueso skips;
16 new cases and 31 existing association regressions pass. Seven selected
notebooks/55 code cells and 14 kernel-fault cells pass. Source/wheel/provider
hashes and explicit native Conda mapping verification are retained in
`../evidence/sabueso_diagnostics_linux_py314.json`; the unchanged core preflight
limitation is tracked in uibcdf/recorda#23. Corrected exact-head CI passes all 13 jobs; actual native logs report 47 passes
per Python 3.11–3.14 minor. Published receptors and native conclusions agree.
Source/provider checks and capture hashes are retained in
`../evidence/sabueso_diagnostics_hosted.json`. No platform routing, release/OS/replay
or human usability qualification is selected.

Final review corrected ordinary reference-error precedence for native warnings,
interrupts and cancellation (five additional receiving cases). Initial hosted
preflight rejected the new unclassified environment; explicit route/provider
admission and five negative cases now pass. Initial receipts remain retained.
The final hosted run is
[37584430143](https://github.com/uibcdf/recorda-lab/actions/runs/37584430143),
at Lab `a0376799c25c6b650ffa79aa6e4012601892d24c`. Current receipts freeze the
corrected sources; closing documentation preserves every selected byte. Existing
public references answer the bounded native producer question. No automatic
attachment/context API or platform routing decision is selected.
