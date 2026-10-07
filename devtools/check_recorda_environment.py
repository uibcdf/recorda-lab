"""Read-only receiving preflight for an exact Recorda checkout and Lab routes."""

import argparse
import importlib.util
import json
import re
import subprocess
import tomllib
from pathlib import Path

import yaml
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from packaging.utils import canonicalize_name

ENVIRONMENTS = {
    "development_env.yaml",
    "test_env.yaml",
    "notebook_env.yaml",
    "scientific_env.yaml",
    "sabueso_diagnostics_env.yaml",
}
PROVIDERS = {"smonitor": "0.19.0=py_1", "argdigest": "0.15.0=py_0", "depdigest": "0.13.0=py_0"}


def audit(root, recorda, commit):
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("full reviewed Recorda SHA required")
    actual = subprocess.check_output(["git", "-C", str(recorda), "rev-parse", "HEAD"], text=True)
    if actual.strip() != commit:
        raise ValueError("selected Recorda checkout differs from requested SHA")
    project = tomllib.loads((recorda / "pyproject.toml").read_text())["project"]
    lab = tomllib.loads((root / "pyproject.toml").read_text())["project"]
    if lab["dependencies"]:
        raise ValueError("dummy package must remain independent of Recorda")
    if SpecifierSet(lab["requires-python"]) != SpecifierSet(project["requires-python"]):
        raise ValueError("review changed Recorda/Lab Python targets before receiving adoption")
    # Reuse the selected core's bounded Conda constraint checker; this is a
    # development tool, not a runtime dependency on a checkout or on MOLI.
    spec = importlib.util.spec_from_file_location(
        "recorda_dependency_preflight", recorda / "devtools/check_dependencies.py"
    )
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    required = {canonicalize_name(r.name): r for r in map(Requirement, project["dependencies"])}
    required["python"] = Requirement("python" + project["requires-python"])
    directory = root / "devtools/conda-envs"
    if {p.name for p in directory.glob("*.yaml")} != ENVIRONMENTS:
        raise ValueError("unclassified or missing laboratory environment")
    for name in sorted(ENVIRONMENTS):
        data = yaml.safe_load((directory / name).read_text())
        entries = [e for e in data["dependencies"] if isinstance(e, str)]
        supplied = {canonicalize_name(r.name): r for r in map(checker.conda_requirement, entries)}
        for provider, coordinate in PROVIDERS.items():
            if f"{provider}={coordinate}" not in entries:
                raise ValueError(f"{name}: missing reviewed published artifact for {provider}")
        if name == "sabueso_diagnostics_env.yaml":
            for artifact in ("pyunitwizard=0.28.1=py_0", "ackredit=0.11.0=py_0"):
                if artifact not in entries:
                    raise ValueError(f"{name}: missing reviewed scientific artifact {artifact}")
        for provider, requirement in required.items():
            candidate = supplied.get(provider)
            if candidate is None or not checker.contained(
                candidate.specifier, requirement.specifier
            ):
                raise ValueError(f"{name}: {provider} has {candidate}, requires {requirement}")
    workflow = yaml.safe_load((root / ".github/workflows/tests.yml").read_text())["jobs"]
    for job, environment in (
        ("integration", "notebook_env.yaml"),
        ("scientific", "scientific_env.yaml"),
        ("sabueso_diagnostics", "sabueso_diagnostics_env.yaml"),
    ):
        steps = workflow[job]["steps"]
        routes = [
            s.get("with", {}).get("environment-file")
            for s in steps
            if s.get("uses", "").startswith("mamba-org/setup-micromamba@")
        ]
        if routes != [f"lab/devtools/conda-envs/{environment}"]:
            raise ValueError(f"{job}: required provider closure is not provisioned")
    if any("environment-file" in s.get("with", {}) for s in workflow["dummy"]["steps"]):
        raise ValueError("dummy CI must remain independent of Recorda providers")
    return {
        "recorda_commit": commit,
        "runtime_environments": len(ENVIRONMENTS),
        "dummy_dependencies": 0,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recorda", type=Path, required=True)
    parser.add_argument("--commit", required=True)
    args = parser.parse_args()
    print(
        json.dumps(
            audit(Path(__file__).resolve().parents[1], args.recorda.resolve(), args.commit),
            sort_keys=True,
        )
    )
