"""Controlled science and diagnostic oracles, including honest delivery gaps."""

import asyncio
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from contextvars import Context, copy_context
from pathlib import Path

import pytest

recorda = pytest.importorskip("recorda")
sm = pytest.importorskip("smonitor")


@pytest.fixture
def consumer(monkeypatch):
    root = Path(__file__).resolve().parents[1]
    monkeypatch.syspath_prepend(str(root / "experiments"))
    import diagnostic_consumer as consumer

    return consumer


@pytest.fixture
def sink(consumer):
    manager = consumer.configure_application()
    # Flush leftovers outside the new handler's lifetime.
    manager.flush_duplicate_summaries()
    manager.flush_coalesced_warnings()
    value = consumer.SelectedDiagnostics()
    assert value.attach(manager)
    yield value
    value.detach()


@pytest.fixture
def trial(tmp_path):
    experiment = Path(__file__).resolve().parents[1] / "experiments/run_diagnostic_association.py"
    destination = tmp_path / "trial"
    child = subprocess.run(
        [sys.executable, str(experiment), str(destination)],
        capture_output=True,
        text=True,
        check=True,
    )
    return destination, json.loads((destination / "acceptance.json").read_text()), child


def emit(consumer, code=None, level="WARNING"):
    return sm.emit(level, "", source=consumer.SOURCE, code=code or consumer.BEFORE)


def test_application_setup_preserves_registered_catalogs(consumer):
    existing = sm.get_manager().get_codes()
    sentinel = {"LAB-EXISTING-PROVIDER": {"user_message": "Existing provider."}}
    sm.configure(codes={**existing, **sentinel})
    manager = consumer.configure_application()
    assert manager.get_codes() == {**existing, **sentinel, **consumer.CODES}
    assert sm.resolve(code="LAB-EXISTING-PROVIDER")[0] == "Existing provider."


def test_reviewed_native_bundle_matches_both_session_and_operation(sink, consumer, tmp_path):
    from run_diagnostic_association import reviewed_bundle

    with recorda.session("bundle-binding", path=tmp_path / "record.jsonl") as session:
        with session.operation("summary") as op, sink.boundary(session, op):
            emit(consumer)
            with sm.diagnostic_scope(
                sm.CapturePolicy(), safe_extra={"recorda_session_id": "foreign"}
            ):
                emit(consumer)
        bundle = reviewed_bundle(session.id, op.id)
    assert len(bundle["events"]) == 1
    assert bundle["events"][0]["extra"]["recorda_session_id"] == session.id
    assert sink.counts["unassigned"] == 1


def test_trial_answers_attempt_question_and_preserves_scientific_oracle(trial, consumer):
    root, report, child = trial
    assert json.loads(child.stdout)["execution"] == "failed"
    assert report["science"] == {
        "owner": "recorda-lab",
        "schema": "recorda-lab.result/0.1",
        "count": 4,
        "mean": 2.5,
        "variance": 1.25,
    }
    assert [op["status"] for op in report["record"]["operations"]] == [
        "succeeded",
        "failed",
        "succeeded",
    ]
    rows = report["association"]["operations"]
    assert len({row["operation_id"] for row in rows}) == 3
    assert [[e["code"] for e in row["entries"]] for row in rows] == [
        [consumer.BEFORE, consumer.AFTER],
        [consumer.BEFORE, consumer.FAILED],
        [consumer.BEFORE, consumer.AFTER],
    ]
    bundle = json.loads((root / "failure-bundle.json").read_text())
    association = json.loads((root / "failure-association.json").read_text())
    assert [e["code"] for e in bundle["events"]] == [consumer.BEFORE, consumer.FAILED]
    assert "message" in bundle["events"][0]
    assert "message" not in association["operations"][0]["entries"][0]
    assert "argv" not in bundle and "providers" not in bundle
    assert "smonitor" != association["owner"]
    assert report["interrupted"]["status"] == "incomplete"
    assert report["interrupted"]["operations"][0]["status"] == "incomplete"
    assert report["views"]["missing"]["execution"]["status"] == "failed"
    for phase, state, count in (
        ("intact", "matched", 8),
        ("missing", "missing", 1),
        ("altered", "mismatched", 1),
    ):
        assert (
            sum(item["status"] == state for item in report["references"][phase]["references"])
            == count
        )
    assert report["references"]["restored"] == report["references"]["intact"]


