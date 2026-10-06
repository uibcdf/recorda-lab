"""Compare session selection using unchanged dummy consumers and fresh journals."""

import argparse
import hashlib
import json
import os
import time
from pathlib import Path
from unittest.mock import patch

import recorda
from consumer import REFERENCE_ADAPTERS, analyze, sample_count, summarize_samples

import recorda_lab

POLICIES = {
    "minimal": recorda.CapturePolicy(
        profiles=["scientific_workflow", "scientific_analysis"],
        inputs=False,
        parameters=False,
        outputs=False,
        exception_references=False,
    ),
    "detailed": recorda.CapturePolicy(),
}


def calculate(samples, inspections):
    result = analyze(samples)
    for _ in range(inspections):
        assert sample_count(samples) == len(samples)
    return result


def run(destination, *, repetitions=3, inspections=16):
    if type(repetitions) is not int or not 1 <= repetitions <= 100:
        raise ValueError("repetitions must be an integer between 1 and 100")
    if type(inspections) is not int or not 1 <= inspections <= 1000:
        raise ValueError("inspections must be an integer between 1 and 1000")
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    samples = [1, 2, 3, 4]
    expected = recorda_lab.summarize(samples)
    assert expected.mean == 2.5 and expected.variance == 1.25
    assert calculate(samples, inspections) == expected
    (destination / "samples.json").write_text(json.dumps(samples))
    (destination / "native-result.json").write_text(
        json.dumps(expected.to_dict(), sort_keys=True, allow_nan=False)
    )
    observations = []
    original_fsync = os.fsync
    for repetition in range(repetitions):
        for mode, policy in POLICIES.items():
            counters = {"fsync": 0, "adapters": 0}

            def fsync(fd):
                counters["fsync"] += 1
                return original_fsync(fd)

            def counted(adapter):
                def capture(value):
                    counters["adapters"] += 1
                    return adapter(value)

                return capture

            path = destination / f"{mode}-{repetition}.jsonl"
            wall_start, cpu_start = time.perf_counter_ns(), time.process_time_ns()
            with patch.object(os, "fsync", fsync):
                handle = recorda.start(
                    mode,
                    path=path,
                    capture_policy=policy,
                    reference_adapters={
                        kind: counted(adapter) for kind, adapter in REFERENCE_ADAPTERS.items()
                    },
                    gaps=["unwrapped dummy internals", "native files retained by trial"],
                )
                try:
                    result = calculate(samples, inspections)
                finally:
                    record = handle.stop()
            wall_ns, cpu_ns = (
                time.perf_counter_ns() - wall_start,
                time.process_time_ns() - cpu_start,
            )
            assert result == expected and record.status == "succeeded"
            assert samples == [1, 2, 3, 4]
            assert record.operations[1]["parent_id"] == record.operations[0]["id"]
            if mode == "minimal":
                assert len(record.operations) == 2 and counters["adapters"] == 0
                assert record.coverage["excluded_boundaries"]["by_profile"] == [
                    {"profile": "inspection", "calls": inspections}
                ]
                assert all(operation["outputs"] == {} for operation in record.operations)
            else:
                assert len(record.operations) == 2 + inspections
                assert counters["adapters"] == 4 + inspections
                for operation in record.operations[:2]:
                    assert operation["outputs"]["return"]["identifier"] == expected.identifier
            events = len(path.read_bytes().splitlines())
            assert counters["fsync"] == events
            observations.append(
                {
                    "mode": mode,
                    "repetition": repetition,
                    "journal": path.name,
                    "journal_bytes": path.stat().st_size,
                    "events": events,
                    "fsync_calls": counters["fsync"],
                    "adapter_calls": counters["adapters"],
                    "operations": len(record.operations),
                    "wall_ns": wall_ns,
                    "cpu_ns": cpu_ns,
                }
            )
    failures = {}
    for mode, policy in POLICIES.items():
        handle = recorda.start(
            mode,
            path=destination / f"{mode}-failure.jsonl",
            capture_policy=policy,
            reference_adapters=REFERENCE_ADAPTERS,
        )
        try:
            try:
                summarize_samples([])
            except ValueError as error:
                assert str(error) == "at least one sample is required"
            else:
                raise AssertionError("native dummy error was not raised")
        finally:
            failures[mode] = handle.stop().status
        assert failures[mode] == "failed"
    report = {
        "schema": "recorda-lab.selection/0.1",
        "observations": observations,
        "scientific_result": expected.to_dict(),
        "native_result_identifier": expected.identifier,
        "failures": failures,
        "policies": {name: policy.describe() for name, policy in POLICIES.items()},
        "scope": "Declared consumer boundaries only; timing includes start/calls/stop and inspection; no replay guarantee",
        "native_files": {
            name: hashlib.sha256((destination / name).read_bytes()).hexdigest()
            for name in ["samples.json", "native-result.json"]
        },
    }
    for repetition in range(repetitions):
        minimal, detailed = observations[2 * repetition : 2 * repetition + 2]
        assert minimal["journal_bytes"] < detailed["journal_bytes"]
        assert minimal["fsync_calls"] < detailed["fsync_calls"]
    (destination / "acceptance.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    print(json.dumps(run(parser.parse_args().destination), indent=2))


if __name__ == "__main__":
    main()
