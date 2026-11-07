# Reproducing the experimental Next generation

The selected fresh-app Next smoke passes on component `1c3108d2…`, engine
`4623640b…`, with the genuine2,181-file application and matched Node control
retained in the [fresh paired review](../../tests/node-compat/frameworks/nextjs/next-app-runtime-root-results-v1/first-pair-review/README.md).
The later native three-run cohort passes; its combined gate stays failed
because one stock run aborts. Earlier55f05 first/repeat runs remain in the
[historical milestone report](nextjs-wasm-milestone-2026-11-06.md).
**A clean-machine build has not been demonstrated.** The existing
[regression command](../../tests/node-compat/frameworks/nextjs/run-fresh-next-regression.py)
reuses exact private artifacts; it does not bootstrap them. This plan is a
source audit with the isolated host app build now executed; it does not claim
bit-for-bit rebuilds or a rebuilt native engine.
Performance work is separate in the [measurement plan](nextjs-measurement-plan.md).

## Dependency order and existing mechanisms

Paths below are relative to the repository unless shown otherwise. Command
shapes describe existing programs; `AUTHORITY` means a newly reviewed complete
document with genuine input descriptors, fresh output roots and current
inventories. Historical authorities contain absolute workstation paths and
cannot be made portable by replacing strings or expected hashes.

1. **Recover the finite native sources.** The new
   [portable materializer](../../tests/node-compat/frameworks/nextjs/next-native-portable-source-v1/README.md)
   closes the source-content step for working V7 plus UTF16: default `--check`
   reads only, and `--output /FRESH/ROOT` exclusively creates435 native,
   387 support and3 embedding files from repository-relative donors. Its first
   35 Source-only tests match all825 actual declared inputs and exercise the
   real CLI from a relocated repository closure. No compiler or engine ran.
   The underlying
   [reconstruct-native-inputs.py](../../tests/node-compat/frameworks/nextjs/spidermonkey-intl-build-v1/reconstruct-native-inputs.py)
   accepts `--check` or one fresh absolute output directory:

   ```sh
   python3 -I -B tests/node-compat/frameworks/nextjs/spidermonkey-intl-build-v1/reconstruct-native-inputs.py /FRESH/BASE
   ```

   Its committed [824-row map](../../tests/node-compat/frameworks/nextjs/spidermonkey-intl-build-v1/portable-native-inputs.json)
   selects byte-identical Git donors: 435 native files, 386 support files and
   three embedding files, 7,507,787 bytes. Three merged afterimages are retained
   beside the map. This reconstructs the **C2 pre-Intl baseline**, not V7.
   The [V7 packet](../../tests/node-compat/frameworks/nextjs/next-intl-native-profile-v1/composer-mappings.json)
   supplies five exact replacements and `Cargo.intl.toml.in`, making support387
   while native435/embedding3 stay unchanged.
   [compose-successor.py](../../tests/node-compat/frameworks/nextjs/native-profile-candidate-v1/compose-successor.py)
   takes `BASE_DIRECTORY OUTPUT_DIRECTORY REPAIR_PACKET_DIRECTORY` and verifies
   before hashes. That historical composer expects an existing composition and
   exact installed base path; the new materializer instead applies authenticated
   finite replacements directly to the Git donor map. Its new source-only
   composition and support descriptors now have reviewed integration through
   [portable build preparation V2](../../tests/node-compat/frameworks/nextjs/next-native-portable-build-preparation-v2/README.md).
   It explicitly selects all435 native/387 support/3 embedding files and
   removes the historical compiled-output prerequisites. The real ten
   generator checks passed on that fresh tree; the
   [generator DATA review](../../tests/node-compat/frameworks/nextjs/next-native-portable-generator-root-results-v1/actual-review/README.md)
   retains them. V2 authenticates the indexed producer plan and narrow Root
   grant, exact original selection, Node and argv, plus all61 raw proof
   references. The real receipt passes and25 altered inputs refuse. Root's
   [actual V2 preparation](../../tests/node-compat/frameworks/nextjs/next-native-portable-build-preparation-root-results-v2/README.md)
   passes with an unissued draft and no selection copy. No full build has run;
   these records are source/generator evidence, not compiled metadata.

