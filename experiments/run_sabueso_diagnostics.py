"""Real Sabueso outcomes/diagnostics, controlled offline source responses (Lab #15)."""

import argparse
import json
import socket
import warnings
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

import recorda
import sabueso
import smonitor
from diagnostic_consumer import SelectedDiagnostics, configure_application
from inspect_sabueso_diagnostics import answers
from run_diagnostic_association import retain
from sabueso.core.errors import ConnectorError
from sabueso.resolver import EntityResolver, FixtureUniProtClient
from sabueso.tools.db.rcsb import FixtureRCSBClient, get_entry

FIXTURES = Path(__file__).resolve().parent / "fixtures"
PARTIAL = ("sabueso.warning.enrichment_partial", "SABUESO-W-ENRICH-003")
FAILED = ("sabueso.warning.enrichment_failed", "SABUESO-W-ENRICH-001")


class SabuesoDiagnostics(SelectedDiagnostics):
    allowlist = frozenset((PARTIAL, FAILED))


@contextmanager
def offline():
    """No source connections are permitted; this leaves real kernel sockets alone."""

    def forbidden(*args, **kwargs):
        raise AssertionError("external source connection forbidden in Lab #15")

    with patch.object(socket.socket, "connect", forbidden):
        yield


def resolver(kind):
    return EntityResolver(
        FixtureUniProtClient(FIXTURES / "sabueso_uniprot", retrieved_at="2026-09-23"),
        rcsb_client=FixtureRCSBClient(
            FIXTURES / "sabueso_diagnostics" / ("partial" if kind == "partial" else "complete"),
            retrieved_at="fictional-lab-response",
            failing={"9LAB"} if kind == "failure" else set(),
        ),
    )


def native_call(kind):
    return sabueso.resolve_protein_card("P60174", resolver=resolver(kind), structures=["9LAB"])


# Dormant instrumentation uses the same scientific call, outside a session.
recorded_call = recorda.record("sabueso.resolve_protein_card")(native_call)


def science(result):
    """Native meanings; deliberately exclude per-execution trace identities/times."""
    card, resolution = result
    return {
        "entity_ref": card.id,
        "resolution": resolution.status,
        "sequence": card.get("sequence.primary")["value"],
        "enrichments": card.quality["enrichments"],
        "fictional_structures": [
            row["object_ref"]
            for row in card.relationships("has_structure")
            if row["object_ref"] == "pdb:9LAB"
        ],
    }


def reviewed_events(session_id, operation_id):
    """Review fixed fixtures/catalog only; omit arbitrary bundle/context sections."""
    bundle = smonitor.collect_bundle(max_events=512, drop_context=True)
    return {
        "smonitor_version": bundle["smonitor_version"],
        "events": [
            event
            for event in bundle["events"]
            if (event.get("source"), event.get("code")) in SabuesoDiagnostics.allowlist
            and event.get("extra", {}).get("recorda_session_id") == session_id
            and event.get("extra", {}).get("recorda_operation_id") == operation_id
        ],
        "review": "Fixed attributed UniProt and fictional RCSB fixtures; native catalog prose retained",
        "omissions": "context, unrelated events, argv, config, catalogs, providers, report and triage",
        "coverage": "bounded delivered selected observations, not complete diagnostics",
    }


def attempt(session, sink, root, name, kind, files, *, writer=retain):
    result = error = None
    with session.operation(
        "sabueso.resolve_protein_card" if kind else "sabueso.rcsb.get_entry",
        parameters={"trial_attempt": name},
        implementation={"package": "sabueso", "version": sabueso.__version__},
    ) as operation:
        try:
            with sink.boundary(session, operation):
                if kind:
                    result = native_call(kind)
                else:
                    get_entry("9LAB", client=resolver("failure").rcsb)
        except ConnectorError as native_error:
            error = native_error
            # Public Recorda operation must observe the native failure.
            raise
        finally:
            artifacts = {}
            try:
                if result is not None:
                    card, resolution = result
                    artifacts["native_card"] = writer(
                        root / f"{name}-card.json",
                        card.to_dict(),
                        "sabueso",
                        card.id + "@" + card.snapshot_id(),
                        files,
                    )
                    artifacts["native_acquisition"] = writer(
                        root / f"{name}-acquisition.json",
                        card.acquisition_trace,
                        "sabueso",
                        card.acquisition_trace["id"],
                        files,
                    )
                elif error is not None:
                    artifacts["native_acquisition"] = writer(
                        root / f"{name}-acquisition.json",
                        error.acquisition_trace,
                        "sabueso",
                        error.acquisition_trace["id"],
                        files,
                    )
                artifacts["bundle"] = writer(
                    root / f"{name}-bundle.json",
                    reviewed_events(session.id, operation.id),
                    "smonitor",
                    operation.id + ":bundle",
                    files,
                )
                selected = sink.snapshot(session.id)
                selected["operations"] = [
                    row for row in selected["operations"] if row["operation_id"] == operation.id
                ]
                artifacts["association"] = writer(
                    root / f"{name}-association.json",
                    selected,
                    "recorda-lab-consumer",
                    operation.id + ":association",
                    files,
                )
            except Exception:
                sink.mark_gap("artifact_fault", (session.id, operation.id))
                artifacts = {
                    key: recorda.Omitted("adapter_error")
                    for key in ["native_card", "native_acquisition", "bundle", "association"]
                }
            for label, ref in artifacts.items():
                try:
                    operation.output(label, ref)
                except Exception:
                    if error is None:
                        raise
                    error.add_note("Native reference persistence is unresolved.")
    return result


def run(destination, *, filtered=False, writer=retain):
    root = Path(destination)
    root.mkdir(parents=True, exist_ok=False)
    configure_application(level="ERROR" if filtered else "WARNING")
    sink = SabuesoDiagnostics()
    sink.attach(smonitor.get_manager())
    files, comparisons, warning_types = [], [], []
    session = recorda.RecordingSession("native-sabueso-diagnostics", path=root / "record.jsonl")
    kinds = [
        ("complete", "complete"),
        ("partial", "partial"),
        ("source_failure", "failure"),
        ("source_exception", None),
        ("retry", "complete"),
    ]
    try:
        with offline(), warnings.catch_warnings(record=True) as observed:
            warnings.simplefilter("always")
            direct = {
                kind: science(native_call(kind)) for kind in ["complete", "partial", "failure"]
            }
            dormant = {kind: science(recorded_call(kind)) for kind in direct}
            assert direct == dormant
            observed.clear()
            with session:
                for name, kind in kinds:
                    try:
                        result = attempt(session, sink, root, name, kind, files, writer=writer)
                    except ConnectorError:
                        assert kind is None
                        continue
                    comparisons.append(science(result))
                    assert science(result) == direct[kind]
            warning_types = [type(w.message).__name__ for w in observed]
    finally:
        sink.detach()
    (root / "index.json").write_text(json.dumps(files, indent=2) + "\n")
    report = {
        "schema": "recorda-lab.sabueso-diagnostics/0.1",
        "filtered": filtered,
        "science": comparisons,
        "warning_types": warning_types,
        "answers": answers(root),
    }
    (root / "acceptance.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("destination", type=Path)
    parser.add_argument("--filtered", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run(args.destination, filtered=args.filtered)))
