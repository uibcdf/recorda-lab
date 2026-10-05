# Controlled SciPy parameter-estimation trial

Tracked by `uibcdf/recorda-lab#4`, linked to `uibcdf/recorda#1` and
`uibcdf/recorda-lab#1`. This follows the dummy/kernel experiment and precedes Sabueso.
It qualifies a controlled scientific workflow on a real external API, not general
research usefulness, all SciPy outputs or an entire workflow.

## Scientific behavior

Fit the dimensionless model `y = slope*x + intercept` to eleven deterministic
fictional observations. Compare direct SciPy, the dormant/active decorated alias
and an independent NumPy linear least-squares oracle. A real optimizer attempt
with an insufficient evaluation budget fails; the same inputs/model succeed with
a larger budget. That failure remains visible and the retry session stays failed.
A separate bounded `trf` fit succeeds and agrees with the oracle.

Estimated slope is approximately 2.50236 and intercept -0.696636. Parameter/covariance
arrays and original exception objects retain identity and behavior. Inputs remain
unchanged. The caller-local alias does not replace any SciPy module attribute.
Model/function bodies have no recording statements. Package/callable/version are
captured from the actual external API. Optimizer internals and downstream diagnostics
are unobserved. `parameter_estimation` is a semantic label, not a policy/catalog.

## Native references

`scipy_consumer.py` owns narrow exact-type adapters: registered float64 arrays,
this trusted affine model, permitted numeric solver options, and this model's two-array
return. Bounds and initial guesses are explicitly referenced. Inputs/results use
NumPy-native `.npy` files without pickle; Python model source and solver options
are retained separately. Lab-owned output manifests identify SciPy as producer and
link parameter/covariance arrays. Recorda contains references, not duplicated arrays.
Fixtures/model and persistence receipts belong to the laboratory; scientific values
retain their native SciPy/NumPy representation. All quantities here are dimensionless.

Registration keeps a small-fixture byte snapshot. Capture compares dtype, shape and
bytes; changed/unknown inputs become explicit omissions instead of stale references.
Original arrays are not frozen or modified. This content comparison costs O(input
size); larger integrations should consider owner-native immutable/versioned identities.
`**kwargs` is represented by a reference to strictly permitted numeric solver settings,
so the changed evaluation budget is inspectable without general dictionary capture.
Unknown models/options and `full_output=True` remain explicitly unsupported. The
five-item SciPy return still reaches the caller, with an omitted Recorda output.

Callbacks may persist native artifacts as integration side effects; they do no fitting
and do not change values. Artifact write errors become capture omissions under the
current callback contract. File close and receipts do not establish crash durability.
Scientific dependencies remain laboratory development/test tools; core and dummy
runtime dependencies remain empty.

## Inspection and usage

`inspect_scipy_trial.py` imports Recorda and stdlib only. It checks trusted trial
receipts/output manifests and exposes method, solver options, model/input identities,
implementation version, attempt status and native result references. A fresh process
proves SciPy/NumPy are not imported. Missing or modified files fail this receipt check.
This answers which configuration failed or produced the fit and where its inputs/result
are retained. It does not execute the model, infer research meaning or qualify a generic
Recorda verification, untrusted-schema, tamper-proof integrity or replay contract.

`notebooks/03_scipy_fit.ipynb` runs eight cells, compares solvers, displays covariance
and exports a fit/residual SVG. Sources have no committed outputs. Basic notebook
acceptance explicitly skips this scientific notebook; the full lane selects it.

Use `devtools/conda-envs/scientific_env.yaml`, with `RECORDA_LAB_SCIPY=1` and,
for real kernels, `RECORDA_LAB_NOTEBOOK=1`. Local qualification uses Linux Python
3.14.7, SciPy 1.18.1, NumPy 2.4.6 and Matplotlib 3.11.2 from the existing installed
environment, with published pytest-receptor 1.1.0. A fresh Conda solve and optional
manual hosted CI are configured, not executed evidence. No public support follows.
Exact commands, package/source identities and artifact hashes are in
`evidence/scipy_linux_py314.json` and Recorda's `devguide/evidence/scipy_local.json`.
The core runtime, scientific dummy and external libraries are unchanged by this work.
