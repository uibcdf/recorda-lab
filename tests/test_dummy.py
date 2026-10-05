import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from recorda_lab import summarize


def test_dummy_result_is_deterministic_and_owns_its_native_record():
    result = summarize([1, 2, 3, 4])
    assert result.mean == 2.5
    assert result.variance == 1.25
    assert result.count == 4
    assert result.to_dict()["owner"] == "recorda-lab"
    assert result.identifier == summarize([1, 2, 3, 4]).identifier
    assert json.loads(json.dumps(result.to_dict())) == result.to_dict()


@pytest.mark.parametrize("samples", [[], [float("nan")], [float("inf")], ["not a number"]])
def test_invalid_samples_fail(samples):
    with pytest.raises((ValueError, TypeError)):
        summarize(samples)


def test_dummy_has_no_recorda_instrumentation():
    import recorda_lab

    # Prove the import boundary in a fresh process without replacing native classes
    # used by exact-type reference adapters in other integration tests.
    subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys, recorda_lab; recorda_lab.summarize([1, 2]); "
            "assert 'recorda' not in sys.modules",
        ],
        env=dict(os.environ, PYTHONPATH=str(Path(recorda_lab.__file__).resolve().parents[1])),
        check=True,
    )
