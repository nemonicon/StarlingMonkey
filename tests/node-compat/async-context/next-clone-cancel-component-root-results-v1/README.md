# Repaired-engine lifecycle result

The first real component passes on Wasmtime 42.0.1 against Node 22.14.0:
two context runs with 95 assertions each, the original cloned-response
cancellation case, and four rejection/EOF/error follow-ups. All four HTTP 200
bodies are complete. See [the result and limits](../../../../docs/node-compat/nextjs-clone-cancel-results.md).

```sh
python3 -I -B tests/node-compat/async-context/next-clone-cancel-component-root-results-v1/check-saved.py
```

The checker verifies all 99 retained payloads and recomputes typed comparisons,
HTTP completion, original command cleanup and the 13 standard WASI imports.
It reads no original absolute paths and invokes no tool or helper. The same
check passes from an isolated 101-file copy of staged Git blobs; `-O` is refused
before payload reads. Engine and component binaries are not retained.

`compare-results.mjs` can compare a new capture with the pinned Node reports.
`review-construction.py` binds the actual new-engine admission and closed
constructor/validator outputs before issuing the four-call runtime request.
Existing requests and outputs are immutable; new executions need new names.

Stock wasmCloud and full Next.js tests with this engine remain outstanding.
Same-Store identity, native resource retirement and production acceptance are
not established by this sample. The old failing engine/component and original
post-build failure remain recorded separately.
