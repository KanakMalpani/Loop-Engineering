# LoopBench validity test (deliverable B): pass criterion, fixed before any run

Committed before any benchmark run. Do not edit after results exist.

- Set: the 10 loops in `loops/` (5 GOOD, 5 BAD; one-line note per loop in `loops/NOTES.md` and each file header).
- Suite: `suite-repair`, seeds `0,1,2,3,4`, real model (not the mock LLM). Model, provider and key are recorded in the run log.
- Score: the suite's primary LoopBench score per loop as reported in `results.json`.
- Runs: each loop is run 3 independent times.
- PASS only if, in every one of the 3 runs, min(score of GOOD loops) > max(score of BAD loops). Any tie or overlap in any run is a FAIL.
- On FAIL: no tuning of the benchmark or loops. Write a redesign or a recommendation to drop the benchmark.
