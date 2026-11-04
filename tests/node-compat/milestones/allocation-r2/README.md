# Accepted allocation-r2 milestone

This is the immutable accepted Buffer/stub and packaging-fix checkpoint before
Path and entropy changes. `results.json` records engine/component hashes and
14 copied full reports with their SHA-256 values. Its source archive is the
verified 191-file `/tmp/starling-node-compat/allocation-r2-native-freeze/source`;
those local build artifacts are not vendored binaries.

The pure component has zero imports. The same HTTP component passed three
requests on each unmodified Wasmtime 42.0.1 and official wash 2.11.0 local host.
Its five standard WASI 0.2.10 interfaces include only monotonic-clock types, no
clock operations. Selected upstream gates passed 19 adapted E2E, 15 builtin,
two ownership and nine strict-initializer cases. This checkpoint does not
include the later entropy integration or complete upstream suite.

The genuine DEBUG allocator gate covers four native Buffer allocation API
scopes and 32 recovery pairs per call. All native/GC/error checks stay inside
the guest. The public result is solely `run: func() -> s32`, because the pinned
DEBUG embedding has an independently proved 64-byte indirect-memory displacement.
The default packaging loader refuses general DEBUG components; no assertion or
allocator check is bypassed. `oom/source/` preserves the exact three reported
fixture source hashes. This is bounded allocator evidence, not engine-wide
exhaustive OOM or general DEBUG ABI support.

Historical performance observations predate the clock-errno correction and
require refreshed matched measurements. HTTP counters reset between requests;
this checkpoint does not prove same-instance HTTP reuse. Full roadmap work
remains active; see the repository execution ledger.
