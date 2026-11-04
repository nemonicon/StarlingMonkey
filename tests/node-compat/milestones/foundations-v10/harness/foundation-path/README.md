# Optional Path foundation

`NODE_COMPAT_PATH=ON` adds `node:path`, `node:path/posix`, and
`node:path/win32`, with bare aliases `path`, `path/posix`, and `path/win32`.
It defaults **OFF** and requires the core profile. The core m0.1 manifest and
generated factory header remain unchanged. The separate
[`m0.2 manifest`](../../../builtins/node-compat/export-manifest.path.node-v22.14.0.json)
declares the exact 18 ESM exports. Normal builds need no npm dependencies or
JavaScript generator execution: registration consumes the checked-in optional
header only under `NODE_COMPAT_PATH`.

The implementation is guest JavaScript installed through the existing native
builtin registry. It does not claim that the Path algorithms execute as new
C++ kernels. The lexical algorithms come from exact Node v22.14.0 MIT source;
[`path-sources.json`](../../../builtins/node-compat/path-sources.json), the
source diff and dependency manifests identify the inputs and adaptations.

Host validation currently passes 15,696 differential lexical vectors, 220
invalid-input cases and 934 assertions from 16 pinned upstream Path test files.
The matcher passes 4,046 ordinary differential cases, thirteen coded budget
rejections and four accepted adversarial cases. See
[`semantic-results.json`](semantic-results.json) and
[`glob-results.json`](glob-results.json). The actual Release component gate now
passes all lexical/glob vectors, thirteen budget errors, four bounded adversarial
cases, snapshot calls, export/default/CommonJS identities, and all six uncached
native aliases with repeated namespace caching. It runs three calls on one Jco
instance and a fresh Wasmtime42 instance. Both semantic and alias components
emit **zero host imports**, with final interface audits recorded in
[`results.json`](results.json). Top-level invalid and budget operations also
fail componentization. The 29,254,707-byte semantic component embeds the full
oracle corpus and is not a representative deployment-size measurement.

## Contract

All thirteen callable exports implement their operations: `_makeLong`,
`basename`, `dirname`, `extname`, `format`, `isAbsolute`, `join`, `matchesGlob`,
`normalize`, `parse`, `relative`, `resolve`, and `toNamespacedPath`. `sep` and
`delimiter` retain their string types. `_makeLong` aliases `toNamespacedPath`.

The root default is the real POSIX object. Both default objects are ordinary
mutable objects and share one cyclic `posix`/`win32` graph. ESM named functions
capture their initial values; mutating `default.basename` does not rewrite a
named `basename` binding. `syncBuiltinESMExports` is outside this profile. Static
CommonJS bundler interoperation returns these same default objects. The native
loader caches a namespace per registered specifier; aliases share exported
object/function identities.

The selected platform is fixed POSIX, with **virtual cwd `/`**. Win32 lexical
algorithms remain real Win32 algorithms, including drive letters, UNC roots,
separators, and namespaced paths. There is no host cwd, drive-specific cwd,
environment, filesystem, network or entropy provider. Relative resolution uses
the virtual root. `matchesGlob` uses the POSIX-host case policy for both variants
(`nocase=false`); this explicitly differs from running the pinned Node binary
on macOS or Windows. Its experimental warning is suppressed. TypeError names
and `ERR_INVALID_ARG_TYPE` codes are checked; received-value message rendering
is intentionally simpler than Node's internal inspector.

## Bounded matcher

