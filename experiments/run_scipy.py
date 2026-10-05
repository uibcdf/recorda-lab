"""Fit a controlled scientific dataset with unmodified SciPy and inspect useful provenance."""

import argparse
import json
import os
import subprocess
import sys
from importlib.metadata import version
from pathlib import Path

import numpy as np
import recorda
from inspect_scipy_trial import inspect_trial
from scipy.optimize import curve_fit
from scipy_consumer import FitArtifacts, affine, recorded_curve_fit


def run(destination):
    destination = Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    artifacts = FitArtifacts(destination / "native")
    xdata = np.linspace(-2.0, 3.0, 11, dtype=np.float64)
    noise = np.array(
        [-0.1, 0.08, 0.04, -0.02, 0.06, -0.07, 0.03, -0.01, 0.09, -0.06, 0.01], dtype=np.float64
    )
    ydata = affine(xdata, 2.5, -0.7) + noise
    p0 = np.array([1.0, 0.0], dtype=np.float64)
    bounds = np.array([[-10.0, -10.0], [10.0, 10.0]], dtype=np.float64)
    unbounded = np.array([-np.inf, np.inf], dtype=np.float64)
    for name, value in {
        "xdata": xdata,
        "ydata": ydata,
        "p0": p0,
        "bounds": bounds,
        "unbounded": unbounded,
    }.items():
        artifacts.register_input(name, value)
    before = [value.copy() for value in [xdata, ydata, p0, bounds, unbounded]]
    original_callable = curve_fit
    direct = curve_fit(affine, xdata, ydata, p0=p0, bounds=unbounded, method="lm", maxfev=1000)
    inactive = recorded_curve_fit(
        affine, xdata, ydata, p0=p0, bounds=unbounded, method="lm", maxfev=1000
    )
    for raw, dormant in zip(direct, inactive, strict=True):
        np.testing.assert_array_equal(raw, dormant)
    assert not artifacts.results and not list(destination.glob("*.jsonl"))

    recorda.start(
        "fit_retry",
        path=destination / "retry.jsonl",
        reference_adapters=artifacts.adapters,
        gaps=["dataset generation, residual analysis and SciPy optimizer internals are unobserved"],
    )
    try:
        try:
            recorded_curve_fit(affine, xdata, ydata, p0=p0, bounds=unbounded, method="lm", maxfev=1)
        except RuntimeError:
            pass
        else:
            raise AssertionError("the limited real optimizer must fail")
        fitted = recorded_curve_fit(
            affine, xdata, ydata, p0=p0, bounds=unbounded, method="lm", maxfev=1000
        )
    finally:
        retry = recorda.stop()
    assert retry.status == "failed"
    assert [operation["status"] for operation in retry.operations] == ["failed", "succeeded"]
    assert retry.operations[0]["exception"]["type"] == "builtins.RuntimeError"
    assert artifacts.results[0][0] is fitted
    for raw, observed in zip(direct, fitted, strict=True):
        np.testing.assert_array_equal(raw, observed)

    recorda.start(
        "fit_comparison",
        path=destination / "comparison.jsonl",
        reference_adapters=artifacts.adapters,
    )
    try:
        alternative = recorded_curve_fit(
            affine,
            xdata,
            ydata,
            p0=p0,
            bounds=bounds,
            method="trf",
            max_nfev=1000,
        )
    finally:
        comparison = recorda.stop()
    assert comparison.status == "succeeded" and artifacts.results[1][0] is alternative
    oracle = np.linalg.lstsq(np.column_stack([xdata, np.ones_like(xdata)]), ydata, rcond=None)[0]
    for fit in [fitted, alternative]:
        np.testing.assert_allclose(fit[0], oracle, rtol=1e-7, atol=1e-7)
        assert fit[1].shape == (2, 2) and np.all(np.isfinite(fit[1]))
    for old, current in zip(before, [xdata, ydata, p0, bounds, unbounded], strict=True):
        np.testing.assert_array_equal(old, current)
    assert curve_fit is original_callable and recorded_curve_fit.__wrapped__ is curve_fit
    artifacts.write_index()
    audit = inspect_trial(destination)
    assert audit["records"]["retry"]["operations"][0]["solver_options"] == {"maxfev": 1}
    assert audit["records"]["retry"]["operations"][1]["solver_options"] == {"maxfev": 1000}
    for record in [retry, comparison]:
        for operation in record.operations:
            implementation = operation["implementation"]
            assert implementation["package"] == "scipy" and implementation["version"] == version(
                "scipy"
            )
            assert implementation["callable"].endswith(".curve_fit")
            assert operation["profile"] == "parameter_estimation"
    child_code = (
        "import sys; from inspect_scipy_trial import inspect_trial; "
        "inspect_trial(sys.argv[1]); assert 'numpy' not in sys.modules and 'scipy' not in sys.modules"
    )
    subprocess.run(
        [sys.executable, "-c", child_code, str(destination)],
        check=True,
        env=dict(
            os.environ,
            PYTHONPATH=os.pathsep.join(
                [
                    str(Path(recorda.__file__).resolve().parents[1]),
                    str(Path(__file__).resolve().parent),
                ]
            ),
        ),
    )
    residuals = ydata - affine(xdata, *fitted[0])
    report = {
        "schema": "recorda-lab.scipy/0.1",
        "tracking": ["uibcdf/recorda-lab#4", "uibcdf/recorda#1"],
        "environment": {
            "executable": sys.executable,
            "python": sys.version,
            "scipy": version("scipy"),
            "numpy": version("numpy"),
        },
        "data": "deterministic fictional dimensionless observations; no physical quantity encoding",
        "scientific_summary": {
            "parameters": fitted[0].tolist(),
            "covariance": fitted[1].tolist(),
            "least_squares_oracle": oracle.tolist(),
            "residual_sum_squares": float(residuals @ residuals),
        },
        "checks": [
            "native/dormant/recorded results agree; caller alias leaves SciPy untouched",
            "native result tuple identity and input arrays preserved",
            "failed attempt followed by successful retry; session retains failure",
            "alternate solver agrees with independent linear least-squares oracle",
            "model, inputs, initial guess, solver options, version and native outputs referenced",
            "trial receipts inspect independently without importing SciPy or NumPy",
        ],
        "audit": audit,
        "scope": "controlled real-library usability; not arbitrary calls, broad adapter support or replay",
    }
    (destination / "acceptance.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path, help="fresh directory for trial artifacts")
    print(json.dumps(run(parser.parse_args().destination)["scientific_summary"], indent=2))


if __name__ == "__main__":
    main()
