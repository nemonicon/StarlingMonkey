This is an unexecuted, fixed real-filesystem test suite for the unchanged
portable Next FETCH cache handler. It imports the actual `c1013ea6` handler from
an explicit standalone application root, its actual Next16.4.5 FileSystemCache
class (`427a5a07`), and Next's real `nodeFs` helper (`6bc8642f`). There are no fake filesystem,
random, delegate, clock, publication or module providers and no patched handler.
The earlier V2 fake-only tests remain separate, unchanged evidence.

Root can run the Node22.14 reference once after Source review:

```
/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node \
  tests/node-compat/frameworks/nextjs/next-persistent-cache-overlap-tests-v1/run-node.cjs \
  /private/tmp/starling-node-compat/next-portable-cache-app-build-v1-first/application/.next/standalone \
  /private/tmp/starling-node-compat/cache-overlap-node-v1-first/data
```

The last argument must not exist. Its parent must already be a canonical owned
directory. The CLI creates that root0700, writes only beneath it, never removes
anything, and refuses a reused root. It publishes `result.json` with attempted
cases and partial assertions even after an unexpected rejection, then retains
that original rejection for exit1, including a falsy thrown value. Preflight
refusal before creating a root is reported on stderr instead. Original-owner
process cleanup, input protection and final raw collection belong to Root's
existing launcher; this CLI is not a new authority/owner framework.

Eleven fixed cases exercise two held get→computation→set operations across a
real epoch invalidation; duplicate-tuple poisoning; fixed-slot collision without
wrong-key return; reset while computation is held; the64/65 association boundary;
exclusive pending-file refusal and consumed retry; corrupt read poisoning;
consumption before invalid set validation; exact32KiB/+1 FETCH values, accessor,
URL and object-field limits; absent private parent and over-cap entry/epoch
records; and whole unsupported tag-batch refusal without persisted mutation.
Barriers are ordinary JavaScript promises; every task is observed immediately
and released/collected even when invalidation or reset rejects. They overlap the computation gap,
not synchronous FS syscalls or multiple processes. Real rename races, crash
persistence, lost updates/CAS, fsync durability and cross-process atomicity remain
unavailable here. Fixture-only corruption/restoration writes are explicitly
marked; they do not represent a supported online cache repair API.

The shared CJS export is:

```
const report = {executionKind: 'guest-component'};
await suite.runCacheSuite({applicationRoot: '/app', testRoot: '/cache-tests', report});
```

`report` is caller-owned so a caller can publish partial DATA even when the
promise rejects with a primitive. It is populated before dependency loads and
fixture work. Success returns the same object; failure rethrows the original
value. A guest wrapper must distinguish suite rejection from successful
assertions, and publish bounded failure DATA with `passed:false`.

Guest execution requires a fresh real component using the existing deployed
Node/CJS loader and request entry, the same13 selected standard WASI0.2.10
interfaces, a readonly standalone `/app` and readonly `/cache-test-source` mount,
and a separately owned fresh empty writable `/cache-tests` preopen. The suite
accepts this existing empty mount root; it creates fixed case children itself.
Each case explicitly creates `.next/server` and normally `.next/cache`; the
missing-parent case deliberately omits the latter. No app cache overlay is
needed and the application root is never written. Load the suite and actual
handler only after deployed admission/bootstrap through
`Module.createRequire('/app/server.js')`; do not run it at INIT. The caller must
supply the report object. The suite uses real fs/crypto/Buffer/clock behavior;
Stats modes, inode identities and WASI rights are not inferred. Route-cache
persistence and all methods of Next's nodeFs helper (including its link-based
writeFileAtomic branch) are outside the intended FETCH test coverage.

No Node grammar, test, helper, component, guest, host service or network action
was executed by the author. Root owns later Node execution; guest grammar,
construction, admission, package checks and execution remain separate pending
steps. No huge authority bundle is required by this Source fixture. The fixed
suite retains at most256 ordinary files/1MiB logical bytes and128 directories;
its final JSON is capped256KiB by the Node CLI. The suite's `report.inventory`
is captured before that CLI writes `result.json`; this one publication file
is excluded from the suite inventory and its logical byte count. These bounds exclude dependencies,
stdout/stderr, host memory and disk allocation. Root's normal owner deadline
bounds execution; there are no retries, timers, background cleanup or extra
host services here.

The original app24HTTP,52portable,80supplemental,stream/browser and legacy
cache-generation gates are unchanged. In particular an original1→1 generation
failure remains a failure. These helper tests cannot accept fullNext, establish
Node/guest parity, prove a production fix, or erase any previous runtime result.
