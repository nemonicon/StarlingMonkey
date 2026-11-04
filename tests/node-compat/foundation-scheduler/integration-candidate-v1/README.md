# Private scheduler integration candidate — source only

This is an **unapplied proposal**, not a native engine or compatibility result.
The queue/event-loop/Engine/embedding v2 sources and the v3 diagnostic passed
separate [Release SDK syntax checks](../taskqueue-owner-v3-syntax-v1/results.json).
There has been no engine build, component, runtime ordering, import, GC,
performance or reset/cancellation acceptance for this scheduler.

[build-engine-layer.UNAPPLIED.patch](build-engine-layer.UNAPPLIED.patch) and its
[complete proposed recipe](source/tests/node-compat/build-engine.sh) extend the
actual current recipe SHA `354cbc8c5317bf14f022fd14a9687e382b99c2141135629b56bb541ef6308754`.
The live recipe remains unchanged. Root must review the recipe, native patch and
new admission policy together before applying anything.

The [policy](policy.json) fixes all **306** intended native input hashes: the
304 actual frozen v11 inputs, five existing-file changes, and two new queue
sources. [layer-policy.py](layer-policy.py) accepts only that exact set and the
seven explicit before/after pairs; it rejects missing/duplicate/extra inputs.
The producer pins helper/policy digests before building and checks them again
before publishing metadata. It retains existing full input pre/post capture,
Rust lock, OpenSSL source, dependency, compiler and componentizer checks.

The old strict-v3 and protected-v2 source dictionaries and all original ABI,
BigInt, entropy and strict-boundary patch guards are preserved as exact ancestry.
A new source-policy version is **always** reported when these source bytes are
installed, even with the private feature OFF. The helper resolves only the
seven reviewed pairs, verifies each old expectation against its literal before
hash, and publishes current source hashes under distinct strict/protected
versions. It never labels new engine/CMake bytes as an unchanged old policy.
Historical parentSourcePolicy records contain source ancestry, not fabricated
current compile commands. The safe then-getter counterexample and other strict
policy limits are unchanged.

For repeated builds, an embedding with the **exact** known layered digest is
reversed to the known strict baseline before replaying all unchanged SHA354
embedding patch guards. The new boundary patch is then applied and checked.
Unknown embedding bytes still fail. New `.private-ticks-v1-0/1` namespaces isolate
source/build/artifact paths from the old recipe. Existing no-overwrite artifact
checks remain. The proposed recipe supports Release and Release-GC only.

`NODE_COMPAT_INTERNAL_TICKS` defaults OFF and is validated as 0/1. The already
reviewed native CMake patch selects the new runtime TU only when ON and carries
its macro through extension_api. The producer explicitly requests ON/OFF,
reads CMakeCache, and checks **actual `-c` compiler commands**, rejecting syntax
commands as build evidence. It requires the macro consistently across all
repository builtin/runtime and external embedding TUs, actual Engine/event-loop/
registrar commands, and exactly one queue TU when ON versus none when OFF.
No new flag observation or CMake result exists yet; these are producer checks
that must pass on future builds, not a fabricated receipt.

[admission-plan.json](admission-plan.json) is a required root-owned follow-up.
The current selector correctly rejects these new policy versions. The old
SHA354/version branch must stay exact; a new finite branch must pin the new
recipe/helper/policy and current/parent maps. No new Node module/export manifest
is added. In particular, this does not admit public process, its aliases, an
application nextTick global, ALS, or custom host services.

The [ordinary component protocol](validation-plan.json) names actual existing
harness/packager APIs, finite diagnostic guest modules, WIT, retained/fresh host
calls, imports, limits and regression gates. The production recipe does not
quietly include a test module. A **separate private diagnostic producer** remains
to be implemented; it must add the exact two additional test inputs and their
actual target/flags to its own full receipt. Its proposed
[CMake include](diagnostic-private.UNAPPLIED.cmake) selects the reviewed v3 source,
never historical v2. Raw componentize accesses those explicit test IDs; production
bundler admission remains unchanged.

Two coverage decisions are explicit rather than hidden. Stock ComponentizeJS
has no claimed public custom-initializer option: the proposed controlled test
would append the pinned initializer IIFE through its actual spliceBindings
`jsBindings` result, with a separate process-local/pinned receipt. A legacy
script cannot statically import the private module; dynamic import alone would
only prove Promise-job ordering. An independent classic-initial capture harness
is still required. Neither is claimed executed or complete.

**Reset remains OPEN.** Idle checks and an empty tick FIFO do not establish safe
Engine reset, cancellation, request teardown or post-fatal reuse. Two actual
native tasks currently assert that cancellation is unreachable. No reset-in-
progress/cancellation-owner redesign is part of this candidate. Application
initialization/deployed/task boundaries, full Promise behavior and future ALS
resource capture remain as described in the unchanged v2 packet.

[checks.json](checks.json) distinguishes source parsing/applicability and checks
against actual old compiler observations from future build/runtime evidence.
[The source receipt](source-receipt.json) and [index](index.json) pin this proposal.
