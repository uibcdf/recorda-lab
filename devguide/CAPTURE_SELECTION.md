# Controlled capture selection

Tracked by uibcdf/recorda-lab#8, using the standalone policy in uibcdf/recorda#11.
Read Recorda devguide/CAPTURE_SELECTION.md for provisional API and limits.

run_selection.py calls the unchanged analyze/summarize/sample_count consumers.
The independent dummy computes population mean 2.5 and variance 1.25 for [1,2,3,4].
Minimal selects two scientific operations and omits payload groups; detailed
retains safe references and inspection calls. No scientific body is changed.

Run `python experiments/run_selection.py /tmp/new-selection-trial` for three
repetitions with 16 inspections each. A fresh directory retains input, native
result, success/failure journals and acceptance.json with raw wall/CPU time,
bytes, events, fsync calls and adapter counts. Timing includes start, calls, stop
and inspection, in fixed mode order. No universal speed ratio is asserted.

The fifth notebook uses start/stop across eight actual kernel cells. It compares
8 inspections: minimal has 2 operations and 6 events/fsyncs; detailed has 10
operations and 32 events/fsyncs. Native scientific output agrees in both modes.
Selected dummy failures stay failed; active inspection before stop is incomplete
and exclusion counts remain unknown until a complete terminal marker is visible.

Minimal capture loses native input/output dependencies, explicitly omitted in
metadata. Excluded invocation counts do not certify completed work, failure
coverage or uninstrumented calls. The producer-free reader test imports Recorda
and stdlib only. No replay, public support or published scientific closure is
claimed. Read devguide/evidence/capture_selection_linux_py314.json for actual
qualification. The independent dummy remains version 0.0.0 and dependency-free.
