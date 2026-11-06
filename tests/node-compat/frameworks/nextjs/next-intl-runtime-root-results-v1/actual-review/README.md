# Actual Intl engine runtime baseline

The unchanged Next16.4.5 standalone application runs inside the experimental
StarlingMonkey component on stock Wasmtime42.0.1. Its original full success
contract remains **failed**:11/24 HTTP checks pass; cache JSON parsing prevents
the strict incremental-stream and two browser stages. Successful SSR includes
home, layouts, dynamic/query pages, action-form markup, client-counter markup,
completed Suspense, redirects and404s. No production profile is promoted.

The strict Unicode differential passes36/36 records, including all property
expressions and Kelvin folding. The dependency component passes48/48 controls
across GET/GET/POST. Stack checks pass9/12 selected records: hooks, descriptor
and thrown identity work, and exact depd location extraction succeeds. The
remaining three records differ only because the first anonymous frame has a
SpiderMonkey inferred function name while Node reports null. That run retains
raw1/parityfalse; a successful DATA reader never turns it into acceptance.

The separate diagnostic component changes console/Buffer function identities
to report own-data error causes and input shapes while preserving return and
thrown values. It also passes11/24 HTTP checks and is not a production fix.
It confirms Next's JSON response piping rejects the genuine AbortSignal.
The exact guest fork's [ReadableStream implementation](https://github.com/bytecodealliance/firefox/blob/9dab3d6f643e926a340c391ea30968e940390dec/js/src/builtin/streams/ReadableStream.cpp#L421-L431)
requires embedder signal registration; the [pipe state implementation](https://github.com/bytecodealliance/firefox/blob/9dab3d6f643e926a340c391ea30968e940390dec/js/src/builtin/streams/PipeToState.cpp#L1151-L1183)
also leaves abort algorithms unimplemented. Registering its class alone would
therefore be insufficient. A small audited guest facade is being developed.

Other observed failures are `fs.createReadStream.root` refusal, a CJS expected
Unicode literal appearing as Latin1-decoded UTF8, and a POST Buffer.from refusal
for an ArrayBuffer view whose exact type is still being isolated. The assertion
reports actual `€` first: this does not establish a broken UTF8 decoder.

`ledger.json` and `data.tar.gz` retain129 complete UTF8 files/931,443 bytes:
all five result/outer-monitor trees, raw HTTP bodies/client logs, source-index
and Root-authority roles, and both original Node oracle observations. Identical
read-only app copies, application cache bytes and ephemeral XDG state are not
duplicated; each run retains its original source/cache inventory descriptors.
All129 originals matched before and after publication. Component/library/host
binaries are hash references, not copied into this baseline.

Run `python3 -I -B check.py` from this directory for future DATA regression
review. It authenticates the closed family/archive, checks owned cleanup and
preserved inputs, recomputes selected comparisons/counts, and requires the full
Next and stack failures to remain failures. It launches no guest. To reproduce
ordinary execution, use the separately sealed collectors and exact late Root
descriptors under `intl-component-root-results-v1`; new run IDs and fresh output
directories preserve this baseline. Whole application contracts remain in
`wasmtime-deployment-candidate-v4/run-contracts.mjs` without weakened cases.
