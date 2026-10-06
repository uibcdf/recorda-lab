import importlib
import json
import os
import subprocess
import sys
from functools import wraps
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("RECORDA_LAB_SABUESO") != "1",
    reason="explicit offline Sabueso lane: RECORDA_LAB_SABUESO=1",
)


def load_trial(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "experiments"))
    return importlib.import_module("run_sabueso")


def test_scientific_decisions_lineage_and_offline_receipts(tmp_path, monkeypatch):
    trial = load_trial(monkeypatch)
    import socket

    def forbidden(*args, **kwargs):
        raise AssertionError("this trial must not connect to a source")

    monkeypatch.setattr(socket.socket, "connect", forbidden)
    destination = tmp_path / "trial"
    report = trial.run(destination)
    operations = report["operations"]
    assert report["status"] == "failed"
    assert report["network_attempts"] == 0
    assert operations[0]["source"] == "UniProt"
    assert operations[0]["query"] == {"accession": "P60174"}
    assert operations[0]["retrieved_at"] == "2026-09-23"
    assert operations[2]["parent_id"] == operations[1]["operation_id"]
    assert operations[3]["semantic_status"] == "ambiguous"
    assert operations[4]["entity_ref"] == "sabueso:protein:uniprot:P60174"
    assert operations[4]["alternatives"][0]["entity_ref"] == "sabueso:protein:uniprot:P60175"
    assert operations[5]["execution_status"] == "succeeded"
    assert operations[5]["semantic_status"] == "error"
    assert operations[6]["execution_status"] == "failed"
    assert operations[2]["card_reference"]["owner"] == "sabueso"
    assert json.loads((destination / "acceptance.json").read_text()) == report
    with pytest.raises(FileExistsError):
        trial.run(destination)


def test_native_return_and_exception_identity(tmp_path, monkeypatch):
    trial = load_trial(monkeypatch)
    observed = []

    @wraps(trial.native_get_entry)
    def caller(*args, **kwargs):
        try:
            result = trial.native_get_entry(*args, **kwargs)
        except Exception as error:
            observed.append(error)
            raise
        observed.append(result)
        return result

    decorated = trial.recorda.record("sabueso.uniprot.get_entry")(caller)
    artifacts = trial.SabuesoArtifacts(tmp_path / "native")
    handle = trial.recorda.start(
        "identity", path=tmp_path / "session.jsonl", reference_adapters=artifacts.adapters
    )
    try:
        result = decorated("P60174", client=trial.fixture_client())
        assert result is observed[-1]
        with pytest.raises(trial.ConnectorError) as raised:
            decorated("P12345", client=trial.fixture_client(failing=True))
        assert raised.value is observed[-1]
        assert raised.value.acquisition_trace["records"][-1]["network_attempts"] == 0
    finally:
        record = handle.stop()
    assert [op["status"] for op in record.operations] == ["succeeded", "failed"]


def test_reader_without_producer_and_visible_artifact_loss(tmp_path, monkeypatch):
    trial = load_trial(monkeypatch)
    import recorda

    destination = tmp_path / "trial"
    trial.run(destination)
    reader = Path(trial.__file__).parent
    code = """import importlib.util, json, sys
from inspect_sabueso_trial import inspect_trial
assert all(importlib.util.find_spec(name) is None for name in ('sabueso','ackredit','pyunitwizard'))
report = inspect_trial(sys.argv[1])
print(json.dumps({'status': report['status'], 'semantic_statuses': report['semantic_statuses']}))
"""
    env = {
        **os.environ,
        "PYTHONPATH": os.pathsep.join([str(Path(recorda.__file__).parents[1]), str(reader)]),
    }
    result = subprocess.run(
        [sys.executable, "-S", "-c", code, str(destination)],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    assert json.loads(result.stdout)["semantic_statuses"] == [
        "resolved",
        "resolved",
        "ambiguous",
        "resolved",
        "error",
    ]
    index = json.loads((destination / "native/index.json").read_text())
    file = destination / "native" / index["files"][0]["path"]
    original = file.read_bytes()
    file.write_bytes(original + b"changed")
    with pytest.raises(ValueError, match="no longer matches"):
        trial.inspect_trial(destination)
    file.write_bytes(original)
    file.unlink()
    with pytest.raises(ValueError, match="missing"):
        trial.inspect_trial(destination)


def test_unknown_inputs_and_mutated_native_snapshot_are_omitted(tmp_path, monkeypatch):
    trial = load_trial(monkeypatch)
    artifacts = trial.SabuesoArtifacts(tmp_path / "native")
    assert isinstance(artifacts.envelope({"api_key": "do-not-store"}), trial.recorda.Omitted)

    class Opaque:
        def __repr__(self):
            raise AssertionError("opaque repr must not be inspected")

    @trial.recorda.record("lab.opaque")
    def echo(value):
        return value

    handle = trial.recorda.start(
        "safe", path=tmp_path / "session.jsonl", reference_adapters=artifacts.adapters
    )
    try:
        opaque = Opaque()
        assert echo(opaque) is opaque
        result = trial.sabueso.resolve(
            "P60174", resolver=trial.EntityResolver(trial.fixture_client())
        )
        reference = artifacts.result(result)
        assert isinstance(reference, trial.recorda.Reference)
        result[1].status = "ambiguous"
        assert isinstance(artifacts.result(result), trial.recorda.Omitted)
    finally:
        record = handle.stop()
    assert record.operations[0]["outputs"]["return"]["kind"] == "omitted"
    assert "do-not-store" not in "".join(
        p.read_text() for p in artifacts.destination.glob("*.json")
    )
