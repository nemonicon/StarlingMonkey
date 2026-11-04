# Isolated readable iteration stage

This adds actual `ReadableStream.from`, `values` and `@@asyncIterator` to the
preserved [codec/guard candidate](../candidate/README.md). It is uninstalled
and changes no production files. The factory's native stream constructor and
prototype identities remain unchanged; the fixture restores all eight static
and prototype descriptors after each call. `values` and `@@asyncIterator` are
the same function. Compression, WDC.signal and the earlier DataView guard
remain deferred in this stage.

The [algorithms](algorithms.mjs) capture public native reader/controller methods
and intrinsic promise operations. `from` selects the async protocol first,
uses Node22's async-generator bridge for sync iterables, captures the async
iterator's next method, and uses highWaterMark zero to avoid eager collection
or prefetch. Async iterator `value` promises remain values; sync yielded
promises are awaited by the bridge, matching the pinned Node behavior.
Cancellation obtains and invokes the iterator's return method with the original
reason and validates its awaited result.

`values` checks the ordinary native receiver before options, obtains a default
reader and serializes next/return operations. Close and read failure release
the lock; return cancels with its value and releases the lock before awaiting
cancellation, or only releases it when preventCancel is true. Repeated done
calls and concurrent operations follow the recorded Node results. This is not
an async generator with an implicit cancellation policy.

The ordinary receiver domain excludes Proxy/cross-realm claims. The native
prototype is rejected before its getter is delegated. Original read errors and
cancel-rejection objects retain identity. Intrinsic isolation is limited to the
captured operations tested: native read/cancel/release, controller enqueue/close,
Promise.resolve, global Promise/TypeError, Reflect.apply and Object.setPrototypeOf.
The async-from-sync generator bridge can observe Promise.prototype.then during
promise assimilation, as the actual Node22 bridge does; no immunity to all
promise/protocol mutation is claimed.

The algorithms retain one reader and serialized pending promises per iterator.
They perform one bounded source operation at a time and do not collect an
iterable into memory. There is no total lifetime, source-size or outstanding
caller-operation cap: callers can retain arbitrary chunks or queue arbitrary
operations, just as with the underlying stream. Host capabilities are absent.

[Node results](node-results.json) and [host checks](host-results.json) cover 67
cases: sync/async protocols, malformed results, next capture, yielding promised
values, no eager pull, serialized pulls, cancel/rejection/finally behavior,
option/getter/error order, concurrent next/return, early return, lock lifetime,
preventCancel, for-await break and iterator descriptors. The selected error
codes/types match Node; full messages/stacks and arbitrary scheduling interleave
are outside this recorded comparison.

[Component results](component-results.json) contain the exact component SHA,
all 285 immutable native input hashes, candidate source hashes, final zero-import
audit and packager provenance. All 67 cases pass twice in Jco-hosted Wasm and
once in fresh stock Wasmtime42.0.1. Both calls restore the descriptors and retain
constructor/iterator identities; the captured-operation test invokes zero
replacement functions. This is ordinary public-API proof, with no compression,
raw-memory, unsafe receiver, allocation fault or new engine build.

The earlier 56/66-case receipts remain in external
`foundations-v6/stream-web-iteration-v1` and `-v2`. The final v3 adds an inherited
Error.prototype.code getter/setter oracle: all selected errors define their own
code without reading or writing the inherited property. [Source pins](source-pins.json) and
[Node MIT attribution](LICENSE.node) cover the adapted source algorithms.

```sh
/path/to/node-v22.14.0 tests/node-compat/foundation-stream-web/iteration/node-oracle.mjs
/path/to/node-v22.14.0 tests/node-compat/foundation-stream-web/iteration/run-host.mjs
# Use the same locked-toolchain, v2 componentizer, immutable v6 OFF engine,
# source-root and Wasmtime42 environment as the preceding candidate stage.
NODE_COMPAT_STREAM_ITERATION_OUTPUT=/path/to/fresh-output \
/path/to/node-v22.14.0 tests/node-compat/foundation-stream-web/iteration/run-component.mjs
```