def test_native_return_and_error_are_exact_objects(sink, consumer, tmp_path, monkeypatch):
    import recorda_lab

    native_result, error = object(), ValueError()
    with recorda.session("identity", path=tmp_path / "record.jsonl") as session:
        with session.operation("success") as operation, sink.boundary(session, operation):
            monkeypatch.setattr(recorda_lab, "summarize", lambda samples: native_result)
            assert consumer.observed_summary([1], diagnostics=sink) is native_result

        def fail(samples):
            raise error

        monkeypatch.setattr(recorda_lab, "summarize", fail)
        with pytest.raises(ValueError) as caught:
            with session.operation("failed") as operation, sink.boundary(session, operation):
                consumer.observed_summary([], diagnostics=sink)
        assert caught.value is error


@pytest.mark.parametrize(
    "policy",
    [
        {"enabled": False},
        {"level": "CRITICAL"},
        {"filters": [{"when": {"source": "recorda_lab_consumer.summary"}, "drop": True}]},
        {"routes": [{"when": {"source": "recorda_lab_consumer.summary"}, "send_to": ["memory"]}]},
    ],
)
def test_zero_observations_do_not_assert_no_warnings(sink, consumer, tmp_path, policy):
    sm.configure(**policy)
    with recorda.session("filter", path=tmp_path / "record.jsonl") as session:
        with session.operation("summary") as operation, sink.boundary(session, operation):
            assert consumer.observed_summary([1, 2, 3, 4], diagnostics=sink).mean == 2.5
    (row,) = sink.snapshot(session.id)["operations"]
    assert row["entries"] == [] and row["coverage"]["state"] == "observed_under_policy"
    assert "suppressed events unknown" in row["coverage"]["meaning"]


def test_app_declares_replaced_handler_without_private_polling(sink, consumer, tmp_path):
    from smonitor.handlers.memory import MemoryHandler

    with recorda.session("replacement", path=tmp_path / "record.jsonl") as session:
        with session.operation("summary") as operation, sink.boundary(session, operation):
            sm.configure(handlers=[MemoryHandler()])
            sink.declare_attachment_lost()
            result = consumer.observed_summary([1, 2, 3, 4], diagnostics=sink)
    (row,) = sink.snapshot(session.id)["operations"]
    assert result.mean == 2.5 and row["entries"] == []
    assert row["coverage"]["gaps"] == ["unattached"]


@pytest.mark.parametrize(
    "policy", [{"duplicate_policy": "emit_summary"}, {"warning_coalesce_window_s": 60}]
)
def test_deferred_aggregates_keep_attempt_origin_and_separate_counts(
    sink, consumer, tmp_path, policy
):
    sm.configure(**policy)
    with recorda.session("aggregate", path=tmp_path / "record.jsonl") as session:
        for name in ("left", "right"):
            with session.operation(name) as operation, sink.boundary(session, operation):
                emit(consumer)
                emit(consumer)
        sm.get_manager().flush_duplicate_summaries()
        sm.get_manager().flush_coalesced_warnings()
    rows = sink.snapshot(session.id)["operations"]
    for row in rows:
        assert [e["kind"] for e in row["entries"]] == ["event", "aggregate"]
        assert row["entries"][1]["producer_summary"] == {
            "suppressed_count": 1,
            "total_occurrences": 2,
        }


