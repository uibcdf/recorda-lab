# Recorda Lab reporting protocol

Follow the canonical MOLI protocol:
https://github.com/uibcdf/moli/blob/main/devguide/governance/reporting_protocol.md

Recorda owns its recording implementation and schema experiments. Recorda Lab owns
dummy operations, fixtures and acceptance scenarios. MOLI owns shared platform contracts.
One independently closable theme has an owning issue. Every queued report uses the
front matter in `templates/report.md`, including its owning GitHub issue and evidence state.

Use `pending_bugs/` and `pending_proposals/` while work is open. On resolution record
the outcome and verification, set the closed date, move the report into `archive/`,
and synchronize the owning issue. Preserve meaningful history. Small issues need no report.

The permitted open states are `open`, `active`, `blocked`, `partial`; closed states
are `resolved`, `withdrawn`, `superseded`. Evidence states are `asserted`, `inspected`,
`reproduced`, `measured`, `upstream`. Do not put credentials or private scientific data
in reports. Provider limitations are reported at the provider and cross-linked here.

Run `python devtools/validate_governance.py` to check the local surface and report metadata.
