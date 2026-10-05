import importlib.util
import json
from pathlib import Path

import pytest


def test_measurements_check_real_journals_without_timing_thresholds(tmp_path, monkeypatch):
    experiments = Path(__file__).resolve().parents[1] / "experiments"
    monkeypatch.syspath_prepend(str(experiments))
    spec = importlib.util.spec_from_file_location(
        "lab_performance", experiments / "run_performance.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    destination = tmp_path / "performance"
    report = module.run(
        destination, repetitions=2, baseline_iterations=10, active_iterations=2, size=100
    )
    assert len(report["observations"]) == 24
    assert set(report["summaries"]) == {"count_small", "summary_small", "summary_large"}
    assert len(list(destination.glob("*.jsonl"))) == 12
    for row in report["observations"]:
        assert row["wall_ns"] >= 0 and row["cpu_ns"] >= 0
        if row["mode"].startswith("active_"):
            assert row["events"] == row["fsync_calls"] == 8
            assert row["timed_fsync_calls"] == 6
    assert json.loads((destination / "measurements.json").read_text()) == report
    with pytest.raises(FileExistsError):
        module.run(destination)
    with pytest.raises(ValueError):
        module.run(tmp_path / "invalid", repetitions=0)
    assert not (tmp_path / "invalid").exists()
