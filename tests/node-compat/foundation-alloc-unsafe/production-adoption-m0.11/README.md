# Bounded m0.11 adoption: accepted v11

The [v11 checkpoint](../../milestones/foundations-v11/README.md) is accepted after
all required source, engine, release, GC, focused and both-host HTTP gates. The
[independent receipt](v11-acceptance-receipt.json) records 1,746 rehashed copied
files, 33 full reports, 304 native inputs and three current engines. Known Node
deviations remain explicit; the broader roadmap is unfinished. The initial
source receipt and preparation files below retain their historical states.

The reviewed [second integration packet](../production-candidate-m0.11-v2/README.md)
was applied coherently to the live worktree. Its immutable packet still describes
its earlier unapplied state. The [adoption receipt](source-receipt.json) records
the actual application, all 11 before/after hashes, four changed native inputs
and 300 unchanged native inputs. The protected abort-listener source, build
recipe, registration, native Buffer kernel and selected host capability policy
are unchanged.

Root and an independent reviewer verified all 2,404 packet entries and the exact
baseline before application. All eight generated factory checks and all 328
module-admission checks pass after application. These are source/build-admission
checks, not production guest validation.

The only allocation expression change replaces a secondary facade call with
`tagTrusted(new U8(unsafeTrunc(length)))`. Existing primary validation, 16 MiB
limit, truncation, zeroed independent storage, branding, backing/view rules and
finite export/refusal surface remain the selected contract. The selected core
version is `sm-node-22.14.0-m0.11`, with
`zeroed-no-pool-direct-u8-v1` allocation policy. A secondary mutable Number hook
difference remains explicit and outside the declared supported domain.

Fresh ordinary Release OFF, RuntimeOnly and existing Release GC-stress builds,
full module/core/allocator/strict/protected-listener regressions, final imports
and the joint HTTP-v11 artifact on both stock target hosts now pass. New
versioned harnesses preserve the historical v10 runners/results.
[Harness preparation](release-harness-preparation.json) records the original
source-only state; [release results](release-gate-results.json) record execution.

The [v10 parent](../../milestones/foundations-v10/README.md) remains unchanged.
Fresh v11 tests confirm its returned-object `then` getter and disposal-symbol
counterexamples remain known limitations. No Node-wide callback-return,
process, ALS or HTTP reuse claim follows from this allocation change.

Private timing results motivate evaluating the simpler expression, but do not
measure this rebased production engine. Higher candidate peak RSS in 29/30
comparisons, higher observed capacity in 4/30, an 8,513-byte larger minimal
snapshot, slower/reversing controls and n=2 independent processes remain
mandatory counterevidence. No performance claim is transferred here.

See the repository [progress tracker](../../../../progress.md) for the active
roadmap and outstanding work.
