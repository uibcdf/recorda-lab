# Controlled diagnostic association — Lab #14

The experiment selected by `uibcdf/recorda#15` compares reviewed native SMonitor
events with bounded consumer-owned per-attempt associations. It uses current
public explicit operations/references; no Recorda runtime or automatic context API
is changed. Native dummy science remains byte-identical and dependency-free.

Run `python experiments/run_diagnostic_association.py NEW_DIRECTORY` in the
declared Recorda environment. Notebook 08 executes this runner in a fresh process
and displays native events, selected associations, scientific facts and current
reference observations. Published SMonitor 0.19.0 py_1 supplies the public APIs.

## Scientific and diagnostic oracles

Native/dormant/recorded summaries of fictional `[1, 2, 3, 4]` have count 4, mean
2.5 and population variance 1.25. Empty samples actually raise the dummy's native
ValueError. Success, failed attempt and retry are three distinct declared
operations; the session remains failed after retry success. Exact native return/
error objects are tested independently of serialization.

The small producer belongs to **recorda-lab-consumer**, not the dummy library or
SciPy. Its fixed catalog announces before-call, observed failure or observed return.
The deterministic expected sequences are `[BEFORE, AFTER]`, `[BEFORE, FAILED]`,
`[BEFORE, AFTER]`. These controlled messages test association mechanics, not real
scientific warning usefulness or native SciPy SMonitor emission.

## Alternatives and ownership

| Question / detail | Reviewed native bundle | Selected association |
| --- | --- | --- |
| Which selected observations accompanied this attempt? | Join retained native event extras to the public operation ID. | Read fixed selected codes/ordinals beside the operation ID. |
| What native diagnostic text/runtime/fingerprint was retained? | Native event dictionaries retain those fields. | Free text, native runtime IDs and fingerprint are absent. |
| What observation coverage is declared? | Explicit review declares bounded selection and omitted sections/history. | Fixed state/gaps and aggregate facts declare conditional delivered observation. |
| Where are bytes retained? | Application-owned local index plus full `smonitor` reference. | Application-owned local index plus full `recorda-lab-consumer` reference. |
| Does missing diagnostic retention change science? | Existing byte checker observes missing/altered files. | Reader reports unavailable codes, retaining original execution. |

The application calls public `collect_bundle(max_events=512, drop_context=True)`
explicitly; that call flushes and delivers deferred summaries. It retains unchanged
native event dictionaries after the declared context omission, only for the
controlled source/catalog and full session/operation identity pair.
The reviewed subset omits argv, configuration/catalogs, provider locations,
reports/triage and unrelated events. It discloses those omissions in `redactions`.
This is an application-reviewed **subset of a native bundle**, not a general safe
export profile or an automatically retained complete SMonitor report. It works
because the producer/data/policy are fixed and synthetic; arbitrary caller inputs
would require a new review. SMonitor #40 owns the reusable strict export opportunity.

Recorda owns declared attempt identity/lifecycle and reference occurrences.
SMonitor owns diagnostic code/rendering and native event format. The consumer
owns selection, association schema, retention and diagnostic gaps. Native results
retain the dummy owner and scientific representation. Digest matches establish
only local byte observations, not authenticity, scientific correctness or replay.

## Lifecycle and bounded facts

The application configures SMonitor once, attaches a bounded handler, then uses
public `session.id` / `operation.id` and its own ContextVar/locked registry around
explicit operations. No private Recorda/SMonitor context or observer is accessed.
Detailed capture permissions are retained through explicit
`diagnostic_scope(CapturePolicy(), safe_extra=...)`; safe facts partition native
aggregation, an acknowledged application policy choice. A restrictive parent
still wins. The experiment adds no broad signal decorator or per-operation
global configuration.

The selected sidecar `recorda-lab.diagnostic-association/0.1` contains session/
operation/parent identities, fixed code/source/severity/kind, local ordinals and
optional exact nonnegative 63-bit producer summary counts. It excludes arbitrary
messages, hints, human summaries, contexts/args, ordinary extras, exception text,
tags, paths and native objects. Hostile values are neither stringified nor copied.
It is not an authenticated source identity or a content-based secrets classifier.

Budgets are 32 registered operations, 256 entries per operation, 512 entries
overall and one MiB per serialized artifact. Overflow is counted and marks retained
operation coverage limited; excess registry operations remain unassigned rather
than preventing the scientific call. The registry retains at most 32 closed
origins (below the architectural 128-origin ceiling). Counters saturate at 63 bits.
Snapshots copy facts; mutation does not affect later observations.

An inherited SMonitor scope may already use all 32 safe metadata fields. If new
association identities cannot be added, the consumer keeps the parent's capture
restrictions, records `provider_fault`, and runs the native scientific call without
claiming assigned observations. Ordinary scope setup/cleanup errors are diagnostic
gaps, not replacement scientific failures; native interrupts still propagate.

