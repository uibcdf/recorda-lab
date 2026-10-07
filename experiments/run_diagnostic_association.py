"""Compare reviewed native events and selected associations at declared dummy attempts."""

import argparse
import hashlib
import json
import os
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

import recorda
from diagnostic_consumer import (
    AFTER,
    AGGREGATES,
    BEFORE,
    CODES,
    FAILED,
    SOURCE,
    SelectedDiagnostics,
    configure_application,
    observed_summary,
)

from recorda_lab import summarize


def retain(path, payload, owner, identifier, entries):
    data = json.dumps(payload, sort_keys=True, allow_nan=False).encode()
    if len(data) > 1024 * 1024:
        raise ValueError("trial artifact byte budget exceeded")
    path.write_bytes(data)
    reference = recorda.Reference(
        owner=owner, identifier=identifier, revision="1", digest=hashlib.sha256(data).hexdigest()
    )
    entries.append({"reference": asdict(reference), "path": path.name})
    return reference


def reviewed_bundle(session_id, operation_id):
    """Explicit review of a fixed synthetic producer, not a general privacy exporter.

    Native event dictionaries are retained as emitted. Unrelated sections/events
    are omitted; argv, catalogs/configuration, provider locations and reports are
    deliberately not persisted. collect_bundle flushes summaries before selection.
    """
    import smonitor

    bundle = smonitor.collect_bundle(max_events=512, drop_context=True)
    events = [
        event
        for event in bundle["events"]
        if event.get("source") == SOURCE
        and event.get("code") in set(CODES) | AGGREGATES
        and event.get("extra", {}).get("recorda_operation_id") == operation_id
        and event.get("extra", {}).get("recorda_session_id") == session_id
    ]
    return {
        "smonitor_version": bundle["smonitor_version"],
        "runtime": bundle["runtime"],
        "events": events,
        "redactions": {
            "drop_context": True,
            "review": "fixed synthetic consumer catalog and caller-owned opaque IDs",
            "omitted_sections": [
                "argv",
                "python",
                "platform",
                "config",
                "policy",
                "codes",
                "internal_codes",
                "signals",
                "providers",
                "report",
                "triage",
            ],
            "coverage": "bounded selected operation events; other native history omitted",
        },
    }


def attempt(session, sink, destination, name, samples, entries, *, writer=retain):
    """Retain failed-attempt diagnostics before native error propagation finishes."""
    result, native_error = None, None
    with session.operation(
        "recorda_lab.summarize",
        parameters={"trial_attempt": name},
        implementation={"package": "recorda-lab", "callable": "recorda_lab.summarize"},
    ) as operation:
        try:
            with sink.boundary(session, operation):
                result = observed_summary(samples, diagnostics=sink)
        except BaseException as error:
            native_error = error
            raise
        finally:
            artifacts = {}
            try:
                # Bundle collection can deliver deferred summaries after boundary
                # closure; originating facts are checked by the selected sink.
                native = reviewed_bundle(session.id, operation.id)
                selected = sink.snapshot(session.id)
                selected["operations"] = [
                    item for item in selected["operations"] if item["operation_id"] == operation.id
                ]
                for kind, payload, owner in (
                    ("bundle", native, "smonitor"),
                    ("association", selected, "recorda-lab-consumer"),
                ):
                    artifacts[kind] = writer(
                        destination / f"{name}-{kind}.json",
                        payload,
                        owner,
                        f"{operation.id}:{kind}",
                        entries,
                    )
            except Exception:
                sink.mark_gap("artifact_fault", (session.id, operation.id))
                artifacts = {"bundle": recorda.Omitted(), "association": recorda.Omitted()}
            for kind, reference in artifacts.items():
                try:
                    operation.output(kind, reference)
                except Exception:
                    if native_error is None:
                        raise
                    # The journal can be broken, but the existing native error
                    # keeps precedence. Core terminal handling exposes incompleteness.
                    native_error.add_note("Diagnostic reference persistence is unresolved.")
            if result is not None:
                path = destination / "native-result.json"
                if path.exists():
                    reference = next(
                        recorda.Reference(**entry["reference"])
                        for entry in entries
                        if entry["path"] == path.name
                    )
                    assert json.loads(path.read_text()) == result.to_dict()
                else:
                    reference = retain(
                        path, result.to_dict(), "recorda-lab", result.identifier, entries
                    )
                operation.output("native_result", reference)
    return result


