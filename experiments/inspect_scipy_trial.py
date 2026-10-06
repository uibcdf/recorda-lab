"""Inspect the trial's declared journal and artifact receipts using Recorda, its required support providers and stdlib."""

import argparse
import json
from pathlib import Path

import recorda
from reference_files import local_files


def inspect_trial(destination):
    destination = Path(destination).resolve()
    artifacts = destination / "native"
    index = json.loads((artifacts / "index.json").read_text())
    assert index["schema"] == "recorda-lab.scipy-artifacts/0.1"
    files = local_files(artifacts, index["files"])
    for reference in files.references:
        if reference.identifier != f"sha256:{reference.digest}":
            raise ValueError("native artifact identity does not match its receipt")

    def resolve(reference):
        path = files.path_for(reference)
        if (
            path is None
            or reference["owner"] != "recorda-lab"
            or reference["identifier"] != f"sha256:{reference['digest']}"
        ):
            raise ValueError("operation has an unresolved trial reference")
        return path

    records = {}
    for name in ["retry", "comparison"]:
        record = recorda.inspect(destination / f"{name}.jsonl")
        checked = []
        for operation in record.operations:
            for field in [*operation["inputs"].values(), *operation["outputs"].values()]:
                if type(field) is dict and field.get("kind") == "reference":
                    resolve(field)
            options = operation["inputs"]["kwargs"]
            solver = json.loads(resolve(options).read_text())
            result = operation["outputs"].get("return")
            if result is not None:
                manifest = json.loads(resolve(result).read_text())
                for key in ["parameters", "covariance"]:
                    resolve(manifest[key])
            checked.append(
                {
                    "operation_id": operation["id"],
                    "status": operation["status"],
                    "implementation": operation["implementation"],
                    "method": operation["inputs"]["method"],
                    "solver_options": solver,
                    "model_reference": operation["inputs"]["f"]["identifier"],
                    "input_references": {
                        key: operation["inputs"][key]["identifier"]
                        for key in ["xdata", "ydata", "p0", "bounds"]
                    },
                    "result_reference": operation["outputs"].get("return"),
                }
            )
        records[name] = {
            "status": record.status,
            "operations": checked,
            "reference_checks": recorda.check_references(record, resolver=files),
        }
    return {
        "schema": "recorda-lab.scipy-inspection/0.1",
        "records": records,
        "native_files_checked": len(index["files"]),
        "scope": "trial-specific receipts and declared boundaries, not Recorda verification/replay",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    print(json.dumps(inspect_trial(parser.parse_args().destination), indent=2))


if __name__ == "__main__":
    main()
