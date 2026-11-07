This is a Source-based future app plan, not an application fork, build or
runtime result. No existing fixture, handler, dependency, runner or protected
application is changed. No Next code, configuration file or actor is authored
here. All future operational fields in `plan.json` are null.

The new Source fixture should descend from the exact 29-file app-fixture used by
next-app-build-v1. Keep package.json/package-lock.json and all existing routes,
layouts, actions, CSS and assets byte-identical. Change only next.config.mjs and
add cache-handler.cjs plus app/api/portable-cache/route.js: 31 future Source
files, including 28 unchanged originals. This is a new versioned fixture; do not
mutate the existing directory, fresh2181 build or historical inventories.

Keep standalone output, original tracing root, cpus:1 and the /api/fs-crypto
message.txt tracing include. Set the real Next cacheHandler field to the local
cache-handler.cjs filesystem path derived with the existing fileURLToPath/new
URL configuration idiom; set cacheMaxMemorySize:0. Do not set cacheHandlers or
patch a Next/global cache map. The pinned builder normalizes cacheHandler
relative to distDir and its trace collector includes the configured file.
Therefore inspect the new required-server-files config and NFT/standalone
output, rather than assume an emitted path. Resolving the emitted path against
the new standalone distDir must select the traced cache-handler.cjs inside the
new application, also when mounted at /app. Require matching Source/standalone
bytes and the real pinned FileSystemCache dependency; no manual post-build
injection or host absolute-path workaround.

Handler Source1f8398a6 is immutable and cannot serve the legacy fixture as is.
Its allowlist lacks next-runtime-fixture-v1 and its context guard independently
requires portable-fetch-v1. A genuine successor should accept exactly one of
those two explicit primary tags and use the ten-tag union in plan.json. Each
ordinary API route has five derived soft tags. The legacy compiled route proves
page /api/cache/route and pathname /api/cache, and actual compiled chunk124
passes implicitTags.tags and the same fetchIdx to its cache get. The pinned
getImplicitTags source derives the listed roster. These are Source-derived
ordinary-route expectations, not observed handler calls or permission to accept
unknown tags. Keep missing/ambiguous get→set snapshots non-persistent.

Use a new fixed portable-fetch-v2 storage namespace. Keep64 entry slots,
64 retained/poisoned associations per handler and the old record/value caps.
With10 tag slots, targets+fixed pending names total148 files and8,429,568
logical bytes, excluding directories/delegated route data. Preserve all prior
epoch checks, fixed pending ownership, partial/error retention and no online
reclamation/retries. Add model coverage for legacy/new primary tags, soft-tag
invalidation and separation before any real FS test. The old40 fake-only pass
does not validate the changed successor.

There is a separate route-storage boundary. Pinned FileSystemCache sends scoped
route entries to serverDistDir/route-cache, outside the current native writable
.next/cache mount. promoteSeed may write there; its errors are caught by Next.
A new zero-memory configuration must not infer successful route persistence or
silently make the application writable. The proposed bounded choice is a real
FileSystemCache delegate with maxMemoryCacheSize:0 and flushToDisk:false for
APP_PAGE/APP_ROUTE/PAGES, while FETCH persistence still requires the genuine
outer flushToDisk:true. This keeps actual get/set/reset/revalidate calls and
immutable build-seed reads; route/ISR persistence is explicitly deferred. It is
not route-tag coherence support. Root selected the flush:false/max0 Source
design boundary; it is still unimplemented and untested. Retain that explicit
choice in the successor rather than silently swallowing denied promotion
attempts. Existing/later static memoryCache must still
refuse; no Next global mutation or new writable server mount is proposed.

Read tags and mutation tags must be different declared roles. Track all ten
explicit/implicit tags when admitting a FETCH lookup, but accept only the two
explicit primary tags for revalidateTag. Reject every implicit `_N_T_` tag and
unknown mutation tag before any FS, entropy, publication or route-delegate call.
Validate an entire multi-tag list first so an unsupported path mutation cannot
partly invalidate a primary tag. This explicitly refuses revalidatePath and
direct implicit-tag mutation; it cannot pretend that updating FETCH epoch files
also invalidates immutable build seeds across instances. Next queues public
revalidation calls, so direct helper refusal and application error observation
are distinct tests. Do not promise that revalidatePath throws synchronously in
the route or that a returned HTTP acknowledgement means the mutation succeeded.

The new route should use the genuine unstable_cache API with one fixed key/tag
portable-fetch-v1 and revalidate3600. Its callback returns a marker and a fresh
64-lowercase-hex nonce from randomBytes(32), drawn only inside the callback at
runtime. There is no lexical generation counter, top-level nonce or cache global.
GET returns the cached value. POST calls revalidateTag for that same tag with
expire:0 and returns a distinct acknowledgement. Next queues revalidation; the
acknowledgement alone is not a disk-commit proof. The strict finite five-request
scenario tests the visible boundary after POST without polling or sleep.

The five requests are GET-first, GET-repeat, POST-revalidate, GET-after and
GET-after-repeat. Require status/markers/types, exact first/repeat nonce equality,
different after nonce and exact after/after-repeat equality. This is finite
freshness/value evidence, not Store identity, a universal nonce uniqueness claim
or exactly-once computation. Preserve all raw outcomes before comparisons and
retain failures. Test direct real-FS concurrent writers/invalidation, corruption,
busy/uncertain publication and restart separately; forty in-memory checks do not
close those prerequisites.

Reuse the existing app-only build mechanism through a genuine Source successor:
same explicit Node/npm, lock, ci options, webpack build, original owners/caps,
private caches and standalone packaging, with the new fixture catalogue. Require
fresh generated inventory/root identity and action/BUILD_ID extraction. A new
browser worker may need new exact asset pins from this build; preserve its
functional bodies, observers,20s/500ms and strict error gates. No old result,
2181/425 count, source inode, action ID or asset hash may be retargeted.

Use reviewed native/StockV6 runner mechanisms and one shared future five-case
collector, with real new build/constructor/metadata bindings. Original24 HTTP,
cache generation comparison, strict stream, two strict browsers and six-case
supplement remain intact and separately reported. Keep /api/cache and
/api/revalidate byte-identical and operational through the declared legacy tag.
The original module-local counter can still return1 after invalidation in a
different JS global. Its gate remains false if observed; the nonce scenario
cannot replace it or turn a failed original contract into full acceptance.

Before actual new app build: accept the new full engine and constructor and run
the genuine16-case deployed interop probe. That gate precedes handler loading;
the prior checked refusal and frontend-only compilation are insufficient.
Review the handler successor and real-FS tests, then build once under a separate
Root grant. Later Node/native trials require fresh owned application/cache roots
and unchanged input/world/ownership protections. No automatic next action is
authorized by this plan.
