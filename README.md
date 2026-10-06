# Recorda Lab

Controlled dummy operations and repeatable integration experiments for Recorda.
This is test infrastructure associated with MOLI's Recorda component, not a
MolSysSuite member or a molecular-modeling library. Dummy and SciPy inputs are
fictional. The separate Sabueso trial uses three frozen public UniProt responses
with their original CC BY 4.0 attribution.

`recorda_lab.summarize()` computes deterministic population statistics and owns its
native result representation. It does not import Recorda or contain recording hooks.
Caller-owned boundaries and an instrumented example live in `experiments/run_slice.py`.

## Recorded baseline

The reviewed Recorda baseline is **0.1.0**, commit
`7e0c8dc79fbc529826d27e467de381e248c36da8`. See
[`devguide/RECORDA_BASELINE.md`](devguide/RECORDA_BASELINE.md) for paired identities
and historical qualification. Manual integration defaults to this full SHA.
The independent dummy package remains experimental version `0.0.0`.

## Run the first experiment

Create the declared development environment, then install the two local checkouts:

```bash
python -m pip install --no-deps --editable ../recorda
python -m pip install --no-deps --editable .
python experiments/run_activation.py artifacts/first-run
python -m recorda artifacts/first-run/interruption.jsonl
python -m pytest --receptor=llm
```

The destination must be new. It contains independent journals for success, failure,
hard process exit, nested operations and omissions, a fixture, the dummy's native
result, and `acceptance.json` with checked outcomes. The runner asserts expected
facts rather than merely displaying records. Reading journals requires only Recorda.

The recommended runner uses `start()/stop()` and ordinary calls to decorated consumers
in `experiments/consumer.py`. Consumers contain no Recorda `with` blocks. Session-local
adapters reference the fixture and native result automatically, preserving scientific
return values. Calls before activation and after stopping execute normally. `profile=`
is a recorded semantic label, not an implemented policy/catalog engine.

The complementary `python experiments/run_slice.py artifacts/explicit-run` experiment
retains explicit caller-owned boundaries for an unmodified library; use a new destination.

## Notebooks and performance

[`notebooks/`](notebooks/README.md) contains simulations of activation across cells
and recording-cost measurements. Committed notebooks have no execution outputs;
each run creates fresh artifacts. The development environment includes JupyterLab.

```bash
python -m jupyterlab
python experiments/run_examples.py artifacts/example-check
python experiments/run_notebook.py artifacts/kernel-check
python experiments/run_performance.py artifacts/performance-check
RECORDA_LAB_NOTEBOOK=1 python -m pytest --receptor=llm
```

The notebook runner launches the current interpreter as a disposable real kernel.
It checks separate-cell activation, top-level await, child ownership, native failure,
SIGINT, and kernel termination without stop. It preserves an executed notebook and
inspectable journals; it does not qualify every browser frontend. Performance uses
the unchanged synchronous recorder, verifies results outside timing, and retains
raw wall/CPU measurements. No performance threshold is imposed on CI.

Notebook integration is an explicit test lane; ordinary runs skip the real-kernel
test unless `RECORDA_LAB_NOTEBOOK=1`. The declared notebook test environment provides
its dependencies. Manual hosted integration enables the lane after publication.

The instrumented example also executes normally outside a session. Native results
are referenced by owner and content identity, not embedded as duplicate scientific
results in Recorda. Raw samples and opaque return objects are not automatically captured.
Coverage describes declared boundaries; dummy internals and unwrapped calls are unobserved.

## Controlled scientific trial

`notebooks/03_scipy_fit.ipynb` and `experiments/run_scipy.py` exercise unmodified
`scipy.optimize.curve_fit` through a caller-local decorated alias. The dimensionless
fictional fit retains an actual optimizer failure, a successful retry and an alternate
solver; native outputs agree with direct SciPy and an independent least-squares oracle.
Input/model/solver references and output manifests link to separate native files.

Use `devtools/conda-envs/scientific_env.yaml` for the declared scientific test stack:

```bash
python experiments/run_scipy.py artifacts/scipy-check
python experiments/inspect_scipy_trial.py artifacts/scipy-check
RECORDA_LAB_SCIPY=1 python experiments/run_examples.py artifacts/scientific-notebooks
RECORDA_LAB_NOTEBOOK=1 RECORDA_LAB_SCIPY=1 python -m pytest --receptor=llm
```

The trial-specific inspector needs Recorda and stdlib only; it checks the retained
artifact receipts without executing SciPy. This is not a generic integrity/replay API.
Scientific dependencies stay outside the dummy and Recorda runtimes. Scientific tests
are explicit; ordinary test runs skip them. The manual baseline run [37379156594](https://github.com/uibcdf/recorda-lab/actions/runs/37379156594)
passed all seven jobs against Lab `eed6bcc055c1c884187dbca1ed2b278498339f0b`
and Recorda `7e0c8dc79fbc529826d27e467de381e248c36da8`, including the
Conda scientific lane. That historical result does not qualify later Lab changes.
See `devguide/SCIPY_TRIAL.md` for scope.

## Offline Sabueso trial

`notebooks/04_sabueso_resolution.ipynb` and `experiments/run_sabueso.py` use
caller-local aliases of native Sabueso APIs. Retrieve a public entry, consume its
accession in a resolution, retain a demerged ambiguity and organism-based choice,
then exercise returned errors and native source exceptions without network access.
Cards, decisions and acquisition traces keep native scientific ownership.

Use the co-development Python 3.14 environment with both checkouts installed
and Sabueso's declared dependency closure; this is an opt-in laboratory lane:

```bash
python experiments/run_sabueso.py artifacts/sabueso-check
python experiments/inspect_sabueso_trial.py artifacts/sabueso-check
RECORDA_LAB_SABUESO=1 python -m pytest --receptor=llm tests/test_sabueso_experiment.py
RECORDA_LAB_NOTEBOOK=1 RECORDA_LAB_SABUESO=1 python experiments/run_examples.py artifacts/sabueso-notebooks
```

The independent inspector requires Recorda and stdlib only. It detects missing or
changed retained files; it does not authenticate manifests or replay computation.
Exception sidecars are explicitly retained by the caller. These adapters accept
known fixture contracts, not arbitrary Sabueso objects. See `devguide/SABUESO_TRIAL.md`.
Routine CI skips Sabueso tests and its notebook; this trial is qualified locally.

## Scope

This laboratory validates recording mechanisms, not real-world scientific usefulness,
complete workflow capture, replay or a stable schema. The SciPy trial exercises a
real external API; wider research-workflow usability remains unqualified.
PyUnitWizard is neither modified nor instrumented by this experiment.

Local qualification does not establish public OS support or publication. Python
3.11–3.14 is the target and development uses 3.14; CI configuration is not passing evidence. No package-channel
or DOI availability is claimed. Dummy tests run on routine pushes; cross-repository
CI integration is manually dispatched with a reviewed full Recorda commit SHA after
the implementation has been published. Local integration uses the two actual checkouts.

Read `AGENTS.md`, `MOLI_GUIDE.md` and `devguide/README.md` for governance.

Python 3.11–3.14 is the target and Python 3.14 is the working default. Read `devguide/PYTHON_SUPPORT.md` for the tracked MOLI transition and explicit selection of `molsyssuite@uibcdf_3.14`.
