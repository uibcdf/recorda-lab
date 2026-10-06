# Controlled local reference checks

Tracked by uibcdf/recorda-lab#9 and core uibcdf/recorda#12. Read Recorda's
REFERENCE_CHECKS.md for provisional APIs, observation states and limits.

run_reference_checks.py preserves the unchanged dummy oracle: [1,2,3,4] gives
mean 2.5 and population variance 1.25. Full capture has four reference occurrences
for two native files. The explicit local index declares SHA256. Removing the
input yields missing occurrences; adding a newline to the output changes its
byte digest despite equivalent parsed JSON. Restoration yields matched again.
The checker does not reinterpret scientific meaning or change execution status.

The runner also distinguishes available_unverified (no recorded digest),
unresolved (no full-key locator), payload omission under minimal policy, and an
actual child-process exit after durable operation start. Producer-free inspection
uses Recorda and stdlib only. Run with a fresh destination:
`python experiments/run_reference_checks.py /tmp/new-reference-trial`.

The sixth notebook performs these steps in eight kernel cells. Journals, index,
native files and acceptance.json remain inspectable. reference_files.py adapts
existing SciPy/Sabueso receipt formats to the common rooted byte checker. Their
own model, native-manifest, Card, trace and version-binding rules remain intact;
reference_checks is added to their reports. Current source requires the reviewed
core implementation, pinned by manual integration.

No arbitrary path is inferred from an identifier. Indices use full owner/id/
revision/digest keys, relative locations and an explicit algorithm declaration.
This is controlled local availability and byte matching, not authenticated
ownership, a complete native dependency graph or replay. Read
`evidence/reference_checks_linux_py314.json` for commands and qualified sources.
