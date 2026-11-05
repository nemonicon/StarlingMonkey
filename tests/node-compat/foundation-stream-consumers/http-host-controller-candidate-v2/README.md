Thin source correction of the held generic Root controller. No host/stage action.

The v1 monitor omitted an observed nonleader's group if its leader was never
observed. It also omitted a known PID's current group after group migration.
Either could falsely report complete cleanup. The original source remains sealed.

`group_model` now accounts for all stored groups and every current group of every
known PID. Unknown ownership or changed identity is never silently adopted for
signalling, and its live group blocks completion. `remainingObservedPids` separately
blocks final acceptance. Only captured owned sessions with a matching current
process identity remain eligible for signalling. A migrated or unknown group may
require external resolution; this controller reports incomplete cleanup rather
than claiming success or signalling an unproved group.

Seven reversible source edits preserve the actual generic API, HTTP phase guard,
2400-second maximum, source authentication and before/after checks. The caller for
isolated GC staging must separately select this new source index. Native metadata,
guest code, host versions and capability imports are unchanged.

All35 checks pass: original identity counterexamples, both newly exposed M1 cases,
reused PID in another group, and three actual benign Python sessions (normal,
bounded timeout, parent exit leaving an observed detached descendant). Full raw
test streams and terminal descriptors are retained. None is a host or source-stage
result. The inherited scratch prefix still contains `v1`; actual source module and
code provenance are this v2 packet, not a relocated old action.

Importing launches nothing. No Root phase, config, peer or host/controller authority
is supplied. Independent source review and separately issued actual phases remain
required. No server, HTTP request, Git clone, native build, component, guest, key or
GC workload has run. Original HOLDs and packets are preserved.
