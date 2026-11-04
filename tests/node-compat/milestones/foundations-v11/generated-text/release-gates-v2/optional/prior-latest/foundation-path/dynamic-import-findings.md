# First deployed builtin import

The all-dynamic alias fixture exposed a general loader defect on the immutable
`foundations-v2` Release engine, rather than a Path algorithm failure. The same
uncached import of `node:buffer` and `node:child_process` failed. Both cached
dynamic imports and ordinary async functions succeeded.

| Fixture | Jco, two calls | Fresh Wasmtime42 |
| --- | --- | --- |
| Async function awaiting a resolved promise | `ok`, `ok` | `ok` |
| Dynamic Buffer import after a static Buffer import | `ok`, `ok` | `ok` |
| Dynamic Path import after a static Path import | `ok`, `ok` | `ok` |
| First deployed Buffer import | trap | trap |
| First deployed Path import | trap | trap |
| First deployed child_process import | trap | trap |
| First Buffer import caught inside the guest | `InternalError`, twice | same error |

The caught error is **`module record has unexpected status: New`**. These
capability-free components and their reports are retained at
`/tmp/starling-node-compat/foundations-v2/path-dynamic-diagnostic` and
`path-dynamic-diagnostic-caught`. The latter requires no stdio diagnostic import
to expose the original JavaScript rejection. The build/run driver is
[`dynamic-import-diagnostic.mjs`](dynamic-import-diagnostic.mjs).

The exact pinned SpiderMonkey source is
[`Modules.cpp` at 9dab3d6f643e926a340c391ea30968e940390dec](https://github.com/bytecodealliance/firefox/blob/9dab3d6f643e926a340c391ea30968e940390dec/js/src/vm/Modules.cpp),
SHA-256 `eefba8a5222f3d1c6032417ea3b719ea8705cf6cbe80b5dd070ff3c53b6a0538`.
Its `ContinueDynamicImport` calls `ModuleLink`; `ModuleLink` rejects the `New`
status. `LoadRequestedModules` performs the required transition to `Unlinked`.
For a graph with zero requested modules, `InnerModuleLoading` decrements its
initial pending count to zero and calls its fulfillment callback synchronously.

StarlingMonkey's `get_builtin_module` generated and compiled its ESM wrapper,
then cached it immediately. That wrapper uses `import.meta.builtin` and export
declarations, with **no import declarations**. Static graph loading completed
the dependency phase when an application statically imported the wrapper.
The first deployed dynamic import had no corresponding dependency-loading
step, so it supplied a `New` module to SpiderMonkey's dynamic linker.

The scoped fix calls the real `JS::LoadRequestedModules` callback overload for
this empty graph before publishing the wrapper in `moduleRegistry`. Allocation
failure or a pending/rejected error returns `nullptr` before caching. The
module, metadata and export record remain rooted across the API call. This
does not add general asynchronous filesystem-module graph loading.

The uncaught JavaScript rejection subsequently reaches ComponentizeJS's
existing export-promise failure path. Its native `call` aborts when the export
promise is not fulfilled. The observed trap therefore does not establish a
Buffer memory-ownership or Path matching fault. No live component memory was
read or modified for this diagnosis.

The fix compiled against the actual SDK30/SpiderMonkey147 headers. The rebuilt
`foundations-v3` Release engine (SHA-256
`3d106756f65c6dd18b590ba3f41b4cc760635c27fb738b678ead8bccd8a21897`)
passes the complete unmodified all-dynamic alias fixture for all six Path
identifiers on two calls through one Jco instance and a fresh Wasmtime42
instance. It also passes the full Path semantic component, including its static
imports and three reused-instance calls. Both components have zero host
imports. The accepted artifact receipts and source archive are recorded in
[`results.json`](results.json).

The separate nine-case post-fix control set also passes: ordinary async,
cached Buffer/Path, uncached Buffer/Path/child_process, and caught versions of
all three uncached imports. Each real component returns `ok` twice on the same
Jco instance and once through a fresh Wasmtime invocation, with zero imports.
See [`dynamic-import-results.json`](dynamic-import-results.json). The preserved
pre-fix caught control continues to identify the original `New` error.
