"""Controlled native-file availability and byte checking, with normal dummy calls."""

import argparse
import hashlib
import json
import os
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

import recorda
from consumer import analyze, samples_reference
from run_selection import POLICIES

import recorda_lab


def prepare(destination):
    destination = Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    native = destination / "native"
    native.mkdir()
    samples = [1, 2, 3, 4]
    expected = recorda_lab.summarize(samples)
    assert expected.mean == 2.5 and expected.variance == 1.25
    source = samples_reference(samples)
    source_path = native / "samples.json"
    source_path.write_text(json.dumps(samples))
    result_path = native / "result.json"
    result_path.write_text(json.dumps(expected.to_dict(), sort_keys=True, allow_nan=False))
    result_ref = recorda.Reference(
        owner="recorda-lab",
        identifier=expected.identifier,
        digest=hashlib.sha256(result_path.read_bytes()).hexdigest(),
    )
    unverified = recorda.Reference(owner="recorda-lab", identifier=expected.identifier)
    unknown = recorda.Reference(owner="recorda-lab", identifier="unknown-result")
    files = recorda.LocalFileResolver(
        native,
        {
            source: "samples.json",
            result_ref: "result.json",
            unverified: "result.json",
        },
        digest_algorithm="sha256",
    )

    def result_reference(result):
        if result != expected:
            return recorda.Omitted()
        return result_ref

    adapters = {list: samples_reference, recorda_lab.Result: result_reference}
    records = {}
    for name, policy in [("full", None), ("minimal", POLICIES["minimal"])]:
        handle = recorda.start(
            name,
            path=destination / f"{name}.jsonl",
            reference_adapters=adapters,
            capture_policy=policy,
        )
        try:
            result = analyze(samples)
        finally:
            records[name] = handle.stop()
        assert result == expected and records[name].status == "succeeded"
    handle = recorda.start("reference_limits", path=destination / "limits.jsonl")
    try:
        with handle.operation(
            "lab.reference_examples", inputs={"unverified": unverified, "unknown": unknown}
        ):
            pass
    finally:
        records["limits"] = handle.stop()
    script = """
import json, os, sys, recorda
source = recorda.Reference(**json.loads(sys.argv[2]))
handle = recorda.start('interrupted', path=sys.argv[1])
with handle.operation('lab.pending', inputs={'samples':source}):
    os._exit(23)
"""
    child = subprocess.run(
        [
            sys.executable,
            "-c",
            script,
            str(destination / "interrupted.jsonl"),
            json.dumps(asdict(source)),
        ],
        cwd=destination,
        env={**os.environ, "PYTHONPATH": str(Path(recorda.__file__).resolve().parents[1])},
        check=False,
    )
    assert child.returncode == 23
    records["interrupted"] = recorda.inspect(destination / "interrupted.jsonl")
    index = {
        "schema": "recorda-lab.local-references/0.1",
        "digest_algorithm": "sha256",
        "files": [
            {"reference": asdict(ref), "path": files.path_for(ref).name} for ref in files.references
        ],
    }
    (native / "index.json").write_text(json.dumps(index, indent=2) + "\n")
    return {
        "destination": destination,
        "files": files,
        "records": records,
        "scientific_result": expected.to_dict(),
    }


def inspect_trial(destination):
    """Read journals and an explicit index with Recorda, its required support providers and stdlib."""
    destination = Path(destination)
    native = destination / "native"
    index = json.loads((native / "index.json").read_text())
    assert index["schema"] == "recorda-lab.local-references/0.1"
    locations = {}
    for entry in index["files"]:
        ref = recorda.Reference(**entry["reference"])
        if ref in locations and locations[ref] != entry["path"]:
            raise ValueError("duplicate local reference")
        locations[ref] = entry["path"]
    files = recorda.LocalFileResolver(
        native, locations, digest_algorithm=index.get("digest_algorithm")
    )
    return {
        name: recorda.check_references(
            recorda.inspect(destination / f"{name}.jsonl"), resolver=files
        )
        for name in ["full", "minimal", "limits", "interrupted"]
    }


def run(destination):
    trial = prepare(destination)
    destination = trial["destination"]
    source, result = destination / "native/samples.json", destination / "native/result.json"
    source_bytes, result_bytes = source.read_bytes(), result.read_bytes()
    reports = {"intact": inspect_trial(destination)}
    source.unlink()
    try:
        reports["missing_input"] = inspect_trial(destination)
    finally:
        source.write_bytes(source_bytes)
    result.write_bytes(result_bytes + b"\n")
    try:
        reports["modified_output"] = inspect_trial(destination)
    finally:
        result.write_bytes(result_bytes)
    reports["restored"] = inspect_trial(destination)
    assert {row["status"] for row in reports["intact"]["full"]["references"]} == {"matched"}
    assert {row["status"] for row in reports["missing_input"]["full"]["references"]} == {
        "matched",
        "missing",
    }
    assert {row["status"] for row in reports["modified_output"]["full"]["references"]} == {
        "matched",
        "mismatched",
    }
    assert {row["status"] for row in reports["restored"]["full"]["references"]} == {"matched"}
    assert reports["intact"]["minimal"]["references"] == []
    assert len(reports["intact"]["minimal"]["omissions"]) == 6
    assert {row["status"] for row in reports["intact"]["limits"]["references"]} == {
        "available_unverified",
        "unresolved",
    }
    assert reports["intact"]["interrupted"]["session_status"] == "incomplete"
    report = {
        "schema": "recorda-lab.reference-checks/0.1",
        "scientific_result": trial["scientific_result"],
        "reports": reports,
        "scope": "Local reference bytes and availability; no semantic identity, authenticity or replay certification",
    }
    (destination / "acceptance.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    report = run(parser.parse_args().destination)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
