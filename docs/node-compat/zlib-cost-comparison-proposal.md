# Proposed bounded codec cost comparison

This is a source-based engineering proposal. No new codec, bundle, component,
performance run or public API is implemented by this document. The actual350
six-sync validation remains separate from operational admission.

The [existing adapter audit](../../tests/node-compat/foundation-zlib/README.md#inspected-sources-and-existing-tests)
shows that pinned Jco delegates zlib to the nonstandard `jco:node/zlib@0.1.0`
host service. That adapter cannot supply a portable guest comparison under this
profile's selected WASI interfaces. It must not be represented as an existing
portable JavaScript implementation.

The installed tool tree contains **fflate0.8.3**. Its inspected browser ESM
source supplies the following possible finite guest comparand. The
[local source ledger](zlib-cost-comparison-source-inputs.json) pins package,
implementation, declarations, MIT license and existing package lock. Presence
as a tooling dependency establishes neither guest compatibility nor performance.

| Bounded profile operation | Proposed browser ESM function |
| --- | --- |
| `deflateSync` | `zlibSync` |
| `inflateSync` | `unzlibSync` |
| `gzipSync` | `gzipSync` with internal `mtime:0` |
| `gunzipSync` | `gunzipSync` |
| `deflateRawSync` | `deflateSync` |
| `inflateRawSync` | `inflateSync` |

Select the explicit browser entry. Package-root resolution selects a different
Node entry under Node conditions. Browser source also contains asynchronous
Worker/Blob code; final module graph, generated bundle and actual initialization
must prove that only the selected synchronous implementation is used. The gzip
header helper calls Date.now unless mtime is zero, so deterministic mtime zero
is required. The intended emitted component imports are empty; that is a gate,
not an observation. No worker, entropy, clock or custom host service is allowed.
Preserve the MIT notice with any future bundled code.

Use actual, independently reviewed350 engines and genuine metadata throughout:

1. Compare registered native six-sync operations with the selected bundled
   JavaScript provider on the same normal zlib-ON engine, same Buffer facade,
   fixtures, result consumption, public scalar ABI and bundler version.
2. Measure the identical JavaScript bundle on actual zlib-ON and zlib-OFF
   engines to report the cost of an unused installation. Keep its component
   size, startup and RSS evidence distinct from the provider comparison.
3. Keep Node22.14 as an external correctness oracle. Its native host codec is
   not a portable-component performance arm. Historical Jco host delegation is
   not an allowed performance arm either.

Before timing, publish a finite fixture manifest covering all six operations,
empty/small/large inputs and deterministic compressible/incompressible data.
Use only valid single-member, no-dictionary streams within the common domain;
all native inputs must fit1MiB and outputs16MiB. Validate full decoded bytes,
cross-decode both encoders with pinned Node and record compressed lengths.
Encoded byte identity across implementations or codec versions is not required.
A valid-input benchmark does not establish fflate's malformed-data, output-limit,
constructor, option or Node error semantics. It does not add a public fallback.
Account explicitly for input staging, output copying, backing-buffer ownership
and any facade work in the selected comparison.

Reuse the owned-process collector and actual-artifact admission mechanisms.
Require fresh source/runtime authority and a review of physical packaging
closure; the native767-tool producer list is not that closure. Keep full proofs
in the parent and bounded hash-authenticated descriptors in measured workers.
Bind scalar types to actual WIT/declarations and build descriptors from real
oracles before issuing authority, retaining the setup-type regression.

Record final component bytes, compile-and-binding-load, instantiate, first
export, operational whole-worker time, public RSS/maxRSS and operation samples.
Use fresh process repetitions, explicit order, unchanged per-case work and
calibrated shared iteration counts with unclipped deadlines. Persist raw public
returns before assertions. State exactly whether full byte validation/checksum
work is inside timing and include common construction/copy/consume controls;
never subtract controls into an invented isolated codec time. Report logical
uncompressed-byte throughput separately from compressed input/output lengths;
empty cases use operations per second. Raw medians/ranges and counterexamples
must accompany any strategy decision. No result currently supports a codec
speed, memory or size advantage.

Outstanding decisions are the exact finite cases and sample budgets, shared
facade/copy contract, validity of the browser-only bundle in a real component,
and the later operational/release evidence contract. Implement and validate
those before authorizing any measurements or changing the released profile.
