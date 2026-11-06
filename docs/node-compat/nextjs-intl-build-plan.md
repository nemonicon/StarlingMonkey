# Next.js: Intl-enabled SpiderMonkey 147 build plan

Status: **unpatched and SavedFrame-enabled Intl libraries built in CI;
84-package Rust graph resolves offline; fresh V7 native engine builds and links
in six clean phases. New component and Next runtime gates remain pending.**
The current WASI 0.2.10 world and stock
Wasmtime/wasmCloud hosts remain unchanged. No application/regex rewriting or JS
compatibility shim is proposed.

## Why a guest-library rebuild is needed

The actual `next-native-build-v5/extracted-spidermonkey/` headers report
`MOZJS_MAJOR_VERSION=147` and undefine `JS_HAS_INTL_API` at `js-config.h:42`.
That 2,324-byte header has SHA256
`ffa2a28de2b1138ec4aa9a214e9fdbebc8ad314f6c8ae560fdee24b34f68492e`.
`js-confdefs.h` is 2,283 bytes/SHA256
`841e57a382d7d8219431dc26e1d1307af1649228503d21bcf2eac826fc99acd6`;
its `MOZ_ICU4X=1` does **not** establish an Intl-enabled parser. The retained
538,170,426-byte `libspidermonkey.a` is the old non-Intl artifact.

