"""Caller-owned Sabueso boundaries and narrow adapters for frozen public fixtures."""

import hashlib
import json
from dataclasses import asdict
from pathlib import Path

import recorda
import sabueso
from sabueso.core.card import Card
from sabueso.resolver import EntityQuery, EntityResolution, EntityResolver
from sabueso.tools.db.uniprot import FixtureUniProtClient
from sabueso.tools.db.uniprot import get_entry as native_get_entry

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "sabueso_uniprot"
ACCESSIONS = {"P60174", "P60175", "P00938", "P12345"}
RETRIEVED_AT = "2026-09-23"

# These are local aliases of actual scientific APIs, not module monkeypatches.
get_entry = recorda.record("sabueso.uniprot.get_entry", profile="knowledge_retrieval")(
    native_get_entry
)
resolve = recorda.record("sabueso.resolve", profile="entity_resolution")(sabueso.resolve)


@recorda.record("recorda-lab.resolve_retrieved_entry", profile="entity_resolution")
def resolve_retrieved_entry(envelope, resolver):
    """Use the accession in the retrieved response as the actual resolution input."""
    return resolve(envelope["record"]["primaryAccession"], resolver=resolver)


def fixture_client(*, failing=False, directory=FIXTURES):
    return FixtureUniProtClient(
        directory, retrieved_at=RETRIEVED_AT, failing={"P12345"} if failing else set()
    )


