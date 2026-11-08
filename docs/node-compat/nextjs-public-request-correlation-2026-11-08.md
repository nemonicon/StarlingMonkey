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

Both authorities are prepared; application trials and correlation analysis are
pending. The initial production
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
```
