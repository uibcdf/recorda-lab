"""Receiving questions use real native receipts, not duplicated core algorithms."""

import copy
import importlib.util
import json
import logging
import os
import subprocess
import sys
import warnings
from pathlib import Path

import pytest
import recorda


def load_trial(monkeypatch):
    experiments = Path(__file__).resolve().parents[1] / "experiments"
    monkeypatch.syspath_prepend(str(experiments))
    spec = importlib.util.spec_from_file_location(
        "inspection_trial", experiments / "run_inspection_view.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def trial(tmp_path, monkeypatch):
    module = load_trial(monkeypatch)
    destination = tmp_path / "inspection"
    return destination, module.run(destination)


def test_questions_distinguish_history_reference_observations_and_coverage(trial):
    destination, result = trial
    assert result["scientific_result"] == {
        "owner": "recorda-lab",
        "schema": "recorda-lab.result/0.1",
        "count": 4,
        "mean": 2.5,
        "variance": 1.25,
    }
    phases = result["reference_views"]
    raw = json.loads((destination / "references/acceptance.json").read_text())["reports"]
    for phase, cases in phases.items():
        for name, view in cases.items():
            assert view["reference_report"] == raw[phase][name]
            assert view["execution"]["status"] == raw[phase][name]["session_status"]
            assert all(f["presentation"]["status"] == "resolved" for f in view["findings"])
    for phase, state in (("missing_input", "missing"), ("modified_output", "mismatched")):
        view = phases[phase]["full"]
        (finding,) = view["findings"]
        assert view["execution"]["status"] == "succeeded"
        assert finding["state"] == state and finding["count"] == 2
        assert finding["presentation"]["message"].startswith("Supplied reference check: ")
        assert finding["distinct_references"] == 1
        assert len(finding["source_indices"]) == 2
        assert view["references"]["by_status"] == {state: 2, "matched": 2}
    for phase in ("intact", "restored"):
        assert phases[phase]["full"]["findings"] == []
        assert phases[phase]["full"]["references"]["by_status"] == {"matched": 4}
    minimal = phases["intact"]["minimal"]
    assert minimal["references"]["checked_occurrences"] == 0
    assert minimal["coverage"]["omissions_by_reason"] == {"capture_policy": 6}
    assert minimal["findings"] == []
    limits = phases["intact"]["limits"]
    assert limits["references"]["by_status"] == {"available_unverified": 1, "unresolved": 1}
    assert {f["state"] for f in limits["findings"]} == {"available_unverified", "unresolved"}
    interrupted = phases["intact"]["interrupted"]
    assert interrupted["execution"]["status"] == "incomplete"
    assert interrupted["findings"][0]["state"] == "incomplete"
    assert interrupted["findings"][0]["count"] == 1
    assert result["without_checking"]["references"]["check_state"] == "not_requested"
    assert result["without_checking"]["references"]["checked_occurrences"] is None
    tail = result["truncated"]
    assert tail["record"]["problems"] == ["truncated_tail"]
    assert tail["execution"]["status"] == "incomplete"
    assert "truncated_tail" in {f["state"] for f in tail["findings"]}
    assert json.loads((destination / "acceptance.json").read_text()) == result
    assert (destination / "references/native/samples.json").read_text() == "[1, 2, 3, 4]"
    assert (
        json.loads((destination / "references/native/result.json").read_text())
        == result["scientific_result"]
    )


def test_projection_preserves_saved_sources_and_does_not_recheck(trial, monkeypatch):
    import recorda.references as references
    from inspection_examples import reference_views

    destination, result = trial
    root = destination / "references"
    inputs = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
    raw = json.loads((root / "acceptance.json").read_text())["reports"]
    saved = copy.deepcopy(raw)

    def forbidden(*args, **kwargs):
        raise AssertionError("projection must not reread native bytes")

    monkeypatch.setattr(references, "_check_reference", forbidden)
    views = reference_views(root, raw)
    assert views == result["reference_views"]
    assert raw == saved and all(path.read_bytes() == data for path, data in inputs.items())
    views["intact"]["full"]["reference_report"]["references"].clear()
    assert raw == saved


@pytest.mark.parametrize("missing", [False, True])
def test_saved_view_reading_needs_no_scientific_producers(trial, reader_packages, missing):
    destination, _ = trial
    experiments = Path(__file__).resolve().parents[1] / "experiments"
    script = """
import importlib.abc, importlib.util, json, logging, sys, warnings
sys.path[:0] = sys.argv[1:3]
missing = sys.argv[4] == 'True'
class Block(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] == 'smonitor' and missing:
            raise ModuleNotFoundError('provider unavailable', name='smonitor')
sys.meta_path.insert(0,Block())
from pathlib import Path
from inspection_examples import reference_views
root = Path(sys.argv[3]) / 'references'
raw = json.loads((root/'acceptance.json').read_text())['reports']
hook, handlers = warnings.showwarning, tuple(logging.getLogger().handlers)
view = reference_views(root,raw)['missing_input']['full']
assert warnings.showwarning is hook and tuple(logging.getLogger().handlers) == handlers
assert all(importlib.util.find_spec(name) is None for name in ('recorda_lab','numpy','scipy','sabueso','pyunitwizard'))
finding, = view['findings']
assert finding['count'] == 2 and finding['distinct_references'] == 1
assert finding['presentation']['status'] == ('unavailable' if missing else 'resolved')
if missing:
    assert finding['presentation']['reason'] == 'provider_missing'
print(json.dumps({'execution':view['execution']['status'],'state':finding['state']}))
"""
    child = subprocess.run(
        [
            sys.executable,
            "-I",
            "-S",
            "-c",
            script,
            str(experiments),
            str(reader_packages),
            str(destination),
            str(missing),
        ],
        env={k: v for k, v in os.environ.items() if k != "PYTHONPATH"},
        capture_output=True,
        text=True,
        check=True,
    )
    assert json.loads(child.stdout) == {"execution": "succeeded", "state": "missing"}


class Opaque:
    def __repr__(self):
        raise AssertionError("native repr called")

    def __str__(self):
        raise AssertionError("native text called")

    def __deepcopy__(self, memo):
        raise AssertionError("native copying called")


def test_hostile_snapshot_and_incompatible_saved_observations_are_rejected(trial):
    destination, result = trial
    record = recorda.inspect(destination / "references/full.jsonl")
    report = result["reference_views"]["missing_input"]["full"]["reference_report"]
    changed = copy.deepcopy(report)
    changed["references"][0]["reference"]["revision"] = "wrong snapshot"
    with pytest.raises(ValueError):
        recorda.inspection_view(record, reference_report=changed)
    changed = copy.deepcopy(report)
    index = next(i for i, r in enumerate(changed["references"]) if r["status"] == "missing")
    changed["references"][index]["status"] = "matched"
    with pytest.raises(ValueError):
        recorda.inspection_view(record, reference_report=changed)
    record.operations[0]["outputs"]["native"] = Opaque()
    with pytest.raises(TypeError):
        recorda.inspection_view(record, reference_report=report)


def test_rendering_failure_keeps_answers_and_application_policy(trial, monkeypatch):
    import recorda.integrations.smonitor as adapter
    import smonitor
    from smonitor.handlers.memory import MemoryHandler

    destination, result = trial
    record = recorda.inspect(destination / "references/full.jsonl")
    # These JSON details remain source-owned and must never reach templates.
    record.name = "private session token"
    report = copy.deepcopy(result["reference_views"]["missing_input"]["full"]["reference_report"])
    handler = MemoryHandler()
    manager = smonitor.configure(
        handlers=[handler],
        level="DEBUG",
        profile="qa",
        enabled=True,
        args_summary=True,
        capture_logging=False,
        capture_warnings=False,
        capture_exceptions=False,
        profiling=False,
        filters=[],
        routes=[],
    )
    policy = manager.config
    hook, handlers = warnings.showwarning, tuple(logging.getLogger().handlers)
    view = recorda.inspection_view(record, reference_report=report)
    assert view["findings"][0]["presentation"]["status"] == "resolved"
    assert "private" not in json.dumps(view["findings"])

    class ProviderFault(RuntimeError):
        __repr__ = Opaque.__repr__
        __str__ = Opaque.__str__

    def fail(**kwargs):
        raise ProviderFault()

    monkeypatch.setattr(adapter, "resolve", fail)
    fallback = recorda.inspection_view(record, reference_report=report)
    assert fallback["references"] == view["references"]
    assert fallback["execution"] == view["execution"]
    assert fallback["reference_report"] == report
    (finding,) = fallback["findings"]
    assert finding["presentation"]["reason"] == "rendering_failed"
    assert finding["fallback"] == "references/missing: 2"
    assert manager.config is policy and handler.events == []
    assert warnings.showwarning is hook and tuple(logging.getLogger().handlers) == handlers


@pytest.mark.skipif(
    os.environ.get("RECORDA_LAB_SCIPY") != "1",
    reason="inspection workflow comparison requires explicit SciPy lane",
)
def test_multi_step_view_keeps_native_oracle_and_attempt_history(tmp_path, monkeypatch):
    module = load_trial(monkeypatch)
    result = module.run(tmp_path / "workflow-view", with_workflow=True)
    workflow = result["workflow"]
    views, scientific = workflow["views"], workflow["scientific_checks"]
    assert scientific["full"]["oracle"]["parameters"] == pytest.approx([87 / 35, -23 / 35])
    assert scientific["full"]["oracle"]["rss"] == pytest.approx(1 / 14)
    assert views["full"]["execution"]["status"] == "succeeded"
    assert scientific["full"]["status"] == "consistent"
    assert views["retry"]["execution"]["status"] == "failed"
    assert views["retry"]["execution"]["by_status"]["failed"] == 1
    assert scientific["retry"]["status"] == "consistent"
    assert views["minimal"]["findings"] == []
    assert views["minimal"]["coverage"]["omissions_by_reason"]["capture_policy"] > 0
    assert scientific["minimal"]["status"] == "unavailable"
    assert views["interrupted"]["execution"]["status"] == "incomplete"
    assert views["interrupted"]["findings"][0]["count"] == 2
    for case, state in (
        ("missing_intermediate", "missing"),
        ("modified_intermediate", "mismatched"),
    ):
        assert views[case]["execution"]["status"] == "succeeded"
        assert state in views[case]["references"]["by_status"]
        assert scientific[case]["status"] == "unavailable"
    assert views["restored"] == views["full"]
