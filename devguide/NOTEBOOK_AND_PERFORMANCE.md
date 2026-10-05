# Notebook and performance laboratory

Tracked by `uibcdf/recorda-lab#3` and `uibcdf/recorda-lab#2`, linked to
`uibcdf/recorda#1` and `uibcdf/recorda-lab#1`. The dummy scientific library is
unchanged and dependency-free. Instrumentation and native adapters stay in consumers.

## Notebook acceptance

`notebooks/01_manual_activation.ipynb` simulates start, ordinary decorated calls,
open-record inspection, stop and a failed analysis in separate cells.
`notebooks/02_recording_cost.ipynb` runs the performance experiment and presents its
medians. Sources have no execution outputs. `run_examples.py` executes every code
cell in disposable workspaces; it retains executed copies and checked source hashes.

`run_notebook.py` launches the current interpreter explicitly as a real IPykernel.
It checks separate execute requests for activation, calls and closing; top-level
await; rejection of a child task closing its owner; unhandled native ValueError;
SIGINT during a controlled declared wait; and kernel termination while an operation
is open. The four inspected journals have statuses succeeded, failed, failed and
incomplete. Native results and references agree. It saves cell sources in an executed
notebook, identities, journals and an acceptance report. Connection credentials and
kernel configuration/tracebacks are not archived. Runtime client channels are closed.

Linux Python 3.14.7 / IPykernel 7.3.0 / IPython 9.17.1 / jupyter-client 8.10.0 /
nbformat 5.11.1 is the qualified local combination. This proves kernel execute-request
behavior, not every browser frontend, deployment or context implementation.
The user-facing notebooks do not terminate their own interactive kernel.

## Measurement method

`run_performance.py` compares the same function directly, dormant-decorated,
active with omitted objects and active with exact-type native-reference adapters.
Workloads are sample count for four values, population statistics for four values
and population statistics for 10,000 deterministic values. Each mode rotates through
seven repetitions. Direct/dormant loops have 3,000 calls (60 for the larger input);
active loops have 30 calls. Native results and statuses are checked outside timing.
GC is collected before each loop and disabled only during timing. Opening/closing
the session and inspection are excluded. Raw wall and CPU observations and ranges
are retained; negative dormant deltas are measurement noise, not an acceleration claim.

The writer is unchanged: each active call records start, output and finish with
synchronous fsync. Event counts are inspected; fsync counts are inferred from the
current writer, not syscall tracing. Adapters include input JSON hashing and native
result identity. Fixtures/native output files accompany journals. No buffering,
mock fsync or performance pass/fail threshold is introduced. Measurements apply to
this Linux filesystem and process environment, with no deliberate concurrent laboratory
test load during the retained full benchmark.

The raw measured report is in `evidence/performance_linux_py314.json`. Notebook
qualification is in `evidence/notebook_linux_py314.json`. Recorda indexes commands,
tool versions, source/artifact hashes and regression results in
`recorda/devguide/evidence/notebook_performance_local.json`.

The expensive active path favors consequential semantic operations over frequent
helpers. Reference identities can also be costly when computed from large input
content; real integrations should evaluate native stable identities. Measurements
do not establish practical scientific utility or universal negligible overhead.

## Regression and scope

The explicit lane is `RECORDA_LAB_NOTEBOOK=1 python -m pytest --receptor=llm` with
published receptor 1.1.0 and declared Jupyter test dependencies. Ordinary runs skip
the two real-kernel tests. Manual hosted integration enables the lane, but has not
been executed. No public support, release, replay, browser or distribution is claimed.

The dummy-independence test now runs in a fresh process. Its former module reload
replaced the native Result class and contaminated later exact-type adapter tests.
The subprocess preserves the import-independence assertion without mutating classes
shared by other tests. This is a laboratory test isolation fix, not a Recorda adapter change.
