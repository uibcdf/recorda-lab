"""Producer-free projection of already observed Lab reference reports."""

from pathlib import Path

import recorda


def reference_views(destination, reports):
    """Read named snapshots and present saved phase observations, without rechecking."""
    destination = Path(destination)
    records = {
        name: recorda.inspect(destination / f"{name}.jsonl")
        for name in ("full", "minimal", "limits", "interrupted")
    }
    return {
        phase: {
            name: recorda.inspection_view(records[name], reference_report=report)
            for name, report in observations.items()
        }
        for phase, observations in reports.items()
    }


def workflow_views(destination, reports):
    """Present declared workflow references beside the separate scientific oracle."""
    destination = Path(destination)
    return {
        name: recorda.inspection_view(
            recorda.inspect(
                destination
                / (name if name in {"full", "retry", "minimal", "interrupted"} else "full")
                / "workflow.jsonl"
            ),
            reference_report=report["reference_checks"],
        )
        for name, report in reports.items()
    }
