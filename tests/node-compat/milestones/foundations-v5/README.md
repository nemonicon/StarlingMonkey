# Accepted ordinary codec integration checkpoint

The11 indexed files in `results.json` preserve both exact native engines,
271 source-input receipts, the production encoder source, ordinary codec tests,
Buffer regression and the joint HTTP host tests. Earlier checkpoints remain
unchanged. The production file has no private GC/fault wrappers or hooks.

`TextEncoder.encode` now roots the converted string, computes its exact UTF8
length, allocates a GC-owned Uint8Array and writes only inside a no-GC borrow.
It removes the explicit malloc-backed staging buffer and ArrayBuffer ownership
transfer. Conversion exceptions, including Symbol TypeError, propagate correctly.
`encodeInto` roots its source, handles zero/detached/OOB destinations without
passing null empty slices to the codec, and reports documented allocation
failure. Existing Starling source coercion is retained; Node22's stricter
primitive-string source rule remains an explicit deviation.

Both OFF and runtime-only engines pass77,769 baseline assertions plus226 new
shared assertions, seven separate source-policy cases and snapshot ownership,
three retained Jco calls and fresh stock Wasmtime42 execution. OFF emits no
imports; runtime-only emits exactly secure random0.2.10. Buffer's381 string and
250 byte vectors, identities, aliases and initialization failures pass on OFF.

The same joint HTTP component passes three requests on each stock Wasmtime42.0.1
and official wash2.11.0 host. Each request validates full Buffer, Path, synchronous
Events and entropy checks, plus six first-use computed bare aliases. Exactly
six standard WASI0.2.10 interfaces are imported; the clock is type-only. Counters
remain1 per request, so HTTP instance reuse and request isolation are not proved.

A separate same-project private Release comparison motivated the change:
64-byte peakRSS fell51.64→24.58MiB and throughput rose8.8%;512KiB throughput
rose1.66x with essentially unchanged memory. Those exact observations remain
attached to their private control/candidate artifacts, not transferred to
these production engines. See [the measured pair](../../utf8-direct/README.md).

The new private allocation-failure diagnostic did not pass: its first
linearization assertion failed, and automatic review blocked the follow-up.
It remains unverified. The prior four-site Buffer allocator evidence is
separate; neither this checkpoint nor the Release/GC tests imply universal OOM
recovery. No blocked diagnostic was retried through a different access setting.

The full roadmap remains active. StringDecoder/Assert/Querystring are isolated
prototypes, Weval is being measured separately, and remaining streams,
scheduler/ALS, Node crypto/compression and optional capabilities are unfinished.
