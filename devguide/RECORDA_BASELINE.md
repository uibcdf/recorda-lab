# Recorded laboratory baseline

Recorda's first experimental source checkpoint is `0.1.0`, commit
`7e0c8dc79fbc529826d27e467de381e248c36da8`:
https://github.com/uibcdf/recorda/tree/0.1.0.

Use this exact identity when reproducing the initial activation, notebook,
performance and SciPy experiments. Manual hosted integration defaults to that
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
Consolidation is tracked in `uibcdf/recorda-lab#1`; the next controlled Sabueso
scenario is tracked in `uibcdf/recorda-lab#5`.
