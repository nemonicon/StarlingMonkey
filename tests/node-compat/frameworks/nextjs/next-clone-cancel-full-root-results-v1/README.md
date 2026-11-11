# Next.js full regression with native clone-cancellation repair

The selected Next.js 16.4.5 / React 19.3.1 production application passes once
on Wasmtime 42.0.1, stock wasmCloud 2.11.0 and matched Node 22.14.0. Chrome
157.0.8103.39 and Playwright 1.64.1 are fixed across the three arms.

Each arm passes 24 HTTP cases, 52 portable-cache checks, 80 supplemental checks,
persisted generation 1→2, incremental streaming, two UI interactions, assets and
the original strict browser response-completion predicates. All resource
observations contain complete 2,963-byte response bodies. Original owners
85601 / 86646 / 88034 exit 0 with clean shutdown, without retries. The independent
`actual-runtime-review.json` (`003ba83c`) recomputes these outcomes from 210 inputs.

The engine is `e3075c14`; component `bfb106fe` and observer envelope `f1c32f45`
preserve exactly 13 selected standard WASI 0.2.10 imports. Guest HTTP transport
and filesystem access use standard host interfaces. The application is supplied
through an app preopen and a separate writable cache. No host modification or
custom host service is required. The selected profile uses `compress: false`.

`raw-records/` retains 350 payloads: 16,214,908 stored bytes and 75,005,319 expanded
bytes. Every actual semantic-review input is included. Large text files use
deterministic gzip; original absolute paths are lookup keys for the saved data.
Full app/build/compiler/binary trees are explicitly omitted. `operation-records/`
separately retains the closed binding, authority-preparation, review and retention
commands.

Recheck the saved sample from any checkout:

```sh
python3 -I -B tests/node-compat/frameworks/nextjs/next-clone-cancel-full-root-results-v1/check-saved.py
```

This authenticates every retained file, loads the exact reviewed semantic
validators and supplies only verified repository copies to their file readers.
It recomputes all three outcomes and all 210 original review inputs. It passes
both this checkout and an isolated copy of 352 actual staged Git files
(16,460,847 bytes), with identical output. Optimized Python is rejected before
packet reads. The original callback-directory absence observation is retained
as evidence; the checker does not claim to inspect the old physical directory.

The runtime and client Sources remain versioned under sibling directories.
`prepare-bindings.py` creates a fresh verified input union and exclusive per-arm
authority; the original bounded command runner launches each arm. These frozen
first-run namespaces refuse an in-place retry. Fresh deployed runs need an
explicit new namespace and current prerequisite verification. Checking saved
evidence does not rerun the app or verify omitted binaries.

Earlier failures remain unchanged. This run establishes neither their cause
nor repeated-run reliability, native resource retirement, same-Store identity,
complete Node/Buffer support, clean-machine reproduction or a performance gain.
Production remains foundations-v13. See the [results](../../../../../docs/node-compat/nextjs-clone-cancel-full-results.md)
and [current roadmap](../../../../../docs/node-compat/nextjs-priority-roadmap.md).
