"""Controlled preparation → SciPy fit → residual evaluation with retained references."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import recorda
from inspect_workflow import inspect_workflow, scalar_oracle
from scipy.optimize import curve_fit
from scipy_consumer import recorded_curve_fit
from workflow_consumer import (
    WorkflowArtifacts,
    affine,
    evaluate_fit,
    prepare_samples,
    recorded_evaluate,
    recorded_prepare,
)


def inputs():
    return np.arange(-3, 4, dtype=np.float64), np.array(
        [-8.1, -5.8, -3.0, -0.6, 1.9, 4.2, np.nan], dtype=np.float64
    )


def setup(destination):
    destination = Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    store = WorkflowArtifacts(destination / "native")
    x, y = inputs()
    store.register_input("raw-x", x)
    store.register_input("raw-y", y)
    p0 = np.array([1.0, 0.0], dtype=np.float64)
    store.register_input("initial-parameters", p0)
    return destination, store, x, y, p0


def write_index(store):
    (store.destination / "index.json").write_text(
        json.dumps({"schema": "recorda-lab.workflow-files/0.1", "files": store.files}, indent=2)
        + "\n"
    )


def execute_stages(x, y, p0, *, observed=True):
    prepare = recorded_prepare if observed else prepare_samples
    fit = recorded_curve_fit if observed else curve_fit
    evaluate = recorded_evaluate if observed else evaluate_fit
    prepared = prepare(x, y)
    fitted = fit(affine, prepared.x, prepared.y, p0=p0, method="lm", maxfev=1000)
    return prepared, fitted, evaluate(prepared, fitted)


def run_scenario(destination, mode="full"):
    if mode not in {"full", "retry", "minimal", "interrupted"}:
        raise ValueError("unknown controlled scenario")
    destination, store, x, y, p0 = setup(destination)
    original_x, original_y = x.copy(), y.copy()
    direct = execute_stages(x, y, p0, observed=False)
    dormant = execute_stages(x, y, p0)
    policy = None
    if mode == "minimal":
        policy = recorda.CapturePolicy(
            inputs=False, parameters=False, outputs=False, exception_references=False
        )
    handle = recorda.start(
        "multi-step fitting",
        path=destination / "workflow.jsonl",
        reference_adapters=store.adapters,
        capture_policy=policy,
        gaps=["undeclared helpers; external work; source bytes retained by the caller"],
    )
    failure = None
    try:
        with handle.operation("lab.affine_workflow", profile="scientific_workflow"):
            prepared = recorded_prepare(x, y)
            if mode == "interrupted":
                write_index(store)
                with handle.operation(
                    "scipy.optimize.curve_fit",
                    inputs={"xdata": prepared.x, "ydata": prepared.y},
                    implementation={"package": "scipy", "callable": "scipy.optimize.curve_fit"},
                    profile="parameter_estimation",
                ):
                    os._exit(23)
            if mode == "retry":
                try:
                    recorded_curve_fit(affine, prepared.x, prepared.y, p0=p0, method="lm", maxfev=1)
                except RuntimeError as error:
                    failure = error
                else:
                    raise AssertionError("controlled optimizer attempt must actually fail")
            fitted = recorded_curve_fit(
                affine, prepared.x, prepared.y, p0=p0, method="lm", maxfev=1000
            )
            evaluation = recorded_evaluate(prepared, fitted)
    finally:
        record = handle.stop()
        write_index(store)
    oracle = scalar_oracle(x.tolist(), y.tolist())
    assert np.array_equal(x, original_x, equal_nan=True)
    assert np.array_equal(y, original_y, equal_nan=True)
    for result in (direct, dormant, (prepared, fitted, evaluation)):
        assert result[0].kept_rows == tuple(oracle["kept_rows"])
        np.testing.assert_allclose(result[1][0], oracle["parameters"], rtol=1e-7, atol=1e-8)
        np.testing.assert_allclose(result[2].rss, oracle["rss"], rtol=1e-7, atol=1e-8)
    assert record.status == ("failed" if failure else "succeeded")
    return inspect_workflow(destination)


def run(destination):
    destination = Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    reports = {
        mode: run_scenario(destination / mode, mode) for mode in ("full", "retry", "minimal")
    }
    child = subprocess.run(
        [sys.executable, __file__, str(destination / "interrupted"), "--interrupt"],
        check=False,
    )
    assert child.returncode == 23
    reports["interrupted"] = inspect_workflow(destination / "interrupted")
    intact = reports["full"]
    intermediate = next((destination / "full/native").glob("prepared-*-y.npy"))
    original = intermediate.read_bytes()
    intermediate.unlink()
    try:
        reports["missing_intermediate"] = inspect_workflow(destination / "full")
    finally:
        intermediate.write_bytes(original)
    intermediate.write_bytes(original + b"changed")
    try:
        reports["modified_intermediate"] = inspect_workflow(destination / "full")
    finally:
        intermediate.write_bytes(original)
    reports["restored"] = inspect_workflow(destination / "full")
    assert reports["full"]["scientific_check"]["status"] == "consistent"
    assert reports["retry"]["scientific_check"]["status"] == "consistent"
    assert reports["minimal"]["dependency_links"] == []
    assert reports["minimal"]["scientific_check"]["status"] == "unavailable"
    assert reports["interrupted"]["session_status"] == "incomplete"
    assert reports["restored"] == intact
    report = {"schema": "recorda-lab.workflow-acceptance/0.1", "reports": reports}
    (destination / "acceptance.json").write_text(
        json.dumps(report, indent=2, allow_nan=False) + "\n"
    )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--interrupt", action="store_true", help="disposable child only")
    args = parser.parse_args()
    print(
        json.dumps(
            run_scenario(args.destination, "interrupted")
            if args.interrupt
            else run(args.destination),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
