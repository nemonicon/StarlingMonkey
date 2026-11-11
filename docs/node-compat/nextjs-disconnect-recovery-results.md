# Next.js disconnect and recovery

The repeated-disconnect probe exposes a lifecycle failure on both Wasm hosts:
later requests recover and all client checks pass, but both guests emit abort
diagnostics. The Node bridge control also fails with transport errors. These
results block lifecycle acceptance. They do not
invalidate the earlier [complete application sample](nextjs-clone-cancel-full-results.md),
which did not exercise these disconnects.

The unchanged Next 16.4.5 / React 19.3.1 application runs with engine `e3075c14`,
component `bfb106fe` and observer envelope `f1c32f45`. The component still imports
the same 13 selected standard WASI 0.2.10 interfaces. No host changes, custom
services, browser invocation or new native build are involved.

The [fixed plan](../../tests/node-compat/frameworks/nextjs/next-disconnect-recovery-root-results-v1/run-plan.md)
declares Wasmtime 42.0.1, stock wasmCloud 2.11.0 and matched Node 22.14.0, in that
order. Each arm makes three warm-up and sixteen recorded cycles of six calls:
complete streaming; destruction after the first actual response-body Buffer;
malformed JSON; distinct per-cycle request context; empty request context; and
filesystem/SHA-256 recovery. There are 114 planned calls per arm, with no retries.
The warm-up labels do not make this a performance benchmark.

| Environment | Client observations | Lifecycle evidence | Status |
| --- | --- | --- | --- |
| Wasmtime 42.0.1 | 114/114 pass; 95 complete responses; 19 disconnect observations | 19 `Request aborted` stacks, 19 `mozalloc_abort` diagnostics, 19 worker-error backtraces | Functional recovery passes; lifecycle failure |
| wasmCloud 2.11.0 | 114/114 pass; 95 complete responses; 19 disconnect observations | 19 `Request aborted` stacks and 19 `mozalloc_abort` diagnostics | Functional recovery passes; lifecycle failure |
| Node 22.14.0 bridge control | 114/114 pass; 95 complete responses; 19 disconnect observations | 19 `/stream` transport errors with `Request aborted` | Actor fails; raw exit 1 |

The Wasmtime owner, PID 95660 with a 600-second bound, exits 0 with all owned
processes gone. Its client records all 19 disconnect intents before HTTP
completion. Request, response and socket closure, body publication, complete
host captures and input preservation are verified. The separate
[continuation record](../../tests/node-compat/frameworks/nextjs/next-disconnect-recovery-root-results-v1/wasmtime-continuation-review.json)
checks 241 referenced files before the next fixed comparison. It preserves the
abort diagnostics as a negative outcome; a clean host exit does not establish
successful guest cleanup.

The wasmCloud owner, PID 96690 with a 600-second bound, also exits 0 with clean
process shutdown and complete collection. The Node owner, PID 98526 with a
300-second bound, exits 1 without timeout, forced cleanup or remaining owned
processes. Its client passes, but its actor correctly remains failed because
`transportErrors` contains 19 entries. All three arms record the disconnect
intent before HTTP completion in each of their 19 cases. There were 342 client
observations altogether; successful client observations do not waive the host
or bridge failures. The log/error counts alone do not join a diagnostic to a
specific client request.

Independent review verifies 734 input artifacts and recomputes every call,
publication receipt, body/chunk digest, completion predicate, actor outcome and
diagnostic count. The [saved regression packet](../../tests/node-compat/frameworks/nextjs/next-disconnect-recovery-root-results-v1/README.md)
contains 793 payloads / 14,877,142 stored bytes. Its Python-only checker passes
both here and from an isolated copy of 795 staged Git files, with identical
output. A successful checker exit verifies the recorded failure; it does not
turn it into a passing runtime result.

```sh
python3 -I -B tests/node-compat/frameworks/nextjs/next-disconnect-recovery-root-results-v1/check-saved.py
```

The guest logs pass through `BridgeIncomingMessage.onAbort`, `abortObservedIo`
and `handleResources`. Source review identifies a likely path: abort propagation
errors the response stream, then canceling that errored stream rejects and can
escape the HTTP export. The Node errors also name `BridgeIncomingMessage.onAbort`.
This is a source-supported hypothesis, not a demonstrated causal join. The next
implementation task is a narrow bridge/real-component regression followed by a
guest-side repair that preserves unrelated errors and cleanup failures. Error
suppression or healthy subsequent requests would not prove a repair. The
existing native clone-cancellation regression must continue to pass.

The collector's six real loopback controls pass before deployment, covering
Content-Length, chunked framing, truncated bodies, overflow, timeout and
first-body close. Review also corrected a late-event mutation race after an
unknown cleanup timeout; the corrected collector passes the same six controls
in a fresh run. The unknown-cleanup timeout branch itself was reviewed in
source, not forced dynamically. Original source and control records are saved.

These serial requests test observable application recovery and set-to-empty
context isolation. They do not prove concurrent AsyncLocalStorage isolation,
same-Store reuse, native resource retirement, leak freedom or stable memory.
The matched Node arm uses the existing message bridge and module provider;
it is not guest execution. Full browser repeatability, clean-checkout
reproduction, empirical cost measurements and production promotion remain
outstanding. Production remains foundations-v13.
