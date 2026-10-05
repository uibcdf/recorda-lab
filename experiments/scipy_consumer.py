"""Caller-owned instrumentation and narrow artifact adapters for a SciPy fitting trial."""

import hashlib
import inspect
import json
import math
import re
from dataclasses import asdict
from importlib.metadata import version
from pathlib import Path
from types import FunctionType

import numpy as np
import recorda
from scipy.optimize import curve_fit


def affine(x, slope, intercept):
    """The laboratory's dimensionless two-parameter model."""
    return slope * x + intercept


# This alias leaves SciPy's module and callable untouched. There is no recording
# statement inside the model or the external library's scientific function body.
recorded_curve_fit = recorda.record("scipy.optimize.curve_fit", profile="parameter_estimation")(
    curve_fit
)


class FitArtifacts:
    """Known fictional inputs and the two-array output of this specific fit contract."""

    def __init__(self, destination):
        self.destination = Path(destination)
        self.destination.mkdir(parents=True, exist_ok=False)
        self.files = []
        self.inputs = {}
        self.results = []
        self.model = self._save_bytes("affine.py", inspect.getsource(affine).encode())

    def _register_file(self, path):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        reference = recorda.Reference(
            owner="recorda-lab", identifier=f"sha256:{digest}", digest=digest
        )
        self.files.append({"path": path.name, "reference": asdict(reference)})
        return reference

    def _save_bytes(self, name, data):
        path = self.destination / name
        if path.exists():
            assert path.read_bytes() == data
            return recorda.Reference(
                **next(item["reference"] for item in self.files if item["path"] == name)
            )
        with path.open("xb") as stream:
            stream.write(data)
        return self._register_file(path)

    def _save_json(self, prefix, value):
        data = json.dumps(value, sort_keys=True, allow_nan=False).encode()
        name = f"{prefix}-{hashlib.sha256(data).hexdigest()[:16]}.json"
        return self._save_bytes(name, data)

    def _save_array(self, name, value):
        if type(value) is not np.ndarray or value.dtype != np.dtype("float64"):
            raise TypeError("this experiment persists only ordinary float64 arrays")
        path = self.destination / f"{name}.npy"
        with path.open("xb") as stream:
            np.save(stream, value, allow_pickle=False)
        return self._register_file(path)

    def register_input(self, name, value):
        if not re.fullmatch(r"[a-z][a-z0-9_-]{0,63}", name):
            raise ValueError("input artifact requires a simple laboratory label")
        reference = self._save_array(name, value)
        self.inputs[id(value)] = (
            value,
            reference,
            (value.shape, value.dtype.str, value.tobytes()),
        )
        return reference

    def array_reference(self, value):
        entry = self.inputs.get(id(value))
        if entry is None or entry[0] is not value:
            return recorda.Omitted()
        if (value.shape, value.dtype.str, value.tobytes()) != entry[2]:
            return recorda.Omitted()
        return entry[1]

    def model_reference(self, value):
        return self.model if value is affine else recorda.Omitted()

    def solver_reference(self, value):
        permitted = {"maxfev", "max_nfev", "ftol", "gtol", "xtol"}
        if not value.keys() <= permitted or any(
            type(item) not in {int, float} or not math.isfinite(item) or item <= 0
            for item in value.values()
        ):
            return recorda.Omitted()
        return self._save_json("solver", value)

    def fit_reference(self, value):
        # full_output=True and arbitrary tuples deliberately remain unsupported.
        if len(value) != 2 or any(type(item) is not np.ndarray for item in value):
            return recorda.Omitted()
        parameters, covariance = value
        if parameters.shape != (2,) or covariance.shape != (2, 2):
            return recorda.Omitted()
        index = len(self.results)
        parameter_ref = self._save_array(f"fit-{index}-parameters", parameters)
        covariance_ref = self._save_array(f"fit-{index}-covariance", covariance)
        reference = self._save_json(
            "fit",
            {
                "producer": {
                    "package": "scipy",
                    "version": version("scipy"),
                    "callable": "scipy.optimize.curve_fit",
                },
                "representation": "native NumPy arrays; lab-owned artifact manifest",
                "parameters": asdict(parameter_ref),
                "covariance": asdict(covariance_ref),
            },
        )
        self.results.append((value, reference))
        return reference

    @property
    def adapters(self):
        return {
            np.ndarray: self.array_reference,
            FunctionType: self.model_reference,
            dict: self.solver_reference,
            tuple: self.fit_reference,
        }

    def write_index(self):
        (self.destination / "index.json").write_text(
            json.dumps({"schema": "recorda-lab.scipy-artifacts/0.1", "files": self.files}, indent=2)
            + "\n"
        )
