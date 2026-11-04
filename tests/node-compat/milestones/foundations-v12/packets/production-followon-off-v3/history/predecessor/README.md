This is a **source-only OFF follow-on activation correction**. It preserves
[v1](../production-followon-off-v1/README.md) and binds the same five entries to
exact [common v4](../production-regression-candidate-v4/README.md) indexd0411aaf.
All actual engine pins remain null; every entry fails there before loaders,
fixtures or output. No compiler, driver, packager, component, guest or Wasmtime
was run.

Only common import/index wiring and source-seal membership change. The new733
input closure includes the live `98822428…` adapter physical path, the complete
common666-input closure and preserved source/fixture ancestry. All five whole
case/control sections and original fixture bytes remain identical. Reversing
declared transformations restores all original m0.11 runner bytes; comparing
new bodies to v1 after undoing the common import path gives exact equality.

Preflight still captures an immutable local manifest digest; post-run common
recheck verifies original primitive pin/manifest digests first, then the local
manifest hash is checked before parsing/following rows. Fresh outputs, exact
actual inner guards, layered strict policy, parent84a/current9d distinction,
complete retained controls and exclusive completion seals remain unchanged.
Source paths do not select a different engine or an unreviewed pin export.

Host checks passed28 cases (the inherited27 plus live-adapter physical-path
membership);15 syntax checks,15 ancestry inputs and current306 native policy
hashes passed. The original scratch tamper tests and v4 missing/tampered owned
adapter cases remain preparation evidence. No actual artifact-success or
runtime branch has executed. Old packets, source files and latest reports are
unchanged.

The [entry contract](entry-contract.json) is byte-identical to v1: entries
`run-{sync,runtime,late,callbacks,stream-web}.mjs`; strict output variable
`NODE_COMPAT_STRICT_EVENT_OUTPUT`, Web variable `NODE_COMPAT_STREAM_WEB_OUTPUT`;
primary reports `private-ticks-{sync,runtime,late,callback}-results.json` and Web
`results.json`. All future passes also require exit0 and
`followon-admission-complete.json`. The full case counts and explicit
getter/Symbol/GC/reset/ALS/process and fatal-discard limitations are preserved in
v1 and the unchanged entry contract. No API, capability, world or callback-policy
change is made.

Actual reviewed production freezes/pins and a reviewed activation revision are
still required. Standalone unreviewed artifact exports never activate these
entries. No complete Node profile or new runtime acceptance follows.

For an independent host-only rerun, choose a fresh report path:

```sh
NODE_COMPAT_FOLLOWON_HOST_TEST_OUTPUT=/tmp/off-followon-v2-NEW.json \
  /tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node \
  tests/node-compat/foundation-scheduler/production-followon-off-v2/test-host.mjs
```

[source-receipt.json](source-receipt.json), [runner-transformations.json](runner-transformations.json)
and [index.json](index.json) freeze the exact correction; no binary was copied.
