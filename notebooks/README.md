# Laboratory notebooks

These notebooks simulate recommended usage with deterministic fixtures. Dummy/SciPy
data is fictional; the Sabueso notebook uses attributed frozen public UniProt responses.
They belong to Recorda Lab; the scientific dummy package remains independent.

- `01_manual_activation.ipynb`: start in one cell, make normal decorated calls in
  later cells, inspect the open record, stop in another cell, and retain a native
  result and a failed attempt.
- `02_recording_cost.ipynb`: run repeated direct/inactive/active measurements and
  display the measured medians. Raw observations and checked journals are retained.
- `03_scipy_fit.ipynb`: fit dimensionless fictional observations with unmodified
  SciPy, retain a failed attempt/retry and native NumPy outputs, compare solvers,
  export a fit/residual SVG and inspect trial receipts. Use the scientific environment.

- `04_sabueso_resolution.ipynb`: retrieve an entry, resolve its consumed accession,
  retain ambiguity and alternatives, and preserve native source failure traces.
  Requires the co-development Sabueso closure and `RECORDA_LAB_SABUESO=1`.

- `05_capture_selection.ipynb`: compare two session policies for the same native
  calculation, with explicit coverage, omitted payloads, bytes and repeated
  wall/CPU observations. Tracked by `uibcdf/recorda-lab#8`.

- `06_reference_checks.ipynb`: inspect retained references, remove an input,
  alter output bytes and restore files. Distinguish availability/hash checks,
  omissions and interrupted work. Tracked by `uibcdf/recorda-lab#9`.

- `07_multi_step_workflow.ipynb`: prepare finite observations, fit with SciPy,
  evaluate residuals and inspect native dependencies across cells. Check failure,
  interruption, minimal capture and intermediate-file loss. Requires the scientific
  lane; tracked by `uibcdf/recorda-lab#10`. Read `devguide/MULTI_STEP_WORKFLOW.md`.

Use Python 3.14 and the declared development environment. Install both checkouts
with `--no-deps --editable`, then launch `python -m jupyterlab` from the laboratory
root and select that environment's kernel. The setup cell prints the actual interpreter.
Committed notebooks have no outputs; each execution creates a new artifact directory.

`python experiments/run_examples.py artifacts/example-check` executes every code cell
of the selected committed notebooks in disposable workspaces and saves checked executed copies.
The explicit pytest kernel lane runs this acceptance check as well as the fault scenarios.
The scientific notebook is selected with `RECORDA_LAB_SCIPY=1`; the basic environment
and kernel lane explicitly skip it. Use `devtools/conda-envs/scientific_env.yaml`
and set both `RECORDA_LAB_NOTEBOOK=1` and `RECORDA_LAB_SCIPY=1` for full acceptance.

`python experiments/run_notebook.py artifacts/kernel-check` uses a disposable real
kernel to check separate cells, top-level await, child context ownership, uncaught
native failure, SIGINT and loss of the kernel without stop. It saves `executed.ipynb`
and independently inspected journals. The interrupted boundary is a controlled
wait, not a claimed scientific calculation. The runner never terminates the user's
interactive kernel. Browser frontends are not individually qualified by this test.

The full performance runner is
`python experiments/run_performance.py artifacts/performance-check`. There are no
timing thresholds in pytest. Negative inactive deltas and variable small timings
are possible measurement noise; keep the raw values and ranges. Active recording
retains synchronous fsync per event. Results apply to the tested storage/environment.

Tracking: `uibcdf/recorda-lab#3` (notebooks), `uibcdf/recorda-lab#2` (performance),
with recording implementation tracked by `uibcdf/recorda#1`.
The scientific trials are tracked by `uibcdf/recorda-lab#4` (SciPy) and
`uibcdf/recorda-lab#5` (Sabueso). The explicit Sabueso lane fails if selected
dependencies are unavailable; ordinary runs visibly skip it.
