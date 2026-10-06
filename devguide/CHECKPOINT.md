# Laboratory checkpoint — 2026-10-06

Resume with Recorda's [development checkpoint](https://github.com/uibcdf/recorda/blob/main/devguide/CHECKPOINT.md),
this guide and [RECORDA_BASELINE.md](RECORDA_BASELINE.md). Lab owns scenarios
and evidence, Recorda owns the standalone runtime, and MOLI owns shared contracts.

## Current qualified pair

- Recorda: `b3a53770e3b9917e5ff399dbfc00a9c53f2a37ac`.
- Lab receiving implementation: `11b1465f9b8558a2ac4c7c172ab2377251820af3`.
- Lab default promotion: `4256184d185cbae469b90de36f6f0fb260b7e4d4`.
- Later documentation-only commits retain these implementation identities. The
  dummy remains 0.0.0 with empty runtime dependencies and unchanged native code.

`uibcdf/recorda-lab#12` provisions published SMonitor 0.19.0 py_1, ArgDigest
0.15.0 py_0 and transitive DepDigest 0.13.0 py_0 in all four Recorda-bearing
Conda environments. Manual CI checks the selected source SHA, exact provider
coordinates/hashes/managed Python bytes, metadata constraints and pip check.
Dummy-only CI retains its separate pip-only environment.

[Local receipt](evidence/published_providers_linux_py314.json): Linux Python
3.14.7, ordinary installed wheels, published pytest-receptor 1.1.0, **242 passed
and four explicit Sabueso skips** (221 core + 21 Lab). Six selected notebooks
execute 45 cells; the real-kernel fault scenario adds 14 cells. NumPy 2.4.6,
SciPy 1.18.1 and IPykernel 7.3.0 match the declared scientific route. Governance,
Ruff, shared MOLI checks and negative preflight scenarios pass.

[Explicit-candidate qualification](https://github.com/uibcdf/recorda-lab/actions/runs/37536928526)
passes all nine jobs before default promotion: dummy and real-kernel integration
on Python 3.11–3.14, plus scientific integration on 3.14.
[Default qualification](https://github.com/uibcdf/recorda-lab/actions/runs/37537236289) passes the same nine jobs after promotion.
Published gh-run-receptor 1.2.0 and native GitHub conclusions agree. Exact heads,
source selection and hosted verdicts are in
[evidence/published_providers_hosted.json](evidence/published_providers_hosted.json).

Seven usage notebooks are retained. The current pair executes 01/02/03/05/06/07;
04/Sabueso is explicitly excluded. Producer-free reference readers receive only
Recorda and its required support package trees in controlled `-I -S` children,
with scientific producers unavailable. Plain journal reading remains provider-free.
This pair does not requalify Sabueso's frozen development stack. Previous receipts,
including the reference-check and multi-step pairs, remain historical and unchanged.

The Recorda 0.2.0 tag remains `4e3d422fef1b0927fe63422323dc6d941c061bfb`.
Runtime version metadata alone is insufficient to identify the new source.
No public release, general OS support, authenticated integrity or replay is qualified.

## Reproducible resumption

1. Read both repositories' instructions, maintained checkpoints and owning issues;
   inspect exact commits and local/remote changes before editing.
2. Follow `PYTHON_SUPPORT.md`, explicitly select and verify Python 3.14, and use
   a published receptor (`--receptor=llm` locally, `--receptor=ci` in CI).
3. Recreate a declared integration environment and verify published provider
   coordinates/hashes with the selected Recorda checkout's development checker.
   Install both exact sources and run pip check before installed-package tests.
   The local receipt gives commands; `/tmp` installations are disposable evidence.
4. Run local governance, Ruff and relevant pytest checks. Enable optional scientific
   lanes only with verified prerequisites. Reconstruct/hash-check the historical
   frozen scientific providers before rerunning Sabueso, or qualify a new pair.

## Next work

The completed receiving analysis is [archive/published_recorda_providers.md](archive/published_recorda_providers.md).
Consolidate remaining standalone acceptance in `uibcdf/recorda-lab#1`, coordinated
with `uibcdf/recorda#1`; the bounded multi-step trial in Lab #10 is complete.
New experiments need a concrete consumer question, independent oracle and owning
issue. Core ecosystem review #2 is complete; MOLI registry reconciliation remains
separately owned in `uibcdf/moli#62`. Release/OS/coverage remain Recorda #3/#4/#6.
SMonitor inspection presentation and operation correlation are separate core
analyses (#14/#15). Lab is not a production integration destination.
