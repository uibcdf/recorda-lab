"""Independent native source/result and delivered-diagnostic oracles, Lab #15."""

import importlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("RECORDA_LAB_SABUESO_DIAGNOSTICS") != "1",
    reason="explicit native Sabueso diagnostic lane: RECORDA_LAB_SABUESO_DIAGNOSTICS=1",
)


@pytest.fixture
def trial(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "experiments"))
    return importlib.import_module("run_sabueso_diagnostics")


@pytest.fixture
def retained(trial, tmp_path):
    root = tmp_path / "native"
    return root, trial.run(root)


def test_native_meaning_is_independent_of_execution_and_warning_counts(retained, trial):
    root, report = retained
    rows = report["answers"]["attempts"]
    assert report["answers"]["execution"] == "failed"
    assert [r["execution"] for r in rows] == ["succeeded"] * 3 + ["failed", "succeeded"]
    assert len({r["operation_id"] for r in rows}) == 5
    assert [r["codes"] for r in rows] == [[], [trial.PARTIAL[1]], [trial.FAILED[1]], [], []]
    assert [
        r["native_source_outcomes"][0]["status"] for r in rows if r["native_source_outcomes"]
    ] == ["added", "partial", "error", "added"]
    assert report["warning_types"] == ["EnrichmentPartialWarning", "EnrichmentFailedWarning"]
    sequence = json.loads((trial.FIXTURES / "sabueso_uniprot/P60174.json").read_text())["sequence"][
        "value"
    ]
    assert all(
        r["entity_ref"] == "sabueso:protein:uniprot:P60174"
        and r["resolution"] == "resolved"
        and r["sequence"] == sequence
        for r in report["science"]
    )
    assert [r["fictional_structures"] for r in report["science"]] == [
        ["pdb:9LAB"],
        ["pdb:9LAB"],
        [],
        ["pdb:9LAB"],
    ]
    assert rows[1]["native_source_outcomes"][0]["missing"] == [
        "rcsb_polymer_instance_feature",
        "rcsb_ligand_neighbors",
    ]
    references = report["answers"]["reference_report"]["references"]
    assert len(references) == 19 and all(r["status"] == "matched" for r in references)
    trace = json.loads((root / "partial-acquisition.json").read_text())
    assert all(r["network_attempts"] == 0 for r in trace["records"])
    card = json.loads((root / "partial-card.json").read_text())
    assert "quantities" in card  # Native sealed representation stays owned by Sabueso/PUW.
    bundle = json.loads((root / "partial-bundle.json").read_text())
    (event,) = bundle["events"]
    assert (event["source"], event["code"]) == trial.PARTIAL
    assert event["extra"]["recorda_operation_id"] == rows[1]["operation_id"]
    assert "message" in event and "context" not in event
    association = json.loads((root / "partial-association.json").read_text())
    assert "message" not in association["operations"][0]["entries"][0]


def test_filtered_native_warning_leaves_native_partial_outcome(trial, tmp_path):
    report = trial.run(tmp_path / "filtered", filtered=True)
    assert all(row["codes"] == [] for row in report["answers"]["attempts"])
    assert report["warning_types"] == ["EnrichmentPartialWarning", "EnrichmentFailedWarning"]
    assert report["answers"]["attempts"][1]["native_source_outcomes"][0]["status"] == "partial"
    assert report["answers"]["attempts"][2]["native_source_outcomes"][0]["status"] == "error"
    assert all(
        "suppressed events unknown" in row["coverage"]["meaning"]
        for row in report["answers"]["attempts"]
    )


@pytest.mark.parametrize("artifact", ["partial-card.json", "partial-association.json"])
@pytest.mark.parametrize("defect", ["missing", "changed"])
def test_artifact_loss_keeps_execution_and_separate_available_evidence(retained, artifact, defect):
    from inspect_sabueso_diagnostics import answers

    root, original = retained
    path = root / artifact
    data = path.read_bytes()
    if defect == "missing":
        path.unlink()
    else:
        path.write_bytes(b"{}")
    report = answers(root)
    row = report["attempts"][1]
    assert row["execution"] == "succeeded" and report["execution"] == "failed"
    if artifact.endswith("card.json"):
        assert row["native_source_outcomes"] is None and row["codes"] == ["SABUESO-W-ENRICH-003"]
    else:
        assert row["codes"] is None and row["native_source_outcomes"][0]["status"] == "partial"
    assert any(
        r["status"] == ("missing" if defect == "missing" else "mismatched")
        for r in report["reference_report"]["references"]
    )
    path.write_bytes(data)
    assert answers(root) == original["answers"]


