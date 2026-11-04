This is a **source-only activation correction**, derived from preserved
[common v3](../production-regression-candidate-v3/README.md). It adds the live
repository Preview1 adapter `98822428…` to the captured pre/post manifest.
All665 old manifest rows remain identical; the new manifest has666 rows.
Frozen/control copies cannot replace that physical live path. The
[activation gap note](../activation-seal-gap-v1/README.md) preserves the earlier
finding; v3 and its indices remain unchanged.

The production guards and runner semantics are unchanged. `admission.mjs`,
`preflight.mjs`, all three entries, both allocator sibling bodies and their
reversible transformations are byte-identical to v3. Primitive initial pin and
manifest digests, digest-before-parse/rows, private frozen-copy checks, all
finite source/configuration/Rust/OpenSSL/stock-host guards and the seven owned
scratch cases remain. No compiler, component driver, packager, guest, Wasmtime
or native allocator operation was run by this preparation.

All actual engine pins stay `null`. Every entry stops at that gate before any
toolchain/output. The separate production-artifact exporter must not activate
these consumers: it can publish unreviewed observations only. Actual reviewed
pins and a reviewed activation revision are required. The expected frozen
receipt remains schema1/`immutable-release-engine-frozen`, source306/external3,
native61/strict4/embedding1 and recipe869. No diagnostic projection or invented
engine hash is accepted. RuntimeOnly remains in its separate capability packet.

Host checks passed45 cases: the original41 are retained, with live-path/actual
666-file membership checks and missing/tampered **owned scratch adapter**
refusals. Twelve syntax checks, old29 ancestry and current306 native source
hashes passed. The scratch adapter is plain data; it is never executed. The
fixed-artifact success branch remains unexecuted. No old fixture, accepted
report or native source was modified.

The retained core/allocator/allocator-GC scope, actual v7/v10 controls, eight
native roundtrip GC fixture, output/seal contracts and limitations are described
in the preserved v3 README. This revision changes no API, world, capability,
callback policy, fixture, expected result or report namespace. In particular it
does not establish private-tick GC/ALS, Engine reset, post-fatal reuse or a new
runtime pass. Each future successful entry still requires fresh output, full
body completion, process exit0 and `production-admission-complete.json`.

To rerun host-only checks, choose a fresh report path:

```sh
NODE_COMPAT_REGRESSION_HOST_TEST_OUTPUT=/tmp/common-v4-host-NEW.json \
  /tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node \
  tests/node-compat/foundation-scheduler/production-regression-candidate-v4/test-host.mjs
```

`check-source.py` takes a fresh `NODE_COMPAT_REGRESSION_SOURCE_CHECK_OUTPUT`.
Regenerators are preparation tools, not permission to change sealed evidence.
[source-receipt.json](source-receipt.json) and [index.json](index.json) record the
exact source delta; no binary is copied into the repository packet.
