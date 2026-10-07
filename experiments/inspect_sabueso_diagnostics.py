"""Read retained native source outcomes beside diagnostics, without Sabueso."""

import json
from pathlib import Path

import recorda
from inspect_diagnostic_association import answers as diagnostic_answers


def answers(destination):
    root = Path(destination)
    report = diagnostic_answers(root)
    record = recorda.inspect(root / "record.jsonl")
    entries = json.loads((root / "index.json").read_text())
    files = {recorda.Reference(**item["reference"]): item["path"] for item in entries}
    resolver = recorda.LocalFileResolver(root, files, digest_algorithm="sha256")
    for row, operation in zip(report["attempts"], record.operations, strict=True):
        row["native_source_outcomes"] = None
        row["native_card"] = "unavailable"
        value = operation["outputs"].get("native_card")
        if type(value) is not dict or value.get("kind") != "reference":
            continue
        ref = recorda.Reference(
            **{k: value.get(k) for k in ["owner", "identifier", "revision", "digest"]}
        )
        if ref.owner != "sabueso":
            raise ValueError("native Card owner mismatch")
        if (
            recorda.check_reference(ref, resolver=resolver, max_bytes=1024 * 1024)["status"]
            != "matched"
        ):
            continue
        card = json.loads((root / files[ref]).read_text())
        # This is an explicit view of Sabueso's retained source records, not a new
        # quality score or completeness inference derived from warning counts.
        outcomes = card.get("quality", {}).get("enrichments")
        if type(outcomes) is not list or len(outcomes) > 16:
            raise ValueError("invalid controlled source outcomes")
        row["native_source_outcomes"] = [
            {
                key: item[key]
                for key in ["source", "structure", "status", "count", "missing"]
                if key in item
            }
            for item in outcomes
        ]
        row["native_card"] = "available"
    return report