def test_reader_needs_no_scientific_producers(retained, reader_packages, tmp_path):
    root, report = retained
    experiments = Path(__file__).resolve().parents[1] / "experiments"
    code = """import sys,importlib.util,json
sys.path[:0]=sys.argv[2:4]
assert all(importlib.util.find_spec(name) is None for name in ('sabueso','pyunitwizard','ackredit','numpy'))
from inspect_sabueso_diagnostics import answers
assert 'run_sabueso_diagnostics' not in sys.modules
print(json.dumps(answers(sys.argv[1])))
"""
    child = subprocess.run(
        [sys.executable, "-I", "-S", "-c", code, str(root), str(reader_packages), str(experiments)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    assert json.loads(child.stdout) == report["answers"]


@pytest.mark.parametrize("failed", [False, True])
def test_exact_native_result_or_error_with_retention_fault(trial, tmp_path, monkeypatch, failed):
    result = error = None
    # Observe the unchanged public producer's actual result/error before Recorda closes.
    if not failed:
        native = trial.native_call

        def observed(kind):
            nonlocal result
            result = native(kind)
            return result

        monkeypatch.setattr(trial, "native_call", observed)
    else:
        native = trial.get_entry

        def observed(*args, **kwargs):
            nonlocal error
            try:
                return native(*args, **kwargs)
            except trial.ConnectorError as caught:
                error = caught
                raise

        monkeypatch.setattr(trial, "get_entry", observed)

    def broken(*args):
        raise OSError("fixture writer fault")

    sink = trial.SabuesoDiagnostics()
    sink.attach(trial.configure_application())
    root = tmp_path / "artifacts"
    root.mkdir()
    try:
        with (
            trial.offline(),
            trial.recorda.session("identity", path=tmp_path / "record.jsonl") as session,
        ):
            if failed:
                with pytest.raises(trial.ConnectorError) as caught:
                    trial.attempt(session, sink, root, "failure", None, [], writer=broken)
                assert caught.value is error
            else:
                assert (
                    trial.attempt(session, sink, root, "success", "complete", [], writer=broken)
                    is result
                )
        assert sink.snapshot(session.id)["operations"][0]["coverage"]["gaps"] == ["artifact_fault"]
    finally:
        sink.detach()


def test_native_warning_as_error_is_not_swallowed(trial, tmp_path):
    import warnings

    from sabueso._private.smonitor.warnings import EnrichmentPartialWarning

    sink = trial.SabuesoDiagnostics()
    sink.attach(trial.configure_application())
    root = tmp_path / "artifacts"
    root.mkdir()
    try:
        with trial.offline(), warnings.catch_warnings():
            warnings.simplefilter("error", EnrichmentPartialWarning)
            with trial.recorda.session("warning-error", path=tmp_path / "record.jsonl") as session:
                with pytest.raises(EnrichmentPartialWarning):
                    trial.attempt(session, sink, root, "partial", "partial", [])
        record = trial.recorda.inspect(tmp_path / "record.jsonl")
        assert record.operations[0]["status"] == "failed"
    finally:
        sink.detach()


def test_hard_exit_during_native_diagnostic_leaves_incomplete_work(tmp_path):
    experiments = Path(__file__).resolve().parents[1] / "experiments"
    code = """import sys,os
sys.path.insert(0,sys.argv[2])
import run_sabueso_diagnostics as trial
class ExitAtPartial:
 name='controlled_exit'
 def handle(self,event,**kwargs):
  if event.get('code')==trial.PARTIAL[1]:os._exit(23)
manager=trial.configure_application()
manager.add_handler(ExitAtPartial())
sink=trial.SabuesoDiagnostics();sink.attach(manager)
with trial.offline(),trial.recorda.session('interrupted-native',path=sys.argv[1]) as session:
 with session.operation('sabueso.resolve_protein_card') as operation,sink.boundary(session,operation):
  trial.native_call('partial')
"""
    journal = tmp_path / "interrupted.jsonl"
    child = subprocess.run(
        [sys.executable, "-c", code, str(journal), str(experiments)], capture_output=True, text=True
    )
    assert child.returncode == 23, child.stderr
    import recorda

    record = recorda.inspect(journal)
    assert record.status == "incomplete" and record.operations[0]["status"] == "incomplete"
    assert record.operations[0]["outputs"] == {}
