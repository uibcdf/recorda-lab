# Controlled multi-step scientific workflow

Tracked by `uibcdf/recorda-lab#10`, coordinated with `uibcdf/recorda#1` and
`uibcdf/recorda-lab#1`. This is a standalone consumer experiment. Recorda, SciPy,
NumPy and the independent dummy implementation are unchanged.

## Consumer question and scientific oracle

Can a reader identify the exact retained observations and intermediate result
used to produce an evaluation, and distinguish missing information or files from
the observed execution outcome?

The fictional observations are dimensionless. Raw x is -3 through 3; raw y is
[-8.1, -5.8, -3.0, -0.6, 1.9, 4.2, NaN]. Preparation explicitly excludes the
nonfinite final row, preserving both input arrays. An ordinary SciPy curve_fit
call fits slope*x + intercept to the remaining six observations. Evaluation
computes the residuals and their sum of squares from the native fitted parameters.

The independent reader uses Python scalar arithmetic and closed-form ordinary
least squares, without NumPy/SciPy. Expected slope is 87/35, intercept -23/35,
and residual sum of squares 1/14. It checks covariance using the estimated
residual variance and inverse design-matrix product. Direct, dormant and active
executions agree within the declared numerical tolerance.

## Native ownership and dependency links

`workflow_consumer.py` keeps scientific calculations free of recording statements.
Caller-local decorators select preparation, SciPy fitting and residual evaluation.
The original SciPy callable and native return/exception instances are preserved.
Session-local exact-type adapters retain known small native arrays and manifests.
Repeated use returns the same full reference; changing an already registered native
result causes an explicit omission rather than reusing a stale identity.

Raw observations, initial parameters, model source, solver options, prepared arrays,
native parameter/covariance arrays and residuals remain separate retained files.
Reference lookup includes owner, identifier, revision and digest. The inspector
derives four dependency occurrences from recorded arguments: prepared x/y feed
the fit; prepared samples and the native fit feed evaluation. It expands only
this trial's known native manifest contracts. Parent nesting does not manufacture
scientific data dependencies; there is no new core dependency-graph API.

## Run and inspect

Install both development checkouts with --no-deps --editable in the declared
scientific environment, using Python 3.14 and published pytest-receptor 1.1.0:

```bash
python experiments/run_workflow.py artifacts/workflow-check
python experiments/inspect_workflow.py artifacts/workflow-check/full
RECORDA_LAB_SCIPY=1 python -m pytest --receptor=llm tests/test_workflow_experiment.py
RECORDA_LAB_NOTEBOOK=1 RECORDA_LAB_SCIPY=1 python -m pytest --receptor=llm
```

Destinations must be new. The runner retains success, actual optimizer failure
with maxfev=1 followed by retry, minimal capture and a disposable child hard exit.
The failed optimizer attempt keeps the session failed even when evaluation succeeds.
The hard exit occurs at a persisted fit boundary after preparation; it does not
claim that the interrupted optimizer body executed. Parent and fit remain incomplete.

Minimal capture retains execution identities/outcomes but omits payload groups and
does not run their adapters. Its missing links and unavailable scientific check
are explicit. Journal size or success alone cannot establish adequate provenance.

`inspect_workflow.py` imports Recorda and stdlib only. It reads this trial's NPY
1.0, C-order little-endian float64 files using a deliberately limited native reader;
it is not a general NumPy deserializer. Native receipts and recorded reference
checks use a 64 KiB byte bound. Scientific input/shape/model assumptions remain
laboratory responsibilities.

## Fault observations and limits

Deleting or altering a prepared array produces missing/mismatched file observations
and an unavailable scientific check. Restoring its bytes restores inspection. The
original succeeded execution outcome remains unchanged. A regression deliberately
changes evaluation RSS and updates its receipts and journal references: all byte
checks match, but the independent scientific check reports inconsistency.
Receipts and journals themselves are unauthenticated.

The seventh notebook runs start, preparation, fit, evaluation and stop across
ordinary cells, then inspects references and runs fault scenarios. Committed cells
have no outputs. The scientific lane selects it; the basic lane explicitly skips it.

Evidence is in `evidence/multi_step_workflow_linux_py314.json`. It identifies the
actual interpreter/tools, source and artifact fingerprints, optional lanes and
local check outcomes. Previous receipts remain historical. This scenario does not
execute the Sabueso lane or requalify its frozen provider copies.

The implementation PR is [uibcdf/recorda-lab#11](https://github.com/uibcdf/recorda-lab/pull/11),
paired with [uibcdf/recorda#13](https://github.com/uibcdf/recorda/pull/13).
Published gh-run-receptor 1.2.0 inspected
[routine PR CI](https://github.com/uibcdf/recorda-lab/actions/runs/37440479013)
and [exact-source Jupyter/SciPy integration](https://github.com/uibcdf/recorda-lab/actions/runs/37440827173).
Four routine jobs and all seven integration jobs passed; the scientific log reports
112 passed/four explicit Sabueso skips. The latter uses Lab
`77e7c36a34a2ae0d140c3ad51b461e046ee0b7d5` and the existing pinned core
`565a68c5103a587b06c2411bba2064d1572b4c56`. Capture fingerprints, exact heads and
official conclusions are in `evidence/multi_step_workflow_hosted.json`.
Later documentation-only commits do not change the tested implementation files.

Broader standalone acceptance remains open. No automatic capture, retained-source
authenticity, complete dependency closure, public support, replay, release or MOLI
integration follows from this experiment.
