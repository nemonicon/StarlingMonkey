# Next.js lifecycle checkpoint

The current native engine passes the new bounded request-context checks and
fails cloned-response cancellation. This narrows the next runtime change to
cancellation propagation; it does not establish general resource retirement,
same-instance reuse, or complete Next.js support.

The real component is `ea18d156…` (37,225,626 bytes), built with the unchanged
experimental engine `237c4e5a…` and its genuine `500e76ac…` metadata. It validates
and exposes exactly thirteen selected standard WASI0.2.10 imports and the single
`wasi:http/incoming-handler` export. No custom service or host modification was
introduced. Foundations-v13 remains the accepted production checkpoint.

On stock Wasmtime42.0.1, one host collected three sequential ordinary requests:
`/context`, `/clone-cancel`, `/context`. All returned complete HTTP200 bodies;
the host shut down normally with SIGINT/exit0. The original outer owner41704/120
also exited0 with no forced cleanup. These are host-level observations, not
proof that Wasmtime used the same Store for each request.

| Check | Pinned Node22.14.0 | Real component | Result |
| --- | --- | --- | --- |
| Public AsyncLocalStorage, WebStream callbacks, bind/snapshot exceptions and rejections, queueMicrotask | Eight groups,95 checks | Both context calls match all public observations;190 checks total | Pass within this fixture |
| Public AsyncResource constructor | Available in Node | Named/default bindings are identical; each construction throws the declared `ERR_SM_NODE_UNSUPPORTED` | Explicit unsupported contract passes; API remains unavailable |
| Cancel both cloned response bodies | Calls the source once with both original reason objects; both promises wait for source cancellation | Never calls the source; promises fulfill before source cancellation could finish | Compatibility failure |

The failed cancellation comparison is preserved as an actual failing test:
owner41834/30 exits1, with clean process ownership and unchanged inputs. The
collector's successful HTTP status is not used as a semantic pass. The third
context request remains healthy, but this does not prove absence of retained
handles, memory, or cross-request state.

The source audit locates `clone_tee_cancel_algorithm` in the selected compiled
`builtins/web/fetch/request-response.cpp`. It sets branch flags and returns
undefined without propagating cancellation to the source. The
[fix audit](../../tests/node-compat/async-context/next-lifecycle-root-results-v1/clone-cancel-fix-audit.md)
describes the required traced state, shared cancellation Promise, original
reason identities, and separate EOF/error settlement paths. That native fix is
not implemented or validated by this checkpoint. Source-cancel rejection and
one-cancel/survivor EOF/error cases must precede acceptance of a fix.

The compiler package had been deleted during disk cleanup. Recovery used the
retained dependency lock and all271 authenticated patched compiler Source files.
The Rust1.96.1 build and Jco1.40.0 wrapping/transpilation completed; all4,859
dependency payloads match the old tool cut. The fresh splicer is `716737f5…`,
with a new package inventory of4,887 files/21 symlinks. It is a separately
selected build, not a claim to have recreated the deleted package byte for byte.
The native engine bytes did not change. The locked LZMA tool dependency declares
a newer Node engine range; its original payload was restored and this compiler
invocation succeeded on the selected Node, without claiming broader support for
that dependency combination.

Two test-tool limitations remain visible. The first context-test version could
discard rejected cleanup operations; its corrected v2 passes the same95 checks,
and both original results remain saved. The first HTTP collector's generic
`read(amt)` EOF handling can miss an under-length Content-Length body. Independent
review verifies that all three actual bodies exactly match their declared
lengths—17,379/2,902/17,379 bytes—so this sample is unaffected. A corrected
collector is required before future reuse of that transport path.

The [retained packet and checker](../../tests/node-compat/async-context/next-lifecycle-root-results-v1/check-saved.py)
hold305 payloads/968,759 bytes, including original command logs, Node observations,
component response bodies, Source and independent reviews. Run the offline check:

```sh
python3 -I -B tests/node-compat/async-context/next-lifecycle-root-results-v1/check-saved.py
```

It succeeds only when the saved context successes **and cancellation failure**
remain intact. It does not read old temporary paths or execute a guest. For a
future engine, the shared cases and `compare-results.mjs` accept newly collected
responses and retain the strict Node comparison; the cancellation gate must turn
green before promotion. Binary/tool reconstruction and live host runs remain
separate from this saved-evidence check.

Next: fix cancellation and cover rejection/EOF/error settlement, restore the
missing native build prerequisites, then run both target hosts. Continue with
resource retirement, reuse and memory measurements; the declared full-Next
repeatability matrix and clean-checkout reproduction remain outstanding. The
[passing V4 full Next sample](nextjs-v4-full-results.md) and earlier browser
failures retain their original scopes.
