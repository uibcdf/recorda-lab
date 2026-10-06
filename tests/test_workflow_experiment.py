import importlib.util
import json
import os
import subprocess
import sys
from functools import wraps
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("RECORDA_LAB_SCIPY") != "1",
    reason="multi-step scientific lane requires RECORDA_LAB_SCIPY=1 and SciPy/NumPy",
)


def load_trial(monkeypatch):
    experiments = Path(__file__).resolve().parents[1] / "experiments"
    monkeypatch.syspath_prepend(str(experiments))
    spec = importlib.util.spec_from_file_location("lab_workflow", experiments / "run_workflow.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_multi_step_oracle_dependencies_retry_and_file_loss(tmp_path, monkeypatch):
    trial = load_trial(monkeypatch)
    destination = tmp_path / "workflow"
    result = trial.run(destination)
    reports = result["reports"]
    full = reports["full"]
    oracle = full["scientific_check"]["oracle"]
    assert oracle["kept_rows"] == [0, 1, 2, 3, 4, 5]
    assert oracle["parameters"] == pytest.approx([87 / 35, -23 / 35])
    assert oracle["rss"] == pytest.approx(1 / 14)
    assert full["session_status"] == "succeeded"
    names = {op["id"]: op["name"] for op in full["operations"]}
    assert {
        (names[e["producer"]], names[e["consumer"]], e["input"]) for e in full["dependency_links"]
    } == {
        ("lab.prepare_finite_samples", "scipy.optimize.curve_fit", "xdata"),
        ("lab.prepare_finite_samples", "scipy.optimize.curve_fit", "ydata"),
        ("lab.prepare_finite_samples", "lab.evaluate_residuals", "samples"),
        ("scipy.optimize.curve_fit", "lab.evaluate_residuals", "fit"),
    }
    assert {r["status"] for r in full["native_file_checks"]} == {"matched"}
    retry = reports["retry"]
    assert retry["session_status"] == "failed"
    assert [
        op["status"] for op in retry["operations"] if op["name"] == "scipy.optimize.curve_fit"
    ] == ["failed", "succeeded"]
    assert retry["scientific_check"]["status"] == "consistent"
    minimal = reports["minimal"]
    assert minimal["session_status"] == "succeeded"
    assert minimal["dependency_links"] == []
    assert minimal["reference_checks"]["omissions"]
    assert minimal["scientific_check"]["status"] == "unavailable"
    interrupted = reports["interrupted"]
    assert interrupted["session_status"] == "incomplete"
    assert [op["status"] for op in interrupted["operations"]] == [
        "incomplete",
        "succeeded",
        "incomplete",
    ]
    assert len(interrupted["reference_checks"]["incomplete_operations"]) == 2
    for name, status in [
        ("missing_intermediate", "missing"),
        ("modified_intermediate", "mismatched"),
    ]:
        report = reports[name]
        assert report["session_status"] == "succeeded"
        assert status in {row["status"] for row in report["native_file_checks"]}
        assert report["scientific_check"]["status"] == "unavailable"
    assert reports["restored"] == full
    assert json.loads((destination / "acceptance.json").read_text()) == result
    with pytest.raises(FileExistsError):
        trial.run(destination)


def test_reader_uses_recorda_and_stdlib_without_producers(tmp_path, monkeypatch):
    trial = load_trial(monkeypatch)
    destination = tmp_path / "workflow"
    trial.run_scenario(destination)
    code = """
import json, sys
sys.path[:0] = sys.argv[1:3]
from inspect_workflow import inspect_workflow
report = inspect_workflow(sys.argv[3])
assert report['scientific_check']['status'] == 'consistent'
assert not {'numpy', 'scipy', 'recorda_lab'} & set(sys.modules)
print(json.dumps(report))
"""
    child = subprocess.run(
        [
            sys.executable,
            "-I",
            "-S",
            "-c",
            code,
            str(Path(trial.__file__).parent),
            str(Path(trial.recorda.__file__).parents[1]),
            str(destination),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert json.loads(child.stdout)["session_status"] == "succeeded"


def test_scientific_inconsistency_is_visible_even_when_receipts_match(tmp_path, monkeypatch):
    import hashlib

    trial = load_trial(monkeypatch)
    destination = tmp_path / "workflow"
    trial.run_scenario(destination)
    evaluation = next((destination / "native").glob("evaluation-*.json"))
    data = json.loads(evaluation.read_text())
    data["rss"] = 1.0  # Still valid JSON and a safe scalar, but scientifically wrong.
    evaluation.write_text(json.dumps(data, sort_keys=True))
    index_path = destination / "native/index.json"
    index = json.loads(index_path.read_text())
    entry = next(row for row in index["files"] if row["path"] == evaluation.name)
    old_reference = dict(entry["reference"])
    digest = hashlib.sha256(evaluation.read_bytes()).hexdigest()
    entry["reference"].update(digest=digest, identifier=f"sha256:{digest}")
    index_path.write_text(json.dumps(index))
    journal = destination / "workflow.jsonl"
    events = [json.loads(line) for line in journal.read_text().splitlines()]
    for event in events:
        value = event.get("value")
        if type(value) is dict and value.get("identifier") == old_reference["identifier"]:
            event["value"] = {"kind": "reference", **entry["reference"]}
    journal.write_text("".join(json.dumps(event) + "\n" for event in events))
    report = trial.inspect_workflow(destination)
    assert {r["status"] for r in report["native_file_checks"]} == {"matched"}
    assert report["session_status"] == "succeeded"
    assert report["scientific_check"]["status"] == "inconsistent"


def test_native_fit_and_error_identity_are_preserved_in_the_workflow(tmp_path, monkeypatch):
    trial = load_trial(monkeypatch)
    observed = []

    @wraps(trial.curve_fit)
    def tracked(*args, **kwargs):
        try:
            result = trial.curve_fit(*args, **kwargs)
        except Exception as error:
            observed.append(error)
            raise
        observed.append(result)
        return result

    boundary = trial.recorda.record("scipy.optimize.curve_fit")(tracked)
    _, store, x, y, p0 = trial.setup(tmp_path / "identity")
    prepared = trial.prepare_samples(x, y)
    handle = trial.recorda.start(
        "native identity", path=tmp_path / "identity.jsonl", reference_adapters=store.adapters
    )
    try:
        with pytest.raises(RuntimeError) as raised:
            boundary(trial.affine, prepared.x, prepared.y, p0=p0, method="lm", maxfev=1)
        assert raised.value is observed[-1]
        fit = boundary(trial.affine, prepared.x, prepared.y, p0=p0, method="lm", maxfev=1000)
        assert fit is observed[-1]
        reference = store.fit_reference(fit)
        assert store.fit_reference(fit) == reference
        fit[0][0] += 1
        assert isinstance(store.fit_reference(fit), trial.recorda.Omitted)
    finally:
        report = handle.stop()
    assert report.status == "failed"
