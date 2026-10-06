import importlib.util
import json
import os
from functools import wraps
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("RECORDA_LAB_SCIPY") != "1",
    reason="real scientific lane is explicit: RECORDA_LAB_SCIPY=1 with SciPy/NumPy dependencies",
)


def load_trial(monkeypatch):
    experiments = Path(__file__).resolve().parents[1] / "experiments"
    monkeypatch.syspath_prepend(str(experiments))
    spec = importlib.util.spec_from_file_location("lab_scipy", experiments / "run_scipy.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_fit_retry_preserves_native_results_and_inspectable_configuration(tmp_path, monkeypatch):
    trial = load_trial(monkeypatch)
    destination = tmp_path / "scientific"
    report = trial.run(destination)
    assert report["audit"]["records"]["retry"]["status"] == "failed"
    assert report["audit"]["records"]["comparison"]["status"] == "succeeded"
    operations = report["audit"]["records"]["retry"]["operations"]
    assert operations[0]["input_references"] == operations[1]["input_references"]
    assert operations[0]["result_reference"] is None
    assert operations[1]["result_reference"]["kind"] == "reference"
    for record in report["audit"]["records"].values():
        assert record["reference_checks"]["references"]
        assert all(row["status"] == "matched" for row in record["reference_checks"]["references"])
    assert json.loads((destination / "acceptance.json").read_text()) == report
    with pytest.raises(FileExistsError):
        trial.run(destination)


def test_real_scipy_return_and_exception_objects_are_preserved(tmp_path, monkeypatch):
    trial = load_trial(monkeypatch)
    np, recorda = trial.np, trial.recorda
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

    decorated = recorda.record("scipy.optimize.curve_fit")(tracked)
    recorda.start("identity", path=tmp_path / "identity.jsonl")
    try:
        xdata = np.arange(5, dtype=np.float64)
        result = decorated(trial.affine, xdata, 2.5 * xdata - 0.7, method="lm")
        assert result is observed[-1]
        with pytest.raises(ValueError) as raised:
            decorated(trial.affine, xdata, np.array([], dtype=np.float64), method="lm")
        assert raised.value is observed[-1]
    finally:
        inspected = recorda.stop()
    assert inspected.status == "failed"
    assert [item["status"] for item in inspected.operations] == ["succeeded", "failed"]


def test_narrow_adapters_do_not_expand_to_arbitrary_objects(tmp_path, monkeypatch):
    trial = load_trial(monkeypatch)
    from scipy_consumer import FitArtifacts

    np, recorda = trial.np, trial.recorda
    artifacts = FitArtifacts(tmp_path / "native")
    unknown = np.array([1.0, 2.0, 3.0])
    assert isinstance(artifacts.array_reference(unknown), recorda.Omitted)
    reference = artifacts.register_input("mutable", unknown)
    assert artifacts.array_reference(unknown) == reference
    unknown[0] += 1
    assert isinstance(artifacts.array_reference(unknown), recorda.Omitted)
    unknown[0] -= 1
    assert artifacts.array_reference(unknown) == reference
    assert isinstance(artifacts.solver_reference({"api_key": "do-not-store"}), recorda.Omitted)
    assert isinstance(artifacts.model_reference(lambda x: x), recorda.Omitted)
    recorda.start(
        "full_output", path=tmp_path / "full-output.jsonl", reference_adapters=artifacts.adapters
    )
    try:
        native = trial.recorded_curve_fit(
            trial.affine,
            unknown,
            2.5 * unknown - 0.7,
            method="lm",
            full_output=True,
        )
    finally:
        inspected = recorda.stop()
    assert len(native) == 5 and type(native[0]) is np.ndarray
    assert inspected.status == "succeeded" and not artifacts.results
    assert inspected.operations[0]["outputs"]["return"]["reason"] == "caller_omitted"
    assert "do-not-store" not in "".join(
        path.read_text() for path in artifacts.destination.glob("*.json")
    )


def test_native_file_loss_or_changes_are_visible_to_independent_inspection(tmp_path, monkeypatch):
    trial = load_trial(monkeypatch)
    from inspect_scipy_trial import inspect_trial

    destination = tmp_path / "scientific"
    trial.run(destination)
    path = destination / "native/xdata.npy"
    original = path.read_bytes()
    path.write_bytes(original + b"changed")
    with pytest.raises(ValueError, match="no longer matches"):
        inspect_trial(destination)
    path.write_bytes(original)
    path.unlink()
    with pytest.raises(ValueError, match="missing"):
        inspect_trial(destination)
