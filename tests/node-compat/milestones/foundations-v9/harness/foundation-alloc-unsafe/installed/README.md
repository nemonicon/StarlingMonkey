# Installed m0.8 allocator/helper gate

The actual v8 OFF engine passes **10 Node22 differential groups**, **5 profile
groups**, and the traced readable-stream `BufferList.concat/_getBuffer` allocation
paths. Retained Jco calls `[1,2]` and fresh stock Wasmtime42 call1 pass with **zero
host imports**. This fixture imports real native `node:buffer` and
`node:child_process`; it does not bundle a facade/reference kernel, inject an
allocator, or replace `Buffer.allocUnsafe`.

[The full report](./native-component-results.json) records engine
`e16c19fc567753517d7b61b65372dd7dc86de8f839e7acab959b5cf5eaf294c9`, all293
frozen inputs checked before/after, recognized m0.8 v2 core hashes, Node22.14,
audited ComponentizeJS0.23/Jco1.40 packaging, pinned adapter, and Wasmtime42 binary
identity. Component
`a215bca08da50db641b24ce928ec94d775e31077ac1f2b8cf490c9efcadd324c` exports only
`run: func() -> string`. Its12,124,815B size includes correctness fixtures and
establishes no production size or performance result.

## Contract exercised

Only the bounded `allocUnsafe` static operation advances from the original core:
finite primitive nonnegative numbers up to16MiB, raw size validated before
truncation, fresh zeroed owned Buffer storage, exact backing at offset0, and no
pool. Fractional, signed-zero, type/range, call/new/bind/derived/new-target,
independent storage, view sharing, backing offsets and meaningful error types/codes
are checked. No initial Node unsafe contents are read; every differential byte
vector initializes its entire visible span first.

The fixture checks installed canonical/bare namespace caching, default/named and
global identities, static CommonJS lowering, safe namespace inspection/await, and
snapshot-owned Buffer/shared subarray identity and mutation across retained calls.
The first bare aliases load during deployed execution. Public `Buffer.alloc`,
`Math.trunc` and `Reflect.apply` are briefly replaced and restored in a capture
test; the installed `allocUnsafe` function stays unchanged throughout.

All91 existing unsupported own Buffer prototype functions, five deferred statics,
the legacy constructor, nine import-only Buffer exports, nine child-process
exports and five ChildProcess methods are checked on call and construction:
**240 refusals per component call**. Each remains an original Error with own
enumerable/writable/configurable `code`, `module`, `operation` and m0.8 `profile`
data fields while ambient Error/defineProperty and inherited field getters/setters
throw. Those hooks run zero times and restore in `finally`.

Poison windows execute only synchronous pure JavaScript refusal constructors or
invalid-size facade validation. They collect errors and inspect/assert only after
restoration. No native codec/error oracle, real Node child-process capability,
logging or await runs under inherited-field poison. Ordinary Node allocation
oracles run separately. These checks provide no genuine OOM or allocator-fault
evidence.

Eleven componentization failures check invalid allocator call/new/range/raw-cap,
unawaited rejection, deferred Slow/prototype call/new and child-process call/new.
A separately selected immutable v7 engine with m0.1 still rejects both
`allocUnsafe` call/new; its own engine receipt and293 frozen inputs are verified.
No historical v6/v7 report or source control is rewritten.

## Limits and reproduction

`allocUnsafeSlow`, legacy constructors, other deferred Buffer methods and all
existing encoding/backing restrictions remain unchanged. Zeroed exact no-pool
backing, the raw16MiB cap, and detailed error text deliberately differ from Node.
Only exact four-method BufferList excerpts are used; classic Streams, abort
listeners, nextTick/ALS scheduling and remaining dependency APIs stay deferred.
This scalar test is independent of the coordinated HTTP target-host gates.

Run `run-component.mjs` with exact Node22.14 and the normal
`NODE_COMPAT_ENGINE`, `NODE_COMPAT_ENGINE_SOURCE_ROOT`, `NODE_COMPAT_TOOLCHAIN`,
`NODE_COMPAT_COMPONENTIZE_MODULE`, `NODE_COMPAT_WASMTIME` variables. The engine is
explicitly pinned to the frozen v8 OFF artifact. Optional
`NODE_COMPAT_INSTALLED_ALLOCATOR_OUTPUT` selects a fresh output directory;
`--preflight` validates source/engine/toolchain/Node oracle/bundle without
componentization. Old control paths can be supplied through
`NODE_COMPAT_ALLOCATOR_OLD_ENGINE` and `NODE_COMPAT_ALLOCATOR_OLD_SOURCE_ROOT`,
and remain pinned to the recognized immutable v7 bytes.

The original [isolated experiment](../README.md) and
[unapplied production-candidate evidence](../production-candidate/v2/README.md)
remain historical checkpoints. Their installation/status fields describe those
earlier experiments; this directory records the subsequent actual native gate.
