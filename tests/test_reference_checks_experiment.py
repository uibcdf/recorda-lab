import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


def test_controlled_loss_modification_omission_and_incomplete_are_inspectable(
    tmp_path, monkeypatch, reader_packages
):
    experiments = Path(__file__).resolve().parents[1] / "experiments"
    monkeypatch.syspath_prepend(str(experiments))
    spec = importlib.util.spec_from_file_location(
        "reference_trial", experiments / "run_reference_checks.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    destination = tmp_path / "references"
    report = module.run(destination)
    assert report["scientific_result"] == {
        "owner": "recorda-lab",
        "schema": "recorda-lab.result/0.1",
        "count": 4,
        "mean": 2.5,
        "variance": 1.25,
    }
    for name, scenario in report["reports"].items():
        assert scenario["full"]["session_status"] == "succeeded"
        assert len(scenario["full"]["references"]) == 4
        assert scenario["interrupted"]["incomplete_operations"]
        assert {row["reason"] for row in scenario["minimal"]["omissions"]} == {"capture_policy"}
    assert json.loads((destination / "acceptance.json").read_text()) == report
    # Import neither the dummy nor scientific producers when inspecting saved receipts.
    code = """
import importlib.util, json, sys
sys.path.insert(0,sys.argv[1])
import recorda
from pathlib import Path
root=Path(sys.argv[2])
index=json.loads((root/'native/index.json').read_text())
files=recorda.LocalFileResolver(root/'native',{recorda.Reference(**e['reference']):e['path'] for e in index['files']},digest_algorithm=index.get('digest_algorithm'))
report=recorda.check_references(recorda.inspect(root/'full.jsonl'),resolver=files)
assert all(importlib.util.find_spec(name) is None for name in ('recorda_lab', 'numpy', 'scipy', 'sabueso', 'ackredit', 'pyunitwizard'))
assert all(row['status']=='matched' for row in report['references'])
print(json.dumps({'status':report['session_status'],'references':len(report['references'])}))
"""
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            "-S",
            "-c",
            code,
            str(reader_packages),
            str(destination),
        ],
        env={key: value for key, value in os.environ.items() if key != "PYTHONPATH"},
        capture_output=True,
        text=True,
        check=True,
    )
    assert json.loads(result.stdout) == {"status": "succeeded", "references": 4}
    with pytest.raises(FileExistsError):
        module.run(destination)
