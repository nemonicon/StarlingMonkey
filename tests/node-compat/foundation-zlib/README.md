# Native compression preparation

This is an **uninstalled native candidate**, not a supported `node:zlib`
module. No production source, CMake option, export manifest or host capability
is enabled by these files. The [runtime inventory](inventory.node-v22.14.0.json)
pins Node **v22.14.0**, revision
`5d2feb257bcee090e57900eb51720171a6aa92f3`: 39 named exports plus default.
Every candidate export remains deferred. Constants and reverse error-code maps
are inventoried with their real number/string types and descriptors.

## Inspected sources and existing tests

[Source ledger](source-ledger.json) records selected official Node and Jco
files, exact revisions, URLs, byte lengths and hashes. Node's JS layer uses
`internalBinding('zlib')`, classic Transform, Buffer and async hooks; its native
implementation is `src/node_zlib.cc`. Ordinary convenience, empty, dictionary,
CRC, concatenated-member, trailing-data, limit and truncation tests inform the
required future suite. Those upstream suites have **not** been run here.

Jco **1.40.0**'s `createZlibBuiltin` selects jco-std **0.10.0**'s Node24 adapter.
The installed `zlib.js` imports **`jco:node/zlib@0.1.0`**, and `createZlib(host)`
delegates compression, CRC and engine resources to that host. Its tests
explicitly map a Node provider or deny provider and validate the custom import.
That is a nonstandard host adapter, outside this profile. Its Node24 Zstd
exports also do not belong in the pinned Node22 surface. No such service or
replacement host is proposed. [Pinned Jco test](https://github.com/bytecodealliance/jco/blob/42cd21e0a31362dbb519f4749f3689bba0fbdb1d/packages/jco/test/node/zlib.js).

The actual checkout's existing native classes are guest zlib, but source
inspection blocks direct reuse:

- `deflate_chunk` and `inflate_chunk` retain `z_stream::next_in` from
  `value_to_buffer` across `JS_NewUint8Array` and controller enqueue. Rooting
  the chunk does not pin movable byte storage. The generic helper also does
  not enforce shared/resizable/detached policy.
- Both constructors pass an unchecked `JS_NewObjectForConstructor` result to
  `create`. Their classes use `DefaultClassPolicy`; allocated z_stream structs
  have no finalizer. Normal flush frees the scratch buffer and calls End but
  does not free that struct, while error/cancel and partial construction need
  owned cleanup. Release slots are not cleared after normal cleanup.
- `inflate_chunk` has an empty branch for unexpected zlib status, and flush's
  `avail_in == 0` test is not proof of `Z_STREAM_END`. Trailing members,
  checksums, truncated input, progress and output expansion need explicit
  policies. Enqueueing fixed chunks alone does not bound aggregate output.
- Native Transform cancel/abort/error paths do not provide a codec-specific
  close hook. Merely adding a finalizer would not provide prompt deterministic
  cancellation cleanup.

No known-invalid receiver, compression-global operation or unsafe existing
native path was executed for this audit. See the [local source receipt](local-source-receipt.json)
for exact files and symbols. Existing stream tests remain separate from this
new kernel's evidence.

## Bounded one-shot candidate

[bounded-zlib.template.h](bounded-zlib.template.h) is native code with no JS
API, callback, borrowed guest pointer, resource handle or host call. The
algorithm uses zlib default level/strategy/memory settings, window bits
15/31/-15, at most **1 MiB input** and **16 MiB aggregate output**, and a 16 KiB
scratch buffer. Native output grows fallibly within that cap. End runs through
RAII on every initialized success or error path, including output-limit
failure. Native bytes use malloc/realloc/free consistently and are never
adopted into SpiderMonkey.

The output cap bounds retained result bytes, not total peak memory. A codec
call can produce another scratch chunk before the limit check; zlib also owns
its internal state/window allocations. Realloc can transiently need old and new
storage, and the future wrapper adds input staging plus the final JS-owned
result during the copy. Those costs need actual target measurement.

Decoding requires exactly one complete member with no trailing bytes. It
explicitly distinguishes truncation, dictionary demand, checksum/data failure,
limits, memory failure and internal failure. **This is narrower than Node**:
gunzip accepts concatenated members and zero padding; zlib/raw trailing-byte
behavior also differs. These statuses have no public JS error mapping yet.
The driver suppresses all partial bytes on failure. The template retains
partial native output only until its normal owner is destroyed.

A future JSAPI wrapper must root and validate a fixed, attached, unshared
BufferSource, allocate native staging before borrowing, reacquire the pointer
inside a no-GC copy, then leave that borrow before running this kernel. It must
allocate the final rooted JS-owned Uint8Array and copy once into it, freeing
native staging/output through their own owners. Buffer result wrapping, string
input, observable options, error codes, constructor/callback semantics, GC and
allocation limits need their own gates. No allocator-transfer or zero-copy
claim is made. The first proposed public operations are six bounded synchronous
deflate/gzip/raw functions; streaming and callback methods remain separate.

## Executed evidence and remaining gates

The retained [first host report](host-template-results.json) passes 66 ordinary
cases, but its encode inputs all fit one output scratch chunk. Independent
review identified that coverage gap. The separate [v2 host report](host-v2/results.json)
passes **86 cases**, including deterministic incompressible encode output over
262 KiB in all three formats, Node-produced input decoding, host-produced
output accepted by Node, full 1 MiB input and one byte over, exact 16 MiB decoded
output and one byte over, zero output limits, truncation, zlib/gzip checksum
errors and dictionary refusal. Concatenated gzip members and zero padding are
explicit profile-refusal versus Node-acceptance controls. Earlier evidence is
unchanged. Encoded byte identity across zlib versions is not assumed.

V2 records actual compiler version, compile arguments, binary hash,
`zlibVersion()` and dynamic linkage. Node22 uses
`1.3.0.1-motley-82a5fec`; this host uses **1.2.12** and the target SpiderMonkey
header is **1.3.1**. The macOS library identity is its recorded dyld install name
and version, not an individual hash of bytes in the system shared cache. These
host tests do not substitute for target execution.

[Actual SDK30/SM147 syntax](sdk-syntax-results.json) passes using the frozen
v7 Buffer translation unit's compiler flags and exact compilation-database
hash. **It is syntax only:** no new engine or component has linked this code,
and there is no emitted-import, GC, allocation-exhaustion, streaming, lifecycle,
target-host, throughput or component-size result. No stopped diagnostic branch
is used.

Next gates are an independently reviewed JSAPI ownership wrapper and real
component with zero final imports, Node differential and negative initialization
cases, retained successful calls, fresh Wasmtime execution, limits and ordinary
moving-GC checks, followed by minimal size/startup/memory/throughput comparison.
Native stream reuse additionally needs deterministic close/cancel integration
and backpressure/error/flush/member-boundary tests. Brotli remains excluded
until its separate empirical size and demand decision.

Reproduce source retrieval with `python3 audit-sources.py`; execute
`check-native-template.mjs` with pinned Node22 and run `python3
check-sdk-syntax.py`. Default outputs are in
`/tmp/starling-node-compat/zlib-template-v1`; choose a fresh
`NODE_COMPAT_ZLIB_OUTPUT` for another run. Accepted reports are never silently
replaced. The initial source retrieval included a nonexistent `src/node_zlib.h`
path and stopped before producing a ledger; the corrected finite source list
pins the actual implementation and all twenty successful downloads.

V2 is reproduced with pinned Node22 and
`host-v2/check-native-template.mjs`; its default output is
`/tmp/starling-node-compat/zlib-template-v2`. [Evidence index](evidence-index.json)
preserves the initial source/host/syntax stage, [v2 receipt](host-v2/evidence-index.json)
pins its later source/report/raw-output hashes, and [license supplement](license-supplement.json)
retains upstream notices without rewriting the earlier receipt.
