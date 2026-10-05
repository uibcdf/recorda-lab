import importlib.util
from pathlib import Path

import pytest


def test_all_acceptance_scenarios(tmp_path):
    path = Path(__file__).resolve().parents[1] / "experiments/run_slice.py"
    spec = importlib.util.spec_from_file_location("lab_slice", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    report = module.run(tmp_path / "artifacts")
    assert report["scenarios"]["interruption"] == "incomplete"
    assert (tmp_path / "artifacts/acceptance.json").exists()
    with pytest.raises(FileExistsError):
        module.run(tmp_path / "artifacts")
