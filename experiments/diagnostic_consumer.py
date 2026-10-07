"""Application-owned Lab #14 diagnostic selection; native dummy science is independent."""

import json
from contextlib import contextmanager
from contextvars import ContextVar
from threading import RLock, local

SOURCE = "recorda_lab_consumer.summary"
BEFORE = "LAB-CONSUMER-BEFORE"
FAILED = "LAB-CONSUMER-FAILED"
AFTER = "LAB-CONSUMER-AFTER"
CODES = {
    BEFORE: {"user_message": "Controlled consumer diagnostic before summary."},
    FAILED: {"user_message": "Controlled consumer observed a failed summary attempt."},
    AFTER: {"user_message": "Controlled consumer observed a returned summary."},
}
AGGREGATES = {"SMONITOR-WARNING-COALESCED", "SMONITOR-EVENT-DUPLICATE-SUMMARY"}
SEVERITIES = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
_CURRENT = ContextVar("lab_diagnostic_operation", default=None)


def configure_application(*, handlers=None, **policy):
    """Explicit controlled application setup; never called per operation."""
    import smonitor
    from smonitor.handlers.memory import MemoryHandler

    if handlers is None:
        handlers = [MemoryHandler(max_events=512)]

    options = dict(
        handlers=list(handlers),
        codes={**smonitor.get_manager().get_codes(), **CODES},
        level="DEBUG",
        profile="user",
        enabled=True,
        capture_logging=False,
        capture_warnings=False,
        capture_exceptions=False,
        profiling=False,
        routes=[],
        filters=[],
        silence=[],
        duplicate_policy="off",
        warning_coalesce_window_s=0,
        event_buffer_size=1024,
        handler_error_threshold=0,
    )
    options.update(policy)
    return smonitor.configure(**options)


def observed_summary(samples, *, diagnostics=None):
    """Attribute diagnostics to this consumer, not the unchanged scientific library."""
    import smonitor

    from recorda_lab import summarize

    def diagnostic(level, code):
        try:
            smonitor.emit(level, "", source=SOURCE, code=code)
        except Exception:
            # Provider faults are diagnostic gaps; they cannot replace science.
            # Selected observation coverage always remains conditional on delivery.
            if diagnostics is not None:
                diagnostics.mark_gap("provider_fault")

    diagnostic("WARNING", BEFORE)
    try:
        result = summarize(samples)
    except Exception:
        diagnostic("ERROR", FAILED)
        raise
    diagnostic("INFO", AFTER)
    return result


