import importlib.util
import json
import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("RECORDA_LAB_NOTEBOOK") != "1",
    reason="real kernel lane is explicit: RECORDA_LAB_NOTEBOOK=1 with Jupyter test dependencies",
)


def test_real_kernel_cells_failures_interruptions_and_loss(tmp_path):
    # An explicitly selected lane must fail if its declared dependencies are missing.
    experiments = Path(__file__).resolve().parents[1] / "experiments"
    spec = importlib.util.spec_from_file_location("lab_notebook", experiments / "run_notebook.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    destination = tmp_path / "notebook"
    report = module.run(destination)
    assert report["scenarios"] == {
        "cross-cell": "succeeded",
        "failure": "failed",
        "interrupt": "failed",
        "kernel-loss": "incomplete",
    }
    assert json.loads((destination / "acceptance.json").read_text()) == report
    import nbformat

    notebook = nbformat.read(destination / "executed.ipynb", as_version=4)
    nbformat.validate(notebook)
    assert len(notebook.cells) == 14
    assert (
        notebook.cells[-1].metadata["recorda_lab"]["outcome"] == "kernel_terminated_without_reply"
    )
    with pytest.raises(FileExistsError):
        module.run(destination)


def test_committed_usage_notebooks_execute_all_cells(tmp_path, monkeypatch):
    experiments = Path(__file__).resolve().parents[1] / "experiments"
    monkeypatch.syspath_prepend(str(experiments))
    spec = importlib.util.spec_from_file_location("lab_examples", experiments / "run_examples.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    report = module.run(tmp_path / "examples")
    expected = {
        "01_manual_activation.ipynb": 9,
        "02_recording_cost.ipynb": 4,
        "05_capture_selection.ipynb": 8,
        "06_reference_checks.ipynb": 11,
    }
    if os.environ.get("RECORDA_LAB_SCIPY") == "1":
        expected["03_scipy_fit.ipynb"] = 8
        expected["07_multi_step_workflow.ipynb"] = 9
    else:
        assert "03_scipy_fit.ipynb" in report["skipped"]
        assert "07_multi_step_workflow.ipynb" in report["skipped"]
    if os.environ.get("RECORDA_LAB_SABUESO") == "1":
        expected["04_sabueso_resolution.ipynb"] = 8
    else:
        assert "04_sabueso_resolution.ipynb" in report["skipped"]
    assert {
        name: value["code_cells_passed"] for name, value in report["notebooks"].items()
    } == expected
    for value in report["notebooks"].values():
        assert (tmp_path / "examples" / value["executed_notebook"]).exists()
