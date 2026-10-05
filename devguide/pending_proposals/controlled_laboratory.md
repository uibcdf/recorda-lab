---
summary: Build repeatable independent Recorda acceptance scenarios.
issue: uibcdf/recorda-lab#1
status: active
opened: 2026-10-05
closed:
verification: reproduced
area: [laboratory, acceptance]
blocked_by: []
supersedes: []
---

## Purpose

Build the controlled laboratory for uibcdf/recorda#1. The recorda_lab dummy package computes deterministic population statistics and owns a native result. It has no Recorda dependency or hooks. Experimental consumers exercise explicit boundaries and an opt-in wrapper.

## Acceptance

Check success, actual dummy exception, hard process exit, inactive calls, nested correlation, secret/opaque omissions, native result references and honest declared coverage. Preserve fixture, native result, journals and a checked acceptance report in a fresh destination. Inspect journals with Recorda alone. Keep core unit tests in Recorda and laboratory/integration tests here.

The follow-on activation experiment implements the agreed primary usage: activate once
with start/stop and call decorated consumers normally. Session-local adapters retain
native identity without recording statements inside scientific functions. Dummy code
and its returned result remain independent; the explicit-boundary experiment is retained.

Initial local evidence: six dummy cases plus one complete integration scenario test; 24 tests across both projects pass on Python 3.11 and on built wheels on Python 3.13. Source files are prepared locally, not yet committed/pushed. Manual hosted integration requires a reviewed full published Recorda commit SHA. A real external library remains later usability validation. The laboratory is associated MOLI infrastructure, not a MolSysSuite member or new scientific pillar.