2. **Build or obtain the coherent guest SpiderMonkey prerequisite.** The manual
   [Intl workflow](../../.github/workflows/spidermonkey-intl.yml) invokes
   `python -B -I …/spidermonkey-intl-build-v1/build.py WORK`, with
   `SM_SAVED_FRAME_EVAL=1` for this generation. It builds fork commit
   `9dab3d6f643e926a340c391ea30968e940390dec` with Intl and the committed
   [SavedFrame patch](../../tests/node-compat/frameworks/nextjs/stacktrace-native-v1/spidermonkey-patch/index.json).
   The [actual CI review](../../tests/node-compat/frameworks/nextjs/spidermonkey-intl-build-v1/ci-patched-root-results-v1/README.md)
   retains all22 successful phases, coherent headers and the defined accessor
   symbol. Its library is `ca04fe5e…`, 637,175,630 bytes. The binary distribution
   and four-directory Firefox FFI payload remain external, descriptor-bound
   archives; committed text evidence is not those binaries. The original
   Actions artifact expires on2026-11-09. Its exact227,965,139-byte ZIP is now
   [retained in a draft release](../../tests/node-compat/frameworks/nextjs/native-bootstrap-artifact-retention-v1/README.md):
   release437352699/asset719685339, matching SHAabbbd377. Uploaded asset digests
   match local files and independent readback passes. Restoration through that
   API requires repository authentication; the draft remains unpublished.
   No archive was repacked and no new library/engine build followed. The
   workflow's 20GiB start/4GiB floor is policy, not measured peak demand.

3. **Restore the single Rust aggregate and offline inputs.**
   [resolve-aggregate-v2.py](../../tests/node-compat/frameworks/nextjs/spidermonkey-intl-build-v1/resolve-aggregate-v2.py)
   renders the six-root aggregate and command plan;
   [run-cargo-phase-v2.py](../../tests/node-compat/frameworks/nextjs/spidermonkey-intl-build-v1/run-cargo-phase-v2.py)
   runs one separately authorized metadata/vendor phase. Actual online
   resolution, vendor and offline locked metadata passed, with all49 prior
   identities preserved inside the84-package lock `dc098f33…`.
   [The DATA review](../../tests/node-compat/frameworks/nextjs/spidermonkey-intl-build-v1/cargo-root-results-v1/actual-review/README.md)
   preserves the lock/source/feature joins. The live lock, config, four FFI
   directories and76-crate vendor tree currently reside in private
   `next-intl-cargo-resolution-v2`. A clean machine needs their authenticated
   materialization, not a newly unconstrained Cargo resolution. The old49 lock
   remains a native source input; the Intl CMake path explicitly selects the84
   lock through `NODE_COMPAT_INTL_LOCKFILE`.

