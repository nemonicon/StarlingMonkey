# Scheduler v3 diagnostic guard — unapplied

This small revision preserves the [frozen v2 packet](../taskqueue-owner-v2/index.json)
and its later [five-TU syntax result](../taskqueue-owner-v2-syntax-v1/results.json).
It changes only the **diagnostic** `scheduleTask`: callable validation is followed
by the same actual `JS::GetObjectRealmOrNull` / `JS::GetCurrentRealmOrNull` check
already used by the private queue, before limits/private Array creation. A
foreign or unknown callback-object realm throws a TypeError with own
`ERR_SM_NODE_UNSUPPORTED`. Dispatch therefore stays in the accepted realm; no
cross-realm argument-wrapping or security/isolation claim is made.

The [diff](diagnostic-same-realm.UNAPPLIED.patch),
[complete new diagnostic source](test-extension.UNCOMPILED.cpp), and
[source receipt](source-receipt.json) are isolated from live native code and v2.
The native queue/Engine/embedding patches and all reset limitations are unchanged.
There is no live apply, new engine, guest, foreign-callback guest probe, public
process/global/ALS API, custom host service or additional WASI import.

**This v3 source has not yet been syntax checked.** Root source review precedes
that step; guest execution additionally requires an approved new engine and
actual finite test-module installation. v2's successful syntax does not certify
v3 compilation, CMake linkage, initialization or observable scheduling behavior.
