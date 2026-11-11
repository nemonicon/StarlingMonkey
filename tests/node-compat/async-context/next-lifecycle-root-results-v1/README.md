# Public context and clone cancellation results

Actual Wasmtime42.0.1 collection41704/120 is clean: three complete HTTP200
responses, complete stdout/stderr and normal SIGINT0 shutdown. The independently
checked Content-Length values exactly match17,379/2,902/17,379 retained bytes.

Both `/context` calls match the pinned Node22.14.0 oracle across eight groups
and95 assertions each. Four named/default public AsyncResource constructions
throw the explicit unsupported error; no facade supplies that API.

`/clone-cancel` fails differential comparison. Node invokes the source once with
both original reason objects and keeps both promises pending until the source
settles. This native engine invokes it zero times and resolves both promises
early. Comparison owner41834/30 therefore exits1. This failure is not waived by
the successful HTTP collection or the later healthy context request.

```sh
python3 -I -B tests/node-compat/async-context/next-lifecycle-root-results-v1/check-saved.py
```

The checker verifies305 closed payloads/968,759B without reading original
temporary paths. It deliberately requires the recorded cancellation failure.
For newly collected component responses, `compare-results.mjs` takes the two
Node reference files, context/clone/context response files, and a fresh output
path; it exits1 for a mismatch. Shared fixtures and explicit export bindings
are in the adjacent versioned Source families.

`construction-review.json` records component `ea18d156…`/37,225,626B, unchanged
engine `237c4e5a…`, genuine52-field metadata, thirteen standard WASI0.2.10 imports
and one incoming-handler export. The compiler was rebuilt from the authenticated
271-file source cut and separately selected; the deleted old package identity
is not claimed. Tool binaries and dependencies are not copied into this packet.

The v1 HTTP collector has a generic under-length Content-Length gap, qualified
by independent byte-length verification for this sample. Use its corrected
successor for future transport collection. Native cancellation repair, native
build prerequisite recovery, both-host validation, resource retirement,
same-instance evidence, memory/cost measurements and promotion remain open.
See [the result report](../../../../docs/node-compat/nextjs-lifecycle-results.md)
and `clone-cancel-fix-audit.md` for scope and the planned native correction.
