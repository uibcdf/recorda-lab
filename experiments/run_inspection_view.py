"""Compare technical views with existing dummy/reference and optional SciPy trials."""

import argparse
import json
from pathlib import Path

import recorda
from inspection_examples import reference_views, workflow_views
from run_reference_checks import run as run_references


def run(destination, *, with_workflow=False):
    destination = Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    reference_root = destination / "references"
    source = run_references(reference_root)
    views = reference_views(reference_root, source["reports"])
    full = recorda.inspect(reference_root / "full.jsonl")
    unchecked = recorda.inspection_view(full)
    # Deliberately create a separate damaged-prefix fixture. The original
    # interrupted journal and native source/result bytes remain unchanged.
    tail_path = destination / "truncated.jsonl"
    tail_path.write_bytes((reference_root / "interrupted.jsonl").read_bytes() + b'{"unfinished')
    tail = recorda.inspect(tail_path)
    tail_view = recorda.inspection_view(tail, reference_report=recorda.check_references(tail))
    result = {
        "schema": "recorda-lab.inspection-view/0.1",
        "scientific_result": source["scientific_result"],
        "reference_views": views,
        "without_checking": unchecked,
        "truncated": tail_view,
        "scope": "Technical view of declared observations; scientific oracles stay separate",
    }
    if with_workflow:
        from run_workflow import run as run_workflow

        workflow_root = destination / "workflow"
        source_workflow = run_workflow(workflow_root)
        result["workflow"] = {
            "views": workflow_views(workflow_root, source_workflow["reports"]),
            "scientific_checks": {
                name: report["scientific_check"]
                for name, report in source_workflow["reports"].items()
            },
        }
    (destination / "acceptance.json").write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n"
    )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--workflow", action="store_true", help="include the explicit SciPy lane")
    args = parser.parse_args()
    print(json.dumps(run(args.destination, with_workflow=args.workflow), indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
