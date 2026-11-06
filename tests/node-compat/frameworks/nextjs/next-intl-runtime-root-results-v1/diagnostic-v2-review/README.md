# Source/view diagnostic V2: retained failure

The diagnostic component constructs successfully: three raw-zero owned phases
(INIT construction, validate, WIT) and its raw-zero outer controller. It binds
engine `e7baa5a9…`, unchanged native metadata and the exact diagnostic Source
index/entry. Its whole typed return graphs and emitted 13 standard 0.2.10
interfaces are retained. No external Preview1/custom interface was introduced.

The actual ordinary runtime remains **failed**:

- Client: 11 of 24 HTTP contracts passed, exit 1; no browser success is inferred.
- Wasmtime: requested graceful SIGINT, exit 0, no forced cleanup.
- Outer controller: exit 1 with all observed owned processes gone and clean
  signal/error/timeout fields.
- Original inputs and the read-only application copy remained preserved.

The source diagnostic appears twice at `Module._compile` for the actual compat
route. The provided value is a string; its retained window includes Euro
**U+20AC / decimal 8364**. `mojibakeLiteralOffset` is -1. This observes the input
at the JS compile entrypoint; it does not establish the resulting compiled
literal semantics or explain every later Euro assertion failure.

The POST failure logs one intrinsic view observation: `Uint8Array`, byte offset
0, byte length 134. Its prototype does not equal the captured Uint8Array
prototype and the captured constructor's `hasInstance` is false; its backing
ArrayBuffer prototype does equal the captured one, with length 134. The original
Buffer unsupported error remains. This is type/branding DATA, not an
implementation fix or authorization to treat arbitrary objects as byte views.
Full cause chains, raw stdout/stderr, HTTP response bodies, statuses and hashes
remain available without reducing failures to these two observations.

`data.tar.gz` retains all selected constructor/runtime/outer text trees and exact
Source indices, plans, entries and authority records. Application, cache, XDG,
engine, adapter and component payloads are excluded; binary references retain
their hashes/sizes. No old five-runtime baseline payloads are duplicated.

Run the portable, standard-library-only DATA checker, placing output outside
this indexed family:

```sh
python3 -B check.py
```

This reader invokes no constructor, Wasmtime, browser, guest, native tool or
historic Source code. Successful DATA reconciliation leaves the original
runtime `passed:false` unchanged. Instrumentation changes function identities;
it is diagnostic evidence and provides no production, implementation, snapshot,
profile or full-Next acceptance.
