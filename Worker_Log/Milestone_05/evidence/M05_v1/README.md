# M05 frozen technical evidence

Scientific source: `424a859732b77b2f91cd03b12bb3f0b8adf3f541`, child branch
`m05-colab-workflows` of M04 `fab6388b041acc4362f30b5ff7d3789a33fc536f`.
These results were produced in the managed CPU workspace on 2026-10-05 UTC,
not on Colab. CPU locks and model bytes are unchanged.

`archives.json` binds compressed archives. Each successful archive contains its
complete stopped attempt, including a `.evidence.json` seal verified by
`atm_mlmm.evidence.verify_evidence`. Four dense attempts retain source/model
assets, prepared workers, full raw-force samples, States/checkpoints and exchange
phase/RNG/history journals. The CPU reference retains 108 actual-MACE ABFE/RBFE
both-map inputs, cap/real projection, changed coordinates/graphs, all-real ML
forces, three FD step sizes and equivalent CPU startup/steady timings. No TPU
hardware result exists. Extract these trusted archives into unused local folders;
verify seals before executable loading. Keep mounted storage export-only.

The fixed-window attempts have nine samples/18 sampling steps and six thermal
preparation steps each. Exchange attempts have four complete rounds, eight
unique samples, two walkers, seed711 and two integration steps per round/worker.
Command logs/resource/exit JSON and the preflight record are adjacent. Their
prepared exports predate the TPU-only extension: they retain the exact bundled
source they used. RBFE exchange executed that bundled source explicitly; physical,
geometry, ATM and controller code match the frozen scientific implementation.
A different source/profile must not silently reuse old checkpoints.

`dense-numerical-*.json` are passing independent energy/full-force and cap-parent,
ligand/solvent FD records with full coordinates. `failed-dense-0.json` and
`failed-denser-fixture-v2.tar.gz` preserve the original failed representation.
`stock-six-atom-probe.json` records the reduced entirely stock OpenMM reproducer:
Reference real-space periodic contribution changes at a tiny negative water-H
coordinate; reciprocal contribution is unchanged. This is examined/reported,
not repaired. General runtime geometry and OpenMM remain unchanged. The input-only
representation is defined in the proposed scientific amendment.

Full-suite logs/JUnit/resource summary, notebook schema tooling inventory and
focused RED/GREEN records accompany the submission. Larger temporary test trees
and earlier failed reference attempts remain in `/workspace/m05-evidence`.
No new QM, liquid-density, equilibration, affinity, protein, GPU or production
qualification follows from these bounded technical records.