Observation states are `observed_under_policy`, `limited` and `incomplete` with
fixed gap labels. Zero observations do not mean no warnings occurred: disabled
emission, levels, filters, routes, duplicates and unknown producer work affect
delivery. Counters outside operations are application-wide; they are not derived
from global SMonitor report differences or assigned as per-attempt totals.

## Concurrency, feedback and faults

Nested/interleaved async operations keep their own identities and recorded parents.
An inherited child context after closure is stale: ordinary events are excluded,
while deferred aggregates may reference a known closed origin. Individual entries
and aggregate `total_occurrences`/`suppressed_count` stay separate; they are not
summed into an invented warning count. Fingerprint does not identify an attempt.

Threads explicitly use a fresh `copy_context().run` per submission or independent
`Context().run`. Cross-process routing is not implemented. The controlled hard-exit
child actually emits within the declared diagnostic scope, then exits before
retention/finalization: Recorda retains incomplete work, with no complete diagnostic
artifact claimed.

The handler allowlist excludes unknown codes, Recorda recovery and other sources.
It does not emit, write the journal or generate scientific operations. A reentrancy
guard counts observation gaps. Attach/cleanup/sink/provider/artifact ordinary
faults are contained and expose fixed gaps/counters; cancellation and process
interrupts retain native precedence. Native failures keep exact object identity.
Partial/unlinked artifacts are not promoted to completed retention; a failed
artifact write produces explicit omitted references. Core writer reliability is
unchanged; it is not converted to universal best effort.

Handler reconfiguration is an application-owned fact: the application explicitly
declares replacement, rather than inspecting a private handler list or inferring
attachment from zero observations. Failed removal stops local acceptance even if
the provider still holds the handler. This controlled lifecycle is not a reusable
attachment guarantee across arbitrary reconfiguration.

## Reading and qualification

`inspect_diagnostic_association.answers(ROOT)` reads the journal, bounded local
index and matched association artifacts. Scientific and controlled diagnostic
producers are unavailable in the isolated reader test. Native reference checking
still needs Recorda's published support closure; plain journal reading remains
independent. Missing/mismatched artifacts give unavailable codes, not a success
or no-warning inference. Association session/operation/parent binding is checked.

The [local receipt](evidence/diagnostic_association_linux_py314.json) retains the
exact frozen Lab/core source manifests and ordinary installed wheel/provider hashes.
Corrected Linux Python 3.14.7 qualification passes **364 tests/four explicit Sabueso
skips** (305 core + 59 Lab), including **31 new receiving cases**, seven selected notebooks/**55 code
cells** and the **14-cell** kernel fault scenario. Published pytest-receptor 1.1.0,
provider verification, pip check, governance/canonical MOLI and Ruff pass. The
initial catalogue-replacement defect is preserved with its resolved regression
in the local receipt.

[Corrected exact-pair manual CI](https://github.com/uibcdf/recorda-lab/actions/runs/37581680564)
passes all **nine jobs** at Lab `214a68d93a878bfe2b0d70a3aa90f81e00620db1` with
Recorda `48a6c9a0630027f0f2c3d8d82215de8e27764913`, the unchanged workflow default.
Actual logs report 364 passes/four Sabueso skips in the scientific/recovery lane,
50 passes/13 optional skips in each Python 3.11–3.14 kernel lane, and six dummy
passes per minor. [Routine push CI](https://github.com/uibcdf/recorda-lab/actions/runs/37581672334)
passes four dummy jobs and skips the two manual groups. Published gh-run-receptor
1.2.0 and native GitHub conclusions agree; raw capture/verdict/source-selection
hashes are retained in [the hosted receipt](evidence/diagnostic_association_hosted.json).
The initial Lab `8d81819` pair, with 360 passes/27 receiving cases, remains in
`diagnostic_association_*_initial.json`, including its earlier nine passing jobs.
Final review added four regressions for ordinary scope setup/cleanup faults and
preserves native outcomes when the inherited safe-metadata budget is full.
Later closing documentation preserves every corrected local receipt-selected byte.
No configured CI is treated as executed evidence. Provider defects remain
`uibcdf/smonitor#41` (buffer resizing) and `uibcdf/smonitor#42` (degradation warning
precedence); the fault-contained controlled sink does not qualify those fixes.
All three proposals are coordinated in `uibcdf/moli#62`.

## Decision gate

The two existing-reference alternatives can answer this controlled attempt
question. A selected sidecar provides bounded facts and explicit gaps; reviewed
native events retain more diagnostic detail and require an explicit join/review.
Lab #14 is qualified, including scope-budget containment. This dummy evidence does not
yet justify a reusable automatic core bridge: a real producer/user question and
separately scoped public context/attachment decision are required. Standalone
acceptance, distribution/OS/coverage, human usability and replay remain separate.
