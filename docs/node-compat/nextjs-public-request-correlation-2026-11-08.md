# Next.js public request correlation checkpoint

The full Next.js contract remains unaccepted. Earlier fixed comparisons and the
full stock wasmCloud run preserve two unresolved outcomes: the legacy cache
generation check can remain 1→1, and a strict browser Server Action POST can
report `ERR_ABORTED` while the visible interaction succeeds. Existing completion
markers do not identify a browser request across guest instances or establish
Promise, host, TCP, or resource completion.

This diagnostic adds `x-next-public-request-correlation` through the existing
browser-context header option. A fixed native→Node pair declares two distinct
public 64-hex values per arm before either application trial. Its host manifest
is outside the guest app/cache mounts. No guest environment value, entropy at
INIT, WASI interface, custom host service, host patch, extra request-path await,
body read, tee, or ownership transfer is introduced.

The guest observes bounded header metadata independently at the existing WASI
HTTP adapter and classic request boundaries. V2 markers add correlation state,
value and bounded count. Module-local tokens and sequence numbers remain local
observations. Matching a public value alone cannot prove physical identity;
duplicate, forwarded, replayed, spoofed, coalesced or missing observations remain
unjoined. The planned review requires actual Playwright and same-local NetLog
sent-header evidence plus unique valid guest POST candidates.

The reviewed source checkpoint `526b4da3` is committed and pushed. Root then ran
the constructor once under the original 2400-second owner. All three inner
commands and the outer owner exited raw0, without timeout, signals, forced
cleanup or remaining observed groups. The new component is
`df8d74204ca638a664236ed7f0b615eb2b8828a0da40a0abfe9ee72ade04e0bc`,
37,266,121 bytes. Its actual returned import graph has 131 typed functions;
that number is an observation, not an admission target. Emitted interfaces
remain the same 13 standard WASI 0.2.10 interfaces, with only
`wasi:http/incoming-handler@0.2.10` exported. Native engine `476b1c1d` and
metadata `22f1d456` are reused; this milestone does not rebuild SpiderMonkey.

Primary INIT review `1dff8468` and complementary owner/world review `b0549965`
check the actual artifact, complete typed graph, current build roles and world.
No V1, V2 or Promise completion markers appear in the eight INIT streams. These
are snapshot-construction checks; deployed header correlation is still untested.

Root validation so far includes 21 actual guest-helper seam cases with no
accessor invocation, seven host syntax checks, 15 bounded host-manifest cases,
26 checks of the two final acceptance expressions, and six existing pure
publication-policy tests. The manifest seam's first failure was a temporary-path
alias in the test fixture; the corrected canonical fixture passed. The first
runtime-binding attempt named a nonexistent bridge index and stopped before
writing. Its source and failure record are retained; the corrected binder
protects the actual unindexed bridge source without inventing an index.

The native and Node actors now bind the current component and reviewed shared
browser/client sources. The pair driver retains the original 600-second native
and 300-second Node owners under a 1200-second outer owner. It checks completed
raw capture and natural client/host termination before moving to the second
arm. A complete semantic raw1 remains a failed test result and can continue;
incomplete evidence stops the sequence. There are no retries, replacements,
filtered application failures, gate waivers or production promotion.

The prepared pair executed once in declared order. The outer driver exited
raw0/clean in 23.34 seconds; this is an experiment-completion result. The native
owner exited raw1 and the Node owner raw0. No trial was retried or replaced.

| Existing contract | Native Wasm | Node reference |
| --- | --- | --- |
| HTTP cases | 24 pass | 24 pass |
| Persistent-cache checks | 52 pass | 52 pass |
| Supplemental checks | 80 pass | 80 pass |
| Incremental stream | 5 chunks, shell0/ready2 | 5 chunks, shell0/ready2 |
| Legacy generation | 1→2, pass | 1→2, pass |
| Functional browser cases | Both pass | Both pass |
| Strict browser completion | Fail | Pass |
| Original full suite | Fail | Pass |

Native POST7 `/actions` reports `net::ERR_ABORTED`, with three observer errors
and unavailable decoded body/sizes. Native stdout is fully finalized at 17,508
bytes within the existing 8 MiB limit. Complementary review `75095ddc` confirms
the original owners, publication, manifests, browser and NetLog records. The
failure precedes explicit context close. The completed analyzer `558dc24d` and
independent correlation review `96e7d886` observe a conservative public POST
metadata match: Playwright's exact header, a unique same-local NetLog send, and
one valid adapter/classic POST entry each. The 54 reported marker witnesses
match raw stdout; matching GETs remain separate observations.

The matching POST has nine site records, including an adapter EOF counter of
1,488 bytes across seven reads, child disposal, outgoing-body finish, cleanup,
normal return, and classic finish/close. These are the named guest observations;
they do not prove gzip integrity, fulfilled native export, host task completion,
transport EOF, private identity or a cancellation cause. Undetectable spoofing
and replay are not excluded. No fix is claimed.

Before analysis, review caught an ambiguity in the initial parser: an additional
invalid or duplicate POST header could hide the matching value. The corrected
rule rejects that join and passes 17 classified-frame decision tests. An initial
Root launch preflight used an incorrect argv hash and stopped before analyzer
execution; the exact hash was read and the corrected invocation ran the actual
analyzer once. Both preflight history and the initial unexecuted parser source
are retained. Primary review `ad0944cb` independently verifies the original
48 HTTP cases, 104 persistent-cache checks and 160 supplemental checks across
the pair, the current native/build/app/world evidence, and both complementary
reviews. Its state explicitly records an unaccepted runtime: native false,
Node true, full Next false. Four large binary payloads are delegated to accepted
construction/build evidence rather than replayed by that DATA review. The finite
raw-pair corpus contains 318 files (5,969,078 bytes). Its checker passes both in
the current checkout and in an independent copy with the actual staged Git
permissions (320 files including manifest/checker, all mode0644). It recomputes
the retained 52/80/24/cache/stream predicates per arm, preserves both strict
outcomes, and checks the public metadata match without running the analyzer,
guest or original temporary paths. Omitted native/app/package payloads are not
revalidated by this offline check.

The initial production
checkpoint remains foundations-v13. Persistent-cache concurrency and storage
bounds, lifecycle behavior, clean-machine bootstrap, component-size/startup/
memory/throughput measurements, and broader compatibility remain outstanding.

Evidence lives under
`tests/node-compat/frameworks/nextjs/next-public-request-correlation-*`.
`progress.md` records subsequent execution and remaining work. Finite INIT
retention contains 80 files (649,898 bytes); its offline checker passes without
reading original paths. It intentionally excludes component, engine, SDK,
package and app payloads and does not recreate a host instantiation. Run:

```sh
python3 -I -B tests/node-compat/frameworks/nextjs/next-public-request-correlation-construction-root-results-v1/retained-data-v1/check.py
python3 -I -B tests/node-compat/frameworks/nextjs/next-public-request-correlation-pair-root-results-v1/retained-raw-data-v1/check.py
```

The [native-boundary Source proposal](../../tests/node-compat/frameworks/nextjs/next-native-export-public-correlation-plan-v1/README.md)
identifies existing internal guest registration and ordinary native `call`
observation sites. It rules out direct stdout inside canonical `post_call`:
the ABI's may-leave restriction forbids those imports. It contains no native
patch or implemented diagnostic API. The next engineering decisions are a
default-off internal guest surface, primitive/string validation, per-export
ambiguity/clearing rules and ordinary-call I/O error behavior, followed by
targeted native tests and a fresh same-world build/constructor if implemented.