def test_nested_interleaved_tasks_and_late_child(sink, consumer, tmp_path):
    async def scenario():
        with recorda.session("tasks", path=tmp_path / "record.jsonl") as session:
            with session.operation("parent") as parent, sink.boundary(session, parent):

                async def worker(name):
                    with session.operation(name) as op, sink.boundary(session, op):
                        await asyncio.sleep(0)
                        emit(consumer)

                await asyncio.gather(worker("left"), worker("right"))
                ready = asyncio.Event()

                async def late():
                    await ready.wait()
                    emit(consumer)

                child = asyncio.create_task(late())
            ready.set()
            await child
        return session.id, parent.id

    identity, parent = asyncio.run(scenario())
    rows = sink.snapshot(identity)["operations"]
    assert rows[0]["entries"] == []
    assert all(row["parent_id"] == parent and len(row["entries"]) == 1 for row in rows[1:])
    assert sink.counts["stale"] == 1
    emit(consumer)
    assert sink.counts["unassigned"] == 1


def test_thread_context_is_explicit(sink, consumer, tmp_path):
    with recorda.session("threads", path=tmp_path / "record.jsonl") as session:
        with session.operation("parent") as op, sink.boundary(session, op):
            with ThreadPoolExecutor(max_workers=1) as pool:
                pool.submit(Context().run, emit, consumer).result()
                pool.submit(copy_context().run, emit, consumer).result()
    (row,) = sink.snapshot(session.id)["operations"]
    assert len(row["entries"]) == 1 and sink.counts["unassigned"] == 1


def test_unknown_recovery_and_hostile_payloads_are_not_copied(sink, consumer, tmp_path):
    class Opaque:
        def __repr__(self):
            raise AssertionError("repr invoked")

        __str__ = __repr__

        def __deepcopy__(self, memo):
            raise AssertionError("deepcopy invoked")

    with recorda.session("privacy", path=tmp_path / "record.jsonl") as session:
        with session.operation("summary") as op, sink.boundary(session, op):
            ids = {"recorda_session_id": session.id, "recorda_operation_id": op.id}
            sink.handle(
                {
                    "source": consumer.SOURCE,
                    "code": consumer.BEFORE,
                    "level": "WARNING",
                    "extra": dict(ids, private=Opaque()),
                    "message": Opaque(),
                    "context": Opaque(),
                }
            )
            sink.handle({"source": Opaque(), "code": Opaque()})
            sink.handle({"source": consumer.SOURCE, "code": "UNSELECTED", "level": "WARNING"})
            sink.handle({"source": "recorda.runtime", "code": "RECORDA-RECOVERY-OPERATION-001"})
    data = json.dumps(sink.snapshot(session.id))
    assert "private" not in data and "UNSELECTED" not in data and "RECOVERY" not in data
    assert sink.counts["excluded"] == 3


def test_sink_and_provider_faults_are_visible_without_replacing_science(
    sink, consumer, tmp_path, monkeypatch
):
    def fault(event):
        raise OSError()

    monkeypatch.setattr(sink, "_select", fault)
    with recorda.session("fault", path=tmp_path / "record.jsonl") as session:
        with session.operation("summary") as op, sink.boundary(session, op):
            assert consumer.observed_summary([1, 2, 3, 4], diagnostics=sink).variance == 1.25
    (row,) = sink.snapshot(session.id)["operations"]
    assert row["coverage"]["gaps"] == ["sink_fault"] and sink.counts["sink_fault"] == 2

    def provider_fault(*args, **kwargs):
        raise OSError()

    monkeypatch.setattr(sm, "emit", provider_fault)
    with recorda.session("provider-fault", path=tmp_path / "other.jsonl") as other:
        with other.operation("summary") as op, sink.boundary(other, op):
            assert consumer.observed_summary([1, 2, 3, 4], diagnostics=sink).mean == 2.5
    assert sink.snapshot(other.id)["operations"][0]["coverage"]["gaps"] == ["provider_fault"]


