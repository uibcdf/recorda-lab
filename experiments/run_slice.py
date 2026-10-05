"""Run independent acceptance scenarios against an installed Recorda checkout."""

import argparse
import hashlib
import json
import os
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

import recorda

from recorda_lab import __version__, summarize


def run(destination):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    samples = [1, 2, 3, 4]
    fixture = json.dumps(samples).encode()
    (destination / "samples.json").write_bytes(fixture)
    input_ref = recorda.Reference(
        owner="recorda-lab", identifier="samples:four", digest=hashlib.sha256(fixture).hexdigest()
    )
    implementation = {
        "package": "recorda-lab",
        "callable": "recorda_lab.summarize",
        "version": __version__,
    }
    with recorda.session(
        "success", path=destination / "success.jsonl", gaps=["unwrapped dummy calls"]
    ) as session:
        with session.operation(
            "recorda_lab.summarize",
            inputs={"samples": input_ref},
            implementation=implementation,
        ) as operation:
            result = summarize(samples)
            native = json.dumps(result.to_dict(), sort_keys=True, allow_nan=False).encode()
            (destination / "native-result.json").write_bytes(native)
            operation.output(
                "result",
                recorda.Reference(owner="recorda-lab", identifier=result.identifier),
            )
    assert result.mean == 2.5 and result.variance == 1.25
    assert json.loads((destination / "native-result.json").read_text()) == result.to_dict()

    failed = False
    try:
        with recorda.session("failure", path=destination / "failure.jsonl") as session:
            with session.operation("recorda_lab.summarize", implementation=implementation):
                summarize([])
    except ValueError as error:
        assert str(error) == "at least one sample is required"
        failed = True
    assert failed

    child_script = """
import os, sys, recorda
with recorda.session('interruption', path=sys.argv[1]) as session:
    with session.operation('dummy.interrupted'):
        os._exit(23)
"""
    # Source experiments and installed-package experiments both work in a fresh child.
    env = dict(os.environ, PYTHONPATH=str(Path(recorda.__file__).resolve().parents[1]))
    child = subprocess.run(
        [sys.executable, "-c", child_script, str(destination / "interruption.jsonl")],
        env=env,
        check=False,
    )
    assert child.returncode == 23

    @recorda.record("lab.instrumented_summary")
    def instrumented_summary(values):
        return summarize(values)

    assert instrumented_summary(samples) == result
    with recorda.session("nested", path=destination / "nested.jsonl") as session:
        with session.operation("lab.workflow"):
            assert instrumented_summary(samples) == result
    with recorda.session("omissions", path=destination / "omissions.jsonl") as session:
        with session.operation("dummy.safe", inputs={"api_key": "never-store", "opaque": object()}):
            pass

    expected = {
        "success": "succeeded",
        "failure": "failed",
        "interruption": "incomplete",
        "nested": "succeeded",
        "omissions": "succeeded",
    }
    records = {}
    for name, status in expected.items():
        record = recorda.inspect(destination / f"{name}.jsonl")
        assert record.status == status
        records[name] = asdict(record)
    parent, child = records["nested"]["operations"]
    assert child["parent_id"] == parent["id"]
    assert child["outputs"]["return"]["reason"] == "unsupported_type"
    assert (
        records["success"]["operations"][0]["outputs"]["result"]["identifier"] == result.identifier
    )
    assert records["success"]["coverage"]["known_gaps"] == ["unwrapped dummy calls"]
    safe = records["omissions"]["operations"][0]["inputs"]
    assert safe["api_key"]["reason"] == "sensitive_name"
    assert safe["opaque"]["reason"] == "unsupported_type"
    assert "never-store" not in (destination / "omissions.jsonl").read_text()
    assert "sensitive scientific" not in (destination / "failure.jsonl").read_text()
    report = {
        "schema": "recorda-lab.acceptance/0.1",
        "recorda_version": recorda.__version__,
        "dummy_version": __version__,
        "scenarios": expected,
        "inactive_call": "normal behavior, no recording session",
        "coverage": "declared boundaries only; dummy internals and unwrapped calls are unobserved",
        "records": records,
        "native_files": [
            {"file": "samples.json", "reference": asdict(input_ref)},
            {"file": "native-result.json", "owner": "recorda-lab", "identifier": result.identifier},
        ],
    }
    (destination / "acceptance.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path, help="new directory for experiment artifacts")
    args = parser.parse_args()
    report = run(args.destination)
    print(json.dumps(report["scenarios"], indent=2))


if __name__ == "__main__":
    main()
