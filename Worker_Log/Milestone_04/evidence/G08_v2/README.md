# G08 v2 repair evidence

Exact tested source: `8cf2494424d796fc3fc393e25b00e05b6281a85f`.

- `admission-red.txt`: four expected failures before implementation, from the
  outside-checkout draft test file; the committed tests add serialized negatives.
- `focused.txt`: 21 G08/admission passes, 34.16 seconds.
- `full-cpu.txt`: 437 available CPU passes, 322.62 seconds; outside-checkout temp.
- `docs-check.txt`: local documentation and eight checker self-tests.
- `source-test-manifest.json`: 83 scientific files with size/SHA-256; only schema,
  analysis result construction and the new admission regression file differ from
  v1's manifest. Prior numerical evidence remains in G08_v1 and its independent
  review; none was modified or superseded by a result admission claim.
- `snapshot.json`: source, commands, outcomes and resource observation.

Frozen [v2 worker](../../Gate_08_v2_worker.md) defines scope and limitations.
