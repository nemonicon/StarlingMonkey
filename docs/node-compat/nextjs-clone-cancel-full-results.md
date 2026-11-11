# Full Next.js regression with native cancellation repair

The complete selected Next.js workload passes once on Wasmtime, stock
wasmCloud and matched Node. Independent review recomputes every reported
compatibility gate from the closed captures. The [lifecycle regression](nextjs-clone-cancel-results.md)
also passes on both target hosts. This is a bounded application sample, not
complete Next.js/Node compatibility or a reliability claim.

The selected application uses Next.js 16.4.5 and React 19.3.1, with 2,196
standalone files and `compress: false`. The filesystem-backed cache fixture,
HTTP cases, strict browser worker and all semantic assertions are unchanged
from the prior [V4 full sample](nextjs-v4-full-results.md). Engine `e3075c14`
contains the bounded native cloned-response cancellation repair. Component
`bfb106fe` and observer envelope `f1c32f45` pass construction and structural
validation, with exactly 13 standard WASI 0.2.10 imports.

| Fixed arm | Host/control | Limit | Result |
|---|---|---|---|
| 1 | Wasmtime 42.0.1 | 600 seconds | Passed; owner 85601 exits 0, clean cleanup |
| 2 | Stock wasmCloud 2.11.0 | 600 seconds | Passed; owner 86646 exits 0, clean cleanup |
| 3 | Matched Node.js 22.14.0 | 300 seconds | Passed; owner 88034 exits 0, clean cleanup |

Chrome 157.0.8103.39 and Playwright 1.64.1 are selected for all arms. Fresh
version commands and complete selected Playwright package checks pass. The
Chrome executable hash covers its launcher, not the whole application bundle.

Each arm passes the original 24 HTTP checks, 52 portable-cache checks,
80 supplemental checks, persisted generation 1→2, incremental streaming,
two UI interactions, assets and strict browser response-completion assertions.
All three deliver three observed stream chunks, with the shell preceding the
ready content. Each resource observer captures a complete 2,963-byte response
and records `Network.loadingFinished`. Each physical callback state contains
generation 2. Review `003ba83c` checks 210 input artifacts; its original owner
88588 exits 0 with clean cleanup.

No capability failure was observed in this fixed three-arm run. The earlier
Chrome 156 aborts remain failed and unexplained. This passing run does not
establish that the native cancellation repair caused those older symptoms.

The resource observer records an additional result; it cannot waive a strict
browser failure. Every original outcome is retained. A known semantic failure
may be followed by the next fixed arm only after capture publication, input
preservation and normal host/browser shutdown are established. Uncertain
collection stops the remaining arms. No automatic retry is planned.

Each guest arm gets an independent application copy and writable cache, with
only selected standard WASI capabilities. There are no custom host services or
host modifications. These tests do not promise one retained Node process,
general TCP/TLS behavior or complete Node/Buffer compatibility.

The closed packet retains 350 files (16,214,908 stored bytes). Recheck its
semantics without the original build paths:

```sh
python3 -I -B tests/node-compat/frameworks/nextjs/next-clone-cancel-full-root-results-v1/check-saved.py
```

The checker passes here and from an isolated copy of 352 actual staged Git
files, with identical output. It verifies all retained/expanded hashes and
recomputes the three original outcomes through repository-only file reads.
It executes no host and does not verify omitted binaries or re-observe the
original physical cache directories. Optimized Python is refused before reads.

Resource retirement, repeated-run stability,
clean-checkout reproduction and size/startup/memory/throughput measurements
remain separate gates. Production remains foundations-v13.
