# Host facade semantic checks

The unchanged [test program](test-facade-host.mjs) ran twice in pinned Node
22.14.0 under the original 60-second owned-process monitor. Attempt 1 was
**61/64, raw 1**: sparse provider arrays, inherited frame fields and accessor
frame fields were accepted. Root hardened the provider boundary to require
dense own array elements and five own data fields. The same test then passed
**64/64, raw 0**. Both process groups were clean, stderr was empty, source
bookends matched, and original Error-related descriptors were restored.
[Summary](host-test-results.json) and both attempt directories preserve the
actual raw observations and exact executed source versions.

The test uses the actual `createStartupFacade`, Node EventEmitter, URL,
querystring, path and Buffer values, and the pinned complete startup inventory.
Its private provider calls the **original Node captureStackTrace** and maps
real V8 CallSite getters to the proposed finite records. `isEval` comes from
V8's actual `CallSite.isEval()`, including a real eval case; no filename or
stack-string inference is used. Provider internals temporarily replace
`prepareStackTrace`/`stackTraceLimit` and restore them in `finally`.

All four retained probe cases match the original Node baseline's selected
semantics, including depd's exact getStack/location functions. Further checks
cover zero/max limits and refusals, bad provider provenance, callback identity
and laziness, object/falsy throws and retries, caching/setters/reentry, hidden
CallSite construction, explicit unsupported methods and eval-origin refusal.
Factory creation made zero capture calls. No host-operation stub was called;
the actual host process environment/FS/clock/stdio provider was never used.

These are **host facade tests**, not SpiderMonkey/native/guest proof. Node's
existing behavior for ordinary `new Error()` cannot prove automatic guest
Error-constructor integration; the measured cases use explicit
`Error.captureStackTrace` targets. The v1 native prototype lacks eval
provenance, and the new guest SavedFrame getter/library remains a separate
uncompiled dependency. Full engine/guest and unchanged Next.js regressions
remain pending.

The first source-curation attempt refused Root's already-hardened file hashes
after the completed first run. No changed source was copied as old evidence.
The two old source versions were reconstructed by reversing only the `sites`
replacement and matched byte-for-byte to the actual before/final hashes.
That provenance is recorded in attempt 1's manifest; actual run streams and
terminals are direct copies.