def run(destination):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)

    manager = configure_application()
    sink = SelectedDiagnostics()
    sink.attach(manager)
    entries, results = [], []
    session = recorda.RecordingSession("diagnostic-comparison", path=destination / "record.jsonl")
    expected_error = None
    try:
        with session:
            results.append(attempt(session, sink, destination, "success", [1, 2, 3, 4], entries))
            try:
                attempt(session, sink, destination, "failure", [], entries)
            except ValueError as error:
                expected_error = error
            results.append(attempt(session, sink, destination, "retry", [1, 2, 3, 4], entries))
    finally:
        sink.detach()
    assert expected_error is not None
    native = summarize([1, 2, 3, 4])
    dormant = observed_summary([1, 2, 3, 4])
    assert native.to_dict() == dormant.to_dict() == results[0].to_dict() == results[1].to_dict()
    assert native.count == 4 and native.mean == 2.5 and native.variance == 1.25
    record = recorda.inspect(destination / "record.jsonl")
    assert record.status == "failed"  # Later retry cannot rewrite the failed attempt.
    assert [op["status"] for op in record.operations] == ["succeeded", "failed", "succeeded"]
    selected = sink.snapshot(session.id)
    by_operation = {item["operation_id"]: item for item in selected["operations"]}
    expected_codes = [[BEFORE, AFTER], [BEFORE, FAILED], [BEFORE, AFTER]]
    for operation, codes in zip(record.operations, expected_codes, strict=True):
        assert [entry["code"] for entry in by_operation[operation["id"]]["entries"]] == codes
        assert by_operation[operation["id"]]["coverage"]["state"] == "observed_under_policy"
    (destination / "index.json").write_text(json.dumps(entries, indent=2) + "\n")
    refs = {recorda.Reference(**item["reference"]): item["path"] for item in entries}
    resolver = recorda.LocalFileResolver(destination, refs, digest_algorithm="sha256")
    before = recorda.check_references(record, resolver=resolver)
    artifact = destination / "failure-association.json"
    original = artifact.read_bytes()
    artifact.unlink()
    missing = recorda.check_references(record, resolver=resolver)
    artifact.write_bytes(b"{}")
    altered = recorda.check_references(record, resolver=resolver)
    artifact.write_bytes(original)
    restored = recorda.check_references(record, resolver=resolver)
    assert before == restored
    child = subprocess.run(
        [
            sys.executable,
            "-c",
            "import os,recorda,sys,smonitor; sys.path.insert(0,sys.argv[2]); "
            "from diagnostic_consumer import SelectedDiagnostics,configure_application,BEFORE,SOURCE; "
            "sink=SelectedDiagnostics(); sink.attach(configure_application()); "
            "s=recorda.start('interrupted',path=sys.argv[1]); "
            "op=s.operation('recorda_lab.summarize'); op.__enter__(); "
            "scope=sink.boundary(s,op); scope.__enter__(); "
            "smonitor.emit('WARNING','',source=SOURCE,code=BEFORE); os._exit(23)",
            str(destination / "interrupted.jsonl"),
            str(Path(__file__).resolve().parent),
        ],
        check=False,
        env={key: value for key, value in os.environ.items() if key != "PYTHONPATH"},
    )
    assert child.returncode == 23
    interrupted = recorda.inspect(destination / "interrupted.jsonl")
    assert interrupted.status == "incomplete"
    report = {
        "schema": "recorda-lab.diagnostic-comparison/0.1",
        "science": native.to_dict(),
        "record": asdict(record),
        "association": selected,
        "references": {
            "intact": before,
            "missing": missing,
            "altered": altered,
            "restored": restored,
        },
        "views": {
            "intact": recorda.inspection_view(record, reference_report=before),
            "missing": recorda.inspection_view(record, reference_report=missing),
        },
        "interrupted": asdict(interrupted),
        "comparison": {
            "native_bundle": "native message/runtime/fingerprint details; explicit review and operation join",
            "association": "fixed selected code/level/ordinal and declared attempt coverage; no free text",
            "limit": "consumer-attributed synthetic diagnostics, not native SciPy warnings or complete capture",
        },
    }
    (destination / "acceptance.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    report = run(args.destination)
    print(json.dumps({"science": report["science"], "execution": report["record"]["status"]}))


if __name__ == "__main__":
    main()
