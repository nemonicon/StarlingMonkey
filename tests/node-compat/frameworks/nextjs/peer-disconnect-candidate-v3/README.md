# Peer V3: guard controller allocation with owned-resource cleanup

Source only. This preserves held11fe V2 and its unused Root grant. The only
adapter behavior change moves AbortController allocation into the existing
owned-resource try, before headers. V2 allocated after callback ownership entry
but before try/finally; a constructor throw skipped both that finally and the
outer pre-entry cleanup. V3 declares the local first and assigns inside try.

Policy, handler, guest tail, assembler and existing33 DATA gates are byte-identical
V2 copies. Genuine native APIs, observed-I/O signal policy, exact output-write
closed handling, cancellation/lock/finally gates, healthy EOF,13 standard0.2.10
interfaces and8025 world are unchanged. Future.get and typed HTTP error extraction
remain deferred. No native Source/engine/public profile is changed.

`test-ownership.mjs` extracts the exact old/new handleResources function text and
uses lexical inert callbacks plus Symbol DATA. It demonstrates that the same
inert allocation throw retains identity, skips old cleanup, and reaches V3's
outparam/incoming cleanup callbacks. It invokes no real AbortController,
resource method, WASI, OOM/fault workload, socket, engine or guest. These callbacks
are a control-flow model, not native disposal proof.

The first inert reader omitted its lexical errorData callback and failed with
ReferenceError while reporting the injected marker. Its exact test/logs are
retained in preparation-history; only that test binding was corrected. No
adapter behavior or actual workload was changed in response to that reader error.

All actual target/authority/review slots remain NULL. Grammar, assembly and inert
DATA checks do not grant construction/runtime. See held V2 README/plan for the
unchanged policy scope; the prior ownership hold is corrected, not retroactively
admitted. Root must separately review V3 and issue fresh construction/runtime
authority with a genuine collector successor.