4. **Build the complete portable engine with the UTF-16 afterimage.** The reviewed
   [portable V2 builder](../../tests/node-compat/frameworks/nextjs/next-native-portable-build-preparation-v2/run.py)
   is the next full-build path. It preserves the existing real CMake/Rust
   commands, offline policy, one-job limit and3GiB start/1GiB phase guard while
   selecting the fresh825-file input tree and genuine fresh generator proof.
   The [unissued input draft](../../tests/node-compat/frameworks/nextjs/next-native-portable-build-root-results-v2/README.md)
   now binds the genuine tool/SpiderMonkey/Rust fields and fresh generator
   proof. The actual read-only builder input check passes1,767 file descriptors,
   ten inventory descriptors and22 public+2 private manifests, with independent
   field review. No required field or file is missing; full live tool-tree
   reauthentication still belongs to launch. Build/configure permissions remain
   NULL, with insufficient current headroom. A new full build and its new metadata must pass the original
   whole-app contract; neither the old engine identity nor old compile rows
   may be projected onto it.

   The historical tested chain first built V7, then compiled a UTF-16 delta. Its
   existing
   [V4 builder](../../tests/node-compat/frameworks/nextjs/next-native-build-candidate-v4/run.py)
   accepts `python3 -I -B …/run.py --authority AUTHORITY`. Its `command_plan`
   performs direct Rust1.88 version/sysroot checks, then real
   `cmake -S COMPONENTIZE_SOURCE -B BUILD -G Ninja …`,
   `cmake --build BUILD --target starlingmonkey_embedding --parallel 1 -- -d keeprsp`,
   and read-only Ninja command harvesting. The full flag set comes from the
   [base plan](../../tests/node-compat/frameworks/nextjs/next-native-build-candidate-v3/plan.json)
   plus the [Intl additions](../../tests/node-compat/frameworks/nextjs/next-native-build-candidate-v4/plan.json),
   including Intl ON, direct preinstalled Rust, offline locked Cargo and runtime
   entropy. Debug/GC/OOM/BORROW/reset probes stay off. Actual V7 compiled80 rows
   plus the separate embedding; [its review](../../tests/node-compat/frameworks/nextjs/next-native-build-v4-root-results/actual-review/README.md)
   binds patched headers/library, lock, sources and real link inputs.

   The working `4623640b…` engine additionally uses the
   [UTF-16 delta V2](../../tests/node-compat/frameworks/nextjs/next-native-module-utf16-delta-candidate-v2/run.py):
   `python3 -I -B …/run.py --authority AUTHORITY`. Five direct phases compile
   one `module-kernel.cpp` through a one-file VFS overlay, replace its private
   archive member, run `llvm-ar s`, relink, then run `wasm-opt --strip-debug -O3`.
   [Actual metadata](../../tests/node-compat/frameworks/nextjs/next-native-module-utf16-delta-root-results-v1/actual-review/README.md)
   `726d69cf…` records one fresh frontend,79 reused baseline rows and the retained
   embedding. A clean full build with this afterimage may be a simpler future
   recipe, but has not replaced this tested full-build-plus-delta chain.

5. **Restore the packaging tools and guest-contained adapter.** The constructor
   uses the private ComponentizeJS0.23/Jco1.40 package with genuine Wasm splicer
   `61685a01…` and adapter `d30ade5b…` (49,672 bytes). The
   [CLI build](../../tests/node-compat/frameworks/nextjs/next-preview1-adapter-cli-build-v1/README.md)
   and [adapter publication](../../tests/node-compat/frameworks/nextjs/next-preview1-adapter-publish-v1/README.md)
   retain their real Cargo/offline and finite binary transformation mechanisms.
   Source afterimages and pins are committed; the package installation, vendor,
   native CLI and adapter binaries are external. npm install alone does not
   establish that private package/splicer identity. The baseline source
   acquisition gap is now closed: [the exact upstream commit archive](../../tests/node-compat/frameworks/nextjs/componentize-source-origin-v1.json)
   for ComponentizeJS0.23.0/4d812f5a downloads publicly and byte-equals the
   captured8178fb67 archive,162,093 bytes. Its270 regular files become271 only
   after the later provenance marker is added. No extraction or package build
   was performed for this acquisition check. Reconstructing the generated
   61685 splicer/private package, offline tool dependencies and exact adapter
   provenance remain separate requirements; npm install alone cannot replace
   them.

