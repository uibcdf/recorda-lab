# Explicit inspection-view receiving experiment

Owner: [uibcdf/recorda-lab#13](https://github.com/uibcdf/recorda-lab/issues/13).
The core API belongs to uibcdf/recorda#21; supplied-check wording is uibcdf/recorda#22.
This is a controlled technical presentation experiment, not a human usability
study, scientific interpretation, fresh-check certification or replay.

## Consumer questions and retained source facts

`run_inspection_view.py` reuses existing Lab #9/#10 fixtures and computations.
The unchanged dummy oracle remains mean **2.5**, variance **1.25**, count **4**.
The workflow's separate closed-form OLS oracle remains slope **87/35**, intercept
**-23/35** and residual sum of squares **1/14**. Original objects, exceptions,
references, source reports and execution outcomes remain producer-owned.

| Question | Source JSON | View and useful limit |
| --- | --- | --- |
| Did a lost input make execution fail? | Succeeded; two missing occurrences, two matched occurrences. | Succeeded execution; one missing full identity affects two occurrences, with source pointers and a hint. |
| Did altered output rewrite history? | Succeeded; two mismatched occurrences of one identity. | Original execution retained; supplied byte observation grouped separately. |
| Does restoration erase earlier observations? | Earlier report missing/mismatched; restored report matched. | Each supplied phase remains visible; only explicit new checking observes restoration. |
| Is minimal capture broken? | Six deliberate omissions, zero checked reference occurrences. | Coverage total retains six `capture_policy` omissions; no warning per omission and no implied verification. |
| Is an unverified reference corrupt? | One available_unverified and one unresolved reference. | Separate informational limitations, distinct from mismatched bytes. |
| What completed before interruption? | Incomplete session and unfinished operation. | Recorded work/counts retained without guessing a cause. A constructed truncated prefix is identified separately. |
| Does requesting a view check files? | No reference report supplied. | `not_requested`, `checked_occurrences=None`; no implicit hashing or resolution. |
| Did retry erase a failed attempt? | Failed recorded session, later fit consistent with native OLS oracle. | Failed attempt history retained; scientific consistency stays in the separate Lab check. |
| Do matching declared bytes establish scientific consistency? | Workflow has a separate oracle and native child-file scope. | Technical totals do not replace the scientific check or traverse arbitrary manifests. |

This gives evidence that the implemented view answers these fixed questions from
real scenario facts. It does not establish usefulness for untested workflows or
measure reader comprehension. Original JSON remains alongside the view.

## Usage and ownership

```bash
python experiments/run_inspection_view.py artifacts/inspection
python experiments/run_inspection_view.py artifacts/inspection-scientific --workflow
```

Use the explicitly selected installed candidate and declared published providers.
The first command runs unchanged dummy/reference scenarios; the second additionally
requires the declared scientific environment. Fresh destinations prevent overwriting.
The runner creates a separate truncated journal copy and retains `acceptance.json`.
Notebook 06 now executes 11 code cells and notebook 07 nine. Committed sources have
no outputs; executed copies belong to disposable acceptance workspaces.

`inspection_examples.py` receives saved reports, reads named journals explicitly,
and projects them through Recorda. It imports only Recorda and stdlib. The reader
can run in an isolated child supplied only with Recorda and required support trees,
without dummy/NumPy/SciPy/Sabueso/PyUnitWizard. It does not recheck native bytes.
Reference messages identify the supplied check, not an unobserved fresh check.
Source facts retain the original phase even if local files have since been restored.

Closed core input contracts, JSON budgets and same-declared-scope validation stay
owned by Recorda; reports have no authenticity, freshness or full-snapshot proof.
Malformed reports and opaque copying/string protocols fail before presentation.
Missing/failing presentation keeps facts, counts and fixed fallback reasons.
Enabled DEBUG application policy, handlers, warning/logging hooks and events remain
unchanged during projection. Invalid scientific calls/native exceptions are not
turned into new technical-view errors. Provider text improvements remain SMonitor
#39 and uibcdf/argdigest#32 coordinated with uibcdf/moli#62.

## Qualification

Current pair: Recorda `48a6c9a0630027f0f2c3d8d82215de8e27764913`, Lab receiving implementation `b2b44d18f726bae975c7d21af3bf13bcda594980`,
default promotion `181f706c09cef42ec104a8edc7b3c413601307d9`. Later documentation preserves all receipt-selected
runtime/test/experiment/fixture/notebook/tool/metadata/environment/README bytes;
the one-line workflow promotion is separately fingerprinted.

The [local receipt](evidence/inspection_view_linux_py314.json) records **333 passes,
four explicit Sabueso skips** (305 core + 28 Lab), seven new receiving regressions,
six selected notebooks/**49 code cells**, and the **14-cell** real-kernel fault
scenario on Linux Python 3.14.7. Source/wheel/ordinary-install equality, published
SMonitor 0.19.0 py_1, ArgDigest 0.15.0 py_0 and DepDigest 0.13.0 py_0, pip check,
source/environment preflight, governance/shared MOLI core and Ruff pass.

[Candidate CI](https://github.com/uibcdf/recorda-lab/actions/runs/37544421813) passes
all nine jobs before promotion; [default CI](https://github.com/uibcdf/recorda-lab/actions/runs/37544670429)
passes the same nine afterward without a Recorda SHA override (SciPy explicitly
selected). Four dummy and four real-kernel lanes cover Linux Python 3.11–3.14;
the scientific/core-recovery lane uses 3.14. Actual logs report six dummy passes,
19 integration passes/13 optional skips, and 333 scientific passes/four Sabueso
skips. Published pytest-receptor 1.1.0 and gh-run-receptor 1.2.0 were used.
The [hosted receipt](evidence/inspection_view_hosted.json) retains exact heads,
selected core identities, verdicts and log hashes. The resolved analysis is
[archive/inspection_view.md](archive/inspection_view.md).

Sabueso remains historical/optional. The experiment answers fixed technical
questions alongside source JSON; it does not measure human comprehension,
certify fresh/authenticated bytes, scientific correctness, public OS support,
a release or replay. uibcdf/recorda#15 live correlation remains separately scoped.
