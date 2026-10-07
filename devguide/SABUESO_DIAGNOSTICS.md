# Native Sabueso source diagnostics — Lab #15

Owner: `uibcdf/recorda-lab#15`, following the controlled association comparison
in Lab #14 and the architectural evaluation in `uibcdf/recorda#15`.

## Consumer question

A public call returned a Card: which requested sources failed or delivered
incomplete information, which native diagnostics were delivered, and to which
attempt do those observations belong?

Run `python experiments/run_sabueso_diagnostics.py NEW_DIRECTORY` in the declared
`sabueso_diagnostics_env.yaml`, with the fixed Sabueso source installed. Add
`--filtered` for a separate application run with WARNING delivery disabled.
`inspect_sabueso_diagnostics.answers(ROOT)` reads retained evidence without Sabueso,
PyUnitWizard, Ackredit or NumPy. Reference checks use Recorda's support closure.

## Scientific/source oracle and diagnostic oracle

Sabueso `68dac8f8bfc35944f5b6dd59aca8cb2a2819388d` is an ordinary source-built
installed wheel. Its dirty concurrent checkout is not used. Published SMonitor
0.19.0 py_1, ArgDigest 0.15.0 py_0, DepDigest 0.13.0 py_0, PyUnitWizard 0.28.1 py_0
and Ackredit 0.11.0 py_0 provide its support closure. Recorda's runtime stays at
`48a6c9a0630027f0f2c3d8d82215de8e27764913`.

The unchanged public UniProt P60174 fixture retains its original attribution and
source-byte hashes. A small RCSB-shaped entry, **9LAB**, is explicitly fictional;
it asserts no actual structure for this protein. The complete fixture maps one
structure relationship. The partial fixture declares unavailable instance fields.
Sabueso's public FixtureRCSBClient supplies them or injects a native transport error.
External source connections are forbidden. No private report function or invented
Lab warning substitutes for native producer behavior.

| Declared attempt | Native execution | Sabueso source/result facts | Selected native codes |
| --- | --- | --- | --- |
| Complete Card | succeeded | resolved P60174, source added, one fictional structure | none observed |
| Partial Card | succeeded | same protein, source partial, missing instance fields, structure retained | SABUESO-W-ENRICH-003 |
| Failed source within Card construction | succeeded | same protein, source error, fictional structure absent | SABUESO-W-ENRICH-001 |
| Public source query with native ConnectorError | failed | native acquisition trace retained; no Card returned | none selected |
| Retry Card | succeeded | source added; earlier failed attempt remains | none observed |

Direct, dormant decorated and explicitly recorded Card calls agree on native
identity, resolution, sequence, source outcomes and fictional structure presence.
These expected facts are checked independently of diagnostic codes. Per-execution
trace IDs/times are not scientific equality criteria. The session remains failed
because the public source query failed, despite its later successful retry.

Sabueso emits its catalog warnings from its stored enrichment outcomes. The
selected observer uses an immutable source/code allowlist and the already tested
bounded handler/lifecycle from Lab #14. Its default dummy allowlist is unchanged.
The observer cannot infer source completeness from zero observations. In a
separate ERROR-threshold application run, Python native warnings and partial/error
Card records remain, while selected SMonitor events are absent. Native warnings
promoted to errors retain native exception behavior and a failed operation.

## Retention, ownership and fault limits

Sabueso owns Cards, pinned snapshots, source assertions, sealed quantity nodes and
acquisition traces. The experiment persists their native representations without
conversion or quantity interpretation. Source status is a projection of retained
Sabueso quality records; it is not a new Recorda scientific quality score.

SMonitor owns native event dictionaries and prose. Explicit bundle collection
flushes deferred summaries; retain only the two reviewed source/code pairs and
full session/operation identities after context omission. All other bundle
sections are excluded. This review depends on the fixed attributed/public and
fictional inputs; it is not an exporter for arbitrary user objects or secrets.

