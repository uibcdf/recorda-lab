# Recorded laboratory baseline

Read [CHECKPOINT.md](CHECKPOINT.md) for hosted conclusions and resumption steps.
Historical entries below retain the state at their respective checkpoints.

## Current integration source — declared reference checks

Manual integration pins Recorda `565a68c5103a587b06c2411bba2064d1572b4c56`. This unreleased
source after 0.2.0 adds explicit local reference availability and bounded byte
checking with declared SHA256, while retaining capture selection and lifecycle
recovery. Core ownership is uibcdf/recorda#12; Lab adoption and the sixth notebook
are uibcdf/recorda-lab#9. Native scientific ownership and manifest rules remain local.

The local pair passes 112 tests on Linux Python 3.14.7, including six notebooks
(45 code cells), SciPy and frozen-source Sabueso. Source hashes, command and
controlled reports are in evidence/reference_checks_linux_py314.json. The dummy
remains 0.0.0 and unchanged. Current/historical source and artifact qualification
remain separate; no new release or public support/replay claim is made.

## Historical integration source — capture selection

The capture-selection integration baseline used Recorda `90ae0decbde4e18ecee206f2097ed9a0bc79ae0a`. This is unreleased
source after 0.2.0, adding manual persistence recovery and standalone session
CapturePolicy. Its owning issues are uibcdf/recorda#8 and uibcdf/recorda#11;
the laboratory experiment/fifth notebook is uibcdf/recorda-lab#8.

The local paired receipt passes 89 tests on Linux Python 3.14.7, including
five notebooks (37 code cells), SciPy and frozen-source Sabueso. Runtime,
consumer, test and notebook fingerprints are in evidence/capture_selection_linux_py314.json.
Core and Lab qualification have independent source identities; the dummy remains
0.0.0 and unchanged. The 0.2.0 tag and its exact historical artifact receipt
remain identified below. No new release or public support claim is made.

## Historical source checkpoint — 0.2.0

Recorda `0.2.0` is pinned to `4e3d422fef1b0927fe63422323dc6d941c061bfb`. At that checkpoint the manual integration default used
this full source identity. The checkpoint is tracked by `uibcdf/recorda#9`, which
retains artifact hashes, installed-candidate checks, paired laboratory identities
and exact CI conclusions. The independent dummy remains `0.0.0`.

This includes the exact-type native exception references in `uibcdf/recorda#7`
and the Sabueso adoption in `uibcdf/recorda-lab#6`. The fourth notebook no longer
retains exception traces manually. `uibcdf/recorda#8` remains separate follow-up.
Scientific package copies and public fixture identities are qualified within the
recorded local scope; hosted Jupyter/SciPy gates do not claim Sabueso execution.
No public package-channel, OS-support, archival or replay claim follows from the tag.

## Historical source checkpoint — 0.1.0

Recorda's first experimental source checkpoint is `0.1.0`, commit
`7e0c8dc79fbc529826d27e467de381e248c36da8`:
https://github.com/uibcdf/recorda/tree/0.1.0.

Use this exact identity when reproducing the initial activation, notebook,
performance and SciPy experiments. At that checkpoint, manual integration defaulted to its
reviewed full SHA; choosing another commit creates a separately qualified pair.
The dummy package retains its independent experimental version `0.0.0` and no
Recorda runtime dependency. A laboratory source commit identifies experiments
and notebooks separately from the installed dummy package.

The fresh Recorda wheel qualified for that checkpoint has SHA256
`612ab04c2354278feb6f1c4e1b4c85128054513a0bb88c6e9f6b8dc524c79d73`.
Its paired laboratory inputs and dependency identities are recorded in
[uibcdf/recorda#5](https://github.com/uibcdf/recorda/issues/5#issuecomment-6002919490).
Linux Python 3.14 passed all 50 core/laboratory tests with Jupyter/SciPy enabled;
3.11, 3.12 and 3.13 passed 44 with six explicit optional-lane skips each.
These results qualify those recorded inputs, not subsequent laboratory changes.

Historical 0.0.0 receipts remain unchanged. This is source test infrastructure;
package distribution, public OS qualification and archival remain separate work.
Consolidation remains tracked in `uibcdf/recorda-lab#1`. The subsequently
completed controlled Sabueso scenario is tracked in `uibcdf/recorda-lab#5`.

## Native exception-reference extension

`uibcdf/recorda#7` is implemented at Recorda `eabc4a6918bb3b03148b3b6989ccc780a52fb841`. That source extension was reviewed before the 0.2.0 tag; its original
paired receipt remains historical. The historical 0.1.0
pair remains identified above. The Sabueso consumer now registers exact ConnectorError
capture once and reads native trace references from failed operations. Adoption is
tracked by `uibcdf/recorda-lab#6`; the 0.1.0 consumer is preserved in Lab
`84fec7dbac4daa63b976bee06882403bb734400c`. Read `SABUESO_TRIAL.md` and the new
`evidence/exception_references_linux_py314.json` for source qualification.
