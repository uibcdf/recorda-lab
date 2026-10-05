"""Check manual recording across execute requests to a real, explicitly selected kernel."""

import argparse
import hashlib
import json
import os
import sys
import tempfile
import time
from dataclasses import asdict
from importlib.metadata import version
from pathlib import Path

import nbformat
import recorda
from jupyter_client import KernelManager

import recorda_lab


class NotebookKernel:
    def __init__(self, destination):
        self.destination = destination
        self.notebook = nbformat.v4.new_notebook()
        self.connection = tempfile.TemporaryDirectory(prefix="recorda-kernel-")
        self.manager = KernelManager(
            kernel_name="python3", connection_file=str(Path(self.connection.name) / "kernel.json")
        )
        self.manager.kernel_spec.argv = [
            sys.executable,
            "-m",
            "ipykernel_launcher",
            "-f",
            "{connection_file}",
        ]
        paths = [
            Path(recorda.__file__).resolve().parents[1],
            Path(recorda_lab.__file__).resolve().parents[1],
            Path(__file__).resolve().parent,
        ]
        env = dict(
            os.environ,
            PYTHONPATH=os.pathsep.join(map(str, paths)),
            IPYTHONDIR=str(destination / "ipython"),
            JUPYTER_CONFIG_DIR=str(destination / "jupyter-config"),
        )
        try:
            self.manager.start_kernel(cwd=str(destination), env=env)
            self.client = self.manager.blocking_client()
            self.client.start_channels()
            self.client.wait_for_ready(timeout=30)
        except BaseException:
            self.close()
            raise

    def close(self):
        if hasattr(self, "client"):
            self.client.stop_channels()
        try:
            if self.manager.has_kernel:
                self.manager.shutdown_kernel(now=True)
        finally:
            self.connection.cleanup()
            nbformat.write(self.notebook, self.destination / "executed.ipynb")

    def execute(self, source, *, expected_error=None, marker=None, terminate=False):
        cell = nbformat.v4.new_code_cell(source)
        self.notebook.cells.append(cell)
        message_id = self.client.execute(source, stop_on_error=False)
        if marker is not None:
            deadline = time.monotonic() + 30
            while not marker.exists():
                if time.monotonic() >= deadline or not self.manager.is_alive():
                    raise RuntimeError("kernel did not enter the interruptible boundary")
                time.sleep(0.02)
            if terminate:
                self.manager.shutdown_kernel(now=True)
                cell.metadata["recorda_lab"] = {"outcome": "kernel_terminated_without_reply"}
                return
            self.manager.interrupt_kernel()
        deadline = time.monotonic() + 30
        errors = []
        while True:
            message = self.client.get_iopub_msg(timeout=max(0.1, deadline - time.monotonic()))
            if message["parent_header"].get("msg_id") != message_id:
                continue
            kind, content = message["header"]["msg_type"], message["content"]
            if kind == "execute_input":
                cell.execution_count = content["execution_count"]
            elif kind == "stream":
                cell.outputs.append(
                    nbformat.v4.new_output("stream", name=content["name"], text=content["text"])
                )
            elif kind in {"display_data", "execute_result"}:
                output = {"data": content["data"], "metadata": content.get("metadata", {})}
                if kind == "execute_result":
                    output["execution_count"] = content["execution_count"]
                cell.outputs.append(nbformat.v4.new_output(kind, **output))
            elif kind == "error":
                errors.append(content["ename"])
                # Fictional fixture errors only; do not archive kernel tracebacks/configuration.
                cell.outputs.append(
                    nbformat.v4.new_output("error", ename=content["ename"], evalue="", traceback=[])
                )
            elif kind == "status" and content["execution_state"] == "idle":
                break
        while True:
            reply = self.client.get_shell_msg(timeout=30)
            if reply["parent_header"].get("msg_id") == message_id:
                break
        expected = [] if expected_error is None else [expected_error]
        if errors != expected:
            raise AssertionError(f"unexpected cell error types: {errors}; expected {expected}")
        assert reply["content"]["status"] == ("ok" if expected_error is None else "error")
        cell.metadata["recorda_lab"] = {"expected_error": expected_error, "checked": True}


