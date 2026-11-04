# Single-project sequential build preparation, no build yet

This amends the execution topology of the original195-file source/host
checkpoint. Its expression, API proof, four host forms and every original file
remain unchanged. **No CMake configuration, native build, componentization or
measurement has run here.** Root review and a later CPU/disk coordination signal
are required before the two four-job builds. The live m0.9 work proceeds
independently; no production source/selector is edited by this preparation.

Use **one** fixed project at
`/tmp/starling-node-compat/allocunsafe-direct-m0.11-one-project/project`, with one
fixed external embedding source/build subtree under its sibling `build` folder.
Build baseline first; archive its complete engine,293 native source bytes,
support/helper inputs, external embedding inputs, CMake cache/commands/Ninja and
dependency/toolchain hashes **before** switching the two candidate files.
Candidate uses the same absolute paths/toolchain/cache/libraries/flags. The only
tag change names the output artifact/log/receipt; the frozen recipe does not
derive CMake/source/build directories from that tag.

[preparation-results.json](./preparation-results.json) records an actual
source-only rehearsal: all293 project-native input paths match the expected
baseline, switching at those same paths changes **only** buffer-facade.mjs and
factories.generated.h, all28 support/helper inputs stay constant, and baseline
bytes are restored. The project is currently `baseline-prepared`; no baseline
engine exists. [plan-amendment.patch](./plan-amendment.patch) changes the original
two-project plan explicitly rather than silently rewriting its accepted bytes.

## Frozen recipe and private admission

[build-engine.v8.sh](./build-engine.v8.sh) is byte-identical to frozen v8 recipe
`af5b0e8cd34aae6923dacf32bfaf80f8c05c8f12edf014a3ae3c77d58ed2226f`.
[recipe-diff.patch](./recipe-diff.patch) is intentionally empty. Project bootstrap
uses an isolated local clone at audited revision54b3329, then overlays the exact
frozen-v8 native files and reviewed private m0.11 sources. It never copies the
evolving live native tree.

The six archived-v8 harness files, including selector
`711a06add9529e27aceac0775f4349f94b82890e4a4ecf87266c44469a371312`, are copied
unchanged into the private project. Their private use is explicit. The new live
m0.9 guard is neither modified nor bypassed for production, and no nonexistent
new `observed...=OFF` field is inserted. `admitFrozenEngine(arm)` additionally
requires the exact arm-specific293-source map, actual metadata/macros/recipe,
archived file/engine hashes and selected manifest. Version text alone is
insufficient. The same m0.11 module manifest/helper metadata is shared by the
two private experimental source variants; this does not extend the active
production known-profile selector.

The older293-path native inventory excludes some configuration/support inputs.
This preparation separately pins12 tracked files to original Git blobs:
deps/include headers, scripts/cxx-wrapper.in and scripts/wasm-opt, componentize
template and WPT CMake/support files. Sixteen additional recipe/old-harness/
auditor/reviewed-patch files are pinned and verified. Disabled WPT source is
copied for configuration completeness, not compiled or executed as a test.
This is an additional private receipt, not a retroactive assertion that the
earlier inventory contained these paths.

## Controller and safeguards

[prepare.mjs](./prepare.mjs) has already performed only source/file/Git/hash work.
It refuses to overwrite its preparation marker. It does not run CMake, Rust,
compiler, componentizer or timing commands. Shared dependency/archive locations
are explicit symlinks; three source archives are hash-verified. No extracted
library copy is multiplied between arms.

[experiment.mjs](./experiment.mjs) with `--verify` currently passes source/helper/
archive checks only. Its heavy `--build baseline` and `--build candidate` paths
remain **unexecuted**. They require the separate
`NODE_COMPAT_M011_BUILD_APPROVED=1` flag after root authorization, run the same
frozen recipe with four jobs, and preserve raw recipe logs. Candidate admission
requires the completed baseline freeze. Parent toolchain/flag environment is
compared before switching; partial failures retain state for review rather than
automatically retrying or overwriting accepted artifacts.

The linked-archive parser was checked read-only against the existing v8 Ninja
graph, with no compilation or engine execution: it finds30 explicit archives.
`libbuiltin_node_compat.a` is expected to differ because it contains the reviewed
changed code; the other29 archives are held constant. The controller also hashes
all SDK static archives (covering implicit `-l`/runtime inputs) and compiler/
archive tools. Their actual future baseline/candidate values are not yet known.
Candidate post-build comparison requires exact held-constant archives, SDK
inputs, CMake cache and compile-command hashes, external embedding inputs and
actual compile flags. Any mismatch stops before component/performance claims.

After both builds pass, the installed corpus and separate minimal correctness
fixtures must pass with explicit private receipts before a coordinated timing
window. No older v8 timings are numerically transferred, and no part of the old
slowdown is attributed to zero-fill alone. No raw/private memory access, fault/
DEBUG/OOM work or host/runtime modifications are introduced.
