"""Inspect this workflow's references and scientific oracle with Recorda and its required support closure."""

import argparse
import ast
import json
import math
import struct
from pathlib import Path

import recorda

REFERENCE_FIELDS = ("owner", "identifier", "revision", "digest")
NATIVE_CHILDREN = {
    "recorda-lab.workflow-prepared/0.1": ("x", "y"),
    "recorda-lab.workflow-fit/0.1": ("parameters", "covariance"),
    "recorda-lab.workflow-evaluation/0.1": ("residuals",),
}


def reference_key(value):
    return tuple(value.get(key) for key in REFERENCE_FIELDS)


def scalar_oracle(x, y):
    """Closed-form OLS, independent of NumPy and the SciPy optimizer."""
    rows = [
        i
        for i, (a, b) in enumerate(zip(x, y, strict=True))
        if math.isfinite(a) and math.isfinite(b)
    ]
    selected_x, selected_y = [x[i] for i in rows], [y[i] for i in rows]
    n = len(rows)
    sx, sy = math.fsum(selected_x), math.fsum(selected_y)
    denominator = n * math.fsum(a * a for a in selected_x) - sx * sx
    slope = (n * math.fsum(a * b for a, b in zip(selected_x, selected_y)) - sx * sy) / denominator
    intercept = (sy - slope * sx) / n
    residuals = [b - (slope * a + intercept) for a, b in zip(selected_x, selected_y)]
    rss = math.fsum(r * r for r in residuals)
    variance = rss / (n - 2)
    return {
        "kept_rows": rows,
        "parameters": [slope, intercept],
        "residuals": residuals,
        "rss": rss,
        "covariance": [
            variance * n / denominator,
            -variance * sx / denominator,
            -variance * sx / denominator,
            variance * math.fsum(a * a for a in selected_x) / denominator,
        ],
    }


def read_float64(path):
    """Trial-native NPY 1.0, C-order float64 only; no general array deserializer."""
    data = path.read_bytes()
    if len(data) < 10 or data[:8] != b"\x93NUMPY\x01\x00":
        raise ValueError("unsupported trial array format")
    offset = 10 + struct.unpack("<H", data[8:10])[0]
    header = ast.literal_eval(data[10:offset].decode("ascii"))
    shape = header["shape"]
    if (
        header["descr"] != "<f8"
        or header["fortran_order"] is not False
        or type(shape) is not tuple
        or not 1 <= len(shape) <= 2
        or any(type(n) is not int or not 0 < n <= 64 for n in shape)
    ):
        raise ValueError("unsupported trial array contract")
    count = math.prod(shape)
    if len(data) - offset != count * 8:
        raise ValueError("invalid trial array length")
    return shape, list(struct.unpack(f"<{count}d", data[offset:]))


