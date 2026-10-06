---
summary: Evaluate explicit technical inspection views against laboratory JSON and notebooks.
issue: uibcdf/recorda-lab#13
status: resolved
opened: 2026-10-06
closed: 2026-10-06
verification: measured
area: [inspection, notebooks, receiving]
blocked_by: []
supersedes: []
---

# Inspection-view receiving experiment

## What

Receive the qualified uibcdf/recorda#21 prototype at
80ef3dd337cd7db901132007c390ced8b7980b9c. Compare explicitly requested views with
existing reference JSON and native multi-step scientific checks. Keep the dummy
implementation and scientific libraries independent.

## How / evidence

Reuse Lab #9 loss/alteration/restoration, unverified/unresolved, minimal capture
and hard-exit scenarios; add an explicitly constructed truncated journal copy.
Reuse Lab #10 preparation/fit/residual references and failed-attempt history.
Demonstrate messages in notebooks 06/07, beside raw facts and independent oracles.
Verify installed wheels, published providers, safe/no-event policy preservation,
malformed/hostile inputs and provider faults, then local real kernels and all
existing hosted Python 3.11–3.14 manual gates. Do not advance the default before
explicit-candidate qualification; qualify its promotion separately.

## Why

A user must distinguish recorded execution from present byte observations,
intentional omissions, absent checks and message availability. A byte match or
technical message does not replace the laboratory's scientific oracle.

## Alternatives

A new text renderer would duplicate the core catalog. Live provider-event capture
and scientific narrative are separately scoped in uibcdf/recorda#15; this trial only
receives the read-only technical view. Existing source JSON remains available.

## Acceptance criteria

Retain all original facts, compare useful fixed questions with independent source
observations, count repeated occurrences and full identities, expose omitted and
incomplete work, and keep source/reader scientific independence. Execute selected
notebooks and kernel faults with ordinary installed packages and published
pytest-receptor; inspect actual hosted runs with gh-run-receptor. Record limits
and exact sources before default promotion.

## Resolution

Local qualification passes: 333 installed-pair tests with four explicit Sabueso
skips (305 core + 28 Lab), six selected notebooks/49 code cells and the 14-cell
real-kernel fault scenario. Seven new receiving regressions pass. Source/wheel/
installed bytes, published providers, pip check, source/environment preflight,
governance/shared MOLI core and Ruff pass. Evidence is retained in
`devguide/evidence/inspection_view_linux_py314.json`.

The initial uibcdf/recorda#21 head exposed a saved-report wording ambiguity; Recorda
#22 corrects it with an actual restoration regression. The selected corrected
candidate is 48a6c9a0630027f0f2c3d8d82215de8e27764913, whose core source/installed
305 tests and all 11 exact-head CI jobs pass. Explicit-candidate Lab CI
https://github.com/uibcdf/recorda-lab/actions/runs/37544421813 passes all nine jobs
at b2b44d18f726bae975c7d21af3bf13bcda594980. Only the default SHA was promoted in
181f706c09cef42ec104a8edc7b3c413601307d9; the subsequent default run
https://github.com/uibcdf/recorda-lab/actions/runs/37544670429 passes the same nine
without a Recorda override. Published gh-run-receptor 1.2.0 and native GitHub
conclusions agree. Actual logs establish all five receiving/scientific selections
at the exact core SHA, 19 passes/13 explicit optional skips per kernel lane,
333 passes/four Sabueso skips in scientific, and six passes per dummy lane.
Hosted evidence is retained in `devguide/evidence/inspection_view_hosted.json`.

Closing documentation preserves every selected source/qualification byte and
records the one-line workflow promotion separately. The fixed user questions are
answered by actual source observations and messages; this is not a human usability
study or broader standalone/public-release certification. Provider proposals remain uibcdf/smonitor#39 and uibcdf/argdigest#32,
coordinated with uibcdf/moli#62; no provider implementation belongs to this trial.
