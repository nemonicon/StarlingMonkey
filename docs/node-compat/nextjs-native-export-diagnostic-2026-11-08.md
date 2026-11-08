# Native export diagnostic checkpoint

The private diagnostic now compiles into a real guest engine and passes its
fixed seventeen-case Wasmtime deployment. The full Next.js comparison is next;
the earlier Server Action failures remain unresolved. Production acceptance
remains foundations-v13, and neither complete Node.js nor complete Buffer
compatibility is claimed.

The [native candidate](../../tests/node-compat/frameworks/nextjs/next-native-export-public-correlation-candidate-v1/README.md)
registers `internal:starlingmonkey/native-export-diagnostic-v1` through the
existing `embedding::install` and `Engine::define_builtin_module` path. It has
one named export, `observe`, and no default export. The guest entry preserves
this native import. The existing builtin module resolver and cache supply the
binding; no host service or new WIT interface is introduced.

`NODE_COMPAT_NATIVE_EXPORT_DIAGNOSTIC_V1` defaults OFF. The experimental build
enables it privately on the separate embedding target. Actual CMake and Ninja
evidence shows one embedding definition and none in the eighty native compile
rows. Engine `237c4e5a` is 31,350,211 bytes, 2,858 bytes larger than the preceding
engine. This is a size observation, not a throughput or memory result. The
[coordinated build review](../../tests/node-compat/frameworks/nextjs/next-native-export-diagnostic-build-root-results-v1/actual-build-review.json)
binds the six clean phases, 1,950 protected descriptors and separate Source/link
review. The coherent SpiderMonkey library is reused rather than rebuilt.

`observe(method, path, state, count, value)` accepts only the declared primitive
enums and a 64-character lowercase hexadecimal string or the permitted null
shapes. It returns undefined and performs no object coercion. A rooted input
string is copied under a no-GC scope into owned fixed storage; nonlinear strings
are reported unavailable. No JS edge or borrowed character pointer survives.
Two observations make the window ambiguous and discard its metadata. Logging
is bounded and occurs at the ordinary native success site. `post_call` only
clears memory; it performs no logging or import.

Probe component `d04c4289` is 37,156,919 bytes. Its
[INIT review](../../tests/node-compat/frameworks/nextjs/next-native-export-diagnostic-probe-root-results-v1/actual-construction-review.json)
verifies the complete returned graph, 131 observed imports across the same
thirteen WASI 0.2.10 interfaces, incoming-handler-only export and complete
marker-free INIT streams. The interface allowlist remains CLI environment and
stdout/stderr, both clocks, random, filesystem types/preopens, IO error/poll/
streams, and HTTP types/outgoing-handler. No socket or TLS capability is added.

The first fixed runtime finishes raw0 under its original 1,800-second owner.
Each case has a fresh owned Wasmtime process and one GET. All seventeen cases
pass the controller's validation and the
[coordinated runtime DATA review](../../tests/node-compat/frameworks/nextjs/next-native-export-diagnostic-probe-root-results-v1/actual-runtime-review.json),
which joins all eighteen original owners and seventeen complete captures:

| Cases | Observed result |
|---|---|
| `/none` | No native record in complete bounded capture; snapshot return flag true. |
| Valid value, then ordinary 512-KiB allocation | One valid record with copied fixture bytes. |
| Missing, invalid and duplicate states | Their declared unavailable reasons. |
| String/object enum, object value, wrong arity | Invalid arguments; conversion/accessor hooks untouched. |
| Short, uppercase, newline and nonhex values | Invalid value; no correlation bytes published. |
| Repeated identical or different observations | Ambiguous, saturated count two, metadata cleared. |
| Concatenated-string fixture | Observer reports nonlinear-string, an admitted unavailable result. |

These static fixture arguments are not incoming request metadata. Ordinary
allocation does not prove GC occurred, and the concatenation fixture does not
establish a particular string representation. A native return-site record does
not prove C-function return, canonical post-return, receiver acknowledgement or
host/TCP completion. The HTTP finish limitation is documented in the
[completion audit](nextjs-export-promise-completion-audit.md).

The real-Next constructor also finishes raw0 as component`6b2084d0`
(37,282,148 bytes), with the same standard interface audit and
[coordinated INIT review](../../tests/node-compat/frameworks/nextjs/next-native-export-diagnostic-next-root-results-v1/actual-construction-review.json).
Next is one fixed native-to-Node comparison with every existing gate preserved.
Output-quota exhaustion, failed stdout, forced-GC/OOM, broader lifecycle reuse,
persistent-cache overlap and performance measurements remain outstanding.
`progress.md` tracks execution and the portable evidence checks.
