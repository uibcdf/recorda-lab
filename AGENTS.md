# Recorda Lab contributor instructions

Read the canonical byte-identical `MOLI_GUIDE.md` and `devguide/README.md` first.
This is Recorda's associated laboratory under MOLI governance, not a MolSysSuite member.
Keep dummy operations independent of Recorda. Instrument experimental consumers, not
the dummy implementation. Keep fixtures deterministic, small and non-confidential.

Report laboratory issues in `uibcdf/recorda-lab`, recording defects in `uibcdf/recorda`,
and shared platform contracts in `uibcdf/moli`. Cross-link provider limitations;
follow `devguide/reporting_protocol.md` and archive meaningful resolved history.

Run `python devtools/validate_governance.py`, Ruff checks, and
`python -m pytest --receptor=llm` with the declared environment and both local
checkouts installed. Use published Pytest Receptor; use GH Run Receptor for first
Actions inspection, retaining GitHub's authoritative conclusions.
Configured/manual workflows are not executed evidence. Never imply that the dummy
laboratory establishes real scientific utility, full capture, replay or public support.

Python 3.11–3.14 is the target and Python 3.14 is the working default. Read `devguide/PYTHON_SUPPORT.md` for the tracked MOLI transition and explicit selection of `molsyssuite@uibcdf_3.14`.

Keep defect details in owning issues, code, tests and technical documentation.
Put only accepted, lasting working instructions in the correctly scoped `AGENTS.md`,
following `MOLI_GUIDE.md#durable-instructions-for-development-agents`.
For developer-guide work, read `devguide/AGENTS.md`.
