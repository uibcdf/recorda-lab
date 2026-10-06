"""Qualify native Sabueso retrieval, resolution, ambiguity and source failure offline."""

import argparse
import hashlib
import json
from pathlib import Path

import recorda
import sabueso
from inspect_sabueso_trial import inspect_trial
from sabueso.core.errors import ConnectorError
from sabueso.resolver import EntityQuery, EntityResolver
from sabueso.tools.db.uniprot import get_entry as native_get_entry
from sabueso_consumer import (
    FIXTURES,
    SabuesoArtifacts,
    fixture_client,
    get_entry,
    resolve,
    resolve_retrieved_entry,
)


def run(destination):
    destination = Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in FIXTURES.glob("*.json")}
    client = fixture_client()
    failing = fixture_client(failing=True)
    resolver = EntityResolver(client)
    failure_resolver = EntityResolver(failing)

    # Compare scientific content, not the per-execution ids/times of native traces.
    direct_entry = native_get_entry("P60174", client=client)
    dormant_entry = get_entry("P60174", client=client)
    assert direct_entry["record"] == dormant_entry["record"]
    direct_card, direct_resolution = sabueso.resolve("P60174", resolver=resolver)
    dormant_card, dormant_resolution = resolve("P60174", resolver=resolver)
    assert direct_card.snapshot_id() == dormant_card.snapshot_id()
    assert direct_resolution.to_dict() == dormant_resolution.to_dict()

    artifacts = SabuesoArtifacts(destination / "native")
    handle = recorda.start(
        "sabueso-public-fixture-trial",
        path=destination / "session.jsonl",
        gaps=[
            "unwrapped source helpers",
            "unregistered exception provenance is omitted",
            "no MOLI project context, routing or complete pipeline capture",
        ],
        reference_adapters=artifacts.adapters,
    )
    try:
        envelope = get_entry("P60174", client=client)
        result = resolve_retrieved_entry(envelope, resolver)
        card, resolution = result
        assert card.snapshot_id() == direct_card.snapshot_id()
        assert resolution.to_dict() == direct_resolution.to_dict()
        assert card.acquisition_trace == resolution.acquisition_trace
        assert envelope["record"] == direct_entry["record"]
        ambiguous = resolve(EntityQuery(identifier="P00938"), resolver=resolver)
        selected = resolve(EntityQuery(identifier="P00938", organism=9606), resolver=resolver)
        returned_error = resolve("P12345", resolver=failure_resolver)
        assert ambiguous[0] is None and ambiguous[1].status == "ambiguous"
        assert [c["entity_ref"] for c in ambiguous[1].candidates] == [
            "sabueso:protein:uniprot:P60174",
            "sabueso:protein:uniprot:P60175",
        ]
        assert selected[1].status == "resolved"
        assert selected[1].decision["rules"] == ["inactive_demerged_filtered_by_organism"]
        assert selected[1].alternatives[0]["entity_ref"] == "sabueso:protein:uniprot:P60175"
        assert returned_error[0] is None and returned_error[1].status == "error"
        try:
            get_entry("P12345", client=failing)
        except ConnectorError:
            pass
        else:
            raise AssertionError("the actual fixture source failure did not escape")
    finally:
        record = handle.stop()
    assert record.operations[-1]["exception"]["reference"]["owner"] == "sabueso"
    assert record.status == "failed"
    assert len(record.operations) == 7
    assert record.operations[-1]["exception"]["type"] == (
        f"{ConnectorError.__module__}.{ConnectorError.__qualname__}"
    )
    # The real resolution target returned normally: semantic error stays native.
    assert record.operations[-2]["status"] == "succeeded"
    assert record.operations[2]["parent_id"] == record.operations[1]["id"]
    assert record.operations[0]["outputs"]["return"] == record.operations[1]["inputs"]["envelope"]
    artifacts.finish(journal="session.jsonl")
    report = inspect_trial(destination)
    assert before == {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in FIXTURES.glob("*.json")
    }
    assert report["semantic_statuses"] == ["resolved", "resolved", "ambiguous", "resolved", "error"]
    assert report["network_attempts"] == 0
    (destination / "acceptance.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "destination", type=Path, help="fresh directory for retained native artifacts"
    )
    print(json.dumps(run(parser.parse_args().destination), indent=2))


if __name__ == "__main__":
    main()
