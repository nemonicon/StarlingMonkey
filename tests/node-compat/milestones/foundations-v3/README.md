# Accepted bounded Path and loader checkpoint

The immutable `results.json` indexes12 copied reports/sources and verifies268
frozen native inputs. The OFF Release engine is
`3d106756f65c6dd18b590ba3f41b4cc760635c27fb738b678ead8bccd8a21897`.
Buffer/stub regression passes381 string and250 byte cases, two retained Jco
calls, Wasmtime, raw aliases and expected initialization failures.

The Path semantic component passes15,696 lexical vectors,4,046 glob vectors,
13 budget denials, four accepted adversarial inputs and12 invalid operations,
with three retained Jco calls and fresh Wasmtime. Its18 exports per namespace,
mutable default graph, static CommonJS lowering, snapshot behavior and zero
imports are checked. The separate raw-alias component proves first deployed
imports of all six prefixed/bare Path identifiers, per-specifier caching and
shared default identities, twice on Jco and on fresh Wasmtime. Both final
components emit zero host interfaces.

Pinned SpiderMonkey lacks Unicode property escapes. Twelve finite Unicode16
category tables replace only internal matcher class fragments; all1,114,112
code points per category were compared with pinned Node22 (13,369,344 checks).
Expansion consumes the existing deterministic pattern budget before compilation.
The fixed virtual cwd, default POSIX behavior, case policy and resource budgets
remain explicit Path deviations.

The raw-alias fixture exposed a general loader bug: freshly compiled synthetic
builtins remained in `New` status. Catching inside the guest preserved the
actual `InternalError`; uncaught export rejection had caused the embedding's
normal abort. `get_builtin_module` now uses the actual supported
`JS::LoadRequestedModules` zero-dependency path before caching. All nine
separate pure/cached/uncached/caught controls pass on Jco and Wasmtime with zero
imports. There is no generic asynchronous dependency-graph claim.

The runtime-only engine is also built and frozen; this initial index does not
transfer earlier entropy evidence to it automatically. Subsequent scalar
acceptance is recorded separately. The complete entropy and upstream233-subtest
host checkpoint remains [entropy-v1](../entropy-v1/README.md).

Path adapter size comparison is separate from this immutable checkpoint:
[latest benchmark](../../foundation-path/benchmark-results.json). It uses a
shared explicit environment world and measures avoided duplicate adapter code,
not minimal deployment size. General Node/Buffer support, production ALS,
remaining foundations, streams and optional capabilities remain unfinished.
