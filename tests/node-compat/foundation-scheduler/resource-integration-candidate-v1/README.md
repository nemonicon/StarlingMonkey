# Scheduler resource integration draft

**Unsealed work in progress, preserved at the user's requested Git checkpoint
on 2026-11-05.** No index, independent review or acceptance exists.

The draft contains two timer/task ownership afterimages, a proposed342-source
policy and build recipe, a467-row staging plan, dormant staging code and runtime
fixtures. Preparation reports5,399 source/pure checks over822 inputs, including
four Python AST checks. These are preparation findings, not runtime evidence.

No Node, compiler, staging, build or guest action has run for this draft. The
production timer/task patch remains unapplied. Source sealing, independent
review, actual activation, native build/freezer/controller gates, packaging,
clock-import admission and runtime validation remain open. Clock capability
scope and deterministic argument-allocation-failure testing need decisions.
See [integration-plan.md](integration-plan.md) and
[progress.md](../../../../progress.md).
