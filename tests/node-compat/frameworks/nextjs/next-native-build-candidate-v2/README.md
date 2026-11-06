This is the small, dormant successor of immutable build runner Source84aa.
No configure, compiler, native build, helper, original monitor, engine or guest
was invoked in its preparation. Root must issue a complete authority selecting
the exact current composition, passed frontend/generator results, embedding3,
22 public and2 private manifests. The Source count remains derived from that
composition; neither430 nor432 is cast into an old metadata schema.

The five exact runner edits are in derivation.json. Clean child environments now
set CARGO_BUILD_JOBS=1, MAKEFLAGS=-j1, CARGO_INCREMENTAL=0, CCACHE_DISABLE=1 and
SCCACHE_DISABLE=1. The existing Ninja/CMake build parallelism remains1; the new
settings also constrain nested Cargo/make and disable incremental/compiler-cache
reuse. All other environment construction is unchanged, including preservation
of HOME/home/CODEX_HOME and exclusion of inherited startup controls.

Every phase now retains the original0af terminal's signals, interruptedSignals
and remainingObservedPids arrays. The same mandatory phase_succeeded predicate
guards ordinary commands and final Ninja-command harvesting: raw inner/outer0,
both owned-clean conditions, no timeout/forced cleanup/errors and all three
arrays empty are required. A signaled command that returns0 cannot pass this
gate. No existing monitor code or context is changed or rebound.

The only CMake flag change is NODE_COMPAT_CLASSIC_STREAMS_TOWEB=ON. The plan's
Source version isV2; every other plan value, archive/support descriptor and
private-Rust policy is unchanged. The existing Root authority JSON schema/state
V1 is deliberately reused: actual entry and plan descriptors, HERE and the
worker's own file checks bind this new family rather than the original runner.
Template action slots remain null/false. Root chooses a fresh WORK path.

The v1 README documents unchanged build/copy/archive/metadata/failure behavior.
test-delta.py proves the exact whole-runner inverse and whole-plan change, tests
the actual clean environment function and strict gate, and invokes only the real
phase *publication* function with an inert fake monitor over tiny temporary DATA.
It never calls main/phase_worker, loads original utility modules, or spawns a
process. The recorded raw0-with-signals counterexample is synthetic DATA, not an
observed native command. Source is unexecuted for build/runtime purposes.
