# Reproducing the experimental Next generation

The selected full Next smoke passes on component `55f05e3d…`, engine
`4623640b…`, with the first and repeat Wasmtime runs and matched Node control
retained in the [milestone report](nextjs-wasm-milestone-2026-11-06.md).
**A clean-machine build has not been demonstrated.** The existing
[regression command](../../tests/node-compat/frameworks/nextjs/run-native-next-regression.py)
reuses exact private artifacts; it does not bootstrap them. This plan is a
read-only source audit, not another build or a claim of bit-for-bit rebuilds.
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
   composition and support descriptors still require reviewed integration with
   the builder's path-bound late inputs; they are not compiled metadata.

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
   archives; committed text evidence is not those binaries. Artifact retention
   and a durable download/bootstrap path must be handled explicitly. The
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

4. **Build the complete V7 engine, then the recorded UTF-16 delta.** The existing
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
   establish that private package/splicer identity. A portable tool-package
   reconstruction and artifact distribution step is still required.

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
   inert Source tests pass; **the npm/Next build path remains unexecuted**.
   The working app inventory binds2218 files/48,808,299 bytes. Fresh generated
   build/action IDs and file hashes require a genuine new inventory and checks;
   old inode/mode/path records cannot be cast into evidence for a new build.

7. **Construct, audit, then run.** The committed raw
   [entry V4](../../tests/node-compat/frameworks/nextjs/next-component-entry-fixes-v4/index.json)
   installs six bounded facades during INIT; the deployed loader reads the real
   app from `/app`. Its
   [constructor V4](../../tests/node-compat/frameworks/nextjs/next-entry-fixes-construction-v4/run.py)
   accepts `python3 -I -B …/run.py --authority AUTHORITY --sha256 AUTHORITY_SHA`.
   It configures the official tool shim's single WIT-directory preopen, uses a
   held cwd outside output/TMPDIR, calls the genuine raw-source API, saves the
   entire return before checks, then validates and emits WIT. Keep stdio, random,
   clocks and HTTP; disable only `fetch-event`; AOT/debug remain off. Admit only
   the selected13 standard0.2.10 interfaces and incoming-handler export. No
   textual version rewrite, bundler substitute or app mount during INIT is used.
   The final [V5 deployment runner](../../tests/node-compat/frameworks/nextjs/wasmtime-deployment-candidate-v5/run-owned.py)
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

The next useful implementation is one reviewed bootstrap/materialization layer:
restore authenticated external archives and Cargo inputs; relocate finite source
composition without changing content; create fresh tool/app inventories and
late authorities; then execute the existing stages in this order. Keep new
outputs and actual metadata separate from captured successful artifacts. Pass
the full contract on the genuinely rebuilt generation before calling this a
clean-machine reproduction or considering production promotion. The accepted
production checkpoint remains foundations-v13.