The baseline [CMake integration](../../cmake/spidermonkey.cmake) selects
`FIREFOX_147_0_4_RELEASE_STARLING` and supplies `--without-intl-api` in its
default configuration.
GitHub's tag-ref API resolved this tag to commit
**`9dab3d6f643e926a340c391ea30968e940390dec`** in
[`bytecodealliance/firefox`](https://github.com/bytecodealliance/firefox/tree/9dab3d6f643e926a340c391ea30968e940390dec).
Use that exact fork/commit, not a stock Firefox release or a moving branch.

At that commit, [irregexp's build selection](https://github.com/bytecodealliance/firefox/blob/9dab3d6f643e926a340c391ea30968e940390dec/js/src/irregexp/moz.build)
adds `V8_INTL_SUPPORT` only with `JS_HAS_INTL_API`.
The [parser's non-Intl branches](https://github.com/bytecodealliance/firefox/blob/9dab3d6f643e926a340c391ea30968e940390dec/js/src/irregexp/imported/regexp-parser.cc#L2270-L2286)
return false for Unicode property-name/range parsing. This strongly explains
the actual Next `ID_Start`/`ID_Continue` literal rejection. It is Source-based
diagnosis, not a retained compiler-argv observation or a successful repair.
The bounded [probe findings](../../tests/node-compat/frameworks/nextjs/regexp-unicode-probe-candidate-v1/findings.json)
retain the actual header evidence and the separate unexecuted-probe status.

## Smallest coherent build change

1. Use a fresh private source/object/distribution namespace. Authenticate the
   exact commit and its vendored dependency/lockfiles. Prefer the upstream
   SpiderMonkey [source-package selection](https://github.com/bytecodealliance/firefox/blob/9dab3d6f643e926a340c391ea30968e940390dec/js/src/make-source-package.py)
   or an equivalent authenticated sparse checkout; avoid full Git history.
2. Retain existing WASI SDK 30 `wasm32-unknown-wasi`, Release/O3, static,
   portable-baseline, no-JIT, no-shared-memory, no-shell and no-debug policies.
   Replace `--without-intl-api` with supported `--with-intl-api`. Do not add
   `--disable-icu4x`: the exact fork [explicitly refuses that combination](https://github.com/bytecodealliance/firefox/blob/9dab3d6f643e926a340c391ea30968e940390dec/js/moz.configure#L1199-L1217).
3. Use the fork's bundled ICU 78.1/data, not host/system ICU. Its
   [static dependency graph](https://github.com/bytecodealliance/firefox/blob/9dab3d6f643e926a340c391ea30968e940390dec/config/external/icu/moz.build)
   includes common/i18n/data; the [data assembly has an explicit WASI branch](https://github.com/bytecodealliance/firefox/blob/9dab3d6f643e926a340c391ea30968e940390dec/config/external/icu/data/icu_data.S).
   Retain actual archive members and generated link response files to verify
   ICU/data inclusion; do not assume a filename proves the closure.
4. Resolve the **Rust aggregate join before linking**. Disabling the JS shell
   omits upstream `js/src/rust`; existing StarlingMonkey
   [single-aggregate tooling](../../cmake/build-crates.cmake) does not supply
   all new Intl FFI. The exact fork requires
   [`icu_capi` 2.0](https://github.com/bytecodealliance/firefox/blob/9dab3d6f643e926a340c391ea30968e940390dec/js/src/rust/shared/Cargo.toml)
   with `any_provider`, `compiled_data`, `segmenter`, `calendar`, plus the
   same fork's `unicode-bidi-ffi`. Prepare genuine `add_rust_lib` integration
   and a new locked dependency graph, using the upstream vendored sources.
   Do not simply link another `jsrust` staticlib alongside the current
   aggregate: duplicate Rust runtime/hooks and allocator ownership need an
   explicit coherent solution. The V7 build now compiles this single aggregate.
5. Produce coherent new `include/`, generated `js-config.h`/`js-confdefs.h`
   and `libspidermonkey.a`. The existing `SPIDERMONKEY_BINARIES` mechanism
   accepts this distribution. The current Next runner sets that variable from
   its authenticated SpiderMonkey archive plan; issue a genuine new plan
   binding the new archive rather than changing a live old extraction.
   Recompile all selected native and embedding units against these headers,
   rebuild the single Rust aggregate and link a fresh engine. A consumer
   macro, header-only replacement or old-object relink is insufficient ABI
   evidence. Preserve all old engines, WORKs and failure records.

## Tools and capacity

The pinned fork's [Mach entry](https://github.com/bytecodealliance/firefox/blob/9dab3d6f643e926a340c391ea30968e940390dec/mach)
requires Python ≥ 3.9 and lists 3.12 as its highest considered version. Installed
Python 3.9/3.11/3.12 are available. The fork's
[Rust minimum](https://github.com/bytecodealliance/firefox/blob/9dab3d6f643e926a340c391ea30968e940390dec/python/mozboot/mozboot/util.py)
is 1.82.0; the existing private Rust 1.88 toolchain/wasm32-wasip1 target can be
reused as authenticated read-only inputs or copied into new owned caches.
[Compiler checks](https://github.com/bytecodealliance/firefox/blob/9dab3d6f643e926a340c391ea30968e940390dec/build/moz.configure/toolchain.configure)
require clang ≥ 17 and macOS SDK ≥ 26.1. SDK 30 supplies clang 21; installed Xcode
SDK 27 satisfies the SDK minimum. The host compiler/version and complete Mach
Python environment still need explicit authentication before execution.
Autoconf is absent from PATH, but the inspected active path uses Python
configure; no autoconf2.13 invocation was found, so its absence is not a
demonstrated blocker. Do not install it solely from older SpiderMonkey guides.

At **2026-11-06T17:45:21Z**, the only identified writable volume
(`/System/Volumes/Data`, shared by the workspace and `/private/tmp`) had
**3,236,143,104 bytes available**. No full cached Firefox source checkout was
found; available archives/headers are the existing non-Intl distribution.
Root requested at least 20 GiB headroom or another writable volume; no capacity
answer has arrived. **Do not start a heavy fetch/build at current capacity.**
20 GiB is a planning budget, not a measured peak guarantee. Account separately
for source, object/LTO files, vendored Rust, new aggregate target, distribution
and the subsequent full engine build. Use single-job limits, an explicit disk
floor and raw monitored commands; any source reduction or debug-symbol policy
change must be recorded honestly. Do not delete prior evidence to make space.

## Capacity workaround and integration preparation

The first manual [run42272037547](https://github.com/nemonicon/StarlingMonkey/actions/runs/42272037547)
at StarlingMonkey commit`dc7bad5c36306368fd8a2816136f02f959aed0ee` succeeds:
17 raw0 owned phases, exact fork9dab and a222,772,017-byte coherent Intl
distribution archive, SHA256`2508af52c38510b56d711bc37a0ffb5a32450a1dc2847787eebf62f09a4ca062`.
The downloaded227,191,494-byte Actions ZIP matches its published SHA256
`ae81c73ecb7b9e93eb08e265d64836e68e3d838d9bbc8bb602ca79a3cbc8342f`.
Independent artifact/ICU closure review is being retained. Library compilation
does not establish a native engine, Unicode differential or Next runtime pass.

Actual Rust resolution now produces84 packages, preserving all49 old lock
identities. The first conflicting smallvec seed failure remains preserved.
Ten explicit compatible-family reconciliations pass actual Cargo resolution;
76 external packages/2,278 files/35,510,599 bytes pass vendor checksums and
patched Bidi source/manifest equality. Fresh offline `--locked` metadata matches
the online graph/features. New features on old packages are separately recorded;
these are dependency-resolution results, not Rust compilation/FFI link proof.

The [structured-stack failure](../../tests/node-compat/frameworks/nextjs/stacktrace-probe-root-results-v1/actual-review/README.md)
adds a coherent guest-library requirement. The
[four-file guest patch](../../tests/node-compat/frameworks/nextjs/stacktrace-native-v1/spidermonkey-patch/README.md)
introduces a **new** `GetSavedFrameIsEval` API; existing
SavedFrame APIs cannot provide truthful eval provenance. It changes no host
interface. The next opt-in CI build applies exactly that sealed patch to9dab,
requires matching installed headers/library, and records a distinct variant.
The first unpatched Intl artifact remains an honest separate checkpoint.
The [opt-in run42281671898](https://github.com/nemonicon/StarlingMonkey/actions/runs/42281671898)
also succeeds:22 clean0 phases, matching API headerfc3b58f8 and libraryca04fe5e,
637,175,630 bytes. The archive is222,806,343 bytes/SHA256e1f1e208. All596 staged
files match the downloaded variant. The full V7 native consumer now compiles
and links; source/compiler success does not establish the API's runtime behavior.

The [bounded local tool preflight](../../tests/node-compat/frameworks/nextjs/spidermonkey-intl-tool-preflight-v1/README.md)
executes 17 read-only tool/version commands and verifies Make 3.81, SDK 27 and
Python 3.12 prerequisites. It finds one concrete upgrade: existing cbindgen
0.29.0 is below the exact fork's required 0.29.1. No local Mach/build runs.

The [manual CI library build](../../tests/node-compat/frameworks/nextjs/spidermonkey-intl-build-v1/README.md)
uses the existing CMake module with explicit source/Intl opt-ins, exact commit
verification and private build state. Six actual CMake selection tests pass;
the default distribution path remains unchanged. The already enabled public
fork can use standard Ubuntu runners, avoiding a local source/compiler peak.
The job requires 20 GiB free initially and a 4 GiB floor, retains raw failure
evidence and uploads artifacts only. No repository setting, release workflow,
host interface or runtime policy is changed. Compilation is verified for the
unpatched and patched libraries and the V7 engine. The complete guest runtime
gates remain pending. The first Linux run starts with
88,822,759,424 bytes free and ends with77,543,546,880; this is a measured run,
not a universal platform/peak guarantee.

## Required evidence after the library and engine builds

Retain generated Intl configuration, actual `V8_INTL_SUPPORT` compile rows,
ICU/data/Rust archive identities, whole link commands, all raw failures and
source/tool bookends. The first C++/ICU guest library compiles; the separate
single-Rust aggregate and whole-engine FFI link now compile. Audit the
new engine/component's actual imports without widening the current 13-interface
world by assumption. Run the isolated Unicode-property probe, then the
unchanged full Next application/contracts. Neither a defined `Intl` global
nor a successful regex alone admits the complete profile, snapshot/reuse,
security or performance gates.

The bounded [single-aggregate companion](nextjs-intl-build-plan/README.md)
contains proposed Cargo/CMake afterimages, exact upstream manifest snapshots,
root patch/vendor requirements and offline Source tests. It consumes Root's
`SPIDERMONKEY_INTL` selector without editing the SpiderMonkey workflow or build
options. That immutable companion's original input slots remain unissued;
the actual84-package resolution/vendor/offline evidence above is a separate
successor, now consumed by the successfully linked V7 native engine. All four
new components validate with the same13 standard WASI0.2.10 imports. The strict
Unicode differential passes36/36 selected records. The unchanged full Next
attempt passes11/24 HTTP cases; response piping, file-stream options and
Buffer/decoder behavior are the next demonstrated blockers. No full Next or
production-profile acceptance follows from these partial results.
