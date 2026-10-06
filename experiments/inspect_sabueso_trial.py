"""Read the trial's native receipts using Recorda and its required support closure, without Sabueso."""

import argparse
import json
from pathlib import Path

import recorda
from reference_files import local_files


def _key(reference):
    return (
        reference["owner"],
        reference["identifier"],
        reference.get("revision"),
        reference["digest"],
    )


def inspect_trial(destination):
    destination = Path(destination).resolve()
    native = destination / "native"
    index = json.loads((native / "index.json").read_text())
    assert index["schema"] == "recorda-lab.sabueso-artifacts/0.1"
    resolver = local_files(native, index["files"])
    files = {
        (ref.owner, ref.identifier, ref.revision, ref.digest): resolver.path_for(ref)
        for ref in resolver.references
    }

    def read(reference):
        try:
            path = files[_key(reference)]
        except KeyError:
            raise ValueError("unresolved native reference") from None
        return json.loads(path.read_text())

    def trace(reference):
        data = read(reference)
        if (
            reference["owner"] != "sabueso"
            or data["id"] != reference["identifier"]
            or data["format"] != "sabueso.acquisition_trace@1"
        ):
            raise ValueError("native trace identity does not match")
        return data

    def nested_inputs(value):
        if type(value) is dict and value.get("kind") == "reference":
            data = read(value)
            if data.get("schema") == "recorda-lab.sabueso-client/0.1":
                for ref in data["fixtures"].values():
                    read(ref)
            elif data.get("schema") == "recorda-lab.sabueso-resolver/0.1":
                client = read(data["uniprot"])
                for ref in client["fixtures"].values():
                    read(ref)
            elif data.get("schema") == "recorda-lab.sabueso-options/0.1":
                resolver = read(data["resolver"])
                client = read(resolver["uniprot"])
                for ref in client["fixtures"].values():
                    read(ref)
            elif data.get("schema") == "recorda-lab.sabueso-envelope/0.1":
                read(data["payload"])
                trace(data["trace"])

    journal = (destination / index["journal"]).resolve()
    if not journal.is_relative_to(destination):
        raise ValueError("journal outside the trial")
    record = recorda.inspect(journal)
    checked, statuses, events = [], [], {}
    for operation in record.operations:
        for value in operation["inputs"].values():
            nested_inputs(value)
        row = {
            "operation_id": operation["id"],
            "name": operation["name"],
            "parent_id": operation["parent_id"],
            "execution_status": operation["status"],
            "implementation": operation["implementation"],
        }
        output = operation["outputs"].get("return")
        if output is not None and output.get("kind") == "reference":
            manifest = read(output)
            native_trace = trace(manifest["trace"])
            if manifest["schema"] == "recorda-lab.sabueso-envelope/0.1":
                payload = read(manifest["payload"])
                row["source"] = payload["source"]
                row["query"] = payload["query"]
                row["retrieved_at"] = payload["retrieved_at"]
                row["source_version"] = payload["version"]
            elif manifest["schema"] == "recorda-lab.sabueso-result/0.1":
                resolution = read(manifest["resolution"])
                row["semantic_status"] = resolution["status"]
                row["entity_ref"] = resolution["entity_ref"]
                row["decision"] = resolution["decision"]
                row["candidates"] = resolution["candidates"]
                row["alternatives"] = resolution["alternatives"]
                statuses.append(resolution["status"])
                if manifest["card"] is not None:
                    card = read(manifest["card"])
                    ref = manifest["card"]
                    if (
                        ref["owner"] != "sabueso"
                        or ref["identifier"] != f"{card['meta']['card_id']}@{ref['revision']}"
                    ):
                        raise ValueError("native card pin does not match its receipt")
                    row["card_reference"] = ref
                    if native_trace.get("card_ref") != ref["identifier"]:
                        raise ValueError("native trace and card are misbound")
                elif resolution["status"] == "resolved":
                    raise ValueError("resolved entity has no retained card")
            else:
                raise ValueError("unsupported native result manifest")
            row["trace_reference"] = manifest["trace"]
            for event in native_trace["records"]:
                events[event["id"]] = event
        if "exception" in operation:
            reference = operation["exception"].get("reference")
            row["exception_reference"] = reference
            if reference is not None and reference.get("kind") == "reference":
                for event in trace(reference)["records"]:
                    events[event["id"]] = event
        checked.append(row)
    failure = index["failure"]
    if failure is not None:
        operation = next((op for op in record.operations if op["id"] == failure["operation"]), None)
        if operation is None or operation["status"] != "failed":
            raise ValueError("exception sidecar has no matching failed operation")
        for event in trace(failure["trace"])["records"]:
            events[event["id"]] = event
    return {
        "schema": "recorda-lab.sabueso-inspection/0.1",
        "status": record.status,
        "operations": checked,
        "semantic_statuses": statuses,
        "native_files_checked": len(index["files"]),
        "source_events": [
            {
                key: event.get(key)
                for key in (
                    "id",
                    "source",
                    "operation",
                    "query",
                    "producer",
                    "access",
                    "outcome",
                    "retrieved_at",
                    "source_version",
                    "response_identity",
                    "network_attempts",
                )
            }
            for event in events.values()
        ],
        "network_attempts": sum(event["network_attempts"] for event in events.values()),
        "coverage": record.coverage,
        "reference_checks": recorda.check_references(record, resolver=resolver),
        "scope": "trial-specific receipts, not authenticated integrity or replay",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    print(json.dumps(inspect_trial(parser.parse_args().destination), indent=2))


if __name__ == "__main__":
    main()