The historical Node matcher is not shipped: its brace dependency and regular
expression matcher have subsequently published availability defects. The
profile pins minimatch **11.0.1**, nonrecursive-glob-match **1.0.3**,
brace-expansion **5.0.12**, and balanced-match **4.0.4**, with original/adapted
source hashes, exact local patches, registry integrity pins, and all four package license
texts under [`path-vendor`](../../../builtins/node-compat/path-vendor).
The authors' [matcher advisory](https://github.com/isaacs/minimatch/security/advisories/GHSA-g3hv-75wg-m249)
and [brace advisories](https://github.com/juliangruber/brace-expansion/security)
explain the patch selection. No assertion of future vulnerability absence is
made.

Matching uses a bounded state machine. Regular expressions are limited to
literal or character-class checks, not generated whole-pattern backtracking
expressions. Local compatibility changes retain Node22 UTF-16 wildcard behavior,
its POSIX class mappings and nullable-extglob behavior. Ordinary inputs are
compared with the exact Node22 embedded matcher, changing only the documented
host case option. Known hostile inputs are never sent to that historical oracle.

The pinned SpiderMonkey build rejects RegExp Unicode property escapes (including
`\p{L}`), so internal POSIX classes use checked-in Unicode16.0 intervals from
the exact Node22.14 oracle instead. The finite twelve-category allowlist is
generated and independently compared at all 1,114,112 code-point values per
category, including lone surrogates: 13,369,344 comparisons. See
[`unicode-results.json`](unicode-results.json). Only internal POSIX fragments
expand; application patterns never select arbitrary Unicode properties. Expanded
class-source code units charge the existing work budget **before** appending or
compiling them. This bounds repeated large classes as well as state-machine
work. Negation, astral characters, combining marks and lone surrogates are also
covered by the ordinary differential/component corpus. The original failure and
portable probe are retained separately under `/tmp/starling-node-compat/foundations-v1/path`.

| Resource | Profile bound |
| --- | ---: |
| Input path / pattern | 4096 / 1024 UTF-16 code units |
| Brace alternatives / aggregate output | 128 / 32768 code units |
| Brace depth / rewrite passes | 8 / 16 |
| Extglob depth / path or pattern portions | 8 / 128 |
| Portion containing magic | 256 code units |
| Conservative precompile state estimate | 65536 |
| Input-length × state estimate | 2000000 |
| Dynamically charged work units per call | 250000 |
| One state-key string | 32768 code units |
| Globstar recursion | 32 |
| Upstream DFA cache clearing threshold | 262144 units |

Length, nesting and integer-range checks run before expansion. Bounded expansion
outputs are rechecked for generated syntax; graph-work estimates are checked
before matcher compilation. Strict expansion checks run before another result is
copied or appended. State construction, comparisons, keys and globstar dispatch
charge deterministic work units. Budget exhaustion throws a **RangeError** with
`code="ERR_SM_NODE_PATH_BUDGET"` and a precise `resource` string. No result set
is silently truncated and no budget produces a false match result. Work units
are a defined algorithmic budget, not a wall-clock or whole-engine instruction
limit.

No pattern cache survives a call. The lazy module retains its implementation,
bounded static tables and the latest bounded escape sentinels; matcher/DFA
objects become collectible after each operation. The upstream case-fold cache
is bounded and remains unused by this fixed case-sensitive policy. Per-call
work also bounds allocation after a cache clearing event. Escape sentinels are
deterministic and selected absent from the original pattern; Math.random and
cryptographic randomness are never used. `finally` releases the private budget
state after success or failure, including between component invocations.

## Reproduction and gates

```sh
NODE_COMPAT_TOOLCHAIN=/absolute/path/to/pinned-toolchain \
  /absolute/path/to/node-v22.14.0 tests/node-compat/foundation-path/generate-matcher.mjs --check
/absolute/path/to/node-v22.14.0 builtins/node-compat/generate-factories.mjs --check
/absolute/path/to/node-v22.14.0 tests/node-compat/foundation-path/generate-unicode.mjs --check
/absolute/path/to/node-v22.14.0 tests/node-compat/foundation-path/semantic.mjs
/absolute/path/to/node-v22.14.0 --expose-internals tests/node-compat/foundation-path/glob.mjs
```

For the component gate, build with the core profile and `NODE_COMPAT_PATH=ON`,
select the audited v2 packager, then run:

```sh
NODE_COMPAT_ENGINE=/absolute/path/to/path-enabled-release-engine.wasm \
NODE_COMPAT_WASMTIME=/absolute/path/to/wasmtime-42.0.1 \
NODE_COMPAT_COMPONENTIZE_MODULE=/absolute/path/to/v2/package/src/componentize.js \
  /absolute/path/to/node-v22.14.0 tests/node-compat/foundation-path/run.mjs
```

The runner checks the engine receipt and selected manifest hashes, preserves
native module imports, rejects bundled replacements, tests every differential
vector inside the real component, inspects zero emitted imports, invokes one
Jco instance three times and a fresh Wasmtime instance, checks native alias
caching and static require identities, and requires invalid/budget operations
at application top level to fail componentization. It records actual artifacts
and provenance in `results.json`. DEBUG indirect canonical-memory bindings are
not admitted for this string-result world.

`tests/node-compat/module-selection-test.mjs` separately verifies 67 build-time
admission cases. Core-only selection rejects Path imports before the actual Jco
adapter can resolve them; optional selection preserves canonical ESM/static-CJS
aliases. Receipt flags, manifest hashes, collisions and protected virtual-module
declarations fail closed, including independent Path/Events flag combinations.
These tests use synthetic rejection receipts and do
not substitute for engine execution.

The upstream fixture harness excludes exact received-value messages and the
probe replacing `process.cwd()` with a failing provider, because those differ
by contract. Windows-host process/filesystem blocks are not selected; Win32
lexical behavior is exercised directly. These are explicit limits, not claims
that the full Node test suite or real Windows process behavior passed.

The uncached alias test exposed and fixed a general builtin-loader defect:
newly compiled wrappers reached dynamic linking with module status `New`.
The actual empty dependency graph is now loaded before caching, using the
existing SpiderMonkey API. See
[`dynamic-import-findings.md`](dynamic-import-findings.md) for the failing
controls, exact source analysis and scope of the fix.

## Existing-adapter comparison

`benchmark-adapter.mjs` builds the registered profile and the **actual installed
Jco1.40 Path adapter** against the identical Path-enabled Release engine. Both
use Rolldown tree shaking and the same tiny workload: POSIX join, Win32
normalize, and one ordinary brace glob. The common benchmark world explicitly
selects standard `wasi:cli/environment@0.2.10`, required by the existing adapter;
this is separate from the capability-free acceptance world. Emitted imports
are recorded for both arms and must contain no other interface.

The primary result is component/bundle size and checksum correctness. The size
delta measures avoided **duplicate bundled adapter code** under the same
profile-enabled engine, not a minimal deployment saving. The adapter implements
a newer Node release and broader cwd behavior; no equivalence outside the fixed
common workload is claimed. Set `NODE_COMPAT_PATH_TIMING=1` only in an idle
measurement window to add three warmups and seven persistent-instance batches
of 1000 iterations. Those are explicitly V8-hosted Wasm timings through Jco,
not Wasmtime throughput or startup/memory measurements. `benchmark-results.json`
is written only after the actual components are built and checked.

The accepted same-engine measurement is:

| Arm | Application bundle | Component |
| --- | ---: | ---: |
| Registered guest Path profile | 457 B | 11,834,360 B |
| Existing Jco1.40 adapter | 96,977 B | 12,160,661 B |

The component difference is **326,301 bytes** of avoided duplicate adapter
code. Both checksum results are `-448926747` for 1000 iterations on Jco and
Wasmtime42. Timing is disabled in this accepted measurement. Actual final
components import exactly `wasi:cli/environment@0.2.10`; all three canonical
function types are compared with checked-in `.10` WIT. See
[`benchmark-results.json`](benchmark-results.json).

The original feature pass retains four internal Preview1 args/environment
imports whenever this benchmark world selects P2 environment. Standard Preview1
adapters also pulled in unselected stderr/I/O interfaces. The controlled
benchmark therefore uses a **108-byte guest-only denial adapter** through the
existing `componentNew` adapter mechanism. It has no imports or memory and
exports exactly `args_get`, `args_sizes_get`, `environ_get`, and
`environ_sizes_get`, each `(i32,i32)->i32` with an `unreachable` body. All four
independently trap on V8 and Wasmtime. This preserves the pure-profile denial
of unused internal P1 paths; it implements no environment API or host service.
The actual Jco adapter still receives real selected **P2** environment imports.
This adapter is limited to the benchmark and does not change production Path.

[`adapter-control-results.json`](adapter-control-results.json) preserves the
unchanged refused components for the npm default adapter, repository legacy
adapter, and official Wasmtime42.0.1 reactor adapter, including adapter and
component hashes. The default emits environment, stderr, I/O error and streams
at `.12`; the other two emit those four interfaces at `.10`. The final audit
rejects every control, and none is instantiated. No version text is rewritten
and no capability allowlist is broadened.

To repeat the size/checksum gate, select the same audited Release engine and
toolchain, then run `benchmark-adapter.mjs` with explicit
`NODE_COMPAT_ENGINE`, `NODE_COMPAT_ENGINE_SOURCE_ROOT` (if using a frozen source
archive), `NODE_COMPAT_TOOLCHAIN`, `NODE_COMPAT_COMPONENTIZE_MODULE`,
`NODE_COMPAT_WASMTIME`, and `NODE_COMPAT_WASM_TOOLS`. The latter must be the
pinned wasm-tools1.235.0 executable. The denial adapter is generated from its
checked-in WAT and hash-checked before composition.