@pytest.mark.parametrize("failure", [KeyboardInterrupt(), SystemExit(), asyncio.CancelledError()])
def test_native_interruptions_and_cancellation_propagate(
    sink, consumer, tmp_path, monkeypatch, failure
):
    import recorda_lab

    def fail(samples):
        raise failure

    monkeypatch.setattr(recorda_lab, "summarize", fail)
    with pytest.raises(type(failure)) as caught:
        with recorda.session("interrupt", path=tmp_path / "record.jsonl") as session:
            with session.operation("summary") as op, sink.boundary(session, op):
                consumer.observed_summary([1], diagnostics=sink)
    assert caught.value is failure
    assert recorda.inspect(tmp_path / "record.jsonl").status == "failed"


def test_artifact_writer_fault_keeps_native_error_and_exposes_gap(
    sink, consumer, tmp_path, monkeypatch
):
    import run_diagnostic_association as trial

    import recorda_lab

    error = ValueError()

    def science_failure(samples):
        raise error

    def artifact_failure(*args):
        raise OSError()

    monkeypatch.setattr(recorda_lab, "summarize", science_failure)
    with recorda.session("writer-fault", path=tmp_path / "record.jsonl") as session:
        with pytest.raises(ValueError) as caught:
            trial.attempt(session, sink, tmp_path, "failure", [], [], writer=artifact_failure)
        assert caught.value is error
    (row,) = sink.snapshot(session.id)["operations"]
    assert row["coverage"]["gaps"] == ["artifact_fault"]
    (op,) = recorda.inspect(tmp_path / "record.jsonl").operations
    assert op["status"] == "failed" and op["outputs"]["association"]["kind"] == "omitted"


def test_artifact_writer_fault_keeps_successful_native_result(sink, consumer, tmp_path):
    import run_diagnostic_association as trial

    def artifact_failure(*args):
        raise OSError()

    with recorda.session("writer-success", path=tmp_path / "record.jsonl") as session:
        result = trial.attempt(
            session, sink, tmp_path, "success", [1, 2, 3, 4], [], writer=artifact_failure
        )
    assert result.mean == 2.5 and result.variance == 1.25
    assert sink.snapshot(session.id)["operations"][0]["coverage"]["gaps"] == ["artifact_fault"]
    (operation,) = recorda.inspect(tmp_path / "record.jsonl").operations
    assert operation["status"] == "succeeded"
    assert operation["outputs"]["association"]["reason"] == "caller_omitted"


def test_detach_failure_stops_accepting_events_and_keeps_native_error(
    sink, consumer, tmp_path, monkeypatch
):
    manager = sm.get_manager()
    remove = manager.remove_handler
    error = ValueError()

    def cleanup_fault(handler):
        raise OSError()

    monkeypatch.setattr(manager, "remove_handler", cleanup_fault)
    try:
        with pytest.raises(ValueError) as caught:
            with recorda.session("detach", path=tmp_path / "record.jsonl") as session:
                with session.operation("failure") as op, sink.boundary(session, op):
                    emit(consumer)
                    try:
                        raise error
                    finally:
                        sink.detach()
        assert caught.value is error
        emit(consumer)
        assert sink.counts["sink_fault"] == 1
        assert len(sink.snapshot(session.id)["operations"][0]["entries"]) == 1
    finally:
        remove(sink)


def test_invalid_summary_and_snapshot_mutation_do_not_corrupt_facts(sink, consumer, tmp_path):
    with recorda.session("validation", path=tmp_path / "record.jsonl") as session:
        with session.operation("summary") as op, sink.boundary(session, op):
            ids = {"recorda_session_id": session.id, "recorda_operation_id": op.id}
            sink.handle(
                {
                    "source": consumer.SOURCE,
                    "code": "SMONITOR-EVENT-DUPLICATE-SUMMARY",
                    "level": "WARNING",
                    "extra": dict(ids, suppressed_count=True, total_occurrences=2),
                }
            )
            emit(consumer)
    snapshot = sink.snapshot(session.id)
    snapshot["operations"][0]["entries"][0]["code"] = "changed"
    snapshot["counts"]["invalid"] = 0
    fresh = sink.snapshot(session.id)
    assert fresh["counts"]["invalid"] == 1
    assert fresh["operations"][0]["entries"][0]["code"] == consumer.BEFORE


