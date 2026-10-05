"""Deterministic dummy library. No dependency on or instrumentation by Recorda."""

import hashlib
import json
import math
from dataclasses import dataclass

__version__ = "0.0.0"


@dataclass(frozen=True)
class Result:
    count: int
    mean: float
    variance: float

    def to_dict(self):
        return {
            "owner": "recorda-lab",
            "schema": "recorda-lab.result/0.1",
            "count": self.count,
            "mean": self.mean,
            "variance": self.variance,
        }

    @property
    def identifier(self):
        payload = json.dumps(self.to_dict(), sort_keys=True, allow_nan=False).encode()
        return "sha256:" + hashlib.sha256(payload).hexdigest()


def summarize(samples):
    """Compute a population mean and variance; retain the result's native identity."""
    if not samples:
        raise ValueError("at least one sample is required")
    if any(type(value) not in {int, float} for value in samples):
        raise TypeError("samples must be ordinary numbers")
    if any(not math.isfinite(value) for value in samples):
        raise ValueError("samples must be finite")
    mean = math.fsum(samples) / len(samples)
    variance = math.fsum((value - mean) ** 2 for value in samples) / len(samples)
    if not math.isfinite(mean) or not math.isfinite(variance):
        raise ValueError("result is outside the finite floating point range")
    return Result(len(samples), mean, variance)
