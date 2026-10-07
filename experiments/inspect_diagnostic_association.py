"""Read controlled association artifacts without importing scientific/diagnostic producers."""

import json
from pathlib import Path

import recorda


def answers(destination):
    root = Path(destination)
    record = recorda.inspect(root / "record.jsonl")
    index_path = root / "index.json"
    if index_path.stat().st_size > 1024 * 1024:
        raise ValueError("trial index byte budget exceeded")
    entries = json.loads(index_path.read_text())
    if type(entries) is not list or len(entries) > 128:
        raise ValueError("invalid trial reference index")
    references = {recorda.Reference(**item["reference"]): item["path"] for item in entries}
    resolver = recorda.LocalFileResolver(root, references, digest_algorithm="sha256")
    report = recorda.check_references(record, resolver=resolver, max_bytes=1024 * 1024)
    rows = []
    for operation in record.operations:
        row = {
            "operation_id": operation["id"],
            "execution": operation["status"],
            "diagnostics": "unavailable",
            "codes": None,
            "coverage": None,
        }
        value = operation["outputs"].get("association")
        if type(value) is dict and value.get("kind") == "reference":
            reference = recorda.Reference(
                **{k: value.get(k) for k in ("owner", "identifier", "revision", "digest")}
            )
            if (
                recorda.check_reference(reference, resolver=resolver, max_bytes=1024 * 1024)[
                    "status"
                ]
                == "matched"
            ):
                payload = json.loads((root / references[reference]).read_text())
                items = payload.get("operations")
                if (
                    payload.get("schema") != "recorda-lab.diagnostic-association/0.1"
                    or payload.get("owner") != "recorda-lab-consumer"
                    or payload.get("session_id") != record.session_id
                    or type(items) is not list
                    or len(items) != 1
                    or items[0].get("operation_id") != operation["id"]
                    or items[0].get("parent_id") != operation["parent_id"]
                ):
                    raise ValueError("association artifact belongs to another operation")
                item = items[0]
                if type(item.get("entries")) is not list or len(item["entries"]) > 256:
                    raise ValueError("invalid selected diagnostic entries")
                row.update(
                    diagnostics="available",
                    codes=[e["code"] for e in item["entries"]],
                    coverage=item["coverage"],
                )
        rows.append(row)
    return {"execution": record.status, "attempts": rows, "reference_report": report}
