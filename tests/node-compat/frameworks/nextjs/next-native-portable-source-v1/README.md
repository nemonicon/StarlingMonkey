# Portable working Next native source

`materialize.py` reconstructs the exact **source content** selected by the
working V7-plus-UTF16 generation using committed repository donors. It requires
no private SDK, tool, engine, Cargo vendor, metadata file or network access.
Default invocation and `--check` only read and hash files:

```sh
python3 -B -I tests/node-compat/frameworks/nextjs/next-native-portable-source-v1/materialize.py
```

An explicit canonical absolute `--output` creates a fresh tree outside the
checkout. Existing outputs, aliases and unsafe paths refuse:

```sh
python3 -B -I tests/node-compat/frameworks/nextjs/next-native-portable-source-v1/materialize.py \
  --output /private/tmp/next-native-source-FRESH
```

The output contains:

| Directory | Role | Files |
| --- | --- | ---: |
| `source` | Native-policy sources |435 |
| `build-support` | Build support, including alternate Intl Cargo template |387 |
| `componentize-source` | Embedding CMake/header/CPP |3 |

All825 payloads total7,530,166 bytes. The role/path/mode/hash fingerprint is
`47755843d22d8e0e355ddc56e263e30aa997b4bd963fac50609639913c5c35df`.
The selection starts with the committed824-row C2 donor map, applies the five
exact V7 replacements and one Cargo support addition, then replaces only
`module-kernel.cpp` with the real UTF16 afterimage. Every replacement checks its
original hash. Repository-relative donor names resolve from this script's
checkout; absolute paths inside historical input maps are inert provenance,
never runtime source locations. All822 distinct donors are read with hash,
regular-file/no-alias and before/final checks. Files are copied exclusively,
fsynced with declared modes, distinct from donors and nlink1. No donor executes.

`composition.json` records the new435-file native root, actual repository input
descriptors and source-only flags. Its native fields match the shape read by the
existing native builder; it is not old compiled metadata. The separate
`source-materialization.json` records all825 copied files with their fresh paths,
roles and modes. The builder's old support/tool paths and late authorities are
still workstation-specific: consuming this portable layout requires an explicit
reviewed caller/authority integration, fresh installed-generator checks and
actual compilation. This copier does not silently retarget the old builder.

The first Source-only test run passed35 cases. It compared every role/path/
SHA/byte entry against actual V7 declarations with exactly the UTF16 substitution,
created complete copies and ran the real CLI from a relocated finite repository
closure. It also refused overwrite, traversal, symlink ancestors, hardlinks,
tampered bytes/modes, extra files and changed donors. Hardlink negatives use only
owned scratch. Temporary test copies were removed; originals were unchanged.
`checks.json` is the typed author observation of that actual run, not a retained
raw monitor transcript. The historical metadata descriptors and comparison
boundary remain in `historical-comparison.json`; neither is required to use the
portable materializer.

To repeat the finite copy/relocation tests without private evidence:

```sh
python3 -B -I tests/node-compat/frameworks/nextjs/next-native-portable-source-v1/test-materialize.py
```

Optional `--baseline-metadata FILE --delta-metadata FILE` rechecks the genuine
historical declarations when those exact external files are available. The
first such test passed. One separate fresh retained materialization is recorded
in `materialization-observation.json`; its composition hash is `7db73397…`.

No CMake/configure, generator, compiler, Cargo/Rustup, tool installation, CI,
engine, component or guest ran. These files close the finite source-content
materialization step, not clean-machine engine reproduction, build equivalence,
metadata admission or runtime acceptance. SDK/tools, coherent patched Intl
library, offline84-package Rust closure, app build and package/adapter acquisition
remain separate in the [reproducibility plan](../../../../../docs/node-compat/nextjs-reproducibility-plan.md).
