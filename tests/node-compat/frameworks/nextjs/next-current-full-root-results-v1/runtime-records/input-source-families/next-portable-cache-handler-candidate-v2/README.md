Optional CommonJS cache-handler Source V2. This is a separate successor to held
Source1f8398a6; V1 and its seven frozen model inputs remain unchanged. No app,
configuration, Next dependency, host or native/WIT source is changed here.

The genuine `cacheHandler` class contract remains constructor/get/set/
revalidateTag/resetRequestCache. Next must provide production, the real
cacheMaxMemorySize:0 option and outer flushToDisk:true. Its declared future
fixture is the separately reviewed cache-app plan ee8be276, not an installed
application. The `cacheHandlers`/"use cache" protocol is outside this class.

V2 has exactly ten declared read-epoch tags: legacy next-runtime-fixture-v1,
portable-fetch-v1, and their five ordinary API-route soft tags with two shared
members. get/set require a raw explicit-tag array of exactly one of those two
primary tags. Both primaries together, duplicates and implicit-only explicit
tags refuse. Soft tags remain part of the pre-computation epoch snapshot and
stored FETCH record; fetchIdx remains request-local, never a global ID.

Mutation permission is narrower than the read roster. revalidateTag validates
the entire batch and duration before changing local state, opening files,
drawing entropy, publishing or calling the route delegate. Only the two primary
tags with immediate expiration/expire:0 are accepted. Every implicit `_N_T_`
tag, public path mutation and unknown mutation tag refuses identifiably. This
does not claim portable route invalidation. Next queues its public API, so a
direct helper rejection is not proof of synchronous route/API rejection.

FETCH persistence uses new namespace portable-fetch-v2 beneath the actual
serverDistDir's sibling cache directory. Its parent must already be the owned
private writable cache mount. There are64 entry slots and10 tag slots, one
target plus fixed exclusive pending filename each:148 cooperative files and
8,429,568 maximum logical file bytes at64KiB/2KiB caps. This excludes directories
and delegated data; it is not allocated disk, RSS, heap or adversarial-input
memory proof. A collision evicts availability, never returns another key's data.

The genuine pinned Next FileSystemCache delegate receives maxMemoryCacheSize:0
and flushToDisk:false. APP_PAGE/APP_ROUTE/PAGES still call its real get/set/reset
and accepted-primary revalidation methods. Immutable build seeds can be read;
route writes and ISR persistence are explicitly deferred. Existing/later
static memoryCache still refuses, with no Next global deletion or patch. The
outer flush:true requirement remains for the separate FETCH backend. Delegate
route errors-to-miss, local tag maps and bookkeeping remain Next behavior;
cross-instance route coherence and successful route persistence are not claimed.

V1's computation-association, JSON/FETCH validation and publication algorithms
are retained: instance+key+actual fetchIdx snapshots; permanently consumed or
poisoned tuples;64-association sticky write-disable instead of eviction; fresh
epoch reads on both sides of a lookup; original epochs at set; skip missing,
ambiguous/reset or invalidated writes. Missing epoch files produce fresh random
tokens; corruption/inaccessible state throws. SHA envelopes are not authentication.

Fixed `wx` pending files publish by same-directory rename. Partial valid
multi-primary invalidation reports only completed publications and retains its
original cause. A race can leave an old record that later reads reject, or
overwrite a newer record and cause an extra miss. There is no compute-once/CAS
or atomic multi-tag transaction. Uncertain pending state is never reclaimed
online. No retry, timer, background cleanup or fsync/durability claim is added.
Real host rename/visibility, concurrent processes, failure and restart behavior
still need separate validation. External adversarial writers are outside scope.

No explicit FS or entropy call occurs at module evaluation. Construction loads
the real Next dependency, so it must occur after runtime admission. Guest Stats
exposes no dev/ino/mode; the class invents none and infers no WASI rights. Next
RDC/HMR/on-demand bypasses can omit handler.get; missing/ambiguous association
never stamps new epochs at set. No freshness claim covers those memory bypasses.
Next catches handler.set errors and warns; identifiable helper errors are not
automatically failed HTTP requests.

Direct Source checks used pinned-path Node22: two `--check` grammar commands
exited0 and the fake-only test exited0 with72 assertions and empty stderr.
Raw logs and author-recorded command/input descriptors are retained under
checks/. These were ordinary local Source unit checks, not an original-owner
runtime experiment or OS sandbox/clean-process attestation. Only own Source
reads and real Node SHA are used; cache FS, random draws and Next delegate are
explicit in-memory fakes. Copied UNEXECUTED comments describe the initial
Source cut; the additive validation records describe these later checks.

Tests retain all original cases and add both primary/soft rosters, primary
invalidation isolation, inert valid soft-epoch staleness, whole-batch implicit/
unknown refusal before effects, initial-reset safety after refusal, duplicate/
dual-primary refusal, genuine delegate options without original-context mutation,
and valid multi-primary partial failure with original falsy cause. The soft-epoch
test edits fake persisted data; it is not a supported public implicit mutation.

This does not exercise real cache FS, entropy, Next loading, tracing, HTTP,
browser or guest behavior. Source review and fake checks do not establish the
new optional Next profile. The real deployed16-case loader result is a separate
gate, followed by a fresh app build, real-FS tests and matched Node/native trials.
Existing24/cache/stream/strict2+six-case gates and all historical failures remain
intact. In particular this cannot make a lexical generation counter process-wide
or accept a failed original generation comparison.
