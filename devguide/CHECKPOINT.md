# Laboratory checkpoint — 2026-10-06

Resume with Recorda's [development checkpoint](https://github.com/uibcdf/recorda/blob/main/devguide/CHECKPOINT.md),
this guide and [RECORDA_BASELINE.md](RECORDA_BASELINE.md). The laboratory owns
scenarios and evidence; Recorda owns the standalone runtime; MOLI owns shared
contracts. Proposed next experiments require their own issue before implementation.

## Qualified source pair and completed work

- Recorda: `565a68c5103a587b06c2411bba2064d1572b4c56`.
- Lab: `bac97e6e53c842846b5d21b3905df79cee9b3342`.
- Checkpoint-only documentation commits do not change that tested pair. Manual
  integration pins the full Recorda identity above. The dummy remains 0.0.0,
  independent of Recorda and unchanged by the consumer experiments.
- Six usage notebooks cover manual activation, cost measurements, SciPy fitting,
  offline Sabueso resolution, capture selection and common reference checks.
  Native providers keep ownership of their results, decisions and records.

The local paired receipt in `evidence/reference_checks_linux_py314.json` records
112 passing tests (91 core + 21 Lab) on Linux Python 3.14.7 with published
pytest-receptor 1.1.0, and six real-kernel notebooks with 45 code cells. Its SHA256
is `c9f575747ad0f498cbca7ea3da474beeabb46291ad2f080a870256bdedb45cce`;
it is byte-identical to Recorda's paired receipt. Tested runtime, consumer,
fixture, test and notebook hashes match the published pair. Governance and Ruff
checks passed; original receipts and resolved analyses remain historical evidence.

[Routine CI](https://github.com/uibcdf/recorda-lab/actions/runs/37433553465)
passed four dummy Python 3.11–3.14 jobs; its manual-only jobs were skipped.
[Exact-pair manual integration](https://github.com/uibcdf/recorda-lab/actions/runs/37433724195)
passed all seven jobs, including Jupyter on 3.13/3.14 and SciPy. Hosted CI does
not execute Sabueso. Local Sabueso evidence uses frozen development package
copies and attributed public fixtures, not published provider-package closure.

Recorda's immutable 0.2.0 tag is historical source
`4e3d422fef1b0927fe63422323dc6d941c061bfb`, without later recovery/selection/checks.
Current runtime version metadata alone is insufficient to identify source.
No new release, general OS support, authenticated integrity or replay is qualified.

## Reproducible resumption

1. Read both repositories' `AGENTS.md`, the core checkpoint and owning issues;
   inspect Git status, exact commits and remote changes before editing.
2. Select `/home/diego/Myopt/miniconda3/envs/molsyssuite@uibcdf_3.14/bin/python`
   explicitly and verify its executable/version. Follow `PYTHON_SUPPORT.md` and
   use a published receptor, with `--receptor=llm` locally and `--receptor=ci` in CI.
3. Read the paired receipt for exact commands and lane flags. The receipt is
   durable; `/tmp` provider/tool installations are temporary. Reconstruct and
   hash-check matching frozen providers before rerunning Sabueso, or qualify a
   new pair. Do not silently substitute live development checkouts.
4. Run local governance, Ruff check/format and relevant pytest acceptance.
   Enable optional Jupyter/SciPy/Sabueso lanes only with verified prerequisites.

## Next work

Consolidate useful provenance and remaining acceptance in
[uibcdf/recorda-lab#1](https://github.com/uibcdf/recorda-lab/issues/1), coordinated
with [uibcdf/recorda#1](https://github.com/uibcdf/recorda/issues/1). The six notebook
scenarios are complete. A small multi-step workflow linking native references
was chosen under `uibcdf/recorda-lab#10` and implemented locally. Read
[MULTI_STEP_WORKFLOW.md](MULTI_STEP_WORKFLOW.md) for the consumer question,
independent scientific oracle, failure/omission cases and exact local receipt.
It does not replace the published pair above or complete broader acceptance;
owner review remains pending. The subsequent exact-source hosted qualification
is recorded separately in the workflow guide and hosted receipt.

Ecosystem boundaries and release/OS/coverage reviews remain core issues
uibcdf/recorda#2, uibcdf/recorda#3, uibcdf/recorda#4 and uibcdf/recorda#6. MOLI
context/routing and component adoption need a concrete missing provenance link
and separately owned work. Do not use Lab as a production integration destination.