The application owns the selected association and local reference index. Selection
stores only fixed code/source/severity/kind/ordinal and bounded coverage facts.
Native catalog text is retained in the reviewed event artifact, not the selected
association. Every file is limited to one MiB; existing reference checks observe
local SHA-256 bytes rather than certify scientific correctness or authenticity.

Missing/changed Cards and diagnostic artifacts remain independently unavailable,
without changing saved execution. An isolated reader answers the source question
with no scientific producers. Ordinary artifact faults expose omissions/gaps and
preserve exact native result/error objects. A hard-exit child exits on the actual
native partial diagnostic during the declared scientific call: work remains
incomplete and no completed artifact is claimed. Existing core writer reliability
is unchanged. Native process interrupts/cancellation retain their behavior.

## Qualification and decision

The [local receipt](evidence/sabueso_diagnostics_linux_py314.json) records the
installed pair and frozen source/wheel/provider hashes: **380 passed/four historical
Sabueso skips** (305 core + 75 Lab), **16 new cases**, seven notebooks/**55 code
cells**, and **14 kernel-fault cells**. The 47 targeted native/association cases pass.
An initial test expected a null context after bundle omission; the provider
correctly removes the key. The receiving assertion was corrected before qualification.
Exact implementation CI now passes as recorded below; configured lanes alone are
not qualification. Python 3.11–3.14 native lanes select the 16 new cases and the
31 existing association regressions using published pytest-receptor 1.1.0.

Local native Conda installation stores archive-relative noarch paths in
`paths_data`; Recorda's unchanged development preflight expects installation-relative
paths and rejects that mapping (`uibcdf/recorda#23`). Local qualification explicitly
maps noarch `site-packages` to the interpreter's installation directory, checks
membership in Conda's actual managed files, and verifies each Python-file hash.
It does not rewrite metadata or claim the unchanged checker passed. Hosted
micromamba lanes also execute Recorda's existing preflight.

The native Card establishes the source outcome; the diagnostic provides an
explanation and next-step hint; Recorda binds both to the declared attempt and
retained files. Existing public references suffice for this bounded real-library
question. The explicit scope/retention is application code; no reusable automatic
attachment guarantee or core context API is introduced. A broader ordinary-call
adapter would need a separate public context/attachment proposal and its own
receiving qualification. No MOLI routing change is selected.

Historical Sabueso #5/#6 receipts and the synthetic #14 receipts remain unchanged.
This is a controlled real-library technical trial, not live source completeness,
production adoption, human usability, release/OS/distribution or replay evidence.

Final review corrected ordinary reference-error precedence for native warnings,
interrupts and cancellation (five additional receiving cases). Initial hosted
preflight rejected the new unclassified environment; explicit route/provider
admission and five negative cases now pass. Initial receipts remain retained.

[Corrected exact-pair CI](https://github.com/uibcdf/recorda-lab/actions/runs/37584430143)
passes **13/13 jobs** at Lab `a0376799c25c6b650ffa79aa6e4012601892d24c`, with
unchanged Recorda `48a6c9a0630027f0f2c3d8d82215de8e27764913` and fixed clean Sabueso.
Actual logs report **47 passes** in each native Python 3.11–3.14 lane, **364 passes/
20 explicit skips** in the existing scientific/recovery lane, **50 passes/29 optional
skips** in each existing kernel lane, and **six passes** per dummy minor. The
native cases execute in their dedicated lanes and remain explicitly skipped in
existing scientific/kernel environments. [Routine push](https://github.com/uibcdf/recorda-lab/actions/runs/37584383768)
passes four dummy jobs and skips three manual groups. Published pytest-receptor
1.1.0 and gh-run-receptor 1.2.0 supply actual verdicts; native GitHub conclusions
agree. [The hosted receipt](evidence/sabueso_diagnostics_hosted.json) retains source/
provider checks and raw capture/verdict hashes. Closing docs preserve every
corrected receipt-selected source byte. Earlier failed/initial receipts remain
unchanged and are not relabelled as passing final evidence.
