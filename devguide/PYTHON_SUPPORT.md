# Python support and working environment

Recorda and Recorda Lab admit Python 3.11–3.14 with
`requires-python = ">=3.11,<3.15"`. Their development environments use Python 3.14.
Ruff keeps `target-version = "py311"` to preserve the oldest supported syntax.

For the existing shared workspace, use the interpreter in
`/home/diego/Myopt/miniconda3/envs/molsyssuite@uibcdf_3.14`. Its name does not change
Recorda's direct MOLI governance. Check `sys.executable` and `sys.version`; an inherited
shell may still activate `molsyssuite@uibcdf_3.13`. Commands executed in a subprocess
do not change the parent shell's active environment.

## MOLI baseline and transition history

MOLI's current registry admits Python 3.11–3.14, uses Python 3.14 for development
and marks the common transition completed. Recorda's earlier component-specific
admission is retained in
`policies.python.transition.components` in MOLI's registry, with ownership in
[uibcdf/recorda#4](https://github.com/uibcdf/recorda/issues/4) and coordination in
[uibcdf/moli#50](https://github.com/uibcdf/moli/issues/50). Recorda Lab follows that
admission as associated test infrastructure, tracked by
[uibcdf/recorda-lab#1](https://github.com/uibcdf/recorda-lab/issues/1).

The earlier local 3.14 development default was a bounded deviation from MOLI's
routine 3.13 default, with review due by 2026-11-05 or the first public release.
Common-baseline adoption now satisfies that exit condition. Preserve historical
evidence and retain required Linux tests for every admitted minor, including 3.13.
This baseline alignment does not resolve the distribution or OS-support reviews.

## Qualification

Use published pytest-receptor 1.1.0, whose metadata admits Python 3.11–3.14, and
Ruff 0.16.5. The shared 3.14 environment contains a development receptor; select the
published tool separately for evidence. Do not change shared packages merely to run
the experiment. Preserve source and installed-wheel results with interpreter/tool
versions and artifact fingerprints in `evidence/`.

Required CI includes 3.14 without tolerated failures, while preserving older minors.
Configured workflows and local Linux results do not establish public macOS support
or qualify a public release. The existing OS/distribution reviews remain open.