def inspect_workflow(destination):
    destination = Path(destination)
    native = destination / "native"
    index = json.loads((native / "index.json").read_text())
    if index["schema"] != "recorda-lab.workflow-files/0.1":
        raise ValueError("unsupported workflow receipt")
    locations = {}
    for item in index["files"]:
        ref = recorda.Reference(**item["reference"])
        if ref in locations and locations[ref] != item["path"]:
            raise ValueError("ambiguous workflow receipt")
        locations[ref] = item["path"]
    files = recorda.LocalFileResolver(native, locations, digest_algorithm="sha256")
    observations = [
        recorda.check_reference(ref, resolver=files, max_bytes=65536) for ref in files.references
    ]
    states = {reference_key(row["reference"]): row["status"] for row in observations}

    def path_for(value):
        if states.get(reference_key(value)) != "matched":
            return None
        return files.path_for(value)

    def manifest(value):
        path = path_for(value)
        return json.loads(path.read_text()) if path is not None and path.suffix == ".json" else None

    def array(value):
        path = path_for(value)
        return read_float64(path) if path is not None else None

    record = recorda.inspect(destination / "workflow.jsonl")
    checks = recorda.check_references(record, resolver=files, max_bytes=65536)
    produced, edges = {}, []
    scientific = {"status": "unavailable", "reason": "required_references_not_recorded"}
    prepared = fitted = evaluated = None
    for op in record.operations:
        for field, value in op["inputs"].items():
            if type(value) is dict and value.get("kind") == "reference":
                producer = produced.get(reference_key(value))
                if producer is not None:
                    edges.append({"producer": producer, "consumer": op["id"], "input": field})
        value = op["outputs"].get("return")
        if type(value) is not dict or value.get("kind") != "reference":
            continue
        produced[reference_key(value)] = op["id"]
        item = manifest(value)
        if item is None:
            continue
        for field in NATIVE_CHILDREN.get(item.get("schema"), ()):
            produced[reference_key(item[field])] = op["id"]
        if op["name"] == "lab.prepare_finite_samples":
            prepared = (op, item)
        elif op["name"] == "scipy.optimize.curve_fit":
            fitted = (op, item)
        elif op["name"] == "lab.evaluate_residuals":
            evaluated = (op, item)

    if prepared and fitted and evaluated:
        source = prepared[0]["inputs"]
        required = [source.get("x"), source.get("y"), prepared[1].get("x"), prepared[1].get("y")]
        required += [fitted[1].get("parameters"), fitted[1].get("covariance")]
        required += [evaluated[1].get("residuals")]
        if any(type(value) is not dict or path_for(value) is None for value in required):
            scientific = {"status": "unavailable", "reason": "required_native_file_unavailable"}
        else:
            raw_x, raw_y, x, y, parameters, covariance, residuals = [array(v) for v in required]
            oracle = scalar_oracle(raw_x[1], raw_y[1])
            selected = oracle["kept_rows"]
            consistent = (
                raw_x[0] == raw_y[0]
                and x[0] == y[0] == residuals[0] == (len(selected),)
                and prepared[1]["kept_rows"] == selected
                and x[1] == [raw_x[1][i] for i in selected]
                and y[1] == [raw_y[1][i] for i in selected]
                and parameters[0] == (2,)
                and covariance[0] == (2, 2)
                and evaluated[1]["count"] == len(selected)
                and all(
                    math.isclose(a, b, rel_tol=1e-7, abs_tol=1e-8)
                    for a, b in zip(parameters[1], oracle["parameters"], strict=True)
                )
                and all(
                    math.isclose(a, b, rel_tol=1e-7, abs_tol=1e-8)
                    for a, b in zip(covariance[1], oracle["covariance"], strict=True)
                )
                and all(
                    math.isclose(a, b, rel_tol=1e-7, abs_tol=1e-8)
                    for a, b in zip(residuals[1], oracle["residuals"], strict=True)
                )
                and math.isclose(evaluated[1]["rss"], oracle["rss"], rel_tol=1e-7, abs_tol=1e-8)
            )
            # Check that actual recorded stage arguments consume the exact produced identities.
            consistent = consistent and all(
                reference_key(a) == reference_key(b)
                for a, b in [
                    (fitted[0]["inputs"]["xdata"], prepared[1]["x"]),
                    (fitted[0]["inputs"]["ydata"], prepared[1]["y"]),
                    (evaluated[0]["inputs"]["samples"], prepared[0]["outputs"]["return"]),
                    (evaluated[0]["inputs"]["fit"], fitted[0]["outputs"]["return"]),
                ]
            )
            scientific = {
                "status": "consistent" if consistent else "inconsistent",
                "oracle": oracle,
            }
    elif any(row["status"] != "matched" for row in observations):
        scientific = {"status": "unavailable", "reason": "required_native_file_unavailable"}
    return {
        "schema": "recorda-lab.workflow-inspection/0.1",
        "session_status": record.status,
        "operations": [
            {"id": op["id"], "name": op["name"], "status": op["status"]} for op in record.operations
        ],
        "dependency_links": edges,
        "reference_checks": checks,
        "native_file_checks": observations,
        "scientific_check": scientific,
        "scope": "trial-specific declared dependencies, local bytes and dimensionless OLS",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    print(json.dumps(inspect_workflow(parser.parse_args().destination), indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
