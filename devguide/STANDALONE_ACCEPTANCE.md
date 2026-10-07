# Original laboratory acceptance — 2026-10-07

`uibcdf/recorda-lab#1` and `uibcdf/recorda#1` are resolved against their original
experimental acceptance criteria. The independent dummy, experimental consumers,
fresh artifact reports and bounded real SciPy/native Sabueso follow-ons provide
the required evidence. The core's [criterion matrix](https://github.com/uibcdf/recorda/blob/main/devguide/STANDALONE_ACCEPTANCE.md)
records recording guarantees; [archive/controlled_laboratory.md](archive/controlled_laboratory.md)
preserves the laboratory proposal and historical progress.

| Laboratory criterion | Checked evidence |
| --- | --- |
| Independent deterministic dummy and native result | Dependency-free `recorda_lab` remains 0.0.0; both original runners verify count 4, mean 2.5 and population variance 1.25. |
| Success, actual exception, hard exit, inactive calls and parent identities | `test_experiment.py` and `test_activation_experiment.py` execute both original five-scenario runners. |
| Safe omissions, native references and declared coverage | Runner assertions check sensitive/opaque omissions, native reference identity and unwrapped-call gaps. |
| Fresh retained fixture, native result, journals and checked report | Fresh destinations retain both five-scenario artifact sets; tests reject destination reuse. |
| Inspection without scientific producers | An isolated `-I -S` reader receives only Recorda and reads all ten new journals; scientific and support packages are unavailable. Semantic reference readers have their separately tested required support closure. |
| Real external-library and Sabueso follow-ons | SciPy fitting/multi-step OLS and native Sabueso source/diagnostic cases check independent native facts, attempt history, filtering, artifact loss and interrupted work. |

The byte-identical paired [consolidation receipt](evidence/standalone_acceptance_consolidation.json)
retains 75 fresh installed core guards and 26 fresh installed Lab cases, both
original runner reports and producer-free inspection. Published pytest-receptor
1.1.0 was used. The audit matches 67 qualified Lab files, 15 current/installed
Recorda runtime files and 394 installed Sabueso wheel members. Dummy/scientific
source, package metadata, fixtures, notebooks and workflow default remain unchanged.

Existing complete evidence retains its own source scope: Lab
`a0376799c25c6b650ffa79aa6e4012601892d24c` with Recorda
`48a6c9a0630027f0f2c3d8d82215de8e27764913` and clean source-built Sabueso
`68dac8f8bfc35944f5b6dd59aca8cb2a2819388d` passed 380 local tests/four historical
Sabueso skips, seven notebooks/55 cells and 14 kernel-fault cells.
[Native-pair CI](https://github.com/uibcdf/recorda-lab/actions/runs/37584430143)
passed all 13 jobs, with 47 native passes per Python 3.11–3.14 lane. Current-core
development verifier `9228c84f78221442a4ceb0cfbc45887a919d8367` has unchanged
runtime bytes and separate 331-source/331-installed checks plus
[11 passing CI jobs](https://github.com/uibcdf/recorda/actions/runs/37587276559).
Published gh-run-receptor 1.2.0 reinspected both runs successfully. The new 101
targeted passes are not a merged rerun of those complete qualifications.

API/schema remain provisional. Human usability, live-source completeness,
public distribution/OS/coverage, automatic capture, shared integration and replay
have separate gates. Core engineering work remains Recorda #3/#4/#6; a new
scientific question needs its own Lab issue and independent oracle. The original
coordination issues are complete and are not an indefinite laboratory backlog.