def test_reader_keeps_failed_history_when_sidecar_disappears(trial, consumer):
    from inspect_diagnostic_association import answers

    root, _, _ = trial
    (root / "failure-association.json").unlink()
    value = answers(root)
    assert value["execution"] == "failed"
    assert [row["diagnostics"] for row in value["attempts"]] == [
        "available",
        "unavailable",
        "available",
    ]
    assert value["attempts"][1]["codes"] is None


def test_entry_and_registry_budgets_are_explicit(consumer, tmp_path):
    manager = consumer.configure_application()
    sink = consumer.SelectedDiagnostics(max_entries=1, max_total=2)
    sink.attach(manager)
    try:
        with recorda.session("budget", path=tmp_path / "record.jsonl") as session:
            for index in range(32):
                with session.operation("bounded") as op, sink.boundary(session, op):
                    emit(consumer)
                    emit(consumer)
            with session.operation("overflow") as op, sink.boundary(session, op):
                assert consumer.observed_summary([1, 2, 3, 4], diagnostics=sink).mean == 2.5
        rows = sink.snapshot(session.id)["operations"]
        assert len(rows) == 32 and sum(len(row["entries"]) for row in rows) == 2
        assert all(row["coverage"]["state"] == "limited" for row in rows)
    finally:
        sink.detach()


def test_incomplete_lifetime_and_reentrancy_are_explicit(sink, consumer, tmp_path, monkeypatch):
    original = sink._select

    def recursive(event):
        sink.handle(event)
        original(event)

    monkeypatch.setattr(sink, "_select", recursive)
    with recorda.session("reentrancy", path=tmp_path / "record.jsonl") as session:
        with session.operation("summary") as op, sink.boundary(session, op):
            (before,) = sink.snapshot(session.id)["operations"]
            assert before["coverage"]["gaps"] == ["missing_finalization"]
            emit(consumer)
    (row,) = sink.snapshot(session.id)["operations"]
    assert sink.counts["reentrant"] == 1 and row["coverage"]["gaps"] == ["sink_fault"]


def test_public_attachment_faults_cannot_replace_science(consumer, tmp_path):
    class FaultyManager:
        def add_handler(self, sink):
            raise OSError()

        def remove_handler(self, sink):
            raise OSError()

    sink = consumer.SelectedDiagnostics()
    consumer.configure_application()
    assert sink.attach(FaultyManager()) is False
    with recorda.session("unattached", path=tmp_path / "record.jsonl") as session:
        with session.operation("summary") as op, sink.boundary(session, op):
            assert consumer.observed_summary([1, 2, 3, 4], diagnostics=sink).mean == 2.5
    assert sink.snapshot(session.id)["operations"][0]["coverage"]["gaps"] == ["unattached"]


def test_reader_uses_no_scientific_or_diagnostic_producer(trial, reader_packages):
    destination, _, _ = trial
    experiments = Path(__file__).resolve().parents[1] / "experiments"
    code = """
import importlib.util, json, sys
sys.path[:0] = sys.argv[1:3]
from inspect_diagnostic_association import answers
value = answers(sys.argv[3])
assert all(importlib.util.find_spec(n) is None for n in ('recorda_lab','numpy','scipy','sabueso'))
assert 'diagnostic_consumer' not in sys.modules
print(json.dumps(value))
"""
    child = subprocess.run(
        [
            sys.executable,
            "-I",
            "-S",
            "-c",
            code,
            str(experiments),
            str(reader_packages),
            str(destination),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    result = json.loads(child.stdout)
    assert result["execution"] == "failed"
    assert len(result["attempts"]) == 3 and all(
        row["diagnostics"] == "available" for row in result["attempts"]
    )
