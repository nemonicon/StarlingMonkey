This is a **driver-only source correction** to the preserved
[link1 consumers-v1](../diagnostic-link1-consumers-v1/README.md). It closes that
driver's live Preview1-adapter pre/post input gap: the new manifest contains32
inputs, including the exact live repository adapter `98822428…`. No adapter
binary is copied into this packet.

The native acceptance contract is unchanged. `preflight.mjs`, `link-evidence.mjs`,
`consumer-pins.json`, `freeze-diagnostic-engine.py`, `build-one-diagnostic.py`,
`diagnostic.cmake` and `test-extension.cpp` are **byte-identical** to v1. Producer
pins3763b45d, recipe24e5dc9a, policyf0f83e5e, helperc80e47e3, the fixed
`/tmp/starling-node-compat/foundation-scheduler-link1-v1/native-freeze` root and
build namespace remain the same. The schema3 freezer/metadata acceptance can
therefore consume the same valid v1-built link1 engine: no new native recipe,
configuration, diagnostic IDs or build is requested. This compatibility is
source-checked; no real metadata/freeze success was executed here.

`run-components.UNEXECUTED.mjs` adds only32-input/adapter-membership assertions
and driver-v2 report fields. The full packaging/invocation/case section and all
14 fixture/worker/oracle/CMake/CPP inputs are unchanged. It retains10 components,
five initialization failures, three fresh fatal/discard observations paired with
three successful controls, all Node phase/classic/INIT/late traces, FIFO/argument/
work/queue-owner checks, retained calls and fresh Wasmtime. Generic traps still
do not prove original error cause. Release-GC scope remains distinct from an
ordinary Release run, and Reset/public process/ALS remain OPEN.

The existing verifier captures its initial manifest digest and parsed rows
privately, checks that digest before following rows, then rehashes every listed
path before packaging and after future calls. The adapter remains separately
prehashed before the packager opens its path; it is now also in that complete
pre/post list. `freeze-inputs.py` extends the same24-input ancestral mapping to32
and refuses an existing output.

Host-only validation passed46 unchanged link-contract tests plus10 new source/
adapter-seal checks. The new tests evaluate **only the exact extracted file
verifier function** in a Node VM with owned32-file scratch data. Missing/tampered
adapter data and changed manifests fail; no whole driver, adapter, toolchain,
producer, launcher, freezer, component, guest or host is executed. Source/syntax
checks also prove identical native acceptance files, lifecycle definitions,
fixture bytes and complete corpus. Reports distinguish this from real engine
acceptance. The original packet and all indices remain unchanged.

`driver-pins.json` describes this32-input source revision. The copied
`native-consumer-ledger.v1.json` is historical v1 source-ledger data; it is not
read by the driver and its old31-input count is not this revision's count.
Actual native pins remain the unchanged `consumer-pins.json` and referenced
producer pins. No engine hash is invented. Root's separately authorized native
build/freeze continues independently; **do not run the copied launcher** to
start a second build.

After Root reviews the source seal and freezes the actual link1 engine using
the unchanged v1 freezer, the future entry is this packet's
`run-components.UNEXECUTED.mjs` with the existing explicit diagnostic opt-in,
engine/frozen source/Wasmtime settings and a fresh `NODE_COMPAT_TICK_OUTPUT`.
No component run is authorized or claimed by these preparation results.

The host-only checks support fresh independent reports:

```sh
NODE_COMPAT_LINK1_CONSUMER_TEST_OUTPUT=/tmp/link1-consumer-check-NEW.json \
  /tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node \
  tests/node-compat/foundation-scheduler/diagnostic-link1-driver-v2/test-consumers.mjs
NODE_COMPAT_LINK1_ADAPTER_TEST_OUTPUT=/tmp/link1-adapter-check-NEW.json \
  /tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node \
  tests/node-compat/foundation-scheduler/diagnostic-link1-driver-v2/test-adapter-seal.mjs
```
