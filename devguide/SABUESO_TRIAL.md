# Controlled standalone Sabueso trial

Owner: `uibcdf/recorda-lab#5`; recording substrate: `uibcdf/recorda#1`.

## Scientific acceptance

The unchanged UniProt P60174 response is retrieved, then its primary accession is
actually consumed by a nested entity-resolution call. Its native Card and resolution
agree with direct and dormant calls. The inactive P00938 response points to human
P60174 and chimpanzee P60175: resolution without an organism is ambiguous; selecting
9606 resolves human TIM while retaining the alternative and original decision rule.
P12345 is an injected fixture source failure, not an assertion about live UniProt.
Resolving it returns a native error result; retrieving it raises native ConnectorError.
Recorda records these as a succeeded call and a failed call respectively.

Seven declared operations retain lineage, implementation identities and safe references.
The session intentionally finishes failed. Internal helpers and arbitrary library calls
are unobserved. Semantic profiles are labels, not a policy engine. The dummy package,
Sabueso, PyUnitWizard and Recorda runtime source are unchanged by this experiment.

## Native ownership and retained artifacts

Sabueso owns entity identities, Cards, pinned revisions, resolution decisions and
acquisition traces, including its own source credits. UniProt owns the source data.
The lab stores native serializations and separate manifests; retained EntityResolution
snapshots have lab-owned receipts because that object has no native snapshot identifier.
Native Card snapshot identity differs from the SHA-256 of its serialized file bytes.
No unit conversion or quantity reinterpretation is performed by the inspector.

Exact-type trusted adapters are deliberately limited to the supplied public fixtures,
known queries, fixture clients and UniProt-only resolvers. Unknown contracts are omitted.
Reusing a mutated retained native result omits the stale reference. Callbacks are trusted
code, not a general privacy or serialization policy. They do not inspect opaque repr.

The core records exception type and preserves the same exception instance. The caller
explicitly retains its native acquisition trace and links it to the failed operation in
the lab index. This is an acknowledged gap in automatic boundary capture. The follow-up is tracked
by `uibcdf/recorda#7`; no exception hook or shared MOLI contract is introduced here.

## Qualification and limits

Use Python 3.14 in the existing co-development environment and published
pytest-receptor 1.1.0. Select `RECORDA_LAB_SABUESO=1`; selecting an unavailable
dependency fails rather than silently skipping. Add `RECORDA_LAB_NOTEBOOK=1` for
real-kernel execution; add `RECORDA_LAB_SCIPY=1` for the complete laboratory suite.
The baseline Recorda is 0.1.0 at `7e0c8dc79fbc529826d27e467de381e248c36da8`.
`evidence/sabueso_linux_py314.json` records tested source hashes and participants.
Sabueso and several providers are editable development checkouts. Their live shared
environment passed the full suite, but concurrent provider edits prevented sealing
those live hashes. The final receipted execution uses temporary frozen copies of
their package trees via PYTHONPATH and verifies every retained package byte before
and after tests. Original observed checkout identities and exact frozen package
manifests are separate evidence fields. These are development source snapshots;
local evidence does not qualify published packages or a clean installed closure.

Tests prohibit source connections, check scientific decisions and return/exception
identity, and execute the receipt reader in Python `-S` without Sabueso, Ackredit or
PyUnitWizard. Removing or changing a retained file fails inspection. The eight-cell
notebook uses start/stop across cells with ordinary decorated calls. Raw retained
traces preserve full native events; the inspection summary intentionally shows selected
fields. Expected observed network attempts are zero.

Source attribution and byte hashes are in
`../experiments/fixtures/sabueso_uniprot/NOTICE.md`. Copying fixtures does not verify
the current remote source release. Receipts are not authenticated manifests, a generic
integrity API or computational replay. No ProjectContext, routing, source-pipeline
coverage, production adoption, public OS support or distribution is qualified.
Routine Lab CI exercises the dummy on Python 3.11–3.14; Sabueso is locally qualified
on Linux 3.14 only. Exact local commands and remote baseline gates belong to evidence.
