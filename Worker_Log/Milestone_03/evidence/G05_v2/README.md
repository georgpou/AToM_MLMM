# Prepared-reference provenance repair evidence

This is software integrity evidence only. The source/input manifest identifies
the single production importer repair and added test. `run_check.py` records
exact commands, cwd, HEAD, timestamps, exit status and complete output in new
gzip JSON captures without overwriting earlier attempts.

RED reproduces six accepted corrupt/missing approval records. GREEN passes the
matched synthetic fixture, six required rejections and three known-number
metric checks. Full-suite capture has 292 passes and the two genuine
missing-quantum-data failures. Analytic selection has 272 passes/22 deselected.
Synthetic records live only in temporary unit-test directories and never in
the frozen chemical reference bundle. The actual user explicitly approved the
exact plan after these runs; that decision is independently recorded. The v2
audit closes importer R1 on `3124c6d` only. Actual target quantum references and
chemical/full-G05 qualification remain pending.