6. **Build the unchanged application and record fresh generated inputs.**
   [app-fixture](../../tests/node-compat/frameworks/nextjs/app-fixture/package.json)
   and its npm lock pin Next16.4.5/React+DOM19.3.1. The existing
   [run.mjs](../../tests/node-compat/frameworks/nextjs/run.mjs) copies it outside
   the checkout, uses Node22.14's `npm-cli.js ci --ignore-scripts --no-audit
   --no-fund`, runs `next build --webpack`, then copies `.next/static` and
   `public` into `.next/standalone`. The fixture's `fixtures/message.txt` is part
   of the runtime packaging contract. This historical driver also executes the
   Node/bundler corpus. The new [isolated app CLI](../../tests/node-compat/frameworks/nextjs/next-app-build-v1/README.md)
   extracts these stages with a read-only default/`--plan`, explicit Node/npm
   inputs, private cache/configs and a fresh `--output` build action. Its57
   inert Source tests pass. The [first isolated actual build](../../tests/node-compat/frameworks/nextjs/next-app-build-root-results-v1/actual-review/README.md)
   now passes four owned phases, raw0/clean, with original inputs preserved.
   The [official Node/npm acquisition](../../tests/node-compat/frameworks/nextjs/next-app-tools-bootstrap-v1/README.md)
   binds the Node22.14 archive to its published HTTPS checksum and extracts
   npm10.9.2 privately; OpenPGP verification is not claimed. The fresh standalone
   inventory binds2181 files/48,714,867 bytes,425 descendant directories and
   new build/action IDs. Its directory schema omits the root and its tree lacks
   a warmed `.next/cache`: runtime admission must explicitly handle the root
   identity and declare an empty cache mountpoint in the owned copy. Two of five
   browser asset pins changed. New nativeV7/stockV3/browserV3 Sources and the
   [fresh-app regression CLI](../../tests/node-compat/frameworks/nextjs/next-app-runtime-root-results-v1/README.md)
   now pass independent review and their first actual matched Node/Wasmtime
   pair passes24HTTP/cache/stream/2strict-browser checks. The fresh app also
   passes cold8 on stock wasmCloud with the same1c31 component. Earlier capacity
   holds ended above the unchanged1GiB Root start floor. The portable paired and
   cold DATA readers both pass Root readback; no native engine rebuild or
   clean-machine reproduction follows from these retained-artifact trials.
   The historical accepted app has2218 files/48,808,299 bytes; its inode/mode/path
   records cannot be cast into evidence for this new build.

7. **Construct, audit, then run.** The committed raw
   [entry V5](../../tests/node-compat/frameworks/nextjs/next-component-entry-fixes-v5/index.json)
   retains six bounded facades during INIT and the observed-I/O abort policy;
   the deployed loader reads the real
   app from `/app`. Its
   [constructor V5](../../tests/node-compat/frameworks/nextjs/next-entry-fixes-construction-v5/run.py)
   accepts `python3 -I -B …/run.py --authority AUTHORITY --sha256 AUTHORITY_SHA`.
   It configures the official tool shim's single WIT-directory preopen, uses a
   held cwd outside output/TMPDIR, calls the genuine raw-source API, saves the
   entire return before checks, then validates and emits WIT. Keep stdio, random,
   clocks and HTTP; disable only `fetch-event`; AOT/debug remain off. Admit only
   the selected13 standard0.2.10 interfaces and incoming-handler export. No
   textual version rewrite, bundler substitute or app mount during INIT is used.
   The current [V7 deployment runner](../../tests/node-compat/frameworks/nextjs/wasmtime-deployment-candidate-v7/run-owned.py)
   binds the constructor, engine, metadata, source families and fresh app
   inventory before serving. The retained-artifact regression wrapper selects
   Wasmtime42.0.1 reuse128/idle60, a physical0444/0555 app copy, fresh nested
   writable cache, explicit origin and the unchanged24HTTP/cache/stream/2browser
   contract. Physical modes do not prove read-only WASI descriptor rights.

## Remaining portable bootstrap work

The existing V4 builder deliberately reuses workstation-private SDK30,
Binaryen123, wasm-tools1.235, Wasmtime42, weval0.5.1, Corrosion0.5.1 and direct
Rust1.88/wasip1 roots. Their archive pins, provenance and current whole-tree
inventories are recorded; it does not install them on a clean machine. OpenSSL
3.0.17 is freshly extracted privately because its build can mutate source.
Node/npm, Python, CMake/Ninja, cbindgen, the private packaging toolchain and the
pinned Chrome/Playwright setup also require explicit acquisition and validation.
These macOS ARM64 paths and host executables are not a portable OS image.

The source-selection and generator-admission layer is now reviewed and exercised
without a native build. The next build-portability work is the external layer:
restore authenticated external archives and Cargo inputs; relocate finite source
composition without changing content; create fresh tool/app inventories and
late authorities; then execute the existing stages in this order. Keep new
outputs and actual metadata separate from captured successful artifacts. Pass
the full contract on the genuinely rebuilt generation before calling this a
clean-machine reproduction or considering production promotion. The accepted
production checkpoint remains foundations-v13.

The [bootstrap input manifest](../../tests/node-compat/frameworks/nextjs/native-bootstrap-inputs-v1.json)
now records that external layer explicitly:25 payload pins with retained
witnesses,84 aggregate Cargo packages,76 vendor-checksum records,78 npm transport
rows and an eight-step restoration order. The read-only checker verifies37
repository records and all25 pin joins;51 DATA refusal cases and independent
review pass. Root's [actual readback](../../tests/node-compat/frameworks/nextjs/native-bootstrap-inputs-v1-root-readback.json)
also passes, including optional hashes of the two existing SM/Componentize
archives. It performs no acquisition, extraction, dependency resolution or build.

```sh
python3.12 -I -B tests/node-compat/frameworks/nextjs/check-native-bootstrap-inputs-v1.py --plan
```

This metadata helper needs Python3.11+ for `tomllib`; the pinned native build
interpreter remains Python3.9. Optional `--verify-local ID=CANONICAL_FILE` hashes
an already-owned payload. Availability is a dated metadata observation; the
checker does not probe it live. The eight official Rust-component rows are
reported metadata, with no channel-snapshot rehash or archive verification.

The [captured installed npm lock](../../tests/node-compat/frameworks/nextjs/native-bootstrap-npm-installed-lock-v1.provenance.json)
is now retained as exact text, and the78 normalized rows are independently
rederived from it. Historical filesystem keys and extraneous earlier tools are
preserved as DATA. It is not an npm-ci root lock or proof of a reconstructed
private package. The first [relocated Cargo source restoration](../../tests/node-compat/frameworks/nextjs/native-cargo-restore-root-results-v1/README.md)
now completes raw0 from75 checksum-pinned registry archives plus authenticated
Firefox/base donors. It restores3506 payload files with the exact final84-package
lock. The original V1 readback failed on APFS root nlink6→7 after receipt
publication; that failure and receipt remain unchanged. A separately reviewed
V2 reader validates all3507 files including receipt,464 directories including
root, stable root identity, exact membership and current physical bookends.
Source-stage process observation and structural admission remain distinct.
No Cargo metadata, compiler or guest result follows from this restoration.

The separate [actual offline metadata query](../../tests/node-compat/frameworks/nextjs/native-cargo-offline-verify-root-results-v2/README.md)
now passes against those fresh roles: new `65544c7b…` metadata, all 84 logical
packages/features/dependency edges, six root dependencies, exact fresh manifest
paths, raw exit 0 and clean original ownership. Source/tool bookends pass.
The complete 23-file output is retained as indexed DATA. The earlier V1 verifier
failed before output or Cargo on a strict boolean flag bug; its failure remains
preserved, and V2 changes only the two entry predicates. Cargo's observed
`rustc` information query is not a source-compilation result.

Remaining work includes implementing and reviewing the
[V3 builder integration](../../tests/node-compat/frameworks/nextjs/next-native-portable-build-preparation-v3/change-plan.json)
that consumes this actual proof and fresh roles,
exact host-tool/cbindgen/Corrosion acquisition, generated61685 package rebuild,
original988 adapter upstream provenance, and sufficient capacity for the fresh
full native build and subsequent application gates. The committed988 bytes
remain available; a same-size official adapter cannot replace their identity.
