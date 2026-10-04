# G09-R1 retention repair

The independent v1 review accepts the bounded design/numerics but confirms that
an exception originating inside actual integration bypasses the archive handler.
V1 worker/audit/evidence remain frozen. This repair does not change physical or
thermodynamic definitions, tolerances, model/environment assets, QM accounting,
or the partial G09/G10 scope.

1. Reproduce integration and final-State acquisition faults on actual pinned
   workers, advancing the real integrator before raising. Require the exact
   advanced State/checkpoint, original error and explicit attempted sample IDs.
2. Widen the existing try boundary to include guard, integration and final State
   acquisition. Preserve normal full-force refresh; failure capture requests
   only cached position/velocity/parameters, never failed energy/forces again.
3. Record attempted sample/walker/state/sequence/index and actual step/time.
   No accepted journal sample is manufactured for a failed step.
4. Keep strict continuation tests. Diagnostic failures showed that the old test
   compared independently minimized snapshots and different anchor centers.
   Build the uninterrupted reference from the identical exported System/State
   and seed; compare exact positions, velocities, raw values and real forces.
   Do not change numerical tolerances to hide differing initial Hamiltonians.
5. Run focused checks, full CPU suite and a new short CLI pilot. Carry the frozen
   v1 longer pilot/numerical evidence only with its original source identity.
6. Submit unused Gate_09_v2_worker/evidence and exact source to the actual same
   GPT-6.1-sol/MAX auditor for R1 closure and scoped acceptance. No full M05 claim.
