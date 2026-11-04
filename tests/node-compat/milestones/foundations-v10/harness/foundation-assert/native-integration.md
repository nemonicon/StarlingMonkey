# Optional Assert native preparation

Production-source preparation lives in `builtins/node-compat/assert.mjs`,
`assert-strict.mjs`, the schema-valid version `sm-node-22.14.0-m0.5` manifest,
and the independent generator/header. Checked prototype sources and accepted
Node/component reports are preserved unchanged.

Proposed feature flag: **`NODE_COMPAT_ASSERT`**, default **OFF**, rejected when ON
without `ENABLE_BUILTIN_NODE_COMPAT`. It adds no host capability or dependency on
Path, Events, Querystring or StringDecoder. No shared register/CMake/generator
file is changed by this preparation.

`generate-assert-factories.mjs [--check]` validates the strict production schema,
derives finite root exports and the strict reexport map, and emits only
`assert-factories.generated.h`. The shared core/Path/Events headers are untouched.
It rejects unhandled module syntax/export mismatches instead of silently
producing incomplete records. The existing checked-in-header build convention
continues to require no Node/npm during normal CMake builds.

Exact C++ contract for Root's later integration:

```cpp
// Include only under NODE_COMPAT_ASSERT:
#include "assert-factories.generated.h"
// Existing private helper, already used by the other optional modules:
JS::RootedValue graph(cx);
if (!evaluate_factory(cx, kAssertFactorySource,
                      JS::UndefinedHandleValue, &graph)) return false;
JS::RootedObject object(cx, &graph.toObject());
JS::RootedValue root(cx), strict(cx);
if (!JS_GetProperty(cx, object, "root", &root) ||
    !JS_GetProperty(cx, object, "strict", &strict)) return false;
// Register these same rooted values with engine->define_builtin_module:
// node:assert + assert -> root
// node:assert/strict + assert/strict -> strict
```

This is a proposed integration snippet, not compiled code or a new embedding API.
`kAssertFactorySource` evaluates to a private callable with arity0. The existing
`evaluate_factory` always supplies one argument; undefined is ignored. Its result
is frozen `{root,strict}` containing two frozen finite22-export records. Their
default functions remain mutable and share Node's root/strict/ok graph. Named
bindings retain initial references. Explicit ordinary function descriptor order,
captured primordials, typed deferred errors and semantic restrictions are copied
from the checked prototype.

`run-native-node.mjs` passed actual production ESM sources and the exact generated
header against the same55 groups/784 primitive comparisons and22 profile cases
per variant, including namespace/default identity and no global injection.
[native-node-results.json](./native-node-results.json) records schema validation,
source/header/generator hashes and the strict registrar hash. VM evaluation uses
an explicit strict script prefix to match native `CompileOptions::setForceStrictMode()`;
no sloppy-script equivalence is claimed. Original reports were not overwritten.

`native-component.mjs`/`run-native-component.mjs` passed while retaining actual
`node:assert` and `/strict` externals. They cover first-deployed computed bare
aliases, actual module namespace type/prototype, cache/default/named identity,
static CommonJS lowering, snapshotted Error/reference state, all oracle/profile
vectors, nine initialization failures, and actual optional-OFF admission.
The new shared host-only `foundations/native-scalar-harness.mjs` audits frozen
engine inputs, strict registrar parity, exact pure WIT exports/imports and fresh
Wasmtime. [native-component-results.json](./native-component-results.json) records
the compiled v6 OFF engine `33b9cb248afbb4a3b3653c7b76bd656e51443e6823fa72d712758c742cd59516`
and all285 frozen inputs. All55 groups/784 comparisons and22 profile cases passed
on retained Jco calls `[1,2]` and fresh stock Wasmtime42 call1. All nine init
failures and actual v5 optional-OFF admission passed. Final WIT has zero imports
and exactly `run() -> string`. Real namespace tags/prototypes, alias value/state
sharing, CommonJS and snapshot reference identity are verified by that report.
Set `NODE_COMPAT_ASSERT_OFF_ENGINE`/`NODE_COMPAT_ASSERT_OFF_SOURCE_ROOT` to the
frozen v5 OFF negative control and `NODE_COMPAT_ASSERT_OUTPUT` for a distinct output.

Shared registration/build selection was integrated by Root and is covered by
the compiled receipt; this agent did not edit those shared files. The
[immutable v6 checkpoint](../milestones/foundations-v6/README.md) also records the
same joint HTTP component passing three requests on stock Wasmtime42 and official
wash2.11 with exactly six standard WASI0.2.10 interfaces. Counters `[1,1,1]` do not
prove HTTP instance reuse. Empirical Assert component-size/performance comparisons
and the broader roadmap remain open. Scalar native evidence is independent
of the earlier isolated prototype reports, which remain unchanged.
