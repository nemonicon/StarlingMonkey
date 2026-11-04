This is a source-only activation mechanism for the future sibling
`production-runtime-activated-v1`. That output has not been created. No engine
or consumer pin is invented or modified by this proposal. The two sealed inputs
are the integration191 index5826a3df… and mandatory completion-amendment12
index76e73533…. Both remain unchanged.

After independently checking **this candidate's exact index**, Root may invoke
the producer with exactly four arguments:

```sh
python3 tests/node-compat/foundation-classic-streams/runtime-activation-candidate-v1/activate.py \
  REVIEWED_PINS_JSON EXPECTED_PINS_SHA256 ROOT_REVIEW_JSON EXPECTED_ROOT_REVIEW_SHA256
```

Missing, null, malformed and unreviewed authority is rejected before artifact
imports, engine access or output creation. The reviewed document must contain
all four genuine variants and use the existing reviewed pin contract. The Root
receipt must have schemaVersion1, state
`ROOT_REVIEWED_REAL_CLASSIC_PRODUCTION_FREEZES_V1`, the reviewed pins digest,
sourceFiles342, recipe71b48d2e…, all four labels, and matching engine/receipt/freeze
tuples plus independent proof digests. It must not claim runtime acceptance.

The producer reuses the sealed artifact exporter's read-only verifier and
compares every actual frozen field to the reviewed rows. There is no306 or
diagnostic projection and no duplicate342 metadata backend. The original
`classicPreflight({variant})` backend is copied with only two integrity-wiring
edits. All five source placeholders are explicitly bound; its compiled bytes
are checked against captured sealed-template bytes during every recheck. It
returns the same actual engine/source/metadata/pin/variant and private-primitive
`recheck()` API expected by the separate regression replay packet.

The new runtime family preserves all guest, checks, oracle, refusal and run-entry
bytes. Its only harness changes are the exact reviewed completion driver and
new completion helper. The old real Node oracle results are copied as oracle
evidence, never represented as a new guest result. The activated family will
still be **runtime-unexecuted** when source creation completes. A separate Root
review of its index and actual read-only preflights must precede guests. An
external collector must require completion.json, rehash every listed output,
and require actual raw terminal exit0; neither file alone admits a run.

The fresh consumed-input manifest binds current live342 bytes, all four frozen
inventories and receipts, Root's exact original documents and byte copies,
both complete source packets, producer sources, actual Node oracle inputs,
the live adapter988224…, installed selectors, componentizer guards/patches/lock,
Node/Wasmtime executables, and both complete selected tool roots:

* `/tmp/starling-node-compat/native-toolchain-lock`
* `/tmp/starling-node-compat/import-abi-clock-v2-build/package`

There are no implicit cache exclusions. Every ordinary file is hashed and the
exact directory/file/link membership is rechecked. Known npm file links retain
exact link text, canonical targets and target hashes. The patched package's
node_modules directory link must resolve inside the separately inventoried
toolchain root. Other escaped links or special files fail closed. This tool-link
handling does not relax ordinary native-source, WIT, adapter, engine or frozen
inventory symlink rejection. NAPI_RS overrides, NODE_PATH/NODE_OPTIONS, legacy
packager selection and unexpected toolchain/componentizer/host paths are refused.
Hashing cost is outside performance measurements.

The input manifest is hashed before parsing or following its rows. Rechecks use
fixed primitive pin/manifest digests and private frozen-receipt expectations.
The final payload is written exclusively into an absent staging directory,
read back, and renamed only to an absent final path. Any failed stage is retained;
there is no overwrite, automatic cleanup, binary copy or guest execution.
This is not a hostile concurrent-filesystem-race guarantee.

Preparation executed only12 owned tiny-text integrity checks, six negative
authority-document checks, syntax/source comparisons and one authorized
read-only check of Root's actual authority documents. No artifact verifier,
activation producer, toolchain loader, componentizer, compiler, guest or target
host was executed. All older null-pin packets remain null and immutable.
Actual source creation, four read-only preflights, disabled admission control
and ordinary/Runtime/GC component gates are subsequent separately authorized
steps. No Node API version, public nextTick/process, ALS, reset, cancellation,
memory or performance support is promoted here.
