"""Execute the committed usage notebooks in disposable workspaces and real kernels."""

import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path

import nbformat
from run_notebook import NotebookKernel


def run(destination):
    destination = Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=False)
    laboratory = Path(__file__).resolve().parents[1]
    examples = sorted((laboratory / "notebooks").glob("*.ipynb"))
    assert examples, "no committed notebook examples found"
    checked, skipped = {}, {}
    for source in examples:
        notebook = nbformat.read(source, as_version=4)
        nbformat.validate(notebook)
        if (
            notebook.metadata.get("recorda_lab", {}).get("lane") == "scipy"
            and os.environ.get("RECORDA_LAB_SCIPY") != "1"
        ):
            skipped[source.name] = "enable RECORDA_LAB_SCIPY=1 with scientific environment"
            continue
        workspace = destination / source.stem
        workspace.mkdir()
        shutil.copytree(laboratory / "experiments", workspace / "experiments")
        kernel = NotebookKernel(workspace)
        kernel.notebook.metadata = notebook.metadata
        try:
            for cell in notebook.cells:
                if cell.cell_type == "code":
                    assert not cell.outputs and cell.execution_count is None
                    kernel.execute(cell.source)
                else:
                    kernel.notebook.cells.append(cell)
        finally:
            kernel.close()
        nbformat.validate(kernel.notebook)
        executed = workspace / "executed.ipynb"
        checked[source.name] = {
            "code_cells_passed": sum(cell.cell_type == "code" for cell in notebook.cells),
            "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "executed_notebook": str(executed.relative_to(destination)),
            "executed_sha256": hashlib.sha256(executed.read_bytes()).hexdigest(),
        }
    report = {"schema": "recorda-lab.examples/0.1", "notebooks": checked, "skipped": skipped}
    (destination / "acceptance.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path, help="fresh directory for checked artifacts")
    print(json.dumps(run(parser.parse_args().destination), indent=2))


if __name__ == "__main__":
    main()