class SabuesoArtifacts:
    """Retain known native files; references do not transfer scientific ownership."""

    def __init__(self, destination, fixture_directory=FIXTURES):
        self.destination = Path(destination)
        self.destination.mkdir(parents=True, exist_ok=False)
        self.fixture_directory = Path(fixture_directory).resolve()
        self.files = []
        self.fixtures = {}
        self.fixture_payloads = {}
        for accession in sorted(ACCESSIONS - {"P12345"}):
            path = self.fixture_directory / f"{accession}.json"
            data = path.read_bytes()
            entry = json.loads(data)
            self.fixture_payloads[accession] = entry
            self.fixtures[accession] = self._save(
                data,
                owner="UniProt",
                identifier=f"uniprot:{accession}",
                revision=str(entry["entryAudit"]["entryVersion"])
                if entry.get("entryAudit", {}).get("entryVersion") is not None
                else None,
                kind="fixture",
            )
        self.retained = {}

    def _save(self, data, *, owner="recorda-lab", identifier=None, revision=None, kind):
        digest = hashlib.sha256(data).hexdigest()
        path = self.destination / f"{kind}-{digest}.json"
        reference = recorda.Reference(
            owner=owner,
            identifier=identifier or f"sha256:{digest}",
            revision=revision,
            digest=digest,
        )
        entry = {"path": path.name, "kind": kind, "reference": asdict(reference)}
        if path.exists():
            assert path.read_bytes() == data
        else:
            path.write_bytes(data)
        if entry not in self.files:
            self.files.append(entry)
        return reference

    def _json(self, value, **kwargs):
        return self._save(
            (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode(),
            **kwargs,
        )

    def trace(self, value):
        if type(value) is not dict or value.get("format") != "sabueso.acquisition_trace@1":
            raise ValueError("this trial requires a native acquisition trace")
        for event in value["records"]:
            if (
                event["source"] != "UniProt"
                or event["operation"] != "entry"
                or event["query"].get("accession") not in ACCESSIONS
                or set(event["query"]) != {"accession"}
                or event["requests"]
                or event["network_attempts"] != 0
                or event["access"] != "fixture"
            ):
                raise ValueError("native trace is outside this fixture-only trial")
        return self._json(value, owner="sabueso", identifier=value["id"], kind="trace")

    def envelope(self, value):
        if type(value) is dict and set(value) == {"resolver"}:
            resolver = self.resolver(value["resolver"])
            if not isinstance(resolver, recorda.Reference):
                return resolver
            return self._json(
                {"schema": "recorda-lab.sabueso-options/0.1", "resolver": asdict(resolver)},
                kind="options",
            )
        if (
            type(value) is not dict
            or set(value)
            != {"source", "kind", "query", "retrieved_at", "version", "record", "acquisition_trace"}
            or value.get("source") != "UniProt"
            or value.get("kind") != "entry"
            or value.get("query", {}).get("accession") not in ACCESSIONS
            or value.get("retrieved_at") != RETRIEVED_AT
            or "acquisition_trace" not in value
            or value.get("record")
            != self.fixture_payloads.get(value.get("query", {}).get("accession"))
        ):
            return recorda.Omitted("unsupported_value")
        trace = self.trace(value["acquisition_trace"])
        # Separate the unchanged scientific envelope and its original runtime trace.
        payload = self._json(
            {key: item for key, item in value.items() if key != "acquisition_trace"},
            kind="envelope",
        )
        return self._json(
            {
                "schema": "recorda-lab.sabueso-envelope/0.1",
                "producer": "sabueso",
                "payload": asdict(payload),
                "trace": asdict(trace),
            },
            kind="envelope-manifest",
        )

    def query(self, value):
        if (
            type(value) is not EntityQuery
            or value.identifier not in ACCESSIONS
            or value.name is not None
            or value.organism not in (None, 9606)
            or value.include_subtaxa
            or value.entity_type is not None
        ):
            return recorda.Omitted("unsupported_value")
        return self._json(asdict(value), kind="query")

    def client(self, value):
        if (
            type(value) is not FixtureUniProtClient
            or value.directory.resolve() != self.fixture_directory
            or value.retrieved_at != RETRIEVED_AT
            or not value.failing <= {"P12345"}
        ):
            return recorda.Omitted("unsupported_value")
        return self._json(
            {
                "schema": "recorda-lab.sabueso-client/0.1",
                "access": "fixture",
                "retrieved_at": value.retrieved_at,
                "failing": sorted(value.failing),
                "fixtures": {key: asdict(ref) for key, ref in self.fixtures.items()},
            },
            kind="client",
        )

    def resolver(self, value):
        if type(value) is not EntityResolver or value.policy not in (None, "prefer_reviewed@1"):
            return recorda.Omitted("unsupported_value")
        client = self.client(value.uniprot)
        if not isinstance(client, recorda.Reference):
            return client
        return self._json(
            {
                "schema": "recorda-lab.sabueso-resolver/0.1",
                "policy": value.policy,
                "uniprot": asdict(client),
                "scope": "UniProt-only trial queries",
            },
            kind="resolver",
        )

    def result(self, value):
        if (
            type(value) is not tuple
            or len(value) != 2
            or type(value[1]) is not EntityResolution
            or (value[0] is not None and type(value[0]) is not Card)
        ):
            return recorda.Omitted("unsupported_value")
        cached = self.retained.get(id(value))
        card, resolution = value
        payload = resolution.to_dict()
        native_trace = resolution.acquisition_trace
        snapshot = (
            json.dumps(payload, sort_keys=True, allow_nan=False),
            card.snapshot_id() if card is not None else None,
            json.dumps(native_trace, sort_keys=True, allow_nan=False),
        )
        if cached is not None and cached[0] is value:
            return cached[1] if cached[2] == snapshot else recorda.Omitted("unsupported_value")
        trace = self.trace(native_trace)
        # EntityResolution has no native snapshot id. The lab owns this retained
        # snapshot, while its status, decisions and entity identity remain native.
        resolution_ref = self._json(payload, kind="resolution")
        card_ref = None
        if card is not None:
            card_ref = self._json(
                card.to_dict(),
                owner="sabueso",
                identifier=card.pinned_ref(),
                revision=card.snapshot_id(),
                kind="card",
            )
        manifest = {
            "schema": "recorda-lab.sabueso-result/0.1",
            "producer": "sabueso",
            "resolution": asdict(resolution_ref),
            "trace": asdict(trace),
            "card": asdict(card_ref) if card_ref is not None else None,
        }
        ref = self._json(manifest, kind="result")
        self.retained[id(value)] = (value, ref, snapshot)
        return ref

    @property
    def adapters(self):
        return {
            dict: self.envelope,
            tuple: self.result,
            EntityQuery: self.query,
            FixtureUniProtClient: self.client,
            EntityResolver: self.resolver,
        }

    def finish(self, *, journal, failed_trace=None, failed_operation=None):
        index = {
            "schema": "recorda-lab.sabueso-artifacts/0.1",
            "journal": journal,
            "files": self.files,
            "failure": {"operation": failed_operation, "trace": asdict(failed_trace)}
            if failed_trace is not None
            else None,
        }
        (self.destination / "index.json").write_text(json.dumps(index, indent=2) + "\n")
        return index