def run(destination):
    destination = Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    kernel = NotebookKernel(destination)
    try:
        kernel.execute(
            "import asyncio, json, sys, time\n"
            "from pathlib import Path\n"
            "from importlib.metadata import version\n"
            "import recorda, recorda_lab\n"
            "from consumer import REFERENCE_ADAPTERS, analyze, sample_count, summarize_samples\n"
            "samples = [1, 2, 3, 4]\n"
            "expected = recorda_lab.summarize(samples)\n"
            "assert summarize_samples(samples) == expected\n"
            "assert not list(Path('.').glob('*.jsonl'))\n"
            "Path('kernel-identity.json').write_text(json.dumps({\n"
            "    'executable': sys.executable, 'python': sys.version,\n"
            "    'ipykernel': version('ipykernel'), 'ipython': version('ipython'),\n"
            "    'recorda_file': recorda.__file__, 'dummy_file': recorda_lab.__file__,\n"
            "}))"
        )
        kernel.execute(
            "handle = recorda.start('cross_cell', path='cross-cell.jsonl',\n"
            "    reference_adapters=REFERENCE_ADAPTERS, gaps=['unwrapped dummy calls'])"
        )
        kernel.execute(
            "result = analyze(samples)\n"
            "assert result == expected\n"
            "assert sample_count(samples) == 4\n"
            "Path('native-result.json').write_text(json.dumps(result.to_dict(), sort_keys=True))"
        )
        kernel.execute(
            "async def inherited_child():\n"
            "    try:\n"
            "        recorda.stop()\n"
            "    except RuntimeError:\n"
            "        pass\n"
            "    else:\n"
            "        raise AssertionError('child closed its owner session')\n"
            "    return summarize_samples(samples)\n"
            "await asyncio.sleep(0)\n"
            "assert await asyncio.create_task(inherited_child()) == expected"
        )
        kernel.execute(
            "record = recorda.stop()\n"
            "assert record.status == 'succeeded' and len(record.operations) == 4\n"
            "assert summarize_samples(samples) == expected\n"
            "assert len(recorda.inspect('cross-cell.jsonl').operations) == 4"
        )
        kernel.execute(
            "recorda.start('native_failure', path='failure.jsonl',\n"
            "    reference_adapters=REFERENCE_ADAPTERS)"
        )
        kernel.execute("summarize_samples([])", expected_error="ValueError")
        kernel.execute("assert recorda.stop().status == 'failed'")
        kernel.execute(
            "@recorda.record('lab.wait_for_interrupt', profile='scientific_analysis')\n"
            "def wait_for_interrupt(marker):\n"
            "    Path(marker).write_text('boundary entered')\n"
            "    time.sleep(300)\n"
            "recorda.start('user_interrupt', path='interrupt.jsonl')"
        )
        kernel.execute(
            "wait_for_interrupt('interrupt-ready')",
            expected_error="KeyboardInterrupt",
            marker=destination / "interrupt-ready",
        )
        kernel.execute(
            "assert recorda.inspect('interrupt.jsonl').status == 'incomplete'\n"
            "assert recorda.stop().status == 'failed'"
        )
        kernel.execute("recorda.start('kernel_loss', path='kernel-loss.jsonl')")
        kernel.execute("assert sample_count(samples) == 4")
        kernel.execute(
            "wait_for_interrupt('loss-ready')", marker=destination / "loss-ready", terminate=True
        )
    finally:
        kernel.close()

    identity = json.loads((destination / "kernel-identity.json").read_text())
    assert Path(identity["executable"]).resolve() == Path(sys.executable).resolve()
    expected_status = {
        "cross-cell": "succeeded",
        "failure": "failed",
        "interrupt": "failed",
        "kernel-loss": "incomplete",
    }
    records = {}
    for name, status in expected_status.items():
        inspected = recorda.inspect(destination / f"{name}.jsonl")
        assert inspected.status == status and not inspected.problems
        records[name] = asdict(inspected)
    operations = records["cross-cell"]["operations"]
    assert [item["name"] for item in operations] == [
        "lab.analyze",
        "lab.summarize_samples",
        "lab.sample_count",
        "lab.summarize_samples",
    ]
    assert operations[1]["parent_id"] == operations[0]["id"]
    assert all(operations[index]["parent_id"] is None for index in [0, 2, 3])
    native = recorda_lab.summarize([1, 2, 3, 4])
    assert json.loads((destination / "native-result.json").read_text()) == native.to_dict()
    for index in [0, 1, 3]:
        assert operations[index]["outputs"]["return"]["identifier"] == native.identifier
    assert records["failure"]["operations"][0]["exception"]["type"] == "builtins.ValueError"
    assert (
        records["interrupt"]["operations"][0]["exception"]["type"] == "builtins.KeyboardInterrupt"
    )
    assert records["kernel-loss"]["operations"][-1]["status"] == "incomplete"
    report = {
        "schema": "recorda-lab.notebook/0.1",
        "tracking": ["uibcdf/recorda-lab#3", "uibcdf/recorda#1"],
        "kernel": identity,
        "client": {"jupyter_client": version("jupyter_client"), "nbformat": version("nbformat")},
        "scenarios": expected_status,
        "checks": [
            "activation/calls/stop in separate real kernel execute requests",
            "top-level await and child ownership guard",
            "inactive calls before and after; native result/reference coexistence",
            "uncaught native failure followed by stop in next cell",
            "SIGINT KeyboardInterrupt within declared operation",
            "kernel termination preserves unclosed operation/session",
        ],
        "records": records,
        "scope": "this IPykernel/client combination on this interpreter; no browser frontend claim",
    }
    report["executed_notebook_sha256"] = hashlib.sha256(
        (destination / "executed.ipynb").read_bytes()
    ).hexdigest()
    (destination / "acceptance.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path, help="fresh directory for checked artifacts")
    report = run(parser.parse_args().destination)
    print(json.dumps(report["scenarios"], indent=2))


if __name__ == "__main__":
    main()
