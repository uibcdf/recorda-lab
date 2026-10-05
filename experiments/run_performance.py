"""Measure direct, dormant and durable recorded calls without changing recording policy."""

import argparse
import gc
import hashlib
import json
import platform
import statistics
import sys
import time
from pathlib import Path

import recorda
from consumer import REFERENCE_ADAPTERS, sample_count, summarize_samples

import recorda_lab

MODES = ("direct", "inactive", "active_omissions", "active_references")


def _measure(function, samples, iterations):
    cpu_start = time.process_time_ns()
    wall_start = time.perf_counter_ns()
    result = None
    for _ in range(iterations):
        result = function(samples)
    wall = time.perf_counter_ns() - wall_start
    cpu = time.process_time_ns() - cpu_start
    return result, wall, cpu


def run(destination, *, repetitions=7, baseline_iterations=3000, active_iterations=30, size=10000):
    for value in (repetitions, baseline_iterations, active_iterations, size):
        if type(value) is not int or value < 1:
            raise ValueError("measurement counts and sample size must be positive integers")
    destination = Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    workloads = {
        "count_small": (sample_count, [1, 2, 3, 4], baseline_iterations),
        "summary_small": (summarize_samples, [1, 2, 3, 4], baseline_iterations),
        "summary_large": (
            summarize_samples,
            [float(index % 101) for index in range(size)],
            max(1, baseline_iterations // 50),
        ),
    }
    rows, summaries = [], {}
    for name, (decorated, samples, baseline_count) in workloads.items():
        direct = decorated.__wrapped__
        expected = direct(samples)
        (destination / f"{name}-samples.json").write_text(json.dumps(samples))
        (destination / f"{name}-native-result.json").write_text(
            json.dumps(expected if type(expected) is int else expected.to_dict(), sort_keys=True)
        )
        for _ in range(5):
            assert direct(samples) == decorated(samples) == expected
        for repetition in range(repetitions):
            # Rotate order to reduce systematic bias from process warmup or storage load.
            order = MODES[repetition % 4 :] + MODES[: repetition % 4]
            for mode in order:
                recorded = mode.startswith("active_")
                iterations = active_iterations if recorded else baseline_count
                journal = destination / f"{name}-{mode}-{repetition}.jsonl"
                handle = None
                if recorded:
                    handle = recorda.start(
                        name,
                        path=journal,
                        reference_adapters=REFERENCE_ADAPTERS
                        if mode == "active_references"
                        else {},
                    )
                gc.collect()
                gc_was_enabled = gc.isenabled()
                gc.disable()
                try:
                    result, wall, cpu = _measure(
                        direct if mode == "direct" else decorated, samples, iterations
                    )
                finally:
                    if gc_was_enabled:
                        gc.enable()
                    if handle is not None:
                        inspected = handle.stop()
                assert result == expected
                row = {
                    "workload": name,
                    "mode": mode,
                    "repetition": repetition,
                    "iterations": iterations,
                    "wall_ns": wall,
                    "cpu_ns": cpu,
                    "wall_ns_per_call": wall / iterations,
                    "cpu_ns_per_call": cpu / iterations,
                }
                if recorded:
                    assert inspected.status == "succeeded" and not inspected.problems
                    assert len(inspected.operations) == iterations
                    for operation in inspected.operations:
                        assert operation["status"] == "succeeded"
                        captured = operation["outputs"]["return"]
                        if name == "count_small":
                            assert captured == expected
                        elif mode == "active_references":
                            assert captured["identifier"] == expected.identifier
                        else:
                            assert captured["reason"] == "unsupported_type"
                        assert operation["inputs"]["samples"]["kind"] == (
                            "reference" if mode == "active_references" else "omitted"
                        )
                    events = len(journal.read_bytes().splitlines())
                    assert events == 3 * iterations + 2
                    row.update(
                        journal=journal.name,
                        journal_bytes=journal.stat().st_size,
                        events=events,
                        fsync_calls=events,
                        timed_fsync_calls=3 * iterations,
                        journal_sha256=hashlib.sha256(journal.read_bytes()).hexdigest(),
                    )
                rows.append(row)
        medians = {}
        for mode in MODES:
            selected = [row for row in rows if row["workload"] == name and row["mode"] == mode]
            wall_values = [row["wall_ns_per_call"] for row in selected]
            medians[mode] = {
                "median_wall_ns_per_call": statistics.median(wall_values),
                "min_wall_ns_per_call": min(wall_values),
                "max_wall_ns_per_call": max(wall_values),
                "median_cpu_ns_per_call": statistics.median(
                    row["cpu_ns_per_call"] for row in selected
                ),
            }
        baseline = medians["direct"]["median_wall_ns_per_call"]
        for mode, result in medians.items():
            result["ratio_to_direct"] = result["median_wall_ns_per_call"] / baseline
            result["added_wall_ns_per_call"] = result["median_wall_ns_per_call"] - baseline
        summaries[name] = {
            "sample_count": len(samples),
            "modes": medians,
            "samples_file": f"{name}-samples.json",
            "native_result_file": f"{name}-native-result.json",
        }
    report = {
        "schema": "recorda-lab.performance/0.1",
        "tracking": ["uibcdf/recorda-lab#2", "uibcdf/recorda#1"],
        "environment": {
            "executable": sys.executable,
            "python": sys.version,
            "platform": platform.platform(),
            "storage_directory": str(destination),
            "recorda_file": recorda.__file__,
            "dummy_file": recorda_lab.__file__,
        },
        "settings": {
            "repetitions": repetitions,
            "baseline_iterations": baseline_iterations,
            "active_iterations": active_iterations,
            "large_sample_count": size,
        },
        "method": {
            "clock": "perf_counter_ns wall time and process_time_ns CPU time",
            "order": "rotating four modes each repetition; five untimed native/dormant warmup calls",
            "excluded": "session start, stop/inspection, GC collection and result verification",
            "gc": "disabled only during timed loops; restored afterwards",
            "persistence": "production synchronous fsync per event, unchanged; three timed events per call",
            "reference_cost": "input list JSON/hash and native-result identity included in active_references",
            "fsync_counts": "inferred from persisted event count and unchanged writer, not syscall tracing",
            "scope": "local dummy workload on this filesystem; no timing threshold or universal guarantee",
        },
        "summaries": summaries,
        "observations": rows,
    }
    (destination / "measurements.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path, help="fresh directory for measurements/journals")
    parser.add_argument("--repetitions", type=int, default=7)
    parser.add_argument("--baseline-iterations", type=int, default=3000)
    parser.add_argument("--active-iterations", type=int, default=30)
    parser.add_argument("--size", type=int, default=10000)
    args = parser.parse_args()
    report = run(
        args.destination,
        repetitions=args.repetitions,
        baseline_iterations=args.baseline_iterations,
        active_iterations=args.active_iterations,
        size=args.size,
    )
    print(json.dumps(report["summaries"], indent=2))


if __name__ == "__main__":
    main()
