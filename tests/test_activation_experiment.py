import importlib.util
import json
from pathlib import Path

import pytest


def test_manual_activation_preserves_native_result_and_checked_artifacts(tmp_path, monkeypatch):
    experiments = Path(__file__).resolve().parents[1] / "experiments"
    monkeypatch.syspath_prepend(str(experiments))
    spec = importlib.util.spec_from_file_location(
        "lab_activation", experiments / "run_activation.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    destination = tmp_path / "activation"
    report = module.run(destination)
    assert report["scenarios"] == {
        "success": "succeeded",
        "failure": "failed",
        "interruption": "incomplete",
        "nested": "succeeded",
        "omissions": "succeeded",
    }
    assert json.loads((destination / "native-result.json").read_text()) == {
        "owner": "recorda-lab",
        "schema": "recorda-lab.result/0.1",
        "count": 4,
        "mean": 2.5,
        "variance": 1.25,
    }
    assert json.loads((destination / "acceptance.json").read_text()) == report
    with pytest.raises(FileExistsError):
        module.run(destination)
