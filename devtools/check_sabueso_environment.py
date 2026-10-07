"""Verify Lab #15's additional published scientific support closure."""

import hashlib
import importlib
import json
import sys
import sysconfig
from importlib.metadata import version
from pathlib import Path

ARTIFACTS = {
    "pyunitwizard": (
        "0.28.1",
        "py_0",
        "d4654faf93ed4181bf331f7d382379e78f02784f71f678ad19d0ac43d8062cc6",
    ),
    "ackredit": (
        "0.11.0",
        "py_0",
        "df8963ca2d286f50b19eb778e95c54c5ebb79c12fb55a6504e7c23daf5717d4f",
    ),
}


def verify():
    prefix = Path(sys.prefix).resolve()
    purelib = Path(sysconfig.get_paths()["purelib"]).resolve()
    evidence = {}
    for name, (expected_version, build, sha) in ARTIFACTS.items():
        records = list((prefix / "conda-meta").glob(f"{name}-*.json"))
        assert len(records) == 1, name
        record = json.loads(records[0].read_text())
        filename = f"{name}-{expected_version}-{build}.tar.bz2"
        assert (record["fn"], record["sha256"]) == (filename, sha), name
        assert record["url"] == f"https://conda.anaconda.org/uibcdf/noarch/{filename}", name
        assert version(name) == expected_version, name
        package = Path(importlib.import_module(name).__file__).resolve().parent
        assert package.is_relative_to(prefix), f"{name}: source shadowing"
        managed = set(record["files"])
        checked = 0
        for item in record["paths_data"]["paths"]:
            rel = item["_path"]
            path = (
                purelib / rel.removeprefix("site-packages/")
                if rel.startswith("site-packages/")
                else prefix / rel
            )
            assert str(path.relative_to(prefix)) in managed, path
            if path.suffix == ".py" and path.is_relative_to(package):
                expected = item.get("sha256_in_prefix", item["sha256"])
                assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, path
                checked += 1
        assert checked, name
        evidence[name] = dict(
            version=expected_version, file=filename, sha256=sha, python_files=checked
        )
    print(json.dumps(evidence, sort_keys=True))


if __name__ == "__main__":
    verify()
