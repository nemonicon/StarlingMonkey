# Retained native dependency controls

The actual profile3 Wasmtime run passed GET/GET/POST: all 16 canonical controls
passed in each complete response, **48 records total**. POST read 21 request
bytes and returned HTTP 200. The successful host shut down with the requested
SIGINT/raw0; the owned Node monitor also returned 0 with no timeout, signal,
forced cleanup, remaining process or cleanup error. Full raw responses,
Wasmtime streams, monitor/start/process records, authority and construction
text are retained byte-for-byte through `copy-map.json`.

| Run | Responses | Passing records | Monitor exit | Retained disposition |
| --- | --- | ---: | ---: | --- |
| Original ALS oracle | GET 500 | 0 | 1 | Failed; probe incorrectly expected captured stores inside disabled `exit` |
| Profile2, original adapter | GET 200/GET 200/POST 500 | 32 | 1 | Failed; POST incoming stream reached the wrapped-WIT error mismatch |
| Profile3, corrected adapter | GET 200/GET 200/POST 200 | 48 | 0 | This bounded dependency baseline passed |

The first two failing records remain unchanged and unaccepted. Their parser
errors describe the saved HTTP500 HTML, while full Wasmtime stderr retains the
earlier guest diagnostics. The actual pinned default Node 22 oracle shows both
captured callbacks return undefined inside disabled `exit`; the corrected probe
instead tests capture/restoration from a distinct enabled caller store, while
keeping a separate exit undefined control. Its full actual host result is
retained under `inputs/`. No native ALS patch was needed.

The profile3 Source adapter unwraps the actual binding's own DATA `payload`
for `closed` and `last-operation-failed`. Its source-only host regressions are
retained separately; the actual successful POST establishes ordinary EOF/body
handling for this component/run. It does not establish all failure paths.

The curator authored the runner and adapter and discloses that relationship;
this is a retained-DATA audit, not an independent Source-peer approval. It
authenticated 65 existing original files before/final, including exact
component/engine/metadata descriptors, but copied no Wasm binary or application
tree. Retained execution guards report original-input and read-only-copy
preservation; this review did not repeat the full application/source-tree
guards. The oldest runtime result predates its `inputSourceIndex` field; that
role is joined from its actual fixed plan and construction artifact, without
altering the original result. A retained curator-local failed reader records
the initial newer-wire assumption before this correction.

From any relocated checkout containing this directory, run:

```sh
python3 -B check-retained.py
```

The checker reads only this directory, authenticates all indexed membership and
copy hashes before semantic inspection, and validates whole response records
and terminal facts. It executes no Node, native engine, host, guest or crypto
operation. `curate.py` is an authoring-only writer and must not be rerun in the
held directory.

Scope is these 16 dependency controls only. The records do not establish full
Next application serving, same-instance identity, deployed reset/resnapshot,
GC/Store teardown, public profile adoption, security or cost gates. The three
requests used configured reuse 32/idle 60; that configuration alone is not
instance-identity proof. No later action is granted by this baseline.
