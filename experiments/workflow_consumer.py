"""Ordinary dimensionless calculations and caller-owned workflow instrumentation."""

from dataclasses import asdict, dataclass
from importlib.metadata import version

import numpy as np
import recorda
from scipy_consumer import FitArtifacts, affine


@dataclass(frozen=True)
class PreparedSamples:
    x: np.ndarray
    y: np.ndarray
    kept_rows: tuple[int, ...]


@dataclass(frozen=True)
class Evaluation:
    residuals: np.ndarray
    rss: float
    count: int


def prepare_samples(x, y):
    """Select finite paired observations, preserving input arrays."""
    if x.ndim != 1 or x.shape != y.shape:
        raise ValueError("paired one-dimensional observations required")
    mask = np.isfinite(x) & np.isfinite(y)
    if np.count_nonzero(mask) < 3:
        raise ValueError("at least three finite observations required")
    return PreparedSamples(x[mask], y[mask], tuple(int(i) for i in np.flatnonzero(mask)))


def evaluate_fit(samples, fit):
    """Evaluate native fitted parameters on the prepared observations."""
    parameters, _ = fit
    residuals = samples.y - affine(samples.x, *parameters)
    return Evaluation(residuals, float(np.dot(residuals, residuals)), len(residuals))


recorded_prepare = recorda.record("lab.prepare_finite_samples", profile="data_preparation")(
    prepare_samples
)
recorded_evaluate = recorda.record("lab.evaluate_residuals", profile="scientific_analysis")(
    evaluate_fit
)


class WorkflowArtifacts(FitArtifacts):
    """References to the exact retained native objects of this small trial only."""

    def __init__(self, destination):
        super().__init__(destination)
        self.native_objects = {}

    @staticmethod
    def _snapshot(value):
        if type(value) is PreparedSamples:
            return (
                value.x.tobytes(),
                value.y.tobytes(),
                value.kept_rows,
                value.x.shape,
                value.y.shape,
            )
        if type(value) is Evaluation:
            return (value.residuals.tobytes(), value.residuals.shape, value.rss, value.count)
        return tuple((item.shape, item.dtype.str, item.tobytes()) for item in value)

    def _remember(self, value, reference):
        self.native_objects[id(value)] = (value, reference, self._snapshot(value))
        return reference

    def _existing(self, value):
        entry = self.native_objects.get(id(value))
        if entry is None or entry[0] is not value:
            return None
        return entry[1] if self._snapshot(value) == entry[2] else recorda.Omitted()

    def prepared_reference(self, value):
        existing = self._existing(value)
        if existing is not None:
            return existing
        index = len(self.native_objects)
        x = self.register_input(f"prepared-{index}-x", value.x)
        y = self.register_input(f"prepared-{index}-y", value.y)
        reference = self._save_json(
            "prepared",
            {
                "schema": "recorda-lab.workflow-prepared/0.1",
                "x": asdict(x),
                "y": asdict(y),
                "kept_rows": value.kept_rows,
            },
        )
        return self._remember(value, reference)

    def fit_reference(self, value):
        if len(value) != 2 or any(type(item) is not np.ndarray for item in value):
            return recorda.Omitted()
        if value[0].shape != (2,) or value[1].shape != (2, 2):
            return recorda.Omitted()
        existing = self._existing(value)
        if existing is not None:
            return existing
        index = len(self.native_objects)
        parameters = self._save_array(f"fit-{index}-parameters", value[0])
        covariance = self._save_array(f"fit-{index}-covariance", value[1])
        reference = self._save_json(
            "fit",
            {
                "schema": "recorda-lab.workflow-fit/0.1",
                "parameters": asdict(parameters),
                "covariance": asdict(covariance),
                "producer": {"package": "scipy", "version": version("scipy")},
            },
        )
        return self._remember(value, reference)

    def evaluation_reference(self, value):
        existing = self._existing(value)
        if existing is not None:
            return existing
        residuals = self._save_array(f"residuals-{len(self.native_objects)}", value.residuals)
        reference = self._save_json(
            "evaluation",
            {
                "schema": "recorda-lab.workflow-evaluation/0.1",
                "residuals": asdict(residuals),
                "rss": value.rss,
                "count": value.count,
            },
        )
        return self._remember(value, reference)

    @property
    def adapters(self):
        return {
            **super().adapters,
            PreparedSamples: self.prepared_reference,
            Evaluation: self.evaluation_reference,
        }
