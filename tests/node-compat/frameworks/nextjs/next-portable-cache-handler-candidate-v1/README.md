This is a stopped, unsealed optional CommonJS cache-handler Source prototype.
It has not been parsed by Node, loaded by Next, written a cache file, compiled
into a component or exercised on a host. No existing application/configuration,
guest entry, engine, host scheduling or world is changed. All operational fields
in `manifest.json` remain null. This is a new scenario prerequisite, not a repair
or waiver of the original lexical counter generation1→2 failure.

`cache-handler.cjs` exports the genuine Next `cacheHandler` class contract. The
distinct `cacheHandlers` / `"use cache"` contract is outside this prototype.
The real options must select production, flushToDisk and cacheMaxMemorySize:0.
The private root is derived from actual `serverDistDir` as
`../cache/portable-fetch-v1`. Its cache parent must already be an externally
owned private writable mount. The module uses existing node:fs, node:crypto,
node:path and node:buffer APIs only; it performs no explicit FS or entropy call
at module evaluation. Construction loads the pinned real Next FileSystemCache
dependency, so construction itself must occur after deployed runtime admission.

For APP_PAGE, APP_ROUTE and PAGES, get/set/reset and immediate revalidation use
the actual pinned FileSystemCache default class with the genuine constructor
options and maxMemoryCacheSize:0. An existing or later active static memoryCache
causes an identifiable refusal, since passing zero does not disable that cache.
No Next global is cleared or patched. These delegated files are outside the
prototype's FETCH storage bound. Route tag maps, seed promotion, error-to-miss
handling and multi-file publication remain pinned Next behavior; shared route
tag coherence is **not** promised. Other kinds are explicitly refused. A fresh
configured Next build must verify tracing, fileURL loading and actual route
behavior before this fallback can be considered supported.

The FETCH profile declares one explicit tag within the six-entry tag namespace
in the code, including the prospective `/api/portable-cache/route` implicit
tags. That route is not implemented here. Unknown tags are refused. Values are
bounded JSON FETCH records; bodies stay opaque strings, including Next's
unstable_cache JSON or fetch base64. The handler preserves lastModified/value
and leaves TTL policy to Next. Other expiration profiles, arbitrary tags,
large/binary values and unsupported input objects fail identifiably.

Each actual get records pre-computation persisted epochs against the handler
instance, exact SHA256 key and actual request-local fetchIdx. Repeated tuples
are permanently poisoned; consumed tuples remain consumed. After 64 tuples,
all writes on that handler are disabled instead of evicting associations that
delayed set calls might reuse. Missing/ambiguous/reset associations skip writes.
Next's initial reset before use is allowed; a later reset permanently disables
writes for that instance. get still checks persisted tag files afresh. These
choices trade cache availability for refusing unauthenticated stale writes.

Next can bypass handler.get through resume-data/HMR/on-demand paths, and an
origin error/non200/cancel can omit set. This prototype cannot force those paths
through disk or promise fresh shared epochs for Next's own memory hits. A later
scenario must show which real handler operations occurred. It must not infer
universal freshness or cross-request identity from fetchIdx.

Every tag publication uses a runtime random 256-bit epoch. An absent tag file
creates a fresh token, never a constant initial token that could revive an old
entry after deletion. A get compares fresh epochs on both sides of reading the
entry. A set uses only its original get snapshot and refuses changed epochs.
Invalidation between the final set check and rename may leave an old record on
disk; later get rejects its old epochs. A delayed writer may overwrite a newer
record, causing an extra miss. No compute-once, CAS, ordering, ABA-free entropy,
cross-process lock or globally serialized operation is claimed.

Publication requires an exclusive fixed pending filename then same-directory
rename. No retry loop exists. Invalidation is sequential across tags, not an
atomic multi-tag transaction. A partial error reports only completed
publications in committedTags; the original cause, including falsy values, is
retained. A crash or ambiguous write/rename failure leaves bounded pending state
and can block that slot. Pending files are never reclaimed online, because
ownership after failure is uncertain. Recovery requires an exclusive offline
procedure or fresh cache namespace, neither implemented here. Selected-host
rename/visibility semantics remain an empirical prerequisite. Native flush:true
is unavailable; no crash durability or filesystem-transaction claim is made.

There are 64 entry slots and 6 tag slots, with one target and one pending name
each: at most 140 cooperative-protocol files plus three directories. Targets
include the full key, so slot collisions cause misses, not wrong-key values.
At the declared 64KiB/2KiB file caps the logical data bound is 8,413,184 bytes;
this is not allocated disk, host RSS, guest heap or arbitrary-input memory proof.
Delegated route artifacts are outside this count. SHA256 envelopes and strict
JSON/UTF8/schema checks identify corruption; they are not authentication.
Guest stat exposes no dev/ino/mode, so the code does not invent those checks or
infer private modes/WASI descriptor rights. Symlinks, hard-link aliases,
unexpected members, malformed or oversized records fail explicitly. External
adversarial mutations/TOCTOU and uncooperative writers are outside the profile.

Next IncrementalCache.set catches handler errors and warns. Direct identifiable
errors are not automatically failed application requests. `test-handler.cjs`
is unexecuted test Source using fake in-memory FS/entropy/delegate objects. It
specifies ordinary reuse, delayed/stale writers, invalidation at publication,
absence/corruption, ambiguous associations, reset/overflow, partial write and
ambiguous rename, accessor refusal, real delegation shape and storage bounds.
No real Next module, cache FS, entropy, server, browser or component is used by
that test. `test-source.py` only reads Source references and structure. No test
result should be presented as actual handler support.

Before any actual Next installation: the separately versioned native fileURL
interop must compile/link and pass its deployed 16-case probe; permit reviewed
pure fake tests and grammar checks; test real FS publication/concurrent writers
and failure retention; build a new optional scenario through normal Next tracing;
then run pinned Node and genuine components with all existing gates unchanged.
The original failed scenarios remain preserved. No actor or automatic next step
is authorized by these files.
