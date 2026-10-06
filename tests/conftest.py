"""Controlled reader imports with Recorda's required support closure only."""

import importlib.util
import shutil

import pytest


@pytest.fixture
def reader_packages(tmp_path):
    # -I -S children receive these unchanged package trees, never the complete
    # scientific site-packages directory. Producers are genuinely unavailable.
    destination = tmp_path / "reader-packages"
    destination.mkdir()
    for name in ("recorda", "smonitor", "argdigest", "depdigest"):
        spec = importlib.util.find_spec(name)
        assert spec is not None and spec.submodule_search_locations, name
        shutil.copytree(next(iter(spec.submodule_search_locations)), destination / name)
    return destination
