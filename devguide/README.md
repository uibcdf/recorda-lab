# Recorda Lab developer guide

Read [CHECKPOINT.md](CHECKPOINT.md) first for the published pair, executed
evidence, resumption procedure and next issue-backed work.

The laboratory owns dummy fixtures, controlled failures, acceptance scenarios and
experiment artifacts. Recorda owns recording behavior and its provisional API.
MOLI owns shared provenance and governance contracts. Follow `reporting_protocol.md`.

The laboratory is tracked by `uibcdf/recorda-lab#1`, coordinated
with the core experiment in `uibcdf/recorda#1`. Its local runner
checks success, failure, interruption, inactive behavior, nesting, omissions, native
references and declared coverage. A run produces fresh inspectable artifacts.

`experiments/run_activation.py` is the recommended activation experiment: start once,
call decorated consumer functions normally and stop. `experiments/consumer.py` owns
the hooks and exact-type reference adapters, with no change to the dummy library.
`experiments/run_slice.py` remains the complementary explicit-boundary scenario.

Use small non-confidential fixtures. Dummy/SciPy fixtures are fictional; the Sabueso
trial uses unchanged public UniProt responses with retained source attribution.
Evidence is scoped to the exact checkouts, Python
environment, scenarios and artifact directory used. Keep core unit tests in Recorda;
keep independent dummy and cross-package acceptance tests here.

`notebooks/` retains runnable usage simulations. `experiments/run_notebook.py`
qualifies a disposable real IPykernel across separate cells and controlled interruption,
tracked by `uibcdf/recorda-lab#3`. `experiments/run_performance.py` retains repeated
wall/CPU observations for direct, dormant and active calls, tracked by
`uibcdf/recorda-lab#2`. Notebook dependencies stay in the development/test surface;
the dummy package remains dependency-free. See `NOTEBOOK_AND_PERFORMANCE.md` for evidence.

`experiments/run_scipy.py` and `notebooks/03_scipy_fit.ipynb` exercise a real external
parameter-estimation API, tracked by `uibcdf/recorda-lab#4`. Local instrumentation,
narrow adapters and trial receipt inspection stay in `experiments/`; SciPy, NumPy
and the dummy package are unmodified. Read `SCIPY_TRIAL.md`. Enable the explicit
scientific lane with its declared environment; the basic lab remains independent.

`experiments/run_sabueso.py` and the fourth notebook exercise native knowledge
retrieval and entity resolution, tracked by `uibcdf/recorda-lab#5`. Read
`SABUESO_TRIAL.md` for public data attribution, exact co-development scope and
the opt-in exception-reference capture adopted in `uibcdf/recorda-lab#6`. The scientific source is unmodified.

The laboratory is not a production integration destination. New scenarios must name
their expected scientific result and recorded facts; do not merely mirror implementation.

Python 3.11–3.14 is the target and Python 3.14 is the working default. Read `PYTHON_SUPPORT.md` for the tracked MOLI transition and explicit selection of `molsyssuite@uibcdf_3.14`.

`experiments/run_selection.py` and the fifth notebook compare minimal/detailed
session capture under `uibcdf/recorda-lab#8`. Read `CAPTURE_SELECTION.md`.

`experiments/run_reference_checks.py` and the sixth notebook exercise common
local reference checks. Existing SciPy/Sabueso inspectors reuse their byte checks
with unchanged native semantic ownership. Read `REFERENCE_CHECKS.md`; tracked
by `uibcdf/recorda-lab#9` and `uibcdf/recorda#12`.

`experiments/run_workflow.py`, its producer-free Recorda inspector and the seventh
notebook link preparation, SciPy fitting and residual evaluation through retained
native references. Read `MULTI_STEP_WORKFLOW.md`; tracked by `uibcdf/recorda-lab#10`.

Required published-provider adoption and the current exact integration pair are
tracked by `uibcdf/recorda-lab#12`; read `CHECKPOINT.md` and
`archive/published_recorda_providers.md`. Reference checking needs Recorda's support
closure; scientific producers remain unnecessary for independent receipt reading.


`experiments/run_inspection_view.py` explicitly compares technical presentation
with the existing reference and optional SciPy workflow scenarios. Producer-free
`experiments/inspection_examples.py` projects saved observations without rechecking
native bytes. Notebooks 06/07 demonstrate the view beside original JSON and the
separate scientific oracle. Tracked by `uibcdf/recorda-lab#13`; read
[INSPECTION_VIEW.md](INSPECTION_VIEW.md).

`experiments/run_diagnostic_association.py` and notebook 08 compare application-
reviewed native SMonitor events with bounded selected associations at public
explicit dummy boundaries. `inspect_diagnostic_association.py` reads retained
references without scientific/consumer producers. Tracked by
`uibcdf/recorda-lab#14`; read [DIAGNOSTIC_ASSOCIATION.md](DIAGNOSTIC_ASSOCIATION.md).