class SelectedDiagnostics:
    """Small controlled sink; no journal writes, arbitrary copies or emissions.

    Facts are conditional delivered observations, not authenticated provenance.
    Application reconfiguration must explicitly declare loss of attachment.
    """

    name = "lab_selected_diagnostics"

    def __init__(self, *, max_entries=256, max_total=512):
        if type(max_entries) is not int or not 1 <= max_entries <= 256:
            raise ValueError("invalid per-operation budget")
        if type(max_total) is not int or not 1 <= max_total <= 512:
            raise ValueError("invalid aggregate budget")
        self.max_entries, self.max_total = max_entries, max_total
        self.operations = {}
        self.counts = dict.fromkeys(
            ("excluded", "unassigned", "stale", "invalid", "overflow", "sink_fault", "reentrant"), 0
        )
        self._lock = RLock()
        self._handling = local()
        self._manager = None
        self._total = 0

    def _count(self, reason):
        self.counts[reason] = min(self.counts[reason] + 1, (1 << 63) - 1)

    def attach(self, manager):
        if self._manager is not None:
            raise RuntimeError("sink is already attached")
        try:
            manager.add_handler(self)
        except Exception:
            self._count("sink_fault")
            try:
                manager.remove_handler(self)
            except Exception:
                self._count("sink_fault")
            return False
        self._manager = manager
        return True

    def detach(self):
        if self._manager is not None:
            manager = self._manager
            self._manager = None
            try:
                manager.remove_handler(self)
            except Exception:
                self._count("sink_fault")

    def declare_attachment_lost(self):
        """Application-owned fact; no inspection of private provider state."""
        with self._lock:
            for operation in self.operations.values():
                if operation["active"]:
                    operation["gaps"].add("unattached")
            self.detach()

    @contextmanager
    def boundary(self, session, operation):
        import smonitor

        key = (session.id, operation.id)
        parent = _CURRENT.get()
        with self._lock:
            if key in self.operations:
                raise ValueError("operation boundary already declared")
            registered = len(self.operations) < 32
            if not registered:
                self._count("overflow")
            else:
                self.operations[key] = {
                    "parent_id": parent[1] if parent and parent[0] == session.id else None,
                    "active": True,
                    "entries": [],
                    "gaps": set() if self._manager is not None else {"unattached"},
                }
        token = _CURRENT.set(key)
        try:
            # Detailed permissions preserve application rendering. Safe identities
            # partition provider aggregation; this is an explicit application choice.
            with smonitor.diagnostic_scope(
                smonitor.CapturePolicy(),
                safe_extra={"recorda_session_id": session.id, "recorda_operation_id": operation.id},
            ):
                yield
        finally:
            with self._lock:
                if registered:
                    self.operations[key]["active"] = False
            _CURRENT.reset(token)

    def mark_gap(self, reason, key=None):
        if reason not in {
            "artifact_fault",
            "provider_fault",
            "sink_fault",
            "overflow",
            "unattached",
        }:
            raise ValueError("unknown fixed gap")
        with self._lock:
            target = key or _CURRENT.get()
            if target in self.operations:
                self.operations[target]["gaps"].add(reason)

    def handle(self, event, *, profile="user"):
        with self._lock:
            if self._manager is None:
                return
            if getattr(self._handling, "active", False):
                self._count("reentrant")
                self.mark_gap("sink_fault")
                return
            self._handling.active = True
            try:
                self._select(event)
            except Exception:
                self._count("sink_fault")
                self.mark_gap("sink_fault")
            finally:
                self._handling.active = False

    def _select(self, event):
        if type(event) is not dict:
            self._count("invalid")
            return
        source, code, level = (event.get(k) for k in ("source", "code", "level"))
        if type(source) is not str or type(code) is not str or source != SOURCE:
            self._count("excluded")
            return
        aggregate = code in AGGREGATES
        if code not in CODES and not aggregate:
            self._count("excluded")
            return
        if type(level) is not str or level not in SEVERITIES:
            self._count("invalid")
            return
        extra = event.get("extra")
        if type(extra) is not dict:
            self._count("invalid")
            return
        ids = tuple(extra.get(k) for k in ("recorda_session_id", "recorda_operation_id"))
        if any(type(value) is not str or len(value) > 128 for value in ids):
            self._count("unassigned")
            return
        operation = self.operations.get(ids)
        if operation is None:
            self._count("unassigned")
            return
        if not aggregate and not operation["active"]:
            self._count("stale")
            return
        if not aggregate and _CURRENT.get() != ids:
            self._count("unassigned")
            return
        entry = {
            "code": code,
            "source": SOURCE,
            "level": level,
            "kind": "aggregate" if aggregate else "event",
        }
        if aggregate:
            numbers = {}
            for field in ("suppressed_count", "total_occurrences"):
                value = extra.get(field)
                if type(value) is not int or not 0 <= value < (1 << 63):
                    self._count("invalid")
                    return
                numbers[field] = value
            entry["producer_summary"] = numbers
        if len(operation["entries"]) >= self.max_entries or self._total >= self.max_total:
            self._count("overflow")
            operation["gaps"].add("overflow")
            return
        entry["ordinal"] = len(operation["entries"]) + 1
        operation["entries"].append(entry)
        self._total += 1

    def snapshot(self, session_id):
        with self._lock:
            operations = []
            for (recording, identity), item in self.operations.items():
                if recording != session_id:
                    continue
                gaps = sorted(
                    item["gaps"] | ({"missing_finalization"} if item["active"] else set())
                )
                state = "incomplete" if gaps else "observed_under_policy"
                if gaps == ["overflow"]:
                    state = "limited"
                operations.append(
                    {
                        "operation_id": identity,
                        "parent_id": item["parent_id"],
                        "coverage": {
                            "state": state,
                            "gaps": gaps,
                            "meaning": "selected delivered observations; suppressed events unknown",
                        },
                        "entries": [
                            dict(
                                e,
                                **(
                                    {"producer_summary": dict(e["producer_summary"])}
                                    if "producer_summary" in e
                                    else {}
                                ),
                            )
                            for e in item["entries"]
                        ],
                    }
                )
            snapshot = {
                "schema": "recorda-lab.diagnostic-association/0.1",
                "owner": "recorda-lab-consumer",
                "session_id": session_id,
                "operations": operations,
                "counts": dict(self.counts),
            }
            if len(json.dumps(snapshot, allow_nan=False).encode()) > 1024 * 1024:
                raise ValueError("association artifact byte budget exceeded")
            return snapshot
