# Optional Querystring native preparation

Production-source preparation lives in `builtins/node-compat/querystring.mjs`,
the schema-valid version `sm-node-22.14.0-m0.6` manifest, and independent
`generate-querystring-factories.mjs`/`querystring-factories.generated.h`.
The isolated prototype and accepted Node/v5 component reports remain unchanged.

Proposed feature flag: **`NODE_COMPAT_QUERYSTRING`**, default **OFF**, rejected
when ON without `ENABLE_BUILTIN_NODE_COMPAT`. It requires only the existing core
Buffer constructor. Optional StringDecoder, Assert, Path and Events are not
dependencies. No new host interfaces or public global factory are added.
Shared registration/CMake/main-generator files are intentionally untouched here.

The independent generator validates the existing strict manifest schema, removes
the exact source-only Buffer import, and derives the eight finite export
bindings. Unsupported module syntax/missing bindings fail generation. Normal
CMake builds can use the checked-in header without Node/npm.

Exact C++ contract for Root's later integration:

```cpp
// Include only under NODE_COMPAT_QUERYSTRING:
#include "querystring-factories.generated.h"
// Existing install() has obtained and rooted buffer_constructor via
// JS_GetProperty(buffer_namespace, "Buffer", &buffer_constructor).
JS::RootedValue querystring_module(cx);
if (!evaluate_factory(cx, kQuerystringFactorySource, buffer_constructor,
                      &querystring_module)) return false;
// Register this same rooted record with engine->define_builtin_module:
// node:querystring + querystring -> querystring_module
```

This is a proposed integration snippet, not compiled code or an invented API.
`kQuerystringFactorySource` evaluates to a private callable with arity1, whose
sole argument is the existing Buffer constructor. Captures occur during that
private installation call. It returns a frozen eight-export record; its ordinary
default object remains mutable, with `encode===stringify` and `decode===parse`.
It does not read `globalThis.Buffer` or expose a guest-callable installer.

The production facade preserves the tested pinned parser, native URI fast paths,
legacy surrogate repair, byte fallback, limits and deferred nonstring overload.
Buffer allocation/slice captures remain private. No extra byte copy or native
borrowed-pointer lifetime is introduced by adapting the source import to a
private factory parameter.

`run-native-node.mjs` passed production ESM and exact generated factory against
the same32 groups/210 delimiter and1,536 byte vectors plus11 profile cases each.
[native-node-results.json](./native-node-results.json) records schema validity,
no global injection and private argument injection while global Buffer is
undefined. Generated VM scripts use strict mode to match the shared native
registrar; its exact source hash is pinned. Accepted records were not overwritten.

The actual-native `native-component.mjs`/`run-native-component.mjs` passed, keeping
Querystring and Buffer external, checks first-deployed computed bare alias/cache,
actual namespace type/prototype and shared values, static CommonJS lowering,
snapshotted typed-array backing/dictionary state, all oracle/profile vectors,
eight initialization failures, and optional-OFF admission. The native factory is
also exercised with global Buffer undefined at deployed execution. Shared
host-only `foundations/native-scalar-harness.mjs` verifies frozen source receipts,
strict registrar parity, final pure WIT and fresh Wasmtime.
[native-component-results.json](./native-component-results.json) records compiled
v6 OFF engine `33b9cb248afbb4a3b3653c7b76bd656e51443e6823fa72d712758c742cd59516`
and all285 frozen inputs. All32 groups/210 delimiter/1,536 byte-BOM vectors and11
profile checks passed on retained Jco calls `[1,2]` and fresh stock Wasmtime42
call1. Eight initialization failures and actual v5 optional-OFF admission passed.
Final WIT has zero imports and exactly `run() -> string`; namespace/cache/shared
default, static CommonJS, private Buffer dependency and snapshot backing/dictionary
state are actual native results. Set `NODE_COMPAT_QUERYSTRING_OFF_ENGINE`/
`NODE_COMPAT_QUERYSTRING_OFF_SOURCE_ROOT` to frozen v5 and use
`NODE_COMPAT_QUERYSTRING_OUTPUT` for distinct output.

Root completed shared registration/CMake/selection integration; this agent made
no shared-file edits. The [immutable v6 checkpoint](../milestones/foundations-v6/README.md)
records the same joint HTTP component passing three requests on stock Wasmtime42
and official wash2.11 with exactly six standard WASI0.2.10 interfaces. Counters
`[1,1,1]` establish no HTTP instance reuse claim.
Performance and final-size claims require stripped-fixture comparisons against
the locked Jco/unenv adapter. The isolated v5 guest-Buffer proof does not establish
production Querystring installation.
