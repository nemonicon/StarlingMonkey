# Standard HTTP transport for the native profile tests

This component carries the existing native Buffer/stub fixtures through an
explicit `wasi:http/incoming-handler@0.2.10` export. Every request runs the same
381 string and 250 byte differential vectors, native/global/CommonJS identities,
Buffer limits/views/errors and nine unavailable process calls/constructors. The
transport is a test entry point; it does not implement `node:http`.

Build and validate it using the already pinned native engine and npm toolchain:

```sh
NODE_COMPAT_TOOLCHAIN=/private/tmp/starling-node-compat/native-toolchain-lock \
NODE_COMPAT_ENGINE=/tmp/starling-node-compat/native-build/artifacts/starlingmonkey_embedding.wasm \
NODE_COMPAT_WASM_TOOLS=/path/to/wasm-tools-1.235.0 \
  /path/to/node-v22.14.0 tests/node-compat/wasmcloud/build-http.mjs

NODE_COMPAT_WASMTIME=/path/to/wasmtime-42.0.1 \
  /path/to/node-v22.14.0 tests/node-compat/wasmcloud/test-wasmtime-http.mjs
```

`NODE_COMPAT_HTTP_OUTPUT` changes the external output directory; its default is
`/tmp/starling-node-compat/wasmcloud-http`. Build outputs include the component,
post-stubbing core, bundle, actual emitted WIT, component type graph, packaging
audit and `component-audit.json`. The HTTP test writes `wasmtime-results.json`.
The wasmCloud runner and its deployment evidence are documented separately in
`README-host.md`.

The measured imports are exactly:

| Interface at 0.2.10 | Role |
| --- | --- |
| `wasi:http/types` | Incoming request, response and HTTP resource operations |
| `wasi:io/streams` | Output stream and its write/close operations |
| `wasi:io/poll` | I/O resource dependency and polling functions |
| `wasi:io/error` | I/O error resource dependency |
| `wasi:clocks/monotonic-clock` | **Type only:** `duration = u64`, required by HTTP signatures |

`type-audit.mjs` reads the actual component type graph with repository-pinned
wasm-tools 1.235.0. It rejects any monotonic-clock function or additional clock
type. The post-stubbing core must have zero clock imports. Thus there are five
interface imports and four executable core interface namespaces. This does not
grant or test `now`, timer subscription, Node timers or clock resumption. The
component imports no outgoing HTTP handler, sockets, DNS, filesystem, CLI,
environment, entropy, custom `jco:*`/`wasmcloud:*` service or Preview1 interface.

The explicit handler uses byte-valued headers through `Fields.fromList`; it
transfers response/outparam ownership, writes in chunks of at most 4096 bytes,
drops the output stream before finishing its body, and drops the incoming
request. It avoids the existing fetch-event singleton. A per-handler counter and
the native fixture's counter report observed state retention. Repeated HTTP
success alone does not establish that a host reuses component instances or that
general request isolation works.

## Pinned guest packaging adjustment

ComponentizeJS 0.23.0's existing stubbing pass replaces HTTP methods with traps
when both HTTP features are disabled, even if the application world explicitly
selects HTTP types. Enabling HTTP preserves an unwanted outgoing handler. Its
I/O preservation logic also does not recognize a directly selected I/O world.

`http-stubbing.mjs` uses the real exported `splicer.stubWasi` integration point
after Wizer. Manual bindings are generated with only `http` enabled. The first
stubbing pass uses `random,stdio,clocks,fetch-event`, preserving HTTP types/I/O
and removing outgoing HTTP. The second uses `http`, retaining those types/I/O
while stubbing random, clocks and stdio. RNG is preserved during the first pass
because the second pass expects its original import. The temporary function
replacement is restored in `finally`; this dedicated build process performs one
componentization at a time.

Exact hashes of ComponentizeJS's JavaScript integration point, generated splicer
bindings and both splicer Wasm files are checked before that composition. No npm
package file, native engine, Wasmtime binary or wasmCloud binary is patched.
This adapter is specific to the audited 0.23.0 packaging implementation; it is
not presented as a general ComponentizeJS option.

The high-level componentizer also unconditionally supplies a Preview1 adapter.
Jco 1.40.0's default adapter references 0.2.12, so the build explicitly pins the
repository's existing standard 0.2.0 release adapter by SHA-256 during that step.
After confirming that the resulting core has no Preview1 imports, the final
component is wrapped through the same public Jco `componentNew`/`metadataAdd`
APIs with an empty adapter list. All final imports must be exactly 0.2.10. The
monotonic `duration` import remains a required nominal signature dependency even
without an adapter; it is not attributed to an executable clock call.

## Executed Wasmtime result

On 2026-11-03 the unchanged normal native engine produced the HTTP component
`d32752b8f240d8edaa2f868469c4b788bd31da8cf0739230b7ed2884f3206f7f`
(18,190,456 bytes, including the oracle corpus). Unmodified Wasmtime 42.0.1
served three successful requests, each passing the full native fixture and
identifiable stub failures. JSON/no-store headers passed. Both counters were
one for every request, so same-instance state retention was **not established**.
The loopback server stopped cleanly after the test.

These byte counts are test-artifact observations. They do not measure a native
performance improvement or product-size delta. No general Node HTTP semantics,
entropy/clock refresh, OOM behavior, AsyncLocalStorage or concurrent request
isolation is established by these fixtures.
