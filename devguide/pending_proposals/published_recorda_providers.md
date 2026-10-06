---
summary: Receive required published Recorda providers and qualify the new laboratory pair.
issue: uibcdf/recorda-lab#12
status: active
opened: 2026-10-06
closed:
verification: reproduced
area: [integration, published-providers, notebooks]
blocked_by: []
supersedes: []
---

# Published Recorda provider closure

## What

Provision required SMonitor/ArgDigest and transitive DepDigest in all four
Recorda-bearing laboratory environments, then qualify an exact source pair
before advancing the manual integration default. Keep dummy runtime metadata
and its routine CI independent of the recording and support libraries.

## How / evidence

Recorda's default capture and local reference configuration now require the
published provider closure. Previous pip-only manual integration did not provision
it; the scientific route also lacked PyYAML for the core dependency preflight.
Use SMonitor 0.19.0 py_1, ArgDigest 0.15.0 py_0 and DepDigest 0.13.0 py_0 with
the core's exact Conda provenance/hash checker. Check installed requirements with
pip check and run installed-package tests using published pytest-receptor.

Producer-free reference readers also need these support providers. Controlled
-I -S children receive unchanged copies of only Recorda and its three required
provider package trees, so scientific producers remain unavailable even in the
scientific environment. Plain journal inspection keeps its previous lazy boundary.

## Why

An environment declaration and a passing dummy lane do not qualify receiving
integration. Native result/exception ownership, missing/altered references and
interrupted work must continue to pass with the actual required providers.

## Alternatives

Retaining the previous source as the default is the safe starting point until
qualification passes. Installing editable provider checkouts would not establish
published-artifact compatibility. Adding scientific/support dependencies to the
dummy package would violate its independent ownership.

## Acceptance criteria

- Required published closure is provisioned and verified in runtime-bearing routes.
- Dummy package and routine CI remain independent.
- Installed paired core/Lab tests, notebooks and SciPy execute for exact sources.
- Hosted Jupyter checks retain Python 3.11–3.14 and the scientific lane uses 3.14.
- Advance the default only after explicit-candidate qualification; verify the new default.
- Preserve historical receipts and publish a separately scoped receipt and issue outcome.

## Resolution

Local installed-pair qualification passes 242 tests with four explicit Sabueso
skips, six notebooks/45 cells and the real-kernel fault scenario. Published
provider provenance, pip check, negative preflight scenarios, governance and
Ruff pass. See `../evidence/published_providers_linux_py314.json`. Hosted explicit
candidate qualification and subsequent default promotion remain pending.
