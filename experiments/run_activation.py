"""Activate once, call decorated consumers normally, stop and inspect the record."""

import argparse
import json
import os
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

import recorda
from consumer import (
    REFERENCE_ADAPTERS,
    analyze,
    echo,
    sample_count,
    samples_reference,
    summarize_samples,
)

import recorda_lab


def run(destination):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    samples = [1, 2, 3, 4]
    (destination / "samples.json").write_text(json.dumps(samples))
    (destination / "empty-samples.json").write_text(json.dumps([]))
    expected_result = recorda_lab.summarize(samples)

    # Ordinary calls before activation do not create a recording or change results.
    assert summarize_samples(samples) == expected_result
    assert sample_count(samples) == 4
    assert not list(destination.glob("*.jsonl"))

    recorda.start(
        "success",
        path=destination / "success.jsonl",
        reference_adapters=REFERENCE_ADAPTERS,
        gaps=["unwrapped dummy calls", "native file persistence outside decorated functions"],
    )
    try:
        result = summarize_samples(samples)
        count = sample_count(samples)
    finally:
        success = recorda.stop()
    assert result == expected_result and count == 4
    native = json.dumps(result.to_dict(), sort_keys=True, allow_nan=False)
    (destination / "native-result.json").write_text(native)
    assert success.status == "succeeded"
    assert len(success.operations) == 2
    summary, counted = success.operations
    assert summary["profile"] == "scientific_analysis"
    assert summary["inputs"]["samples"]["identifier"] == samples_reference(samples).identifier
    assert summary["outputs"]["return"]["identifier"] == result.identifier
    assert counted["outputs"]["return"] == 4

    recorda.start(
        "failure", path=destination / "failure.jsonl", reference_adapters=REFERENCE_ADAPTERS
    )
    failed = False
    try:
        summarize_samples([])
    except ValueError as error:
        assert str(error) == "at least one sample is required"
        failed = True
    finally:
        failure = recorda.stop()
    assert failed and failure.status == "failed"

    child_script = """
import sys, recorda
sys.path.insert(0, sys.argv[2])
from consumer import interrupt
recorda.start('interruption', path=sys.argv[1])
interrupt()
"""
    package_paths = [
        str(Path(recorda.__file__).resolve().parents[1]),
        str(Path(recorda_lab.__file__).resolve().parents[1]),
    ]
    env = dict(os.environ, PYTHONPATH=os.pathsep.join(package_paths))
    child = subprocess.run(
        [
            sys.executable,
            "-c",
            child_script,
            str(destination / "interruption.jsonl"),
            str(Path(__file__).resolve().parent),
        ],
        env=env,
        check=False,
    )
    assert child.returncode == 23

    handle = recorda.start(
        "nested", path=destination / "nested.jsonl", reference_adapters=REFERENCE_ADAPTERS
    )
    try:
        nested_result = analyze(samples)
    finally:
        nested = handle.stop()
    assert nested_result == result
    parent, child = nested.operations
    assert parent["parent_id"] is None and child["parent_id"] == parent["id"]
    assert parent["outputs"]["return"]["identifier"] == result.identifier
    assert child["outputs"]["return"]["identifier"] == result.identifier

    sentinel = object()
    recorda.start("omissions", path=destination / "omissions.jsonl")
    try:
        assert echo(sentinel, api_key="never-store") is sentinel
    finally:
        omissions = recorda.stop()
    safe_inputs = omissions.operations[0]["inputs"]
    assert safe_inputs["api_key"]["reason"] == "sensitive_name"
    assert safe_inputs["value"]["reason"] == "unsupported_type"
    assert "never-store" not in (destination / "omissions.jsonl").read_text()

    # After stopping, the same consumers continue to behave as ordinary functions.
    assert summarize_samples(samples) == result
    assert echo(sentinel) is sentinel
    assert len(recorda.inspect(destination / "success.jsonl").operations) == 2
    expected = {
        "success": "succeeded",
        "failure": "failed",
        "interruption": "incomplete",
        "nested": "succeeded",
        "omissions": "succeeded",
    }
    records = {}
    for name, status in expected.items():
        inspected = recorda.inspect(destination / f"{name}.jsonl")
        assert inspected.status == status
        records[name] = asdict(inspected)
    assert records["interruption"]["operations"][0]["status"] == "incomplete"
    report = {
        "schema": "recorda-lab.activation/0.1",
        "activation": "manual start/stop with decorated consumer functions",
        "recorda_version": recorda.__version__,
        "dummy_version": recorda_lab.__version__,
        "scenarios": expected,
        "scientific_result": result.to_dict(),
        "inactive_calls": "normal before start and after stop",
        "coverage": "declared decorated boundaries only; dummy internals remain unobserved",
        "records": records,
        "native_files": [
            {"file": "samples.json", "reference": asdict(samples_reference(samples))},
            {"file": "empty-samples.json", "reference": asdict(samples_reference([]))},
            {"file": "native-result.json", "owner": "recorda-lab", "identifier": result.identifier},
        ],
    }
    (destination / "acceptance.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path, help="new directory for inspectable artifacts")
    report = run(parser.parse_args().destination)
    print(json.dumps(report["scenarios"], indent=2))


if __name__ == "__main__":
    main()
