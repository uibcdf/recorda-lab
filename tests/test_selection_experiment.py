import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import recorda


def test_same_native_calculation_has_checked_selection_and_measured_storage(tmp_path, monkeypatch):
    experiments = Path(__file__).resolve().parents[1] / "experiments"
    monkeypatch.syspath_prepend(str(experiments))
    spec = importlib.util.spec_from_file_location("lab_selection", experiments / "run_selection.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    destination = tmp_path / "selection"
    report = module.run(destination, repetitions=2, inspections=8)
    assert report["scientific_result"]["mean"] == 2.5
    assert report["scientific_result"]["variance"] == 1.25
    assert report["failures"] == {"minimal": "failed", "detailed": "failed"}
    assert len(report["observations"]) == 4
    for row in report["observations"]:
        assert row["wall_ns"] >= 0 and row["cpu_ns"] >= 0
        assert row["fsync_calls"] == row["events"] == (6 if row["mode"] == "minimal" else 32)
    # A producer-free interpreter can read coverage and selected native references.
    script = """
import json, sys
sys.path.insert(0,sys.argv[1])
import recorda
assert 'recorda_lab' not in sys.modules
minimal=recorda.inspect(sys.argv[2])
detailed=recorda.inspect(sys.argv[3])
assert len(minimal.operations)==2 and len(detailed.operations)==10
assert minimal.coverage['excluded_boundaries']['by_profile']==[{'profile':'inspection','calls':8}]
assert detailed.operations[0]['outputs']['return']['identifier']==sys.argv[4]
print(json.dumps({'minimal':minimal.status,'detailed':detailed.status}))
"""
    completed = subprocess.run(
        [
            sys.executable,
            "-S",
            "-c",
            script,
            str(Path(recorda.__file__).resolve().parents[1]),
            str(destination / "minimal-0.jsonl"),
            str(destination / "detailed-0.jsonl"),
            report["native_result_identifier"],
        ],
        env={key: value for key, value in os.environ.items() if key != "PYTHONPATH"},
        capture_output=True,
        text=True,
        check=True,
    )
    assert json.loads(completed.stdout) == {"minimal": "succeeded", "detailed": "succeeded"}
    assert json.loads((destination / "acceptance.json").read_text()) == report
    with pytest.raises(FileExistsError):
        module.run(destination)
    with pytest.raises(ValueError):
        module.run(tmp_path / "invalid", repetitions=0)
    assert not (tmp_path / "invalid").exists()
