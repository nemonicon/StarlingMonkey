# Node compatibility profile progress

Current accepted checkpoint: [foundations-v13, bounded classic streams](tests/node-compat/foundation-classic-streams/production-acceptance-v13/README.md). The corrected342-source production layer, exact five-file promotion, runtime gates, separate cost evidence and declared preservation scope are accepted. Consumer355/zlib350 experiments and the broader roadmap remain outside that checkpoint; historical preparation statements below retain their original scopes.

Last updated: 2026-11-11. Overall roadmap: **in progress**.

Current native repair work: the cloned-response cancellation candidate is
source-reviewed but **not compiled or tested in a component yet**. Four additional
Node22.14.0 references pass: deferred cancellation rejection preserves false or
object identity, and a canceled branch settles correctly when its sibling reaches
EOF or errors. The corrected HTTP collector passes real TCP tests for complete,
truncated Content-Length, and chunked bodies; no guest claim follows from those
collector tests.

Native build prerequisites are now recovered with about98GiB initially free.
All six tool archives and the public SpiderMonkey header-donor archive match
their saved hashes. All243 missing Intl headers now match:242 were fetched from
the pinned source, and the generated bidi header was reproduced exactly with
cbindgen0.29.1. The complete selected SDK596 files/13 directories matches the
historical content and modes, preserving the patched library. Native Rust1.88
and Corrosion0.5.1 also match their selected payloads. The first tool
materialization's macOS symlink-mode failure and partial tree remain preserved;
the corrected V2 succeeds with all31 symlinks at their declared mode.

The fresh435-native/387-support/3-embedding recipe is assembled with exactly one
C++ change. All ten installed generator checks pass. The [saved recovery
checker](tests/node-compat/async-context/clone-cancel-recovery-root-results-v1/check-recovery-saved.py)
passes885 retained payloads/5,698,413B, preserving all three original recovery
failures and the four Node references. It reads no original absolute paths.
Fresh offline Cargo verification, native compilation and metadata, real-component
cancellation tests, and subsequent full Next regressions remain outstanding.
The existing237c engine and prior failing lifecycle component remain unchanged.
The previous lifecycle failure checkpoint is
`b71aa50478c705803d9a62dbe6a44a89dcd642bb`. This recovery checkpoint does not
promote the cancellation fix. The native build runner and its final input
selection remain work in progress.

Latest lifecycle result: the [real-component comparison](docs/node-compat/nextjs-lifecycle-results.md)
passes both public request-context runs against Node (eight groups/95 checks
each), including four explicit public AsyncResource construction refusals.
Cloned-response cancellation **fails**: Node calls the source once with both
reason objects and waits; the native engine never calls it and fulfills early.
Original runtime owner41704/120 exits0 clean with three complete HTTP200 bodies;
semantic comparison41834/30 exits1 as required. Exact Content-Length/body sizes
are independently verified. No same-Store or native retirement claim follows.
Componentea18d156/37,225,626B validates with exactly13 standard WASI0.2.10 imports
and the sole incoming-handler export. Its engine237c remains unchanged.
The305-payload/968,759B saved packet and repository-only checker pass while
preserving the cancellation failure. The checker also passes from an isolated
307-file copy of actual staged Git blobs; optimized Python is refused before
payload reads. Native cancellation repair and its
negative cases are the next priority; a generic HTTP collector under-length
gap is documented and must be corrected before future reuse.

Compiler recovery: the volume has about100GiB free. The deleted compiler
package is being replaced by a separately selected, freshly rebuilt package;
the old package identity is not claimed. Its271 compiler Source files match the
saved cut, all4859 dependency payloads match the original tool cut, and the
locked Rust build plus Jco wrapping/transpilation finish cleanly. The new
splicer is716737f5/5,589,391B. The existing237c engine remains unchanged, and
its genuine52-field metadata/35 build/1,678 Source-reference admission passes.

Pinned Node22.14.0 now collects eight new public AsyncLocalStorage/WebStream
groups with95 passing assertions, including bind/snapshot exception and
rejection restoration and queueMicrotask. A review found a negative-path
cleanup weakness in the first test version; that version and its positive
result remain preserved. The corrected v2 also passes95 assertions with
identical normal observations. A separate Response.clone cancellation oracle
observes one source cancellation with both original reason objects; both branch
promises remain pending until the source cancellation completes. These are
Node observations, now compared with the real component as recorded above.
The native cancellation fix, restored native build prerequisites and broader
host lifecycle validation are still in progress. Public AsyncResource remains
unsupported. The recovered compiler package has constructed and validated this
component successfully.

Latest full Next result: the [V4 full comparison](docs/node-compat/nextjs-v4-full-results.md)
passes once on stock wasmCloud2.11.0 and matched Node22.14.0 with Chrome157.0.8103.39
and Playwright1.64.1. Original owners32470/600 and33103/300 exit0 clean. Both pass
24HTTP,52 portable-cache checks,80 supplemental checks, generation1→2, incremental
streaming, both UI interactions, asset checks and the original strict browser
completion assertions. Both resource observers report complete bodies. Primary
review791317fe recomputes these gates from the closed captures. This is one
bounded profile sample; the older Chrome156 aborts remain failed and unexplained.
No engine fix or production promotion is claimed.

The fresh V4 capture contains51 normal metadata rows:47 known other paths,
three distinct target requests and one matching public POST tuple. The analyzer
admits that observed witness. Its stronger join remains inconclusive because the
capture assessment deliberately claims observed-only coverage. It does not prove
private identity, React reader EOF or a cause for the historical abort.

Environment recovery is recorded: exact Playwright1.64.1 was restored after
its old directory disappeared; Chrome had updated156→157. First owner30991/600
failed cleanly before host/output creation because a pinned constructor adapter
was absent. Its logs remain retained and its Node slot was not attempted. Root
recovered the exact original adapter d30ade5b/49,672B from retained WAT and verified
all54 constructor inputs plus all2,196 application files. The separately versioned
V2 runner closes that prerequisite gap before issuing an owner. Its fresh2,199
input binding and source review pass. No component bytes changed.

The successful pair is retained as270 payloads/7,987,845B, indexd588c81e.
The repository-only reader recomputes the original review and passes; optimized
Python is refused before reads. Independent runtime8595fd75, tuplea82bfea9,
bindingdd29bba3 and Sourcebe160074 reviews pass within their stated scopes.
The same reader also passes from an isolated273-file copy made from actual
staged Git blobs, with identical output and no original input-path reads.
At that validation cut all505 staged files matched the worktree byte for byte.
This completes the full-workload evidence checkpoint. Next prioritize request-state
isolation, resource retirement and component reuse, followed by repeatability,
clean-machine reproduction, cost measurements and production promotion.

Completed prerequisite: [observer V4](docs/node-compat/nextjs-observer-v4-results.md)
builds and passes all seven real-component metadata probes on Wasmtime42.0.1.
Original owner22795/900 exits0 clean; all seven hosts shut down normally, captures
complete and original inputs remain preserved. The 5,771B observer keeps the
selected13 standard WASI0.2.10 external imports and unchanged diagnostic inner
bytes. Primary composition214c1d9b and metadata61bb6690 reviews pass. The saved
70-file/2,233,749B packet and repository-only checker retain the exact cases.
Independent Source/binding b151d23c, composition299f5760 and runtime2ee2df27
reviews pass. The hardened reader7a59c5b1 passes current and isolated72-file
staged-Git copies; old reader/61bb proof remain preserved. Next envelope9da63790
now composes the unchanged6b20 inner and tested3534 observer: all four tool steps
and Root structural review730c2698 plus independent peeraba36a69 pass, with
nine tool records retained.
The subsequent fresh V4 full-runtime comparison is recorded above. The
metadata/composition result itself does not resolve or waive the earlier abort.

Previous full-workload diagnostic: the [CDP resource-stream comparison](docs/node-compat/nextjs-resource-stream-results.md)
finishes cloud67923/600 raw1/clean and Node68512/300 raw0/clean. Both pass24HTTP,
52 portable checks,80 supplemental checks, generation1→2, stream3(0,1), UI2 and
assets. The original strict browser gate remains cloudfalse/Nodetrue with3/0
capture errors and1/0 failed requests. The pinned Chrome command actually works:
both empty-prefix+one-binary-piece captures retain2,963 bytes, with different
hashes. Cloud loadingFailed/canceled:true keeps completeResourceBody:false;
Node loadingFinished proves that observer's completeResourceBody:true.
CollectionComplete is true for both; no cloud EOF/React/host/cause claim follows.
Primary review`7c181b42`, independent runtime gate`73c73690` and Root rehash pass.
Raw index`304e67db` retains331 payloads/10,242,832 bytes. All original failures,
preparation failure/correction and prior Source-peer qualifications remain.
Source checkpoint`959454bc` is pushed. The saved-failure checker passes the
current corpus and an isolated333-file copy from actual staged Git blobs, while
requiring cloudfalse/NodeTrue and retaining resource-incomplete/complete. Root
compares every staged payload byte; optimized Python is explicitly refused.
Checker Source/binding peers`e6c76bb7`/`409899a0`, named-stage DATA peer`1a0853ba`
and outer proposal peer`ebdd744b` pass in their stated scopes. No runtime fix or
production promotion has occurred.

The [compiled-path audit](tests/node-compat/frameworks/nextjs/next-rsc-stream-observer-root-results-v1/native-response-lifetime-source-audit.md)
(`d0a35f2f`, peer`2a7c7aeb`) finds the active direct-standard-WASI response pump
separate from native HttpOutgoingBody.close's ignored finish result. That
separate native error-propagation defect is not established as this abort's
cause. The [public-stage DATA review](tests/node-compat/frameworks/nextjs/next-rsc-stream-observer-root-results-v1/public-completion-stage-data-review.md)
(`768f390a`) witnesses the named valid guest POST stage chain through EOF/child
release/finish return/cleanup, but seven unknown outer POSTs block the broader
join. Token1 and sequences repeat and do not establish physical identity.
The [outer metadata audit](tests/node-compat/frameworks/nextjs/next-rsc-stream-observer-root-results-v1/outer-observer-metadata-source-audit.md)
(`8e2ecc32`) finds deliberate V3 correlation clearing for unadmitted paths, not
proof of a getter failure. The separate [V4 Source](tests/node-compat/frameworks/nextjs/next-standard-handler-return-observer-v4/README.md)
now implements target/other/absent path classification and independent header
state with the same standard calls. Root's finite byte check passes48 variants,
maximum314B within512B. Two model syntax checks, five inert model groups and two
probe-runner syntax checks pass. A premature model preflight safely refuses a
changed, not-yet-frozen source before Node or output creation; its refusal and
exact preimage remain recorded. The final Source is frozen and actual WAT
build/composition and all seven deployed metadata cases now pass. A separate
binding preflight refuses Root's mistyped digest before edits/build; its correction
uses the saved typed descriptor. None/allocator behavior remains model-only.
Old V3 globaljoin:false is unchanged. The build volume now has about100GiB free.

Earlier completed work: the [full-workload CDP observer](tests/node-compat/frameworks/nextjs/next-rsc-stream-observer-root-results-v1/README.md)
now has independent Source/API reviews`7f6e9841`/`f26f5512`, six actual Node
syntax checks and17 actual synthetic groups passing. Earlier12 positive groups
missed post-terminal/empty-body/4MiB decoder counterexamples; those failures,
exact preimages and corrected tests are retained. Original01ca strict/UI/
deadline/drain predicates remain unchanged; the new observer is separate.
Fresh binding`af350c5e` derives2,060 inputs. First preparation fails before
socket/authority/target with missing stock-plan outerSeconds. Root's one-span
correction preserves the actual failure and qualifies both prior Source passes;
peer`cc5290a5` verifies cloud600 validation and unchanged fixed600/300 schedule.
Second preparation`94e0cd22` finishes raw0 with no actor invoked. Independent
binding/correction DATA review`721a82a4` reconstructs the exact union and passes
before the fixed cloud→Node pair. That actual pair now completes as recorded
above; original strict failures remain failed.

Latest bounded diagnostic: the [direct Chrome body control](docs/node-compat/nextjs-browser-body-prework-results.md)
passes once on stock wasmCloud59256/600 and Node59943/300, both raw0/clean.
Both pass24HTTP/52cache/80supplemental, generation1→2, stream3(0,1), then genuine
fetch/arrayBuffer2,963 bytes with independent CDP loadingFinished and no coding.
Page/console/failed-request errors are zero; browser/host/owner cleanup passes.
The intended391-byte POST and five script headers are verified; all13 browser-
managed values match after canonical origin mapping. Exactly one synthetic GET
and one real POST are observed. Actual hasUserGesture:true corrects the
prospective no-gesture assumption; no form/click is performed. React/router
are absent, so the original comprehensive strict failure remains failed.
Source checkpoint`2cc06c56` is pushed; Root terminal check`753fb61d` passes.
Primary DATA review`bc79b811` and independent runtime gate`03955d93` pass.
Raw index`44f69415` retains239 payloads/6,882,196 bytes; both physical35-byte
generation2 files are canonical with no pending file. Cloud config/dev complete
stdout is2,717/22,686 bytes. The portable copied-evidence checker passes the
current corpus and an isolated241-file copy from actual staged Git blobs.
Source/binding peer`c424ab34` verifies the exact three-pin inverse. Root rehashes
all239 payloads and compares every staged byte; no private build trees are copied.
Full Next remains failed. The [next-boundary Source audit](tests/node-compat/frameworks/nextjs/next-rsc-browser-body-prework-root-results-v1/next-boundary-source-audit.md)
(`c897ce46`) recommends bounded CDP resource streaming alongside unchanged
strict assertions; no new observer runner is implemented or launched.

Latest second-host result: the [compression-off stock wasmCloud trial](docs/node-compat/nextjs-compression-off-wasmcloud-results.md)
finishes original47197/600 raw1/clean. It passes24HTTP/52portable/80supplemental,
generation1→2, stream3(0,1), functionalUI2 and assets, but overall strict browser
fails POST7 ERR_ABORTED (three capture errors/one failed request). Status200 and
no Content-Encoding are recorded; body/sizes are unavailable and finished fails
before drain/close. Config inspection, exact2mounts/3guestenv/self-egress,
registration+TCP readiness, normal host shutdown and both complete stdout
captures pass. Primary DATA review`81a9c56b` and independent gate`185cecef` verify
the failed outcome. Raw index`09e9a040` retains155 payloads/5,368,231 bytes.
The observed abort also occurs with compression disabled; no cause is established.
Root rehashes the155-file raw corpus. The boundary audit`b5e4f87a` observes
SPA historyApi update/same loader before canceled:true, not a recorded MPA/new
document; cancellation initiator and HTTP EOF remain unproved. Fresh captured
request`a45dea80` retains this build's391-byte action and all19 ordered headers
with exact manifest provenance. The [identity raw-after-prework Source](tests/node-compat/frameworks/nextjs/next-rsc-identity-prework-root-results-v1/README.md)
now [completes both actual controls](docs/node-compat/nextjs-identity-response-prework-results.md):
cloud53303/600 and Node53776/300 finish raw0/clean. Both pass24HTTP/52portable/
80supplemental, generation1→2 and stream3(0,1), followed by HTTP200/no
Content-Encoding, complete/end/known socket cleanup and2,963 retained entity
bytes. Each identity copy matches its own raw file; cross-host hashes differ.
Captured Accept-Encoding stays unchanged; no gzip operation or wire-byte claim
is made. Binding`84aaacc3` derives2,047 fresh inputs and preparation`57b16d89`
executes the fixed cloud600→Node300 pair once. Independent binding review
`e83bc3c4`, Root terminal DATA check`2886ad91`, primary review`04f53121` and
independent runtime gate`c02e546d` pass. Raw index`3f20c56c` retains208 payloads/
5,576,656 bytes, rehashed by Root. Both physical35-byte canonical generation2
records have no pending file. Cloud config/dev complete stdout sizes are2,685/
22,686 bytes, with normal shutdown. The strict browser failure remains failed.
Checkpoint`bcc465b2` is pushed. The new portable retained-data checker passes
both the working-tree corpus and a210-file copy from actual staged Git blobs,
without private build trees. It starts no runtime. The next diagnostic isolates
Chrome fetch body consumption from React navigation. Its corrected6-file client
and14-file actor Source pass independent whole Source/API review`eefe5b3a`,
with all three actual Node syntax checks passing. Both preactivation observer/
serialization corrections have exact preimages/inverses. Fresh binding`a8e8084e`
protects2,056 inputs; preparation`29f9fe96` issues the fixed cloud600→Node300 pair
without invoking an actor. Independent binding DATA review`05ad2412` reconstructs
the exact union and passes; complementary Source/API review`b401c4d4` also passes.
Both actual browser controls now pass as recorded above; all original failures
remain failed. The next bounded Source audit examines passive response-body
observation within the original React/router path, with no new runner yet.

Latest result: the [compression-off full Next profile](docs/node-compat/nextjs-compression-off-full-results.md)
passes once on Wasm40483/600 and Node40694/300, both raw0/clean. Both pass24HTTP,
52 portable-cache checks,80 supplemental checks, persisted generation1→2,
incremental stream3(shell0,ready1), and both original strict browser tests.
Page/console/failed-request/capture errors are zero; POST7 body/finished/sizes
fulfill with2,963 decoded bytes and no observed Content-Encoding header.
Playwright reports response body sizes3,001/2,976; no raw-wire equality is claimed.
The browser worker01ca and every original full semantic predicate remain exact.
Binding`37db0289` protects2,041 fresh inputs and preparation`340af5c4` executes
each declared slot once. Independent binding review`e68db3bd` and full-gate recomputation`d6ab47a6`
pass. Primary review`e19aaa2d` verifies both full contracts and both physical
35-byte canonical generation2 records with no pending file. Raw index`55487d02`
retains257 payloads/9,536,752 bytes, rehashed by Root; native stdout is complete
at28,755 bytes/104 chunks with normal host shutdown.
This one configuration-profile sample does not resolve the original compressed
failure or establish reliability/general Node support/production promotion.

The [compression-off application](docs/node-compat/nextjs-compression-off-profile.md)
builds through original owners36534/120,36554/120,36565/600 and36633/900, with
2,196 files/48,805,615 bytes/431 child directories and no links/source cache.
Both emitted configs contain compress:false. Only19 fixture bytes change;
34 files and the tracing exclusion remain exact. Source5c280e4b, build review
9106545f, independent gate d4194323 and fresh5/4asset selection05c965a6 with
independent join a9fe908f pass. The92-payload build corpus totals2,795,484 bytes.
The stock host profile uses actual wash2.11.0 version/hash preflight and current
52-field admission. Binding`a069e157` protects2,049 inputs; preparation`c4c1e09c`
issues one literal origin and one original600 owner with no handoff guarantee,
fallback or replacement trial. The failed trial above completes that declared
slot. Lifecycle, resource/reuse, clean-machine, empirical cost and promotion
work remain outstanding.

The [raw response after non-browser prework](docs/node-compat/nextjs-rsc-prework-response-results.md)
passes once on Wasm34292/600 and Node34423/300, both raw0/clean. Both pass24HTTP,
52 portable-cache checks,80 supplemental checks, persisted generation1→2 and
stream5(0,2), then complete the raw RSC POST with normal gzip/CRC/ISIZE and HTTP
EOF. Encoded sizes1,486/1,492 both decode to2,963 bytes. Binding`b27b9b19` derives
2,028 fresh inputs; preparation`2bdd462d` executes each slot once. The exact
4,382-byte original pre-browser span runs on the same listener before replay;
Chrome/React and same-Store identity are not established. Primary review`026c026a`,
binding review`fa90206c` and independent runtime/gzip review`79d0bfa0` pass,
including all50 raw prework files per arm and both physical generation2 records
with no pending file. Raw index`61ce2c24` retains202 payloads/6,368,082 bytes;
Root verifies current and staged Git blobs. Checkpoint`1c1c7a21` is pushed.

The earlier [fresh-host raw replay](docs/node-compat/nextjs-rsc-http-response-results.md)
also passes once on Wasm29465/600 and Node29725/300, raw0/clean, with1,488/1,491
gzip bytes decoding to2,963. It preserves the actual391-byte body and all19
captured headers, rewriting Host/Origin/Referer and removing the old public
nonce. Reviews`0e74de45` and`e22f9f7a` pass; raw index`b3a97510` retains380
payloads/7,575,911 bytes with current/staged checks. Preparation's JSON-format
assumption failure and exact preimages remain retained. Both raw controls use
the unchanged app/engine/component and13 standard WASI0.2.10 imports. Neither
explains or waives the original strict browser abort; full Next acceptance
remains false.

Latest ported-fixture comparison: explicit filesystem-backed callback state
passes1→2 on both Wasm and Node. Both also pass24HTTP,52 portable-cache checks,
80 supplemental checks and five incremental stream chunks. Node19876/300 is
raw0/clean and passes the full suite. Wasm19501/600 is raw1/clean solely on the
retained strict browser POST7`net::ERR_ABORTED` failure; both functional browser
interactions pass. Both complete the full client with preserved inputs. The
physical callback records both contain canonical generation2 with no pending
file, independently verified by primary DATA review`c6846dbb`. Its528 retained
payloads total10,941,748 bytes; complete native stdout is28,788 bytes/108 chunks
with normal host shutdown and unchanged13 standard WASI0.2.10 imports. This is a new application
contract, not repaired module-global persistence; every older failure remains.

Current implementation: a separately versioned Next callback now persists its
bounded generation record under the existing standard writable cache preopen.
The original module-global fixture and failed result remain untouched. The
real Node reference for Next's `nodeFs.writeFileAtomic` passes3 cases/11
assertions (original12192/120, raw0/clean), including create-only publication,
EEXIST no-replacement and temporary-file cleanup. The callback helper's Node
conformance passes8 groups/9 real calls (original13933/120, raw0/clean), covering
lazy import,1→2 publication and fail-closed pending/corrupt/limit/alias cases.
Independent Node DATA reviews`0b5d842a` and`e8af5ecf` verify those two references;
the same helper also passes actual component HTTP, independently reviewed as
`2dba6246`:3 cases/11 assertions, HTTP200/2,385 bytes, complete capture and
original18925/180 raw0/clean. Its165 retained payloads total1,463,419 bytes.
Raw Node/guest rejection details are preserved; type/code match, while messages
and adapter operation/module fields differ. No whole-error-object parity claim.

The first35-file FS-callback host build passes all4 original monitored phases,
but is **not deployable**: Next traces8 build-cache files/74,976,273 bytes into
standalone, violating the unchanged empty-cache admission. DATA review`f5302c27`
verifies the2204-file artifact and83 retained records/2,576,661 bytes. No runtime
attempt uses it. V2 preserves34/35 files and changes only an explicit
`/api/cache` tracing exclusion for`./.next/cache/**`; no artifact is manually
filtered. Its fresh4-phase host build passes (`5db7f8`/session79563→`fa8b7b`),
with independent DATA review`4a6f03ce`:2,196 files/48,801,297 bytes/431 child
directories, no source cache or callback seed, and fresh5/4 browser asset pins.
The full runtime binding`349283e4` derives2,030 inputs with dynamic counts,
all six external client dependencies and genuine before/final source/world
guards. Fixed preparation`f402d56e` reserves native600→Node300 slots before
either actor. New FS-callback app assertions are unchanged; the original global
fixture remains a separate failed regression.

The first filesystem-helper constructor stops raw1/clean before invoking Node:
its copied working-directory metadata still named the old recipe. Failure
review`9ea9e562` and26 raw copies preserve this pre-Node defect. A new V2 recipe
corrects that field and checks it before authority issuance. The fresh V2
constructor (`72937a`/session7130→`da9d04`, original17011/2400) completes raw0/
clean using the same237c engine, complete metadata and selected13-interface
standard WASI0.2.10 world. INIT DATA review`f395dbe4` verifies the37,252,678-byte
component and complete returned graph with131 observed imports. Actual helper
HTTP then passes separately, as described above. No engine build, host
modification or new host interface is selected.

Checkpoint`d5eb3adb` pushes these Sources and retained counterexamples. The fixed
new-app full pair runs once per arm afterward: native`3c8456`/session49338→
`c39980`, Node`340d2a`/session60640→`36ab31`. The persisted-state gate passes;
the unresolved strict browser failure is again the Next.js critical path.
The staged Git blob check verifies all911 payloads/28,941,994 bytes across six
finite packets, preserving both failed preparations and runtime outcomes.
The [response-completion audit](tests/node-compat/frameworks/nextjs/next-fs-callback-root-results-v2/next-browser-steps.md)
locates real compression/Flight/body-EOF owners without a justified code fix.
Next is a conditional non-browser HTTP replay of the retained391-byte action
POST with captured-header restoration, checking actual gzip completion and EOF.
It is a new diagnostic workload; original strict browser failures remain intact.

Earlier comprehensive current-build comparison: **Node passes; Wasm fails only
the retained legacy generation assertion**. Both pass24HTTP,52 portable-cache
checks,80 supplemental checks, five incremental stream chunks and both strict
browser tests. Wasm records1→1; Node records1→2. Native7204/600 finishes raw1/clean,
Node7523/300 raw0/clean, with protected inputs and complete collection on both.
No test is waived. Independent six-file JSON gate crosscheck`7f416299` confirms
the unchanged conjunctions and this sole false term. Primary DATA review`303ca42f`
verifies both complete collections and632 retained payloads/13,614,165 bytes.
Native stdout is complete at28,746 bytes/111 chunks; the13 standard WASI0.2.10
imports remain unchanged. This is a positive current browser sample; previous
browser aborts remain unresolved, and full Next acceptance remains false.
The staged Git blob check verifies all632 raw payloads/13,614,165 bytes against
their original SHA-256 descriptors, preserving the failed native result and
passed Node result for future comparisons.

Current-build redirect comparison: **all three browser-only profiles pass**:
pristine Node891/600, real Wasm3802/600 and bridge Node4007/300, each raw0/clean.
The fixed matched pair ran once per arm after pushed checkpoint`18771094`,
with exact current app80c/browser7c3 and protected inputs. Both strict original
browser tests pass on both matched arms. Primary pair DATA review`1a689477`
verifies both passes and167 retained payloads/9,038,560 bytes. Next restore the comprehensive HTTP/cache/supplemental/stream workload
using this exact build and browser; keep the legacy generation and every original
predicate. No earlier failure is waived and no cancellation cause is established.

The comprehensive current-build successor is now prepared: full client and
actors preserve all original gates and order while selecting the physical7c3
browser. Source review and three actual Node syntax checks pass. Root bindings
`80ad6105` preserve whole metadata/controller inverses and freshly verify2,025
descriptors with genuine35 build/1,678 source references. Before/final original
constructor/world guards pass. Preparation`35f5ad50` fixes native600→Node300
authorities and fresh slots, with no actor launched at preparation. Execution
scope is derived from published stages, separately from semantic pass. No new
engine, component, observer, app build or host changes are introduced.
The first preparation is held: independent binding review caught the bare HTTP
fixture contract missing from its2,024-input union. All13 original metadata
payloads/1,809,307 bytes are retained; zero actors/trials had run. Exact unbound
Source was restored, and corrected binderV2 explicitly checks all six external
client requirements before deriving the fresh union. Original code/assertions
are unchanged. This qualifies the earlier binder Source PASS and records a
preparation defect, not a runtime failure or retry.
Independent corrected-binding DATA review`ac08a62d` passes all2,025 current
descriptors, exact Source inverses, separate client/browser family joins and the
complete13-file held archive. Git blob verification preserves that archive's
1,809,307 bytes exactly. After pushed checkpoint`02b98ac7`, the fixed pair runs
once per arm: native7204/600 (`fba975`/session94291→`48ae9c`) raw1/clean, then
Node7523/300 (`9d608d`/session89262→`f120b9`) raw0/clean. Both execute the whole
original client; only native legacy generation fails. Primary DATA review
`303ca42f` verifies both complete collections, the retained native semantic
assertion and632 raw payloads/13,614,165 bytes. Runtime/full Next acceptance stays
false. The held first preparation and its corrected dependency closure are
retained alongside the actual results.

Latest redirect control: **pristine standalone Node passes both current strict
browser tests**, including the redirecting Server Action. Original owner891/600
finishes raw0/clean with protected inputs; the requested standalone server
shutdown exits130. The browser records a complete2,963-byte POST7 response with
fulfilled body/sizes/finished. Primary DATA review`374f66d2` verifies the bounded
pass and123 retained payloads/5,245,828 bytes in
[the current control report](docs/node-compat/nextjs-current-redirect-control.md).
This uses the corrected2,196-file app and browser-only workload; the earlier
failed bridge/full pair used a different app and preceding workload. It therefore
does not isolate a bridge cause. Next: run both bridge Node and Wasm with this
exact app and browser-only worker before selecting a runtime fix. The volume
now has approximately42GiB free; launch/build capacity is no longer the current
blocker. Original full failures and production acceptance remain unchanged.

Earlier completed control: the corrected **non-redirecting real Server Action
passes on both Wasm and matched Node22**, raw0/clean, under unchanged strict
observer/deadline/error predicates. Both render the returned value, capture all
five pinned scripts and identical complete89-byte POST200 bodies with fulfilled
sizes/response.finished and no browser errors. Runtime DATA review`484af70a`
verifies this bounded result. The original full redirect/counter gates below
remain failed. See [control results](docs/node-compat/nextjs-nonredirect-action-control.md).

Earlier full application result: the fixed **observer-v3 Wasm → Node22 comparison
completes with both full suites failed**, without retries. Both pass24HTTP,
52 portable-cache checks,80 supplemental checks, five incremental chunks and
two functional browser interactions. Both fail strict POST7 capture with
`net::ERR_ABORTED`; native also retains legacy generation1→1, while Node1→2
passes. Native owner86135/600 and Node86371/300 are clean and inputs preserved.
This sample does not identify a guest-specific browser failure cause. All185
selected raw records/5,066,749 bytes are copied for future checks; independent
full-pair DATA review`75d04310`/84,472 bytes verifies the two failed results
and all185 raw copies. The staged-Git blob check also verifies all185
payloads/5,066,749 bytes against their original SHA-256 descriptors. Source/
document whitespace checks pass separately; captured bundle whitespace is
retained byte-for-byte. Native public DATA review`8ea7854b`
verifies51 typed V3 records,54 guest records and6 native records in complete
capture. One valid POST/actions record matches the public test tuple, while7
unknown-route POST competitors keep the conservative outer join failed. The
witness does not identify a private request/Store, observer return or cause.

Current implementation work: the separate non-redirect app Source is sealed
at index`ae30b268`. It preserves all31 parent files and adds three real
`useActionState`/Server Action files. Root independently verifies the selector-only
builder change and Source copies. Its four original monitored host-build phases
and pinned dependency versions are retained. The new strict-browser Source
preserves the original observer/lifecycle bytes; generated script pins and app
bindings remain pending the actual build. No new engine/component build is
required or claimed. The old full-pair failures remain unchanged.
The actual host build now passes (`ff098e`/session37098, completion`aa136e`)
under original4 owners89901/120,89912/120,89922/600,90029/900, with Source/
tool/native/world guards preserved. Result`4313cdd7`/715,210 bytes derives
2,196 standalone files/48,800,573 bytes/431 directories, genuine new BUILD_ID
and two action IDs. Root derives five eligible scripts from six generated
external script elements, excluding the real noModule polyfill. Build DATA
review`ee491e55` verifies all2,196 payloads, manifests and original phase
owners. New browser/runtime Source passes review and all four Node syntax
checks. Fresh bindings`d69c6809` contain1,926 current host descriptors and
separately typed five browser URLs with their real physical asset files. The
first intake mistook a URL for a filesystem path and failed before authority;
that refusal is retained, the reader corrected, and original native/world
guards still pass. JSON-only pair preparation`97459c81` now completes with
both fixed authorities. The declared v1 control pair now completes once per arm:
native93323/600 and Node93597/300, both raw1/clean with protected inputs. Both
render the returned value and pass five script hashes plus the unique POST200
body/hash/sizes/response.finished checks, with no failed requests or observer
errors. Both remain failed solely on the same Chrome console error: the new
fixture's HTML pattern`[a-z0-9-]+` is invalid in UnicodeSets (`v`) mode. This is
not waived. The [HTML Standard](https://html.spec.whatwg.org/multipage/input.html#the-pattern-attribute)
requires that compilation mode. A new separate fixture version will correct
only that pattern while retaining this failed pair and unchanged strict checks.
V1 runtime DATA review`9c474a61` verifies both failed controls and their
positive89-byte POST captures. The63-file raw packet is3,150,631 bytes.
The corrected v2 fixture preserves33/34 files and changes only the HTML pattern
to`(?:[a-z0-9]|-)+`;264 host-Node UnicodeSets cases pass. Its real fresh build
(`bcbaf2`/session85573, completion`1a2663`) now passes all4 original owners,
with result`26bce5aa`,2,196 files/48,800,578 bytes and new generated action IDs.
Five script hashes are derived from its real HTML. Build DATA review`80c59d47`
verifies the complete new payload and corrected pattern. The byte-identical
browser/runtime code is separately sealed with fresh v2 app and asset bindings;
Root verifies whole controller-preimage/namespace and binding inverses. V2
runtime preparation`ef1b28b0` completes without launching actors. The subsequent
fixed v2 pair passes: native96345/600 (`376109`/session59202→`db4127`) and
Node96562/300 (`7dd3c8`/session63062→`e7377e`), both raw0/clean with current
inputs preserved. Both have real same-page action value, exact five script
captures, one POST200 with complete body/sizes/finished, and no browser errors.
The sole fixture correction is not an observer/gate change. No v1 or original
redirect outcome is overwritten or waived. V2 runtime DATA review`484af70a`/28,221 bytes verifies both strict passes,
all owner/capture/source/app joins and the unchanged v1 failure. The corrected
control does not identify a redirect cancellation cause or accept full Next.js. The staged-Git
raw-corpus check verifies all184 v1/v2 build/runtime payloads/10,526,524 bytes
against their original SHA-256 descriptors, preserving both negative and
positive evidence.






Current critical-path work: the pristine standalone redirect control is complete
with the current v2 app and original800f two-test observer. Current
client/actions HTML selects5/4 scripts; physical hashes and inventories are
independently verified. The new browser preserves the original functional,
network-observer, deadline/drain and final strict predicates; only its genuine
current asset bindings and control labels differ. No app/engine/component
rebuild is needed. Both launcher and browser Source pass whole review. The
first dependency intake refused a documentary asset URL before authority;
explicit executable/app/browser dependencies replace that recursive intake and
the refusal is retained. Genuine original source/world admission passes before/
final; all four Node syntax checks pass. JSON-only preparation`51e87986`
issued one pristine600-second control authority. Its actual original owner891
finishes raw0/clean; both strict browser tests pass. Primary DATA/raw retention
is complete. The exact-app browser-only bridge/Wasm comparison is prepared.
Whole Source review and both Node syntax checks pass. Root bindings`8a9f31be`
preserve exact plan/controller inverses and freshly verify2,016 protected inputs,
genuine35 build/1,678 source references and the whole constructor/world guards.
Preparation`3664207d` fixes both authorities and fresh slots before any actor:
Wasm original600-second owner, then bridge Node original300-second owner.
No new engine/component/observer build or application warmup runs. The actual
fixed pair then finishes once per arm, native3802/600 (`0159c0`/session13562→
`1b5843`) and bridge Node4007/300 (`2b4104`/session86288→`f6fba9`), both raw0/clean
with protected inputs and strict browser passes. Pair DATA review`1a689477`
verifies both strict passes and167 retained payloads/9,038,560 bytes, including
normal host shutdown and complete13,459-byte native stdout. Source preparation for the comprehensive current-build comparison
is underway; no new engine/component or host changes are planned.


Outstanding critical work:

- Define and test the Next persistence integration separately from arbitrary
  cross-request JavaScript-global continuity. The comprehensive current build
  passes every gate except that retained native legacy assertion. Keep original
  failures and current positive samples distinct. The [current Source audit](tests/node-compat/frameworks/nextjs/next-current-full-root-results-v1/next-steps.md)
  identifies the callback's module-local `++misses` and the separate passing
  nonce/invalidation profile. Next is a separately versioned bounded FS-backed
  callback-state gate using the declared route/tag and explicit standard cache
  preopen; no global continuity, concurrent increment, CAS or durability claim.
  Real `nodeFs.writeFileAtomic` branches need a small component test if selected.
  The [Source-backed
  next-step audit](tests/node-compat/frameworks/nextjs/next-nonredirect-action-root-results-v2/next-steps.md)
  locates the existing bare-Node launcher and its earlier strict pass, while
  preserving the current app/worker/asset gap. The bounded
  non-redirect control is complete. The [Source audit](tests/node-compat/frameworks/nextjs/next-standard-handler-observer-root-results-v1/next-steps.md)
  finds no proved deliberate POST cancellation. The Node sample navigates within
  the same document and fails before fixture closure; one failed request feeds
  three observer errors. This Node arm uses the shared bridge profile, not a
  pristine standalone server. Keep both original redirect failures intact.
- Keep arbitrary cross-request JS-global continuity unavailable in the portable
  profile. The explicit filesystem cache subset passes; it does not restore a
  single Node process or waive the legacy counter gate.
- Complete lifecycle/reuse/concurrency, second-host application limits,
  clean-machine reproduction and empirical size/startup/memory/throughput gates.
  Broader Node compatibility and production promotion remain open.

Current critical-path work: a standard-interface return observer is built and
independently type/structure reviewed. WAC CLI0.12.0 builds offline under
original74822/900, raw0 (`8563f9`/session84552, completion`e121a4`), with Source/lock
unchanged. Actual inspection confirms synchronous inner lift plus configured
post-return. V1 validates but WIT decoding panics; both failures remain retained.
A separate v2 uses the existing Starling type-only export shim and passes all7
parse/compose/validate/WIT/print steps (`19ddeb`/session80788, completion`d30c12`).
Envelope`e08b368b` retains exact inner`d04c4289` bytes and the same13 standard
WASI0.2.10 imports/single handler export. Composition DATA review`1c1f8bae`
joins structural review`986a82ce`. The one-GET `/none` runtime actor/controller
pass whole Source review. JSON-only preparation (`4e5987`/session85269,
completion`a9e2b8`) issues authority`199d0c1c`/2,417 bytes; no actor invoked yet.
See the [observer checkpoint](docs/node-compat/nextjs-standard-handler-return-observer.md).
The subsequent actual mechanism runtime passes (`2fb81e`/session16148,
completion`4227ba`), original79199/180/raw0/clean after checkpoint`431743d4` is
pushed. Exactly one GET returns expected371-byte HTTP200 and the sole94-byte
marker. Complete capture, normal Wasmtime79204 shutdown and current inputs/
native/world guards pass. Runtime DATA review`0241d47c` verifies this bounded
configured-inner-post-return witness, without observer-return/host/TCP/private/
cause/Next claims. A separate v3 public-metadata observer now passes all7 actual tool steps
(`b6f21e`/session43893, completion`f77332`). Envelope`a3196c70` retains
exact inner`d04c4289` plus observer`e3cdb976`, with the same13 imports.
Composition DATA review`c80d7319` verifies shared fields types and canonical
getter options. Six fixed method/header probes are in Source review; runtime
metadata behavior and use with the real Next app remain unverified.
The fixed-six Source is sealed after correcting final I/O-vs-semantic error
classification before execution. Root Node22 syntax check passes. JSON-only
preparation (`8fe780`/session62354, completion`fac4d3`) issues authority
`8f41cfcf`/2,427 bytes under genuine existing constructor/build/world guards.
Actor/runtime execution remains pending at this checkpoint.
The subsequent fixed6 run (`2533d4`/session19082, completion`bb895b`)
passes raw0/clean under original83433/900. All6 are attempted exactly once,
with complete collection and normal per-case shutdown. Result`349d3ce2`/44,951
bytes records expected GET404/POST405 fixture responses and exact V3 metadata:
missing/count0, valid/count1, uppercase-invalid/count1, duplicate/count2,
GET/POST and both paths. Current native/world/input guards pass. Raw records
are copied for future checks; runtime DATA review`c56ec847`/58,173 bytes
independently verifies the bounded result. It delegates large binary hashes to
the actual Root guards and composition proofs rather than claiming a fresh
full binary hash sweep.
No Next completion fix or broader allocator/resource-lifetime acceptance is claimed.
The unchanged actual Next component`6b2084d0` is now composed with v3
(`30dc5c`/session73446, completion`3d9bf7`). All4 new composition/validation/
WIT/print steps pass; envelope`e4c79871` is37,298,513 bytes, same13 imports.
Genuine Next constructor/build/world admission passes before/final. New
composition DATA review and a separate full-app runtime Source are in progress;
the new Next envelope has not yet served a request.
New composition DATA review`b333fbc7`/33,472 bytes verifies its exact raw
children and same synchronous/nominal-resource structure. The full Next actor
and Root controller pass Source review, keeping original client/browser gates
and inner constructor roles. Root derives1,859 current protection descriptors
from genuine fresh constructor context (35 build/1,678 source refs, including
825 pairs), actual component/review graphs and host dependencies; the previous
1,771-item protection array is not copied or retargeted. Node syntax checking
passes. JSON-only preparations issue native authority`e03ce8e5`/3,502 bytes
and Node control`92cf7606`/1,718 bytes; neither full actor has started. The fixed
native→Node comparison is declared before execution, with shared physical
browser/app inputs, matching public values and no retries/replacements.

Current completed helper milestone: the same real-filesystem cache suite passes
**11 groups/41 assertions on Node, Wasmtime and stock wasmCloud**. Independent
differential reviews verify identical assertion details and23 cache files per
arm, with only generated epochs/timestamps normalized. The original full Next.js
contract remains failed; production remains foundations-v13. Next priorities are
browser completion, explicit request-state limits, lifecycle/resource checks,
clean-machine bootstrap and measured costs. Broader cache races/crash durability
remain outside this bounded helper result.

Diagnostic-pair checkpoint: `aa1afd42` on `origin/main`, containing the completed
native-to-Node diagnostic comparison, independent DATA reviews and both portable
raw-corpus checks. The Next.js test README now leads with this current failed
full-acceptance result; its earlier smoke status is explicitly historical.
Complementary whole-reader Source and copied-DATA review also passes, with no
material holds: all 350 pair payloads, 33 analysis inputs, 54 guest records and
six native records are verified without opening original paths or executing
the reader/analyzer/target. Its additive receipt preserves full acceptance false.

New implementation: the real-filesystem cache overlap/error/bounds suite now
passes its first Node22.14 reference run: **11 groups/41 assertions**, original
owner65596/raw0/clean (`9738b5`/session34763, completion`edf36f`). It uses the
unchanged handler and real pinned Next delegate/nodeFs, with no dependency
fakes. All2,186 app files/48,755,844 bytes/427 directories and selected Source
inputs remain unchanged. The [reusable launcher and actual records](tests/node-compat/frameworks/nextjs/next-persistent-cache-overlap-root-results-v1/README.md)
preserve this Node-only scope. A new guest entry and constructor are being
prepared to run the same suite inside the actual component; guest parity and
second-host checks remain pending. No new native build or capability is needed.
The new guest/constructor/Root scripts and ordered Source bindings now pass
whole Source review. JSON-only preparation completes (`6c8ee0`/session1931,
completion`178394`) with genuine authority`54a24c40`/5,596,685 bytes; no actor has
been launched at this cutoff. The existing complete-metadata/build guards,
parser-only WIT preopen and original construction ceilings remain in use.
The subsequent actual INIT now completes raw0/clean under original owner66965
(`d78d54`/session28985, completion`489618`). Component`66a3ed9e` is37,239,204
bytes. Coordinated INIT DATA review`0599a450` verifies the complete return
graph,131 observed tuples on the same13 standard WASI0.2.10 interfaces,
incoming-handler-only export, all4 clean owners/8 streams and no deployed
suite/app work. The one-GET guest runtime actor is being prepared; its actual
suite result remains unobserved. Node cache and constructor preparation
checkpoint`20e110d4` is pushed to`origin/main`.
The one-GET guest actor and Root controller now pass whole Source review;
actual INIT roles are bound through genuine review`0599a450`, with actor index
`7073c030` and plan`16cad8e9`. Root verifies the exact metadata-only changes
and two controller descriptor inverses. JSON-only runtime preparation
(`e1a9b1`/session3510, completion`5e2594`) issues authority`5c8ae0d7`/4,386 bytes
without launching an actor. The fixed test remains one GET, original180-second
owner, no HTTP warmup/retry/guest environment or new capabilities.
The subsequent actual guest runtime completes raw0/clean under original
owner69109/180 (`a75c6b`/session69211, completion`21bbbe`). Its one HTTP200
response is9,307 bytes complete. All11 groups/41 assertions pass and match the
Node reference exactly. Coordinated runtime differential DATA review`d474a118`
verifies owner/capture/body/source/copy joins and all23 files/40,541 bytes per
arm; canonical records match after only epoch-token/lastModified normalization.
No Node or target rerun occurs during review. The finite54-file INIT record
copy is275,126 bytes; the58-file runtime/fixture copy is129,191 bytes. Large
binaries, app/package/native metadata payloads are explicitly omitted from
these copies. This accepts only the fixed cache-helper subset on Wasmtime.
Stock wasmCloud, concurrent processes/crash durability, broader lifecycle/costs,
original legacy generation and intermittent browser failures remain open.
Checkpoint`f59e0db8` was pushed before this guest launch. A compact reusable
guest-run CLI and the stock wasmCloud one-request Source are being prepared;
neither has executed a further target.
The future fresh-ID guest CLI is now Source reviewed; Root`10238e` checks
`--help` only (raw0/empty stderr), leaving its operational modes unexecuted.
The separate stock wasmCloud actor passes whole Source review against the
actual three-volume configuration APIs. Its Root controller retains the
genuine original guards and180-second owner, adding explicit stock-host/config
permission while denying external egress/new services/host mutation. Only
genuine0599 INIT roles are Source-bound. JSON-only preparation
(`21ab5b`/session40978, completion`22ed9b`) issues authority`a98fb01b`/4,550 bytes
with no actor invocation. This is still a pending second-host execution gate.
The first stock actor then stops before dev/HTTP/guest work: original71142/180
finishes raw1/operationally clean (`75a987`/session70965, completion`b8a3e8`).
Config-show succeeds with complete2,812-byte capture, but its effective
`environment:{}` omits the empty `config` map, violating the harness's old
unconditional assertion. Failure DATA review`4c060524` preserves that failed
experiment and unobserved guest result;11 finite records/16,792 bytes retain
the raw preflight. Pinned Rust serde Source confirms empty-map omission.
A separate v2 changes exactly one executable predicate, accepting only the
entire environment `{}` or `{config:{}}` while refusing other shapes/values.
Whole/narrow Source reviews pass; v1 Sources/results remain intact. Fresh v2
index`95ca9c27`/plan`6e290fc0` and controller`33fda2ee` retain all16 flags,
three mounts, empty environment/egress and original180-second owner. JSON-only
preparation (`b4b644`/session32019, completion`cb73e9`) issues new authority
`e2529f90`/4,553 bytes without launching another actor.
The fixed new v2 stock trial now completes raw0/clean under original72460/180
(`e49196`/session22659, completion`e2765d`), after checkpoint`e25b203f` is pushed.
HTTP200 delivers9,307 complete bytes. All11 groups/41 assertion details exactly
match Node and Wasmtime. Config-show72474 exits0 with complete2,830-byte stdout;
dev72479 stops normally with complete42-byte stdout. All23 cache files total
40,541 bytes; source/copy/final guards pass. Independent v2 DATA review is
pending. V1's pre-dev failure remains unaccepted and unchanged. This positive
helper scope does not accept the original full Next.js contract or fix either
its module-global generation limitation or intermittent browser completion.
Independent stock-v2 differential DATA review`fbe6f91f` now passes, verifying
all41 assertion details against Node and Wasmtime, all23 actual cache payloads,
both complete stdout captures, quiescent stderr hashes, exact three mounts,
empty effective environment and deny-all egress lists. The short config process
is explicitly not observed between owner samples; its direct child status and
capture are joined separately. V1 remains bound/unaccepted. The39-file v2
runtime/fixture copy totals106,157 bytes. This closes the fixed helper's selected
second-host gate while preserving global runtime/full Next acceptance false.

Active experiment: the opt-in native export diagnostic has passed Source review,
both C++ frontend modes, fresh 825-file materialization and all ten generator
checks. The full native build now finishes raw0/clean under original owner28096
with its 7,200-second ceiling (`37f8d3`/session59432, completion`572b44`). Engine
`237c4e5a` is 31,350,211 bytes; metadata`500e76ac` records the diagnostic ON
definition only in the separate embedding compile, with none in the 80 native
compile rows. Coordinated build DATA review`7e5311ad` and Source/link
review`b473d4c9` pass for this build-only scope. Probe component`d04c4289`
(37,156,919 bytes) now constructs/validates at raw0, with coordinated INIT
review`163eb782`: 131 observed imports across the same thirteen standard
WASI0.2.10 interfaces, incoming-handler-only export, full returned graph and
complete marker-free INIT capture. All seventeen deployed cases now finish
raw0/clean (`f085c120`), with complete capture and final protection. Independent
semantic review confirms sixteen records and all seventeen response contracts;
coordinated review`91e961ab` binds owner/capture review`77fbda3f`. The new real-Next
component also constructs at raw0 as`6b2084d0` (37,282,148 bytes), with the same
thirteen standard interfaces; coordinated INIT review`5c284564` binds
owner/world review`8890980b`. The fixed native→Node comparison now completes
raw0/clean as an experiment. Native passes HTTP/cache/stream/function and strict
browser checks in this sample, but legacy generation1→1 keeps its original full
suite false; Node passes every gate. Complete stdout is19,019 bytes. The first
bounded dual-marker analysis observes one conservative public POST metadata
join at the native success site (`af787ee6`). Coordinated pair DATA review
`83ba87fe` and independent correlation review `0220cebc` verify these outcomes
while retaining native false/Node true/full Next.js false. The portable pair
corpus contains 350 payload files/12,549,393 bytes and passes current-tree and
staged Git-mode checks (352 total files). The separate seventeen-case corpus
also passes both checks. The first pair Git-copy preflight stopped on an
incorrect control-file count before copy creation or reader execution; the
failed preflight receipt and corrected successful receipt are retained.
This positive sample establishes no fix for the earlier
intermittent browser failures. Source/build preparation
checkpoint `2cd7de93` is pushed to `origin/main`.

Next.js executes in a real Wasm component. The fixed ten-trial comparison passes
both Node controls and one of eight guest full-suite samples. All ten pass HTTP,
persistent cache, streaming and functional UI checks; seven guest generation
gates and three strict Server Action completion gates remain failed. Independent
DATA review verifies these outcomes. Portable evidence retention and offline
checks pass for that comparison. The new full stock wasmCloud profile also
passes HTTP/cache/supplemental/stream/function checks and retains generation1→1
and strict POST completion failures. Its DATA review, raw retention and
current/Git-mode offline checks pass. Public request correlation now matches the
actual POST across browser and guest observations while preserving its strict
completion failure. The fresh native diagnostic engine, direct-WASI probe and
full Next.js regression are now complete. Persistent-cache overlap/error/bound
checks are the next implementation work. A source-only standard-interface
composition proposal is being assessed for a later canonical-return observation;
no observer component or new host capability has been activated. No fix,
reliability result or production
promotion is established.

Current engine baseline: native Fetch cleanup compiles and links, a fresh interoperability
component passes INIT construction review, and all16 deployed module cases pass
in one GET with independent runtime review55a255e7 accepted for that subset.
A separate public Fetch lifecycle component passes INIT construction review
(`4b3b0f43`); its first real runtime comparison now exits0 with all eight public
test groups passing against the pinned Node reference; coordinated DATA
review705270ee passes for that public subset. The fresh real-Next component also constructs and validates
successfully (`d990ecc1`,37,241,086 bytes). A first pre-HTTP harness prefix
failure is retained; a separate correction preserves every operational byte.
The corrected full Next.js run now completes: all HTTP, supplemental,
persistent-cache, streaming and functional browser checks pass. Legacy
generation1→1 and strict Server Action `ERR_ABORTED` remain failed.
Two subsequent normal-input controls pass: the current captured action response
fully drains with valid HTTP/gzip integrity on both Wasm and prepared Node, and
the2-MiB gzip composition probe observes16 backpressure/drain cycles with valid
EOF/CRC. A subsequent Chrome NetLog pair preserves both native failures while
the prepared Node control passes. No explicit negative net error in the selected
NetLog request contexts identifies EOF or a cause. The current component now
passes stock wasmCloud cold8, raw0/clean/protected, with coordinated DATA
review0ed0e4c2. It cannot waive full-suite failures.
The matched identity-encoding browser pair now also completes: explicit POST
negotiation/absent response Content-Encoding pass on both arms, while native
retains the same cache and strict browser failures and prepared Node passes.
Coordinated DATA review8151dc47 passes that outcome review. The subsequent
response-completion diagnostic constructs and runs: reviewd0085b5c verifies
complete bounded stdout capture and preserves both failed application gates.
Its54 records reach the adapter's EOF, disposal, finish, cleanup and normal-return
sites, without proving export-Promise or host/TCP completion. The source audit
finds no verified settlement defect. A separate child-handler Promise observer
now constructs and validates as componentcd60c673 (37,260,823 bytes). Its
coordinated INIT review0013502c observes131 imports on the same13 interfaces,
with clean ownership and no INIT markers. Its first full deployed run now
finishes1/clean/protected:52 persistent-cache checks,80 supplemental checks,
24 HTTP cases, five stream chunks and both strict browser tests pass. POST7's
body (2,963 decoded bytes), finished signal and sizes all fulfill, with no browser
errors or failed requests. Legacy generation1→1 keeps the overall suite failed.
Complete stdout capture retains14,762 bytes; coordinated runtime DATA review
4d47759f verifies these outcomes and retains failed overall acceptance.
One instrumented positive sample is not a demonstrated fix or
reliability result. Its
added await observes existing Promise adoption and can perturb scheduling;
it is not a demonstrated fix. No native or host change is selected.

Current next steps and outstanding work:

- **Next.js critical path:** the Root controller is complete and the reviewed fixed
  ten-run comparison has completed under its original7,200-second owner. All ten
  authorities were validated before the first trial. Both new entry-only
  await variants now compile and pass INIT review. Investigate
  completion stability against the retained failed samples without retry-based
  acceptance. The response-site trace cannot establish export or transport
  completion. Separately resolve
  the legacy counter contract against per-request guest state; durable-cache
  success does not waive that failure. Expand the second-host action/browser
  contract only with an explicit self-origin egress policy. The
  [priority roadmap](docs/node-compat/nextjs-priority-roadmap.md) tracks this order.
  The [request-state contract](docs/node-compat/nextjs-request-state-contract.md)
  distinguishes module-local state from persistent cache behavior; it makes no
  claim about a private Store or the exact observed failure cause. The separate
  [completion comparison proposal](docs/node-compat/nextjs-completion-stability-plan.md)
  isolates await and response logging through fixed arms; all ten trials are
  collected and independently reviewed; portable DATA retention and replay pass.
  Independent Source review passes both documents; the request-state note's
  preliminary review-status sentence is updated to the held4d47759f result.
- **Current execution checkpoint:** commit `6ba984ae` is verified on `origin/main`
  with a clean tree before launch. Root tool3e092c/session1711 starts the fixed
  cohort under original owner92634/7,200 seconds. The current volume has47GiB
  free. No additional trials, replacements or retries are authorized by this
  schedule. Collection completion, each original gate and final acceptance
  remain separate; no current run is adjudicated from partial output.
- **Completed comparison, DATA review complete:** Root2e8b71 observes outer raw0;
  Rootb21d29 verifies its clean terminal and all eight native stdout hashes,
  lengths and finalized complete capture metadata before marker analysis.
  Every fixed slot is collected-valid; `originalAllPassed` remains false.
  Complete publications show both Node controls passing. Native B/block1
  passes the original full suite with generation1→2; the seven other native
  samples retain generation1→1. Strict browser completion passes A2/2, B2/2,
  C0/2 and D1/2. These are exploratory observations, not a reliability estimate
  or evidence that await/logging causes the difference. No replacement trial
  or native fix follows from this result. Coordinated primary DATA review
  `3929a4af` binds ownership/browser review`12922bb9` and marker review`cace7809`.
  All ten trials pass 24 HTTP cases, 52 persistent-cache checks, 80 supplemental
  checks, five stream chunks and functional browser checks. All three failed
  POST terminals precede capture drain and context close in their own observer
  clocks; all 20 pre-close drains complete. Each C/D sample has 54 positive
  response-site markers, despite mixed browser outcomes. Root independently
  rederives all 216 frame arrays/counts from authenticated stdout
  (9c46b9). These sites prove no export/host/TCP completion. The finite portable
  corpus contains 1,332 payload files/32,007,325 bytes. Source review catches and
  corrects an offline-reader chunk-count type mismatch before execution, with
  all retained data unchanged. C's corrected Source/copied-DATA review passes
  (378361). Root's standalone check f3f3b7 exits0, saved in
  [retained-data-check.json](tests/node-compat/frameworks/nextjs/next-completion-comparison-root-results-v1/retained-data-check.json);
  R's separate Git-mode check also exits0. Both verify 21 selected namespaces,
  637 raw client files, 240 HTTP body hashes, 20 PNGs, eight complete native
  captures and 216 markers while preserving failed overall acceptance. Neither
  opens original paths, runs a target or revalidates omitted binaries/app trees.
  The
  [complete result table](docs/node-compat/nextjs-completion-comparison-2026-11-08.md)
  preserves every sample. The subsequent comprehensive stock wasmCloud profile
  with exact self-origin allowance is recorded below; original failed gates,
  broader lifecycle/cache overlap, costs and production promotion remain open.
- **Completed different-host implementation and failed full-suite result:** the different-host reuse
  plan `8a268f33` has independent Source review. A new full-contract stock
  wasmCloud actor and Root preparation/wrapper are prepared from
  the existing cold host mechanism. They select the unchanged D990 component,
  f805 app and full client/browser checks. One canonical literal loopback origin
  must bind the exact port and normalized one-entry egress rule; no fallback
  port, host modification or new component import is added. Actor `f22d805c` seals
  18 payload files/127,795 bytes after independent Source/closure review. Root
  syntax checks for all three JS files pass0/empty output, with the external
  grammar receipt preserving actual argv/cwd. Root/B/R review the genuine
  preparer/wrapper and caller coupling; the sole actor-SHA binding produces
  wrapper `95f360f1`, with exact reversal to its reviewed unbound bytes. Natural
  client exits0/1 may publish log digests; interrupted/error/other exits retain
  paths and delegate descendant finalization to the original monitor.
  This Source checkpoint is pushed as `424ba3f2`. Root selects the single origin
  `http://127.0.0.1:61785` (5589a4), then preparation218aaf/bd3fdc exits0 with
  authority`906c12e3`/534,525 bytes, 1,784 fresh protected descriptors, all
  825 source/target pairs and actual31/39/18 roles. The one full target run
  f3e83a/328181 finishes1 under original owner194/600: clean, no timeout/force,
  inputs/world preserved. Config-show/dev/full-client exit0/0/1. Independent
  primary review`c528ca22` binds owner/config/browser review`519e3dd7`: all
  24 HTTP/52 persistent-cache/80 supplemental/five-chunk/function checks pass;
  legacy1→1 and three strict POST7 errors with one ERR_ABORTED remain failed.
  Effective configuration contains exactly one normalized self-origin rule,
  three guest environment values and the two mounts. Actual cache children are
  files0600/directories0700; c101 does not explicitly request those modes.
  Direct-fd log hashes after owner cleanup do not establish pipeEOF, a lifetime
  log bound or transport completion. The
  [full second-host report](docs/node-compat/nextjs-wasmcloud-full-contract-2026-11-08.md)
  records these limits. Its finite raw corpus contains 148 payloads/3,666,674
  bytes. Whole reader Source/copied-DATA review473cd7 passes; Root's actual
  offline check61465e and R's separate Git-mode check both exit0. They verify
  both selected namespaces, 63 client files, 24 HTTP body hashes, two PNGs and
  six direct logs without original paths or target execution. Failed original
  gates stay failed; omitted payloads and full52/80 semantics are not replayed.
  The earlier ten-trial evidence is complete and pushed in`cea5d5d5`.
- **Next Source proposal, unimplemented:** public request-correlation plan
  `fbc52612` has independent Source review. It proposes a versioned 64-hex public
  per-test header, actual Playwright/NetLog sent-header evidence and independently
  observed adapter/classic fields, preserving every original assertion. Existing
  context headers and genuine header-conversion paths supply the integration
  points; a plan field alone cannot retarget the hardcoded browser worker.
  Future worker/client/guest/constructor/runtime bindings and results remain
  NULL. Spoofing, duplicates, coalescing, inner forwarding, missing records and
  scheduling effects remain explicit. No new trial, native patch, private
  identity or cause is claimed. Persistent-cache overlap/error/bounds, lifecycle,
  clean-machine bootstrap, measurements and production promotion remain open.
- **Public correlation implementation in progress:** the previous goal turn made
  concrete progress through the full stock wasmCloud run, independent reviews,
  portable checks and pushed checkpoint `a69c1997`. This turn implements separate
  guest, browser and client Source versions from the reviewed correlation plan.
  The guest V2 draft preserves body/ownership/await paths and observes bounded
  header metadata at the existing adapter/classic boundaries. Browser/client
  drafts preserve original gates and select a host-only manifest through real
  CLI paths. Constructor scaffolding reuses exact generic operations and original
  native/world guard contexts. Root is preparing unbound native/Node control
  actors; the new Stock runner explicitly adds an authority-path argument while
  the full-client CLI remains unchanged. Source reviews pass the guest,
  browser/client and unbound host operations. Root's guest syntax check and
  actual private-helper seam pass all 21 cases with zero accessor calls. Seven
  host JS syntax checks also pass. Host metadata seam tests pass all 15 cases
  after canonicalizing the fixture's macOS temporary-path alias; the first
  fixture-only raw1 is retained. Source review catches and corrects exact-length
  and newline predicates in both host metadata helpers before activation.
  Guest `f8c6d52b` and constructor `6ef36102` seal their reviewed payloads;
  Root's literal-only constructor pins reverse exactly to the reviewed unbound
  files. Browser `a2e8ca55` and client `9a4b5958` are now sealed. Checkpoint
  `526b4da3` is committed and pushed. The actual same-world constructor ran once:
  raw0, no timeout/signals/forced cleanup, all observed owned groups gone. New
  component `df8d7420` is 37,266,121 bytes. Independent INIT checks observe the
  complete returned graph (131 functions, an observation rather than a target),
  the same 13 standard WASI imports, and incoming-handler-only export. The four
  original owners and current world/Source inputs pass complementary review;
  no deployed correlation markers appeared during INIT. Primary `1dff8468` and
  owner/world `b0549965` reviews are held. The offline INIT checker passes all
  80 retained files (649,898 bytes), reads no original paths, and explicitly
  excludes omitted binaries/package/app validation. Runtime actor bindings are
  held at native `67f4eaf6` and Node `eb286ac0`; fresh protection includes all
  1,650 native source/target descriptors. The first DATA binder stopped before
  writing on an incorrectly named bridge index; its source/failure are retained
  and the corrected binder passed. The pair driver passed Source reviews and
  six existing pure publication-policy tests. Both fixed native→Node authorities
  are prepared, with four public header values declared before either trial.
  Checkpoint `9954a664` is committed and pushed. The declared pair then ran once
  under the original 1200-second monitor, completing cleanly in 23.34 seconds.
  Root observes native raw1/full-suite false and Node raw0/full-suite true.
  Native cache1→2, 52 persistent-cache checks, 80 supplemental checks and five
  streaming chunks (shell0/ready2) pass. Its strict browser result remains false:
  POST7 `/actions` reports `ERR_ABORTED`, with three retained observer errors and
  unavailable body/sizes; both visible interactions succeed. Node passes the
  strict browser checks too. Native stdout is completely finalized at 17,508
  bytes within the 8 MiB limit. All original failures remain failures; driver0
  records a clean experiment, not test acceptance. Owner/browser review
  `75095ddc` and correlation review `96e7d886` are held. Root's bounded analyzer
  `558dc24d` observes a unique public POST metadata match across Playwright,
  NetLog and adapter/classic entries. All 54 marker witnesses match raw stdout;
  the matching POST has nine named sites, including EOF1,488 bytes/seven reads.
  Invalid/duplicate competing header observations now block a match, with 17
  actual pure decision cases passing. A mistaken Root argv-hash preflight stops
  before analyzer execution and is retained; the corrected actual analyzer runs
  once. No private identity, native-export/host/TCP completion, gzip integrity or
  cause follows from this match. Primary review `ad0944cb` independently verifies
  both arms' 48 HTTP cases/104 persistent-cache checks/160 supplemental checks,
  the current 825 native roles, 1,761 protected inputs and three app trees, with
  four binary payloads explicitly delegated rather than replayed. Its runtime
  state remains unaccepted. Finite raw-pair retention now holds 318 files
  (5,969,078 bytes); Root's first checker replay and an independent copy with
  actual staged Git permissions both pass. Neither reads original paths nor
  executes helpers/analyzers/targets; omitted payloads stay explicitly excluded.
  The native-boundary Source audit identifies an internal guest registration
  path and an ordinary `call` success site, while proving that direct WASI stdout
  inside canonical `post_call` is forbidden. Its separate proposal has no native
  patch or implemented API. Next are bounded internal-snapshot validation,
  ambiguity/clearing and ordinary-call I/O policy before any new native build.
  Persistent-cache overlap/error/bounds, broader lifecycle coverage, bootstrap,
  empirical cost measurements and production promotion remain outstanding.
- **Native export diagnostic implementation in progress:** the preceding goal
  turn made concrete progress through the real public-correlation pair, three
  DATA reviews, current/Git-permission offline checks, and pushed checkpoint
  `ec3c2020`. This turn adds separate opt-in native and guest candidates using
  the inspected builtin registration and ordinary native `call` site. Native
  Source `6ed5a7ce` uses primitive-only observations, owned fixed bytes, saturated
  ambiguity, bounded stdout and memory-only retirement in `post_call`. It adds
  no host service, WIT interface or core ABI export. Guest `5d20e455` adds one
  named internal import and one synchronous observation from the existing
  snapshot; all body/await/cleanup paths remain unchanged. Probe `2226ae28`
  declares 17 direct-WASI cases with no actual engine/INIT/runtime result yet.
  Source peers pass these candidates and the unbound portable build recipes.
  The first macro-OFF/ON frontend pair fails before reaching the candidate:
  the SDK lacks two empty generic libc++ directories required by LLVM version
  discovery. A full audit hashes all 10,114 SDK files (366,304,928 bytes), finds
  no changed/extra payloads and only those missing directories, then restores
  their authenticated paths/modes with explicit new physical identities. The
  failed outputs remain intact. Fresh V2 frontend checks pass raw0/clean with
  warnings-as-errors in both OFF/ON modes, using the same C++ candidate and
  original compiler vector. This proves frontend compilation only. Full engine
  build, native callback/INIT cases, emitted-import inspection and the next full
  Next.js regression remain outstanding; the strict browser failure is unfixed.
- **Fresh diagnostic source materialization complete:** pushed Source checkpoint
  `97090420` retains the native/guest/probe recipes and both frontend outcomes.
  The real materializer now exits0 and produces 825 files (435 native, 387 build
  support, three embedding), 7,562,493 bytes, with role-content hash `46e78a51`.
  Only the embedding C++ and its CMake file differ from the preceding source set.
  Independent DATA review `19fd3f9f` verifies the actual copies and descriptors;
  Root prepares a genuine new portable selection `f5d37ea0` through the existing
  admission mechanism. The generator recipe `fa8be735` binds these actual
  materialization results and passes independent Source review; its ten unchanged
  checks now finish raw0 (`08479bfe`), with all ten commands passing and the
  runner reporting preserved source/tool inputs. Independent DATA review
  `fbb5db08` verifies all ten commands and their owners, recorded source
  preservation and finite raw streams; current source/tool payload rehashes are
  explicitly delegated to the real admission checks. The real builder
  preparation exits0, creating fresh Cargo selection `98c52b61` and an unissued
  build draft `4937da3c`. Its preparer and launcher pass whole Source review;
  only the two actual draft/receipt SHA bindings change in the launcher. The
  full native build now finishes raw0/clean, producing engine`237c4e5a` and
  metadata`500e76ac`. Coordinated review`7e5311ad` binds Source/link
  review`b473d4c9`: all six phases and seven owners pass, with 1,950 protected
  descriptors and exact private embedding ON evidence. The 825 Source pairs,
  80+1 compile commands and Rust/link inputs are checked; the current complete
  ten-tree payload sweep is delegated to the actual worker/Root guards.
  No engine execution, component or runtime acceptance follows from this build.
  The frontend retained corpus contains
  52 files/4,009,463 bytes; Root's first offline reader exits0, preserving raw
  frontend codes `[1,1,0,0]`, separate driver0 and unaccepted runtime status.
  A separate replay from actual staged Git blobs and permissions also exits0.
  Both read copied DATA only; full SDK and engine payload replay is excluded.
- **Diagnostic component construction complete; deployed cases pending:** Root
  `39caa5`/session91297 completes `7a089a` raw0 under original50481/2,400 seconds.
  Component`d04c4289`, actual audit`3a7a2d1d` and coordinated review`163eb782`
  bind owner/world review`29ede10c`, the full 52-field metadata object and
  genuine build`7e5311ad`. All four owners and eight complete INIT streams pass;
  native/guest/probe markers are absent. Native module resolution and the
  static INIT call do not establish the return flag or active-window behavior;
  the first `/none` response and the fixed seventeen-case deployment will check
  those next. Runtime Source`72eb6fe4` and controller`e4648223` have Source and
  binding review; Root's genuine runtime authority preparation exits0 as
  `9cab7f05`, with no target invoked yet. The preparation-only portable corpus
  contains 115 copies/6,123,766 bytes; Root's first offline check`fc2462` exits0,
  preserving ten generator outcomes and recorded 825-file evidence while
  excluding current Source/tool payload replay and runtime/build acceptance.
- **Seventeen runtime cases collected and passed; review pending:** Root
  `387858`/session46077 finishes`56cea8` raw0 under original53995/1,800 seconds.
  Driver result`f085c120` reports all seventeen cases passed, no unattempted
  suffix, complete stdout and final native/Source/world protection. Independent
  semantic intake checks all sixteen native frames: two single-valid, twelve
  unavailable and two ambiguous. Every response reports the snapshot return
  flag true, undefined observation returns and untouched conversion hooks.
  `/none` has zero native records in complete capture under its declared100ms
  bound; this does not prove native export completion. The concatenation case
  reports nonlinear-string; no representation or forced-GC claim follows.
  The 512-KiB allocation case retains the expected copied fixture bytes.
  Next constructor `fe446b`/session53324 separately finishes`1ab962` raw0 under
  original54388/2,400 seconds, producing component`6b2084d0` and audit`089139f8`.
  It validates the same thirteen WASI0.2.10 interfaces/incoming-only export;
  independent construction review and the full Next.js pair remain open.
- **Diagnostic runtime and new Next INIT reviews complete:** coordinated
  runtime review`91e961ab` accepts all seventeen declared probe cases and joins
  owner/capture review`77fbda3f`: eighteen clean original owners, seventeen
  distinct owned Wasmtime children and seventeen complete captures. Raw stdout
  is 3,760 bytes, direct stderr680 bytes and HTTP bodies6,424 bytes. This remains
  a diagnostic subset, with no full Next acceptance. New Next INIT review
  `5c284564` joins owner/world review`8890980b`, verifies all four clean owners,
  eight marker-free INIT streams, complete 52-field metadata, 131 observed
  imports/13 interfaces and 1,678 freshly derived Source evidence descriptors.
  The four public values for one fixed native→Node pair are declared in
  `public-correlation-declaration.json` (`c0e32a24`) before either arm. Each
  unchanged actor derives its actual origin after its port0 listener is ready.
  Fresh Source/protection assembly and the full pair are next; no earlier
  failure or production gate is waived.
- **Full pair prepared, no arm launched yet:** Source-only binder`6ef473` /
  session21318 exits0 (`a664ef`) and creates native actor index`39cd3c7c` from
  the actual new component/constructor/build evidence. It derives 1,650 current
  Source/target descriptors, 1,771 protected inputs and actual metadata/build/
  Source lengths52/35/1678; no predecessor array is retargeted. Root's
  `ec72c4`/session63690 preparation exits0 (`a6d38c`) and validates both fixed
  arms before writing either runtime grant. Native run`native-export-237c-first`
  and Node run`native-export-stock-22-first` retain the original600/300-second
  owners under the1,200-second pair owner, every original gate and complete
  native stdout capture. The next action is the single declared comparison.
- **Full comparison completed; native original suite remains failed:** Root
  `8e99b1`/session39004 finishes`eed692` raw0 under original57938/1,200 seconds.
  Native owner exits1 with valid complete evidence; Node owner exits0 and passes
  the original full suite. Native passes HTTP24, persistent-cache52,
  supplemental80, five stream chunks, both functional browser tests and both
  strict browser tests. POST7 body/finished/sizes fulfill before context close,
  with no browser errors or failed requests. Legacy generation remains1→1;
  Node observes1→2. All earlier strict failures remain retained and unfixed.
  Final native stdout is19,019 bytes with complete EOF/write/close/bound flags,
  six native site records and54 V2 records. Root's first33-input DATA analysis
  `357de5` exits0 as`af787ee6`: public POST metadata joins across browser,
  same-local NetLog, guest adapter/classic entries and exactly one valid native
  success-site observation. One strictly certified missing POST remains
  separate; GET observations never substitute for POST. Seventeen pure native
  join decisions also pass. This observes the named pre-return site, not C return,
  canonical post-return, host/TCP completion, private identity or cause.
  Independent pair/correlation reviews and portable raw-pair retention are next.
- **Complete:** guarded native build, real-Next component construction, and one
  full deployed regression. HTTP/stream/browser checks pass in that sample;
  cache1→1 keeps the full suite failed. Prior browser failures remain unresolved.
- **Complete for its bounded contract:** the deployed two-case guard test passes
  builtin import and coded file-URL refusal with independent DATA review. This
  is an explicit compatibility gap against the successful pinned Node reference.
- **Complete for the declared subset:** the bounded CJS/fileURL bridge. Its first native build failed
  a SpiderMonkey handle signature check. A separate correction passes frontend,
  generators and full compile/link. Coordinated full-build DATA reviewb9aad169
  passes. The16-case deployed Wasm probe now passes in one GET, raw0/clean,
  with native/world guards preserved; bounded runtime DATA review030fad8b passes.
  The initial optional cache facade retains its40 in-memory model checks only.
  Separate HandlerV2 real-storage and Next/WASI results are recorded below;
  they do not promote that earlier prototype.
- **Complete:** corrected StockV2 VM import seam and owned cache-parent setup;
  real Node seam0 and one fresh full control0 pass. The first Wasm cache scenario
  passes; its legacy counter and strict browser failures remain open.
- **Complete:** the successful StockV2 control and real VM seam now have a closed
  portable DATA archive and standalone reader. Offline/current checks pass for
  137 retained originals, including two screenshots; Root independently compared
  every archived member with the current original. The omitted application and
  tool payloads are not reproduced by this archive.
- **Completed build/public subset; wider lifecycle open:** bounded native Web fetch resource ownership cleanup. Source audit
  identifies missing disposal paths. Six-file afterimages and pure ownership
  models are sealed after independent review. The actual frontend checks now
  pass two translation units and fail the third on three ignored nodiscard
  results. A separate18-byte source correction now passes all three frontend
  checks, raw0 with clean ownership and unchanged guards; independent DATA
  reviewe5712a58 passes for that frontend-only scope. The full native build now
  exits0; coordinated build DATA review41857258 passes. The new engine's
  sixteen module interoperability cases pass in a deployed component
  (review55a255e7). All eight public Fetch lifecycle groups now pass in one
  actual Node/Wasm comparison. The fresh full Next.js run retains the same
  two failed gates; coordinated DATA reviewc3a8b95b verifies the failed outcome.
  Review caught an interaction with the existing
  native append path, now explicitly excluded from this bounded change.
  No cause for browser abort or module-state differences is established.
  Target-host checks and measurements remain separate.
- **Still open:** broader lifecycle/resource coverage, clean-machine bootstrap,
  performance/size evaluation and any production promotion. Foundations-v13 remains
  the accepted checkpoint. Reviewed build, lifecycle and failed Next snapshots
  through1b06d3c2 are committed and pushed. The next gzip-composition probe is
  pushed as Source in9060b4ef; its new INIT and deployed public profile now pass.
  Current action-wire control results also pass. The new NetLog pair completes
  with native raw1/stock raw0; coordinated DATA reviewf3d7a9ab preserves the two
  failed gates. Closed DATA, offline readers, current wasmCloud results and
  documentation are committed and pushed to origin/main in1756de82.
  Current wasmCloud SourceV5 is sealed01a939fa after whole
  Source and closure review. After a separately preserved Python-alias preparation
  failure, corrected Root admission succeeds and the actual cold8 exits0 with
  all eight requests passing. Coordinated result review0ed0e4c2 passes that scope.

The corrected2251/afb build is accepted as build DATA only. A separately sealed
[interop constructorV2](tests/node-compat/frameworks/nextjs/next-module-fileurl-interop-probe-construction-v2/README.md)
selects the unchanged16-case guest contract with the corrected RootedString
native source. Root preparation00a2d33d binds31 actual metadata fields,39 fresh
build roles and12 Source roles. Construction now finishes Root78265/original
77890/2400 raw0/clean, all three inner commands0, protected inputs/world unchanged.
Component08ce7388 is37,153,403 bytes and emits exactly13 standard0.2.10 imports;
coordinated construction DATA review98fc2b09 passes. RuntimeSourcecf205656 and
fresh authorityf2085bc9 then run Root87569/original80224/180 raw0/clean: one
GET200/7152 bytes contains all16 ordered passing cases, result4c919dbf and
response5ebcea5a. All1739 protected inputs and complete world/native guards
match before/final. This validates the selected default-only CJS/fileURL
contract and explicit refusals; it does not establish full Node/Next parity.
Independent bounded runtime DATA review030fad8b passes. New real-Next
constructorSource344d6d5f keeps73b/1e49 unchanged and requires that actual16-case
proof. Root preparation6d8e20d4 enforces it and protects it as the13th Source
role. Construction finishes Root97759/original82335/2400 raw0/clean, all three
inner commands0. Component4e6582ee is37,235,395 bytes, resultca4b8e81, exactly13
standard0.2.10 imports; coordinated construction DATA review7381338c passes.
HandlerV2 c5210cc5 is sealed after72 explicit fake-model checks and Source
semantics/closure review. Catalogue8a2cce89 completes31 files/24 directories,
28 parent files unchanged; thin builder022d823b changes only its catalogue path.
Root19036 then builds the genuine standalone app once: four owned phases0/clean,
resultabdca858/inventoryf8058b47,2,186 files/427 directories/48,755,844 bytes.
Next traces exactc1013ea6 handler and real FileSystemCache delegate; generated
config uses ../cache-handler.cjs/maxMemory0. BuildIDuj_9wJGt4Jh1d8BV6oSsU and
action4018730ebe8dc9bc100be933e21dabdfa132c639ab are fresh actual values.
App-build DATA review163133f1 passes (authorship-only successor to retained3641).
Native full trial Root73058/original87752/600 now finishes raw1/clean/protected:
five nonce requests/52 checks,24HTTP,80supplemental and five-chunk stream pass;
two functional browser checks pass. Legacygeneration1→1 and strict Server Action
ERR_ABORTED/three body/finished/sizes errors remain failed. Native result06ce2d99,
client65bee544 and independent DATA reviews969e99fa/b860b1f2 retain those outcomes.
Stock control Root78336/original88210/300 also finishes raw1/clean/protected:
allfive500,23 baseHTTP observed/one assetpass, action/cachecompare/stream/browser
unobserved. Result266d62ef/review5e709e41 identify the host compatibility loader's
ERR_VM_DYNAMIC_IMPORT_CALLBACK_MISSING; no Node parity acceptance follows.
Separate StockV2 Sourcedf257054 then passes real Node VM seam original91470/120,
resultb75a4064/review0ac120ab: olderrorreproduced, actualdefaultCJSclass/identity/
construction verified, experimentalwarning preserved with noflags. Fresh control
Root81654/original92341/300 finishes0/clean/protected, resultede853eb andreview
d739eacc: five52/24HTTP/80supp/legacy1→2/stream/strict2browser allpass in one sample.
Comparison991c9b93 preserves unavailable native body andseparateclocks/nocause.
BothfailedV1recordsremainfailed; no fullWasm/Node parity orreliability acceptance.
Native Source ownership audit finds finite Web fetch body/future disposal gaps,
with sealed read-based terminalcleanup afterimages and98 pure models before builds;
generic metadataGC/append/error-resource/clone/abort scopes remain explicit.
See [first cache profile results](docs/node-compat/nextjs-portable-cache-2026-11-07.md).
The older
failed25c constructor remains unchanged and unexecuted. The current volume has
about14GiB free, so storage is no longer blocking this step. Fresh Mat5
materialization now completes raw0:825 files/7,554,682 bytes, six changed and819
byte-identical, independently checked against the old payloads and donors.
New selectiona6b9e291 is genuinely admitted; Builder7 JSON-only Cargo preparation
completes raw0 with original inputs preserved. No Cargo command ran during that
JSON preparation. The first frontend harness attempt stopped before Popen on a
missing monitor directory; its inputs and result remain preserved. A separately
reviewed driver correction then runs three original180-second compiler owners,
raw[0,0,1], clean groups and source/tool/failure guards unchanged. The third TU
fails three nodiscard warnings treated as errors, not a host or ownership failure.
Separate sealed cleanup SourceV2 explicitly discards those known-success booleans.
Fresh Mat6 has825files/7,554,700 bytes, exactly one+18B replacement and824
unchanged payloads; new selection0abc4eb4 is genuinely admitted. Corrected
frontendV3 Rootf16b04/original7348,7371,7382/180 completes0/0/0, clean ownership
and source/tool/failed-V2 guards unchanged; independent DATA reviewe5712a58 passes.
GeneratorV6 on this corrected selection also passes all ten checks under
original7942/900, result2ddbfa9e and independent owner/raw DATA reviewb420245f.
Builder8 JSON-only preparation DATA review2f2d5f57 passes. Full native build
admission103ac6dd passes; Root9eab2f/original11018/7200 now exits0 in fresh
`next-native-intl-build-fetch-cleanup825-first`. All six inner/outer phases
return0 with clean groups; result ece47f14 reports1,931 protected inputs and ten
tool trees unchanged. Candidate engine476b1c1d is31,347,353 bytes and metadata
22f1d456 is4,859,179 bytes. Coordinated terminal DATA review41857258 passes,
binding independent owner54d1e14d and source/compiler/linkd0cbd1cf lanes. No
engine/guest export has run. Fresh components and public guest tests follow
a successful reviewed build. A new unchanged16-case interop constructor
selector896379c0 is sealed; its concrete Root authority600289c7 is prepared
with31 fresh metadata values,39 build roles and17 protected Source roles,
passes action-admission reviewf852e3ff. Rootb40054/original32323/2400 then
constructs, validates and emits WIT raw0/clean, with all three inner commands0.
Componenta65097fd is37,159,178 bytes, result0d535aa1; its observed complete
return has131 function tuples and its WIT emits the selected13standard0.2.10
interfaces/onlyincominghandler. Coordinated construction DATA review8ed98322
passes, joining independent typed/package and owner/world6b19ad6e lanes. A
schema-only successor44c37d97 adds the existing collector's truthful
`deployedImportOrFilesystemProbeInvoked:false` field; the original review and
all facts remain unchanged. No
ordinary probe was accepted from that INIT review. A separately reviewed runtime
authorityb10d2c84/3eb5bc8e then runs Root9edf23/original35819/180 raw0/clean with
full native/world guards unchanged: GET200/7,152 bytes, all16 cases pass,
result663a47b1/response5ebcea5a. Coordinated runtime DATA review55a255e7 passes,
joining outcome and ownership/current-roleef9d3608 lanes. No Fetch cleanup or
full Next result is inferred. A separate lifecycle constructorb0d54ea2 and
authority08fff56b/3f27a0cd then run Rootbb5143/original36952/2400 raw0/clean,
all three inner commands0, component e0bb7bc6/37,148,543 bytes and result59562d8c.
The actual return contains131 tuples; coordinated lifecycle INIT DATA
review4b3b0f43 passes with complementary owner/world review130d3a39. Runtime
Source41ad0bd9 is sealed. JSON-only Root preparatione1517c produces
authoritydf18f1d8 with1,743 protected descriptors and three phase grants.
Root4bbfd8/original40184/600 then exits0/clean/protected, result9f043eeb:
eight public groups pass against the independent Node reference, using the same
live control server. Twelve raw DATA copies (46,035 bytes) are retained with an
offline verification command; this does not establish resource counts. Fresh
real-Next preparation2d54ff/e7371c66 binds31/39/18 actual roles, including the
new55a interop prerequisite. Root2b08c0/original40615/2400 constructs, validates
and emits WIT raw0/clean: componentd990ecc1/37,241,086 bytes, resultc1bd0e4d;
actual131 returned tuples and thirteen standard0.2.10 interfaces. Its complete
INIT DATA review9256cdd5 passes with owner/world reviewe249469a. Full runtime
Source7b719ac1/plan8d2251a8 preserves all six operational files, but its changed
outputPrefix conflicts with the unchanged client's literal contract. Root
preparation5007ea/authority4853261d protects1,781 descriptors; first launch
80f2c2/original42322/600 exits1/clean/protected, resultabe0e953. Wasmtime42341
stops normally0; client42361 exits1 before its first declared HTTP request
(stderr c6a6cb6e/1,072 bytes), with no client result. Thus all application gates
are unobserved in this attempt; no new runtime compatibility finding follows.
The original failed Source, outputs and guards remain unchanged. A separate
V2 plan will restore the original output prefix while preserving every client
assertion and using a fresh runId/output. No component rebuild is needed.
That separate correction is now executed: Source16d093e7/plancf7f39ec keeps all
six operational files unchanged and adds a narrow literal-path regression
check. Root preparationcec1b4/authority98a39cc9 derives the same1,781 fresh
roles. Root6b9eb7/original43391/600 finishes raw1/clean/protected, result2fb8d5fd
and client55d29476. Five requests/52 persistent-cache checks,24 HTTP cases,
80 supplemental checks, five stream chunks and both functional browser tests
pass. Legacygeneration1→1 and strict POST7 body/finished/sizes ERR_ABORTED errors
persist; page/console/client transport errors remain empty. Owner/current-role
review31017ce2 passes its scope; coordinated outcome reviewc3a8b95b independently
verifies the failed trial. Lifecycle review705270ee separately accepts its
eight public groups and binds owner37ab2610; no native resource count or full
Next acceptance follows from either review.
All62 client files (including2screenshots) plus7Root/world records are retained
as69 raw payloads/1,555,648 bytes with manifest0e0a8e28. Root033101 independently
compares all69 copies to their originals; the standalone offline checker passes
3a9b94 and preserves both expected failures. Its first unsealed reader field
error is recorded separately and does not alter runtime DATA. The new cleanup
has not resolved either application gap. Next work audits request/module state
and Server Action response consumption before adding more native APIs.
The [client Source audit](docs/node-compat/nextjs-server-action-next-steps.md)
finds no POST AbortSignal or explicit response cancellation in the inspected
production action chain. Flight root/UI resolution may precede response EOF;
this does not identify the abort cause. It also refines version reporting:
React19.3.1 is the installed dependency, while actual captured shared browser
assets contain Next-vendored19.3.0-canary-278794d7-20261002 (Roota6c81d confirms).
The [response-path audit](docs/node-compat/nextjs-response-completion-next-steps.md)
separates the outer JS WASI adapter from native Fetch body owners. A proposed
normal-input gzip-tail/backpressure probe is now sealed as uncompiled Source92aa205a:
15 payloads/103,900 bytes,34 Python Source/artificial-DATA checks, no Node or
guest execution. It retains the V5 adapter and existing hosting API, compares
53-byte/2-MiB generated responses to an independent Node gzip reference, and
requires observed write(false)/drain to claim backpressure coverage. The future
host argument contract explicitly requires standard --no-logging-prefix for
public markers. Constructor/controller/grants, real imports and runtime results
remain outstanding; README's no-index statement describes its preseal draft.
A separate current-cohort action-wire control is also being prepared to isolate
HTTP/gzip EOF without browser navigation. No extra native patch or runtime
acceptance follows from either preparation.
The gzip probe subsequently constructs successfully: selector875ce909,
Root676066/original49983/2400 raw0/clean, all three inner commands0,
result98ca3f7c/component1b4feb75/37,260,529 bytes. INIT DATA reviewab6a0c61
audits its actual131 imports/134 identities, unchanged standard13 world and
complete current31/39/17 roles. No Node-reference codec or deployed gzip case
has run; the new runtime controller/grants are still being prepared. Current
action-wire Source is also sealed (common596792c5, native2e33f8de,
prepared-Node2c95a071), preserving original prefixes/CRC/framing gates and the
captured391-byte POST. Concrete grants and both actual transport runs remain
outstanding. These Source/preparation results do not change the failed full
Next baseline.
Those controls have now executed once. Native wire Root9da74a/original52331/600
and prepared Node Root04097a/original52580/300 both exit0/clean/protected, after
explicit native-clean/protected sequencing. Native transportee6c24ad and Node
transport8b4b2161 retain complete HTTP messages/single gzip/CRC/ISIZE and2,963
decoded bytes each; bytes/CRCs differ and Flight is opaque. DATA review52fa402d
binds independent owner/wireb6d0e86a. The33-file/671,933-byte raw corpus is
retained (manifest9f5c3b56); its standalone Python check passes67cb66.
Gzip runtime Root0c9d20/original53251/600 also exits0/clean/protected with both
180-second phase owners0. Resultc98f5472 and validation24c188d8 show exact53-byte
and2-MiB plaintext/CRC/EOF against independent Node; actual large guest compressed
bytes2,097,810 versus Node2,097,815. Public response write(false)/drain/pause/resume
are each16, input-write(false)32. Coordinated DATA review86220bbe binds owner/
world/public-log11c365a3. A39-file/6,350,276-byte raw corpus (manifest11d9a1b9)
and offline Python checker pass7d6a43 without Node/guest/network invocation;
only a clearly derived temporary descriptor-path view is made for the held
DATA verifier. No retained originals change. Both controls preserve the failed
full Next/capture baseline and establish no native resource count or cause.
See [current completion controls](docs/node-compat/nextjs-completion-controls-2026-11-08.md).
The next diagnostic uses one shared strict browser worker with only standard
Chrome NetLog startup capture, a16-MiB circular target/20-MiB final read cap,
default capture mode and unchanged interactions/assertions/deadlines. Its Source
is under ordered sealing at that preparation cutoff. The subsequently sealed
sharedc7be23d9, nativee697c715 and stockdb0b4eb3 then execute in one fresh pair.
Root64c124/original57224/600 terminates raw1/clean; Root8ab627/original57521/300
terminates raw0/clean. Native result91880401 preserves legacy1→1 and the three
strict POST7 abort failures; prepared Node result723cc5c6 passes all declared
gates. Both pass5/52 persistent-cache,6/80 supplemental,24 HTTP,5 stream and2
functional browser checks. Coordinated DATA reviewf3d7a9ab binds independent
browser/NetLog reviewa3707d8c and current native/world/app-copy evidence.
The3,331-event native and3,413-event Node NetLogs each have one exact-origin
POST/actions candidate and no explicit negative net error in the selected
request/one-hop context. Empty end-record parameters prove neither EOF nor
cause; public browser/CDP abort remains failed. An initial native DATA analysis
used the wrong origin; both it and the explicit corrected-origin report are
preserved, with no target rerun. See the
[NetLog result record](tests/node-compat/frameworks/nextjs/next-browser-netlog-root-results-v1/README.md).
Its92-file/5,601,728-byte raw corpus is retained (manifest056dabc2). The original
copy-mode checker passes Rootb124d3. A separate portable reader4d595df6 preserves
that checker/manifest while treating historical permissions as DATA, because Git
does not preserve them; temporary0644/0755 checkout checks pass and Root4b5360
also passes the current-copy reader. No actor runs and no original absolute path
is read.
The next executable portability check is current D990/f805 stock wasmCloud
cold8. SourceV5 index01a939fa seals13 unchanged payloads/85,462 bytes after C's
whole Source and closure reviews. Root full-native/world admission is being
implemented separately at that cutoff. The first JSON preparationfaa419 fails
before guard loading/authority/actor because Homebrew reports an executable
alias. Original RootV5 sources and1032-byte traceback are preserved. A separate
RootV6 resolves that path before the same binary pin check; its sole+10B wrapper
change passes narrow Source review. Preparation91b952/f1de29 issues actual
authorityc4075e8b with1784 protected descriptors and31/39/18+825pairs.
Rootfeb2db/original61905/600 then exits0/clean/protected, result efac2d2a:
eight status200 responses pass, including three streamed chunks with shell0
and ready1. Config inspection and normal SIGINT shutdown both exit0. Coordinated
DATA review0ed0e4c2 binds independent owner/config/response review6dbf5c9a.
The45-file/749,774-byte raw corpus is closed (manifestd0fd9e03), including all
eight bodies/chunk records. Portable checker e22e91ae passes a Git-style copy
and Rooteef354 current copy without original-path/actor/network operations.
Its physical app modes do not imply readonly WASI
descriptor rights; explicit empty allowedHosts denies outgoing HTTP; pinned
P2 hosting creates a new Store per request. These source limits and future
exact-origin egress selection are recorded in the
[host audit](docs/node-compat/nextjs-wasmcloud-mount-egress-source-note.md).
Next is a matched browser `Accept-Encoding: identity` diagnostic, preserving
all strict gates and explicitly verifying request negotiation/absent response
Content-Encoding. It changes outer response coding only; pinned Next strips
that header before internal self-fetch. Source preparation is underway, with
no actor/grant/result at that preparation cutoff. Sealed Sourcece4f5538,
native880a19a8 and stockc20a85c3 subsequently pass whole Source/closure review.
Preparationf50436 issues protocol314b4566/nativeb4e62057/stock81eca687.
Root439c49/original65026/600 terminates raw1/clean/protected; Root7957e5
verifies that boundary before StockRoot9bba39/original65237/300 terminates0.
Native resulte0deb8d2 and Node result0e560a52 both pass explicit NetLog identity
send-header/absent Content-Encoding negotiation. Native still has legacy1→1
and all three strict POST7 ERR_ABORTED errors; Node passes every declared gate.
All52/80/24/stream5/functional2 groups pass in both samples. Coordinated DATA
review8151dc47 binds independent browser/NetLog/owner review27751124.
Its90-file/5,625,171-byte raw corpus is closed (manifeste9dba92c); portable
checker1a4f1ae6 passes a Git-style copy and Rootf7d17f current copy without
original-path/JS/actor/network execution. This checkpoint is committed and pushed
to origin/main in96304c24. Context-wide negotiation changes assets and
timing too; no unique cause or inner-fetch/append/EOF proof follows. See the
[identity diagnostic](tests/node-compat/frameworks/nextjs/next-browser-identity-root-results-v1/README.md).
The next Source-only diagnostic is bounded deployed guest completion markers at
existing adapter/public-response boundaries. It adds no reader/fetch wrapper,
new host capability or INIT I/O; native Source remains unchanged. Correlation
between separate request objects must stay explicit/qualified, and no error
listener may mask an otherwise unhandled EventEmitter error. No trace component
or runtime result exists yet.
The first guest entry/marker-contract cores now pass Root/C Source review
(bf44a61c/f2fbb92f). Twelve explicit edits reconstruct the exact1e49 parent;
the helper has no INIT I/O and adds no await/body reader/error listener/native
change. GET/POST/actions and GET/action-result are the selected existing routes.
Markers distinguish read EOF, disposal/finish return, post-finally cleanup and
the original normal-return site. These are local observations, not Promise,
transport or resource completion. Metadata/constructor templates are being
prepared; no trace component or runtime has executed.
That preparation now has held entry Source8043008f and constructor Source5ffcf4d1
after whole Source and ordered binding/closure review. Rootfb2dc1 independently
verifies only the three typed Root pins changed. Preparationd130a8 issues
authority6de134d3 with current31/39/18 roles; Rootde31fc/original69034/2400 then
terminates0/clean (749568), all three inner commands0. Result3c5fa94b records
componentc6ae13b9/37,253,260 bytes and audit01607fe7. INIT stdout is one858-byte
capture record with no logger markers and empty stderr. Independent typed/package
review observes131 actual import tuples/134 graph IDs and the same13 standard
interfaces; coordinated INIT DATA review `ee7511ac` binds owner/world review `ed6c19e0`
and passes the declared INIT scope. No deployed trace
or runtime acceptance follows. The separate parent stdout-capture audit finds
the old direct-FD/readiness-size check is not a lifetime bound: the next runtime
controller needs a bounded prewrite pipe, explicit incomplete-prefix failure on
overflow, pipe-EOF/write/sync/close settlement and complete-line readiness checks.
The new INIT corpus closes97 files/639,455 bytes (manifest018f814a); its portable
checker2f8f3694 passes Git-style modes and Root0e1eed current copy, preserving
typed-return/owner/options/WIT/marker-absence evidence without original paths,
JavaScript, Node, guards or Wasm execution. Omitted package/binary/native payloads
are not reproduced by replay.
The [capture plan](docs/node-compat/nextjs-guest-completion-capture-plan.md)
records actual files/symbols and the proposed boundary. Root's finite Node22
capture-helper tests d7b91a now pass all nine cases, including exact8MiB,
whole-chunk refusal, live-pipe EOF, partial writes and sync/close/abort failures.
Independent DATA reviewb68296a6 verifies real file bytes and retained report8887349d;
orchestration failure handling remains Source-only. No Wasm/Wasmtime/network
was invoked by those tests. The full runtime13-payload Source and fresh Root
binder pass whole Source and mechanical closure (indexbf552c58/c828 wrapper).
Preparation647582/ad6beb issues authorityff6dbe1b/1,787 protected refs; Root99a366
and original74838/600 then terminate1/clean/protected (a1f83c). Native full
result62cff4ff retains the same two failed gates: legacy1→1 and three strict
POST7 ERR_ABORTED errors;52/80/24/stream5/functional2 pass. Wasmtime74870 exits0
on normal SIGINT; stdoutba199ca0 is completely captured13,296 bytes/52 parent
chunks under the8-MiB bound, with EOF/write/sync/close/bookends and no capture
error/overflow. Coordinated DATA reviewd0085b5c binds B2a05a418/Rc2f37726.
The54 marker records positively observe six each adapter terminal sites and
classic enter/finish/close; none reports catch/logger-error/truncation. Resets
and token collisions prevent private/cross-lane/outer-inner identity joins;
these are recorded Source-site observations, not Promise/export/host completion
or a cause. The60-file/3,266,120-byte raw corpus closes(manifestf3fc1168), with
portable reader170ea6fb passing B's current/Git-style checks and Root2a3e64.
The reader does not reinterpret markers or reproduce omitted app/tool/native
payloads. See [actual trace results](tests/node-compat/frameworks/nextjs/next-guest-completion-runtime-root-results-v1/README.md).
The [export/Promise audit](docs/node-compat/nextjs-export-promise-completion-audit.md)
finds no Source defect: compiled embedding requires a fulfilled lowered Promise
after the event loop, with later post_call/host-task boundaries unobserved.
Next Source-only entry work observes the exact handler.handle Promise adoption
with one explicit diagnostic await, preserving value/rejection while declaring
scheduling perturbation. Its first two cores50a4736a/cce84ff2 pass Root/C Source
review: nine exact replacements, an internal per-call holder and separate
post-ownership rejection handling. The existing async return already adopts the
child Promise; this is an observation/scheduling intervention, not a missing-await
fix. Whole-family review now passes and entry indexd7fbc202 seals the unchanged
seven payloads/91,333 bytes. The constructor is being bound to that genuine
index; no new component/runtime exists for it yet. Its three generic executable
files retain the preceding constructor's exact bytes. Runtime capture will reuse
the reviewed helper and full application gates. All completed trace/audit/raw
results through3988e1e9 are committed and pushed; this new work remains pending
the next checkpoint.
Ordered binding/closure review now passes for callerc0cf231a and plan8f56ab94.
Root5e30ae independently reverses the three Root pins to exact reviewed source;
preparationf9e2e4 exits0 and issues authority9ba322b2 with current31/39/18 roles.
Root4ace77/session3014 starts original79742/2400 for fresh INIT construction and
terminates0/clean (4ac9d2); all three inner commands return0, with unchanged
world/input guards. Rootea87ed reads resultab13bb42 and new componentcd60c673,
37,260,823 bytes; audit21e8ad86 emits the same13 standard interfaces. INIT
stdout is906 bytes and stderr is empty. Coordinated whole-return/import/INIT
review0013502c now passes, binding B owner/world reviewd65be4be (actual11 outer
observations and2/1/1 inner observations, not inherited counts). All eight INIT
streams contain no new marker. C freshly hashes the whole component, typed graph,
current package and metadata; existing engine/Node payloads delegate to the
accepted build and actual constructor guards. Deployed child-Promise markers
remain unobserved. Source-only runtime binding is the next step.
The new INIT retained corpus closes69 payloads/619,676 bytes (manifest55e97332).
B's current/Git-style checks and Root40d8f7 pass the offline readerd592d8cc;
it verifies retained owner/options/WIT/INIT joins without original paths or
execution and does not reproduce omitted binary/package/native payloads.
The reviewed entry and construction checkpoint is committed and pushed in
a03974fb. The subsequent runtime Source, raw archives and offline checks are
included with this tracker.
Runtime Source1b728657 now seals13 payloads/126,000 bytes after whole Source and
actual-binding closure review; all six operational files remain byte-identical.
Roota573e6 reverses the sole wrapper binding to exact reviewed Source. Preparation
0dd8a9/session27304 terminates0 (11bfc9), issuing authority1113140e with1,787
fresh protected descriptors,825 source/target pairs and31/39/18 roles. Original
native/world guards pass and admission observes48,769,073,152 free bytes.
Root838c00/session64237 runs original81527/600 and terminates1/clean/protected
(47ed83). Result2ae87cb0 retains client1294c107: portable52/supplemental80/HTTP24/
stream5 and both strict browser tests pass, while legacy1→1 fails. Root270208,
2d0c7d and2e88d3 read those actual gates; POST7 body/finished/sizes fulfill with
2,963 decoded bytes, and browser errors/failed requests are empty. Rootecb24a
reads final capture metadata before marker interpretation: stdout6fea20d1 is
completely retained14,762 bytes/62 parent chunks with EOF/write/close/bookends,
no overflow and no errors. Host81556 exits0 by normal SIGINT; client81572 exits1
naturally. Coordinated DATA review4d47759f now passes for these observed outcomes,
binding Bffc43a9b and Rc64c02ca. It verifies1787 current protected roles,825pairs,
31/39/18,35 closed families, both2,186-file app inventories and12 cache files;
6,733 finite current hashes and five explicit binary stat/delegation roles remain
qualified. The retained pure-Python analyzer f7fdd2f1 runs once after Source
review and complete capture, yielding eb5cc366:60 strict markers/5 ordinary lines,
six positive child fulfillment sites, no catch/rejection/logger-error/truncation.
Root0e0f5a independently counts these raw sites. Sequence/token collisions remain
descriptive, and the Source-local holder is not a physical/cross-lane identity.
Rootfbb3c8/3e31d9 reads review scope/joins/limitations. No enclosing export,
native loop/post_call, host task, TCP completion, cause or fix is proved. Added
await/logging can perturb scheduling; all earlier failed samples remain unchanged.
The runtime retained corpus now closes60 payloads/3,361,206 bytes (manifest6016cc6e),
including all14 browser files,21 outer records, complete stdout, the three reviews,
analyzer Source and full analysis. B's current/Git-style checks and Root5474a9
pass reader4fe15fe6; Rootec3966 reads its whole Source and portable six-input
analyzer command. The reader verifies retained owners/capture/strict positive
browser data and legacy failure without original paths or marker-code execution.
Historical modes/identities and omitted binary/app/package/native payloads remain
documentary. The marker analyzer can be explicitly replayed on the retained six
copied inputs. Two minimal await-only entry variants are now being authored for
the separately reviewed fixed comparison. Their shared Source family now seals
as55551d4b after Root/C whole-family and final mechanical review: seven payloads/
113,541 bytes, plan72ce4d40, B30b4644e/40,906 bytes and Dcffdccd0/45,374 bytes.
Each has exactly one six-byte `await ` insertion and otherwise reproduces its
parent byte-for-byte; D retains the parent response logger/schema. The historical
f2fb whole-entry/no-await wording is explicitly not adopted for D. Real world
fields and current build/cleanup/interop prerequisites remain. At that Source
seal the new constructor/component/count/runtime fields were NULL; actual
construction updates follow below. No trial in that comparison schedule has run.
The complete Promise trace/raw/checker checkpoint is committed and pushed in
5cc6e5ef; the working tree was clean at that cut. Subsequent work is now Source
implementation of the fixed comparison: two sole-real-next callers (Bplan8ce4c7cd,
Dplan234d4f3d) reuse the three generic executables and exact31/39/18 build
algorithm, with extra shared-family variant selection checks. Whole Source and
final closure reviews now pass: Bcallerbbbfcf69/Dcaller2b0e4f0d; Root9fb093
reverses each three-pin binding to the reviewed Source. Four runtime actor
scaffolds pass whole Source review and preserve the same six operational files.
A/C indices9736914f/98cfe869 seal their unchanged thirteen payloads. Following
genuine new INIT reviews, bound B/D actors now seal3a00ff3a/cd38d1dc with13
payloads/138,845 and139,209 bytes. Whole and final Source closure pass; six
operational files remain unchanged and all prospective trial grants are NULL.
Root Source plan5613cd96 (initial
cut1b7759ff, with only the proposal-status reference clarified) declares all ten unique
output/owner namespaces, eight native trials and two unchanged Stock controls,
with no replacements and all original gates required. No comparison action has
started; old A/D990 and C/c6ae components are reused without reconstruction.
B preparationb51cfc issues authorityf5ec0282; Root0599ba/session4525 runs
original86727/2400 and finishes0/clean/protected (60f407). Resulteb166eff records
component59a88505/37,239,252 bytes and auditf50d4939. D preparation870bb4 issues
authority72f16a56. A Root command typo412821 fails in the shell127 before the
interpreter/target starts; the separately recorded correction810cc7/session24188
runs original87057/2400 and finishes0/clean/protected (12a6ee). Resultad33478f
records componentdda80e61/37,253,073 bytes and auditc1f547e9. Each has all three
inner commands0. Root9a3bf3/902af4 reads actual results; current WIT audits retain
the same13 standard interfaces/incoming-handler-only export. No comparison
request has run and artifact size alone establishes no performance advantage.
Owner/world reviews9260319f/164cad43 pass with actual2/1/1/6 and2/1/1/29 owned
observations; all eight INIT streams per case lack markers. Joint primary
typed-return/import/package reviews b35640a9/94cbfa54 now pass. Each audits the
whole actual component,131 returned tuples/134 typed graph IDs/debugundefined,
standard13 surface and31/39/18 joins. The unchanged package4889files/21links/
424directories is hashed once jointly after both results; existing engine/Node
binary integrity is explicitly delegated to accepted build and actual guards.
Rootcb3f3a reads both scopes/provenance; D's shell-path error remains qualified
as a pre-target command error, not a failed or repeated INIT trial.
B/D INIT corpora now close63/598,982 bytes and88/640,973 bytes, with manifests
a680f3e8/6c52ece7 and readers0e491672/211c3401. Original monitors, typed-return
records, options, WIT and finite Source/review witnesses are retained; full binary,
metadata, package/SDK/app/native payloads remain omitted. Root92510a/93b639 reads
both readers and scope; independent offline runs f5cb64/ce7350 pass without
original paths or target execution, alongside R's current/Git-style checks.
The common Root ten-trial policy/preparer/controller now passes whole Source
review and ten pure policy tests. Review caught and corrected an aggregate
reporting edge: originalAllPassed requires raw0, the original observation's
acceptance and the producer's predicate; clean raw1 remains a recorded failure
that can continue the fixed schedule. Bound policyd2418e3c/39,927 bytes differs
only in six genuine descriptor bindings from reviewed675de2e6; Root9435b7
independently reverses them exactly. Original guards remain in their own contexts,
native argv remainslen2, Stock argvlen3, and no review fields are defaulted.
Root61cb76/session5760 preparation finishes0 (ce8432), validating all ten fresh
contexts before writing any authority. Cohort authority6643729c/14,011 bytes
binds the ten authorities, fixed order and whole driver Source; Rootb0f5fd reads
the concrete manifest. No comparison trial has started. Driver completion and
original test acceptance remain separate, with no retries/replacements/promotion.
Git's whitespace check notes an extra final blank line in the authenticated
Root policy. Its reviewed bytes are retained because all ten prepared authorities
pin that exact Source; other current Source whitespace checks pass.
Commit4ffa8659 is pushed to origin/main; live
build logs and the unfinished runtime controller were excluded from that cut.
GeneratorV5 runs all ten checks successfully under original4023/900, result795dab0e;
this is not compiler or runtime acceptance. Full build and public component
tests remain required. Prior
2251/4e build and runtime results do not validate the new cleanup candidate.

Execution resumed after the user freed the current volume. Native admission
observed 23,397,662,720 free bytes. Both first real request-regression arms have
now completed, and **both strict results fail**. Each records 80 passing checks
for the six concurrency/body/recovery cases, all 24 individual HTTP contracts,
five incremental stream chunks and two functional browser interactions. Native
cache generation remains 1→1 after revalidation (failed); stock Node advances
1→2 (passed). Both strict browser gates retain a Server Action POST
`ERR_ABORTED`, with unavailable response body/sizes. No failure was filtered or
retried. The closed reader accepts both supplemental captures as intact and
strictly passing for those six cases, then rejects whole-pair admission.
Independent DATA review verifies the physical outcomes and preserves both
failed original-contract gates. See [first real pair results](tests/node-compat/frameworks/nextjs/next-app-request-isolation-root-results-v1/first-real-pair-results/).

The first actual V3 full-build admission also failed before WORK creation or
compilation: the SDK was missing two empty archive-declared directories. All
other common SDK entries matched, and the other nine declared trees matched.
Root restored only those two mode0755 directories from their pinned archive
metadata, without changing payload files, Source or inventories. All ten tree
content checks now pass. The first failed attempt remains preserved. A fresh
[SDK-restored build](tests/node-compat/frameworks/nextjs/next-native-portable-build-sdk-restored-root-v1/README.md)
now completes with exit 0 under the unchanged d434 builder and original
7200-second owner. Independent coordinated review passes: all 825 copies match,
80 actual native TUs (79 C++/1 C) plus a separate embedding compile, fresh Rust
aggregate and 1,078 link inputs, and all protected inputs/ten tool trees remain
intact. New core engine `02a6601d…` is 31,324,563 bytes; actual full metadata
`9e960c41…` is 4,877,968 bytes. This accepts build DATA only. No ordinary engine
or guest export ran. The reviewed constructorV6 preserves all three existing
executables and changes only the plan for genuine full-build metadata and a
fresh namespace. Actual INIT construction, validation and WIT emission now all
finish exit0 with clean ownership and protected inputs. Independent DATA review
accepts component `4afeeb76…` (37,218,693 bytes), exactly13 selected standard
WASI0.2.10 imports and only incoming-handler export; no app was mounted at INIT
and no ordinary export or HTTP handler ran during construction.

The first application trial on that rebuilt component is now terminal, raw1
with clean ownership and protected inputs. It again passes all80 supplemental
checks,24HTTP checks, five incremental stream chunks and both functional browser
interactions. Cache generation remains1→1 and strict action-response capture
retains `ERR_ABORTED`/missing body and sizes. Independent physical DATA review
confirms these failures; the full rebuild did not resolve them. See the
[full-build runtime results](tests/node-compat/frameworks/nextjs/next-full-build-runtime-root-results-v1/).

The three predeclared matched-Node controls with only the additional diagnostic
CDP session disabled have also completed. Each passes24HTTP/cache1→2/five-chunk
stream/two strict browser interactions, raw0/clean/protected. Root called the
driver's genuine final audit through off3. These observations do not establish
an abort cause or accept any earlier failed cohort. A separately versioned
native control has now completed on the same component, app, world and strict
gates. It exits1/clean/protected:80 supplemental/24HTTP/stream/two browser
functions pass, while cache1→1 and the action POST `ERR_ABORTED` still fail.
Disabling the extra session is not a sufficient fix in that native sample.
See the [native control](tests/node-compat/frameworks/nextjs/next-native-extra-cdp-off-root-results-v1/README.md).
See the [completed Node control audit](tests/node-compat/frameworks/nextjs/extra-cdp-off-root-results-v1/completed-final-audit.json).

The roadmap remains incomplete: diagnose the cache/process-instance and
browser-abort gaps, implement justified fixes, and rerun the full application
gates. A bounded deployed-only JS-global affinity diagnostic now runs; it does
not identify private native Store IDs or establish cache
coherence. Its entry8f1a5b5f/constructor e0ec4689 Sources are now sealed and
independently reviewed;74 inert helper checks pass. The fresh INIT-only constructor
now completes0/clean/protected for component811459ea/37,222,602 bytes, using the
same full native engine and standard world. Validation/WIT pass with exactly13
standard0.2.10 imports and only incoming-handler export. All six inner command
streams contain no affinity marker; coordinated DATA review passes.
Its first deployed run exits1/clean/protected. All80 supplemental/24HTTP/stream
checks and both strict browser interactions pass, but cache1→1 still fails.
The four cache/revalidation admissions have different JS-global state-epoch
nonces, each ordinal7. These are observed state boundaries, not private Store
IDs, callback/tag-map traces or sole-cause proof. Added entropy/logging can
perturb timing; this browser positive does not accept any earlier failure.
Independent bounded outcome/owner/world/app review and coordinated DATA review
pass. The marker parser passes34 pure-DATA checks; both sealed constructor/runtime
capsule readers pass current-original checks. Root independently rereads all300
members and their live originals/modes with unchanged read bookends. See the
[diagnostic plan](docs/node-compat/nextjs-cache-affinity-diagnostic-plan.md).

The full-build V9, three Node off-controls and failed native off-control are
now retained as three sealed finite DATA capsules (750 members,13,713,561
logical bytes). All three readers pass `--current`; Root independently rereads
every archive member and live original with unchanged read bookends. Original
failed gates and null action bodies remain intact. An exact captured-POST
HTTP/gzip EOF diagnostic is in Source preparation, without browser navigation.
The [portable-cache proposal](docs/node-compat/nextjs-portable-cache-proposal.md)
records15 exact source descriptors and the genuine Next CacheHandler/build
integration; no shared cache handler or new application scenario is implemented.
Its real CommonJS/fileURL dynamic-import path is an unverified prerequisite.
The generic loader's referrer-private assumption needs a checked error boundary
before any suspected invalid-referrer path is exercised. The checked native boundary is now compiled in the separately reviewed ca84
build below; no suspected-invalid-referrer runtime probe has run. Next also catches handler.set exceptions, so direct error tests must
not equate every helper error with a failed application request.
Checkpoint79cdaf6c is committed and pushed. The subsequent constructor/runtime
records and five finite DATA capsules (1,050 members/32,633,279 logical bytes)
are retained in pushed checkpoint2b097ac5. The exact-action wire protocol now
completes its one native and one Node arm, both0/clean/protected. Native4afe
delivers1956 wire/1488 gzip/2963 decoded bytes; Node1997/1489/2963. Both pass
normal chunked-message EOF, dechunk equality, single-member gzip finish and
CRC/ISIZE before private-Agent cleanup. This is transport-only, without browser
navigation or React Flight parsing; original failures remain failed. Independent
DATA verification and a sealed182-member packet now pass, including Root archive/current-original readback. See the
[transport findings](docs/node-compat/nextjs-action-transport-2026-11-07.md).
The checked native referrer-boundary template is sealed/reviewed at5e7b07a6
with43 Source/API/symbolic checks. A fresh825 materialization now passes, with
824 payloads unchanged and only script_loader.cpp622b→fbc1 (+2061 bytes).
New selection456afe is genuinely admitted; all ten fresh generator checks
pass0/clean/protected. Actual V4 JSON-only preparation produces new Cargo
selectionc7e21d3e; independent/coordinated five-file, Source/Cargo and launcher
reviews pass. The full guarded native build now completes0/clean as Rootsession25962
under original owner96055/7200, unchanged3GiB start/1GiB phase/jobs1/offline
policies. Six phases pass; all825 copies,1841 protected descriptors and ten
trees remain intact. New coreca84baa1/31,326,382 bytes and actual fullmetadata
e674f7d2/4,839,816 bytes record80 native TUs plus separate embedding. Coordinated
Source/TU/link/Rust and independent owner/tree/build DATA reviews pass at a4c3c19b.
The fresh real-Next INIT constructor also completes0/clean/protected: component
49013f31/37,217,436 bytes validates with exactly13 selected standard0.2.10 imports
and only incoming-handler export. Coordinated typed-return/full-metadata review
17afbe24, independent owner/world87713051 and current packagec415d9e2 reviews pass.
No app was mounted at INIT and no ordinary export ran. The first fresh full unchanged Next regression now completes as Root
session23385/original19988/600: raw1/clean/protected/fullworld unchanged,
result2f3c0918. All24HTTP/80supplemental/five-stream checks and both strict
browser interactions pass with empty error arrays. Cache generation1→1 still
fails, so the suite remains failed; this single browser positive neither proves
a fix nor accepts earlier failures. Independent bounded runtime DATA review435dced8 now passes physical outcomes,
original owner/world,4,520 finite inputs and all2,181 app copies. It accepts
the failed result as recorded, not the cache gate or overall suite. No guarded
import-safety result exists yet. The172-text Source-stage
capsule passes its current reader and Root independently reads all172 members
and live originals/modes; it does not accept the native build.
The guarded native build is now retained in a sealed2,364-text DATA packet
(20,838,442 logical bytes; archive9c88e937/2,873,584 bytes). Default/current
readers and independent Source/DATA review pass. Root independently rereads
all2,364 archived/current original bytes and modes with unchanged nanosecond
physical bookends. The packet excludes binaries/825 payload rehash and accepts
no import/runtime behavior.
The guarded real-Next constructor/runtime packets are now sealed at120b8626/
ae829e0e (197+314 original records;30,241,812 logical bytes). Final portable and
current readers pass. Root independently rereads all511 archive/current original
bytes/modes with stable nanosecond physical bookends. Constructor-only replay
joins were strengthened before sealing, with prior reader Source preserved.
The runtime packet keeps cache1→1/raw1 and its one strict-browser positive.
Checkpoint38d05887 is now committed and pushed:264 files retain the action
transport controls, guarded full-build/INIT evidence and bounded import Sources.
The native fileURL/CJS prototype is separately sealed at3856b027 after static
review/60 Source checks, with the initial incorrect compiler-guard draft retained.
It is uncompiled and excluded from this guarded build. A separate guard-only probe INIT now completes0/clean under Rootsession13386/
original20407/2400. Componente1bddfbc/37,141,676 bytes validates with the same
thirteen standard imports and incoming-handler export. Coordinated typed/full-
metadata review6b4affe3, independent owner/worlda2171853 and fresh packagea5ef2369
reviews pass. No fixture was mounted at INIT. The first deployed guard request now completes
Rootsession84379/original24048/180 raw0/clean/protected/full-native-world guarded.
One GET returns1065 bytesb3f10854 with exactlytwo passing cases: node:path
identity/join and TypeError ERR_SM_MODULE_IMPORT_REFERRER/module_load_hook/actual
fileURL. Independent84-input owner/world/fixture/raw-response DATA review55a449e6
passes. This accepts safe refusal only; Node parity and3856 interoperability remain
false. No prototype runtime action has run.
A separate genuine Node22.14 control completes0/clean under original22178/120
using the same sealed CommonJS driver and eight fresh physical read-only fixture
copies. Natural CJS import(fileURL) succeeds, default equals require exports and
repeated namespace identity holds. It uses a canonical host fixture URL, not a
guest /probe emulation. Fifteen retained original text records/10,083 bytes pass
Root current DATA replay. Independent Source/current-DATA review now passes,
including the corrected reader's Source/fixture/URL joins; family82ddcf61 is sealed. This
reference does not accept the guest guard refusal or uncompiled interop profile.
The bounded interop source integration is now materialized once from sealed
MatV3d6c8e96b:825 files/7,548,909 bytes/fingerprint77346c39. Exactly loaderfbc1→25c
changes (+16,682 bytes);824 payloads and21 Rust base files match. Root
independently rehashes all825 source/donor pairs with modes/distinct identities.
The initial inherited readback fails at stat_result equality, which included
access time; its before/after values were not retained, so that cause remains
a source-level inference. Original code/raw1 are preserved. New stable-field
verifierd4d3eec5 passes0 without a second materialization or native/tool action.
GeneratorV3 now passes ten30-second checks/outer26747/900, result9054c28e;
coordinated/independent DATAafaa9dfb/90794dbc pass. Actual V5 JSON preparation
finishes0 with five files, new Cargo selection3b53bc43, review04fb01ba.
The first actual full interop native build completes Root7872/original28790/7200
raw1/clean: build phase fails at script_loader.cpp324 because JS_ConcatStrings
requires a HandleString and receives a raw JSString*. Other five phases finish0.
All825 copies/1871 protected descriptors/ten trees remain unchanged; independent
failure DATA reviewd2419fe2 verifies them. Genuine failure metadataBE397c3c is
retained whole and unaccepted; engineCandidate is NULL and DB80 is configured
inventory, not80 successfully compiled units. No constructor or guest followed.
A separate sealed candidateV2 7dbad8b6 adds only a rooted string handle (+67B).
Fresh Mat4 6d51906e produces825/7,548,976 bytes/fingerprint89331d92; summaryd0948dee,
composition2ba95fc6 and genuineV6 selection06d0d597. All825 donor/target pairs
pass Root stable-field readback,824 other payloads/21Rust unchanged. The single
owned frontend-only check now finishes Root50200/original52221/180 raw0/clean,
with fresh Source, complete SDK/SM trees and failed WORK snapshots unchanged.
It produces no object/link/engine; coordinated owner/snapshot DATA review51f52a15
passes. Fresh GenV4 finishes Root46354/original53305/900 raw0/clean for ten30-second
checks, result5ebaaf31; deep/current and owner reviews50568cd3/d7c0bcc5 pass.
Actual V6 JSON preparation finishes0 with new Cargo selectionf9a39f84, five
outputs and reviewdce0cf7e. The corrected full native build now completes
Root10067/original56661/7200 raw0/clean, all six phases0, all825 copies/1887
protected files/ten trees unchanged. New core2251f11a is31,341,287 bytes and full
metadataafb14d8a is4,861,271 bytes. Independent current payload/owner/tree DATA
primary review0d23a90e and coordinated Source/TU/link/Rust review237cd3a3 pass.
Aggregateb9aad169 accepts build DATA only. Subsequent component08ce/98fc INIT
review and one deployed16-case pass4c919dbf are recorded separately above.
Optional CacheHandler Source1f8398a6 is sealed separately. Root's owned fake-Node
model50293/120 passes40 assertions, with independent model/ledger review. All
cache FS, entropy and Next calls are explicitly in-memory fakes (actual Source
reads and Node SHA remain real). No real storage/Next/WASI or old cache-gate
acceptance follows. Eight Source payloads/55,129 bytes retain their initial
UNEXECUTED cutoff labels with a separate factual execution ledger.
The failedInteropV1/frontendV2 packet is sealed at4a978157 (2,233 original
records/42,758,939 logical bytes, archiveeb2f87f6/6,437,743 bytes). Default/current
readers and final peer closure pass; Root independently rereads all2,233
archive/current bytes/modes with stable full nanosecond bookends. The old build
stays failed; the standalone frontend trial does not become a full build.
The235-record guard INIT/runtime capsule is sealed at a5fb78c5 (20,870,204 logical
bytes; archivef8c93bac/2,992,159 bytes). Default/current readers and final peer
closure pass; Root independently reads all235 archive/current originals/modes
with stable nanosecond physical bookends. Guard safe refusal remains the scope.
The prior capacity observations below
are historical; the storage blocker is resolved for this execution.

**Next.js is the immediate priority.** Next: retain the new failed full
regression, run the deployed checked-referrer probe, compile/test the bounded
CJS/fileURL bridge, then implement the explicit shared-cache scenario, using
standard WASI and unchanged stock hosts. Resolve demonstrated response/resource
issues before expanding APIs. A future portable cache scenario must use a new
versioned fixture and genuine Next extension; it cannot relabel the failed
lexical-counter gate. Broader cancellation/resource boundaries, Node APIs,
performance measurements and production promotion follow these gates. See the updated
[execution roadmap](docs/node-compat/nextjs-priority-roadmap.md).

The earlier prepared NativeV8/StockV6 pair and full build were held below their
1 GiB and 3 GiB start guards. Those holds preceded the actual results above.
During that hold, the
first [relocated Cargo source restoration](tests/node-compat/frameworks/nextjs/native-cargo-restore-root-results-v1/README.md)
completed with exit 0 using 75 checksum-pinned cached registry archives, the
exact Firefox FFI donor and 21 portable native source files. It created 3,506
payload files plus its receipt, with 47,176,588 logical payload bytes. No
Cargo, compiler, network or guest ran in that source-only operation.

The first V1 admission then failed: publishing the receipt changed the APFS
root link count from 6 to 7. Its failure and original `42559665…` receipt are
preserved unchanged. A separately reviewed
[V2 read-only admission](tests/node-compat/frameworks/nextjs/native-cargo-restore-admission-v2/README.md)
checks stable root device/inode/mode, every payload and exact membership,
and retains the current full-root bookend guard. Root's genuine corrected
readback now passes 3,507 files and 464 directories including the root, while
reporting both link counts separately. It does not attest source process
execution; the original terminal exit 0 and raw streams supply that separate
observation. The relocated inputs now also pass a genuine offline Cargo query,
as recorded below. The complete native build and new Next request-pair results
remain outstanding.

The first [offline metadata verifier launch](tests/node-compat/frameworks/nextjs/native-cargo-offline-verify-root-results-v1/README.md)
exits 1 before creating output or starting Cargo. Its strict boolean guard
incorrectly rejects Python's integer `sys.flags.isolated` value `1`, despite
the actual `-I -B` command. The original Source, authority and raw failure
are retained; no dependency query or native compilation occurred in that
attempt. The separately reviewed V2 corrects only those two guards and passes
23 real-interpreter/inert flag checks.

The [new actual metadata query](tests/node-compat/frameworks/nextjs/native-cargo-offline-verify-root-results-v2/README.md)
now passes: Root, original process owner, worker and Cargo all exit 0, with
clean cleanup and unchanged inputs. New metadata `65544c7b…` (352,680 bytes)
matches all 84 logical packages, features, dependency aliases/kinds/edges and
six root dependencies. Every manifest points to its fresh restored role; the
old graph remains a comparison reference. Cargo made a sampled, observed
`rustc` information query. No source-compilation command, engine build or guest
execution was requested. The complete 23-file output is retained as an indexed
DATA archive for future inspection; live source identities still require the
separate admission API.

The [V3 builder integration](tests/node-compat/frameworks/nextjs/next-native-portable-build-preparation-v3/README.md)
is now **implemented, reviewed and held** at index `d4341284…`. It replaces
four old Cargo locations through the existing build mechanisms, admits the
actual offline metadata and live restored files, joins all 21 base files to
the full portable source selection, and verifies their independent WORK copies.
The Python 3.11 wrapper is separately pinned; Python 3.9 remains the native
build tool. Both Source reviews pass, including 53 helper DATA checks and the
specific CMake empty-feature equivalence; 19 operational functions and the
same-role native command/environment behavior remain unchanged.

The [actual V3 preparation](tests/node-compat/frameworks/nextjs/next-native-portable-build-root-results-v3/README.md)
exits 0. It writes five JSON files and no source copies or native commands.
The new Cargo selection is `1947c893…`; Root's concrete unissued draft is
`1124aab9…`. Root's 33 inert checks, read-only launcher and input admission pass:
435 native/387 support/3 embedding files, 22 public/2 private manifests, 1,825
file descriptors and ten inventory descriptors. This does not replay every
live tool-tree member. Final preparation/launcher review passes, and the five
original JSON files are retained as indexed DATA.

The actual **read-only capacity check exits 1** at 659,873,792 free bytes,
below 3 GiB. No full build launch is attempted, authority issued, or native
WORK/monitor directory created. Preparation is complete for this generation;
the complete native build and new Next request pair remain outstanding.
Priority remains: run the prepared request pair once 1 GiB is free, then run
the full build when 3 GiB is free and test the complete application on the new
component. No production default or compatibility claim has changed.

The prior goal turn made concrete progress: paired six-case regression Sources,
reviewed commands, native build preparation/launcher and capacity refusals were
committed and pushed ase0adca1c. Current capacity remains below1GiB; no new
application trial has started. While launch is held, source/bootstrap work has
removed two concrete acquisition risks. The exact patched SpiderMonkey CI ZIP
was due to expire on2026-11-09. Root rehashed its existing227,965,139-byte copy
and [preserved it in an authenticated draft release](tests/node-compat/frameworks/nextjs/native-bootstrap-artifact-retention-v1/README.md),
release437352699/asset719685339. All three uploaded server asset digests match
the local ZIP/checksum/provenance files, and independent readback passes. The
archive was neither repacked nor downloaded again; no remote round-trip,
public release, engine rebuild or runtime validation is claimed.

The previously unresolved baseline ComponentizeJS source archive now has a
[verified public acquisition record](tests/node-compat/frameworks/nextjs/componentize-source-origin-v1.json).
The GitHub connector confirms release0.23.0 commit4d812f5a; a bounded HTTPS
download of that exact commit archive returns200 and matches the captured
archive byte-for-byte:8178fb67/162,093 bytes. Its270 original regular files plus
a later marker account for the staged271 count;89 directory entries and no
links are present. No archive was extracted or package/toolchain built. The
generated private61685 splicer/package reproduction remains a separate gap.

Future request-pair checks now have a reviewed
[V3 DATA reader](tests/node-compat/frameworks/nextjs/next-request-regression-check-v3/README.md),
index521ed6bd, with178 inert/retained-DATA checks and explicit separate capture
and pair modes. It binds current V8/V6 Sources, original ownership/protection,
all24 HTTP/cache/stream/2browser checks, physical six-case bytes, fixed native
component/metadata/constructor and the standard13-interface world. Genuine
older-generation wire audits are schema evidence only. Review found a missing
native namespace separator, Python boolean/integer equality and missing origin
joins before any actual pair was admitted; those V1 bytes remain held. V2's
failed-capture parser rejected numeric DOMException codes, so the minimal V3
preserves finite20/23 values with strict pair errors still required null.
Constructed Node error serialization is not a timeout or abort experiment.

Root's three read-only CLI checks validate a retained local positive capture,
retain an intact partial response as integrity-valid/strict-failed, and refuse
the older NativeV7/StockV4 pair at its Source-authority join. Every result has
pairAdmission:false and no actor/network action. The actual new V8/V6 pair and
successful real-pair admission remain unexecuted under the same capacity hold.
All failed/limited Source generations are preserved; no target result is
retargeted or relabelled.

The [external bootstrap manifest](tests/node-compat/frameworks/nextjs/native-bootstrap-inputs-v1.json)
and stdlib checker now pass independent review and51 DATA refusals. The default
read-only check authenticates37 retained records, all25 payload pins through
explicit witnesses,84 Cargo packages and76 vendor-checksum records. A small
[installed-state npm lock capture](tests/node-compat/frameworks/nextjs/native-bootstrap-npm-installed-lock-v1.provenance.json)
retains exact28d3/46,394 bytes and independently binds78 normalized transport
rows; historical filesystem keys/extraneous tools remain DATA, not an npm-ci
root lock or private package reconstruction. Review caught missing null-digest
pin witnesses and Python boolean/integer row equality before final handoff;
all25 changed-hash cases and the typed row counterexample now refuse.

Root's actual `python3.12 -I -B .../check-native-bootstrap-inputs-v1.py --plan`
readback with two explicit existing-payload hashes exits0. No payload is
downloaded/extracted and no build/target tool runs. Python3.11+ is specific to
this metadata reader; buildPython3.9 stays pinned. Rust's eight component rows
remain reported metadata, with no snapshot or archive rehash claim. The
manifest's eight-step restoration order keeps five gaps explicit: relocated
locked vendor restore, exact host-tool acquisition, generated61685 package,
original988 adapter provenance and capacity/full native build. Clean-machine
restoration and new V8/V6 application results are still unproved.

The **first fresh-build Next.js pair now passes on Node and real Wasm**. Each
passes24/24 HTTP, cache generation1→2, five incremental stream chunks(shell0,
ready2) and2/2 strict browser interactions with empty error arrays. The actual
2,181-file app comes from the isolated build, with its new build/action IDs.
Matched Node result1e02e583/323608 and native result650e7a91/8546 both finish
raw0 with clean ownership and protected inputs. Native physical-copy and full
world/native/constructor guards pass; server SIGINT exits0. The [portable paired
DATA review](tests/node-compat/frameworks/nextjs/next-app-runtime-root-results-v1/first-pair-review/README.md)
is sealed83988ce9/1712, retains304 logical payloads and passes Root readback.
The earlier V5 abort remains unresolved.
The stock copy retains source modes and gains owned runtime cache files under
both `.next/cache` and `.next/server/route-cache`; its whole tree is not
immutable. Native copy guards require exactly the2,181 input files plus the
declared empty mountpoint; final copy checks pass, with a separately mounted
writable cache. The
matching cache API result is not a claim of identical filesystem layouts.

Headroom recovered before launch: stock admitted1,638,600,704 free bytes and
native1,578,336,256, above the unchanged1GiB Root start floor. These are start
observations, not a measured peak or continuous disk guard. No new engine or
component was built: existing1c3108d2 loads the genuinely fresh `/app` tree.
The fresh wasmCloud cold8 trial also passes. The fixed three-pair browser
cohort is now complete: **5/6 runs pass, so the all-six strict gate fails**. Native3/3 pass, matched
Node2/3 pass. All144 HTTP checks and12 browser functions pass, but p3-stock
reproduces action POST `ERR_ABORTED` with no captured body. All six cleanup,
source/world and helper checks pass; no sample was retried or filtered. This
reproduces the symptom under the matched Node bridge and does not identify its
cause. The [portable cohort DATA review](tests/node-compat/frameworks/nextjs/next-browser-reliability-root-results-v1/cohort-review/README.md)
is sealedd9ffd359/2008, retains580 logical records and passes Root readback with
strictCohortGatePassed:false. Direct unmodified standalone Node comparison now
also passes once, as described below; no cause is inferred. Earlier capacity
holds and preparation-only observations below retain their original scopes.


**Established passing Next baseline:24/24 HTTP,2/2 browser on55f05.**

The new integrated observed-I/O adapter candidateV5 constructs as1c3108d2/
37,214,251 bytes, same462 engine and13 standard WASI0.2.10 imports. Its first
full Wasmtime run passes24/24 HTTP, cache1→2, five stream chunks(shell0/ready2)
and both browser interactions, but the **strict overall result fails**:
the browser action POST reports ERR_ABORTED after its200 response/URL change,
followed by unavailable response-body capture. The abort precedes explicit
context close; a later response.finished Targetclosed is secondary. No cause
or benign exception is established, and no error is filtered. Result8fa934ee/
7970 bytes and complete browser evidence remain retained. The [portable failed
review](tests/node-compat/frameworks/nextjs/next-intl-runtime-root-results-v1/full-next-io-v5-first-review/README.md)
retains195 records and passes Root readback, without changing the runtime's
raw1/strict-failure status. Process shutdown,
inputs, app copy and whole-world/native guards pass. V4 had a similar abort
pattern, so this observation alone does not establish an adapter regression.

The same new component separately passes all8 cold wasmCloud requests, including
strict streaming(three chunks/shell0/ready1), config/dev/outer0 with inputs and
ownership preserved. That result e7c99602/46831 bytes does not accept the failed
Wasmtime browser contract. The [cold DATA review](tests/node-compat/frameworks/nextjs/wasmcloud-cold-root-results-v3/actual-review/README.md)
retains150 records and passes Root readback;175 selected current descriptors
and both2218-file app trees pass separately. The failed full-run review above
also passes evidence validation while retaining the strict failure.
Read-only CDP network diagnostics and an observer failure-terminal correction
now have one actual paired trial: matched Node and the **same integrated1c31
component** both pass24/24 HTTP, cache/stream and2/2 strict browser checks with
empty error/failure arrays. Seven CDP event types record action network
completion before same-document navigation in each trial;2963-byte body files
are captured afterward. Their opaque action bodies have different hashes and
are not normalized. This is a new observer trial with unchanged assertions,
20s/500ms limits and strict failure gate; it **does not establish the cause,
fix or reliability of the earlier abort**. Resultc737eaad/7450 bytes and matched
Node51c54176/322922 bytes both finish raw0/clean with inputs preserved.
The [portable paired DATA review](tests/node-compat/frameworks/nextjs/next-intl-runtime-root-results-v1/full-next-io-cdp-v6-review/README.md)
retains299 records and passes Root readback. Previous55f05 first/repeat passes and the
failedV5 record remain unchanged.
The native copy is physically0444/0555; the matched Node copy retains original
source permissions and checks2,217 immutable files while excluding its owned
cache. The captured stock request's prose incorrectly called that copy
read-only; the request remains unchanged and the DATA review records this
qualification. Neither result proves equivalent OS/WASI permission mechanisms
or read-only WASI descriptor rights.
The unchanged Next16.4.5/React19.3.1 standalone application runs in the real
SpiderMonkey Wasm component on stock Wasmtime42.0.1, in two fresh successful
runs. Native UTF16 engine
`4623640b` and component`55f05e3d` pass cache invalidation generation1→2,
incremental Suspense delivery (five chunks/shell0/ready2), a hydrated counter
click and a real browser Server Action. Page, console, network and collector
errors are all empty. Five pinned client scripts match their decoded source
bytes. Original parent exit0, owned shutdown and original/read-only app
bookends pass. The matched pinned Node22.14 control also passes the same full
contract using byte-identical browser-worker code. The new
`tests/node-compat/frameworks/nextjs/run-native-next-regression.py` command
creates a fresh request and reuses the existing bounded runner; its actual
`engine462-hydration-v5-repeat` run passes the complete contract again.
The [portable native first/repeat reader](tests/node-compat/frameworks/nextjs/next-intl-runtime-root-results-v1/hydration-v5-review/README.md)
and [matched Node reader](tests/node-compat/frameworks/nextjs/next-intl-runtime-root-results-v1/hydration-stock-v1-review/README.md)
both pass Root readback. Full raw process, HTTP, stream, browser, decoded body
and screenshot evidence is retained; generated action RSC bodies retain their
distinct hashes. These DATA readers validate evidence without executing targets.

**Next phase in progress:** the [native signal-pipe regression](tests/node-compat/frameworks/nextjs/native-pipe-root-results-v1/README.md)
now has an actual pinned Node reference: three complete calls ×12 cases,
36 captured records, raw0/clean and empty stderr. Complete monitor/stdout records
are retained. These are reference records, not Node/guest comparisons. A
reporting-label mistake in the original observation is preserved and clarified.
The [strict real-component collector](tests/node-compat/frameworks/nextjs/native-pipe-wasmtime-collector-v1/README.md)
now runs successfully: all36 actual guest records match Node exactly, runtime
and constructor parents0/clean with inputs preserved. Component1c711297 is
37,162,665 bytes and emits exactly13 selected standard0.2.10 imports. This tests
the guest facade over actual native streams, not a replacement C++ pipeTo or
native teardown/resource-count proof. The [portable actual review](tests/node-compat/frameworks/nextjs/native-pipe-root-results-v1/actual-review/README.md)
retains169 raw/source records and passes Root's DATA readback; its optional
current check covers188 selected descriptors, not a recursive SDK audit.
The collector's42 pure retained-DATA/
mutation checks and27 Source joins remain separate. Root's wrapper checks
the referenced8025 WIT family, exact file/directory membership and all8 WIT
descriptors before/finally, with independent source review. The earlier
unexecuted grant lacking that explicit whole-family guard is retained.
The [request-context/lifecycle audit](docs/node-compat/nextjs-context-lifecycle-plan.md)
identifies the nonreentrant embedding, cross-owner Promise coverage, surviving
unref-task policy and missing peer-disconnect→Request.signal mapping. These are
coverage/design boundaries, not newly observed native failures. A five-control
same-export native A/B differential Source now passes918 host assertions across
six collections (original Node and sealed facade); this is not native proof.
It constructs as component938e6913/37,207,968 bytes, three phases plus parent0/
clean, same13standardimports and unchanged whole-world guard. The actual V2
runtime now passes all459 native assertions across three HTTP calls, with29
required event edges per call and exact original-Node public projections.
Runtime/parent0, clean owned shutdown and input preservation pass. These are
genuine native logical branches within an export; actual same-Store HTTP
concurrency and native peer-disconnect teardown remain open. The separate
unref-across-calls result below closes its finite ordinary-call control.
Independent review found that the first
collector's positive self-report gate could reuse a structurally unknown
collection before later strict validation rejected it. No runtime was launched
with that collector or its grant. Both are retained; a successor will require
strict schema/assertion/edge validation after saving each body and before any
reuse, while preserving the all-three-before-Node-comparison fence. The V2
successor implements that correction and passes85 inert DATA checks, including
four actual old-pass/new-refuse cases and stop-before-next-request controls.
Only V2 was executed. Its [portable actual review](tests/node-compat/async-context/context-interleaving-root-results-v1/actual-review/README.md)
is sealed and passes Root's DATA readback:154 retained records, all459 native
assertions/87 edges and15 original-Node public projections, with918 host checks
kept separate.

The [ordinary-call unref control](tests/node-compat/async-context/unref-reuse-root-results-v1/actual-review/README.md)
also now passes in the real component: three calls,51 total call checks and9
distinct cumulative callback checks, with exact original Node projections. The
old A callback runs once during B with both original A markers; B cancels the
candidate and C observes no delivery through its finite fence. Component29722cfb
is37,138,315 bytes,13standardimports, constructor/runtime parents0/clean and
whole-world guard unchanged. The162-record portable DATA reader passes Root
readback. Local pending0/hasRef flags are not native queue/root counts, permanent
cancellation, timer accuracy, physical Store identity or teardown proof.

The [peer-disconnect diagnostic Source](tests/node-compat/frameworks/nextjs/peer-disconnect-candidate-v1/README.md)
now has one real Node localhost reference with healthy controls, a partial upload
read error and a later output-write error/cancellation. Its componentfaef5c87/
37,142,088 bytes constructs in three phases plus parent0/clean with13standard
imports. The independently reviewed two-cohort collector now ran once against
the actual component. Both fresh servers passed healthy8192-byte upload and
32768-byte output controls. A1024-byte partial upload produced a typed WASI
last-operation-failed read, translated HttpProtocolError, handler catch/finally
and a normal adapter path, followed by the permitted fourth-call JS inspection.
Closing the output after4096 actual body bytes caused the second write to fail
with closed; reader and producer cancellation returned and adapter finally ran.
That export failed, so the harness sent no inspection request and discarded
the owned server. The retained result is **valid inconclusive evidence**, raw1:
both within-export I/O paths observed, functional controls passed, complete
after-return coverage false. Runtime ownership and protected-input checks pass.
The runtime result is e5e10dac/785436 bytes. The [portable DATA review](tests/node-compat/frameworks/nextjs/peer-disconnect-root-results-v1/actual-review/README.md)
retains186 text/source records and passes Root readback; its212 selected current
descriptors pass separately. The reader reports the actual collector's raw1
and coverageComplete:false explicitly; its evidence-integrity pass is not a
disconnect acceptance pass.
Current uninspected input-finish future and missing peer-linked Request.signal
remain explicit baseline limits. No native cleanup claim follows from Node logs.
An [observed-I/O cancellation successor](tests/node-compat/frameworks/nextjs/peer-disconnect-candidate-v2/README.md)
uses native AbortController/Request signals and a specific handled-output-close
path. Review found a new allocation before its resource try/finally, which could
skip incoming/outparam cleanup on a constructor throw. No V2 construction or
workload ran; the Source, constructor and unused Root request remain retained.
A narrow V3 correction moves allocation inside the existing cleanup block.
Healthy EOF stays unaborted; handled output-close requires successful cancel,
lock release and cleanup. Unknown errors/cleanup failures remain failures;
finish-future inspection remains deferred. [V3 Source](tests/node-compat/frameworks/nextjs/peer-disconnect-candidate-v3/README.md)
passes independent review, including the exact-function inert cleanup case.
It now constructs as643742a2/37,142,579 bytes: three commands and outer parent0/
clean, same13standardimports and whole8025world unchanged. Independent review
found that collectorV2 could permit
inspection after a normal output path with an unexpected aborted signal and
no observed I/O abort. Its Source and unused Root runtime request are preserved;
the narrow collectorV3 correction requires the expected fresh signal on that
normal path, while retaining the stricter handled-close signal/cleanup proof.
That one-line correction passes independent review and now ran once against
the genuine component: **all eight peer-control responses pass**, two fresh
hosts/four healthy controls, both observed-I/O signal paths and both same-factory
fourth-call JS inspections. The upload1024-byte read failure aborts with the
same reader error; outputclosed aborts and completes cancellation, lock release,
ordered drop calls and the explicit handled normal return before inspection.
Healthy and inspection requests keep fresh unaborted signals. Resultf25bed1f/
1,127,253 bytes and outer parent exit0/clean with inputs preserved. The [portable
actual DATA review](tests/node-compat/frameworks/nextjs/peer-disconnect-root-results-v3/actual-review/README.md)
retains263 records and passes Root readback;289 selected current descriptors
pass separately. The upload's already-errored reader cancel rejection and the
host's IncompleteMessage line stay visible. Neither is counted as successful
upload cancellation or native cleanup. This is an isolated JS-adapter regression over native
APIs, not native resource-count/Store-death proof. The policy is now integrated
in candidate1c3108d2, whose first full regression remains a strict failure as
reported above; fully passing55f05 is unchanged.
The next host priority is a finite cold-instance wasmCloud check of the same
unchanged full Next component. The first actual eight-request attempt failed:
the harness mistook the early TCP listener for deployed-workload readiness.
All eight responses were empty host404s; config-show exited0, wash exited130
after SIGINT during startup, outer raw1 with owned groups gone and inputs
preserved. No successful Next handler or thirteen-interface instantiation is
established by that attempt. Source/result1c691de2 are retained unchanged;
a successor will wait for the pinned CLI's exact post-registration
`listening for HTTP requests` marker and matching address before the first
request, with the same eight assertions and no HTTP retries. The [portable
failed-DATA review](tests/node-compat/frameworks/nextjs/wasmcloud-cold-root-results-v1/actual-review/README.md)
retains101 records and passes Root readback. It keeps the failed runtime result
separate from evidence-integrity validation; the original Source review's
missed registration gate is recorded. The [V2 readiness correction](tests/node-compat/frameworks/nextjs/wasmcloud-cold-candidate-v2/README.md)
now ran successfully against the **same unchanged55f05 component** on stock
wasmCloud2.11.0/embedded Wasmtime48.0.7: all8HTTP200/status/body assertions pass,
including SSR, JSON POST, filesystem/SHA and assets. Suspense has three chunks,
shell0/ready1. Config-show, wash-dev and outer parent exit0; owned shutdown,
original/copied app and whole-world protections pass, no recorded errors.
Result0d73be85/44509 bytes is retained. The [portable successful DATA review](tests/node-compat/frameworks/nextjs/wasmcloud-cold-root-results-v2/actual-review/README.md)
retains117 records and passes Root readback;142 selected current descriptors
and both2218-file app trees are checked separately. Both the original failure
and its stricter readiness successor keep
the same60-second registration cap and eight-request contract. wasmCloud's P2
fresh-Store behavior requires a separate contract from retained Wasmtime cache
and browser acceptance.
The [measurement plan](docs/node-compat/nextjs-measurement-plan.md) defines
separate launch/first-health/follow-up timing, paired Node/Wasmtime trials and
sampled public server RSS. It is design only; no new performance or clean-machine
reproduction measurement has run.
The [clean-machine dependency audit](docs/node-compat/nextjs-reproducibility-plan.md)
locates the committed824-source reconstruction map, V7 edits, patched
SpiderMonkey/Rust build mechanisms, UTF16 delta, real app build and constructor.
The new [portable source materializer](tests/node-compat/frameworks/nextjs/next-native-portable-source-v1/README.md)
now reconstructs all825 declared inputs from repository-relative committed
donors:435 native,387 support and3 embedding files,7,530,166 bytes. All content
matches the actual V7 declarations plus the single UTF16 substitution. Its35
source-only tests cover fresh copies, relocation and refusal cases; Root's
read-only --check also passes. No compiler or guest ran. Builder integration,
authenticated external tool/artifact materialization and a full clean-machine
engine build remain outstanding. The isolated app build below has run; no clean
engine build is claimed.

The [isolated app-builder Source](tests/node-compat/frameworks/nextjs/next-app-build-v1/README.md)
is now implemented with a read-only default plan and explicit fresh-output build
mode. It isolates the original locked npm/Next commands and standalone
packaging from the historical corpus.57 inert tests and independent Source
review pass. **The first actual isolated host app build now passes**: four
original-owned phases(version probes, npm ci, Next webpack build) raw0/clean,
package/lock/tool/source preservation and standalone packaging all pass.
Resultfe0e0bdb/709565 bytes records2,181 fresh files/48,714,867 bytes,425
directories(excluding root), no links, buildIDc2R8ovhEoFinJh6IvlO5M and actual
action40ca0bda6c41d5a4ff46cda3035ad9babb89d96900. The new inventory is not the
old2,218-file record and has not yet been served or accepted inside Wasm.
The [sealed actual DATA review](tests/node-compat/frameworks/nextjs/next-app-build-root-results-v1/actual-review/README.md)
retains78 text payloads and passes Root readback. It validates all four owned
phases and fresh inventory without serving the app or executing a guest.
C independently rechecked the DATA package and exact current source/tool/app
membership; no material flaw was found. C authored the app CLI/acquisition, so
this is independent of the DATA curator, not an independent approval of C's
own implementation.
Fresh runtimeV7/stockV3/browserV3 [Source successors](tests/node-compat/frameworks/nextjs/next-app-runtime-root-results-v1/README.md)
are now sealed and independently reviewed: bd785648/3720,41361ae1/3071 and
5faa8f5d/3219. They explicitly handle the root-excluding schema and current
source-root identity, declare only the owned native copy's empty cache
mountpoint before chmod, and replace two of five browser asset pins. Native
owned directory count is427 including root; source425 excludes root. Existing
dynamic action-ID extraction,24HTTP/cache/stream/two-browser assertions,
20s/500ms limits, strict error gates and600/300s owners stay unchanged. Root
readback and C independent reviews pass31 native inert,20 stock read-only/inert
and18 observer checks; this executes no copy/server/browser/guest. No
engine/component rebuild is needed merely to load `/app`.
The new [fresh-app regression CLI](tests/node-compat/frameworks/nextjs/run-fresh-next-regression.py)
pins the reviewed generation, requires a fresh run ID, preserves raw results
through the existing guarded runner, and has an explicit conservative1GiB Root
launch floor. It is not a clean-machine bootstrap or continuous space guard.
Its real `--prepare-only` passes(raw0/request3facd984), duplicate preparation
refuses without changing the request, and an inert mocked-zero-space case
refuses before request/actor. C's read-only grant/CLI review and AST checks pass.
Actual preparation free space was280,678,400 bytes; fresh-app runtime remains
unperformed. Late grants are prepared for matched Node first, then Wasm once
headroom permits; no favorable retry or error filter is introduced.
An official Node22.14 archive and published HTTPS SHA sum now supply npm10.9.2
in a fresh private prefix;2,379 npm files and the existing Node binary's exact
match to the archive entry are verified without executing npm. No OpenPGP
verification is claimed. The [portable acquisition reader](tests/node-compat/frameworks/nextjs/next-app-tools-bootstrap-v1/README.md)
passes Root readback. An initial app-build preflight held at1,019,109,376 bytes;
later launch revalidation passed at1,075,671,040 bytes without changing the1GiB
floor. The app build then ran once. Free space afterward is482,373,632 bytes;
the request for3GiB/another volume remains relevant to further heavy/native
work. A later `df` reports roughly201MiB available. No old proof, SDK, binary or
shared cache was deleted. The [priority roadmap](docs/node-compat/nextjs-priority-roadmap.md)
now puts fresh-app Wasm acceptance first, browser reliability second and the
fresh second-host contract third; unrelated API expansion and a new engine build
are outside that immediate critical path.

The [browser reliability protocol](docs/node-compat/nextjs-browser-reliability-plan.md)
has now run its exact three additional pairs in alternating arm order, retaining
all outcomes without favorable replacement, error filtering or longer limits.
StockV4/1770abb8 and its reusable control CLI provide reviewed safe namespaces;
73 selector and76 single-member-launcher inert checks pass. Exact registry
c185f2f8 fixes six authorities/argvs/outputs and23 shared inputs plus prerequisite
review83988ce9. Root explicitly selected each member and audited all six, including
the last. Final-audit state is COHORT_COMPLETE_STRICT_GATE_FAILED_V1: raw exits
0,0,0,0,1,0. Native3/3, stock2/3, overall5/6 strict runs pass;144/144HTTP and
12/12 browser functions pass. This does not meet the all-six strict gate.
The p3-stock CDP candidate reports200/data/ERR_ABORTED,canceled:true and no
loadingFinished, before explicit context closure. Its3 observer errors stay
failed and no body/hash is invented from byte counters. Primary failure is
about45.5ms before context close; arrival order is not cross-clock causality.
This matched Node reproduction changes the investigation, not the error policy.
Finite positive runs do not establish a cause, failure-rate bound or reliability.
The [pinned client Source analysis](tests/node-compat/frameworks/nextjs/next-browser-reliability-root-results-v1/source-analysis-v1/README.md)
is sealed841c597c/1031 and independently reviewed: the selected production POST
has no signal, its compiled fetch wrapper is pass-through with cacheComponents
false, and React can return the Flight root while its reader continues toward
EOF. No explicit abort was identified on that path. History/context-close
arrival order and equal byte counters are not causal or EOF proof.

The [first direct unmodified standalone control](tests/node-compat/frameworks/nextjs/direct-standalone-control-root-results-v1/README.md)
now passes the same24HTTP/cache/stream/2strict-browser contract, with empty
error arrays. SourceV2e3988d57 and grant06af77ea run bare Node22.14 plus verbatim
ownedserver.js, without Module provider/HTTP bridge/preload/IPC. Result13b50c79/
6864 and outer61630087/5833 record controller/client0, declared serverSIGINT130,
no exit signal/force and original source preserved. SIGINT130 is an explicit
source-derived shutdown convention for this separate control, never a filter
for HTTP/browser failure. V1's cleanup-status/raw0 reporting coupling was
corrected in a genuine V2 before any direct actor; ownership-clean is now
independent while acceptance still requires raw0. Launch admitted1,286,488,064
bytes above1GiB. The [portable direct-control DATA review](tests/node-compat/frameworks/nextjs/direct-standalone-control-root-results-v1/actual-review/README.md)
is sealed8b85ab6d/1715, retains143 logical originals and passes Root readback.
This single positive
comparison does not accept the failed cohort or identify its abort cause.
The extra-CDP-session-off browser/stock controls are now held and independently
reviewed: browserf73c2434/3413, workerd46dbb4b/26248 and stockV5de7f0b14/5224.
Only the additional diagnostic session is disabled; Playwright's built-in
protocol, all functional bodies, five pins,20s/500ms and request/body/error gates
remain unchanged.42 browser and116 stock inert/read-only checks pass. No such
actor has run yet, and a positive control cannot accept the failed original
cohort. The [three-sample diagnostic](tests/node-compat/frameworks/nextjs/extra-cdp-off-root-results-v1/README.md)
is declared79eb9dfa/8680 with11 shared inputs and reviewed single-member driver
066350a3/13014(67 inert checks). Its first launch refused BEFORE any actor or
output/monitor/launcher directory at the unchanged1GiB floor. Subsequent free
space was673,460,224 bytes. All three members remain unexecuted; the same unused
off1 request can resume when headroom returns. Earlier permission-null
preparations were caught in pre-launch review and preserved unused; corrected
V2 requests9fd6e9b6 explicitly select the intended two true permissions. No
runtime failure, retry or gate relaxation is inferred from either preparation
issue. Original cohort remains strict5/6 with its failed p3-stock retained.

While live diagnostics remain capacity-held, the portable native-build path
advanced. The new [V1 Source admission](tests/node-compat/frameworks/nextjs/next-native-portable-build-preparation-v1/README.md)
explicitly selects all435 native/387 support/3 embedding inputs, replacing the
historical386 support donor dependency and removing old compiled-output
prerequisites while retaining archive provenance. Exact CMake/Rust commands
and3GiB/1GiB guards remain.32 portable/42 extended source-data checks pass; Root
actual JSON-only [preparation](tests/node-compat/frameworks/nextjs/next-native-portable-build-preparation-root-results-v1/README.md)
exits0 with selectionb209cf8f and unissued draft68df6a7a. No build was granted.
Independent review qualifies that parser/draft path but holds the V1 generator
consumer for explicit producer-plan/index/Root-grant semantic joins. The
[genuine V2](tests/node-compat/frameworks/nextjs/next-native-portable-build-preparation-v2/README.md)
now passes independent review: the actual receipt reaches all61 proof
references and25 DATA mutations refuse. Root's actual
[V2 preparation/admission](tests/node-compat/frameworks/nextjs/next-native-portable-build-preparation-root-results-v2/README.md)
also exits0, retains the exact originalb209 selection path and emits unissued
draftdc91e5e7 without copying the selection. V1 and its unissued data remain
preserved. This closes receipt linkage, not full build execution.
The [unissued full-build input draft](tests/node-compat/frameworks/nextjs/next-native-portable-build-root-results-v2/README.md)
then passes the real builder's read-only `effective_plan`, `inputs` and
`selected_manifests`:435/387/3 inputs,22 public+2 private manifests,1,767
protected file descriptors and10 inventory/provenance descriptors. Independent
review confirms its inherited tool/SpiderMonkey/Rust facts match the successful
build and its generator pins match the new result. No required field or file
is missing. Full live tool-tree verification remains a launch-time gate;
configure/build remain NULL and the proposed work directory is absent. This
step does not run any tool, source copy or native build.
The compact full-build launcher now passes32 inert checks,2 AST checks and
independent review. Root's actual `--run` invocation refuses at the first3GiB
capacity gate, exit1, before issuing an authority or creating work/monitor
outputs. The unchanged unissued draft and absent paths are checked; the full
refusal and753,332,224-byte **after-refusal** observation are retained. No native
build or workload started. The reviewed one-command path is ready for sufficient
headroom, with original7200s ownership and all worker guards retained.

The next actual application regression is now prepared: reviewed
[NativeV8](tests/node-compat/frameworks/nextjs/wasmtime-deployment-candidate-v8/README.md)
47c821e8 adds six concurrent context/body/recovery cases through unchanged Next
routes, then requires every original24HTTP/cache/stream/2browser assertion.
The deploy actor, owned runner and app policy remain byte-identical to V7;
component1c31, engine462, fresh app and13-interface world remain unchanged.
Source21 and local fake-server62 checks pass across24 outcomes, including
wrong-context, transport-close and partial-response-close failures. A review
correction retains received partial bytes and the original read error; the first
fake fixture's legal close-delimited EOF failure stays in preparation history.
These are harness checks, not target results or guest fault injection.

The [Root wrapper/request/CLI](tests/node-compat/frameworks/nextjs/next-app-request-isolation-root-results-v1/README.md)
also pass independent review. Actual `--prepare-only` exits0 with requested9ebfa4;
the first real launch invocation exits2 at the1GiB gate with761,180,160 bytes,
before creating its request, monitor, output or world receipt. All seven
declared absent paths are checked and raw outputs retained. No new real Next
or guest request ran, and the six cases remain unexecuted. The shared helper
is also selected by the matched pinned-Node differential path. Client overlap
does not prove same-Store concurrency; possible instance-local cache-counter
effects must remain failures under the unchanged cache gate.
The reviewed [StockV6 Source](tests/node-compat/frameworks/nextjs/browser-hydration-matched-host-candidate-v6/README.md)
bccce053 now consumes that one V8 helper, retaining normal CDP and the original
V4 contract/300s owner with a fresh V6 namespace. Source29 wiring/15 namespace
checks and independent Source/request/CLI reviews pass. Actual control
`--prepare-only` exits0 with request6eb140fa, mode0600 in owned0700 parent; both
server/monitor outputs are absent. At preparation770,953,216 bytes are free;
launch is not attempted. The two reusable commands now prepare the exact same
six observable application cases for future differential checks; neither arm
has executed them against real Next yet.

The separate [generator-only producer](tests/node-compat/frameworks/nextjs/next-native-portable-generator-check-v1/README.md)
38cbd788 and Rootgrant0669f9c9 passed Source/pre-action review. Its **first actual
ten Node --check commands all pass**, raw0/clean with empty stderr and900s
outer0. Resultf9e63c04/970943 preserves435 native/825 physical/171 directory
and tool bookends. Only sibling evidence directories were written. Admission
426,127,360 bytes clears its separate64MiB small-scope start gate; total complete
evidence plus final receipt is below8MiB, with no truncation or continuous
limit claim. The [99-record DATA review](tests/node-compat/frameworks/nextjs/next-native-portable-generator-root-results-v1/actual-review/README.md)
984e7313/988 passes Root readback and independent current audit. This is a
fresh source-generation proof, not CMake/Cargo/compiler/engine/guest execution,
a native build, ABI validation, clean-machine reproduction or promotion.
The first V5 abort and later old-app CDP positives remain separate. Fresh-app
wasmCloud admission [SourceV4](tests/node-compat/frameworks/nextjs/wasmcloud-cold-candidate-v4/README.md)
is now sealed8236614e/4170 and independently reviewed, with31 inert checks,
four grammar checks and AST passing. Its policy comes from the pinned host's
actual direct-P2 volume path: exact425 source directories plus root426 owned,
no added app path and a separate0700 host cache/preopen. The existing Wasmtime
actor's declared empty-mountpoint policy stays unchanged and is not a universal
host requirement. Root rehashed all26 payloads. Cold8/readiness60s/600s
ownership/SIGINT gates, component1c31 and standard13-interface world stay exact.
The [first actual coldV4 trial](tests/node-compat/frameworks/nextjs/wasmcloud-cold-root-results-v4/README.md)
now passes all8 requests, including three-chunk streaming(shell0/ready1), on
stock wasmCloud2.11.0/embedded Wasmtime48.0.7. Result6d959823/47822 and outer
9497ad32/1723 finish raw0/clean with source/copy/world protected. Config/dev
exit0, no extra HTTP readiness probes or retries, and SIGINT/owned shutdown
pass. Launch admission recorded1,521,770,496 bytes above1GiB. Portable actual
The [portable cold DATA review](tests/node-compat/frameworks/nextjs/wasmcloud-cold-root-results-v4/actual-review/README.md)
retains175 exact files and passes Root readback;200 selected current references
and both2,181-file trees pass the independent current audit. This finite cold8 result does not establish cache
persistence, browser/retained24+2, private Store identity or general descriptor
rights. The first fresh matched Node, Wasmtime and cold second-host gates have
now run; earlier preparation statements retain their original scopes.

The new read-only browser observer is Source-reviewed: seven bounded CDP event
types plus requestfailed-aware observation completion, with unchanged actions,
asset pins,20-second limits,500ms drain and strict error gate.18 inert tests pass.
The matched Node/native diagnostic trial now passes as described above;
the earlier failedV5 remains failed and its cause remains open.

Full Next entryV5 integration is implemented and constructed. It preserves all
six facades and the application, replaces only the WASI adapter with the audited
observed-I/O policy, and keeps the standard13-interface world unchanged. The
unchanged24+2 runner ran under whole-world/native artifact guards; the strict
failure described above keeps this candidate outside the passing checkpoint.
Earlier811–996MiB capacity holds ended
when free space rose above the unchanged1,024MiB construction start guard; both
constructors then ran. No proof or shared binary was deleted and no guard was
lowered. Temporary disk peak remains unmeasured.

The prior24/24 HTTP,1/2 browser failure remains preserved. Its counter click
preceded client scripts by about2.15s. The new worker waits for load and the
actual React handler before the same user click/submit, within the same20s
limits. It does not invoke handlers directly, change application code, relax
errors or filter cancellations. The earlier action abort remains a historical
failure; this successful run does not retrospectively reclassify it.

The classic Readable Request BodyInit facade and native-snapshot-backed CJS
AsyncResource constructor/runInAsyncScope now work in the actual component:
JSON POST and public assets pass. Host differentials22+16 pass; explicit IDs,
hooks/destroy/bind/options and old ESM named-binding limits remain. The next
step is to retain the passing regression and promote the bounded changes
through ordinary native component/API checks. See the [milestone report](docs/node-compat/nextjs-wasm-milestone-2026-11-06.md)
for repeat commands, exact artifacts and outstanding work. This is an
experimental profile; foundations-v13 remains the accepted production
checkpoint. Full Node/Buffer support, AOT, performance gains and wasmCloud P2
retained-instance deployment are not established.

**Earlier startup history (retained):** The experimental engine now links, and
both real JavaScript component entries construct and validate with exactly13
selected standard WASI0.2.10 imports. The profile globals prelude fixes the first
actual Next startup failure (`global` missing). The second actual attempt then
fails parsing Unicode property regex syntax in Next's Zod dependency. All23
initial HTTP cases return500; missing SSR action markup blocks the24th action
POST, cache comparison, strict-stream and browser stages. No successful Next
contract is claimed from that older run. The Intl-enabled V7 engine now builds;
the current full-app result and remaining blockers are recorded below.
Generic crypto/API expansion and cost work stay behind this gate.

**Earlier V7 baseline:** the rebuilt V7 engine runs the unchanged
Next application and passes11 of24 HTTP cases, including home/nested/dynamic
SSR, query, action-form SSR, client-counter SSR, completed Suspense, redirects
and404s. The run remains raw1/unaccepted. JSON responses fail in the response
pipe; public assets hit the bounded `fs.createReadStream.root` refusal; a
Buffer/string-decoder Unicode assertion and a POST Buffer input refusal also
appear. Cache parsing stops subsequent streaming/browser checks. All24 HTTP
requests are retained, shutdown is clean and original/read-only app inputs are
preserved. Fix these demonstrated paths before unrelated module expansion.

The new isolated Unicode component passes all36 selected semantic records
(12 cases across three requests), including Unicode properties and Kelvin
folding, against Node22.14: raw0, strict paritytrue, counters1,2,3 and clean
owned shutdown. Dependency controls also pass all48 records across GET/GET/POST.
Stack controls match9 of12 records: lazy hooks, descriptors, thrown identity
and depd location extraction now work; the remaining three differences are
an anonymous frame name reported as a SpiderMonkey inferred string versus
Node's null. The strict stack run remains raw1/parityfalse. The
full-app failure is preserved under
`next-wasmtime-deployment-enginee7baa5a9-intl-stack-v1`; a separate diagnostic
entry will report own-data error causes/input shapes while retaining thrown
identity. That diagnostic confirms `pipeTo()` rejects Next's AbortSignal.
The decoder assertion's actual value is correct `€`, while the expected CJS
literal appears as UTF8 bytes decoded as Latin1; source decoding needs
isolation before attributing this to Buffer. The rejected POST value is a
native ArrayBuffer view, with its exact view type still being diagnosed.
Diagnostic function wrappers are not a production acceptance claim.

DiagnosticV2 narrows those two issues further: the POST input's intrinsic brand
is Uint8Array but its prototype differs from the captured constructor; backing
is an ordinary ArrayBuffer. The supplied CommonJS compile source contains the
correct U+20AC. The exact guest fork's `FunctionCompiler::addFunctionBody` passes
`SourceText<Utf8Unit>::get()` to the Latin1 `StringBuilder::append(char*)`
overload. A UTF16 native compiler input is being prepared, alongside a bounded
guest dispatch for testing. No application literals will be rewritten.

Checkpoint `0e97b1d1` is committed and pushed. The independent native-build,
four-constructor and five-runtime DATA readers pass. The latter's reader
validates retained selected projections and recorded input-preservation facts;
it does not execute a fresh guest or independently recreate historical
bookends. Its [scope and future-check instructions](tests/node-compat/frameworks/nextjs/next-intl-runtime-root-results-v1/README.md)
keep the11/24 Next result and9/12 stack result explicitly failed.

The first combined entry-facade experiment constructs/validates successfully
but regresses startup:23/23 initial HTTP cases fail because the nonASCII
`Function` fallback gives send's real frames eval provenance, and its depd
path requests the explicitly unsupported `getEvalOrigin`. That failed
prototype remains unchanged; no provenance or application-source workaround
will be counted as success. The native UTF16 module-compiler afterimage was then
prepared. A separate limited one-object rebuild/relink was prepared from
the actual V7 CMake recipe, reusing audited archives/tools read-only. It has its
own proposed1GiB start/800MiB sampled floor and<100MiB persistent-output budget;
temporary peak remains unmeasured. The full builder's2/3GiB guard is unchanged.
Space subsequently increases enough for the limited operation. The actual
build now passes five phases0/clean plus Root0: one fresh frontend,1,046
preauthenticated dependency paths,14 unchanged node archive members, and
matching core import/export function signatures.80 baseline compile rows/79
unchanged and a separate embedding are ancestry; no80-fresh claim is made.
Engine4623640b is31,324,051 bytes, metadata726d69cf. Independent current1,949-row/
13-tree readback and portable322-file DATA review pass. Minimum sampled free
space is1,309,847,552 bytes; final private output70,761,705 bytes. Temporary peak
remains unproved.

The first [Intl-enabled guest library CI build](https://github.com/nemonicon/StarlingMonkey/actions/runs/42272037547)
now succeeds at pushed commit`dc7bad5c`:17 raw0 owned phases, baseFirefox9dab,
library archive2508af52/222,772,017 bytes. Its complete Actions ZIP is downloaded
and matches published ae81c73e/227,191,494 bytes. This is C++/ICU library evidence,
not successful Next execution. Its artifact closure review now passes; local
capacity is no longer blocking that guest-library prerequisite.

Actual Cargo resolution/vendor/offline-locked metadata now passes with84
packages, all49 old versions preserved.76 external packages/2,278 files/
35,510,599 bytes pass checksums; Mozilla's patched Bidi Rust/manifest match.
First seed's smallvec101 failure remains unchanged. A separate old-only offline
control captures the feature differences: old Serde adds derive/serde_derive,
Smallvec adds union, Syn adds full, and serde_derive becomes selected. The
control's erroneous49-lock==metadata-count assertion stays failed; its actual
Cargo command is0/clean and separate DATA reconciliation records48 old versus84
new metadata nodes. The subsequent V7 engine build now compiles and links this
single aggregate; ordinary guest behavior remains a separate gate.

The [actual structured-stack component probe](tests/node-compat/frameworks/nextjs/stacktrace-probe-root-results-v1/actual-review/README.md)
confirms another startup requirement: three HTTP200 responses/counters1,2,3,
all12 records differ from Node; hooks never run and exact send/depd throws
`e.getFileName is not a function`. The experiment remains raw1/parityfalse,
with clean owned shutdown and preserved inputs; Root's portable DATA reader
passes. The proposed native capture/facade passes64 host checks after three
retained bad-provider failures. SavedFrame lacks truthful eval provenance, so
a sealed four-file **guest SpiderMonkey** patch adds a new API;112 Source/model
checks and a16-case actual Node oracle pass. The subsequent opt-in CI and V7
engine builds compile the new API with coherent patched headers/library.
Ordinary component differentials remain pending. No host modification is
introduced. Complete V8 Error/CallSite semantics are not claimed.

That [patched CI run42281671898](https://github.com/nemonicon/StarlingMonkey/actions/runs/42281671898)
now succeeds at pushed commit`bb2526b7`:22 raw0 owned phases, exact9dab plus
patch1a571a89. ZIPabbbd377/227,965,139 bytes matches GitHub; compressed library
e1f1e208/222,806,343 bytes streams directly into the checked596-file distribution.
Libraryca04fe5e is637,175,630 bytes and installed API headerfc3b58f8 matches the
sealed afterimage exactly. The new guest API is compiled; its runtime behavior
is not yet admitted. Raw result, four-file source checks and full diff remain.

The five-file [V7 source graft](tests/node-compat/frameworks/nextjs/next-intl-native-profile-v1/README.md)
is composed as435 native+embedding3, with one extra Cargo template extending
support386→387. All10 installed canonical generators pass. The
[disk-frugal V4 caller](tests/node-compat/frameworks/nextjs/next-native-build-candidate-v4/README.md)
passes69 Source/model checks, including real CMake branch tests. It supplies an
explicit direct-Rust path because Corrosion otherwise invokes Rustup even with
toolchain resolution disabled. Root checked10 shared read-only inventories and
3,542 descriptors. The fresh full native build in
`next-native-intl-build-v1` now passes all six owned phases raw0/clean, with
80 fresh native compile rows and one separate embedding compile. It uses the
exact84-package lock/six roots, patched libraryca04fe5e and headerfc3b58f8.
The resulting engine is `e7baa5a9…`,31,324,485 bytes; metadata is
`cb473c72…`. Independent actual-build review is in progress. Root issued four
INIT-only construction authorities for Unicode, stack, dependency and full
Next entries. All four now construct, validate and audit successfully with
exactly13 selected standard0.2.10 imports/incoming-handler only. Unicode parity
passes, dependency48/48 passes, stack9/12 with a named-frame deviation; the full24+2 Next contract remains
outstanding. No engine or guest is executed by the native builder itself.

The native dependency component now [passes all16 controls on GET, GET and
POST](tests/node-compat/frameworks/nextjs/dependencies-wasmtime-root-results-v3/actual-review/README.md):48 actual records, HTTP200 each, POST21 bytes, clean0 owned shutdown and
original/read-only app preserved. The initial ALS failure was an incorrect
oracle: pinned default Node22.14 disables the instance inside `exit()`. The
corrected test verifies snapshot/bind capture and caller restoration from a
distinct enabled store. A second failure exposed the real WASI binding's own
`ComponentError.payload` wrapper around normal EOF; the bounded adapter fix now
passes actual POST. Earlier failures remain unchanged. These controls do not
prove the full Next app, exhaustive GC/snapshot/reset or same-instance identity.

Actual SM147 headers have Intl disabled; matching native parser branches reject
Unicode property classes. Next's unchanged dependency contains
`[$_\p{ID_Start}][$\u200c\u200d\p{ID_Continue}]*` with `u`.
The actual12-case guest/Node differential captures all36 records over three
HTTP200 responses, with guest counters1,2,3. Seven property-expression cases
reject per request (21 SyntaxErrors). It also finds a Kelvin-sign ignore-case
mismatch on all three calls; the comparator correctly remains failed and the
extra differences are [retained with the second actual Next failure](tests/node-compat/frameworks/nextjs/regexp-unicode-probe-root-results-v1/actual-review/README.md).
Basic Unicode/ASCII and invalid-property controls match. The
[guest Intl build plan](docs/node-compat/nextjs-intl-build-plan.md) pins fork
commit`9dab3d6f`, bundled ICU78.1 and the required ICU4X/unicode-bidi single-Rust-
aggregate integration. Only about3.2GiB is free; a request for20GiB build headroom
or another writable volume is pending. Heavy source fetch/build has not started.

The [local Intl tool preflight](tests/node-compat/frameworks/nextjs/spidermonkey-intl-tool-preflight-v1/README.md)
now records 17 successful read-only tool/version queries. Installed cbindgen
0.29.0 is below the exact fork's required 0.29.1; Make3.81, SDK27 and Python3.12
meet the inspected prerequisites. The [manual CI library build](tests/node-compat/frameworks/nextjs/spidermonkey-intl-build-v1/README.md)
provides a capacity workaround on the already enabled public fork, using the
existing CMake module with explicit source/Intl options. Six actual selection
tests pass, including rejection of no-Intl headers, conflicting source inputs
and stale cached distributions/wrong revisions. SDK30, Rust1.88, cbindgen0.29.1,
private build state, a20GiB start/4GiB stop policy and artifact-only outputs are
specified. It has not yet compiled SpiderMonkey or run a guest. The existing
release workflow, WASI interfaces and unchanged Next success gates remain.
Commit `dc7bad5c` is pushed; its manual [CI run42272037547](https://github.com/nemonicon/StarlingMonkey/actions/runs/42272037547)
is in progress at exactly `dc7bad5c36306368fd8a2816136f02f959aed0ee`.
An abbreviated-SHA dispatch was rejected422 without creating a run; dispatch
by `main` succeeded and the returned full commit identity was checked.
The first run has a120-minute job ceiling; the next workflow version raises
that ceiling to210 minutes to accommodate the sum of bounded phase deadlines.
Actual successful compilation, ICU archive closure, new Rust lock/vendor,
full engine link and unchanged Next runtime contract are still outstanding.

The [single Rust aggregate companion](docs/node-compat/nextjs-intl-build-plan/README.md)
contains uncompiled templates for the two added FFI crates and three required
root overrides.59 static Source/TOML checks pass under Python3.12; neither old
49-package lock is asserted to be the combined graph. The exact four FFI source
directories were acquired separately within a32MiB ceiling:1,127 files and
11,364,714 bytes, all rooted in the exact commit's26 verified Git trees. Every
blob's Git SHA1/SHA256, size, mode and complete membership match; Root repeated
the complete local-file check. The [manifest](tests/node-compat/frameworks/nextjs/spidermonkey-intl-build-v1/ffi-source-manifest.json)
records the raw-GitHub fallback for binary/large connector responses. No root
Cargo workspace was injected into this reduced source layout. This permits
bounded Cargo-only resolution while CI builds the larger C++ library; actual
resolution/vendor/offline checks remain pending.

The [startup source audit](tests/node-compat/frameworks/nextjs/spidermonkey-intl-build-v1/next-startup-audit.md)
predicts another immediate frontier: bundled send/depd expects lazy V8
structured stack traces, whereas exact SM147's captureStackTrace installs an
eager string. An isolated ordinary guest probe is being prepared; this is not
yet a measured Next failure or an implemented fix. The audit corrects an early
inode hypothesis: send's instanceof Stats branch should accept the actual
guest Stats objects, so no synthetic inode or speculative FS expansion is
justified. Actual Next success gates remain unchanged.

Current native Source candidate is435 inputs/embedding3, V6. Its V5 base includes the
bounded Readable.toWeb extension, ALS's real strict-definition guard, three
authenticated existing compile headers and Performance's actual include-path
correction. V5 passed eight installed generators. An independent read-only
review confirmed its exact435 files, unchanged81 C/C++ bodies and three embedding
files relative to V4. The [closure audit](tests/node-compat/frameworks/nextjs/next-native-header-closure-audit-v1/README.md)
checks1,400 actual old dependencies,80 compile rows and661 quoted includes.
The fresh fourth native build **passes** with386 support inputs. Engine
`84d70a77` is10,255,733 bytes; all six owned phases finish0/clean and2,173
protected inputs remain unchanged. Exact compressed metadata, build result,
Source composition and phase logs are [retained](tests/node-compat/frameworks/nextjs/next-native-build-v3-source435-v5-root-results/actual/observation.json).
This is the first linked experimental Next engine. Component construction,
complete native runtime semantics and successful Next execution remain unverified. The first
dependency component attempt fails before Wizer/engine entry: direct
ComponentizeJS leaves its parser shim's filesystem preopens empty, so the
existing absolute WIT directory is invisible (errno44). Raw failure and clean
terminal are preserved. A caller successor will use the installed documented
`_setPreopens` API for that exact WIT directory only; the runtime world stays
unchanged. That V2 caller now reaches Wizer and exposes a genuine INIT defect:
the FS generated factory spreads non-enumerable native dependency fields away,
so `Readable` is undefined. The failed old engine/attempt stays preserved.

[FS V4](tests/node-compat/foundation-fs/next-fs-candidate-v4/README.md) fixes the
generator and generated header with four explicit dependency transfers. Nine
native-shaped descriptor regressions and41 FS host cases pass. V6 overlays only
those two files on immutable V5: same435 paths, C++ bodies, manifests and flags.
All nine installed generators pass, now including FS. WORK5's full build passes:
engine `c2bff940`,10,255,826 bytes, six clean0 phases and2,631 protected inputs
unchanged. Its actual Wizer attempt passes builtin installation, then fails to
find the top-level script. Source inspection identifies ComponentizeJS's raw
string path-slicing bug when TMPDIR is under the caller cwd. A caller successor
will run from a held directory outside its owned temporary output; no engine
rebuild or world change is needed. That caller V3 succeeds: dependency component
`5526fccd` is15,824,544 bytes; real Next component `f71cf62f` is15,809,047 bytes.
Both have13 exact0.2.10 imports and only incoming-handler exported. All three
construction/validation phases finish0/clean per entry. Their deployed failures
and the next globals/probe corrections are summarized above.

To provide build space, only duplicate SDK/Rust installations in failed WORK1–3
were cleaned. Their3,252 retained source/log/metadata files match before/after;
the [cleanup receipt](tests/node-compat/frameworks/nextjs/next-native-build-v3-source435-v5-root-results/failed-tool-cache-cleanup.json)
explicitly records which historical tool paths no longer exist. The successful
engine, its complete WORK4 and canonical toolchains remain available.

Three failed attempts stay preserved: missing Rust `.in` support templates;
ALS checking an unset CMake variable instead of the actual strict compile
definition; then successful configuration but compilation failing at21/120 on
`sequence.hpp`. The complete header audit additionally found existing `wizer.h`
and `rust-encoding.h` omissions and the Performance target include-path defect.
The corrected headers are exact reviewed donor bytes; generation of their
prebuilt FFI content is not claimed. Failed WORKs and raw process results remain.

The fresh [matched host controls](tests/node-compat/frameworks/nextjs/browser-phase-matched-host-root-results-v1/independent-data-review-v1/results.json)
both finish0 clean: selected guest-JS facades and stock Node each pass24/24 HTTP,
cache1→2, incremental Suspense with five chunks/shell0/ready2 and2/2 error-free
browser checks. All14 browser responses per arm finish before context closure.
The earlier aborted `/actions` fetch does not recur; its cause remains unresolved
and the failed run is retained. Gates and profile behavior were not relaxed.

The selective Preview1-to-P2 **guest adapter** is now published at`d30ade5b`,
49,672 bytes, after an actual fresh native CLI build and one pruning invocation.
Core validation and a complete93-body/seven-stub audit pass; stdout/stderr,
filesystem and clocks remain, initial stdin is genuinely Badfd and terminal
queries are non-TTY. No fake resource handles or host modifications are added.
The [retained evidence](tests/node-compat/frameworks/nextjs/next-preview1-adapter-publish-v1/root-result.json)
is supplemented by an actual small C-component construction: all twelve emitted
interfaces are selected standard0.2.10, with no external Preview1 or custom
interface. The unused outgoing-handler is correctly absent. The control retains
and exercises real Preview1 syscall imports through this adapter. Its stock
Wasmtime [deployment](tests/node-compat/host-capabilities/next-adapter-probe-v1/README.md)
passes three HTTP requests with retained counters1,2,3:
stdout/stderr, non-readable stdin, app-file reads, clocks, entropy and P2/cache
controls all pass. All six construction/validation commands and the one host
run finish cleanly; raw responses and import evidence are retained for replay.
This is not a SpiderMonkey or Next result.

**Target correction:** pinned wasmCloud2.11 P2 HTTP creates a fresh store for
every request even in normal workloads with pool settings. The
[primary-source finding](tests/node-compat/host-capabilities/wasmcloud-warm-candidate-v1/README.md)
makes retained Next server/cache state **unavailable on that path** under the
WASI0.2.x/no-host-modification constraints. The earlier three cold counters are
consistent with this. Wasmtime's tested explicit reuse remains the viable
stateful target. wasmCloud instantiation/cold-request checks remain useful;
they cannot establish the original retained-state success contract.

The [combined Source generation](tests/node-compat/frameworks/nextjs/native-profile-candidate-v1/README.md)
now contains430 native-policy inputs plus three embedding inputs. All eight
installed-generator checks and all13 SDK syntax frontends pass. The latter
include real HTTP/import registrations, VM, streaming zlib, Module/P2 startup
and context/timer integration;13,508 dependency observations/1,204 unique files
match authenticated inputs. No engine or guest was executed by these checks.
Actual CMake support-copy closure and a fresh build runner are being prepared.

The [stronger full Next host control](tests/node-compat/frameworks/nextjs/native-profile-host-v1-root-results/independent-data-review-v1/results.json)
uses the real guest-JS classic streams, Events, decoder, candidate Buffer and
same exported HTTP message classes. It finishes raw1 clean:19/24 HTTP checks,
cache1→2 and both browser interactions pass. Actual SSR/query/action-result/
Suspense calls fail on unsupported `Readable.toWeb`; the action POST also fails.
The stream contains only `BRIDGE_FAILURE`, with no shell/ready markers. This
exposes a required adapter hidden by earlier controls' stock Node streams.
The exact failures, bodies, chunks, browser results and monitor are retained;
they are **host evidence, not Next-in-Wasm evidence**. A bounded stream adapter
now takes priority before the first complete build.

The raw [future component entries](tests/node-compat/frameworks/nextjs/next-component-candidate-v1/README.md)
are prepared for genuine deployed Next loading from`/app`, neutral readiness,
fresh request ownership and explicitly configured origin. Models pass127 checks,
including ownership on readiness/native-entry failure. Actual construction stays
blocked on a compatible guest Preview1-to-P2 adapter: the old clock-only adapter
stubs stdio and cannot supply this profile. Thirteen standard0.2.10 interfaces
are selected; no extra imports, version relabeling or host modification is admitted.

The direct-P2 [FS V3](tests/node-compat/foundation-fs/next-fs-candidate-v3/README.md)
now has explicit sync/callback/promises exports, real ReadStream state, safe
numeric constant inspection and41 host cases. Three actual SDK frontends pass;
[portable raw evidence](tests/node-compat/foundation-fs/next-fs-sdk-root-results-v1/README.md)
retains3,080 postcompile dependency records. These are not runtime ownership,
GC, nested-mount or rights proofs. Next still needs its actual `/app/.next/cache`
layout and any additional writes validated with real preopens.

[Native ALS V3](tests/node-compat/async-context/native-als-candidate-v3/README.md)
now passes all13 actual SDK syntax commands, raw0/clean with unchanged protected
inputs. V2's11 failures are retained: a nonexistent SpiderMonkey handle constant
and an unrooted report-global argument. V3 fixes those exact APIs. Native Promise,
await, timer/tick and concurrent-request behavior is still unexecuted. The join
must retain V3's corrected default while adding Timer's virtual methods.

The held startup/timer/Buffer/RNG Sources now cover actual Next demand with exact
versioned exports. Startup has195 host cases; timers46; Buffer134; RuntimeOnly
RNG46. The full Buffer host control passes24HTTP+2browser, but other host modules
still emit Node Buffers, so it does not establish complete guest Buffer demand.
The startup successor corrects native Performance's Unix epoch and precision;
its six focused SDK frontend checks have been authorized and are pending results.

[Streaming zlib Source](tests/node-compat/foundation-zlib/next-streaming-candidate-v1/README.md)
is sealed at`10947d2a`:28 host cases cover actual Gzip/Deflate members, flush,
backpressure, pause/destroy and26 balanced adapter opens/closes. Native contexts
remain uncompiled. Its alternative manifest replaces the old sync-only zlib
selection when enabled; it must not create duplicate node:zlib declarations.

Root's HTTP module/private hosting factory now passes62 focused host checks;
the explicit tty/inspector/v8/dns-promises surfaces pass422 binding/failure checks.
These are real finite guest factories and uncompiled native registrations.
Unsupported operations throw on call/new; inspection remains safe. The standard
HTTP adapter enters the real native fresh-request boundary before creating any
body/Request, and shared readiness is prepared in a neutral server resource.
The existing Node bridge control remains distinct from native context execution.

Actual Next client-reference manifests require `vm.runInNewContext`; an import
stub would break rendering. A bounded real SpiderMonkey realm/evaluation Source
is being finalized with19 actual manifest oracles and161 host data/model checks.
Full Contextify semantics, asynchronous sandbox mutation, security isolation and
timeouts are not claimed. Root is composing these candidates from frozen9aec,
preserving old crypto/zlib/timer changes and producing fresh Source/build records
instead of casting old metadata counts.

Previous goal turn: **progress**. Checkpoint `5fe139b7` was committed and pushed;
the checkout and origin/main matched before this continuation. The active target
remains the full unchanged Next app running in Wasm, with all original contracts.

New real deployment evidence now exists in the
[standard-WASI probe](tests/node-compat/host-capabilities/probe-v1/results/summary.json).
The93,929-byte C component `32830d39` validates and imports exactly ten selected
standard0.2.10 interfaces: CLI environment, wall/monotonic clocks, filesystem
types/preopens, HTTP types, IO error/poll/streams and secure random. Its only
component export is incoming-handler; no adapter or Preview1 import is used.
This is a genuine Wasm guest deployment control, **not StarlingMonkey or Next**.

Stock Wasmtime42.0.1 serves six successful responses: default lifetime counters
`[1,1,1]`; explicit `--max-instance-reuse-count32 --idle-instance-timeout60s`
gives`[1,2,3]`. Official wasmCloud2.11.0 wash dev serves three successes with
`[1,1,1]`. Both pass selected env, fresh RNG samples, wall/monotonic+poll, app
file read and denied create, and cache create/write/read/link/EEXIST7/rename/
unlink. Both report initial-cwd absent and preopen flags33. Read-only app tests
use owned Unix555/444 modes; narrowed per-preopen WASI rights are **not** proved.
No host source/binary was modified. All three host modes stop raw0 clean.

Pinned primary source confirms Wasmtime's supported reuse options and wasmCloud's
warm-instance policy. The pinned wash dev main component hardcodes ephemeral
limits; normal warm-workload deployment remains a separate unexecuted gate.
Startup therefore explicitly initializes the shared logical cwd to`/app` after
deployed bootstrap. The first probe compile failed on an invented tuple-free
helper and was corrected to the actual list-free API. The second built/validated
successfully but its whole-text Preview1 assertion matched debug strings; the
corrected audit checks actual import declarations. Earlier attempts stay failed.

Current priority, at the user's request: **get the actual comprehensive Next.js
application running successfully in Wasm**. The previous goal turn made progress
and pushed `4a3c6a7b`; the current checkout was clean before this work. No clock
component construction or further generic crypto integration has been issued.
Those follow-ons move behind dependencies needed by the Next app.

The Next success gate remains the complete existing fixture: all24 HTTP/action
contracts, cache reuse/invalidation, real client hydration/click and form action,
public/static assets, request cookies/headers, dynamic rendering, filesystem/SHA
route and streamed Suspense. A generated bundle, Node-host result or isolated
React render does not satisfy that gate. Original failures remain regression
baselines until a genuine new guest artifact passes them.

Dependency order is now: fix actual packaging/resolution defects; implement
real CommonJS/createRequire/cache/chunk loading and required process/URL APIs;
provide explicitly selected standard filesystem/RNG/HTTP capabilities; connect
Next's real custom-server router to a Node-shaped request/response bridge;
integrate correct promise/timer/I/O/tick AsyncLocalStorage; build a new guest
profile and run the full application contracts on real components. Native
Hash/Hmac work proceeds only for required app crypto operations. Existing
production foundations-v13 remains accepted; new app/runtime code is experimental.

One packaging defect is fixed: the optional package bundler now resolves
asset-looking names before classifying targets, allowing genuine Next
`.node.js` sources while refusing actual native addons. All44 host checks pass;
the [new diagnostic](tests/node-compat/frameworks/nextjs/standalone-bundler-diagnostic-v1/README.md)
retains14 earlier bundle attempts and exact traced-versus-broad graph results.
Standalone's `createRequire`, computed webpack chunks and missing native modules
remain actual blockers; no permissive diagnostic is admitted as a guest bundle.

The [HTTP message bridge candidate](tests/node-compat/frameworks/nextjs/http-bridge-candidate-v1/bridge.mjs)
now runs the actual unmodified Next custom-server router on host Node, through
Web Request/Response messages. First attempt95089 finishes1 with22 failed HTTP
observations: null-prototype request headers and missing `_implicitHeader`
break real Next/compression. Its exact executed sources/raw output are retained.
The corrected run96179 finishes0 clean:24/24 contracts pass, including a real
build-derived action POST, filesystem/SHA and cache generation1→2. Five actual
stream chunks put shell in0 and ready in2. Its result `2ad0232c`/18,212 bytes and
monitor `974f7b92` remain external; eighteen host bridge checks also pass.
The third run97040 finishes0 clean with24/24 HTTP and2/2 browser interactions:
actual hydrated counter0→1 and a real form-action POST/redirect pass with no
browser or network errors. Five streamed chunks retain shell0/ready2 and cache
generation1→2. [Portable results](tests/node-compat/frameworks/nextjs/http-bridge-candidate-v1/results/summary.json)
retain all three runs, including the failed first attempt, raw bodies/chunks,
screenshots and monitors:108 copied files/275,808 bytes.
This is **host message-bridge validation, not Wasm execution**. Guest native
loader/FS/process/context integration remains outstanding.

The [Next.js priority roadmap](docs/node-compat/nextjs-priority-roadmap.md) is
the active dependency order and full-app success contract. Native CommonJS
Source is sealed with42 host cases but remains uncompiled; FS and actual native
ALS integration are in progress. Bounded native Buffer.concat is now an explicit
Next blocker. Existing one-shot zlib evidence does not implement Next's streaming
gzip path. These genuine runtime needs take precedence over generic diagnostics.
The standard WASI HTTP adapter now has13 host ownership checks, including status
failure before response transfer, EOF/cancellation, write limits and stream-error
resource disposal. Its WIT and guest smoke are uncompiled. An initial fake-resource
test harness method-name collision was corrected; it was not a native failure.

The [full Module-core host control](tests/node-compat/frameworks/nextjs/http-bridge-candidate-v1/module-results/summary.json)
now finishes0 clean at2073, with24/24 HTTP,2/2 browser, cache1→2 and incremental
Suspense. All application CommonJS loads use the actual candidate core, compiling
406 JS files and caching412 modules. Test-only Node FS/compiler/builtins/globals
remain explicit; this is not native/guest evidence. Its47 portable copied files
retain198,961 bytes. Root's [Module Source review](tests/node-compat/foundation-module/independent-source-review-v1/README.md)
checks76 candidate payloads,363 prospective hashes and six reversible derivations,
but **holds** the sealed v1: its installed generator needs an inventory JSON file
missing from the prospective native cut. A compact v2 successor is in progress.

The [Buffer.concat Source](tests/node-compat/buffer-concat-candidate-v1/README.md)
is now sealed, index `1c7b431e`: actual rooted native memcpy implementation and
precise facade/manifest/generated afterimages, with38 pinned Node differentials
and12 profile/generated checks passed. Its16MiB/fixed-backing/dense-list subset
remains uncompiled/unapplied. No new native build or component ran in this phase.

The [Module v2 inventory fix](tests/node-compat/foundation-module/node-module-candidate-v2/README.md)
is sealed at `c69350e3`; [Root Source review](tests/node-compat/foundation-module/independent-source-review-v1/results-v2.json)
passes its corrected364=351+6+7 cut, explicit versioned inventory and whole-input
digest. The original v1 HOLD remains intact. Actual new [Module kernel SDK syntax](tests/node-compat/foundation-module/module-sdk-v1/README.md)
finishes5054/raw0 with empty streams and1045 dependency hashes. Only that kernel
and proposed declaration headers were checked; registration/link/guest are open.

The actual [Buffer.concat SDK frontend](tests/node-compat/buffer-concat-sdk-v1/README.md)
also finishes4005/raw0 clean with empty streams and1020 dependency hashes. Its
Root driver exits1 afterwards on a reporting comprehension NameError. The exact
executed driver is retained; a separate read-only collector verifies recorded
source/compiler/database bookends and raw output without replaying the compiler.
Header hashes in both checks are captured after compilation, not a full-SDK
preservation proof. No object, new engine or guest ran.

Filesystem and ALS are deliberately checkpointed as **unfinished drafts**.
[FS status](tests/node-compat/foundation-fs/next-fs-candidate-v1/checkpoint-status.json)
records an uncompiled direct-P2 native provider, including private stream handles;
the public facade, actual ReadStream/callback delivery, registration/CMake and
real FS differentials remain unwritten. Two error-preservation paths need fixes.
[ALS status](tests/node-compat/async-context/native-als-candidate-v1/source-status.json)
records24 afterimages,14 existing-file derivations/41 reversible edits and53
synchronous models. Native Promise/task/tick/fresh-request code exists, but final
cross-file audits, request-owner tests, metadata/producer integration, frontend,
link and actual async propagation remain open. Neither draft has Source PASS
or runtime authority; current production C++ and accepted engines are unchanged.

[Independent bridge review](tests/node-compat/frameworks/nextjs/http-bridge-independent-review-v1/README.md)
passes155 copied files/474,769 bytes across all four actual host attempts and
their complete fixed outcomes. The retained checker now rejects empty/missing
runs, a disabled browser gate and relabeling the first failure; a copied positive
control plus all four negatives pass. The current runner's top-level boolean only
requires complete streamed output; the stricter retained checker also requires
ready after shell. All three actual successes meet that stricter condition, but
future live/component acceptance must enforce it directly. Native/WASI/ALS/TLS
scope remains unchanged. The early deployment gate now explicitly requires real
filesystem-rights and instance-lifetime probes before the combined engine build;
earlier stock-host counters1 prove neither reuse nor the new filesystem setup.

The [actual Next startup/API inventory](tests/node-compat/frameworks/nextjs/startup-api-demand-v1/README.md)
parses all406 loaded JS inputs/4,439,412 bytes with pinned Rolldown/Oxc: no parse
errors,40 observed builtin-load spellings,78 statically resolved API paths and56
exact source citations. Nine full Node22 export inventories are retained. Method
calls and conditional branches are **source demand, not measured invocations**.
This tightens the next work to mutable process/env/cwd and truthful OS data;
genuine nextTick/Immediate ordering and mutable timer modules; URL formatting/
file helpers; HTTP Agents/backpressure; and streaming gzip/deflate cleanup.
No attributable node:url.parse call or Brotli token was found in the examined
cut; broader support is deferred. Conditional cache serialization also needs
Buffer base64 support. The build volume now reports about12GiB free; lack of
space is no longer the immediate blocker. Native integration is still blocked
by unfinished runtime dependencies, not claimed complete.

[Independent Buffer.concat Source/SDK review](tests/node-compat/buffer-concat-independent-review-v1/README.md)
passes at `f7a92a66`, without rerunning the compiler: exact34 Source members,
five afterimages,38+12 retained model checks,1020 current dependency hashes and
2560 bounded arithmetic layouts. No material Source blocker was found. Native
runtime/GC/link/component and full Next acceptance remain open.

Checkpoint validation preserves eight staged whitespace warnings across five
byte-exact copied-source/license/raw-log paths. Authored documentation and code
pass the working diff check; historical bytes and draft derivation hashes are
preserved. All delegated writers and operational jobs have stopped for commit.
The full roadmap and complete Next-in-Wasm success gate remain in progress.

Latest actual result: [experimental native SHA256 Hash/Hmac](docs/node-compat/hash-hmac-results-2026-11-06.md)
passes fourteen complete returns across retained/fresh Jco and stock Wasmtime,
280 accepted Node-record comparisons and112 separate native-policy checks.
Both zero-import components pass independent artifact and sequence reviews.
Corrected runtime reports have truthful3/1 call counters. Direct bare/prefixed
imports share functions/default objects but retain distinct namespace objects;
that Node deviation stays explicit. These are pre-freeze experimental results,
with production crypto deferred and lifecycle/cost/adoption gates still open.

The clock diagnostic producer now has a runnable, independently reviewed
[V3 Source](tests/node-compat/foundation-scheduler/combined-clock-diagnostics-native-integration-candidate-v3/README.md),
index `3beebcf7`. The V2 attempt is held: its unsorted expected native manifest
would fail the real helper's canonical-order predicate after compilation.
V3 sorts the declared rows and updates every policy/helper/recipe digest join;
the native C++ and external embedding payloads are unchanged.
[Independent Source review](tests/node-compat/foundation-scheduler/independent-clock-diagnostic357-native-integration-v3-source-review-v1/results.json),
index `a3c58ffd`, passes384 bounded checks, including the actual old-fail/new-pass
predicate and fourteen Root authority models. Seven earlier SDK frontends passed
syntax checks. Source staging, native Release build and their independent DATA
reviews now pass. No new clock component/guest action has run.
Its actual357 native/three external/eleven manifest/82-field identity is
separate from the experimental Hash/Hmac357/83 artifact.

The unapplied [native namespace-cache correction](tests/node-compat/foundation-crypto/node-builtin-namespace-identity-candidate-v1/README.md)
is sealed at `5342a356`. It canonicalizes a bare builtin cache key only when
the explicitly registered `node:` key names the exact same rooted JSObject.
It uses existing SpiderMonkey APIs and preserves the registered metadata key.
One real SDK30 frontend accepts the afterimage `b399c648`; no object, link or
guest test ran. The driver's later sorted-Path versus sorted-string assertion
failure is retained. A separate read-only observer verifies unchanged protected
inputs and exact2,147-file membership without rerunning the compiler.
Fourteen synthetic model cases and two fixture grammar checks pass; the two
raw import-order fixtures remain unexecuted. Current production and staged
sources are unchanged; runtime namespace parity is still false for9aec.

The [Hash/Hmac freezer Source](tests/node-compat/foundation-crypto/node-crypto-hash-hmac-freezer-candidate-v1/README.md)
is sealed at `45eef4b6`, with25 payloads. Its new callback preserves the real
P3 owner and accepts only the new freeze-created root; it consumes corrected
artifact review `a39cce0d` and retains the failed original BUILD history.
The proposed frozen-only verifier reads copied roles and unchanged83-field
pure models. Source checks cover63 bounded cases and21,475 current inputs,
thirty families and eleven trees. The proposed copy includes1,642 source/tool
files, three actual embedding sources, three historical staged references and
169 selected WORK witnesses. Independent Source review, actual freeze,
frozen-only verification and independent frozen-artifact DATA review now pass.
No engine, guest or crypto operation runs in those phases.

The pre-commit closure audit verifies23 changed indexed families,623 payloads
and31,457,812 payload bytes. It excludes only each outer family's own root
index and checks nested copied indexes as ordinary payloads. All new binary
artifacts remain external with descriptors. All writers and operational jobs
are stopped for this checkpoint; full roadmap completion is not claimed.
The staged whitespace check exits2 on six immutable evidence paths: the two
byte-exact generated Jco files, three unapplied embedding patches and one sealed
reviewer's extra EOF newline. Those recorded bytes are preserved; edited
documentation and the new Root launcher have no whitespace warnings.

The complete725-file checkpoint is committed and pushed as
`dca02ed598ade315ed452cf7726641b11ced44b9`; `origin/main` matches, and the
worktree was clean before subsequent actions. The authorized next
[clock source stage](tests/node-compat/foundation-scheduler/combined-clock-diagnostic357-stage-v3-root-results.json)
finishes Root42445/parent52442/worker52704, raw0, clean owned groups.
Journal `93244df7` retains1,583 copied sources/tools, baseline54b, detached
private Git metadata and exact preimages. Current source originals and the
original repository object/index window are preserved. A compact independent
actual-stage review is pending; native compilation and guest execution have
not run. Git mutations are held during that review's before/final window.

[Independent freezer Source review](tests/node-compat/foundation-crypto/independent-node-crypto-hash-hmac-freezer-source-review-v1/results.json)
passes at `d54a57ef`:50,353 checks,21,501 unique files including the freezer's
26 actual members, thirty families and eleven trees. No operational helper,
freezer or verifier ran in that review. Root issues the separate actual
[freeze-only action](tests/node-compat/foundation-crypto/node-crypto-hash-hmac-freeze-v1-root-invocation.json)
at15125/parent54794, with1,800-second owned monitors. Static copies, one genuine
read-only P3 admission and frozen-only verification are allowed; compiler,
engine, guest, crypto and public profile actions remain forbidden. The outcome
is pending; original recipe0/parents1+1/preservationfalse remain unchanged.

The live-EVP snapshot design now identifies a concrete late-INIT seam:
`finish_pre_initialization()` sets EngineState::Initialized before ComponentizeJS
finishes binding exports and draining final jobs/ticks. REQUEST_HANDLER_ONLY
alone cannot cover that window. The existing private entropy policy's deployed
state, flipped through the real embedding entry hook, distinguishes deployed
calls even when entropy is OFF. A proposed read-only accessor plus native
Hash/Hmac guards will use that state and EngineState together. No new host
capability or embedding hook is required; implementation and actual INIT/late
binding/ordinary-call validation remain pending in a separate native generation.

[Independent clock stage review](tests/node-compat/foundation-scheduler/independent-clock-diagnostic357-stage-v3-results-review-v1/results.json)
passes at `ed52c7f6`, with the whole genuine V3 consumer contract. It verifies
all1,583 copies,357 native/1,226 tools, eleven manifests,742 baseline entries,
234 overwritten blob preimages and909 packed Git objects. Both parents/five
Git commands finish0 and current26,341-file/24-family bookends pass. Its separate
29-file current user-Git window is unchanged; historic stage protection is
limited to the actual objects/index capture. Three corrected reader assumptions
are retained (the sealed README says two, a clerical count deviation).
Root issues the separate [clock native build](tests/node-compat/foundation-scheduler/combined-clock-diagnostic357-build-v3-root-invocation.json)
at22041/parent56756: Release, jobs1, entropyOFF, no GC/OOM/DEBUG/reset,7,200-second
owned monitors,2GiB start/800MiB stop. The result is pending; no clock engine or
guest has executed, and no private/public runtime profile is admitted.

The actual [crypto freeze](tests/node-compat/foundation-crypto/node-crypto-hash-hmac-freeze-v1-root-results.json)
now finishes15125/parent54794, raw0, clean. Receipt `187fabbe` retains1,893 copied
payloads/641,351,629 bytes and21,513 protected current references. The genuine
frozen-only verifier returns its whole NOT_ADOPTED record, using the frozen
9aec engine, byte-exact2b725 raw83 metadata and copied roles. No helper admission
or old Ninja command is replayed by that verifier; the freeze itself made one
fresh genuine read-only P3 admission. Independent actual-freeze DATA review is
pending. Uncopied live SDK/reference originals, live-EVP snapshots, security,
cost and profile adoption are outside this frozen-only acceptance scope.

The actual [clock native build](tests/node-compat/foundation-scheduler/combined-clock-diagnostic357-build-v3-root-results.json)
now finishes22041/parent56756, recipe0/wrapper0 and clean owned monitors.
Engine `d13aec90` is10,043,743 bytes; sidecar `56b13135` is848,807 bytes,
with genuine82 raw fields,357 native/three external sources and eleven whole
manifests. Requested/observed diagnostic and performance flags agree. The
direct82 model returns SHAPE_ONLY, runtimeAccepted=false. Original source,
staged copies and cache inputs are preserved. This build's configured Git
index has a retained raw preimage; the allowed comparison proves742 baseline
entries, identical semantics/flags/extensions and mode, with stat-cache bytes
and inode changed. That evidence does not retroactively repair the old Hash
build's missing preimage. Independent actual-build DATA review is pending;
no clock engine/component/guest, lifecycle gate or public adoption is claimed.

[Independent namespace-fix Source review](tests/node-compat/foundation-crypto/independent-node-builtin-namespace-identity-source-review-v1/results.json)
passes at `b6da1601`, covering both exact derivations,357 source files,
1,041 actual SDK dependencies and24 pure predicate cases. The new cache key
remains rooted and explicitly registered. Primitive-value, embedded-NUL and
late-registration synthetic model limits remain explicit; no new registration
API or actual fixture observation is inferred. Clang0/original driver1 remain
separate, and current9aec namespace identity stays unchanged until a new linked
generation and raw import-order tests pass.

The standalone [Hash/Hmac INIT barrier Source](tests/node-compat/foundation-crypto/node-crypto-hash-hmac-init-barrier-candidate-v1/README.md)
is sealed at `b8a4f219`: three existing-file afterimages,357=354 retained+three
changed, no new path/external change or implicit alias-fix composition.
It adds a read-only deployed-state accessor and guards all four native primitives
before native key/state/provider/EVP/output access. Errors carry TypeError and
`ERR_SM_NODE_CRYPTO_INITIALIZATION`; cleanup remains unconditional. Eight future
fixtures cover import-only/ordinary positives and direct, finalized, top-level
job, late getter and final-job refusals. Author checks53 Source/58 synthetic/nine
grammar cases pass. No compiler, engine, crypto, snapshot or fixture executes.
The separate [Root Source review](tests/node-compat/foundation-crypto/independent-node-crypto-hash-hmac-init-barrier-source-review-v1/results.json)
passes at `7c8f9ab8`, covering1,066 checks/498 current files/three families and
twenty exact guard truth-table cases. It authenticates all357 current native
hashes/three actual external inputs and the real lifecycle/bindgen/error seams.
Root requested the high-level requirement; a different agent authored the
afterimages. This source/hash/order review grants no native action or snapshot
acceptance. Two-CPP SDK driver preparation is separate and unexecuted.

The [independent actual clock build review](tests/node-compat/foundation-scheduler/independent-clock-diagnostic357-build-v3-results-review-v1/results.json)
passes at `9d4f0218`, with whole future/own contracts joined. Actual DB69 has
63 policy/five other/one generated-null rows and one separate embedding command;
all seven shared diagnostic commands are bound. Its actual link has31 ordered
static-library arguments/30 unique archives, rather than an inherited old count.
All44,369 current files/25 families, seven distributions/4,650 OpenSSL sources,
62 aliases/two hardlinks and real Git index preimage semantics pass. Recipe and
both parents finish0 clean. No engine, guest or freezer action occurs in review;
private component construction is the next experimental clock step.

The [independent frozen Hash/Hmac review](tests/node-compat/foundation-crypto/independent-node-crypto-hash-hmac-frozen-artifact-review-v1/results.json)
passes at `9d2ed35a`:80,672 checks/23,724 unique files/32 families. All1,893
copied payloads plus receipt have exact hashes,0600 modes, single/distinct inodes
and correct original relationships. Whole P3 return, raw83 metadata,169 WORK
witnesses and1,642+three actual external+three historical reference roles agree.
Both monitored phases finish0; all303 retained events reconcile. The reader's
first stdout-publication typo is preserved; a corrected read-only completion
finishes0, without verifier/helper/admission replay. Whole result/contract coverage
matches. Uncopied live SDK/reference offline closure remains false; the original
failed BUILD outcomes and current unadopted/snapshot/security/cost scope remain.

Preflight of the still-unexecuted INIT-barrier SDK driver finds one concrete
cleanup-predicate gap: it omits `interruptedSignals`, so a cleanly exited child
can be misreported clean after its monitor is interrupted. No compiler authority
is issued. The initial preparation bytes/fingerprint are being retained before
a minimal driver/test correction; this is not a native compiler or guard failure.

The corrected preparation `cf79802e` retains all eleven original15ec files and
passes72 pure cases/three ASTs. [Independent bounded boundary audit](tests/node-compat/foundation-crypto/independent-node-crypto-hash-hmac-init-barrier-boundary-audit-v1.json)
passes its525 joined checks and records the real old-accept/new-refuse interrupt
counterexamples. Root then issues a separate [two-CPP syntax attempt](tests/node-compat/foundation-crypto/node-crypto-hash-hmac-init-barrier-sdk-v1-root-invocation.json),
54203/parent81211. That [actual attempt](tests/node-compat/foundation-crypto/node-crypto-hash-hmac-init-barrier-sdk-v1-root-results.json)
finishes raw1 with clean owned groups before creating its output or importing
the compiler monitor. No compiler starts. The actual directory guard rejects
the fifth declared tree, an absent text-codec include directory with zero ledger
files/aliases. The [Root diagnostic](tests/node-compat/foundation-crypto/node-crypto-hash-hmac-init-barrier-sdk-v1-path-guard-root-data.json)
confirms the first four real trees exist and only this unused `-I` path is
absent. The preflight did not test the actual empty-tree path predicate. All
executed v1 preparation/Root/raw evidence stays immutable; a genuine v2 driver
must preserve the original compile argument and check this explicit absence
before/final, without creating or changing the historical directory. Actual
INIT-barrier C++ syntax remains untested; there is no native compiler failure.
[Independent actual failure review](tests/node-compat/foundation-crypto/independent-node-crypto-hash-hmac-init-barrier-sdk-v1-failure-data-review.json)
passes317 scoped checks and embeds all five original monitor text files. It
reproduces the actual path assertion through the unchanged extracted predicate,
qualifies the prior preflight's missed path parity and confirms no compiler
monitor was reached. The genuine [v2 preparation](tests/node-compat/foundation-crypto/node-crypto-hash-hmac-init-barrier-sdk-syntax-v2/README.md)
is held at `9f0690d3`, with fourteen payloads. It keeps all real compile flags,
authenticates four required trees and explicitly bookends the one absent include.
The real five-path guard checks433,091,709 bytes per bookend/34 aliases;
ten filesystem negatives,77 pure cases and four AST checks pass. Its new Root
protocol/output are unissued, the old attempt and Source b8a4 stay unchanged,
and independent v2 preflight is pending before any new compiler authority.

[Independent v2 SDK preflight](tests/node-compat/foundation-crypto/independent-node-crypto-hash-hmac-init-barrier-sdk-v2-preflight-audit.json)
now passes at `3aa36f2b`, with472 canonical JSON checks/77 scoped files.
The genuine actual root/absence guards and six filesystem negatives pass;
the author's full433MB/12,748-row hash report is authenticated separately.
The chat's474 count included two later output assertions; the immutable JSON472
is authoritative. Root issues a fresh [V2 syntax authority](tests/node-compat/foundation-crypto/node-crypto-hash-hmac-init-barrier-sdk-v2-root-invocation.json),
65438/parent84322, with a300-second outer/two60-second compiler deadlines.
The [actual two-CPP result](tests/node-compat/foundation-crypto/node-crypto-hash-hmac-init-barrier-sdk-v2-root-results.json)
finishes raw0, clean. Both real SDK frontends start and return0; their dependency
files and before/final protections pass. This is C++ syntax/type acceptance,
with no object, link, engine, crypto, snapshot or fixture execution. Independent
actual-result DATA review is pending. Original v1's no-compiler failure remains
unchanged; the barrier is still unapplied to any native engine generation.

The private [clock selector component caller Source](tests/node-compat/foundation-scheduler/clock-diagnostic357-selector-component-candidate-v1/README.md)
is sealed at `8b909eba`, with60 DATA/pure checks and four pinned Node grammar
checks. It uses the actual authenticated61685 package's `componentize` API and
pruned87777 adapter, preserving whole bytes through the real capture helper
before WIT/capability audits. It accepts the full genuine82-field build proof
and declares the actual private guest module's three methods/default record;
only standard0.2.10 wall-clock, monotonic-clock and io/poll are selectable.
The private module is internal guest code, not a host service. General loader
hardpins and callback limitations are handled by this genuine direct API path;
no old355/Hash83 frame, imported namespace/global rebind or host modification is
used. C's narrow preinspection prompted alias/diagnostic/TMPDIR corrections
before sealing; formal Source review now passes. Construction/runtime slots
remain NULL. No package, engine, clock probe, compiler or guest
action ran; this Source admits no lifecycle gate or public API.

[Independent actual two-CPP review](tests/node-compat/foundation-crypto/independent-node-crypto-hash-hmac-init-barrier-sdk-v2-results-review-v1/results.json)
passes at `4d235f7c`, with the whole fixed/exact/coverage contract joined.
Both real compiler starts, original flags/60-second deadlines, raw0 and empty
streams/signals reconcile. Dependency files contain1,021 and1,052 entries,
covering1,053 unique physical inputs; both see the changed header through VFS.
All12,864 current captured files, nine membership trees,34 aliases and one
explicit absence match actual before/final protection; the four required trees
have exactly12,748 approved ledger rows. A closed35-file UTF8 text capsule
retains all23 actual publication files/nested index plus Root context, with no
SDK payload or binaries copied. Source/native binary/raw metadata remain
unchanged; no link, runtime INIT behavior or adoption is proved. All ordinary
native/SDK actions and this result reviewer are terminal before checkpoint.

The [independent clock caller Source peer](tests/node-compat/foundation-scheduler/independent-clock-diagnostic357-selector-component-source-review-v1/results.json)
passes at `10ddfa57`, with the genuine full consumer contract including
verifiedPassed=true. All36 owner payloads/70 declared compact descriptors,
107 unique files/150,439,328 bytes stay stable. Sixty owner and33 independently
exercised exported pure cases pass. Actual61685/87777, Jco and whole-capture
primary APIs are inspected; a full44,369-native/4,889-package replay remains the
operational caller's responsibility. No package, loader, componentizer, engine,
probe, clock or guest action runs in review. All writers are stopped for the
next all-work checkpoint; actual clock component construction remains next.

The final closure audit verifies12 new indexed families,607 payloads and
42,853,252 payload bytes, including all nested copied indexes as DATA. All1,607
local links in current documentation resolve. Engines/components/SDK libraries
stay external; small raw Git and monitor evidence retain their recorded bytes.
All Source/data writers and owned operational processes are stopped.
The staged whitespace check has one warning in the byte-exact retained native
build log; its sealed bytes are preserved. Edited documentation and code have
no whitespace warnings.

The650-file all-work checkpoint is committed and pushed as
`98cb2d37cf650ae18d2f7bcaec0b0a342b1dc9f5`; `origin/main` matches and the
worktree is clean at that checkpoint. This goal turn made **progress** through
actual native build, freeze and SDK results plus reusable retained evidence.
The roadmap remains **in progress**: clock component/runtime gates, a new
integrated Hash/Hmac generation with actual INIT/import-order tests, lifecycle,
cost, optional capability/host gates and broader application compatibility remain.

The next measured application-demand item is the actual
[`format('value:%s:%d', 'ok', 7)` call](tests/node-compat/frameworks/nextjs/app-fixture/lib/compat.mjs#L50),
whose Node result is `value:ok:7`; current `util.format` is explicitly deferred.
A read-only pinned-Node Source assessment identifies a small audited primitive
`%s`/`%d`/`%%` facade with exact parser/negative-zero/missing-argument rules and
explicit object/inspect/directive/limit refusals as a possible bounded successor.
It requires new util/sys support manifests, generated factory/profile checks,
real native artifact metadata and fresh component/application regressions.
No formatter implementation, oracle or guest run occurs in that assessment;
it does not repair the current Next baseline or establish full Next support.

Continuation after `e91cf013`: the previous goal turn made **progress**. It
pushed the all-work checkpoint and fresh comprehensive Next.js/component
regression evidence; remote `origin/main` matched
`e91cf013ee926923c04a54cf0ca8e19d402169de`, with a clean worktree then.

The actual [read-only Hash/Hmac revalidation attempt](tests/node-compat/foundation-crypto/node-crypto-hash-hmac-artifact-revalidation-v1-root-results.json)
now finishes at Root session19977/child15846, raw1, with clean owned-group
shutdown and no timeout/signals. It fails in the Source-input path guard before
creating its payload output, importing the producer helper or calling admission.
The [Root diagnostic](tests/node-compat/foundation-crypto/node-crypto-hash-hmac-artifact-revalidation-v1-path-guard-root-data.json)
finds exactly two logical `/tmp` descriptors in the21,328-row ledger: the retained
classic-streams and zlib admission readers. Their sole symlink ancestor is the
system `/tmp`→`/private/tmp` alias. The actual guard rejects that alias, while
the Source/peer readers had normalized it; their Source checks missed this
operational mismatch. The failed175e attempt and619de Source review remain
unchanged, qualified by this result. A minimal genuine successor will preserve
the old descriptor paths and authenticate only that explicit system alias,
with the actual guard tested over every input and negative alias cases. No
artifact revalidation proof, freeze, engine or crypto execution is claimed.

The genuine [v2 successor](tests/node-compat/foundation-crypto/node-crypto-hash-hmac-artifact-revalidation-candidate-v2/README.md)
is sealed at `559d600d`, with22 payloads and zero duplicated ledger tables.
Its actual guard passes all21,328 retained rows, accepts only the two selected
`/tmp` descriptors and refuses34 real alias paths/48 negative cases. The
[independent Source peer](tests/node-compat/foundation-crypto/independent-node-crypto-hash-hmac-artifact-revalidation-v2-source-review-v1/results.json)
passes at `31d9b3f8`, exercising the genuine guard across21,437 current inputs,
27 families and11 trees. It retains the old619de parity miss explicitly.
Root [actual retry54289](tests/node-compat/foundation-crypto/node-crypto-hash-hmac-artifact-revalidation-v2-root-results.json)
now finishes raw0/child20222, clean, in88.957 operational seconds. The original
P3 `admit` API returns its whole genuine V3 DATA, retaining owner2ebe. Result
`e55c5de6` preserves raw83 metadata2b725,357+3 inputs/twelve manifests,
all21,451 current inputs, seven whole distributions and4,650 OpenSSL sources.
The six payloads and five monitor files are retained byte-exact at
[Root evidence index40c9d46c](tests/node-compat/foundation-crypto/node-crypto-hash-hmac-artifact-revalidation-v2-root-evidence/index.json),
7,293,857 payload bytes. [Independent actual DATA review](tests/node-compat/foundation-crypto/independent-node-crypto-hash-hmac-artifact-revalidation-v2-results-review-v1/results.json)
reports DATA pass at index `61250674`. A subsequent actual caller-contract
check finds its result lacks the `coverage` field required by its indexed
contract. Its underlying observations remain valid, but the complete consumer
wire is unaccepted pending a minimal genuine publication successor. No caller
action was issued against the incomplete pair. The correction will derive
coverage from the retained actual observations and test the unchanged real
`Capture.proof` consumer, including old-pair and mutated-coverage refusals.
The [publication successor](tests/node-compat/foundation-crypto/independent-node-crypto-hash-hmac-artifact-revalidation-v2-results-review-v2/results.json)
now closes that join at index `a39cce0d`, preserving every original observation
and adding derived coverage. The [actual consumer test](tests/node-compat/foundation-crypto/independent-node-crypto-hash-hmac-artifact-revalidation-v2-results-review-v2-consumer-join-check-v2.json)
uses the unchanged extracted caller class: old pair refused, corrected pair and
private recheck passed, consistently mutated coverage refused. Its first test
assumed a more specific assertion message; the external harness correction and
original failed receipt are retained. The complete new pair is consumable;
old6125 remains immutable and consumer-incomplete.
It checks all21,451 files/2,408,228,664 logical bytes twice,28 declared families,
11 trees,35 aliases and an archive hardlink; the current742-entry Git index
matches baseline path/mode/OID/stage semantics at the explicit600-mode exception.
Whole stdout/result/producer return, all12 manifests and raw83 bytes reconcile.
Current distribution hashes/digests are independent DATA checks; archive
correspondence retains its reviewed-Source dependence, without rerunning the
archive verifier. Eight consistent semantic mutations are refused. This is
successful read-only revalidation, with no guest, crypto or freeze execution;
original BUILD4 recipe0/parents1+1/preservationfalse remain unchanged.

The compact experimental [component caller](tests/node-compat/foundation-crypto/node-crypto-hash-hmac-component-diagnostic-candidate-v1/README.md)
is sealed at `7fb5371b`: real full12-manifest bundling, whole pre-audit component
capture, distinct bundled/direct-native arms and isolated retained/fresh Jco
workers. Actual descriptor guards21,451/three tool-tree digests,27 pure cases,
four Node grammar checks and two Python ASTs pass. These are host-only checks;
all actual component and guest slots remain unissued. Independent Source
preinspection finds no remaining caller API defect and holds final acceptance
on the artifact coverage publication join above. A reusable [DATA comparator](tests/node-compat/foundation-crypto/node-crypto-hash-hmac-data-comparator-candidate-v1/README.md)
is sealed at `a6b89157`:60 DATA checks/55 refusals and grammar checks pass.
Its native seven-call records are synthetic; actual guest records remain NULL.
It compares the full20 accepted records, eight native policy cases and real
alias/namespace/typed-constant observations with appropriate Node parity scope.

The [caller Source peer](tests/node-compat/foundation-crypto/independent-node-crypto-hash-hmac-component-diagnostic-source-review-v1/results.json)
then passes at `1448646b` with the corrected artifact pair. Actual [bundle61516](tests/node-compat/foundation-crypto/node-crypto-hash-hmac357-diagnostic-bundle-v1-root-results.json)
finishes raw0/clean:16,479-byte source `6b8f9a5f` retains only native
`node:crypto`/`node:buffer` imports. [Independent bundle DATA review](tests/node-compat/foundation-crypto/independent-node-crypto-hash-hmac357-diagnostic-bundle-results-review-v1.json)
passes780 checks. Actual [construction77438](tests/node-compat/foundation-crypto/node-crypto-hash-hmac357-diagnostic-construct-bundled-v1-root-results.json)
finishes raw0/clean. Component `2e538349` is13,240,343 bytes, imports nothing
and exports only `run() -> string`. [Independent artifact review](tests/node-compat/foundation-crypto/independent-node-crypto-hash-hmac357-diagnostic-component-artifact-review-v1.json)
passes895 checks, including exact whole core `434c9479`, canonical ABI, no core
imports and generated ESM with only the Node FS byte loader/empty utility helper.
The component is an experimental pre-freeze diagnostic; it admits no profile.

Actual [ordinary Jco98316](tests/node-compat/foundation-crypto/node-crypto-hash-hmac357-diagnostic-jco-bundled-v1-root-results.json)
finishes raw0/clean and returns three retained plus one fresh complete strings.
Their comparisons pass80 accepted Node-record checks,32 separate native policy
checks,13 aliases per call,68/71 namespace/default names and nine typed guest
header constants. This is the first actual guest Hash/Hmac execution. A harness
success-path bookkeeping defect is found: `detail={...detail,...await
jcoChild(...)}` snapshots primitive counters before the awaited helper mutates
them, then overwrites those mutations. The shared raw-string arrays retain3/1
records and all comparisons pass, while published child counters/import flags
incorrectly stay0/false. The original7fb/1448 packets and actual results remain
unchanged and qualified. Full runtime-phase acceptance is withheld; a minimal
caller successor will preserve counters after awaiting and repeat only ordinary
Jco calls with the same component. No engine rebuild/revalidation/construction
rerun is needed. Stock Wasmtime3-fresh and direct-native-alias checks remain next.

The separately tagged [direct-native constructor14719](tests/node-compat/foundation-crypto/node-crypto-hash-hmac357-diagnostic-construct-raw-v1-root-results.json)
also finishes raw0/clean using exact16b fixture text, bypassing bundler alias
canonicalization. Component `793c9cb1` is13,250,961 bytes, has no imports and
the same sole scalar ABI. [Independent artifact review](tests/node-compat/foundation-crypto/independent-node-crypto-hash-hmac357-diagnostic-raw-component-artifact-review-v1.json)
passes891 checks; original7fb construction provenance is explicit and the known
Jco-reporting defect does not affect construction. Direct-native runtime alias
behavior is still unexecuted. [Independent original Jco DATA review](tests/node-compat/foundation-crypto/independent-node-crypto-hash-hmac357-diagnostic-jco-v1-data-review.json)
passes the bounded80/32 raw-output evidence and exact process/publication joins,
while keeping phase/runtime acceptance false for stale counters. A separately
reviewed [stock-host companion](tests/node-compat/foundation-crypto/node-crypto-hash-hmac-wasmtime-diagnostic-candidate-v1/README.md)
is prepared for three fresh Wasmtime calls with strict whole WAVE decoding and
full same-arm Jco equality; its activation waits for corrected truthful Jco data.

That boundary now closes with [Jco-only Source v2](tests/node-compat/foundation-crypto/node-crypto-hash-hmac-component-diagnostic-candidate-v2/README.md),
index `48b15d2f`, and [independent delta peer](tests/node-compat/foundation-crypto/independent-node-crypto-hash-hmac-component-diagnostic-v2-source-review-v1.json)
`90f80848`. The actual await/merge regression reproduces old primitive loss and
preserves new success/throw/shared-array state; nine seam and eight genuine
constructor/arm binding cases pass. No native data/tree authoring replay or
engine reconstruction occurs. Corrected [bundled Jco6202](tests/node-compat/foundation-crypto/node-crypto-hash-hmac357-diagnostic-jco-bundled-v2-root-results.json)
and [raw Jco29069](tests/node-compat/foundation-crypto/node-crypto-hash-hmac357-diagnostic-jco-raw-v2-root-results.json)
both finish raw0/clean, each with correct3/1 import/attempt/return/string/comparison
counters and zero throws. Each yields80 accepted/32 policy checks, with complete
fresh1 equal to retained1. Native namespace identity is true for bundled
canonical imports and false for direct bare/prefixed imports; all13 named/default
and alias identities are true in both arms.

Separate [stock Wasmtime bundled96372](tests/node-compat/foundation-crypto/node-crypto-hash-hmac357-diagnostic-wasmtime-bundled-v1-root-results.json)
and [raw36308](tests/node-compat/foundation-crypto/node-crypto-hash-hmac357-diagnostic-wasmtime-raw-v1-root-results.json)
each finish raw0/clean with three fresh processes and strict full WAVE decoding.
All six literal returns equal the corresponding same-arm fresh Jco return.
[Bundled sequence review](tests/node-compat/foundation-crypto/independent-node-crypto-hash-hmac357-diagnostic-bundled-jco-wasmtime-sequence-review-v1.json)
`ee79868d` and [raw sequence review](tests/node-compat/foundation-crypto/independent-node-crypto-hash-hmac357-diagnostic-raw-jco-wasmtime-sequence-review-v1.json)
`49b6c11b` pass each616 DATA checks: fourteen total strings,280 accepted/112
separate policy checks, eight whole same-ordinal guest comparisons, exact source/
component/native tuples and clean process evidence. The [portable dataset](tests/node-compat/foundation-crypto/node-crypto-hash-hmac357-runtime-validation-v1/index.json)
is sealed as `3bdfaa5f`:142 payloads/9,759,458 bytes. It contains exact typed/raw
strings, streams, comparisons, source inputs and Root observations; no Wasm
binary is copied. The [read-only retained checker](tests/node-compat/foundation-crypto/node-crypto-hash-hmac-retained-results-check-v1/README.md)
now passes its28 DATA tests, including relocation, missing/tampered records,
versions, duplicate roles and changed ordinals/types. Root's [actual one-command
recheck](tests/node-compat/foundation-crypto/node-crypto-hash-hmac357-retained-check-root-results-v1.json)
exits0 for all142 payload hashes/membership and14/280/112 semantics. It imports
the pinned pure comparator, performs no workload and leaves provider/lifecycle/
process/provenance conclusions to separate actual reviews.
Public adoption, frozen reproduction, live-EVP snapshot safety, GC/erasure,
allocation-boundary and performance gates remain open. This does not validate
the full Next server or a new wasmCloud application.

The separate [private clock diagnostic v2 Source peer](tests/node-compat/foundation-scheduler/independent-combined-clock-diagnostics-v2-source-review-v1/results.json)
passes at index `2ed8d692`:40 Source members,463 inputs, three donor families,
1,475 read/hash/reversal checks and72 genuine pure collector cases. This covers
the bounded owning-vector sentinels and last-clock/SAME-TU source design; it
does not prove linking, clock execution, natural-loop settlement, broad internal
quiescence, Store death or any of the17 runtime gates. Its Source README's39
member count is clerical; primary result/receipt and actual intake record40.
Fresh [SDK syntax/type checks](tests/node-compat/foundation-scheduler/combined-clock-diagnostics-sdk-syntax-v2/results.json)
now pass for all seven changed translation units: six native and one separately
configured external embedding unit, with actual WASI SDK30/LLVM21 frontends,
empty streams, raw0 and clean groups. Source90ef and peer2ed8 are bound by
index `c669522f`,54 payloads. [Root readback](tests/node-compat/foundation-scheduler/combined-clock-diagnostics-sdk-syntax-v2-root-observation.json)
rehashes all11,721 protected originals and31 SDK aliases, checks exact actual
started argv/terminal pairs and all seven empty streams. The first inline Root
reader mistook an alias count for a boolean; it stopped before publication and
was corrected to exact31 without rerunning the compiler. There is no object,
link, ODR/shared-state, engine, guest or clock result. Older v1 syntax evidence
remains separate.

Engineering sequencing decision: once actual read-only357/83 revalidation and
its independent DATA review pass, an isolated ordinary-call Hash/Hmac component
may run before the full distribution freeze. The caller must preserve the full
83-field metadata/current357+3 source protection, select the actual twelve
manifests with `builtinMap`/`bundleProfile`, and use the genuine componentizer
with raw partial capture, an empty selected-interface set and an audited
`run() -> string` component. The current fixture16b creates no EVP contexts at
module initialization. This diagnostic can expose algorithm/binding bugs early;
full freeze/reproduction, native live-EVP snapshot policy, secret ownership,
GC/lifecycle, cost and release gates remain required for profile adoption.
The old355/80 tooling and its fixed manifest catalogue remain closed.

All work through checkpoint `77659217c92019d5471570b937d69f6352cbe4e5` is
committed and pushed; remote `origin/main` matched and the worktree was clean.
The subsequent [fresh comprehensive Next.js checks](docs/node-compat/nextjs-results-2026-11-06.md)
retain two successful Node builds and24/24 HTTP checks per run. Both browser
interactions work in both runs; the first records one aborted action POST and
fails its strict network check. An untouched replay passes all browser checks.
Its19 Wasm observations preserve17 known failures with no changed blocker;
the full Next server still does not compile. The supported-module differential
passes Node/Jco/Wasmtime, and the optional package matrix passes its three
positives while retaining seven guest failures. All raw observations and exact
generated-source mismatches remain recorded for future checks. This advances
application regression coverage; it does not admit a new runtime profile.

The same-build optional-matrix replay now also passes its comparison with no
changed blockers; the historical comparison's three generated-source mismatches
stay failed. A finite Root check verifies all16 component occurrences' actual
bytes, retained empty-import/scalar-WIT records and12 whole-string cases. The
compact independent main review checks1,981 DATA assertions/568 descriptor
copies, both runs' raw terminals/streams and six actual component import
sections. Main43/package40 injected comparator checks and the separate retained
clock checker pass. All ordinary workers and reviewers are terminal before the
results checkpoint. No new Wasm binaries or dependencies are added to Git;
their external locations and hashes remain recorded.

Completion audit: the requested commit/push and comprehensive application
experiment have concrete results, including retained failures and reusable
comparators. The full roadmap is incomplete. Native crypto full freeze,
snapshot/lifetime/cost/adoption, native clock lifecycle and request-context/ALS gates remain
open; optional filesystem, Node HTTP/network/process profiles and same-component
both-host release gates remain pending. Full Next server execution and adoption
of a broader runtime profile are unproved. These are outstanding work, not
successful compatibility claims.

Current application result: the comprehensive Next.js fixture passes its Node
build/HTTP/browser controls, while the full Next server still fails Wasm
compilation. Three optional package cases pass full Node/Jco/Wasmtime
comparison. A separate explicitly selected standard-clock component now renders
real ReactDOM edge HTML on both Jco and Wasmtime in a seven-return differential;
independent result review passes.
See the [Next fixture](tests/node-compat/frameworks/nextjs/README.md) for the
original failures and reusable regression commands. This Git checkpoint
preserves the new evidence, retained failures and proposed source-only tooling; the full roadmap remains incomplete.

Immediate remaining work:

1. Complete the remaining native clock lifecycle gates. Ordinary timer,
   snapshot-clock and surviving-job tests passed their bounded reviews; fatal
   cause, native pollable/drop/interest, invalid-queue, offset and teardown proof
   remain open. Failed-instance reuse and request isolation remain unproved.
2. Integrate a genuine new Hash/Hmac generation after the reviewed freeze.
   Raw83 metadata, frozen-only verification, zero-import component inspection
   and fourteen ordinary-call Node differentials pass their experimental reviews.
   The namespace-cache fix and INIT barrier are reviewed unapplied sources;
   the barrier's two-CPP syntax checks and independent DATA review pass after
   preserved driver corrections. Compose/version the policies explicitly, build/link new bytes,
   test early/late INIT refusals and repeat ordinary-call/import-order checks.
   Borrowing, secret erasure, lifecycle, cost and public admission stay open.
3. Admit any new profile only after its required correctness, capability, lifecycle
   and cost checks. Re-run the pinned Next/package checks with genuine new artifact
   pins and retain changed blockers. The full Next server is still unavailable.

Checkpoint `6066915b` verified 15 completed indexed families: 774 payloads,
14,122,361 payload bytes, exact membership and every nested copied index. It also
includes 38 explicitly **UNSEALED WIP** files in controller Sourcev3: no index,
result, receipt or action grant. Its inherited references/templates are not
runnable or approved. All writers are held during this Git snapshot; Source
validation and independent review remain required before any new native phase.

Current continuation after `6066915b`: previous goal turn **made progress**.
It pushed all 875 changed files as `6066915b3daa6fa09c0b221229f9698cc9b4e239`;
remote `origin/main` matched and the worktree was clean at that checkpoint.
The corrected [controller Sourcev3](tests/node-compat/foundation-crypto/node-crypto-hash-hmac-native-controller-candidate-v3/README.md)
is now sealed as `2ebed6b8`, with49 members. Its3,055 Source/data/pure checks
cover5,336 inputs/21 families and21 Python AST files. All56 producer bindings
pass;28 guard-regression checks/12 isolated hash-predicate commands reproduce
the held-v2 two stale guards, accept all four corrected guards and reject four
zero-pin mutations with diagnostics. All five real copy-mode outcomes remain
bound by exact function identity. Initial publication stops on a missing
preparation-history member before indexing; the member is included and final
closure passes. [Independent Source review35be5fcc](tests/node-compat/foundation-crypto/independent-node-crypto-hash-hmac-native-controller-v3-source-review-v1/results.json)
passes all seven active hash guards, complete path/self/model/ref joins,
22 reversals,103 inert cases and full5,378-file/22-family before/final intake.
The only noted future-contract prose saysV2; actual states, paths and model
checks enforceV3. No Source action is inferred from that review. Root's complete
actual pure Root/peer checks pass before authority files are written, then a
fresh [build-v4 invocation](tests/node-compat/foundation-crypto/node-crypto-hash-hmac-native-build-v4-root-invocation.json)
starts at62405/parent87467:7,200s outer/inner, jobs1,2GiB start/800MiB stop,
HASH-ON/COPY-only/BORROW-OFF/entropy-OFF, no DEBUG/GC/OOM. New WORK3 and producer
identities82dd/12abb/225f are used; failed WORK1/2 remain protected. The [actual build4 observation](tests/node-compat/foundation-crypto/node-crypto-hash-hmac-native-build-v4-root-results.json)
now records **recipe exit0 and wrapper exit1**. Compilation/linking/copy complete:
engine `9aec9297` is10,024,185B and byte-exact raw83 metadata `2b725c11` is731,387B,
with357 native/three embedding/twelve manifest rows. The log has109 display
records ending109/109, but repeats39 and omits40; those display values do not
prove unique task ordinals. A Root reader's overly strict ordered-label assertion
is retained/corrected before its result write; no build rerun occurs.
The wrapper fails recheck before inline admission and in final protection. Both
original parent exits1 and recipe0 retain clean owned-group cleanup. A [current
input recheck](tests/node-compat/foundation-crypto/node-crypto-hash-hmac-native-build-v4-input-recheck-root-data.json)
finds exactly one changed hash among5,375 inputs: staged `.git/index`,03f5eb17
becomesbfbb4330 at the same95,901B length;5,374 other files still match. Original
index bytes are absent, so exact writer/stat-only change is unproved. Independent
pure decoding confirms current valid DIRCv2/checksum/742 stage0 path-mode-OID
entries equal the authenticated54b baseline tree. Independent raw83 metadata,
69-row DB/macros/objects/archives/link validation is passing; full failure DATA
review is being finished. Original owner evidenceComplete remains false.
[Independent build4 failure/candidate reviewa4338bdc](tests/node-compat/foundation-crypto/independent-node-crypto-hash-hmac-native-build-v4-results-review-v1/results.json)
now passes the raw83 model, actual69=63+5+null compile rows, strict4/private7/
separate embedding1, guest OpenSSL include/link, whole ordered archives and
engine copies. The Git index also changes mode0644 to0600; all other configured
modes match. Its current742 entries match baseline semantics, without proof of
old index bytes, exact writer or stat-only mutation. The review records recipe0,
parents1+1 and preservationfalse; its5,541-file/34-alias finite ledger is not a
full future-freezer distribution proof. A compact separate [read-only revalidation
Source](tests/node-compat/foundation-crypto/node-crypto-hash-hmac-artifact-revalidation-candidate-v1/README.md)
is sealed at `175e4061`, with25 payloads. [Independent Source review](tests/node-compat/foundation-crypto/independent-node-crypto-hash-hmac-artifact-revalidation-source-review-v1/results.json)
passes at `619de02f`, covering21,398 files/24 families,11 trees,34 aliases,
six active ASTs and32 independent pure cases. The later actual attempt fails
before admission on the path-guard mismatch described above; neither Source
review nor author checks establish a successful artifact revalidation.
Its134,641 author checks cover21,372 current inputs/23 families/11 trees;
41 pure cases pass. No operational adapter call has run. It may establish
a new proof with an exact index hash/mode exception and fresh full before/final
bookends.
It must preserve the old failed wrapper and must not rewrite metadata, repin an
old guard, cast an old frame or imply every original parent exited0. No engine,
crypto, component, freeze or production admission is granted yet. The complete
roadmap, including the later optional host-capability phases, remains active.

Parallel Source progress: [private diagnostic v2](tests/node-compat/foundation-scheduler/combined-clock-diagnostics-candidate-v2/README.md)
is sealed at90efee09 with1,398 Source checks/72 synthetic cases. It implements a
cap8 synchronous probe on the actual owning queue and same-translation-unit
clock offset/wizen/origin observations, default OFF. Its357-source cohort is
349 retained+six changed+two new, with three separate embedding inputs/one
changed; it is distinct from Hash/Hmac357. It is uncompiled and not independently
Source-approved, and proves no link/ODR, natural-loop settlement, Store death,
teardown or runtime gate. Runtime Hash/Hmac fixture Source78008e58 supplies20
accepted and eight policy records but remains unexecuted. Root inspection finds
two setup calls outside the bounded Buffer API (from(Array) and Buffer.fill);
a small fixture successor is correcting those with supported Uint8Array paths
before the pinned Node oracle and any guest run. [Fixtures v2](tests/node-compat/foundation-crypto/node-crypto-hash-hmac-runtime-fixtures-v2/README.md)
is now sealed as16b195e6: exactly two expression changes use
Buffer.from(Uint8Array.of(...)) and Uint8Array.prototype.fill.call on its Buffer
window. All20/8 IDs and values remain unchanged; actual repo/staged Buffer
facade/manifest/factory inventory and static negative cases are checked.
A separate [pinned Node oracle](tests/node-compat/foundation-crypto/node-crypto-hash-hmac-node-oracle-v1-root-results.json)
finishes raw0 under original0af with clean ownership and three complete scalar
strings (calls1/2/3). Root validates60 accepted observations: all SHA/RFC vectors,
UTF8-surrogate bytes, block partitions, view mutation/copy, Hmac key snapshot,
output ownership and finalized-state behavior. All20 accepted records are equal
across calls. The24 policy observations, namespace descriptors and full host
constants/provider records remain separate; they do not imply guest parity.
Raw strings and original streams are retained. [Independent DATA review](tests/node-compat/foundation-crypto/independent-node-crypto-hash-hmac-node-oracle-results-review-v1/results.json)
passes at index `aa9a3ef4`: all60 accepted and24 separate policy observations,
complete strings, process completion and20 mutated-DATA refusals. The review
discloses fixture authorship and does not claim independent fixture Source
approval. Host-only constants/provider and accepted unsupported-profile calls
remain separate from native parity.
This is real host Hash/Hmac execution, with no guest or engine crypto invocation.

All-work checkpoint preparation on2026-11-06 verifies eight completed changed
indexed families:216 payloads/20,560,929 bytes, exact membership and all payload
hashes, including nested copied indices. Only each family's own root index is
excluded from its inventory. Status documentation passes whitespace checks.
The checkpoint includes source proposals, retained failures and unadopted native
candidate evidence; it does not promote those candidates. After its push, fresh
comprehensive Next.js build/HTTP/browser/Wasm replay, supported-module and
optional-package differentials execute against accepted v13. The linked
application report above records results, remaining failures and future checks.

Roadmap continuation after `ceb1ffe9`:

- Previous goal turn: **progress**. All872 changed files were committed and
  pushed as `ceb1ffe9810aea5bbbc4b2424324cc897bae32de`; remote `origin/main`
  matched and the worktree was clean. The full roadmap remains incomplete.
- The next work validates actual combined355 ordinary runtime behavior and the
  complete lifecycle fixture catalogue. Pure artifact review is complete;
  [resource artifact reviewce6fb731](tests/node-compat/foundation-scheduler/independent-combined355-resource-component-artifact-review-v1/results.json)
  now passes. Its exact three standard interfaces/five callable imports share
  the real pollable/drop graph; three scalar exports and all four core bytes
  are verified. The missing original construction tool response remains unknown;
  both actual terminal files are raw0 and clean. Clock-snapshot bundle preparation
  finishes raw0 at Root2014, with Root [whole-output observation](tests/node-compat/foundation-scheduler/combined-native-component-v1-bundle-clock-snapshot-root-results.json).
  Its separate fresh construction finishes raw0 at Root26228:
  [component5e020b28](tests/node-compat/foundation-scheduler/combined-native-component-v1-construct-clock-snapshot-root-results.json)
  is13,059,236 bytes, with exactly the three selected standard clock/poll imports.
  Whole publication/paired pre-load bundle bindings and final guards pass Root
  observation; independent artifact review and ordinary runtime remain pending.
  No ordinary export has run in this phase.
  Remaining construction, generated-output review and runtime calls require
  their own actual results. The accepted profile stays foundations-v13.
- A genuine combined355 runtime harness and a COPY-only experimental SHA256
  Hash/Hmac native integration recipe are being prepared. Their source work
  grants no build or runtime authority. The latter uses a new357-source frame,
  explicit new flag/manifest metadata and the existing guest OpenSSL target;
  the two diagnostic357 and Hash/Hmac357 generations are separate candidates.
- [Full runtime Source859957d7](tests/node-compat/foundation-scheduler/combined-native-runtime-candidate-v1/README.md)
  is now sealed:77,256 data checks across30,022 current inputs/36 families,
  140 pure cases and11 grammar checks pass. It requires an independently reviewed
  actual mapped Jco output before generated application import, parent-owned full
  native admission and authenticated children, all seven resource cases across
  the49/98/322 schedule, and separate clock/survivor/fatal/INIT-failure evidence.
  No API, ordinary worker, Node oracle, Wasmtime or guest action has run from this
  Source. [Independent reviewe22fa3fc](tests/node-compat/foundation-scheduler/independent-combined355-native-runtime-source-review-v1/results.json)
  now **holds** it on M1: unrelated post-arm Error/null/undefined/0/false throws
  satisfy its Jco fatal endpoint; deliberate and unrelated Error capture rows
  are identical. This is an authenticated pure validator counterexample, not an
  observed guest failure. The original Source remains immutable. A genuine v2
  successor must retain generic throws/traps as cause-inconclusive, with the
  expected-fatal gate false until specific evidence exists. All six fixtures and
  seventeen gates remain required; no runtime action is allowed from the held
  family. The remaining Source joins pass the bounded review.
- A preliminary pure-only runtime control is being prepared for the actual
  reviewed combined355 component: pinned Node oracle, three retained/one fresh
  Jco calls and three fresh stock-Wasmtime calls. It supplies no clock/resource,
  full Next, six-fixture acceptance or broader17-gate completion claim. The
  complete lifecycle harness continues independently.
- [Pure-control Source8feef25e](tests/node-compat/foundation-scheduler/combined-native-pure-runtime-control-candidate-v1/README.md)
  now passes [independent Source reviewca26fa82](tests/node-compat/foundation-scheduler/independent-combined355-pure-runtime-control-source-review-v1/results.json):
  full current Source/proof boundaries, real parent-only full80 admission,
  authenticated children and partial-failure retention. Root issues a separate
  [pure runtime phase](tests/node-compat/foundation-scheduler/combined-native-pure-runtime-control-v1-root-invocation.json)
  and starts it at62153/parent9047, with1,800s outer/1,200s inner parent and60s
  child bounds. The [actual run](tests/node-compat/foundation-scheduler/combined-native-pure-runtime-control-v1-root-results.json)
  now finishes raw0: three actual Node fixture values match all seven component
  values by call ordinal (three retained/one fresh Jco, three fresh Wasmtime).
  Retained calls increment1/2/3 and every fresh instance starts at1. All six
  child terminals and both original parent monitors are raw0 and clean; complete
  53-member output publication and native DATA9eaa pass Root checks. Independent
  [Independent runtime DATA reviewc3011423](tests/node-compat/foundation-scheduler/independent-combined355-pure-control-runtime-results-review-v1/results.json)
  passes all ten complete typed/WAVE values, whole UTF8/ordinal comparison,
  six owned commands, both parents, all publications and full current native/
  Source protection. It qualifies expected9eaa transport after fresh-record
  equality and Source-coupled time bookends. Reader-only pipe-mode and key-name
  mistakes are retained separately; no workload rerun or target failure occurred.
  All clock,
  resource, crypto, reset/reuse, deployment and adoption gates stay separate.
- [Hash/Hmac integration Source7c5a8468](tests/node-compat/foundation-crypto/node-crypto-hash-hmac-native-integration-candidate-v1/README.md)
  passes [Root independent Source review0a7ea900](tests/node-compat/foundation-crypto/independent-node-crypto-hash-hmac-native-integration-source-review-v1/results.json).
  It verifies2,622 declared input rows/2,676 unique current files/eight families,
  all54 tooling reversals,357-source arithmetic, new83-field schema and separate
  twelve-manifest scope; six independent command and five manifest checks pass.
  Native helper/staging/build/compiler/engine/crypto operations remain unexecuted.
  A new owned stage-controller Source is being prepared, with exact destination
  union and authenticated Git preimage overlays; it grants no staging action.
  The current experimental kernel has no INIT barrier on `createHash`/`createHmac`.
  Live EVP-context snapshot safety is already declared unproved. Before public
  crypto component admission, define and enforce that lifecycle policy or prove
  the supported snapshot state; guest malloc alone is insufficient evidence.
  Initial future crypto fixtures must create/use/finalize state inside deployed
  ordinary calls. No Hash/Hmac operation ran in the pure Buffer control.
- [Full-runtime v2 Source1cda0bd6](tests/node-compat/foundation-scheduler/combined-native-runtime-candidate-v2/README.md)
  passes [independent Source review42ed1306](tests/node-compat/foundation-scheduler/independent-combined355-native-runtime-v2-source-review-v1/results.json):
  exact28-file/70-edit successor, full current boundary and68 independent pure
  counterfactuals. Generic fatal throws/SIGABRT remain cause-inconclusive and
  unaccepted, with proof/gate false and no fatal PASS contract. All positive
  35-string/49-case/98-callback/322-ID resource scope and the actual mapped-output
  review barrier remain unchanged. Failed-positive-child receipts are explicitly
  best-effort; physical raw may survive without a complete failed index.
  A new [mapping-only resource phase](tests/node-compat/foundation-scheduler/combined-native-runtime-v2-resource-map-root-invocation.json)
  starts at50606/parent17800 with1,800s/1,200s bounds and finishes **raw1**.
  [Actual failure](tests/node-compat/foundation-scheduler/combined-native-runtime-v2-resource-map-root-results.json)
  retains all11 partial files: seven generated files, input/return-shape/static
  audit and failure records. The mapped audit passes, but `output.finish` raises
  `Ordinary acyclic JSON only`; no result/index/completion is published. Both
  original monitors terminate with clean ownership and no timeout/signals/errors.
  No generated application or guest export was invoked. Pinned Jco `prepOpts`
  mutates its input options, including an own undefined `flagsAsBigInt`, while
  this caller publishes the same object. That field attribution is Source-based
  inference, since the failed run did not capture post-call options. Independent
  failure DATA review and a genuine v3 publication fix are in progress; the
  failed mapped output remains unaccepted and may not authorize runtime.
  [Independent failure review30b21b1e](tests/node-compat/foundation-scheduler/independent-combined355-runtime-v2-resource-map-failure-review-v2/results.json)
  confirms the actual11-file/raw1 outcome, all Source/native protections and29
  host-only serialization/normalization/AST checks. Actual post-call options
  remain unobserved. The review's original publication omitted its result coverage
  join; its immutable v1 is held for whole-contract use. A tiny v2 repair supplies
  the matching coverage and references the original raw evidence; no source,
  native artifact, mapped byte or workload is changed or rerun.
  [Runtime Source v354a70237](tests/node-compat/foundation-scheduler/combined-native-runtime-candidate-v3/README.md)
  now passes [independent Source reviewecd595bc](tests/node-compat/foundation-scheduler/independent-combined355-native-runtime-v3-source-review-v1/results.json).
  It persists pristine requested options before Jco import, supplies an isolated
  workcopy/deep map, publishes only the request as input and records a typed
  post-call shape. Real-writer old-failure/pristine-success evidence is checked;
  all native/schedule/mapped-review/fatal-cause limits remain unchanged. Root
  issues a fresh [v3 resource map](tests/node-compat/foundation-scheduler/combined-native-runtime-v3-resource-map-root-invocation.json)
  at29603/parent26721 with1,800s/1,200s bounds. The [actual v3 map](tests/node-compat/foundation-scheduler/combined-native-runtime-v3-resource-map-root-results.json)
  finishes raw0 with13 payload files/15 total and seven complete generated files;
  both monitors are clean. The396-byte requested options stay pristine; typed
  post-call observation now records own `flagsAsBigInt: undefined` and Jco's
  extra default maps honestly. Those nonstandard `jco:node/*`/draft-TLS entries
  are unused: the original component still imports only three standard0.2.10
  interfaces and the mapped static graph uses only official clock/io shims.
  [Independent mapped DATA reviewfebf7c47](tests/node-compat/foundation-scheduler/independent-combined355-runtime-v3-resource-mapped-results-review-v1/results.json)
  now passes: all15 files, seven loading artifacts, pristine request/actual typed
  shape, original raw0 terminals and full Source/native protection are checked.
  The23 unused nonstandard default rules grant no capability or TLS support.
  Root issues a separate [ordinary resource phase](tests/node-compat/foundation-scheduler/combined-native-runtime-v3-resource-run-root-invocation.json)
  and starts it at55164/parent32525 with1,800s outer/1,200s inner bounds. This
  permits only the reviewed ordinary schedule:35 public strings,49 inner cases,
  98 callback observations and322 new timer IDs across retained/fresh Jco and
  three fresh Wasmtime processes. Its actual result and independent runtime
  review are pending. No fatal, crypto, native build or adoption follows. An
  initial Root launcher-generation assertion fails before any file/action;
  redundant text replacement is corrected before this launch. The old v2
  attempt remains failed and unchanged. A separate clock-snapshot mapping-only
  Root starts at30639/parent33375, invocation34760977, with the same1,800/1,200s
  bounds; its actual result, independent mapped DATA and ordinary calls remain
  pending. It does not reuse the resource mapping as a different fixture proof.
  Its original30639 tool later finishes raw0 and clean; [Root observation](tests/node-compat/foundation-scheduler/combined-native-runtime-v3-clock-snapshot-map-root-results.json)
  verifies all15 published files and the original inner/outer/Node frames.
  [Independent clock mapping DATA review07c61d25](tests/node-compat/foundation-scheduler/independent-combined355-runtime-v3-clock-snapshot-mapped-results-review-v1/results.json)
  now passes all15 actual files, seven loading artifacts, unchanged core/ABI,
  standard shim imports and full native protection. The pristine request is402B;
  actual typed undefined/default-map observations remain separate. Root issues a
  separate [ordinary clock phase](tests/node-compat/foundation-scheduler/combined-native-runtime-v3-clock-snapshot-run-root-invocation.json)
  at65943/parent49310 with1,800/1,200s bounds: three retained/one fresh Jco and
  three fresh Wasmtime strings, live host wall brackets with1ms coarse allowance,
  no `performance.timeOrigin` epoch assumption. Actual clock result/review remain
  pending at launch. The original65943 later finishes raw0/clean across all five
  commands; [Root clock observation](tests/node-compat/foundation-scheduler/combined-native-runtime-v3-clock-snapshot-run-root-results.json)
  authenticates42 payload/44 total files and all seven complete returns.
  [Independent clock runtime review5cb20028](tests/node-compat/foundation-scheduler/independent-combined355-clock-snapshot-runtime-v3-results-review-v1/results.json)
  now passes all seven strings, initialization/jobs/retained counters, Date/ISO
  host brackets and retained monotonic/origin continuity,20 mutation refusals,
  whole44-file publication and all five child/two parent clean0 layers. Actual
  `timeOrigin` values remain host-clock observations, without Unix-epoch, Node
  performance parity, native-offset or teardown claims. The first
  data-reader attempt looked for the Python terminal frame in Node publication
  stdout; its pre-write assertion is retained in a [preparation correction](tests/node-compat/foundation-scheduler/combined-native-runtime-v3-root-observe-preparation-correction-v1.json).
  Correcting that endpoint does not rerun the target. Separate mapping-only
  Roots for surviving-interest41448/parent42167 and fatal5482/parent42192 now
  start with1,800/1,200s bounds and fresh fixture-specific paths. Neither grants
  ordinary or fatal execution; actual mapped reviews remain required. Both
  original mapping tools subsequently finish raw0/clean and Root observes all15
  members each: [surviving-interest map](tests/node-compat/foundation-scheduler/combined-native-runtime-v3-surviving-interest-map-root-results.json)
  and [fatal map](tests/node-compat/foundation-scheduler/combined-native-runtime-v3-fatal-map-root-results.json).
  A new data-only observer v2 adds fatal mapping to its CLI and explicitly
  excludes fatal runtime classification; the already-used v1 stays unchanged.
  [Independent survivor mapping review73837797](tests/node-compat/foundation-scheduler/independent-combined355-runtime-v3-surviving-interest-mapped-results-review-v1/results.json)
  passes all15 files/seven loading artifacts, unchanged core/ABI, standard3
  bindings and native protections. Root issues a separate [ordinary survivor phase](tests/node-compat/foundation-scheduler/combined-native-runtime-v3-surviving-interest-run-root-invocation.json)
  at22922/parent54250, with1,800/1,200s bounds and the seven-string retained/
  fresh Jco/Wasmtime schedule. The original22922 later finishes raw0/clean;
  [Root survivor observation](tests/node-compat/foundation-scheduler/combined-native-runtime-v3-surviving-interest-run-root-results.json)
  authenticates42 payload/44 total files and all seven whole strings. Independent
  [actual survivor review98dc56ca](tests/node-compat/foundation-scheduler/independent-combined355-surviving-interest-runtime-v3-results-review-v1/results.json)
  now passes all seven strings:8 cancellations and two surviving Promise values
  per call, ordered fence/events, zero cancelled callbacks, retained1/2/3 and
  fresh1 counters, and retained ID continuity. Totals are77 per-instance ID
  observations/56 cancellations/14 values/35 events;22 mutations refuse. Full
  publication, all five child/two parent clean0 layers and frozen/native guards
  pass. Native interest/drop/all-invalid/offset/teardown remain unproved. Independent
  [fatal mapping review580e1f59](tests/node-compat/foundation-scheduler/independent-combined355-runtime-v3-fatal-mapped-results-review-v1/results.json)
  now passes all15 files/core/ABI/standard bindings and actual raw0 ownership.
  Its direct fields keep every fatal-runtime/cause/gate acceptance claim false.
  After the genuine actual resource prerequisite d77c, Root issues a separate
  [disposable fatal observation](tests/node-compat/foundation-scheduler/combined-native-runtime-v3-fatal-fatal-root-invocation.json)
  at52435/parent60456 with1,800/1,200s bounds. At most one fresh Jco and one
  fresh Wasmtime attempt may be observed; generic throws/traps stay
  cause-inconclusive and unaccepted. No current355 native callback diagnostic
  or expected-callback cause proof is invented. The [actual fatal observation](tests/node-compat/foundation-scheduler/combined-native-runtime-v3-fatal-fatal-root-results.json)
  finishes **raw1/unaccepted**: one Jco child exits1 with an actual pre-call
  marker/retained typed throw, and one Wasmtime child exits134 with a generic
  `unreachable` diagnostic. Both children and both parents have clean owned-group
  cleanup, no timeout/signalling/overflow/errors. Wasmtime does not retain the
  unique source marker; the parent correctly refuses that missing identity/reach
  evidence. All15 partial files are hashed; no owner result/index/completion or
  fatal-classification record exists. Generic failure does not prove the callback
  cause, native callback execution, original JS error identity or safe reuse.
  [Independent failure reviewa57873cb](tests/node-compat/foundation-scheduler/independent-combined355-fatal-observation-v3-failure-review-v1/results.json)
  now authenticates all15 partial files, real pure inconclusive classification/
  20 counterexamples, both nonzero children/two parents with clean cleanup and
  complete frozen/native protection. Its exact observation-review state means
  DATA review passed; the fixed outcome remains FAILED_OBSERVATION_CAUSE_INCONCLUSIVE_UNACCEPTED,
  phaseSucceeded/acceptedRuntimeObservation/expected-callback proof/gate allfalse.
  No workload is rerun.
- [Hash/Hmac stage-controller Source2395af2c](tests/node-compat/foundation-crypto/node-crypto-hash-hmac-stage-candidate-v1/README.md)
  passes [qualified independent Source reviewa703429a](tests/node-compat/foundation-crypto/independent-node-crypto-hash-hmac-stage-source-review-v1/results.json).
  Its1642 unique source destinations and three separate embedding DATA copies,
  checked Git preimages/independent inodes, exclusive fsynced overlays and failed
  journals are reviewed. No stage/Git/helper/build action has run. The v1 clone
  copies reachable history and has no history-byte ceiling; deadlines are refusal
  bounds. A genuine refinement is investigating baseline-only fetch and explicit
  Git hook/template isolation before Root issues actual staging. All original
  Source bytes and results remain held unchanged.
  [Baseline-only stage Source v2ed0a3241](tests/node-compat/foundation-crypto/node-crypto-hash-hmac-stage-candidate-v2/README.md)
  now passes [independent Source review11e462ea](tests/node-compat/foundation-crypto/independent-node-crypto-hash-hmac-stage-v2-source-review-v1/results.json).
  Its named recipe needs
  only Git HEAD/tree; Firefox tag/source paths are separate and bypassed by the
  selected prebuilt SpiderMonkey input. The new controller uses private empty
  template/hooks, depth1 literal54b fetch, explicit client/server Git and startup
  isolation, and retained single-history evidence. It keeps the same1642+3
  copy roles and makes no transient pack-byte/exact-object-set promise. No Git,
  native helper or build action has run from that Source review. Root issues a
  separate [stage-only phase](tests/node-compat/foundation-crypto/node-crypto-hash-hmac-stage-v2-root-invocation.json)
  and starts it at37816/parent30967, with1,200s outer/600s inner bounds and pinned
  canonical Git/Python executables. It may create the private source checkout,
  copy1642 source/tool rows and three embedding references; native configure,
  build, engine, crypto, GC and adoption remain forbidden. The [actual stage](tests/node-compat/foundation-crypto/node-crypto-hash-hmac-stage-v2-root-results.json)
  finishes raw0:1,642 source copies plus three embedding reference DATA files,
  234 authenticated baseline Git blob preimages and all eight Git commands pass.
  The staged detached checkout has exact54b HEAD, shallow history/reachable count1
  and no refs; its logical Git object bytes are857,258, without a transient
  storage-cap claim. Every copied file is hash-checked,0600, single-link and
  independent from protected inputs. Both monitors are clean; original Git
  object/config bookends are unchanged. WORK/FREEZE remain absent. Independent
  [actual stage DATA review7df115af](tests/node-compat/foundation-crypto/independent-node-crypto-hash-hmac-stage-v2-results-review-v1/results.json)
  passes:57,345 DATA plus19,684 independent Git-pack checks authenticate all909
  objects,742-entry baseline tree,234 overwritten preimages,508 retained entries
  and the whole copied Source ledger. Its independent current Git before/final
  snapshot covers159 files/145,844,245 logical bytes, equal in hashes and identity;
  historical source-controlled bookends remain separately qualified. All review
  writes stopped and the original Git protection window finished before Root
  creates the next authorized commit. A future owned build-controller Source
  [Source9e5195b9](tests/node-compat/foundation-crypto/node-crypto-hash-hmac-native-controller-candidate-v1/README.md)
  is now sealed:2,458 source/data/pure checks over5,058 inputs/15 families and13
  Python AST checks pass. It separates build from freeze, requires an independent
  actual357/83 BUILD proof/full ledger before freeze imports, uses genuine7c5a/
  0af/f751 contexts, and keeps INIT EVP/public crypto admission open. Independent
  [Source review85f29843](tests/node-compat/foundation-crypto/independent-node-crypto-hash-hmac-native-controller-source-review-v1/results.json)
  now passes5,082 current rows/16 families,91 independent inert cases and full
  actual API/phase/refusal checks. The issued Root must fully populate the
  skeletal templates using the real model and references. Root's first outer
  launcher uses7,500s, beyond the unchanged monitor's7,200s limit; it fails an
  assertion before any child/Source controller/cache/build/WORK is created.
  [Original refusal](tests/node-compat/foundation-crypto/node-crypto-hash-hmac-native-build-v1-root-results.json)
  is retained. A new [v2 Root build invocation](tests/node-compat/foundation-crypto/node-crypto-hash-hmac-native-build-v2-root-invocation.json)
  starts at14463/parent73627 with7,200s outer and7,200s inner refusal bounds,
  jobs1,2GiB start/800MiB stop floors, HASH-ON/COPY-only/entropy-OFF and no
  borrowing/GC/DEBUG/OOM. The source controller and metadata model stay unchanged.
  This is the first actual native build attempt for this generation; configure/
  compile/link and read-only inline metadata validation are allowed, but engine,
  component, crypto, freeze, snapshot and public-profile admission stay forbidden.
  The [actual14463 preparation](tests/node-compat/foundation-crypto/node-crypto-hash-hmac-native-build-v2-root-results.json)
  finishes **raw1 before recipe/compiler execution**. Its owner result records
  zero completed cache copies, rawChildExitCode null and preserved Source/cache
  inputs. The retained WORK contains only one162,093-byte archive, identical in
  hash to its source, distinct inode/single link, with actual mode0600 versus
  requested0644. Source sets umask077 and creates the file without fchmod before
  requiring0644; this Source-derived cause matches every retained predicate.
  The original caught assertion stack is absent, so that attribution remains
  explicitly Source-coupled. Both original parent monitors exit1 with complete
  owned-group cleanup/no timeout/signals/errors. No build.log, engine, metadata,
  recipe, compiler, crypto or freeze exists. Compact independent failure DATA
  [review11c1c14e](tests/node-compat/foundation-crypto/independent-node-crypto-hash-hmac-build-v2-root-preflight-review-v1/results.json)
  now passes the exact Root/preflight models,42 refusal mutations and the compact
  actual failed DATA wire. It verifies the complete original {output,result}
  frame, both clean raw1 parent lifetimes and every hash/inode/link/mode term,
  while keeping actualBuildSucceeded/buildAcceptance false. Its own initial
  bare-envelope reader assumption is retained and corrected within the review.
  Native source has not failed compilation; no compiler was invoked.
  A genuine controller v2 is being prepared with explicit owned-fd fchmod/fsync
  and real benign temp-copy tests under077 for0644/0755. Fresh WORK/freeze/output
  paths preserve the failed v1 files. An initial Root assumption that the recipe
  accepts arbitrary NODE_COMPAT_BUILD_ROOT is withdrawn: its line55 guard plus
  policy/helper/model work contexts bind v1. The fix therefore includes new owned
  producer/context afterimages, exact reversible edits and fresh actual83 output;
  unchanged7c5a native357/3/12 and actualstage7df remain ancestry, without global
  rebinding, restaging or old-metadata projection. New Source/peer/Root/build and
  all actual algorithm/snapshot/cost/adoption gates remain pending. The corrected
  [controller Sourcee8b47cc8](tests/node-compat/foundation-crypto/node-crypto-hash-hmac-native-controller-candidate-v2/README.md)
  is sealed and passes [independent Source review552b65af](tests/node-compat/foundation-crypto/independent-node-crypto-hash-hmac-native-controller-v2-source-review-v1/results.json):
  2,880 preparation checks/5,191 inputs/18 families/19 AST parses, five real tiny
  copy regressions under077, pinned Bash grammar and19-file/12-edit exact
  derivations. Native changes are zero. The peer checks5,230 current files/19
  families,103 inert cases and245 correction checks; retained real copy evidence
  has exact0644/0755 after fchmod and preserves old partial failures. A fresh
  [v3 Root build phase](tests/node-compat/foundation-crypto/node-crypto-hash-hmac-native-build-v3-root-invocation.json)
  starts at83192/parent80122 using the genuine new producer and V2 work/freeze
  roots,7,200s outer/inner bounds, COPY-only/HASH-ON/entropy-OFF/jobs1. Failed v1
  WORK/output and all native7c5a/stage7df source identities remain protected.
  The [actual83192 phase](tests/node-compat/foundation-crypto/node-crypto-hash-hmac-native-build-v3-root-results.json)
  now finishes **raw1 in early recipe authentication**. All four cache copies
  complete with correct hashes/modes/independent inodes, so the077 mode fix works.
  The recipe child starts and exits1 with clean lifecycle/group cleanup; both
  parent monitors also finish1 cleanly. The fresh ABI record and sourceDir/lib
  exist; the seven owner/five WORK files include an empty build.log. No archive
  extraction, helper CLI, dependency fetch, CMake configure, compiler, engine,
  metadata, crypto or freeze is reached. Its new policy is b2421527, while both
  shell policy guards at recipe lines194/204 still require old99f15d4a; the helper
  guards and helper POLICY_SHA match the new policy. This Source-coupled cause
  is qualified by the absent original Bash execution trace. [Independent failed
  DATA reviewf05f9285](tests/node-compat/foundation-crypto/independent-node-crypto-hash-hmac-build-v3-failure-review-v1/results.json)
  now passes all four full cache-copy byte/mode/inode records, seven owner/five
  WORK members, whole JSON/raw lifetimes and exact stale/correct guard joins.
  Both parent/recipe nonzero lifetimes have clean cleanup; actualBuildSucceeded
  remains false. Its recipe process sample has PID/group but only `(bash)` as
  command; full argv is not inferred from that sample. The two reviewer-only
  envelope/key assumptions are retained. Old Sourcepeer552b stays immutable and
  its missed cross-file literal join is recorded. A genuine Sourcev3 successor with fresh
  WORK/freeze/output paths, all policy/helper guard joins and a stale-literal
  regression is being prepared. Native7c5a source remains unchanged and uncompiled
  by these attempts; actual algorithm/snapshot/cost/adoption gates remain open. A private diagnostic-fixture Source audit additionally finds that
  current7aed exports only `snapshot()`: JS cancellation erases queued tasks, so
  it cannot create an all-invalid selector queue, and no native resume-offset
  field is exposed. Those requirements remain blocked by missing guest-only test
  instrumentation, rather than being replaced with public JS counters. The compact
  [fixture Source3c337c1a](tests/node-compat/foundation-scheduler/combined-clock-diagnostic-fixtures-candidate-v1/README.md)
  passes [bounded Source reviewc9af5ff0](tests/node-compat/foundation-scheduler/independent-combined-clock-diagnostic-fixtures-source-review-v1/results.json).
  Its three real API wrappers/seven unchanged resource bodies/45 synthetic and23
  independent cases keep fullGateAccepted false, even for synthetic pruning.
  This is a missing-instrumentation finding, not an impossible passing guest.
  Native offset fields live in runtime/js.cpp (`mono_clock_offset`, `wizen`);
  the actual owning queue/selector and post-selection settlement need distinct
  guest-only seams and real link/transition proof. A synchronous quiescent actual-
  queue selector probe could cover that branch, while natural event-loop settlement
  and Store/fatal/cached-drop proof remain separate. No diagnostic native build
  is issued from the insufficient v1 interface. Diagnostic v2 Source design is
  deferred temporarily while the native cache-mode correction is prepared.
- Checkpoint **1d5edac05f902501c52d8c01690c418a80777f06** commits all1,527
  changed files and is pushed to `origin/main`; `git ls-remote` returns the same
  full SHA and the worktree is clean immediately after push. The next operations
  below continue the roadmap, which remains incomplete. Editable documentation
  whitespace checks pass;3,799 warnings in six byte-exact raw generated captures
  and one sealed Source EOF are preserved instead of altering authenticated bytes.
- After1d5, a read-only closure audit verifies13 completed indexed families:
  705 payloads/718 actual regular files,12,374,845 payload bytes, all12 nested
  copied indexes and the full resource family including its previously tracked
  planning files. It excludes the then-active V2 Source peer; that peer is now
  independently sealed as552b. No closure/path/hash/symlink issue is found.
  The next all-work checkpoint includes these final results, both native
  preparation refusals, the real copy-mode regression/fix and the completed
  failed83192 invocation plus Source-coupled policy-guard finding. The complete roadmap remains in progress.
- This all-work checkpoint includes21 newly sealed families:1,423 indexed
  payloads/14,640,973 bytes pass Root whole-membership/hash checks, including
  nested copied indexes. The resource runtime review directory contains four
  closed, explicitly UNSEALED planning files; no result/index/receipt or runtime
  review is claimed. All review writers are held during the authorized Git
  snapshot. Ordinary resource55164 and clock-map30639 continue externally;
  their configs/invocations are recorded, results still pending at this snapshot.
  The subsequent [resource runtime55164](tests/node-compat/foundation-scheduler/combined-native-runtime-v3-resource-run-root-results.json)
  finishes raw0 with both original monitors clean and all five commands0. Root
  authenticates70 payload/72 total files, including both complete nested child
  indexes/completions and original Node/Python output frames. Whole declared
  coverage is35 public strings/49 inner cases/98 callbacks/322 new timer IDs.
  [Independent actual resource reviewd77c82e2](tests/node-compat/foundation-scheduler/independent-combined355-resource-runtime-v3-results-review-v1/results.json)
  now passes the full whole-string/case/ID schedule,20 retained-DATA mutation
  negatives, all72 files including nested indexes, five child/two parent raw0
  layers and full native/frozen protection. The exact same-index whole contract
  fulfills the handled-error resource prerequisite for a later separate fatal
  observation. The322 ID observations are newly issued within each instance;
  fresh instances intentionally reuse ranges, so global uniqueness is not claimed.
  This is not full17-gate/profile acceptance, native-interest/drop/
  teardown, failed-instance reuse, Node Timeout-object parity or adoption proof.
- Surviving-interest, fatal and INIT-fatal bundles finish raw0 at Root33382,
  68649 and98293 with clean owned groups and complete native-manifest bindings.
  Their separate constructions finish at Root86269/37335 raw0 and26507 raw1,
  each with isolated output/private TMP and a pre-bound actual bundle SHA.
  [Surviving-interest71076407](tests/node-compat/foundation-scheduler/combined-native-component-v1-construct-surviving-interest-root-results.json)
  is13,071,576 bytes; [fatal9d28937f](tests/node-compat/foundation-scheduler/combined-native-component-v1-construct-fatal-root-results.json)
  is13,060,568 bytes. Both select the same three standard clock/poll interfaces.
  [INIT-fatal](tests/node-compat/foundation-scheduler/combined-native-component-v1-construct-init-fatal-root-results.json)
  returns no component and captures the Wizer diagnostic identifying a top-level
  `TypeError: setTimeout can only be used during request handling, not during initialization`.
  Its original inner/outer exit1 is retained; all owned groups are gone with no
  timeout, forced cleanup, signals or monitor errors. This is the observed
  initialization refusal, not an accepted component or ordinary fatal-callback
  result. All six bundles and five positive constructions now have terminal
  outputs. [Independent DATA reviewea27e5ee](tests/node-compat/foundation-scheduler/independent-combined355-remaining-component-artifact-review-v1/results.json)
  now passes the complete six-outcome construction contract, joining immutable
  pure/resource peers with three fresh scalar type/core/glue graphs and the
  specific INIT refusal. This means **five accepted artifacts plus one identified
  unaccepted failure**, not six accepted components or runtime acceptance. All
  per-case contracts, complete publications and process evidence are bound.
  Ordinary clock/resource/fatal/survivor calls remain unexecuted; the separate
  pure-only runtime result is recorded above. The
  [Root DATA observer](tests/node-compat/foundation-scheduler/combined-native-component-v1-root-observe.py)
  verifies published hashes/membership and actual terminals, writes fresh Root
  observations, and cannot launch a process or grant ordinary runtime/adoption.

Roadmap continuation after `30517ee6`:

- Previous goal turn: **progress**. All checkout changes were committed and
  pushed; remote `origin/main` was verified as `30517ee67fde903febf90c16db23842fa3da4933`
  and the worktree was clean. Full roadmap remains incomplete.
- Combined artifact-tooling Source `c365e608` now passes independent
  [Source review4df251c3](tests/node-compat/foundation-scheduler/independent-combined355-native-artifact-tooling-source-review-v1/results.json)
  for genuine full80 input models, full compact protection, real own
  contexts and pure/grammar checks. The [actual export-only phase](tests/node-compat/foundation-scheduler/combined-native355-artifact-v1-export-root-results.json)
  finishes at Root40725 raw0: outer parent46729 and worker47096 under genuine
  nested1,200s/600s monitors, all observed groups gone with no timeout/signals/
  errors. Candidate `435b30fe` is1,574,865 bytes; native frame `5c5c521f` is
  744,251 bytes. Compact worker JSON and formatted candidate differ in bytes
  but have equal complete parsed values; both raw formats remain retained.
  Final protection passes. Independent actual export review passes below.
  No engine or guest action has run; the subsequent validation bootstrap is
  recorded below. The export has exactly five output files and no producer index/completion;
  its reviewer authenticates full native80/355+3/eleven-manifest DATA,
  whole raw candidate JSON and owned cleanup before the pin/bootstrap phase.
- [Export DATA review21d82edd](tests/node-compat/foundation-scheduler/independent-combined355-native-pin-export-results-review-v1/results.json)
  passes all five files, whole parsed candidate/worker equality, full80 frame,
  2,596 frozen rows and both owned monitor results. Root issues validation-only
  pins `a31710b3` with exactly four state/reviewRequired changes; all native data,
  NULL variants and runtime/adoption restrictions remain unchanged. The [actual
  bootstrap phase](tests/node-compat/foundation-scheduler/combined-native355-artifact-v1-bootstrap-root-results.json)
  finishes at Root10796 raw0 (parent50367/worker50636), under1,200s/600s monitors.
  Frame `c9f61b8f` is3,036,236 bytes; full native frame `5c5c521f` is unchanged
  from export. Both monitor cleanups and final protection pass. Independent
  [Bootstrap DATA reviewfa45a2af](tests/node-compat/foundation-scheduler/independent-combined355-native-bootstrap-results-review-v1/results.json)
  passes full frame/pin reconstruction, whole raw JSON and both monitors. No
  engine or guest call occurs. The [actual retained read-only API test](tests/node-compat/foundation-scheduler/combined-native355-artifact-v1-read-only-root-results.json)
  finishes at Root43356 raw0 (Node54826): two full3,112,808-byte data returns are
  identical; fresh recheck functions and three rechecks pass. Current API helper/
  process/write counts remain0, separate from the historical CLI verifier count1.
  [Independent read-only DATA reviewfd06076b](tests/node-compat/foundation-scheduler/independent-combined355-retained-read-only-results-review-v1/results.json)
  passes the actual records/shapes and full current protection, with original
  timing/zero-action counts qualified by inspected Source/control flow.
- Root's bounded pure review of lifecycle Source6cfcc7e4 finds a collector gap:
  a synthetic record with `current=1` and run/started counters9 is accepted.
  Completed-versus-started relations are also missing. This is a test-validator
  finding, not a guest failure. The v1 collector is held for runtime consumption;
  its fixture bytes remain unchanged. A genuine v2 successor tightens those
  relations with negative tests and actual new catalogue paths. [Successor
  960a3b26](tests/node-compat/foundation-scheduler/combined-clock-lifecycle-candidate-v2/README.md)
  passes [independent Source reviewb791b56b](tests/node-compat/foundation-scheduler/independent-combined355-clock-lifecycle-v2-source-review-v1/results.json):
  49 pure checks, eight grammar checks, all source anchors and two independent
  malformed records admitted by v1 but rejected by v2. The initial Root reader
  assumed descriptor-only reference rows; its corrected read/hash result and
  failed preparation code remain separate. No old source/runtime evidence is
  rewritten and all17 runtime gates remain unexecuted.
- The [357-source diagnostic template7aed33ec](tests/node-compat/foundation-scheduler/combined-clock-diagnostics-candidate-v1/README.md)
  is Source-only with default-OFF private read-only queue/interest/timer-lease/
  cache/post-call observations. Its512-row lease ledger reports overflow and
  incomplete recording explicitly; source collectors reject both. It adds no
  current355 export and is not linked/admitted. Actual fixed-source SDK
  [syntax checks29815de8](tests/node-compat/foundation-scheduler/combined-clock-diagnostics-sdk-syntax-v1/README.md)
  and the [new-file driver retryb6a2a716](tests/node-compat/foundation-scheduler/combined-clock-diagnostics-sdk-builtin-retry-v1/README.md)
  pass all five translation units, across six driver invocations. The initial
  new-file path failure is retained. These are front-end checks only: no native
  build, link, diagnostic engine, guest call or lifecycle acceptance follows.
- [Combined component-caller Sourceaec12b5c](tests/node-compat/foundation-scheduler/combined-native-component-caller-candidate-v1/README.md)
  passes [independent Source reviewa4c441dd](tests/node-compat/foundation-scheduler/independent-combined355-component-caller-source-review-v1/results.json).
  It uses real c365 retained full80 admission, the real clock loader and separate
  bundle-preparation/fresh-construction Nodes. Root binds each actual bundle SHA
  in paired loader/construction records before loading. Both actual bundles
  retain native `node:buffer`; no JavaScript Buffer adapter is substituted.
  [Pure construction](tests/node-compat/foundation-scheduler/combined-native-component-v1-construct-pure-root-results.json)
  returns component `181b59fd`,13,053,537 bytes, imports[], `run()->string`;
  [resource construction](tests/node-compat/foundation-scheduler/combined-native-component-v1-construct-resource-root-results.json)
  returns `5599dd8a`,13,092,238 bytes, with exactly the selected monotonic-clock,
  wall-clock and poll interfaces at0.2.10. Both original inner/outer terminals
  are raw0 with clean owned groups; whole publication hashes and membership
  pass Root observation. Resource's tool response was lost during compaction;
  its report records the actual terminal files without reconstructing a session
  ID. [Pure artifact review0dc8bf11](tests/node-compat/foundation-scheduler/independent-combined355-pure-component-artifact-review-v1/results.json)
  passes the actual component/type/core/glue and both owned phases; its explicit
  per-pure result leaves the other five fixtures unaccepted. No ordinary guest export or generated
  application module has run. Resource artifact review, remaining four fixture
  constructions, all runtime/lifecycle gates and overall six-fixture acceptance
  remain open; neither component promotes the355 engine.
- [Native SHA256 Hash/Hmac Sourceafdbefde](tests/node-compat/foundation-crypto/node-crypto-hash-hmac-candidate-v1/README.md)
  passes [independent Source review1c23afaf](tests/node-compat/foundation-crypto/independent-node-crypto-hash-hmac-source-review-v1/results.json).
  It specifies bounded update/digest methods, explicit named/default exports and
  unsupported operations, meaningful partial constants and native WebCrypto
  aliases. Default message handling copies; an experimental borrowed path is
  separately gated. Both flags default OFF. Actual SDK syntax checks pass the
  registrar and kernel in COPY and BORROW modes; the [SDK receipt9b237805](tests/node-compat/foundation-crypto/node-crypto-hash-hmac-sdk-syntax-v1/README.md) records
  the installed guest OpenSSL headers and retained reader-preparation failure.
  Source remains unapplied to production. No real Hash/Hmac algorithm/provider,
  native build/link, component, runtime, alias, GC, erasure or performance gate
  has run. These templates do not add accepted `node:crypto` support.

Checkpoint validation on2026-11-06: all16 new indexed evidence families pass
exact membership and SHA checks (810 indexed members,826 files including their
own indices). New JSON and Python grammar checks pass, and no binary or file
over50MiB is staged. Whitespace warnings are confined to the byte-preserved
upstream Node license and captured generated Jco glue; editable documentation
passes. Those captured bytes remain unchanged.

The five existing read-only framework checks were rerun with pinned Node22.14.0:
Next baseline/replay comparison, its43 self-tests, optional package baseline/
replay comparison, its40 self-tests, and the selected-clock checker with seven
whole returns and18 semantic negatives. All exit0 with no regression or changed
blocker. The17 known main-Next failures and seven optional-matrix failures remain.
These checks inspect retained evidence; no new framework build, server, browser
or component runtime was executed by this checkpoint recheck. The
[Next runner/checker commands](tests/node-compat/frameworks/nextjs/README.md)
and [package/clock checker commands](tests/node-compat/frameworks/package-bundler-execution-v1/README.md)
remain the reusable regression entry points. Full Next HTTP/Wasm, request
context, broader module support and deployment/reuse gates remain outstanding.


Roadmap continuation after `9806b383`:

- Previous goal turn: **progress**. All 473 pending files were committed and
  pushed to `origin/main`; remote HEAD was verified as `9806b383`. The worktree
  was clean at the start of this continuation. Full roadmap remains incomplete.
- The [private Rustup diagnostic review](tests/node-compat/foundation-scheduler/independent-rustup-private-bootstrap-probe-review-v1/results.json)
  passes (`fa0fc90a`): six exact raw-zero commands, persistent private setting,
  target installation, repeated install and Cargo proxy. All 4,253 prior observed
  inputs and the failed build's 755-file membership remain unchanged. Recorded
  process/files corroborate the private Rustup home; whole child environments
  and private Cargo/home values are not independently attested. This is a
  bootstrap diagnostic, not native build authority.
- Independent clock-loader source review finds one concrete blocker: the second
  loader call refuses before running the retained protection recheck promised
  by its documentation. [The held review](tests/node-compat/foundation-scheduler/independent-clock-package-loader-source-review-v1/results.json)
  preserves that finding and otherwise verifies the declared package/proof
  closure. The genuine [v2 successor](tests/node-compat/foundation-scheduler/clock-package-loader-candidate-v2/README.md)
  now passes [independent Source reviewd0b13291](tests/node-compat/foundation-scheduler/independent-clock-package-loader-v2-source-review-v1/results.json):
  all 5,080 inputs/eight families, 4,889 regular files/21 aliases/25 artifacts,
  exact ten-edit reversal and 67 independent pure model checks. The original
  held source remains unchanged. No actual package or engine runs by that review.
- [Crypto construction source v2](tests/node-compat/foundation-crypto/ownership-secret-component-candidate-v2/README.md)
  is sealed at `6a17edae`, with new source/config/output contexts, full prior
  failure evidence and explicit checks for both required packaging paths before
  custom imports. All 33,364 inputs/27 families (2.461 GB logical) pass read/hash
  validation; 20 host-only pure checks pass. The inherited guarded guest/WIT,
  355 native files, three embedding sources, 75 metadata fields and eleven
  manifests remain intact. [Independent source review05323098](tests/node-compat/foundation-crypto/independent-ownership-secret-component-v2-source-review-v1/results.json)
  passes full input/native/packaging joins and separately checks the Root caller.
- The Root v2 crypto observer passes 22 pure lifecycle/environment checks. It
  uses the original owned monitor, a fresh Node process and temporary directory,
  exact packaging paths, retained raw streams and pre/final protection checks.
  The fresh [Root v2 construction phase](tests/node-compat/foundation-crypto/ownership-secret-component-v2-root-results.json)
  completes at Root session37855 exit 0: canonical-Python parent93692 and
  Node93759 both finish cleanly under hard 2,400s/1,800s nested monitors. The
  actual child environment sets and records both authenticated packaging paths.
  Component `c067000d…` is 13,057,762 bytes, with imports[] and the four original
  inspect/run(u32)/clear/validate WIT functions. All 33,407 Root-protected files
  pass final checks. Guest initialization completes without ordinary exports,
  key workloads or generated-module imports. [Independent artifact review28bc2f47](tests/node-compat/foundation-crypto/independent-ownership-secret-component-v2-results-review-v1/results.json)
  passes 257,329 checks, verifying the whole embedded core, four-function ABI,
  raw nested cleanup, package/native protection and loading protocol. Generated
  glue differs from its previously parsed full predecessor only in the exact
  core filename literal. No generated module or guest function is run by this
  review, and no runtime compatibility is claimed.
- [Native-build retry source v2](tests/node-compat/foundation-scheduler/combined-native-build-controller-candidate-v2/README.md)
  is sealed at `24584f96`: 4,515 inputs/twelve families, 78 pure cases and 43
  reversible edits across five files. It keeps staged355 unchanged and uses its
  own actual recipe/helper/work context, persistent private auto-self-update
  disable and integrated clean launcher. The failed 755-file work tree stays
  protected rather than used as a cache. [Independent Source review0430a712](tests/node-compat/foundation-scheduler/independent-combined355-native-build-controller-v2-source-review-v1/results.json)
  passes. It independently parses six actual Python heredoc occurrences; the
  author counted five unique delimiter names, an evidence-count qualification.
  The [fresh actual build](tests/node-compat/foundation-scheduler/combined-native355-v2-build-root-results.json)
  completes at Root61477 exit 0, owned worker795 under the 7,200s monitor.
  Private Rustup bootstrap, SDK/OpenSSL setup and all 108 build steps pass.
  Engine `355550f1…` is 10,007,568 bytes; sidecar `5f3be885…` has **80 actual
  fields**, full355+3 source manifests, eleven selected manifests and complete
  private-Rustup configuration provenance. The pre-install record retains a
  historical 57-byte settings digest, with enforcement observed through the
  unchanged Source-controlled guard; those raw 57 bytes were not archived. The
  actual post-install 107-byte settings are retained separately. Source/stage/cache guards and
  owned cleanup pass. The failed v1 roots stay protected. [Independent BUILD
  DATA review1a67eb2f](tests/node-compat/foundation-scheduler/independent-combined355-native-build-v2-results-review-v1/results.json)
  passes 20,816 actual references, full compile/SDK/library data and 757 raw text
  copies. Compile facts use fresh build/source/DB/object/post-build-command
  evidence, with no standalone per-compiler raw terminals. Ancestor preservation
  is the declared current closure, not a recursive audit of every old freeze.
  [Freezer source5230be98](tests/node-compat/foundation-scheduler/combined-native-freezer-candidate-v1/README.md)
  is sealed with a finite 2,544-copy/653.8 MB base plan, full80 metadata, actual
  current355 producer/model APIs and frozen-only verification. Independent source
  [Source review6a74baab](tests/node-compat/foundation-scheduler/independent-combined355-native-freezer-source-review-v1/results.json)
  passes, including actual untouched path constants and the full copy/protection
  boundary. The donor monitor has the same ownership logic as original0af with
  its ceiling narrowed from7,200s to2,400s; its whole-file hash is distinct.
  [Actual freeze](tests/node-compat/foundation-scheduler/combined-native355-v2-freeze-root-invocation.json)
  finishes at Root4533/owned worker32744 raw0 under that 2,400s monitor. All
  observed owned processes are gone, with no timeout, signals or cleanup errors.
  Receipt `9ce68140` retains 2,596 copies and the unchanged engine/full80
  metadata. Read-only source admission and post-build Ninja capture pass;
  engine, bootstrap and guest execution remain closed. [Independent actual
  freeze reviewe6f9cdcc](tests/node-compat/foundation-scheduler/independent-combined355-native-freeze-v2-results-review-v1/results.json)
  passes every frozen copy/original pair, unique inode/mode, full native/metadata
  frame and raw owned cleanup. Its compact current-payload ledger refers to the
  existing BUILD ledger rather than copying historical trees again. Native
  admission/export/bootstrap tooling is being implemented; runtime remains open. The verifier
  reads frozen payloads/models and self-authenticates its active original source;
  this does not establish that every read was confined to the frozen tree. This combined frame must not be projected into the distinct
  75-field crypto frame.
- The [selected-clock application caller source](tests/node-compat/foundation-scheduler/clock-v13-component-candidate-v1/README.md)
  is sealed at `555b8f10` (11,581 inputs/eleven families, 21 data models and
  grammar checks), with [independent source review7bca0062](tests/node-compat/foundation-scheduler/independent-clock-v13-component-source-review-v1/results.json)
  passed. It uses genuine v13
  `classicPreflight` read/hash admission (full342+3/nine manifests/64-field raw
  sidecar), the exact retained ReactDOM-edge bundle and the reviewed new loader.
  Its historical native-admission environment paths remain separate from the
  new package selection. It imports no old bundler/Jco before the new package.
  [Actual construction](tests/node-compat/foundation-scheduler/clock-v13-component-v1-root-results.json)
  finishes at Root30114 exit 0 (Python1494/Node1798, hard 2,400s/1,800s monitors,
  clean shutdown). Component `5c002f8d…` is 15,693,386 bytes and imports exactly
  wall-clock, monotonic-clock and poll at0.2.10; no selected interface is unused.
  Its sole WIT export remains run()->string. The full original ReactDOM bundle
  and native engine are unchanged. [Independent artifact/type-graph reviewb07378f3](tests/node-compat/foundation-scheduler/independent-clock-v13-component-results-review-v1/results.json)
  passes exact callable/resource bindings and all four embedded cores. Internal
  Preview1 clock calls and adapter0.2.0 labels resolve wholly inside the component
  to its three real0.2.10 imports; no external Preview1/old-version/stdio/error
  interface exists. Authorized host-only grammar/AST parsing passes without any
  generated module, component or guest execution during that artifact review.
  The subsequent separate first render is recorded below.
  This is the first construction probe, with the full seven resource cases,
  Date/monotonic/snapshot/timer/task-lifetime and host tests still required.
- The guarded [crypto runtime caller source](tests/node-compat/foundation-crypto/ownership-secret-runtime-candidate-v1/README.md)
  is sealed at `6afdb00a`, preserving three fresh sessions, 23 full public strings,
  20 inner cases and 45 complete successful tags against pinned Node/RFC oracles.
  Review finds a combined diagnostic failure: when both the guest invocation and
  raw-result writer throw, the writer error masks the original exception.
  The source remains held. The v2 successor fixes both diagnostic paths and
  passes 234 host-only assertions. Before runtime issuance, Root catches another
  source error: its external runner still defines OWN as the old v1 directory.
  Root's first v2 Source PASS missed that constant and is explicitly superseded
  for activation by the [context HOLD](tests/node-compat/foundation-crypto/independent-ownership-secret-runtime-v2-context-correction-v1/results.json).
  No runtime authority, key or prototype workload was issued or executed.
  The genuine [v3 successor](tests/node-compat/foundation-crypto/ownership-secret-runtime-candidate-v3/README.md)
  is sealed at `1f357d3a`: 34,167 inputs/35 families plus the separately declared
  historical donor tree and the same 234 host-only assertions pass. Tests import
  the actual inert external module and compare its untouched OWN/OUTPUT/OUT and
  __file__ constants directly, without a substituted model namespace. All
  compiled artifacts, guest/ABI, oracles and schedules stay unchanged.
  [Independent v3 Source review421fd1b1](tests/node-compat/foundation-crypto/independent-ownership-secret-runtime-v3-source-review-v1/results.json)
  passes, including actual untouched module constants and fresh capture/error
  checks. The separate [guarded runtime phase](tests/node-compat/foundation-crypto/ownership-secret-runtime-v3-root-invocation.json)
  completes at Root37217 exit 0, owned Node parent22906 under its 2,400s
  watchdog. [Actual runtime results](tests/node-compat/foundation-crypto/ownership-secret-runtime-v3-root-results.json)
  retain all three fresh sessions: 23 full public strings, 20 case records,
  ten imports, 55 sign/50 verify attempts and 45 full Node/RFC-matching tags.
  All four guarded cases remain present, including case3 on the verified c067/
  901c guard. Final source/native/API/package checks and owned cleanup pass.
  [Independent actual-result reviewe895e34c](tests/node-compat/foundation-crypto/independent-ownership-secret-runtime-v3-results-review-v1/results.json)
  passes all23 strings/20 full records/45 tags, 45 verification booleans,
  fifteen native-promise TypeError refusals, twenty guarded getter checks and five
  constructor checks, plus raw parent/three-worker cleanup. Current Source/package
  and mode checks pass; original final-check timing is Source-coupled, without
  standalone actual-time snapshot inventories or whole-environment attestation.
  DEBUG/OOM/pressure/fault/reset/other variants remain unexecuted; no native-free/
  wipe or request-reuse claim. A separate stock-Wasmtime host caller source is
  sealed at [851392e5](tests/node-compat/foundation-crypto/ownership-secret-host-candidate-v1/README.md)
  around this exact new runtime DATA proof. [Independent Source review3392d951](tests/node-compat/foundation-crypto/independent-ownership-secret-host-source-review-v1/results.json)
  passes full declared inputs and 68 pure checks, with no engine action. The
  separate [Root host phase](tests/node-compat/foundation-crypto/ownership-secret-host-v1-root-invocation.json)
  completes at Root49701 raw0: three fresh Wasmtime validate() calls return
  whole strings equal to the reviewed Jco wrapper, covering twelve inner cases,
  27 full Node/Jco-matching tags and 27 verification booleans (15 true/12 false).
  All four guarded cases run on c067/901 only. Source-controlled final checks
  and owned cleanup pass. [Independent actual DATA review5fe406ba](tests/node-compat/foundation-crypto/independent-ownership-secret-host-results-review-v2/results.json)
  reconstructs all three whole WAVE strings, all counters/tags and three fresh
  child PIDs plus parent/four clean groups. It retains forty current raw text
  copies and references the fixed declared intake without recursive history
  expansion. Actual-time protection remains Source-coupled, with current hashes
  and raw0; no invented historical snapshots. This is separate fresh
  instantiation, with no request reuse, GC-pressure or wiping proof.
- A [separate first stock-Wasmtime rendering probe](tests/node-compat/foundation-scheduler/clock-v13-wasmtime-first-render-v1-comparison.json)
  completes at Root24861/Wasmtime22455 raw0 under a60s owned watchdog. The
  entire decoded return equals the retained Node oracle: real ReactDOM produces
  `<p id="wasm-ssr">Hello from real ReactDOM</p>` and bytes45. Pre/final full
  input/native/component checks and cleanup pass. This is one fresh host call,
  with no fresh Node oracle, Jco call, retained-instance or wasmCloud result.
  [Independent first-render DATA reviewd0f9d1ed](tests/node-compat/foundation-scheduler/independent-clock-v13-first-wasmtime-render-results-review-v1/results.json)
  passes a separate full raw WAVE decode and current input/component checks.
  The original pre/final 11,935-path check count is Root/control-flow evidence;
  no independent actual-time ledger was saved and no older construction
  bookend is transferred. The former Wasmtime clock-subscription trap is resolved
  for this exact workload, without overwriting its old failed baseline.
- The [full selected-clock runtime Source](tests/node-compat/foundation-scheduler/clock-v13-runtime-candidate-v1/README.md)
  is sealed at `3107eee7` with 11,995 inputs/sixteen families, 81 pure cases and
  five grammar checks. [Independent review05ec90ba](tests/node-compat/foundation-scheduler/independent-clock-v13-runtime-source-review-v1/results.json)
  holds it on a null-exception sentinel: an intermediate fresh-child completion
  can be mislabeled after a synthetic literal-null throw. The parent rejects
  every raw throw, so this cannot yield a full differential PASS. No guest
  failure or runtime action is inferred. The genuine [v2 successor135d1e45](tests/node-compat/foundation-scheduler/clock-v13-runtime-candidate-v2/README.md)
  uses explicit exception-presence flags at all five relevant catches, retains
  failure-presence fields and fresh own/Root/config/output contexts. Full
  12,079 inputs/eighteen families, 81 inherited plus 52 presence checks and six
  grammar checks pass. Component, native bytes, all four cores, oracle, maps and
  schedule remain unchanged. [Independent v2 Source reviewdd8f93f5](tests/node-compat/foundation-scheduler/independent-clock-v13-runtime-v2-source-review-v1/results.json)
  passes, including 80 checks of the actual extracted failure statements plus
  the inherited/presence suites (213 pure checks total). The separate mapping-only
  phase completes at Root19813 raw0 under the genuine 1,200s external monitor.
  Actual mapped core `2f086827` remains unchanged; seven generated files include
  glue `ff45f429`. It invokes Jco tool helpers without importing or running the
  application module. [Independent actual mapped-output review8ab62207](tests/node-compat/foundation-scheduler/independent-clock-v13-mapped-v2-results-review-v1/results.json)
  passes the complete generated source/standard binding graph, all four core
  bytes, unchanged glue suffix, ABI, raw cleanup and current declared inputs.
  Root separately records [the actual mapping67c7a2a9](tests/node-compat/foundation-scheduler/clock-v13-mapped-output-v2-root-review.json).
  The [genuine runtime differential](tests/node-compat/foundation-scheduler/clock-v13-runtime-v2-root-results.json)
  finishes at Root33981 raw0: three retained plus one fresh Jco and three fresh
  Wasmtime returns all equal the complete Node result. Five child terminals and
  outer cleanup complete; Source-controlled final checks pass.
  [Independent actual DATA review54683955](tests/node-compat/foundation-scheduler/independent-clock-v13-runtime-v2-results-review-v2/results.json)
  passes all seven full strings, five child PIDs/six owned groups, all three
  unchanged full native-frame captures and current declared protection. It
  retains 62 actual raw text copies without recursive ancestor copying. Original
  protection timing remains Source-coupled, without invented snapshot ledgers.
  The seven resource/Date/snapshot/timer/teardown gates remain open; no host-call
  counts or full Next result are inferred.
- The new [read-only clock record checker](tests/node-compat/frameworks/package-bundler-execution-v1/check-clock-render.mjs)
  validates this genuine runtime publication, all seven values, five child
  terminals, native-frame counts and recorded selected-interface scope. It passes
  the real records, rejects eighteen semantic mutations plus altered indexed
  bytes/an unexpected publication member, and leaves original evidence unchanged.
  It can inspect a complete relocated copy without loading an application. It
  does not re-audit external type/native provenance or substitute for independent
  actual-result review. Next and package README files document future-check use;
  their original pure-profile comparators and known failures remain unchanged.
  The design preserves two distinct phases: Jco mapped-output preparation, then
  separately reviewed actual mapping plus retained3/fresh1 Jco and three fresh
  Wasmtime calls. It will retain unchanged application inputs, Node comparisons,
  genuine stock Wasmtime scalar invocation and new Jco output mapped through the
  pinned standard WASI shim. Original wasi:* glue stays unchanged. Standard shim
  clocks/polling use a real worker thread and blocking Atomics.wait, requiring
  externally owned Node-process deadlines rather than JavaScript timers.
  Mapped-output and actual runtime reviews now pass for this bounded rendering
  workload. The broader clock suite remains open. No new host service or widened
  component import is introduced by this standard-shim test path.


- [Combined native artifact toolingc365e608](tests/node-compat/foundation-scheduler/combined-native-artifact-tooling-candidate-v1/README.md)
  is sealed **Source-only**: a new actual80-field/355+3/eleven-manifest frame,
  two bounded export/bootstrap phases and a separate repeatable zero-action
  read/hash preflight proposal. It authenticates the active original verifier
  separately from frozen payloads, preserves original metadata paths and never
  adapts the old75-field crypto frame. The compact 2,618-row current boundary,
  existing20,816-row BUILD ledger/fifteen families and 24,325 unique current files
  pass Source checks; 28 pin/data plus16 read-only API model cases and grammar
  checks pass. No helper, verifier, monitor, export, bootstrap, engine or guest
  action runs during preparation. Independent Source review is pending C; all
  operational proof/pin/activation slots remain NULL. These proposed APIs are
  not existing SpiderMonkey embedding APIs or an accepted runtime implementation.
- Pre-commit exact-membership audit catches a publication defect in the first
  stock-crypto and repeated-clock DATA packets: their sealers omit copied nested
  `index.json` files (one/three respectively). All indexed bytes and actual
  runtime values remain correct, but those v1 packets are held for closed-family
  consumption. They remain immutable. Genuine v2 sibling reviews now pass: host `5fe406ba`
  has54 indexed/55 total files; clock `54683955` has78 indexed/79 total files.
  Fresh DATA-only readers use their actual new contexts, with repair provenance
  and a sealer that excludes only its own root index. Exact forward/reverse
  membership and all hashes pass, including the four former omissions. No
  component/guest action is repeated. These successors are the current review
  publications; the historical c60a3b24/8946f77a packets stay held.
- Final checkpoint audit hashes 2,752 indexed members across37 new sealed
  families. Thirty-five are exactly closed; the two retained historical
  publication holds have only the four documented omissions, whose bytes equal
  the actual output indexes. Both successor publications are exactly closed.
  Staged documentation/framework source passes whitespace checks. The whole
  staged check reports retained generated/raw whitespace and one existing
  descriptor-bound controller EOF blank line; those sealed bytes are preserved.
- This continuation is **progress**: native freeze, guarded stock crypto, mapped
  Jco output and repeated real ReactDOM rendering now have bounded actual-result
  reviews. The read-only checker gives future runs a separate experimental
  baseline. Accepted production remains foundations-v13; new native admission,
  seven-case resource/clock/snapshot/lifetime gates, public Node crypto/ALS and
  optional-capability/release/adoption work remain outstanding.


Roadmap continuation after `fdd4ee18`:

- Previous goal turn: **progress**. All repository work was pushed in `d8034839`
  and `fdd4ee18`; the real Next.js/package experiment has two fresh Wasm matrices,
  a passing replay comparison and 40 checker self-tests. The worktree was clean
  at the start of this continuation. The full roadmap is still incomplete.
- Next available runtime dependency is the selected standard-clock path exposed
  by ReactDOM. The Rust/Jco tools are built; the valid adapter source `dc08495d`
  passes independent source review `39013123`.
  Original adapter/tool/package bytes and all historical failures stay unchanged.
- Combined355 integration/stage source reviews `aa64ecb0`/`df3a4b5d` pass. The
  [actual source stage](tests/node-compat/foundation-scheduler/combined-native355-v1-stage-root-results.json)
  exits 0 (Root63390), producing all 1,613 overlay files on detached baseline54b.
  [Independent actual review05346785](tests/node-compat/foundation-scheduler/independent-combined355-source-stage-results-review-v1/results.json)
  verifies copies, modes, inode independence, eleven manifests and raw cleanup.
  At that stage the work/freeze roots were absent. The subsequent build-only
  attempt is recorded below; native guest compilation and engine execution were
  not reached.
- Retained secret-bootstrap source `c47ac2f9` passes independent review `0372effb`.
  The [actual read-only call](tests/node-compat/foundation-crypto/ownership-secret-retained-preflight-root-results.json)
  exits 0 (Root40084/Node77532): one genuine new API call and one fresh own
  recheck. The entire 41-field historical frame remains identical to `fc86…`; all six
  new DATA properties and the separate seventh callable descriptor are retained.
  [Independent actual reviewd80e1142](tests/node-compat/foundation-crypto/independent-ownership-secret-retained-preflight-results-review-v1/results.json)
  verifies API28256 versus Root28257 protected rows, 355+3 sources, eleven whole
  manifests, raw process cleanup and ten evidence copies. Original API/helper/
  historical-callable counts remain zero. New output files are0600 under0700;
  genuine monitor raw files are0644 under0700, an explicitly qualified scope.
  No crypto key or engine has run in this continuation.
- The genuine355-aware component caller `4a2c1e20` passes independent source
  review `53faf8d2` (252,075 closure checks and four grammar checks). The existing
  `selectedManifestsForEngine` enumerates only nine optional/core manifest paths
  and cannot admit the actual eleven-manifest355 frame. Its old policy stays
  unchanged. After full new-frame verification, the new caller must use the
  real `builtinMap(fullManifests)`/manifest validation APIs with all eleven whole
  manifests and preserve the distinct native, embedding and packaging roles.
  Node `crypto` is still unadmitted; this gate concerns the real global
  WebCrypto ownership implementation, not Node Hash/Hmac/KeyObject compatibility.
  The [actual construction attempt](tests/node-compat/foundation-crypto/ownership-secret-component-v1-root-results.json)
  exits 1 before output creation: `packagingEnvironment` rejects the explicit
  packaging-root environment. Retained preflight and packaging read/hash checks
  run, but bundling, componentization, engine initialization and ordinary guest
  calls are not reached. Input protection passes and all owned groups are gone.
  The captured evidence does not identify which environment value was missing
  or different. [Independent failure DATA review6616a140](tests/node-compat/foundation-crypto/independent-ownership-secret-component-failure-review-v1/results.json)
  passes, retaining ten byte-exact copies and verifying terminal cleanup. A fresh
  corrected invocation remains outstanding; the failed phase stays failed.
- Native timers reject snapshot-time calls through `REQUEST_HANDLER_ONLY`.
  Native `clock_gettime` uses Preview1 for both realtime and monotonic clocks;
  the future clock profile therefore needs an explicit decision about standard
  wall-clock as well as monotonic-clock/poll. It must not silently inherit the
  historical failed component's stream/error interfaces or broaden all imports.
- [Root read-only adapter preflight](tests/node-compat/foundation-scheduler/clock-io-valid-adapter-v1-root-preflight.json)
  passes all 24,359 declared inputs, 24,384 unique files and ten full families;
  both fixed action roots are absent. No normalizer, pruner or metadata parser
  ran in that read-only check; the subsequent actual phase is recorded below.
- The [first actual adapter phase](tests/node-compat/foundation-scheduler/clock-io-valid-adapter-v1-root-results.json)
  finishes at Root16422 exit 1. Genuine normalization produces exact667/53,512B;
  the one native pruner invocation exits 0 and produces87777d4e…/48,808B.
  Node core validation exits 0 for both binaries; structural comparison retains
  six clock/two poll imports, all original instructions with declared remapping,
  fourteen unreachable stubs and byte-identical encoded WIT metadata.
- The same phase then fails in Jco's metadata decoder with `Unexpected wit
  package`. Its full raw stdout/stderr/terminal and failed result are preserved;
  all observed groups are gone and final protection passes. This is not a
  successful complete adapter phase. The independent
  [failure DATA reviewbfeab1bb](tests/node-compat/foundation-scheduler/independent-clock-io-valid-adapter-results-and-metadata-failure-review-v1/results.json)
  verifies the successful core steps and unchanged old scope. A new metadata-only
  source `28a8cdab`, with [independent Source reviewe216bd6d](tests/node-compat/foundation-scheduler/independent-clock-io-metadata-package-decoder-source-review-v1/results.json),
  uses the existing pinned native `wasm-tools`1.235.0 package-aware decoder.
  Its [separate Root53377 phase](tests/node-compat/foundation-scheduler/clock-io-metadata-package-v1-root-results.json)
  exits 0 under a300s outer/60s native-command bound. The native decoder retains
  all 15,184 WIT bytes, six packages, 28 declarations and ten resource/alias
  observations. These internal0.2.0 metadata declarations are not selected
  deployed imports; the proposed external profile is still explicitly0.2.10.
  [Independent actual DATA review4da84dac](tests/node-compat/foundation-scheduler/independent-clock-io-metadata-package-results-review-v1/results.json)
  passes 372,987 checks, including the complete WIT, raw command records and
  preserved old trees. Neither normalization nor pruning is repeated or the old
  failure relabelled. No adapter or component is admitted.
- [Proposed clock profile](tests/node-compat/foundation-scheduler/clock-profile-v1-design.json)
  deliberately selects monotonic-clock, wall-clock and poll at 0.2.10. The API
  matrix now distinguishes intrinsic timer needs from the embedding/adapter's
  realtime dependency. No imports are activated by that proposal. The existing
  clock-OFF generic trap remains a compatibility limitation; future identifiable
  guest refusal behavior is open, alongside deployed clock/snapshot/lifetime tests.
- Combined355 build controller source `d646d2ec` is sealed with66 pure checks,
  3,403 inputs and eight families. It reuses the genuine monitor/lifecycle and
  actual staged recipe, with private Rustup/Cargo homes and four exact cache
  copies. Independent source review `17aa133e` passes conditionally on removing
  inherited Bash functions/startup controls before spawning the controller. The
  [Root launcher](tests/node-compat/foundation-scheduler/combined-native355-v1-build-root-launcher.py)
  enforces that policy and records variable names only; actual removed names
  are empty, required entries are absent and home variables are preserved.
- The [actual combined355 build attempt](tests/node-compat/foundation-scheduler/combined-native355-v1-build-root-results.json)
  exits 1 at private Rustup bootstrap. Four cache copies and five embedding
  patches succeed; Rust1.88 installs, then Rustup self-update fails because the
  private Cargo home has no installed Rustup binary. A rustc version child is
  observed, but CMake/native guest compilation is not reached. No engine or
  sidecar is produced. All groups are gone, protection passes, and the failed
  work tree is preserved rather than resumed. [Independent failure DATA
  review188878b4](tests/node-compat/foundation-scheduler/independent-combined355-native-build-bootstrap-failure-review-v1/results.json)
  passes 103,346 checks over 4,253 observed files, including all source/cache
  copies, twelve observed processes and cleanup. It does not accept a native
  build. SDK30, fresh ABI compilation and actual metadata remain open.
- A [fresh private Rustup diagnostic](tests/node-compat/foundation-scheduler/rustup-private-bootstrap-probe-v1-root-results.json)
  passes all six owned commands: disable private auto-self-update, install 1.88,
  add wasm32-wasip1, repeat installation, manager version and Cargo-proxy version.
  It succeeds without a private Cargo bin directory and preserves the original
  failed build and pinned manager. This tests a bootstrap correction only; it
  runs no CMake, engine or guest. Independent DATA review and a genuine fresh
  build recipe/context remain open.
- The [experimental clock package loader source](tests/node-compat/foundation-scheduler/clock-package-loader-candidate-v1/README.md)
  is sealed at `21b9f306`: 59 pure cases, two grammar checks, 5,028 declared
  inputs, actual package/alias/artifact closure and explicit adapter selection.
  It composes the corrected core and separate metadata evidence while leaving
  the default loader unchanged. Independent source review, native admission and
  actual package/component/runtime actions remain open.

- Follow-up static validation passes: 295 JSON documents, 1,616 JSONL rows,
  43 Python ASTs, seven Node syntax checks, 310 member hashes across nineteen
  current sealed indices and 1,533 local documentation links. The
  [audit](tests/node-compat/foundation-scheduler/post-nextjs-checkpoint-audit-v2.json)
  qualifies one archived, unissued index as retained data, rather than treating
  its historical member paths as a new relocated package. The original reader
  failure is retained alongside the corrected audit. No sealed evidence changes.
  A separate read-only checkpoint scan finds no credential candidates, binaries,
  installed dependency caches, symlinks or unrelated paths; the largest new file
  is a 14.8 MB text input manifest.
  Staged whitespace checking reports five retained warnings: final blank lines
  in two sealed Python sources and two raw reader logs, plus original Jco stdout
  trailing whitespace. Their descriptor-bound bytes are preserved; current
  prose changes pass whitespace checking.

Next work, in dependency order: independently review the new clock-loader source
and the successful private Rustup diagnostic; issue a genuine fresh native-build
recipe/context; correct the crypto caller environment in a fresh observed phase;
then validate actual changed-engine components, selected clocks, snapshot behavior
and both-host execution. Only after those gates should the unchanged Next/React
cases be replayed against a new admitted engine. Request context/AsyncLocalStorage,
process/loader contracts, filesystem/crypto/HTTP capabilities, codec adoption and
release/performance checks remain broader roadmap work. The saved Next baseline
and comparators remain the future regression checks; known failures stay visible.

The current accepted native checkpoint remains foundations-v13. All work above
is experimental source/tooling or explicitly scoped evidence.

Commit/push and framework validation checkpoint (2026-11-05):

- The user requested a complete Git checkpoint and push, followed by a
  comprehensive, reusable Next.js/Wasm experiment. All current repository work,
  including unfinished source candidates and retained failures, is included in
  checkpoint `d8034839`, pushed normally to `origin/main`. It contains 1,203
  changed files. Referenced external build products are not Git contents.
- Precommit checks pass: 572 nonempty JSON documents, 30 Python AST parses,
  248 Node 22.14.0 syntax checks, 544 member hashes across 14 new sealed indices,
  1,355 local documentation links, and 43 regression-comparator synthetic checks.
  The independent read-only audit found no credential material, compiled binaries
  or installed dependency caches in the pending files. Small `node_modules`
  fixture paths are deliberate resolver test inputs.
  Staged whitespace checking finds one final blank line in a retained raw
  Wasmtime error log; its evidence bytes are preserved.
- Retained crypto-bootstrap source is now sealed at `c47ac2f9…`, with 29 pure
  checks and all 28,208 declared inputs checked. Its API, fresh recheck and
  component construction remain unexecuted; independent source review is open.
- Valid clock-adapter phase source is sealed at `dc08495d…`: 24 members,
  24,359 inputs and 35 pure checks. Independent source review, actual adapter
  normalization/pruning, metadata decoding and selected-clock runtime tests
  remain outstanding. No adapter has been published or promoted.
- The accepted runtime remains foundations-v13. Existing real Next production
  build/browser controls and optional-package component results are retained.
  The [fresh post-push package-v2 matrix](tests/node-compat/frameworks/package-bundler-execution-v1/results-post-push-v2/results.json)
  exits 0 with all ten observations, 17 clean parent commands and three complete
  Node/Jco/Wasmtime positive differentials. All four emitted components have no
  imports. Corrected Node controls exercise real `next/server.js` successfully
  and preserve the expected `headers()` error outside a request scope.
- Seven guest cases remain unsuccessful: ReactDOM edge builds a 15,685,263-byte
  component but traps on both hosts (`subscribe-instant` is the first named
  Wasmtime frame); the Node renderer refuses `async_hooks`; Next request/headers
  libraries refuse unprovided process/filename references; the real standalone
  server refuses runtime loader behavior; generated page/route entries refuse
  `crypto`. No full Next.js server component or HTTP/Wasm result exists.
- Independent read-only checking of the fresh matrix passes 207 checks,
  including four physical component hashes, all nine retained typed Jco returns,
  three fresh Wasmtime returns, interface records, executed source snapshots and
  all nested command cleanup. The deliberately failing ReactDOM Wasmtime command
  exits 134 without timing out; this remains a runtime failure, not a passed test.
- The full locked Next fixture's existing two Node baseline runs retain 24 HTTP
  and two real browser checks per run. They were not repeated because this change
  exercises the optional bundler against the same built application and pinned
  native engine. The new [matrix comparator](tests/node-compat/frameworks/package-bundler-execution-v1/check-components.mjs)
  passes [40 synthetic cases](tests/node-compat/frameworks/package-bundler-execution-v1/results-post-push-v2/comparator-self-tests.json).
  It rejects missing evidence/fixtures, unverified guest success, changed returns
  and import widening, and flags changed full failure diagnostics for review.
  Declared source roots may relocate without changing their recorded identities.
  Independent review confirms the finite checker contract and reruns all 40
  synthetic checks successfully without modifying its two source files.
- A [genuine fresh ten-case replay](tests/node-compat/frameworks/package-bundler-execution-v1/results-post-push-v2-replay/results.json)
  exits 0. Its [actual baseline comparison](tests/node-compat/frameworks/package-bundler-execution-v1/results-post-push-v2-replay/comparison.json)
  exits 0 with complete evidence, no regressions/improvements/changed blockers,
  and all seven known guest failures retained. This establishes a reusable
  observation check, not Next.js compatibility. Both matrices' tools are terminal.
- The broader native, selected-clock, crypto, HTTP and AsyncLocalStorage roadmap
  remains in progress. The next runtime target from this experiment is the
  explicitly selected standard clocks/poll profile, followed by the separately
  bounded loader, process, crypto and request-context requirements. Full server
  deployment, optional native355 admission, host expansion and performance are
  not claimed by this checkpoint.
- Follow-up precommit checks pass for 245 JSON files, 832 local documentation
  links and the two independently reviewed checker source hashes. The 444-file
  follow-up retains two final blank lines in original Wasmtime error logs;
  their descriptor-bound bytes are preserved. The fresh component binaries and
  installed Next dependencies remain at their recorded external paths.


Work between Next.js checkpoint `d1f8d524` and checkpoint `d8034839`:

- Previous goal turn classification: concrete progress. Real clock-tool builds,
  crypto pin/bootstrap actions, source/actual-result reviews and new package
  component tests completed. These experimental changes are now committed and
  pushed in `d8034839`. Accepted foundations-v13 stays
  unchanged and the full roadmap remains in progress.
- [Optional production-package execution](tests/node-compat/frameworks/package-bundler-execution-v1/README.md)
  preserves the original finite bundler. V1's real CommonJS/native interop and
  React element components pass, but its [bounded Source review](tests/node-compat/frameworks/package-bundler-implementation-review-v1/README.md)
  holds six denial-policy gaps/two local-binding false refusals. V1 and all raw
  evidence remain unchanged. The genuine v2 successor provides no process or
  runtime-loader shim, respects lexical bindings and preserves React's optional
  typeof/process error branch as ordinary JavaScript.
- V2 passes [28 host differential/refusal cases](tests/node-compat/frameworks/package-bundler-execution-v1/results-host-v2/results.json)
  and [bounded Source review](tests/node-compat/frameworks/package-bundler-v2-source-review/results.json)
  `d8663d5f…55eb` (45 expected outcomes). Its lexical helper has60 synthetic/two
  real-source parse checks. The [actual ten-case v2 component matrix](tests/node-compat/frameworks/package-bundler-execution-v1/results-component-matrix-v2/results.json)
  finishes exit0 with three required complete Node/Jco/Wasmtime differentials:
  nested native CJS identity, supported modules and real React elements.
  ReactDOM edge now builds a15,685,392-byte zero-import component but traps on
  both hosts at a named subscribe-instant frame. Its production startWork really
  schedules setTimeout(0); selected-clock construction/runtime is the next gate.
  Six other Next/Node-renderer inputs remain refused. No full Next HTTP/Wasm
  component or secondary-host result is claimed.
- Direct Next library Node controls initially had an extensionless ESM resolver
  error. [Corrected real-CJS controls](tests/node-compat/frameworks/package-bundler-execution-v1/node-library-controls.json)
  confirm NextRequest/NextResponse success and the expected headers-outside-
  request-scope error; original observations are retained. Future runner controls
  resolve the same actual .js entries. The v2 driver's initial default-binding
  setup error is separately retained; it occurred before output/worker creation.
- Crypto [normal-only export DATA review](tests/node-compat/foundation-crypto/independent-ownership-secret-artifact-export-v3-results-review-v1/results.json)
  seals `a4c3eba3…d8fe` (31,979 checks). Genuine derive-pins phase6189 exits0;
  [Root full recursive review](tests/node-compat/foundation-crypto/ownership-secret-artifact-bootstrap-v3-derived-pins-root-review.json)
  confirms exactly four state/flag edits, all other DATA unchanged and three
  other variants NULL. Reviewed pins are727323af…11c9.
- New bootstrap-controller SOURCE d99/Source review34839 pass. The actual
  one-shot JS API phase26525 exits0 with clean retained process levels and
  [Root observation7a620cb7](tests/node-compat/foundation-crypto/ownership-secret-artifact-bootstrap-v3-js-root-results.json).
  [Actual DATA review8298edf6](tests/node-compat/foundation-crypto/independent-ownership-secret-bootstrap-v3-results-review-v1/results.json)
  passes32,260 checks/28,193 paths: complete41-field2,030,522-byte JS DATA equals
  Python framefc86; all42 own properties/callable descriptor,75 metadata fields,
  11 manifests and current frozen/old-normal protection agree. One API/helper
  launch and one returned read-only recheck remain distinct. No engine, key or
  guest ran. One-shot roots now exist and must not be reused. A genuinely new
  historical-reference/current-read-only preflight was subsequently sealed before
  any component construction; no serialized callable is treated as live.
- Clock controller41b/Source review9027 pass. Actual Root30831 exits0 after
  private staging/vendor and all eight Rust/Jco commands, including four exact
  one-test Rust passes. [Root result6844e920](tests/node-compat/foundation-scheduler/clock-io-tools-build-v2-root-results.json)
  preserves raw2+9 JSONL joins, cleanup and actual before/after space checks.
  [BUILD/DATA reviewcc5edbc1](tests/node-compat/foundation-scheduler/independent-clock-io-tools-build-v2-results-review-v1/results.json)
  passes436,062 checks over24,332 files,121 exact archives/three private downloads,
  21 aliases and all produced artifacts. Invalid-input pruner-unit invocation
  is verified; valid adapter normalization/pruning/publication never ran.
  A separate actual-adapter phase was subsequently sealed with all grants NULL;
  exact output/WIT/reference and selected-host gates remain required.
- Combined355 stage/controller [SOURCEb1a21da1](tests/node-compat/foundation-scheduler/combined-native-stage-controller-candidate-v1/README.md)
  is sealed:16 members/1,637 inputs,6,611 checks and exact1,613 copies
  (355 native+1,226 tool+32 integration-family files), inherited54b baseline.
  Independent integration/stage Source reviews, actual stage/build/freeze and
  all subsequent runtime gates are still open. No Source or count projection
  from the old342 artifacts is used.
- Model capacity briefly interrupted the three source writers; their missing/
  unsealed outputs were rechecked and the same tasks resumed without changing
  models or restarting an operational job. All Root operational jobs above are
  terminal. Current work is source preparation/review. No native production
  source, optional host selection or accepted checkpoint was promoted.


Next.js framework experiment after pushed checkpoint `9c426444`:

- All earlier repository work is committed and pushed to `origin/main` at
  `9c426444`. No force push/history rewriting was used. Referenced external
  artifacts remain external.
- [Reusable Next.js project and report](tests/node-compat/frameworks/nextjs/README.md)
  pin Next16.4.5, React/ReactDOM19.3.1 and exact app/browser npm locks. The real
  App Router fixture has28 application files plus its lock and23 HTTP contract
  cases: layouts/metadata/static/dynamic/query SSR, JSON GET/POST/bad input,
  cookies/headers, redirects/not-found, cache invalidation, actions, hydration,
  Suspense, assets, bounded Node operations and deliberate filesystem/crypto.
- [First preparation attempt](tests/node-compat/frameworks/nextjs/results/2026-11-05-v13-attempt1/harness-failure.json)
  retains build exit0 followed by harness tracing-root/path and recorder-parent
  mistakes before Wasm execution. The fixture now selects its real tracing root
  and the reporting paths are corrected. These are harness issues, not native
  runtime findings.
- [Actual full run](tests/node-compat/frameworks/nextjs/results/2026-11-05-v13/results.json)
  and [fresh replay](tests/node-compat/frameworks/nextjs/results/2026-11-05-v13-replay/results.json)
  both finish with complete19-case observations. Each has a real production
  build0, genuine standalone server,24 passing HTTP checks including an actual
  build-derived action POST, and two passing Chrome156 hydration/action tests
  without recorded browser errors. Cache generations1/repeat1/invalidate2 and
  actual raw stream chunk boundaries are retained. First-run shell is in chunk0
  and ready in chunk2 of five. These are Node controls, not Wasm Next results.
- On the exact accepted normal-OFF v13 engine, eight real React/Next/generated
  entries fail at the unchanged CommonJS bundler policy. Eight unselected Node
  module imports fail admission explicitly. The shared application function
  builds a zero-import component but traps on both Jco and fresh Wasmtime;
  child-process and unsupported Buffer probes pass their refusal checks on
  three retained Jco calls and fresh Wasmtime. Main driver exits1 because the
  shared Node/Wasm differential cannot pass. All emitted components have only
  `run()->string` and no imports; no full Next server component is emitted.
- [Supplemental native differential and diagnostic](tests/node-compat/frameworks/nextjs/results/2026-11-05-v13-supplement/results.json)
  finish exit0. The caught original error is `ERR_SM_NODE_UNSUPPORTED` from
  deferred `node:util.format`. The distinct supported probe covers Buffer
  UTF8/hex/copy/ArrayBuffer+slice sharing/zero allocation, path, events, decoder,
  scalar asserts, query strings, util type predicates, web streams and classic
  pipeline. Its complete strings and structured values equal Node on all
  three Jco calls and fresh Wasmtime. This does not replace the original failure.
- Future checks use the executable full runner, exact source/engine preflights,
  browser worker, supplemental differential and known-failure comparator.
  The first fresh comparison flags only reversed order of two identical parallel
  Rolldown diagnostics. Its raw comparison is preserved; a bounded exact-block
  multiset reader correction passes43 synthetic checks. [Actual fresh comparison](tests/node-compat/frameworks/nextjs/results/2026-11-05-v13-replay/comparison.json)
  now exits0: no regressions, improvements or changed blockers, with17 known
  failures still explicit and framework compatibility false. Source snapshots, all HTTP bodies,
  browser screenshots/errors, raw terminals/typed returns, WIT and external
  artifact descriptors are retained. The replay worker snapshot is reconstructed
  from one documented later filename-only edit and cryptographically matches its
  actual executed descriptor; current worker is unchanged by reconstruction.
- [Bounded retained-evidence validation](tests/node-compat/frameworks/nextjs/results/2026-11-05-v13/evidence-validation.json)
  passes1,673 checks across505 files, including native inputs, all HTTP bodies,
  browser screenshots/errors, full raw stream reassembly, clean worker terminals,
  component hashes/WIT and complete successful typed returns. All workers and
  Root operational jobs are terminal. Syntax validation passes45 JS/MJS files;
  both real Next builds separately compile the fixture's JSX. The observation
  comparator passes43 injected checks and an actual fresh-run comparison.
  Precommit whitespace findings are confined to16 original progress/blank-line
  sequences in six raw Next/Wasmtime log files; those bytes remain unchanged.
  Whitespace validation passes for all other staged files.
- Findings prioritize audited package CommonJS bundling, bounded util formatting,
  real ALS/request context and a selected standard WASI HTTP integration. No
  native source, bundler policy, custom host service or selected capability was
  added. Full Next.js compatibility, new host results, performance and request
  reuse remain unestablished. Accepted production stays foundations-v13.


Earlier all-work commit checkpoint `9c426444` (2026-11-05; historical state):

- All three parallel workers have stopped writes; their tools and all Root
  operational jobs are terminal. This checkpoint includes all tracked changes
  and untracked repository files, including retained failures and unfinished
  work. It does not mark the roadmap complete or change accepted foundations-v13.
- Completed since `23c40067`: codec timing DATA review and bounded cost decision;
  crypto complete frozen-verifier DATA review and actual v3 normal-only export
  at exit0; selector342 actual freeze and independent artifact review; clock
  pruning SOURCE review, adapter provenance and redirect-controller HOLD;
  zlib error SOURCE review; convergence audit and combined355 SOURCE candidate.
- The independent crypto actual-export review is an unexecuted, unsealed
  [reader draft](tests/node-compat/foundation-crypto/independent-ownership-secret-artifact-export-v3-results-review-v1/reader.py).
  No PASS, result contract, receipt or index exists yet. Full DATA review and
  sealing must precede reviewed pins and the one-shot Python/JS bootstrap.
- Corrected clock build-controller v2 is an18-file unsealed draft with307 pure
  checks. Its dependency closure, reversible derivations, final audit, seal and
  independent review remain outstanding. No download, staging, Rust/Jco build
  or valid adapter pruning/publication has run.
- Combined355 source is sealed but awaits independent SOURCE review and new
  stage/build/freeze/export/bootstrap/component/runtime gates. Its seven
  replacements have not been promoted into the accepted production source.
- Precommit checks pass:290 nonempty JSON documents,76 Python AST parses,
  two Node v22.14.0 syntax checks, one Bash syntax check, and444 member hashes
  across21 sealed indices. The single empty JSON-named stdout capture is
  preserved as raw failed-reader evidence. All1,327 local links in the six
  updated status/decision documents resolve. Full staged whitespace checking
  reports28 findings confined to six sealed evidence files:25 unified-patch
  blank context lines and three extra final blank lines. Those hash-bound bytes
  are retained; staged whitespace checking passes when those six files are
  excluded. No native build, complete helper, component or guest test is rerun
  solely to make this Git checkpoint.
- Repository files and evidence descriptors are committed. Referenced large
  `/private/tmp` build, freeze and component artifacts remain external; their
  descriptors do not make those artifacts part of the Git commit. No push is
  requested. The dependency-ordered continuation and remaining lifecycle/ALS,
  crypto API, optional capability, host/release and adoption gates remain below.

Historical Git checkpoint `23c40067` on 2026-11-05 (superseded by the continuation below):

- Preserve all current tracked changes and untracked repository files, including
  successful evidence, retained failures, source proposals and unfinished drafts.
  Repository commit preparation does not execute new native/guest work.
- The latest completed codec timing phase exits0; its independent final review
  and operational/adoption decisions remain open. The all-invalid selector native
  build passes independent BUILD review; its new freezer is still source work.
  The crypto frozen verifier passes independent SOURCE review; its separate
  caller and actual complete-helper observation remain open.
- The three parallel workstreams have stopped repository writes at explicit
  incomplete checkpoints: [codec timing review](tests/node-compat/foundation-zlib/independent-cost-timing-v5-results-review-v1/checkpoint-status.json),
  [selector freezer](tests/node-compat/foundation-scheduler/task-selection-freezer-candidate-v1/preparation-history.json)
  and [crypto verifier caller](tests/node-compat/foundation-crypto/ownership-secret-verifier-controller-candidate-v1/README.md).
  Codec raw replay/aggregate/prerequisite checks pass, but outer-window
  reconciliation, interpretation, final stability and sealing remain unfinished.
  The selector freezer lacks its verifier/closure evidence/seal. Crypto caller
  preparation passes28 pure cases and three AST parses; final review and sealing
  remain unfinished. None of these three drafts grants execution authority.
- The clock-profile decision is a proposal. The timer artifact's six-interface
  admission failure remains retained; selective guest pruning, exact adapter
  provenance, new construction and real runtime/host validation are outstanding.
- Export/pin/bootstrap and algorithm gates for the new crypto generation,
  scheduler lifecycle/ALS/reuse, optional capability profiles and roadmap release
  gates remain incomplete. The accepted production checkpoint stays foundations-v13.
- Precommit checks pass:256 JSON documents,67 Python AST parses, five Node
  v22.14.0 syntax checks,362 member hashes across19 sealed indices,1,106 local
  documentation links and Git whitespace validation (CSV CRLF accepted). Twelve empty syntax-check
  stdout captures are preserved as raw evidence, not treated as JSON documents.
  Native builds, complete helpers and components are not rerun for this commit.
- Commit includes repository-resident evidence and descriptors. Large raw build,
  frozen and component outputs referenced under `/private/tmp` remain external
  artifacts and are not made portable merely by committing their descriptors.

Latest continuation after Git checkpoint `23c40067`:

- [Codec actual timing DATA review](tests/node-compat/foundation-zlib/independent-cost-timing-v5-results-review-v1/README.md)
  seals52 members at `434ee6c7…83e5`; result `9cd3ef57…42a3` verifies all360
  fresh workers,7,200 complete strings,3,600 batches,2,160 controls and the361
  observed process/window records. All77,969 final input paths are stable.
  The [Root cost decision](tests/node-compat/foundation-zlib/cost-timing-v5-root-decision.json)
  (`2b3a03f5…ff4a`) authenticates that complete proof/contract and the three
  actual components. Native has lower median batch time in27/30 provider cases;
  three fflate counterexamples and output-size differences remain explicit.
  Continue the bounded native candidate through compatibility/host/release and
  adoption gates. No universal speed, guest-memory or isolated-startup advantage
  is established. [Decision details](docs/node-compat/codec-cost-decision.md)
  preserve the separate unused-profile comparison and all statistical limits.
- Crypto's [read-only verifier caller SOURCE](tests/node-compat/foundation-crypto/ownership-secret-verifier-controller-candidate-v1/README.md)
  seals16 members at `0fc0082d…a78f`. [Independent SOURCE review](tests/node-compat/foundation-crypto/independent-ownership-secret-verifier-controller-source-review-v1/README.md)
  seals at `a2191196…8e7b`, passing227,862 checks/26,310 inputs,80 isolated cases
  and four AST parses. Two independent-reader assumptions are corrected with
  failures retained; the candidate is unchanged. New Root read-only authority
  starts tool83988/owned worker65475. The actual complete original-context
  `verify_frozen(contract)` finishes exit0 with clean groups and source/original
  protection. [Root result](tests/node-compat/foundation-crypto/ownership-secret-frozen-verifier-v1-root-results.json)
  `30759e29…3c34` retains the entire471,365-byte frame `7d319471…52e5`, complete
  raw stdout/stderr and terminal. Whole stdout JSON equals the saved return with
  unchanged355-source metadata/all11 manifests and1,902 verified copies.
  [Independent actual-result DATA review](tests/node-compat/foundation-crypto/independent-ownership-secret-frozen-verifier-results-review-v1/README.md)
  now seals23 members at `f894bf38…b46b`; result `116c339a…698e` passes261,560
  checks/27,729 references with all75 metadata fields/11 manifests unchanged.
  No engine/guest executes. Original e872 remains verifier-only; the separate
  export/pin/bootstrap v2 source remains held; the corrected v3 source and
  actual normal-only export are recorded below.
- [Adapter provenance report](tests/node-compat/foundation-scheduler/clock-adapter-provenance-v1/README.md)
  seals11 members at `dd49f614…9433`. The official equal-sized Wasmtime v25
  reactor adapter differs from the selected988 binary in code/import/metadata
  bytes; the exact original source revision remains unresolved. Static inspection
  finds memory-first import ordering incompatible with pinned wirm's replacement
  index assumption. [Design notes](tests/node-compat/foundation-scheduler/clock-io-pruning-design-review-v1/results.json)
  seal at `8a069abc…5bb3`, with3,767 static checks/672 independent policy cases,
  corroborating that hazard and engine-only random/realloc prerequisites.
  The new uncompiled clock-IO source draft splits poll from stream/error stubs,
  provides a separate narrow CLI and exact normalized-input SHA guard, and keeps
  all clock/poll signatures. Ten pure normalizer cases and in-memory hash
  preparation run; no normalized adapter is published, and no Rust pruner,
  replacement package, component or guest executes. [Independent SOURCE review](tests/node-compat/foundation-scheduler/independent-clock-io-pruning-source-review-v1/README.md)
  seals18 members at `c9fa3ef3…5805`, with54,922 checks/5,579 paths and all four
  reversible derivations. Compilation, real Rust tests, WIT alias/dependency
  elaboration and encoded-reference/clock/poll preservation remain open. A fresh
  owned build controller/private-vendor/SDK plan is being implemented; no build,
  archive download, staging or adapter publication has run. The old six-interface
  timer rejection remains unadmitted.
- A new [zlib error-semantics source proposal](tests/node-compat/foundation-zlib/node-error-semantics-candidate-v1/README.md)
  seals37 members at `7d620e00…edb5`, with2,138 source/DATA checks and63
  extracted status models. It inventories all61 cases/31 error comparisons and
  all22 differences. Three unapplied afterimages propose removing six spurious
  errno fields and matching dictionary-required Z_NEED_DICT/errno2 while still
  refusing dictionary support. Fifteen policy/option/input deviations and true
  linked-version evidence remain open. Seven addressed rows are model predictions,
  not deployed fixes. [Independent SOURCE review](tests/node-compat/foundation-zlib/independent-node-error-semantics-source-review-v1/README.md)
  seals at `002458df…47bc`, with14,566 checks/968 paths, complete350-source
  before/after mapping and exact executable factory preservation. A new native
  integration/build and complete differential/component/release gates remain
  required. Historical codec proofs and all existing artifacts stay unchanged.
- Crypto [artifact-tooling v2 SOURCE](tests/node-compat/foundation-crypto/ownership-secret-artifact-tooling-candidate-v2/README.md)
  seals29 members at `8ebec1f8…1259`, implementing real export/pin/bootstrap APIs
  without running them. [Independent Source HOLD](tests/node-compat/foundation-crypto/independent-ownership-secret-artifact-tooling-source-review-v2/README.md)
  at `a682a562…9d55` identifies two bounded gaps: the runtime guard omits one
  declared provenance-only donor (27,754 versus27,755 inputs), and JS labels an
  ambiguous killed child as a proven timeout. Actual imported dependencies are
  covered, all failures are refused, and syntax-only Node checking passes.
  The [v3 source successor](tests/node-compat/foundation-crypto/ownership-secret-artifact-tooling-candidate-v3/README.md)
  seals27 members at `d62b235c…52a2`, with both guards protecting all27,797
  declared external paths and truthful nullable timeout labels. Its
  [independent SOURCE review](tests/node-compat/foundation-crypto/independent-ownership-secret-artifact-tooling-source-review-v3/README.md)
  seals nine members at `522e1741…6b05`; result `f01cbf84…6269` passes27,930
  read/hash/AST checks, all12 exact reversals and six cause/capture models.
  The v2 source/HOLD and all earlier artifacts remain immutable. New normal-only
  [export authority](tests/node-compat/foundation-crypto/ownership-secret-artifact-export-v3-root-authority.json)
  starts actual Root4382/outerparent86546 under the genuine1,800-second monitor.
  That same action finishes exit0 with clean groups and no signals, timeout or
  forced cleanup. [Root result](tests/node-compat/foundation-crypto/ownership-secret-artifact-export-v3-root-results.json)
  `2295d612…621a` binds the complete1,105,309-byte UNREVIEWED candidate
  `2bbb22d8…d4d4`, unchanged whole helper frame and three NULL other variants.
  The raw worker JSON equals the entire saved candidate. A Root-only reader
  label mistake is retained; no owner action is rerun. Independent actual-export
  review is unfinished at this commit checkpoint. Reviewed pins, bootstrap,
  engine/key/guest and runtime gates remain closed.
- The [clock build-controller Source](tests/node-compat/foundation-scheduler/clock-io-build-controller-candidate-v1/README.md)
  seals30 members at `06400300…72c8`. Its pure actual-plan test catches and fixes
  a package.json collision before any staging: two old tool-root metadata files
  are copied as DATA under `.toolchain-metadata`, preserving the new package's
  source package.json. It specifies5,138 copies/21 links, private locked vendor,
  eight owned commands, four individually checked Rust tests and honest disk/
  timeout/failure boundaries. Review then identifies a redirect-scope gap:
  default urllib follows redirects before its post-response URL check. This is
  held without any network/stage/compiler action. [Independent Source HOLD](tests/node-compat/foundation-scheduler/independent-clock-io-build-controller-source-review-v1/README.md)
  seals seven members at `ef1f1d89…4b9b59`, preserving the redirect counterexample.
  The corrected [v2 controller WIP](tests/node-compat/foundation-scheduler/clock-io-build-controller-candidate-v2/README.md)
  has18 files and307 pure checks, including explicit rejection of301/302/303/
  307/308 before following redirects. It has no source manifest/results/receipt/
  index seal yet. Closure, derivations, final audit, sealing and independent
  review remain outstanding. Unissued Root build code and all actual source/
  package/adapter publication gates remain inactive.
- The [separate-prerequisite Root receipt](tests/node-compat/foundation-scheduler/continuation-prerequisites-after-23c-root-review-v1.json)
  `3e6dfc9a…9b03` authenticates70 indexed proof members across crypto verifier
  DATA, selector frozen DATA, clock SOURCE and zlib error SOURCE. These scopes
  remain separate and grant no operation or source promotion. The [convergence
  audit](tests/node-compat/foundation-scheduler/combined-source-convergence-audit-v1/README.md)
  seals25 members at `84901fd1…2cd`, with6,786 checks. It maps the actual355
  secret source, four final scheduler/resource replacements and three zlib error
  afterimages, preserving the five crypto files and13 additions over342. The
  [combined native SOURCE candidate](tests/node-compat/foundation-scheduler/combined-native-integration-candidate-v1/README.md)
  now seals31 members/1,590 inputs at `08bfe069…df65`:355 native files are348
  unchanged plus seven replacements, with three external inputs/11 manifests.
  Its new genuine355 policy/helper/producer and metadata admission pass8,246
  source/DATA/pure/grammar checks and25 synthetic negative cases. This is held
  SOURCE only, awaiting independent review. Staging/controller/freezer/verifier/
  export/bootstrap and all native/component/runtime actions remain unimplemented
  or NULL; no build or guest validation is implied.
- The [selector342 freezer SOURCE](tests/node-compat/foundation-scheduler/task-selection-freezer-candidate-v1/README.md)
  seals27 members at `83c07efa…37e8`. [Independent SOURCE review](tests/node-compat/foundation-scheduler/independent-task-selection-freezer-source-review-v1/README.md)
  seals at `6c2af2c7…b6eb`, passing158,303 checks/20,812 inputs,37 isolated cases
  and ten AST parses, including the full20,761-file BUILD ledger and712-copy
  base plan. One reader synthetic phase omission is corrected and retained.
  The first Root outer observer then rejects its3,000-second limit against the
  copied monitor's2,400-second maximum before launching any freezer/helper;
  [failure records](tests/node-compat/foundation-scheduler/task-selection-freeze-root-observer-failure-v1/terminal.json)
  preserve that Root API mistake. At that rejection FREEZE/EXTERNAL are absent
  and its observer directory is empty. A distinct v2 Root caller uses the genuine original0af
  monitor's7,200-second-cap API at3,000 seconds, preserving all v1 files and the
  unchanged83c source. Actual tool34677/parent69997 runs under that outer
  monitor. That same phase now finishes exit0 at both owned monitor levels,
  with clean groups and no forced cleanup/signals. [Root result](tests/node-compat/foundation-scheduler/task-selection-normal-off-freeze-v2-root-results.json)
  `43331162…ea00` records762 copies/755 original references/763 actual files;
  Root rehashes every copy. Receipt `42a81bc1…1641` is515,011 bytes. Complete
  outer JSONL has two records and its final record equals the complete inner
  terminal. Actual enginef6a/raw metadata8219 remain unchanged;342 native/three
  external inputs and nine manifests are retained. The f6a generation stays
  separate from old fec7. [Independent frozen-artifact DATA review](tests/node-compat/foundation-scheduler/independent-task-selection-normal-off-frozen-artifact-review-v1/README.md)
  now seals19 members at `6fc8165a…73c3`, with196,579 checks/21,594 current paths
  and the complete20,761-file BUILD ledger. The first reader's strict-target
  count assumption is corrected: four critical policy targets are distinguished
  from61 CPP rows carrying the macro. No source/artifact changes or helper reruns.
  Pins, bootstrap and ordinary runtime gates remain open; no engine/guest executes.


Latest continuation after Git checkpoint `1f459dc`:

- The [timing Root-caller independent SOURCE review](tests/node-compat/foundation-zlib/independent-cost-timing-v5-root-controller-source-review-v1/README.md)
  seals nine members at `9e40baf7…0d5b`; result `ccd7369e…61f4` passes678,721
  checks/59,949 protected lexical paths,61 independent cases and five Python AST
  parses, including eight actual monitor API witnesses. All three agents then
  explicitly acknowledge terminal tools and stop reads/hashes/tests/writes until
  Root release. All Root native, plan and source-review jobs are terminal before
  [fresh timing activation](tests/node-compat/foundation-zlib/cost-timing-v5-root-activation-receipt.json).
  Root receipt `0c7e3120…6ed3` records new timing-only sourcee799/controllerae8/
  peer9e40, actual plan7f019/peer9b75 and distinct originalB5/64472/e545 calibration.
  The [two-hour quiet window](tests/node-compat/foundation-zlib/cost-timing-v5-quiet-window.json)
  and preselected5,400,000ms budget preserve all360 fresh workers/3,600 batches/
  2,160 separate controls. Unrelated desktop/system activity is uncontrolled.
  Actual Root38214/Node43889 now finishes exit0 with clean owned cleanup.
  The [Root observation](tests/node-compat/foundation-zlib/cost-timing-v5-root-results.json)
  (`55cf580f…a8f`) retains all360 fresh worker PIDs,17,642 indexed/17,644 actual
  files,3,600 codec batches (1,080 warmups and2,520 measured samples),2,160
  separate N1 controls and7,200 complete typed API strings. All observed workers
  exit0. The [quiet-window completion](tests/node-compat/foundation-zlib/cost-timing-v5-quiet-window-completion.json)
  (`253c79e5…2248`) closes the phase and releases all three agents. Parent
  duration2,294.432 seconds is an operational record, not a benchmark result.
  The Root observer's initial sample-count assumption and its correction are
  retained in its history; no codec worker or timing phase is rerun. Independent
  actual DATA/provenance/paired-statistics review remains incomplete. No timing
  acceptance, performance advantage or adoption is claimed.
- The [independent selector build-controller SOURCE review](tests/node-compat/foundation-scheduler/independent-task-selection-build-controller-source-review-v1/README.md)
  seals11 members at `17bbc355…be68`; result `0c707ee1…9351` passes53,456
  finite checks/2,608 inputs and40 independent isolated cases. It verifies actual
  stage566 and resource501/666/663 protections, exact existing monitor/lifecycle
  APIs, new ABI/source identities, closed extra action flags and strict clean
  termination before metadata observation. No controller/helper/compiler runs
  during review. New [normal-OFF build authority](tests/node-compat/foundation-scheduler/task-selection-normal-off-build-v1-root-authority.json)
  starts Root88220/controller9641 with the original owned monitors and7200-second
  bound. The [actual native build](tests/node-compat/foundation-scheduler/task-selection-normal-off-build-v1-root-results.json)
  finishes raw0 with clean owned cleanup and all107 Ninja steps. Root result
  `2cc53b11…3ef4` retains new engine `f6a775f0…034f` (9,976,922 bytes), untouched
  raw sidecar `8219b7aa…de4f` (324,280 bytes), complete build log and raw inner/
  outer records. Native worker duration453.270 seconds is an operational record,
  not a performance measurement. Its [independent BUILD-only DATA review](tests/node-compat/foundation-scheduler/independent-task-selection-normal-off-build-review-v1/README.md)
  seals13 members at `6e8c5996…5528`; result `1d5806f6…134b` passes1,105,410
  checks/20,761 files. All67 DB rows/68 objects including embedding,61 policy
  CPP/strict4/private5,29 unique/30 ordered archives, nine manifests, full SDK/
  SM/Binaryen/OpenSSL/locked Rust and prior resource protections pass. The full
  15,227,953-byte ledger is proof DATA with32MiB intake, not a small source file.
  Source-aware freeze/pins/bootstrap/component and runtime gates remain open.
- [Independent codec v5 SOURCE review](tests/node-compat/foundation-zlib/independent-cost-pilot-timing-v5-source-review-v1/README.md)
  seals20 members at `553b000c…782e`; result `df290981…ae7b` passes9,000
  assertions/1,196 stable paths,44 isolated cases plus360 schedule assertions,
  twelve Node syntax/five Python AST checks. It preserves the original b5/64472/
  e545 calibration roles, whole33,066-member DATA index and unchanged timing
  protocol. New read-only [plan authority](tests/node-compat/foundation-zlib/cost-measurement-plan-v5-root-authority.json)
  starts Root8203/Node8510 under the genuine900-second monitor. The actual plan
  finishes raw0 in225.859 operational seconds with clean cleanup. Root result
  `d98a1bf6…3c7e` retains fresh plan `7f019952…fb14` (55,175 bytes), original
  relative rows and separately confined absolute descriptors. Its
  [independent DATA review](tests/node-compat/foundation-zlib/independent-cost-measurement-plan-v5-results-review-v1/README.md)
  seals26 members at `9b75ac47…f27d`; result `16edf7e6…69bd` passes900,991
  assertions/59,878 physical inputs, all90 full-byte/FNV rows, three artifacts,
  original60→120 calibration roles, two tool trees/22 links and actual three-file
  publication. No pilot, codec worker, guest or timed operation runs. A new timing
  Root-caller SOURCE candidate is being prepared; all timing/quiet-window/budget
  authority remains absent while native/audit/source jobs are active.
- [Independent resource component artifact/failure review](tests/node-compat/foundation-scheduler/independent-resource-component-results-and-clock-failure-review-v1/README.md)
  seals12 members at `5a35ea67…7329`; result `08b5d9fa…358c` passes64,758
  checks/6,610 paths. Pure artifact PASS and timer rejection VERIFIED are separate
  scopes. The exact graph resolves core0 Preview1 clock_time_get through a
  generated table shim/fixup to the adapter, then callable wall-clock, stderr
  and stream lowerings. io/error is a resource type with canonical drop, without
  explicit WIT functions. Only generated shim operands/fixup elements are decoded;
  engine/adapter code and all data remain undecoded. Full core/adapter/type graph
  supports the dependency finding without proving the opaque thrown exception.
  The strict two-interface selection stays rejected. Selective poll-versus-stream
  pruning and a deliberate Date/realtime policy are required in a new source
  successor; no blind six-interface widening or runtime authority follows.
- The [next runtime-clock profile decision](docs/node-compat/clock-capability-decision.md)
  selects an intended wall-clock/monotonic-clock/poll@0.2.10 contract so that live
  Date semantics are preserved. It grants no capability to the existing rejected
  component. Pure applications retain imports[]. A guest clock-only adapter or
  native P2 bridge still requires exact source/ABI/ownership/snapshot analysis;
  the existing53512-byte adapter is binary-pinned but its original source/build
  revision is unresolved. Selective stream/error pruning must preserve other
  profiles. Source, construction, full graph and real runtime/host gates remain
  mandatory before this proposed profile can be supported.
- The [verifier-first crypto tooling SOURCE](tests/node-compat/foundation-crypto/ownership-secret-pin-tooling-candidate-v1/README.md)
  seals18 members at `e8726a1c…b7ad`. Its complete frozen-only DATA helper is
  implemented; export entry, pin model and bootstrap API are genuinely absent.
  [Independent SOURCE review](tests/node-compat/foundation-crypto/independent-ownership-secret-frozen-verifier-source-review-v1/README.md)
  seals16 members at `7a453906…c8ff`; result `19ae4348…5e98` passes269,257
  finite checks/26,276 inputs,32 isolated cases and five Python AST parses.
  Exact1902/1899/1903 protection, four original predicates/four reversible edits,
  retained68-row compile/cache/embedding DATA and the real11-manifest boundary
  are checked. The helper confines payload reads to frozen bytes and never opens
  original provenance paths. Full uncopied SDK/archive semantics remain prior
  proof scope. A reader docstring-substring mistake and its AST correction are
  retained; a separate correct Path.open argument-index audit confirms read-only
  modes. No complete verifier/helper/export/bootstrap/engine runs. A separately
  reviewed read-only caller and actual helper observation remain required.
- New [timing Root-caller SOURCE](tests/node-compat/foundation-zlib/cost-timing-v5-root-controller-candidate-v1/README.md)
  seals30 members at `ae8e1f23…9efb`, with63 pure cases and243,164 read/hash/
  source/AST assertions over59,916 protected paths. It consumes separately issued
  Root/config/phase/window files through the genuine0af monitor, and checks full
  JSONL/17642-file publication/360-worker scope without creating any authorities.
  Independent SOURCE review is active. All native and Root plan/review action
  handles are terminal; other agents hold after their immutable checkpoints.
  Actual timing/window/budget activation remains absent until that final source
  peer and explicit idle coordination are complete.
- The all-work commit is complete, with632 changed files and a clean worktree
  before roadmap work resumes. The checkpoint does not repin historical artifacts.
- The [independent resource component SOURCE review](tests/node-compat/foundation-scheduler/independent-resource-component-source-review-v1/README.md)
  seals27 members at `dc452069…e02c`; result `a5017737…b186` covers the exact
  `74413aa9…0055` candidate. It passes60,272 finite checks plus22,024 final
  stability checks across5,506 paths,406 independent synthetic cases, six Node
  syntax checks and four Python AST parses. Actual resource20e/toolingc55/8e1/e9a,
  the whole342-source/nine-manifest frame and4,934 packaging files/22 links are
  retained in their original contexts. No bootstrap, packager, engine, component
  or guest action runs during review. A separately reviewed2400-second outer
  controller, fresh fixture-specific construction authority, actual artifact
  review and runtime gates remain required. Strict timer imports remain only
  monotonic-clock/io-poll@0.2.10; unexpected emitted interfaces must fail and
  retain full candidate bytes/WIT without policy widening.
- The [actual selector-stage DATA review](tests/node-compat/foundation-scheduler/independent-task-selection-stage-results-review-v1/README.md)
  seals11 members at `54fcdb91…e766`; result `032f686f…66a9` passes139,687
  checks/2,570 inputs. It verifies566 target/original pairs, full342=339+three
  source inventory, raw process records/clean cleanup, detached54b/no alternates
  and disjoint Git object inodes, plus old501 and666/663/667 protections within
  their declared mode scope. No stage or Git action is repeated. A newly reviewed
  normal-OFF build controller and full native ABI rebuild remain required.
- The [codec v4 actual-result DATA review](tests/node-compat/foundation-zlib/independent-cost-pilot-v4-results-review-v1/README.md)
  now seals33 members at `64472b26…37a8`; result `ffa1bc08…c032` and contract
  `e3c70652…3d10` preserve the complete actual33,066-member index. It passes
  391,060 output,125,930 prerequisite and2,759 outer-provenance checks, followed
  by59,733 path stability checks. All892 workers/12,488 typed returns,60 curves
  and120 matched-N rows are verified. This closes calibration DATA review only;
  the old16,384 proof bound and original-pilot/new-timing identity coupling still
  require the unsealed v5 source successor, independent source review, a fresh
  genuine read-only plan and later timing authority/window. No speed claim follows.
- [Component outer-controller SOURCE](tests/node-compat/foundation-scheduler/resource-component-root-controller-candidate-v1/README.md)
  seals six members at `453f220f…167c`, with19 isolated pure cases. It binds
  the genuine0af monitor,744 component source and dc452 independent source review
  to one fixture-specific construction action,2400-second outer/600-second inner
  limits and durable full raw outputs. Its [independent SOURCE review](tests/node-compat/foundation-scheduler/independent-resource-component-root-controller-source-review-v1/README.md)
  passes at `cfa0e267…7428`, with308,728 finite checks/5,555 inputs and26 pure
  cases. Actual pure-control construction starts Root97327/Node2529 under that
  reviewed controller and new fixture-specific authority. This is construction
  and initialization only; no generated module or ordinary export is invoked.
  Pure Root97327/Node2529 finishes raw0 with clean cleanup. Root result
  `952d10da…7634` retains the12,926,280-byte component `4d69fb78…287eb`, exact
  imports[] and scalar `run: func() -> string`; generated glue is retained and
  remains unloaded. Separate resource construction Root58880/Node3230 then
  finishes raw1 with clean cleanup after capturing the full12,940,860-byte
  component `55732e31…4f23e` and WIT before final admission. The
  [retained policy-refusal observation](tests/node-compat/foundation-scheduler/resource-component-clock-policy-failure-v1/README.md)
  seals at `a4a71f0d…fa66`. Its emitted root imports all six0.2.10 interfaces:
  io/error, io/poll, io/streams, cli/stderr, monotonic-clock and wall-clock.
  The strict two-interface policy is unchanged and this candidate is unadmitted.
  Neither component is instantiated or used to invoke an ordinary export after
  construction. Full core/adapter/type-graph review and selective clock/stdio
  guest pruning are required before the remaining timer constructions/runtime
  gates. The opaque rejection transport does not establish a unique exception.
- Crypto freezer source `d0d51496…f2bda` passes [independent SOURCE review](tests/node-compat/foundation-crypto/independent-ownership-secret-freezer-source-review-v1/README.md)
  at `a7be2c58…4a75`; result `23bbe8b6…a3e9` covers257,314 finite checks,
  24,312 canonical inputs,24 independent pure cases and seven Python AST parses.
  The first finite reader reaches an incorrect whitespace assumption in a source
  substring check; its raw1 failure is preserved. Only that reader spelling is
  corrected for a fresh read/hash/pure pass. The sealed candidate is unchanged;
  no helper, Ninja, copy, engine or guest action runs during source review.
  New normal-only [freeze authority](tests/node-compat/foundation-crypto/ownership-secret-normal-off-freeze-v1-root-authority.json)
  starts Root68560/controller1667 under the genuine owned monitor. The actual
  [normal-OFF freeze finishes raw0](tests/node-compat/foundation-crypto/ownership-secret-normal-off-freeze-v1-root-results.json)
  with both owned groups clean, both actual raw helper captures retained and
  1,902 copies/1,899 original references/1,903 actual files verified. Receipt
  `da2588f4…a5c2` is1,568,778 bytes. Frozen engine901c/raw metadataCBF remain
  byte-identical, copies0600/private/separate inodes; no engine or guest executes.
  The [independent frozen-artifact DATA review](tests/node-compat/foundation-crypto/independent-ownership-secret-normal-off-frozen-artifact-review-v1/README.md)
  passes at `380e0735…0d96`; result `e0eecded…9fcc` and contract
  `44139ff1…0167` pass275,080 checks/26,247 paths, all1,902 copies/1,899
  originals,25,594 BUILD rows,1,424 stage rows, actual raw helper/owned terminals
  and prior normal protections. Six reviewer schema assumptions are retained as
  history and corrected without owner changes. New frozen-only verifier/export/
  pin/bootstrap SOURCE preparation is next; no such tool is yet admitted and no
  GC reconfiguration is authorized.
  Accepted production remains bounded foundations-v13;
  broader lifecycle/ALS, crypto APIs, optional capability profiles and release
  gates remain outstanding.
- The [timing-only v5 source successor](tests/node-compat/foundation-zlib/cost-pilot-timing-candidate-v5/README.md)
  seals77 members at `e7993501…b321`, binding the actual64472 pilot DATA review
  while preserving b5 as the original calibration source. Source preparation
  records3,924 finite checks,46 pure cases,12 parser/five AST checks and the
  complete38-module/151-edge ancestry. Finite bounds are56,894 for pilot DATA,
  17,642 for timing publication and16,384 for unchanged historical roles. The
  original60 curves/120 N budgets and full33,066-member pilot index are retained.
  Independent source review is underway; all new action/window/budget slots stay
  NULL. A [fresh v5 read-only plan caller](tests/node-compat/foundation-zlib/cost-measurement-plan-v5-root-caller-source.json)
  is prepared without activation. It preserves original relative publication
  rows and separately resolves confined absolute descriptors. It requires the
  actual new source peer before any Root plan authority/action. No timing runs.
- The [selector normal-OFF build-controller SOURCE](tests/node-compat/foundation-scheduler/task-selection-build-controller-candidate-v1/README.md)
  seals17 members at `dd69c405…980f`. It binds the actual88af integration,
  959b controller and54fc stage DATA review to the existing f751 lifecycle and
  0af owned monitor in their genuine original contexts. Preparation passes156,851
  finite checks/2,594 inputs,41 isolated pure cases/four Python AST parses and
  three exact primitive extractions. The new caller adds a strict clean-termination
  check before accepting metadata. Independent SOURCE review and fresh Root
  build authority remain required; no build, native engine or metadata is emitted
  by preparation. Root review is the next native-build dependency.
- The pure component artifact and timer policy-refusal DATA/core-import graph
  review is active separately. It may use finite read-only binary inspection;
  no target core/module loading, compilation, instantiation or ordinary guest
  execution is authorized by that review. The timing v5 source peer review is
  active; no plan authority or timing window has been issued. Current Root
  external action handles68560,97327 and58880 are all terminal.

All-work Git checkpoint requested on 2026-11-05: this checkpoint preserves the
completed work and unfinished drafts since `3dcd49d`. Writers stop before staging.
Native engines, generated components and external build/runtime trees remain
outside Git; their retained receipts identify exact artifacts. Nothing is pushed.
The historical baseline and accepted production checkpoint remain unchanged.

Checkpoint checks parse345 JSON files,77 Python files,51 JavaScript modules and
two shell scripts, and resolve1,383 local tracker/documentation links without
missing targets. Five additional `.mjs` files are deliberately invalid tamper
fixtures created by `test-source-families.mjs`; their exact evidence bytes are
preserved. Staged whitespace checks report the exact sealed freezer-body final
blank line and context-space lines in two unapplied patch artifacts; those bytes
are retained to preserve their hashes. The changed-file credential/artifact screen
finds no concrete blocker. This checkpoint contains632 changed files.
No runtime suite, native build or timing action is repeated for this Git checkpoint.

Latest continuation after Git checkpoint `3dcd49d`:

- The [codec worker diagnosis](tests/node-compat/foundation-zlib/cost-pilot-v3-worker-import-diagnosis-v1/README.md)
  seals24 members at `cb9ade31…3063`. Complete source authentication and worker
  module linking pass without a worker/loader/guest call. A retrospective DATA
  check rejects the exact environment guard: pinned Node receives the eight
  requested entries plus macOS `__CF_USER_TEXT_ENCODING=0x1F5:0x0:0x0`.
  A benign Node child reproduces this extra key. A proposed exact Darwin
  uid/zero/zero exception lets the inspected pre-output models pass, while other
  keys/values remain forbidden. The original worker discarded its exception;
  its exact error and actual environment were not captured. Independent failure
  review now passes at [index231ad982](tests/node-compat/foundation-zlib/independent-cost-pilot-v3-failure-review-v1/README.md),
  preserving that limit. The subsequent [v4 source](tests/node-compat/foundation-zlib/cost-pilot-timing-candidate-v4/README.md)
  seals59 members at `b5b4c9e9…f89d1`: narrow Darwin environment handling,
  observed-environment recording and bounded fixed-stage stderr diagnostics
  preserve all original cases/caps/FNV and360-worker timing protocol. Its
  [independent source review](tests/node-compat/foundation-zlib/independent-cost-pilot-timing-v4-source-review-v1/README.md)
  passes at `19594c59…33b7`, with4,702 source checks/1,080 physical paths,
  69 pure cases and nine parser checks. The model's input domain is the actual
  fresh enumerable `process.env` snapshot, not arbitrary non-enumerable objects.
  New read-only [plan authority](tests/node-compat/foundation-zlib/cost-measurement-plan-v4-root-authority.json)
  starts Root37441/Node45086 under the genuine900-second owned monitor.
  The genuine read-only parent45086 finishes raw0 in158.473 operational seconds,
  with clean owned-group cleanup. Root caller37441 then exits1 while resolving
  three relative publication rows from the repository directory. A separate
  [read-only collector](tests/node-compat/foundation-zlib/cost-measurement-plan-v4-observe.py)
  finishes raw0 and writes [result83566613](tests/node-compat/foundation-zlib/cost-measurement-plan-v4-root-results.json),
  preserving original relative rows and separately verified confined absolute
  descriptors. No action is repeated. Actual plan `297f8fbb…6838` is53,862 bytes.
  Its [independent DATA review](tests/node-compat/foundation-zlib/independent-cost-measurement-plan-v4-results-review-v1/README.md)
  passes at `f7ec29c0…d20b`:307,437 checks/25,719 physical files reconstruct all90
  rows,60 encoded streams/15 Node-oracle matches and three artifact tuples.
  A [future v4 calibration caller](tests/node-compat/foundation-zlib/cost-pilot-v4-root-controller-source-derivation.json)
  is prepared. Its first overlapping text-reversal check
  fails after writing unlaunched source; exact offset reconstruction and AST
  checks then pass, with no authority, worker or guest action.
  After the native build and all three agent audit/source jobs are terminal,
  new [v4 calibration authority](tests/node-compat/foundation-zlib/cost-pilot-v4-root-authority.json)
  starts Root2880/Node80579 under the genuine7200-second owned monitor. The
  preselected90-minute budget/two-hour coordinated window preserve all60 pairs,
  original geometric caps, both arms at50ms and full raw controls/FNV. All three
  agents explicitly hold writes/checks/audits until Root releases them after the
  actual terminal outcome. Unrelated workstation activity remains uncontrolled.
  The actual pilot finishes raw0 in1,850.192 operational seconds, with clean
  owned-group cleanup and no timeout, signals or forced cleanup. The
  [Root observer](tests/node-compat/foundation-zlib/cost-pilot-v4-root-results.json)
  records60 calibration curves,892 fresh workers,5,352 separate controls,
  3,568 codec batches and120 matched-N rows. It hashes33,066 indexed files;
  33,068 files exist including the index and completion receipt. The
  [window completion receipt](tests/node-compat/foundation-zlib/cost-pilot-v4-quiet-window-completion.json)
  closes the coordinated hold and agents resume. This is calibration only;
  actual timing and any performance advantage remain unverified. Independent
  actual-result review is preserved as [unsealed work in progress](tests/node-compat/foundation-zlib/independent-cost-pilot-v4-results-review-v1/checkpoint-status.json):
  391,060 output-replay checks and125,930 prerequisite checks pass, but final
  outer-process provenance checks and the formal result/contract/seal remain open.
  The timing consumer's16,384-file proof limit cannot
  admit this pilot's full index. A separate
  [v5 draft history](tests/node-compat/foundation-zlib/cost-pilot-timing-candidate-v5/preparation-history.json)
  records an unsealed, unvalidated source correction: finite protocol-derived
  bounds and distinct original-pilot/new-timing source identities. Its actual
  calibration-review binding, dependency manifests, source/pure/parser checks,
  template correction and seal remain open; all new action authorities are NULL.
- The [crypto secret integration source](tests/node-compat/foundation-crypto/ownership-secret-integration-candidate-v1/README.md)
  is now sealed at `7eb863b9…4108` (24 members), superseding its draft status at
  the Git checkpoint. Its [independent source review](tests/node-compat/foundation-crypto/independent-ownership-secret-integration-source-review-v1/README.md)
  passes at `8665997e…ca45`:44,751 finite data/pure/AST checks rehash4,176 inputs,
  validate355 paths=352 unchanged+three corrected afterimages, reverse the three
  exact derivations/22 edits, and preserve normal1391/1387 protection. Actual
  bash/Node parser-only checks finish0. No helper, stage, native build, freezer,
  engine, guest, crypto or fault action runs in that source scope. The
  [owned stage controller source](tests/node-compat/foundation-crypto/ownership-secret-stage-controller-candidate-v1/README.md)
  seals14 members at `7758e1a7…0a12`. Its [independent source review](tests/node-compat/foundation-crypto/independent-ownership-secret-stage-controller-source-review-v1/README.md)
  passes at `ec9df97a…5804`, with27,298 read/hash/pure checks over4,189 inputs and
  the actual1,424-copy merger. A Root reader guessed a monitor parameter name;
  the retained history corrects that to the source-indexed actual binding,
  without an owner action. New [source-stage authority](tests/node-compat/foundation-crypto/ownership-secret-stage-v1-root-authority.json)
  starts Root35883/controller42623 with the genuine nested owned monitor and
  a900-second outer/600-second stage deadline. Actual controller42623 and
  stage42671 finish raw0 in15.275/7.675 operational seconds, with both observed
  groups gone and no timeout, signals or forced cleanup. The Root caller then
  exits1 because its report reader treats two monitor/result JSON lines as one
  document. A separate [read-only observer](tests/node-compat/foundation-crypto/ownership-secret-stage-v1-observe.py)
  finishes Root53448 raw0 and writes [result417fbe74](tests/node-compat/foundation-crypto/ownership-secret-stage-v1-root-results.json).
  It rehashes all1,424 copy/original pairs, modes and distinct inodes, checks355
  final sources, detached54b/no alternates/disjoint Git object inodes and normal
  1,391/1,387 protection. Staging is not repeated; work/freeze remain absent.
  [Independent actual-stage review](tests/node-compat/foundation-crypto/independent-ownership-secret-stage-results-review-v1/README.md)
  passes at `41f8a49f…2ffec`, with97,074 data checks/5,636 files and complete
  envelope/copy/normal/Git-isolation verification. The [normal-OFF build controller](tests/node-compat/foundation-crypto/ownership-secret-build-controller-candidate-v1/README.md)
  seals15 members at `c9573e41…3643`; its [independent source review](tests/node-compat/foundation-crypto/independent-ownership-secret-build-controller-source-review-v1/README.md)
  passes at `65caf5b0…bd3a` (43,510 finite checks/5,631 inputs). New build-only
  [Root authority](tests/node-compat/foundation-crypto/ownership-secret-normal-off-build-v1-root-authority.json)
  starts Root95352/controller48796 under the genuine owned monitors. The one-job
  ordinary Release normal-OFF [build finishes raw0](tests/node-compat/foundation-crypto/ownership-secret-normal-off-build-v1-root-results.json),
  completing all108 Ninja steps and clean owned-group cleanup in508.722 outer/
  491.549 inner operational seconds. Fresh engine `901c7ba5…a1a7` is10,003,155
  bytes; raw metadata `cbf93013…15c8` is393,125 bytes. The [independent BUILD-only review](tests/node-compat/foundation-crypto/independent-ownership-secret-normal-off-build-review-v1/README.md)
  passes at `6a0ce53a…d32c`:125,165 main+705 witness+55,727 distribution checks,
  with68 compile-DB rows=62 native+five other native-manifest sources+one null,
  four strict/six private commands, one separate embedding command,11 manifests
  and29 unique archives (30 ordered archive arguments). Compiler/SDK/SM/Rust/
  OpenSSL/codec/link provenance and normal1,391/1,387 protection are verified.
  A duplicate-link-argument reader assumption is corrected without rerunning
  the build. No freeze, engine/runtime or production acceptance follows yet.
  Start2GiB/stop800MiB are disk-space bounds, not memory bounds. Independent
  BUILD-only review uses the actual terminal/result evidence.
  New [freezer tooling SOURCE](tests/node-compat/foundation-crypto/ownership-secret-freezer-candidate-v1/README.md)
  seals26 members at `d0d51496…f2bda`, bound to the actual BUILD review and
  its complete input ledger. It records1,055,466 finite checks,64 pure models,
  seven Python AST parses and24,306 canonical input paths. No helper, Ninja,
  copy, freezer, compiler, engine or guest action runs in that source scope.
  Independent source review, actual normal freeze and frozen-artifact review
  remain required. Frozen-only verifier/export/pin/bootstrap tooling is explicitly
  absent; no later variant, runtime or adoption authority is issued.
- Scheduler [resource pin tooling](tests/node-compat/foundation-scheduler/resource-pin-tooling-candidate-v1/README.md)
  seals39 members at `c55fd0fc…6238`. Its [independent source review](tests/node-compat/foundation-scheduler/independent-resource-pin-tooling-source-review-v1/README.md)
  passes at `78376ab0…e07a` with7,518 finite checks/1,294 inputs. New export-only
  Root authority starts Root38261/Python44303; the [actual export](tests/node-compat/foundation-scheduler/resource-normal-off-pin-export-v1-root-results.json)
  finishes raw0 with clean owned-group cleanup. Candidate `93879925…5256`
  is259,618 bytes and remains explicitly UNREVIEWED, normal-OFF only with the
  other three variants NULL. Its [independent export review](tests/node-compat/foundation-scheduler/independent-resource-normal-off-pin-export-review-v1/README.md)
  passes at `b552683c…fcc0`, with38,074 DATA checks/1,453 paths. New validation-only
  [pins](tests/node-compat/foundation-scheduler/reviewed-resource-normal-off-native-pins-v1.json)
  and a separate Root review/bootstrap authority precede Root15190. Actual CLI
  Python46587 and API Node46632 finish raw0; the [Root result](tests/node-compat/foundation-scheduler/resource-normal-off-bootstrap-v1-root-results.json)
  `8e1f250f…07c1` compares whole CLI/API frames with nine full manifests and
  unchanged enginefec7/metadata51fb. Four Python calls and one Node process are
  observed across two clean groups. The [independent bootstrap review](tests/node-compat/foundation-scheduler/independent-resource-normal-off-bootstrap-review-v1/README.md)
  passes at `e9a798cc…3175`, with64,504 checks/1,917 hashes. Two full public frames
  are retained; intermediate API-return equality is authenticated-code/clean-exit
  supported rather than four separately retained frames. No engine/component/guest
  executes. Separate [component construction source](tests/node-compat/foundation-scheduler/resource-component-candidate-v1/README.md)
  seals99 members at `74413aa9…0055`, with33,033 source/data checks,110 pure cases,
  ten Node parser/four Python AST checks and5,399 preparation inputs. It binds
  the genuine c55 API/whole bootstrap frame,4,934 packaging files and22 link
  witnesses, preserving complete callback capture before strict two-interface
  admission. Independent source review and all construction/runtime phases remain
  unissued. Root's independent source review is unfinished and has no sealed
  result. Accepted production remains foundations-v13.
- The [all-invalid task-selection source proposal](tests/node-compat/foundation-scheduler/task-selection-candidate-v1/README.md)
  seals22 members at `d41686ae…fffb`. The existing `AsyncTask::select` changes
  its return contract to `std::optional<size_t>`; pruning an empty queue returns
  nullopt and its sole event-loop caller rechecks the ordinary checkpoint and
  interest boundary before indexing. Three exact source reversals,12 standalone
  instrumented selector cases and two actual SDK frontend calls pass, with1,031
  dependency paths retained. No engine/component is built or run. Its
  [independent source review](tests/node-compat/foundation-scheduler/independent-task-selection-source-review-v1/README.md)
  passes at `f0a91441…503a`, checking37,952 predicates/1,782 hashes and1,325
  independent scalar cases. EventLoop/interest/rooting/JS/WASI behavior is not
  executed by those models. Native integration and real component behavior
  remain unverified. A [new integration source](tests/node-compat/foundation-scheduler/task-selection-integration-candidate-v1/README.md)
  seals32 members at `88af5db1…74f1`, composing342 paths=339 resource sources
  unchanged+three selector afterimages, preserving the timer patch. Its10,007
  source/data/pure checks, parser evidence and533-row stage plan establish no
  actual staging/build/runtime result. Its [independent source review](tests/node-compat/foundation-scheduler/independent-task-selection-integration-source-review-v1/README.md)
  passes at `145e3ad2…c985`, with24,904 finite checks/575 inputs, all four exact
  derivations/25 edits and566 dynamic stage targets. The dormant publisher still
  needs a separately reviewed owned controller and complete partial-failure
  capture. The [new controller source](tests/node-compat/foundation-scheduler/task-selection-stage-controller-candidate-v1/README.md)
  seals12 members at `959b3e73…fb46`:17,395 read/hash/pure/AST checks over1,933
  inputs reconstruct566 targets and eight owned filesystem models. Original
  modes are captured before launch; truncated/mismatched/symlink/nonregular/shared
  inode targets remain partial observations, with raw stderr retained for normal
  Git progress. Source/normal protection and durable failure observation are
  explicit. No real controller, Git, stage, compiler, engine or guest executes.
  [Independent controller source review](tests/node-compat/foundation-scheduler/independent-task-selection-stage-controller-source-review-v1/README.md)
  passes at `8c288dc1…20dc`, with86,191 finite checks/2,375 files and33 pure
  negative cases. New Root authority starts the actual source stage under
  Root50545/controller95581; both finish raw0 with clean owned-group cleanup.
  The [Root stage result](tests/node-compat/foundation-scheduler/task-selection-stage-v1-root-results.json)
  `9c7403b0…b949` records all566 planned targets matching retained observations
  and the final protection recheck. Independent actual-stage review and the
  complete ABI-changing native rebuild remain required. No new engine, freeze,
  pins or runtime gate is accepted for this selector change.
  Fallible enqueue, cached-pollable lifetime, cancellation,
  reset/reuse and ALS remain open.

At Git checkpoint `3dcd49d`, all-work preservation was requested again on
2026-11-05 and writers stopped. That
checkpoint includes the subsequent crypto GC component/runtime/stock-Wasmtime
results and independent reviews, preserved failures and corrections, scheduler
normal build/freeze evidence and reviews, source fixes, and current documentation.
The [crypto secret integration draft](tests/node-compat/foundation-crypto/ownership-secret-integration-candidate-v1/README.md)
is deliberately included as unsealed work in progress: stored source checks pass
for355 paths (352 unchanged and three corrected), but final source review/seal,
independent review, stage/build controllers, artifact tooling and actual native
validation remain open. No new production acceptance or complete compatibility
claim follows. External engines and build artifacts stay outside the repository;
their receipts remain committed. No push is requested.

Checkpoint checks parse381 structured JSON files and70 Python files and resolve
1,437 local documentation links without missing targets. Two additional files
named `stdout.json` are intentionally empty raw streams from retained failed
source-check attempts; their adjacent terminals record raw1. Whitespace checks
report only preserved crypto source snapshots and unapplied patches. Those
evidence bytes are retained to preserve their hashes. No runtime suite or
calibration retry is run for this Git-only checkpoint.

Latest continuation after Git checkpoint `6bc62c1`:

- Consumer355 HTTP: actual both-host gate and independent result review pass;
  six accepted responses and77 separate readiness attempts are retained.
- Crypto GC: isolated source stage and native build pass review. Corrected freeze
  and full frozen-artifact review pass. Corrected unreviewed pin export finishes
  raw0 and its independent data review passes. New validation-only GC pins and
  paired bootstrap authorities are issued; the genuine pure selector passes.
  Independent finite pin/authority checking passes. Actual Python bootstrap
  and genuine JS API observation finish raw0 with equal full frames,11 actual
  manifests, stable rechecks and clean process cleanup; independent actual
  bootstrap review passes. GC component source and independent source review pass;
  actual construction finishes raw0 under Root96509, with imports[] and four WIT
  functions; independent artifact review passes. GC runtime v1 source passes
  review, but its first actual attempt fails before guest execution on17 relative
  input paths. Failure and review correction are preserved; the v2 source and
  independent review pass. The fresh v2 runtime finishes raw0 under Root52246:
  23 whole strings/20 records and45 full signatures match the retained Node
  oracle; independent actual-result review passes. Three fresh stock-Wasmtime GC
  wrapper calls finish raw0 and match the entire Jco wrapper. Independent host
  result review passes. No new production adoption has run.
- Scheduler: the timer/task ownership patch,342-source integration candidate and
  independent integration source review pass. Production remains unchanged; actual
  staging and independent stage review pass in separate Root session52275.
  The normal-OFF build controller and its independent source review pass; actual
  native compilation and independent BUILD-only review pass under
  Root12069/Python96368. Normal freeze finishes raw0 under Root19779 and its
  independent frozen-artifact review passes. Pins/bootstrap/runtime, clock closure,
  fallible global enqueue, reset/reuse and ALS work remain open.
- Codec calibration pilot v3 ends raw1 under Root62440: the first native-on
  case0/N1 worker exits status1 with empty streams; no pair or matched plan
  completes. [Failure evidence](tests/node-compat/foundation-zlib/cost-pilot-v3-failure-root-checkpoint-v1/README.md)
  is retained and the coordinated window is closed. Diagnosis and independent
  failure review remain open. Actual timing, broader
  lifecycle work and optional standard-capability variants remain outstanding.
  Accepted production remains bounded foundations-v13.

Git checkpoint requested on 2026-11-04: commit
`e7c6e2ce4f430811b90bcad77620c1e549963ca0` preserves the implementation,
documentation, source snapshots, validation evidence, historical failures and
unfinished templates. Follow-up commit
`c51cc993a536beea358ea78f4866b116300df0fb` collects the final in-flight work
and tracker. A further all-work checkpoint was requested on 2026-11-05 and
commit `d54d9d4b565cdd00f84cf751ac60fe5ec553f5c5` includes the subsequent
source templates, executed results, independent reviews, preserved HOLDs and
tracker (644 changed files). Its final worktree was clean; nothing was pushed.
Roadmap work has resumed after that checkpoint. Native engines and external build/runtime artifacts
under `/tmp/starling-node-compat` remain outside this repository; committed
receipts retain their exact references and limits. The pinned
`54b3329b3ce818fd1f244e871e9c259b63667cda` remains the historical baseline;
the Git checkpoints do not automatically revalidate or repin earlier evidence.

At Git checkpoint `6bc62c1`, a further all-work commit was requested on 2026-11-05. It includes the
subsequent HTTP both-host results, GC source/build/freeze/export evidence and
reviews, preserved failures, scheduler ownership source, and updated trackers.
Writers stopped before staging. Two current drafts are deliberately included
without a seal or acceptance claim:

- [GC component construction draft](tests/node-compat/foundation-crypto/ownership-gc-component-candidate-v1/README.md):
  six parser-only checks pass; closure audit, lifecycle review, source seal,
  actual bootstrap, component construction and runtime validation remain open.
- [Scheduler integration draft](tests/node-compat/foundation-scheduler/resource-integration-candidate-v1/README.md):
  preparation reports5,399 source/pure checks over822 inputs; source seal,
  independent review, activation, native build, packaging and runtime gates
  remain open. The timer/task patch is still unapplied.

The checkpoint preserves work in progress; it does not complete the roadmap,
change the accepted foundations-v13 profile, or include external temporary
build artifacts. No push is requested.

Checkpoint validation parses all288 new JSON files and96 Python files, and
resolves988 local documentation links without missing targets. Staged whitespace
checks report existing blank EOF lines in four sealed Python bodies and preserved
whitespace in the scheduler baseline/patch snapshots; those evidence bytes are
retained to preserve their hashes. No runtime suite is rerun for this Git-only
checkpoint.

The [crypto-v3 source correction](tests/node-compat/foundation-crypto/ownership-component-candidate-v3/README.md)
is now sealed at index `593a0e02…c492` with25 files. The draft checker's
`common.py` path was corrected to the actual `artifact_common.py` before its
checks. Preparation reports40 pure,1,759 source/data and8 parse checks;
Root separately verifies all25 indexed members and repeats the40 pure checks.
No bootstrap/component/key operation ran during that preparation. The separate
[independent source review](tests/node-compat/foundation-crypto/independent-ownership-component-v3-source-review-v1/README.md)
now passes at index `e9575477…80c6`, rehashing12,106 unique inputs and confirming
the actual configured context and adapter caller. A new
[Root component authority](tests/node-compat/foundation-crypto/ownership-component-v3-root-authority.json)
(`83f5dca5…2193`) launches construction-only Root session65197/PID5288. The
[actual build](tests/node-compat/foundation-crypto/ownership-component-v3-root-results.json)
finishes raw0 in38.340 operational seconds, with worker5394 raw0 and both owned
groups gone. Component `842f82e8…149d` is13,107,415 bytes, imports nothing and has
four ordinary WIT functions plus the empty non-WIT Jco `_util` helper. All22
indexed/24 actual files rehash. The separate
[artifact review](tests/node-compat/foundation-crypto/independent-ownership-component-v3-results-review-v1/README.md)
passes at index `8be6c70b…2200`, including independent WIT decode, exact nested
core bytes, core imports[]/no start and captured ESM/TLA loading-source checks.
No generated module import or key operation occurs in that construction scope.

The new [normal runtime source](tests/node-compat/foundation-crypto/ownership-runtime-candidate-v1/README.md)
is sealed at index `4cb0d2c3…9dea`:22 members,13,247 inputs,61 pure/counterexample
checks,13,274 source-data checks and7 JS/1 Python parse checks. It uses actual
four-function ESM loading, three fresh owned sessions, whole public returns and
a pinned host Node oracle. The separate
[runtime-source review](tests/node-compat/foundation-crypto/independent-ownership-runtime-source-review-v1/README.md)
passes at index `19e4dcdb…fec7`. New normal-only
[Root authority](tests/node-compat/foundation-crypto/ownership-runtime-v1-root-authority.json)
(`fc11d47b…77b4`) and the2400-second external controller launch Root61190/PID9872.
The [actual run](tests/node-compat/foundation-crypto/ownership-runtime-v1-root-results.json)
finishes raw0 in63.581 operational seconds; workers9893/9940/10005 also finish
raw0 with owned-group cleanup. All46 indexed/48 actual files rehash. Root decodes
23 complete public strings/20 case records: ten imports,55 sign attempts and50
verify attempts. All45 successful32-byte signature records match the pinned
Node/RFC oracle;45 verification booleans split25 true/20 false. Expected guarded
refusals are included in attempt counts. The
[independent actual-result review](tests/node-compat/foundation-crypto/independent-ownership-runtime-v1-results-review-v1/README.md)
passes at index `abcb6da3…2c42`, with stable contract `859649ed…7e4f`. It
independently checks every returned value/type and13,336 unique inputs, including
the full Node oracle, three distinct worker lifetimes, all raw strings and
guarded refusals. These are public/source-coupled observations, not native tracing.
The normal phase adds no Wasmtime key run, GC, OOM, reset,
finalizer/free/wipe/isolated-root observation or Node crypto export. Those and secret-temporary/allocation follow-ons
remain outstanding.

The [stock-Wasmtime source](tests/node-compat/foundation-crypto/ownership-wasmtime-candidate-v1/README.md)
now seals30 members/13,425 inputs at `6f5d38ec…6256`. Root's separate
[source review](tests/node-compat/foundation-crypto/independent-ownership-wasmtime-source-review-v1/README.md)
passes at `b51dc7f6…c37c`, including37 pure checks,59 exact JavaScript contract
comparisons and4 JS/4 Python parser checks. New
[Root authority](tests/node-compat/foundation-crypto/ownership-wasmtime-v1-root-authority.json)
(`5184d974…b9cb`) launches Root43833/PID15457 for three fresh literal
`validate()` calls on the same842f component. The [actual stock-host run](tests/node-compat/foundation-crypto/ownership-wasmtime-v1-root-results.json) finishes parent raw0 in878.006 operational seconds, with workers16735/17913/17995 raw0 and owned groups gone. All23 indexed/25 actual files rehash. Three complete decoded strings are byte-identical to the reviewed normal wrapper:12 case records, six imports,33 sign attempts,30 verify attempts,27 full tags and27 verification booleans (15 true/12 false). The [independent result review](tests/node-compat/foundation-crypto/independent-ownership-wasmtime-v1-results-review-v1/README.md) passes at `d1e3f9f1…357b`, contract `14626e81…e90e`. It strictly decodes all three raw WAVE strings, verifies47,187 decoded UTF8 bytes and every expected field, all process lifetimes and13,504 inputs. No generated JS, new Node oracle, GC, OOM, reset or timing runs; one outer export per process proves no separate-host-call interleaving or instance reuse.

The [independent control-v2 result review](tests/node-compat/foundation-zlib/independent-cost-jco-control-v2-results-review-v1/README.md)
is now sealed at index `20380e3b…7ae9`. It verifies726 complete raw strings,
540 controls,90 setups,90 checkpoints and6 identity calls, the1,480-indexed/
1,482-actual-file output closure and all three worker exits/cleanup. This is
bounded public control correctness; it provides no private heap inspection or
global codec instrumentation. The original `pilotPrerequisitesSatisfied:false`
and `timingAllowed:false` remain unchanged; a new phase still needs its own
complete source and execution authority.

At commit `c51cc99`, the [pilot/timing source](tests/node-compat/foundation-zlib/cost-pilot-timing-candidate-v1/README.md)
was eight explicitly unsealed WIP files. Its completed v1 seal is now
`55db1fc3…135b` (85 indexed files/699 external inputs), with90 pure/mock,
6,924 source-data and17 parse checks, plus separate bounded real host-only
lifecycle regressions. Independent review finds a concrete pre-action blocker:
its nested-proof reader applies a64MiB buffer limit to the actual108,619,024-byte
Node executable. Authentic prerequisite admission therefore refuses before any
worker. The sealed v1 and its [M1 review](tests/node-compat/foundation-zlib/independent-cost-pilot-timing-source-review-v1/README.md) stay unchanged. A thin v2 (`1a294044…30a2`) corrects M1 and passes17 genuine nested-descriptor read/hash tests. Its separate [M2 review](tests/node-compat/foundation-zlib/independent-cost-pilot-timing-v2-source-review-v1/README.md) holds it because inherited parent lifecycle/collector files are absent from runtime source rechecks. The current donor bytes match; the guard coverage is incomplete. The [v3 source](tests/node-compat/foundation-zlib/cost-pilot-timing-candidate-v3/README.md), index `c2ce5f08…64e9` (50 members/918 inputs), adds standard-only bootstraps and complete inherited-family/dependency authentication before custom imports and at final/failure rechecks. Its [independent source review](tests/node-compat/foundation-zlib/independent-cost-pilot-timing-v3-source-review-v1/README.md) passes at `50102240…5bc8`; both held versions remain immutable. No codec pilot/timing
has run. The original360 workers/3,600 codec batch calls/2,160 N1 controls remain
planned. Pilot/timing phase/window/global-budget authority remains NULL. A separate [read-only plan action](tests/node-compat/foundation-zlib/cost-measurement-plan-v3-root-results.json) finishes Root76299/PID25616 raw0 in176.554 operational seconds after genuine full prerequisite guards. Its three-file output includes53,862-byte compact plan `c914e3a0…83b`, with90 expected arm/case fingerprints and three artifact tuples. No guest/codec/worker/pilot/timing action occurs. The [independent plan review](tests/node-compat/foundation-zlib/independent-cost-measurement-plan-v3-results-review-v1/README.md) passes at index `5e81da01…73c`, contract `c2240eca…bf4a`: all90 rows and three artifact tuples are independently reconstructed and25,590 physical files rehashed. This read-only plan provides no measurement execution authority.

The [calibration source decision](tests/node-compat/foundation-zlib/cost-pilot-calibration-source-root-decision-v1.json)
selects fresh paired workers at each geometric N: three same-N warmups, then one
public-call sample, stopping at the first N where both arms reach50ms. Original
caps, budget formula, timing population and separate controls are unchanged.
This selects an implementation design; pilot/timing execution and quiet-window
authority remain false/NULL. The completed v3 source binds the actual
new control-result contract. The consumer355 HTTP gate remains in progress. The new
[consumer355 HTTP construction source](tests/node-compat/foundation-stream-consumers/http-construction-candidate-v1/README.md)
is sealed at index `dc98f465…5487` (39 files/12,789 preparation references),
with54 pure/12,714 source-data/20 parse checks. It preserves the original
protected29/classic19 guest bodies and oracles, adds two request-local iterable
probes, and binds the full original355 context and12,667-file tool/native/data
closure. The [independent source review](tests/node-compat/foundation-stream-consumers/independent-http-construction-source-review-v1/README.md) passes at `dbfa80ae…5efa`. The [actual source publication](tests/node-compat/foundation-stream-consumers/http-source-publication-v1-root-results.json) finishes Root27233/PID16764 raw0 in136.683 operational seconds:32 indexed/34 actual files,18 identical payload copies with distinct inodes and private/no-symlink output. The [independent publication review](tests/node-compat/foundation-stream-consumers/independent-http-source-publication-v1-results-review-v1/README.md) passes at `be271a1a…f3b7`; that copy phase runs no genuine helper or runtime action. A separate [bundle-only action](tests/node-compat/foundation-stream-consumers/http-bundle-v1-root-results.json) now finishes Root93103/PID19432 raw0 in75.079 operational seconds, worker19665 raw0/clean. Genuine full355 preflight succeeds; all19 indexed/21 actual files rehash, with6,614,128-byte bundle `ef192251…25a5`, exact18 native/standard imports and sole `incomingHandler` export. The [whole-entry bundle review](tests/node-compat/foundation-stream-consumers/independent-http-bundle-v1-results-review-v1/README.md) passes at `8129c85c…5980`, including all53 module identities, six complete virtual data modules, nine CJS bodies and original fixtures. The separate [actual component build](tests/node-compat/foundation-stream-consumers/http-component-v1-root-results.json) finishes Root20204/PID23572 raw0 in87.647 operational seconds, worker23812 raw0/clean. Component `2ce7d990…5f33` is64,098,281 bytes; all34 indexed/36 actual files rehash. Its [independent artifact review](tests/node-compat/foundation-stream-consumers/independent-http-component-v1-results-review-v1/README.md) passes at `da7a8d79…6bad`, verifying actual decoded six0.2.10 imports, type-only duration clock/no callable core clocks, sole incoming-handler and full source/native/core provenance. The host source is sealed but held on failure-evidence capture, as recorded below; no new host request or wire-body adapter has run.
Crypto construction and bounded normal key validation above are complete;
timing has not started. Its new external watchdog/ACK path has separately run
bounded benign host-only success/refusal/timeout regressions; the first evidence-
serialization failure is preserved and the original timing v1/v2 sources remain held while the corrected v3 has passed source review and actual read-only plan preparation.

The [HTTP host source](tests/node-compat/foundation-stream-consumers/http-host-candidate-v1/README.md)
is sealed at `4b7c36f2…0e70`. Its [independent source review](tests/node-compat/foundation-stream-consumers/independent-http-host-source-review-v1/README.md)
is **HOLD**, index `58ec38a3…c641`: a failure after receiving headers or body
chunks can discard available raw response data while claiming full retention.
The other bounded source/admission/lifecycle paths pass review. No new host
request ran. The [thin v2 correction](tests/node-compat/foundation-stream-consumers/http-host-candidate-v2/README.md)
is now sealed at `9fc935f6…0788` (31 members/12,835 inputs), with110 injected
pure capture checks,39,100 source/data checks and7 grammar/2 Python AST checks.
Headers, each observed chunk and complete/partial aggregates are persisted before
semantic validation; writer and failure-receipt flags distinguish incomplete
capture. Old source/HOLD remain unchanged. The [independent v2 source review](tests/node-compat/foundation-stream-consumers/independent-http-host-v2-source-review-v1/README.md)
passes at `88ed7e21…3124`, contract `c73e3ef8…dec4`: all31 current members,
held families,12,835 declared inputs,108 graph edges,26 reversals and full actual
native/component context are verified. Actual both-host execution is recorded below.

The [crypto GC source proposal](tests/node-compat/foundation-crypto/ownership-gc-candidate-v1/README.md)
seals an isolated-build/hex-pressure design at `3b6f0480…3dcf`.
Existing `NODE_COMPAT_BUILD_ROOT` supports a fresh build root; GC freeze must
also use a separate root to preserve normal exact membership and both mutable
normal CMake originals. Public Buffer hex paths reach the real stress-GC hook;
`Buffer.alloc` alone supplies allocation pressure. The [independent v1 review](tests/node-compat/foundation-crypto/independent-ownership-gc-source-review-v1/README.md)
holds it at `2ac980be…d597` because its inherited false GC/entropy flag contradicts
deliberate pressure. The [thin v2 correction](tests/node-compat/foundation-crypto/ownership-gc-candidate-v2/README.md),
index `7988586f…88b0`, removes that field and introduces versioned observations:
per-run pressure request counts[4,4,8,0], outer16, entropy false and actual native
GC count unobserved. Its [independent v2 source review](tests/node-compat/foundation-crypto/independent-ownership-gc-v2-source-review-v1/README.md)
passes at `3b2e3380…2cb9`, contract `a460d5cb…a92f`, including6+8 exact
reversals, unchanged full HMAC fields and the complete typed collector. This is
source-only evidence. The separate [isolated native implementation](tests/node-compat/foundation-crypto/ownership-gc-native-candidate-v1/README.md),
index `2fbc01ad…05a`, contains staged build/freeze/export/bootstrap templates.
Its [independent source review](tests/node-compat/foundation-crypto/independent-ownership-gc-native-source-review-v1/README.md)
is **HOLD**, index `f0d12621…acdc`: the freezer reads `authority` while the
guard/wrapper supplies `rootAuthority`. The source would raise `KeyError` after
read-only helpers and before publishing copies. All39 source members,2,843
physical files,14 ASTs,12+1 reversals and protected normal membership are checked;
no actual phase ran. The [thin native v2 correction](tests/node-compat/foundation-crypto/ownership-gc-native-candidate-v2/README.md), index `ed066504…6d05`, now passes [independent source review](tests/node-compat/foundation-crypto/independent-ownership-gc-native-v2-source-review-v1/README.md) at `1cc950dd…4e3a`. The body uses the actual `rootAuthority` descriptor, bound to both authenticated config and captured Root row. All13 context reads,30 members,2,883 physical files and6+12 exact source afterimages pass; the14 stored pure seam checks are authenticated without rerunning owner modules. Old source/HOLD remain unchanged. A reviewed external stage controller and actual isolated source stage are next.
The separate actual source stage is recorded below; no GC build/reconfiguration,
key/GC workload, new engine or GC pin exists. Actual native/freeze/bootstrap proofs, selected-Buffer component and
complete raw runtime collection remain outstanding.

The [new HTTP external controller](tests/node-compat/foundation-stream-consumers/http-host-controller-candidate-v1/controller.py)
is in source preparation. It authenticates the exact corrected source/config and
Root phase before launching a finite owned Node session, captures parent streams
and terminal status, and records observed owned descendants for bounded cleanup.
Its sealed source index is `5ccf3aa6…1217`. All25 benign checks pass across
normal, timeout and detached-descendant cleanup cases; raw0 streams/terminals are
retained. The [dormant GC stage caller](tests/node-compat/foundation-crypto/ownership-gc-stage-controller-candidate-v1/README.md),
index `8ff1af87…2cee`, reuses that actual monitor API with a600-second stage-only
phase and source/native/controller authentication. Independent review of both
controller sources found a blocking group-accounting gap in the generic v1
monitor: an observed nonleader with an unobserved group leader, or a known PID
moving to a new group, could be omitted from final cleanup accounting. The tiny
stage caller's own seam has no blocker but remains transitively held. The
[formal combined controller HOLD](tests/node-compat/foundation-stream-consumers/independent-http-gc-controllers-source-review-v1/README.md)
is sealed at `23738f96…185c`; both genuine extracted-pure counterexamples and the
retained25 benign checks are verified without controller/host invocation. Both old
source seals remain unchanged. The generic v2 correction now accounts for every
stored/current group of known PIDs and explicitly refuses remaining observed
PIDs; unknown ownership is never signalled or accepted. Its35 checks and all
three benign sessions pass raw0. The [generic controller v2](tests/node-compat/foundation-stream-consumers/http-host-controller-candidate-v2/README.md)
is sealed at `71b7f8e5…0ddf` with seven reversible source edits; the [stage caller v2](tests/node-compat/foundation-crypto/ownership-gc-stage-controller-candidate-v2/README.md)
is sealed at `29d59208…700d` with three exact selection/context substitutions.
The [independent corrected-pair review](tests/node-compat/foundation-stream-consumers/independent-http-gc-controllers-v2-source-review-v1/README.md)
passes at `e3c0589e…8a83`, result `e00ee2b0…93f2`, authenticating54 paths,
7+3 exact reversals, eight extracted-pure models and the retained35 checks/three
benign sessions. These source preparations ran no actual host or native phase.

The new [GC source-stage authority](tests/node-compat/foundation-crypto/ownership-gc-v2-stage-root-authority.json)
(`3d77668a…e20b`) runs only the real isolated publisher. Its [actual result](tests/node-compat/foundation-crypto/ownership-gc-v2-stage-root-results.json)
finishes Root session49205/child44203 raw0 in3.251 operational seconds, no signals,
forced cleanup, timeout, errors or remaining observed PIDs. Direct journal
`c35513f8…28b8` reports the fresh v2 destination and1,311 copies; Root verifies
every copied hash/mode/distinct inode and detached54b/no alternates. The old plan's
v1 destination annotation remains explicitly historical DATA. The [independent actual stage review](tests/node-compat/foundation-crypto/independent-ownership-gc-v2-stage-review-v1/README.md)
passes at `dbf58c99…121a`, contract `0ff86b2d…3a0a`: all copies, native/tool sets,
Git context, process records and normal protections match. This runs no native
build/freezer/bootstrap or guest. The [dormant7200-second native build controller](tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1/README.md)
is sealed at `0afae87d…7f1b` (20 members), with899 source/data,77 pure and7 AST
checks. Its monitor differs by one deadline-ceiling edit; the actual build caller
authenticates source, native/source-stage proofs and a new phase before launch.
The [independent build-controller source review](tests/node-compat/foundation-crypto/independent-ownership-gc-build-controller-source-review-v1/README.md)
passes at `76504af1…6176`, contract `dee045ee…ed98`, checking the full20/79/six-family
closure, single ceiling edit,62 independent pure cases and7 ASTs without actions.
The separate [actual build authority](tests/node-compat/foundation-crypto/ownership-gc-v2-build-root-authority.json)
(`8c01977c…ae12`) now starts Root session58915/child49070 under the7200-second
external monitor. It permits only the isolated ordinary single-job Release-GC
compile/link, preserving original normal files and2GiB/800MiB disk guards. The
build [finishes raw0](tests/node-compat/foundation-crypto/ownership-gc-v2-build-root-results.json)
at Root58915/Python49070 and inner Bash49081, in508.732 external/505.746 inner
operational seconds. Engine `289df445…66c8` is10,004,458 bytes; metadata
`90c3f45e…04c8` is376,978 bytes. Source355/external3, Release-GC/OFF/no-OOM and
whole engine/log hashes match; no observed groups/PIDs remain. The
[independent BUILD-only review](tests/node-compat/foundation-crypto/independent-ownership-gc-v2-native-build-review-v1/README.md)
passes at `fc0c7e3c…c9a7`, contract `21f206bf…c9a0`, checking98,717 main facts,
10,986 input hashes, full108-step/log/source/compiler/library witnesses and normal
protections. Engine execution, runtime and frozen-artifact claims remain false.

The [freeze-controller source](tests/node-compat/foundation-crypto/ownership-gc-freeze-controller-candidate-v1/README.md)
is sealed at `502027c9…f218` and its [independent source review](tests/node-compat/foundation-crypto/independent-ownership-gc-freeze-controller-source-review-v1/README.md)
passes at `22bc75b8…82ad`:133 paths, eight families, five exact support functions,
six ASTs and nine independent pure phase cases;85 stored author checks are
authenticated only. New [freeze authority](tests/node-compat/foundation-crypto/ownership-gc-v2-freeze-root-authority.json)
`4299668a…1391` now starts Root34426/Python75163 under the2400-second monitor.
The [actual attempt fails](tests/node-compat/foundation-crypto/ownership-gc-v2-freeze-failure-root-results-v1.json)
Root34426/Python75163 raw1 after2.555 operational seconds, with clean owned-group
cleanup/no signals/forced cleanup/timeouts/errors and zero stdout. The898-byte
stderr identifies **GC-HELPER-SELECTION-M2**: `guard.load_common` chooses the first
of11 `artifact_common.py` suffix matches, a classic-stream helper hash, then
checks the actual crypto helper against it. Both files retain their expected
bytes; source/build proofs remain distinct valid evidence. Root's native source
reviews missed the selector ambiguity. No common/body module import, Ninja,
metadata-admission helper, freeze directory or receipt occurs. Outer provenance
hashing reads the engine, but never executes it. The failed attempt and all old
seals are preserved. The [independent failure-only audit](tests/node-compat/foundation-crypto/independent-ownership-gc-v2-freeze-failure-review-v1/README.md)
passes at `66bc7c6c…a317`, contract `cb92d331…3027`, verifying9,715 physical files,
the exact four stack frames/11 candidate rows and full normal/engine preservation.
This is a failure review, with `artifactVerifiedPassed:false`. The pending artifact
draft remains unsealed with no verdict. A thin explicit helper-selection amendment
with separate native/amendment provenance is prepared; no retry, new native
build, frozen-artifact proof or pin is authorized by that failure record.

The [helper-selection amendment](tests/node-compat/foundation-crypto/ownership-gc-freezer-helper-amendment-v1/README.md)
is sealed at `09ce7fb2…ee79` (20 members/3,017 inputs), with59 pure/data and5 AST
checks. Its [independent source review](tests/node-compat/foundation-crypto/independent-ownership-gc-freezer-helper-source-review-v1/README.md)
passes at `3708bb2a…b5a2`, contract `9dcb4f08…fabc`:3,039 paths/13 families,
six body/seven controller reversals and16 exact-selector cases. The exact full
crypto path is unique and order independent. The genuine native frame/index,
common roots and validator observations remain unchanged; the new amendment's
authority/index/capsules are explicit and separate. No native rebuild occurs.
New [native freeze authority](tests/node-compat/foundation-crypto/ownership-gc-v2-freeze-helper-v1-native-root-authority.json)
`c6a0decf…e423` and [amendment authority](tests/node-compat/foundation-crypto/ownership-gc-v2-freeze-helper-v1-amendment-root-authority.json)
`2fad3e15…339b` start fresh Root session70920 in an isolated, bytecode-disabled
Python process. The [actual corrected freeze](tests/node-compat/foundation-crypto/ownership-gc-v2-freeze-helper-v1-root-results.json)
finishes Root70920/Python79716 raw0 in17.119 operational seconds. Receipt
`7567f60f…f669` binds1,462 copies/1,463 actual files; Root rehashes every frozen
copy and original, distinct inodes and exact membership. Whole stdout decodes to
the written receipt. The correction record `40e6834b…7488` distinguishes native
ed066 from helper09ce and records the actual crypto helper fff7; engine289/meta90
remain unchanged. No observed groups/PIDs or controller failures remain. The
[independent full native-artifact review](tests/node-compat/foundation-crypto/independent-ownership-gc-native-artifact-results-review-v1/README.md)
passes at `64ec1c1e…1737`, contract `f2b30613…9144`: the ordered1,462-copy plan,
1,459 original references, exact1,463 membership,140 capsules, whole correction,
source/compiler/library witnesses, normal protections and both raw completions
are checked. Backend/runtimeValidation/erasure claims remain false/NULL; the old
draft is preserved because the failure audit pins it. No engine has executed.

Corrected [pin export/bootstrap source tooling](tests/node-compat/foundation-crypto/ownership-gc-pin-tooling-candidate-v1/README.md)
is sealed at `08ea9379…9c56` (26 members/3,058 inputs). Its [independent source review](tests/node-compat/foundation-crypto/independent-ownership-gc-pin-tooling-source-review-v1/README.md)
passes at `9350f534…5a35`, with3,085 physical files,14 families, exact selector/
export-body and5+5 bootstrap reversals, six ASTs/twelve pure phase cases and a
pinned Node syntax-only raw0 check. Separate native/tooling roots stay explicit.
New [export authority](tests/node-compat/foundation-crypto/ownership-gc-v2-pin-export-v1-native-root-authority.json)
`4e575f48…f546` and its separate tooling authority run the [actual export](tests/node-compat/foundation-crypto/ownership-gc-v2-pin-export-v1-root-results.json)
Root15372/Python85052 raw0 in15.435 operational seconds. Candidate `52ae49ff…ace9`
is478,956 bytes, remains UNREVIEWED with only gc-off/non-GC NULLs, and matches all
1,462 frozen-file rows. Whole raw stdout equals its JSON; old three build-output
files remain exact and only this one file is added. The [independent export data review](tests/node-compat/foundation-crypto/independent-ownership-gc-pin-export-results-review-v1/README.md)
passes at `bda61549…3229`, contract `eb8e5ee7…ff8c`, reconstructing the entire
candidate and raw stdout, all1,462 frozen rows, provenance and preserved files.
The candidate remains UNREVIEWED and pins remain unadopted. NEW GC-only reviewed
pins and actual read-only bootstrap remain pending. Old native
export/bootstrap entries stay closed; only the reviewed corrected tooling can run.

New [GC-only validation pins](tests/node-compat/foundation-crypto/reviewed-ownership-gc-v2-native-pins-v1.json)
(`e2923fa2…8111`) and their [Root pin review](tests/node-compat/foundation-crypto/reviewed-ownership-gc-v2-native-pin-root-review-v1.json)
(`4f881996…e4f1`) preserve every candidate artifact field and all1,462 frozen rows.
Only the pin state/review flag and four independent artifact-proof fields change;
all three non-GC variants remain NULL. The genuine existing pure selector passes;
an independent finite data check passes69 predicates. Separate native/tooling
bootstrap authorities bind new config `d4e0f991…1107`. The
[actual Python bootstrap](tests/node-compat/foundation-crypto/ownership-gc-v2-bootstrap-v1-cli-root-results.json)
finishes Root35664/Python88872 raw0 in17.311 operational seconds. The genuine
[JS API observation](tests/node-compat/foundation-crypto/ownership-gc-v2-bootstrap-v1-root-results.json)
then finishes Root77845/Node89115 raw0 in54.567 operational seconds. Its initial
call/internal recheck/explicit recheck run three read-only bootstrap bodies,
separate from the one CLI call. The entire frames compare equal; Root also checks
the full metadata against actual frozen sidecar90c3 and all11 manifest values
against actual frozen files. Both external monitors report all observed groups
and PIDs gone with no signals/errors/timeouts/forced cleanup. Full CLI stdout
(`9520bf31…3f9a`,818,188 bytes) and API frame (`675b24c7…62a2`,917,166 bytes)
are retained. The independent actual review is recorded next. This
validates read-only tooling; no engine/component/guest/key/GC workload or runtime
acceptance follows, and the accepted foundations-v13 source remains unchanged.

The [independent actual bootstrap review](tests/node-compat/foundation-crypto/independent-ownership-gc-bootstrap-results-review-v1/README.md)
now passes at `00fad522…a9c8`, result `1dac553c…1b64`. It freshly verifies11,354
physical inputs, both complete25-field retained frames, all11 manifests,1,462
frozen rows, six pin changes, normal protections and process cleanup. Four
completed read-only bodies/four metadata-Node children are source/process coupled;
internal raw body returns and individual metadata-helper terminals are not
separately retained. No reviewer engine or workload action occurs.

The [GC component source](tests/node-compat/foundation-crypto/ownership-gc-component-candidate-v1/README.md)
seals76 members/8,171 inputs at `6f0faf4b…f0db`, with61 pure/67 source checks.
Its [independent construction-source review](tests/node-compat/foundation-crypto/independent-ownership-gc-component-source-review-v1/README.md)
passes at `fbf165fa…a2c9`:69,741 read/hash/source checks,8,248 paths,4,934 packaging
roles,22 links and exact parent/worker derivations. It requires the actual GC-only
pins/bootstrap proofs, genuine native Buffer bundling and unchanged four-function
WIT. Separate [Root construction authority](tests/node-compat/foundation-crypto/ownership-gc-component-v1-root-authority.json)
now starts Root96509/Node92352, allowing component initialization and construction
only. Ordinary/key/GC-pressure exports and runtime acceptance remain closed.

The [actual GC component construction](tests/node-compat/foundation-crypto/ownership-gc-component-v1-root-results.json)
finishes Root96509/Node92352 raw0 in130.359 operational seconds. Worker93037
finishes status0 in11.942 seconds; all observed groups/PIDs are gone with no
signals/errors/timeouts/forced cleanup. Component `52d99f4e…e5f1` is13,118,152
bytes; core `ac5d7a51…9fef` is13,117,532 bytes. Root verifies25 indexed/27 actual
files, retained imports[], four ordinary WIT functions and the empty non-WIT
Jco `_util` helper. The full16,574-byte bundle retains only native `node:buffer`
and one exact physical guest fixture, with11 selected manifests. Generated ESM
has not been imported and no ordinary/key/GC-pressure export has run.
Independent full artifact/ABI/loader-source review is recorded next. A Root data-reader
field mistake (`rawExitCode` versus the durable worker's actual `status`) is
recorded and corrected; it caused no repeated construction or artifact change.

The [independent GC component artifact review](tests/node-compat/foundation-crypto/independent-ownership-gc-component-results-review-v1/README.md)
now passes at `f812eeec…a195`, result `cdca4ae9…4774`, contract `4b2b6897…4a61`.
It freshly checks16,593 physical inputs, all25 indexed/27 actual outputs,104 worker
critical rows,76 source members,8,171 preparation inputs,4,934 packaging files and
22 links. A new metadata-only WIT decode finishes raw0 and exactly matches191
bytes/four functions/imports[]. The nested core is byte-identical to the captured
Jco core, with no imports or start section. Loading-source grammar evidence is
bound by full byte equality with the previously reviewed glue, not a new JS
parse or generated import. The exact12-artifact map is shared by result/contract.
Initialization/Wizer execution is explicit; no ordinary/key/GC-pressure export
has run. New GC runtime source and its separate source/action gates remain open.

The [scheduler integration source](tests/node-compat/foundation-scheduler/resource-integration-candidate-v1/README.md)
now seals33 members at `20e6bab4…c414`. Preparation reports5,401 source/pure checks
over822 inputs,342 expected-source cases and four old-receipt negatives. The
[independent integration source review](tests/node-compat/foundation-scheduler/independent-resource-integration-source-review-v1/README.md)
passes at `360732de…dd5d`:5,290 read/data/pure/grammar checks over858 unique inputs,
all33 members, exact342/340+2/external3 ancestry,467 staging rows and reversible
helper/recipe derivations. Five pinned-Node syntax-only checks pass with empty
streams; no WIT parser, helper, stage, compiler, component or guest runs. The new
source can proceed to a separate Root stage phase. Actual native/freeze/ABI/clock
admission and hard-NULL runtime activation remain open, together with global
fallible enqueue, argv-failure testing, reset/reuse and ALS.

New [scheduler stage authority](tests/node-compat/foundation-scheduler/resource-integration-stage-v1-root-authority.json)
starts a separate accepted342 reconstruction. The [actual stage](tests/node-compat/foundation-scheduler/resource-integration-stage-v1-root-results.json)
finishes Root52275/Python91561 raw0 in8.066 operational seconds, with clean observed
group/PID cleanup and no signals/errors/timeout/forced cleanup. Journal
`266eef63…5e14` retains501 copies: Root verifies every copy/original hash, mode and
distinct inode, all342 final native hashes, detached54b/no alternates and no Git
object inode intersection. Whole raw stdout equals the journal. The separate
source checkout is staged; production remains unchanged. Independent actual
stage review, normal native build/freezer and later GC/runtime gates remain open.

The [independent actual scheduler-stage review](tests/node-compat/foundation-scheduler/independent-resource-integration-stage-review-v1/README.md)
now passes at `f28a190d…5eca`, result `58d6265f…1c40`, checking1,908 physical inputs,
all501 copies,342 final sources and process/Git-context evidence. The three
accepted embedding files are ancestry data; **zero embedding files were copied
by this stage**. Fresh actual build capture must prove its own external3 inputs.
The original UNREVIEWED journal is preserved. A normal-OFF build-controller source
candidate and GC runtime source are being prepared; no native build or exported
GC workload has started for these new phases.

The [scheduler normal-OFF build-controller source](tests/node-compat/foundation-scheduler/resource-build-controller-candidate-v1/README.md)
seals26 members at `f7510454…2bd8`, with4,301 source/pure checks and six AST parses.
Its [independent source review](tests/node-compat/foundation-scheduler/independent-resource-build-controller-source-review-v1/README.md)
passes at `de4a0b43…d18e`:8,438 source/data/pure checks,1,085 inputs, exact19
lifecycle segments, byte-identical7200-second monitor,19 actual extracted Root
predicate cases and eight stage cases. The new local lifecycle module omits the
donor's unrelated admission-pins read and operational main; no globals are
rebound. Initial author syntax whitespace failure is preserved from preparation.
New [normal-OFF Root build authority](tests/node-compat/foundation-scheduler/resource-normal-off-build-v1-root-authority.json)
`9b0ad35a…7907` and config `db981219…a555` now launch Root12069/Python96368.
Only single-job Release342/OFF/no-OOM compilation is selected, with2GiB start and
800MiB stop guards. GC reconfiguration, freezer, engine/guest execution and
runtime acceptance remain closed; a normal freeze/review must precede later GC.

The [actual scheduler normal-OFF build](tests/node-compat/foundation-scheduler/resource-normal-off-build-v1-root-results.json)
finishes Root12069/Python96368 and Bash96374 raw0 in486.794 external/485.340 inner
operational seconds. All714 observed processes and their groups are gone, without
signals/errors/timeouts/forced cleanup. Engine `fec7a900…a704` is9,976,561 bytes;
metadata `51fbc0a0…e80e` is303,587 bytes. Root's actual metadata classifier passes
342/external3/Release/OFF/no-OOM and verifies the generated timer namespace once.
Ninja reports107/107 completion. This actual342 baseline selects nine module
manifests, not355's eleven. The compile DB has67 entries:61 policy builtins/runtime
C++ files, five other configured-source files and one generated `null.cpp`. The
one embedding command is captured separately, not in that DB. The log is not a
full verbose compiler/link transcript; independent
review must qualify command execution using the captured DB/Ninja/library and
clean build evidence. The stdout envelope's complete `result` equals the on-disk
result; a Root data-reader envelope mistake is preserved without rerunning the
build. BUILD-only review is underway. Normal freeze and independent proof must
still precede any GC reconfiguration or timer runtime gate.

The [independent normal-OFF BUILD-only review](tests/node-compat/foundation-scheduler/independent-resource-normal-off-build-review-v1/README.md)
now passes at `bf48593b…f369`, result `dcf60f1e…e432`, contract `e21c5607…80c9`.
It freshly verifies7,500 physical inputs, all501 staged protections,342 native/
external3 identities, nine genuine manifests, SDK/LLVM/SM/archive/header, all4,650
OpenSSL source rows, locked Rust and static-link inputs, and separate embedding
evidence. The67-row DB is correctly61 policy C++, five other configured files
and one generated `null.cpp`, with no embedding row. Retained progress has107
lines,31 twice/no literal32/final107; the review qualifies execution through the
actual DB/rules/objects and successful parent rather than inventing individual
compiler/link terminals. All714 observed identities/77 groups are gone. Native
runtime validation and normal freeze remain NULL; no GC reconfiguration or
engine/bootstrap/timer execution is admitted by this review.

The [GC runtime source](tests/node-compat/foundation-crypto/ownership-gc-runtime-candidate-v1/README.md)
now seals49 members/11,095 inputs at `c298e623…a43a`, with73 extracted data/loader,
six capture-seam,42 source/closure and eight grammar checks. It binds the actual
`f812eeec` artifact/contract as DATA, preserves all23 complete public strings and
20 HMAC records across three fresh retained/fresh/wrapper sessions, and keeps new
Root activation NULL. Expected public pressure counters total48/16/16=80; only
the wrapper returns16 full pressure-byte records. Ordinary64 requests remain
counter/source-assertion observations. Independent source review is finishing;
no generated import or key/GC operation has run for this runtime phase.

The [GC runtime v1 source review](tests/node-compat/foundation-crypto/independent-ownership-gc-runtime-source-review-v1/README.md)
passes at `05e9810c…3cf6`, with57,188 checks/11,163 paths and exact39 derivation
edits plus two unchanged loader/oracle copies. Its first
[actual attempt fails in preflight](tests/node-compat/foundation-crypto/ownership-gc-runtime-v1-preflight-failure-root-results.json)
on **GC-RUNTIME-CANONICAL-INPUTS-M1**: Node21439 raw1 after0.600 operational
seconds, before output creation/oracle/worker/generated import or guest calls.
The strict descriptor correctly rejects17 relative artifact-peer member paths
in the11,095-row input freeze; the other11,078 rows are absolute. Preparation
hashed those rows relative to the original checkout, and source review missed
the actual runtime descriptor boundary. All observed groups/PIDs are gone with
no signals/errors/timeouts/forced cleanup, stdout is empty, and1194 bytes of
stderr identify `guard.mjs:34`. The
[independent failure review](tests/node-compat/foundation-crypto/independent-ownership-gc-runtime-v1-preflight-failure-review-v1/README.md)
seals at `ec5b8ddc…be9e`, explicitly preserving the earlier review miss. The v1
source, peer and failed authority remain immutable and closed to further runtime
activation. R is preparing a thin v2 with17 explicit authenticated original
absolute paths, full real file-reader regression and new source/output/Root
identities. It will not normalize arbitrary runtime paths or project metadata.
The unsealed stock-Wasmtime GC draft is held while this correction is completed.

The [thin GC runtime v2 source](tests/node-compat/foundation-crypto/ownership-gc-runtime-candidate-v2/README.md)
seals56 members/11,171 inputs at `5abe5ed8…0959`, results `e33729ad…05df`. Its
17 active row substitutions explicitly name authenticated original-repository
`f812eeec` members; the other11,078 base rows stay unchanged. New source/output/
Root identities preserve every v1/failure record. The real read-boundary
regression passes all11,171 rows (11,170 regular reads/one streamed read), matching
872,756,583 declared/actual bytes, and rejects all17 original relative rows with
the genuine descriptor. It runs only authenticated file-read/hash utilities;
no preflight, bootstrap, oracle, generated import, guest or key/pressure operation.
Independent v2 source review is underway before a fresh Root retry. The stock-
Wasmtime source draft can now resume against the new v2 provenance; its actual
Jco result/contract/Root activation remain unissued.

The [independent GC runtime v2 source review](tests/node-compat/foundation-crypto/independent-ownership-gc-runtime-v2-source-review-v1/README.md)
passes at `94a2a267…7669`, result `c4c261be…42fb`:56,859 source/data checks,
11,228 paths, all56 source members and11,171 canonical input rows,17 explicit
original-path corrections, unchanged11,078 base rows/five runtime bodies and
genuine file-boundary evidence. New [v2 Root runtime authority](tests/node-compat/foundation-crypto/ownership-gc-runtime-v2-root-authority.json)
starts Root52246/Node25409 for the same three fresh retained/fresh/wrapper sessions.
The new controller has seven explicit reversible changes from the preserved v1
caller; it uses5abe/V2/source/output/Root identities and unchanged actual f812
artifact roles. No metadata/frame projection or runtime path normalization is
introduced. Actual v2 execution and independent result review are recorded next.

The [actual GC runtime v2](tests/node-compat/foundation-crypto/ownership-gc-runtime-v2-root-results.json)
finishes Root52246/Node25409 raw0 in83.029 operational seconds. Workers25459,
25602 and25760 each finish status0; all four observed groups are gone with no
signals/errors/timeouts/forced cleanup and empty stderr. All46 indexed/48 actual
files rehash. Root decodes23 entire public strings/20 records;45 complete
`SignatureHex` values equal the retained pinned-Node/RFC oracle. The whole
within-export wrapper equals the sealed complete schema2 expected record.
Pressure counters total48/16/16=80; all16 exposed wrapper pressure records contain
the complete64 bytes/encoded+decoded128 hex characters. The other64 requests have
counter/source-assertion evidence, without full byte records. Native collection
count, finalizer/free/wipe and isolated roots remain unobserved. No OOM, reset or
stock-Wasmtime run occurs, and no performance/reuse/production acceptance follows.
Root's initial data reader mistook other64-character hex buffers for signatures;
it is corrected to the actual signature fields without rerunning the workload.
The independent actual-result review is queued after the finite secret-failure
source cut is sealed; actual stock-host validation remains a later gate.

The [secret-failure ownership source cut](tests/node-compat/foundation-crypto/ownership-secret-failure-candidate-v1/README.md)
now seals35 members at `070f1c20…1958`, results `0135f7df…fb28`. Eleven reversible
edits change only three genuine355 files, preserving352 inputs: all15 BIGNUM
extractions acquire immediate owners, the OpenSSL point buffer is owned through
parameter conversion, and the allocation check precedes writes. Two genuine
SDK30/LLVM21 syntax-only calls finish raw0 with empty streams and1,104 dependency
paths. The complete355/VFS overlay and four actual configured headers are
captured. The390 source/model checks use synthetic failure scenarios; no real
allocation fault, crypto/guest/GC or new engine build ran. It remains UNAPPLIED
and requires independent source review/new native gates. A separate explicit
[history erratum](tests/node-compat/foundation-crypto/ownership-secret-failure-candidate-v1-history-erratum.json)
corrects an output-chunk ID mislabelled as a session; the sealed source is retained.
Numeric/length bounds, additional secret-copy policies and security-complete
claims remain outside this cut. R is independently reviewing this source.

The [stock-Wasmtime GC source](tests/node-compat/foundation-crypto/ownership-gc-wasmtime-candidate-v1/README.md)
now seals60 members/11,279 inputs at `c5d3ea49…ec35`, with65 pure/data,31 source/
closure and five final syntax checks plus genuine full file-reader regression.
It targets three fresh literal `validate()` calls, full decoded WAVE strings
equal to the actual Jco v2 wrapper, complete schema2/HMAC checks and48 exposed
pressure records across three calls. Actual Jco-result peer/contract and host
activation remain NULL; independent source review and real stock-host execution
are outstanding. Source preparation invoked no Wasmtime/guest/key/pressure call.

The [finite secret/bounds audit](tests/node-compat/foundation-crypto/ownership-secret-bounds-audit-v1/README.md)
seals at `ea74c480…0233`, findings `23291c93…2de7`. It checks14 configured/frozen
native pairs and nine actual OpenSSL3.0.17 API files. Concrete source findings
include `to_bytes_expand` writing through an unchecked `JS_malloc` result, five
BIGNUM extraction groups with partial-failure/CRT-fallback ownership gaps, and
`EC_POINT_point2buf` output missing cleanup on success and early returns. The
proposed first cut is immediate BIGNUM owners, an actual `OPENSSL_free` buffer
owner held through `to_param`, and an allocation check before writing. Numeric/
length bounds and additional secret-copy policies remain separate work. This is
source evidence, not an allocation-fault/runtime/security PASS; the current
20-byte RFC4231 HMAC fixture does not reach those paths. No source was patched.

Parallel Phase3.4 work now has an [unapplied timer/task ownership candidate](tests/node-compat/foundation-scheduler/resource-ownership-candidate-v1/README.md),
index `02e9779b…6f4c` (25 members). Two source afterimages/nine reversible edits
add strong traced timer ownership, idempotent ordinary-path retirement and rooted
task execution/cancellation. Actual pinned SDK frontend checks finish raw0/0 with
1,028 declared dependencies (two afterimages/1,026 headers) retained;12 pure
scenarios/89 checks pass. This is not applied or linked/runtime-tested. The
[independent source review](tests/node-compat/foundation-scheduler/independent-resource-ownership-source-review-v1/README.md)
passes at `aca99b1f…52fa`:25 members/1,075 preparation rows,1,087 lexical paths,
nine exact reversals, retained SDK evidence and ten ownership paths. New integration
and real-component gate source is in preparation. The existing void
global enqueue/std::vector failure seam, reset, request reuse/teardown, all-invalid
selection and native ALS propagation remain open; no public API is enabled.

The new [HTTP both-host authority](tests/node-compat/foundation-stream-consumers/http-both-hosts-v2-root-authority.json)
(`71f8978b…143c`) and separate component/controller phases start Root session72742,
Node child44688, under the reviewed2400-second external controller. It targets the
same64,098,281-byte `2ce7d990…5f33` component and three ordinary responses per host.
The [actual result](tests/node-compat/foundation-stream-consumers/http-both-hosts-v2-root-results.json)
finishes Root72742/Node44688 raw0 in172.534 operational seconds. All391 indexed/
393 actual files rehash. Root checks six full accepted200 bodies against their
recorded UTF8/JSON, both server raw0/graceful SIGINT-only exits and stopped curl7
with zero HTTP stdout. There are83 actual capture attempts: six accepted200,
76 readiness404 responses and one preheader failure, all explicitly retained;
Root checks every chunk sequence against its aggregate. No write failure occurs.
All observed owned groups/PIDs are gone, with no controller signal, forced cleanup,
timeout or error. The [independent actual-result review](tests/node-compat/foundation-stream-consumers/independent-http-both-hosts-v2-results-review-v1/README.md)
passes at `225df389…0659`, contract `765f98d6…bf09`: all83 captures/12 chunks/
793,272 body bytes, six whole bodies and2,172 source/oracle predicates are checked,
plus13,574 final input paths, both configurations and lifecycle joins. Same component
bytes and prior six standard0.2.10/type-only-clock provenance remain bound; that
earlier binary decode is authenticated, not rerun. Internal preflight frames and
the full inherited parent environment were not separately retained; source-coupled
and clean-final/fresh-hash qualifications remain explicit. This
does not establish request reuse/isolation, a wire-body adapter or acceptance.

Checkpoint checks: the existing manifest test passes again under pinned
Node22.14.0 (exact Buffer/child_process namespaces and19 malformed-manifest
rejections), and all942 local links in the three current-status documents resolve.
The bounded644-file hygiene scan found no credential patterns or copied build
caches. The staged whitespace check flags one final blank line in each of the
sealed GC native `export-body.py`/`freezer-body.py` and independent timing-v3
`read-source.py`; these bytes are preserved because their seals depend on them.
The historical `deps/patches/rand.patch` trailing-space line is also preserved.
Full native/component suites are not rerun for the commit; their previously
executed, bounded evidence remains linked below. The roadmap remains in progress.

This file tracks completed work, work in progress, and outstanding gates for the
portable StarlingMonkey Node compatibility profile. It is not a claim of complete
Node.js or Buffer support. The detailed [execution ledger](docs/node-compat/execution-status.md),
[API matrix](docs/node-compat/compatibility-matrix.md), and
[dependency-ordered roadmap](docs/node-compat/roadmap.md) contain the underlying
contracts and evidence. No overall completion percentage is assigned: remaining
phases have substantially different sizes and unresolved design decisions.

The [independent actual GC runtime v2 review](tests/node-compat/foundation-crypto/independent-ownership-gc-runtime-v2-results-review-v1/README.md)
passes at `35218a21…7828`, results `a03cb407…9ce9`, contract `0388578b…30a5`.
It checks16,839 physical inputs, all23 full strings/20 records,45 signatures/
sign-return copies and45 verification booleans (25 true/20 false), whole wrapper,
Node oracle, source/component/native/normal protection and four clean processes.
The exact coverage retains80 counters versus16 full wrapper pressure records;
no native collection/erasure/isolated-root/reuse claim follows. The indexed
contract binds actual index, oracle and raw wrapper for a separate stock-host run.

The [independent stock-Wasmtime source review](tests/node-compat/foundation-crypto/independent-ownership-gc-wasmtime-source-review-v1/README.md)
passes at `486ddaa9…556a`, with56,787 source/data checks over11,340 inputs and35
additional cases exercising the actual pure decoder, argv, full-record and
authority/coverage models. Complete retained Jco values are DATA in that review;
no host/guest action occurs. New [Root host authority](tests/node-compat/foundation-crypto/ownership-gc-wasmtime-v1-root-authority.json)
`88598b7c…c8d9` starts Root54793/Node29869. A prior controller entry stopped before
any phase/output creation on inherited `RUST_LOG`; the actual task removes only
that variable from its child environment, preserving user home variables.

The [actual stock-Wasmtime GC run](tests/node-compat/foundation-crypto/ownership-gc-wasmtime-v1-root-results.json)
finishes Root54793/Node29869 raw0 in42.140 operational seconds. CLI processes29944,
30018 and30124 finish status0; all four observed groups are gone without
signals/errors/timeouts/forced cleanup. All23 indexed/25 actual files rehash.
Three entire decoded strings/records are byte/value-identical to the actual Jco
GC wrapper, with12 inner records,27 complete signatures equal to the retained
Node oracle and48 complete64-byte pressure records. Source-reported attempts
are six key imports,33 signs and30 verifies. No oracle rerun, generated JS import,
OOM/reset or process/request reuse occurs. Native GC count, frees/wipes and
isolated roots remain unobserved. Independent actual host-result review is in
progress; operational duration does not establish startup/throughput performance.

The [secret-failure source v1 review](tests/node-compat/foundation-crypto/independent-ownership-secret-failure-source-review-v1/README.md)
seals **HOLD M1** at `dbcf5cfa…0672`: the new null result from `to_bytes_expand`
is unchecked by ECDSA's r/s conversion consumers before length use/result
allocation/copy. The17-call inventory has15 checked sites and two unchecked
sites. Both failures must report OOM and return before any later consumption.
The finite BN/point ownership and provenance checks pass, but syntax/model
success does not cover this caller-propagation gap. Original070f/erratum remain
unchanged. A thin v2 source correction is being prepared; nothing is applied to
production or admitted as a security-complete crypto implementation.

The [independent actual stock-Wasmtime GC review](tests/node-compat/foundation-crypto/independent-ownership-gc-wasmtime-results-review-v1/README.md)
passes at `52c435cd…f7ad`, results `f71967f1…cd40`, contract `4954e206…8893`.
It independently consumes every raw WAVE byte, including escaped-apostrophe error
text, and matches all three whole strings/typed records to Jco. Derived totals
are27 signatures/sign-return copies and27 verification booleans (15 true/12 false),
six imports/33 sign attempts/30 verify attempts and48 complete pressure records.
The review checks12,783 distinct hashes, all11,279 source rows,23 indexed/25
actual files, native/frozen/original/normal protections and four saved clean
lifetimes. It performs no CLI/helper/guest action or fresh WIT decode. Root's
outer tool exit is Root-observed; full inherited environment values are not
retained. The same limitations on native GC count/free/wipe/isolated roots and
reuse remain; no production or security-complete crypto acceptance follows.

The [thin secret-failure v2 source](tests/node-compat/foundation-crypto/ownership-secret-failure-candidate-v2/README.md)
seals at `26eddb87…ce54`, with two immediate ECDSA r/s guards,13 composed
reversible edits,48 abstract caller cases and one fresh changed-CPP SDK syntax
check. Key/header grammar is reused only by complete byte/dependency identity.
Its [independent source review](tests/node-compat/foundation-crypto/independent-ownership-secret-failure-v2-source-review-v1/README.md)
passes at `b8ca947b…dc3d`, result `ea2d5d9c…ce72`:39,056 assertions/5,446 files,
all17 consumer sites,355/3+352 source, ownership/order/derivation/compiler proofs
and the original HOLD/erratum are checked. M1 is resolved in source. It remains
UNAPPLIED, with native integration/build/runtime/fault gates open. Existing289
HMAC/GC passes are not transferred to these corrected, unbuilt bytes.

The [resource normal-OFF freezer source](tests/node-compat/foundation-scheduler/resource-freezer-candidate-v1/README.md)
seals31 members at `f88db73e…b072`, with25,591 source/pure checks/seven AST files.
Its [independent source review](tests/node-compat/foundation-scheduler/independent-resource-freezer-source-review-v1/README.md)
passes at `4724fa4a…348c`, with39,936 checks/7,548 inputs and17 extracted Root
predicate cases. The623-row base plan copies593,181,282 bytes,342 native/three
embedding/159 nonnative source rows and29 static archives. The7,500 original
build references remain explicitly verified references, not all physically copied.
Twelve genuine copy/command functions have explicit output arguments; no old
trace selector, classifier identity or global rebinding is used.

New [Root freeze authority](tests/node-compat/foundation-scheduler/resource-normal-off-freeze-v1-root-authority.json)
`39efd108…be5f` launches Root19779/Python33769. The
[actual normal freeze](tests/node-compat/foundation-scheduler/resource-normal-off-freeze-v1-root-results.json)
finishes raw0 in16.892 operational seconds, with clean observed-group cleanup and
empty stderr. Receipt `b96f801d…8d86` binds666 copies/663 original references/667
actual files. Root rehashes every copy/original, private modes, distinct inodes
and exact membership. Enginefec7/meta51fb raw bytes stay unchanged. Fresh
post-build Ninja command listing finishes0 and equals the separately captured
embedding command; it executes no compiler or engine. The frozen-only verifier
passes without original-work reexecution. Independent full frozen-artifact review
is underway; new pin export/bootstrap and later GC/runtime gates remain closed.

The [independent resource normal frozen-artifact review](tests/node-compat/foundation-scheduler/independent-resource-normal-off-frozen-artifact-review-v1/README.md)
passes at `80b7174e…1794`, results `285934e5…fe92`, contract `38392252…da71`.
It checks140,844 data assertions/8,227 files, all666 copies/663 originals/667 files,
the623-base/dynamic plan union,7,500 verified references,29 archives, raw metadata,
source/flags/DB/cache/SDK and fresh post-build Ninja evidence. No helper, verifier,
Ninja, compiler, engine or runtime action is performed by the reviewer. Pins,
bootstrap, GC reconfiguration and timer execution remain separate later phases.

Root starts the first [codec calibration pilot](tests/node-compat/foundation-zlib/cost-pilot-v3-root-authority.json)
under session62440/Node35821 using unchanged source `c2ce5f08…64e9`, selected
calibration decision `3cf4eb74…546e`, actual prepared plan `c914e3a0…383b` and
source/plan independent reviews. All three agents confirm terminal tools and a
stable source-work hold before the [quiet window](tests/node-compat/foundation-zlib/cost-pilot-v3-quiet-window.json)
is issued. The phase has a preselected90-minute global budget, two-hour window
and7200-second external monitor. It must complete all60 comparison/case pairs,
using original geometric caps and both arms at50ms, with three warmups/one sample
per candidate and six separate N1 controls per fresh worker. No skipped case,
clipping, control subtraction, timing promotion or performance conclusion is
allowed. Unrelated desktop/system activity is not controlled and remains a
measurement limitation. The attempt ends raw1 after256.524 operational seconds:
first native-on case0/N1 worker37184 exits status1 in227ms with empty streams.
The parent rejects that terminal; no calibration origin or pair completes and
no matched-N plan is produced. Both observed groups are gone without timeout,
signals or forced cleanup. The [Root failure checkpoint](tests/node-compat/foundation-zlib/cost-pilot-v3-failure-root-checkpoint-v1/README.md)
preserves all12 small raw external/partial-output files and closes the coordinated
window. Worker startup cause and independent failure review remain outstanding;
no retry or timing follows. Resource pin-tooling is planning-only with no files,
and secret integration remains unsealed. Agents stay stopped for the Git checkpoint.

## Current work at a glance

| Work | Status | Next required step |
| --- | --- | --- |
| Architecture audit, API matrix, roadmap, Buffer and explicit-stub baseline | Delivered; implementations and templates are distinguished below. | Keep the bounded compatibility contract and known deviations explicit. |
| Accepted production checkpoint | Bounded foundations-v13 classic streams. | Continue experimental355 consumers and the remaining roadmap gates. |
| Corrected classic streams | Full 20-workload/14-boundary gate passes all 105 observations; fresh replay, follow-on and HTTP gates pass. | Accepted in v13; preserve bounded contracts and continue remaining roadmap phases. |
| Corrected HTTP component | Both hosts, combined audit and independent final review pass; included in bounded v13. | Preserve the one-request-per-instance limitation; test new experimental engines separately. |
| Performance comparison | All168 timing workers plus18 corrected RSS workers/126 typed returns pass independent review. | Preserve the separate measurement scopes and failed RSS v1. Same-engine peak RSS ratios cross1; no universal or guest-heap benefit. |
| Codec cost tooling | Fresh source copy and55-call Node oracle pass independent review; Root input capsule is complete. All three source bundles finish raw0 and per-arm source proofs pass. The WIT/glue corrections pass review. All three v3 component builds finish raw0 with imports[]/seven-function ABI; per-arm artifact reviews pass. | V3 retention, full untimed correctness, stock Wasmtime string transport, control-v2 results and the read-only90-row plan pass independent review. Timing v1/v2 holds stay preserved; v3 source review passes. The first authorized v3 pilot fails on its first worker status1; failure evidence is retained and its window is closed. Diagnose/review the failure before a fresh authorized retry and timing. No performance conclusion follows. |
| Crypto key ownership | Normal and GC native/component/Jco/stock-Wasmtime bounded validations pass independent review. GC runtime v1 preflight failure and corrected v2 evidence are preserved. | Corrected three-file secret-failure source passes review but remains unapplied/unbuilt. Complete native integration and algorithm/bounds/secret-copy gates, then Node Hash/Hmac/KeyObject APIs; no erasure, isolated-root, reuse or complete crypto claim. |
| Native zlib extension | Three native variants and bounded normal/GC/control component results pass independent review;22 Node error-case differences are recorded. | Complete matched cost, Node-deviation contract and new-engine host/release gates; operational admission remains closed. |
| Stream consumers | Four native355 variants and bounded normal/GC/control components pass review. Context/data-closure failures remain preserved. The corrected v3 family and admission checks pass review; its entire eight-stage release retry now finishes raw0. | The full eight-stage release and all five follow-ons pass independent review, with false getter parity and raw-output limits retained. New both-host HTTP execution and independent actual-result review pass with six accepted responses and77 separate readiness attempts; later cost/adoption/acceptance gates remain. Blob-dependent APIs remain refusals. |
| Corrected classic checkpoint | Accepted in bounded foundations-v13 after independent preservation and post-promotion verification. | Preserve its limits; continue consumer355 runtime and later phases. |

The detailed evidence below also retains failed attempts. A source check, syntax
check, packaged component, runtime test and accepted checkpoint are separate
completion states.

The [timing-input candidate](tests/node-compat/foundation-classic-streams/production-adoption-v1/composed-timing-phase-candidate-v1.UNREVIEWED.json) now names the exact composed correctness, full20+14, replay/follow-on and HTTP reports. Its four Root prerequisite reviews are recorded, and Root pure/syntax checks pass. The historical candidate remains unapproved (`timingAllowed:false`). A separate [Root-issued phase](tests/node-compat/foundation-classic-streams/production-adoption-v1/reviewed-composed-timing-phase-v1.json) and [quiet-window receipt](tests/node-compat/foundation-classic-streams/production-adoption-v1/composed-timing-window-root-review-v1.json) now authorize the unchanged protocol. The real read-only preflight finishes raw0; measurement finishes at Root-observed raw0 with all42 calibration/126 timed workers and final source audit complete. The [Root result](tests/node-compat/foundation-classic-streams/production-adoption-v1/common-byte-composed-timing-root-results-v1.json), [integrity review](tests/node-compat/foundation-classic-streams/independent-composed-timing-integrity-review-v1/README.md) and [numerical report](docs/node-compat/classic-stream-measurement-v1/README.md) pass. Registered binding saves7.85% component bytes but has no consistent same-engine warm-speed advantage; the stock-provider comparison also retains higher RSS counterexamples. Raw per-timing-call checksum strings were not saved: checks are authenticated-code/terminal supported, separate from full308-observation correctness. The coordinated quiet window has ended. The separate18-worker process RSS supplement now passes independent review, excluding full proof reports from workers; no guest-heap claim follows.

The [corrected zlib harness](tests/node-compat/foundation-zlib/validation-source-activation-v5-root-results.json) now passes [generated-family review](tests/node-compat/foundation-zlib/independent-component-validation-v8-family-review-v1/README.md). [Normal validation-v2](tests/node-compat/foundation-zlib/normal-codec-validation-v2-root-results.json) finishes raw0 with283 bounded-profile records across61 cases. [GC validation-v1](tests/node-compat/foundation-zlib/gc-codec-validation-v1-root-results.json) also finishes raw0 with three codec cases and combined-owner ordinary-GC checks under Jco/fresh Wasmtime. Both import nothing. [Independent normal](tests/node-compat/foundation-zlib/independent-normal-codec-validation-v2-results-review-v1/README.md) and [GC](tests/node-compat/foundation-zlib/independent-gc-codec-validation-results-review-v1/README.md) reviews pass. The [combined Root receipt](tests/node-compat/foundation-zlib/reviewed-codec-validation-results-v1.json) retains22 error-case differences and source-coupled VERNUM4880 versus Node4865; no complete parity or temporary-root-isolation claim follows. The [first fixture failure](tests/node-compat/foundation-zlib/normal-codec-validation-attempt1-fixture-failure-root-results.json) remains preserved; its three unsupported Array inputs were changed to supported Uint8Array inputs without expanding Buffer.

The [disabled-component run](tests/node-compat/foundation-zlib/disabled-selection-validation-root-results-v1.json) and [independent result review](tests/node-compat/foundation-zlib/independent-disabled-selection-results-review-v1/README.md) pass: eight bundler denials, five complete Buffer/stub observations, zero imports,50 completion files and one output link. Generic direct-import rejection does not uniquely prove its cause; codec/backend proof, operational admission and request reuse are not inferred. A new [source-based codec cost proposal](docs/node-compat/zlib-cost-comparison-proposal.md) identifies installed fflate0.8.3 as a possible browser-only guest comparand. Pinned Jco zlib uses a prohibited custom host service, so it is not a portable guest baseline. Five local dependency/source files are pinned. A [concrete source-only cost proposal](tests/node-compat/foundation-zlib/cost-comparison-candidate-v1/README.md), index `e29c596d…47ef8`, now seals83 files/401 source inputs and30 planned cases. Its browser-entry/provider/fixture/control templates and fresh350 selector snapshots leave pair/packaging/runtime/correctness authority null. [Independent source review](tests/node-compat/foundation-zlib/independent-zlib-cost-comparison-source-review-v1/README.md), index `661f8488…dfe29`, passes all83 files/401 inputs, five independently reconstructed fixture hashes and30 case rows. The fresh packaging sealer, context-aware350 diagnostic gate, actual oracles/ABI, full guest/worker/collector and pair/action authority remain unimplemented or null. Their successor tooling and independent guest/oracle sources are being implemented as source only. The draft now contains native-pair/action guards, a real Jco finite resolver and exclusive publisher; context/collector/action integration remains in progress. Root separately [captures and checks the exact guest draft](tests/node-compat/foundation-zlib/cost-guest-draft-pure-root-results-v1.json):99 structural/staging/base64/control checks finish raw0 with zero provider calls. The snapshot is retained under `/tmp/starling-node-compat/codec-cost-guest-draft-pure-root-v1`; this does not verify compressed streams or transfer to changed final source. The author adds typed host return/throw retention and seals [guest/oracle v1](tests/node-compat/foundation-zlib/cost-guest-oracle-candidate-v1/README.md), index `473c9979…5a046` (58 files/160 references). [Independent review](tests/node-compat/foundation-zlib/independent-cost-guest-oracle-source-review-v1/README.md), index `662bf8a5…bbe47`, holds it on COST-GUEST-M1:three exact extracted-predicate counterexamples show prior-output corruption can evade its old ownership checks, despite111 pure/25 source/16 parse checks passing. No real codec defect is observed. The [v2 successor](tests/node-compat/foundation-zlib/cost-guest-oracle-candidate-v2/README.md), index `ebe8fa90…a8eae8` (38 files/199 references), adds an immutable full prior-output baseline check after the next call and restoration. [Independent v2 source review](tests/node-compat/foundation-zlib/independent-cost-guest-oracle-v2-source-review-v1/README.md), index `259a7a31…636ed`, passes116 pure/32 source/17 parse checks and demonstrates all three old counterexamples rejected. Corpus/options/7-export ABI/timed batch remain unchanged; all positive action/oracle/component/correctness/timing slots remain null. An [explicit source protocol amendment](tests/node-compat/foundation-zlib/cost-source-protocol-amendment-root-decision-v2.json) adds bounded ordinary scalar stage/validate exports so other providers actual streams can reach guest decoders on the same component. The validation wrapper makes the explicit setup/stage/adjacent-observe sequence available to the stock single-invoke CLI; timing never uses it. This is seven proposed exports with actual ABI/CLI proof still required; v1 remains historical. New source/bundle bounds are32MiB UTF8 bytes each, distinct from1MiB codec input,16MiB codec output and2MiB UTF16 wire caps. Root observes current ARG_MAX1,048,576B; actual CLI argument/environment feasibility must be proved on real streams, with no truncation or skipped cases. The amendment fixes finite control IDs and six N1 control calls per primary worker, with no subtraction or extra control sample arms; no fflate codec, bundle, component or benchmark has run.

The [bounded strategy decision](tests/node-compat/foundation-classic-streams/production-adoption-v1/classic-implementation-strategy-root-decision-v2.json) retains the audited JavaScript classic state machine and selects native module registration to avoid duplicate bundled code where admitted. The measurements do not justify a C++ state-machine port or a universal CPU/memory advantage. The [small-worker process RSS proposal](tests/node-compat/foundation-classic-streams/measurement-memory-probe-candidate-v1/README.md) is sealed at index `41a6f1b9…e6271`:20 files,10,295 authenticated inputs,35 pure checks and four syntax checks. Its18 planned fresh workers exclude full proof reports, retain all seven public scalar returns before assertions, and measure small then large on one instance. The [independent source review](tests/node-compat/foundation-classic-streams/independent-memory-probe-source-review-v1/README.md), index `daad43d3…a108b`, passes. A separate [Root authority](tests/node-compat/foundation-classic-streams/production-adoption-v1/reviewed-process-rss-supplement-v1.json) and [source review](tests/node-compat/foundation-classic-streams/production-adoption-v1/process-rss-supplement-source-root-review-v1.json) authorize only this supplement. The [first actual attempt](tests/node-compat/foundation-classic-streams/production-adoption-v1/process-rss-supplement-v1-preworker-failure-root-results.json), Root session26865/PID6839, exits1 after14.128 operational seconds before any worker launches. The existing `setup` export returns signed32 numbers (`151852933` and `-1502831163` for the selected cases); the probe incorrectly required strings in its descriptor and comparison paths. Source reviews missed this type mismatch. The partial output contains only a self-manifest and empty worker directory, with no result, completion or RSS observation. All source/review/authority bytes and failed logs are preserved. The [source-only v2 successor](tests/node-compat/foundation-classic-streams/measurement-memory-probe-candidate-v2/README.md), index `6b0b82df…82def0`, now passes53 pure checks against actual WIT, declarations and Node oracles; its parent shares the tested descriptor builder and worker/parent comparisons share the strict typed guard. Root independently verifies all22 indexed files and repeats those53 checks at raw0. The [independent v2 source review](tests/node-compat/foundation-classic-streams/independent-memory-probe-v2-source-review-v1/README.md), index `73fa279b…ca6e`, passes. A separate [v2 Root source review](tests/node-compat/foundation-classic-streams/production-adoption-v1/process-rss-supplement-v2-source-root-review.json) and [v2 authority](tests/node-compat/foundation-classic-streams/production-adoption-v1/reviewed-process-rss-supplement-v2.json) authorize the corrected source only. The [actual v2 run](tests/node-compat/foundation-classic-streams/production-adoption-v1/process-rss-supplement-v2-root-results.json), parent11856/Root session17254, finishes raw0 in98.196 operational seconds. All18 unique fresh workers exit0 with owned-group cleanup; all126 raw returns (36 numbers/90 JSON strings),599 output files and final10,348-input source audit are retained. [Independent result/numerical review](tests/node-compat/foundation-classic-streams/independent-process-rss-supplement-v2-results-review-v1/README.md), index `14611521…2fe5`, passes, with312 summaries/396 paired ratios and full raw-value/type checks. The [v2 strategy decision](tests/node-compat/foundation-classic-streams/production-adoption-v1/classic-implementation-strategy-root-decision-v2.json) retains registered shared JavaScript streams: same-engine pre-final peak RSS paired ratios span0.9837–1.0018, and no controls are subtracted. The source template stays null and the coordinated window has ended. This is whole-process RSS/stage-wall evidence, with no guest-heap, cold physical startup or universal memory advantage claim. The checked-in null template stays unchanged; the first coordinated window ended after that failure.

The current [consumer355 producer v2](tests/node-compat/foundation-stream-consumers/native-integration-candidate-v2/README.md) passes [source review](tests/node-compat/foundation-stream-consumers/independent-native-integration-v2-source-review-v1/README.md) and [actual staging review](tests/node-compat/foundation-stream-consumers/independent-native-integration-v2-stage-review-v1/README.md):59 indexed files,3,420 preparation inputs and1,173 staged overlay files. Real SDK registration syntax ON/OFF also passes. The new module remains a bounded text/JSON proposal; arrayBuffer/blob/buffer are explicit refusals.

| Consumer355 variant | Actual build/freeze/read-only verification | Independent native review |
| --- | --- | --- |
| Normal ON, entropy OFF | [All raw0](tests/node-compat/foundation-stream-consumers/native-integration-v2-normal-off-root-results.json); engine10,002,283B;1,164 frozen copies. | [PASS](tests/node-compat/foundation-stream-consumers/independent-native-consumers-v2-normal-off-review-v1/README.md). |
| GC ON, entropy OFF | [All raw0](tests/node-compat/foundation-stream-consumers/native-integration-v2-gc-off-root-results.json); engine10,003,832B;1,164 frozen copies. | [PASS](tests/node-compat/foundation-stream-consumers/independent-native-consumers-v2-gc-off-review-v1/README.md). |
| Consumers OFF, zlib ON | [All raw0](tests/node-compat/foundation-stream-consumers/native-integration-v2-disabled-off-root-results.json); engine9,995,242B;1,164 frozen copies. | [PASS](tests/node-compat/foundation-stream-consumers/independent-native-consumers-v2-disabled-off-review-v1/README.md). |
| RuntimeOnly, GC OFF | [All raw0](tests/node-compat/foundation-stream-consumers/native-integration-v2-normal-runtime-root-results.json); engine10,009,523B;1,164 frozen copies. | [PASS](tests/node-compat/foundation-stream-consumers/independent-native-consumers-v2-normal-runtime-review-v1/README.md). |

All four build/freeze/read-only verification gates pass. All four independent native reviews pass; the first normal consumer355 component run and its independent result review now pass. Backend-proof fields remain false/null/null and operational admission is closed. Root separately issued [validation-only pins](tests/node-compat/foundation-stream-consumers/reviewed-native-v2-validation-bootstrap-pins-v1.json), a [Root review](tests/node-compat/foundation-stream-consumers/native-v2-validation-bootstrap-root-review-v1.json) and [three successful read-only bootstrap results](tests/node-compat/foundation-stream-consumers/native-v2-validation-bootstrap-root-results-v1.json), without changing the checked-in null templates. The [component-test source](tests/node-compat/foundation-stream-consumers/component-validation-candidate-v1/README.md) is sealed (65 files/5,151 inputs,38 cases); source review found a control-driver mismatch between ESM and literal-CJS bundler denial messages. No action ran. The v1 [source HOLD](tests/node-compat/foundation-stream-consumers/independent-component-validation-source-review-v1/README.md), index `2a76b6c5…5a04fb`, records the literal-CJS mismatch and a separate pre-type-assertion retention gap. The [sealed v2 correction](tests/node-compat/foundation-stream-consumers/component-validation-candidate-v2/README.md), index `a75ee76c…60002b`, fixes exact category/specifier checks and records typed returns before asserting string. All38 cases/eight denials and native authority templates remain unchanged. Preparation passes64+80+13+35 checks; Root separately repeats the80 correction checks at raw0. [Independent v2 source review](tests/node-compat/foundation-stream-consumers/independent-component-validation-v2-source-review-v1/README.md), index `13bc711d…30655a`, passes. A separate [Root source review](tests/node-compat/foundation-stream-consumers/component-validation-v2-source-root-review.json) authorizes activation only. [Actual source activation](tests/node-compat/foundation-stream-consumers/component-validation-v2-source-activation-root-results.json), Root34235/PID72182, finishes raw0 in14.489 operational seconds, creating47 indexed files/7,268 consumed rows at activated-v2 (index `bfb689fe…227835`). The actual three355 tuples and packaging snapshot are bound without native metadata changes. [Independent generated-family review](tests/node-compat/foundation-stream-consumers/independent-component-validation-v2-family-review-v1/README.md), index `e894a968…90722`, passes all47 files and the exact7,268-input union. Root has separately authorized the [actual read-only preflights](tests/node-compat/foundation-stream-consumers/component-validation-v2-actual-preflight-root-review-v1.json) for normal/GC/control. [Attempt1](tests/node-compat/foundation-stream-consumers/component-validation-v2-preflight-attempt1-root-results.json) fails before native bootstrap because Root omitted the pinned toolchain environment; [Fresh attempt2](tests/node-compat/foundation-stream-consumers/component-validation-v2-actual-preflight-root-results-v1.json) passes all three actual preflights at Root-observed raw0 in57.955 operational seconds with the exact sealed environment. A [separate normal-runtime authority](tests/node-compat/foundation-stream-consumers/normal-component-validation-v1-root-authority.json) now starts Root76866/PID75204:190 planned run observations, six namespace checks and11 uncaught initialization failures. The [actual normal run](tests/node-compat/foundation-stream-consumers/normal-component-validation-v1-root-results.json) finishes at Root-observed raw0 in184.075 operational seconds:190 text/JSON observations, six namespace checks,38 fresh Wasmtime cases and11 uncaught initialization failures. Component `77e65636…30b27` is13,117,207B and imports nothing. Root rehashes all1,318 regular output files and the one module link. [Independent actual-result review](tests/node-compat/foundation-stream-consumers/independent-normal-component-validation-v1-results-review-v1/README.md), index `0f068937…9351d`, now passes all196 complete raw returns, all38 Wasmtime decodes, five1MiB strings,1,176 typed refusal records and1,318 files/one link, with8,625 finite source/native/tool/raw paths rehashed. Reviewer parser/schema attempts are retained separately and are not product failures. The [reviewed-normal bridge](tests/node-compat/foundation-stream-consumers/reviewed-normal-component-validation-v1.json) and [separate GC authority](tests/node-compat/foundation-stream-consumers/gc-component-validation-v1-root-authority.json) ran Root98263/PID78733; the [actual GC result](tests/node-compat/foundation-stream-consumers/gc-component-validation-v1-root-results.json) finishes raw0 in41.459 operational seconds:three retained ordinary-GC records, one fresh Wasmtime record and two namespace observations. Component `ff4c2aae…53421` is13,118,622B with imports[],47 regular files and one link. [Independent GC review](tests/node-compat/foundation-stream-consumers/independent-gc-component-validation-v1-results-review-v1/README.md), index `319cb371…ad5f`, passes all six complete raw returns, four GC records, two full namespaces, fresh Wasmtime decoding and47 files/one link;7,362 finite paths rehash successfully. Strong application/VM coowners remain; no isolated-temporary-root, actual-GC-count, reset/reuse, release or performance claim follows. A [separate consumer-OFF authority](tests/node-compat/foundation-stream-consumers/disabled-component-validation-v1-root-authority.json) ran Root88048/PID76515; the [actual consumer-OFF result](tests/node-compat/foundation-stream-consumers/disabled-component-validation-v1-root-results.json) finishes raw0 in42.662 operational seconds:all eight ESM/literal-CJS bundler denials precede componentization and all five Buffer/stub observations pass. Component `404f905c…4ef64` is13,046,739B with imports[],60 regular output files and one link. [Independent control-result review](tests/node-compat/foundation-stream-consumers/independent-disabled-component-validation-v1-results-review-v1/README.md), index `d041164e…ef438`, passes all eight exact diagnostics (six ESM/two CJS), five complete raw returns, fresh Wasmtime transport and60 files/one link; static component/core inspection confirms imports[] and the run()->string ABI. No callback was supplied to the unsupported exec calls, so callback behavior was not empirically tested. GC/control still require their own actions and reviewed gates. Fresh namespace/text/JSON/refusal/snapshot/GC/control component gates remain. The two shared normal project files have retained pre-GC witnesses; frozen copies remain fixed. Source failures, staging/cache preparation and exact artifact details are retained in [consumer355 history](#consumer355-source-and-build-history).

The [artifact-closure and rollforward plan](tests/node-compat/foundation-classic-streams/production-adoption-v1/artifact-closure-plan-v1/README.md) maps five live Root changes. Its [independent review](tests/node-compat/foundation-classic-streams/independent-artifact-closure-plan-review-v1/README.md), index `4929aae9…86c42c`, holds promotion on two findings:12 zlib manifests contain60 direct old-Root references, and one mutable README changed after the original inspection. The other17,884 inspected files match. The old README bytes have no identified witness and must not be claimed preserved or mapped to unequal new bytes. Seven current status documents have now been separately snapshotted for a successor plan. The [sealed current-context amendment](tests/node-compat/foundation-classic-streams/production-adoption-v1/artifact-closure-current-context-amendment-v1/README.md), index `371132b3…53cb`, supplies a data-only reader, exact context holds and separately identified document snapshots. Its35 reader/context checks pass, including an [independent source review](tests/node-compat/foundation-classic-streams/independent-artifact-closure-current-context-review-v1/README.md), index `1c849e61…61c00`, which authenticates35 files/154 references and executes23+12 pure checks. Promotion and bulk-archive acceptance stay held. Old preflight rerunnability is not inferred. Finish the RSS supplement in the current source context before promotion. The [publisher source](tests/node-compat/foundation-classic-streams/production-adoption-v1/artifact-preservation-candidate-v1/README.md), index `fb9baef5…456b73`, and [independent source review](tests/node-compat/foundation-classic-streams/independent-artifact-preservation-source-review-v1/README.md), index `d11fd5f2…180581`, pass. A [separate Root copy config](tests/node-compat/foundation-classic-streams/production-adoption-v1/reviewed-private-artifact-preservation-copy-v1.json) authorizes only private PENDING preservation. The [actual copy](tests/node-compat/foundation-classic-streams/production-adoption-v1/private-artifact-preservation-copy-root-results-v1.json), Root4241/PID65406, exits0 in59.861 operational seconds:21,682 regular files/zero symlinks,10,835 copied objects including source/review capsules,17,884 protected descriptors and50,894 selected context tuples. The one unavailable README remains an omission, seven snapshots are distinct and SDK/host references remain references. Independent actual byte/context validation is underway. Root separately [accepts the declared preservation scope](tests/node-compat/foundation-classic-streams/production-adoption-v1/private-artifact-preservation-root-acceptance-v1.json) after [actual independent validation](tests/node-compat/foundation-classic-streams/independent-artifact-preservation-results-review-v1/README.md), index `f804d28f…13f7d`, which rehashes all21,682 archive files and original inputs. The archive bytes and embedded PENDING labels stay unchanged. A [new exact five-file review](tests/node-compat/foundation-classic-streams/production-adoption-v1/five-file-corrected-classic-source-promotion-root-review-v1.json) then authorizes only three corrected classic sources plus the recipe/admission tools. [Promotion](tests/node-compat/foundation-classic-streams/production-adoption-v1/five-file-corrected-classic-source-promotion-root-results-v1.json) applies at raw0:all342 live native inputs match all four corrected production manifests, with339 other inputs unchanged and file modes preserved. Independent post-promotion review now passes; its result is included in the separate v13 acceptance. The old12 zlib contexts remain held per the explicit context policy; old preflights are not rerun or redirected. A [narrow independent v13 acceptance audit](tests/node-compat/foundation-classic-streams/independent-classic-v13-acceptance-review-v1/README.md), index `2cbf351b…9a2901`, verifies11 proof indices/230 members and13 Root references, finding no concrete scope overclaim. The [post-promotion review](tests/node-compat/foundation-classic-streams/independent-five-file-classic-source-promotion-review-v1/README.md), index `b6630d51…6df0a0`, passes all five afterimages/modes, all342 source inputs and unchanged archive bytes/holds. The separate [bounded v13 acceptance](tests/node-compat/foundation-classic-streams/production-acceptance-v13/README.md), index `398ecd52…2b8b2`, accepts the corrected classic checkpoint; consumer355/zlib350 remain experimental and the full roadmap is incomplete.

The [combined consumer validation receipt](tests/node-compat/foundation-stream-consumers/reviewed-component-validation-results-v1.json), SHA `36964b2d…ded65b`, now records all three independently reviewed runs:207 complete returned strings across190 normal records, four combined-owner GC records, five control records and eight namespace observations;11 initialization rejections are separate. All three components import nothing. This accepts only the bounded experimental validation result. Native source promotion, operational admission, performance, RuntimeOnly, broader regression and both-host HTTP/release gates remain separate; foundations-v13 stays the accepted production checkpoint.

The release/host source audit finds that unchanged producer9edf already supports `normal-runtime`; existing corrected342 release wrappers cannot consume355 validation pins unchanged. A [separate Root fourth-build authority](tests/node-compat/foundation-stream-consumers/native-integration-v2-normal-runtime-build-root-review.json) preserves all3,492 frozen rows of the old three variants and launches existing `build-one.py normal-runtime` under Root7122/PID80946. The [actual RuntimeOnly result](tests/node-compat/foundation-stream-consumers/native-integration-v2-normal-runtime-root-results.json) now finishes raw0 for build/freeze/read-only verification:108 build steps in297.418 operational seconds,4.822s freeze and2.870s verification. Engine `b227a8d2…8ad60` is10,009,523B, metadata `9668b23d…77b49`, freeze `3180f5b8…c5040`,1,164 frozen copies/1,162 original entries. All3,492 older frozen rows still match after build and freeze. The [release/host source plan](tests/node-compat/foundation-stream-consumers/release-host-plan-v1/README.md), index `24a71405…24350`, maps the required new context-aware355 families. The unchanged exporter also finishes raw0 for a separate four-variant **unreviewed** candidate (Root48484/PID2948,12.781 operational seconds); that data does not replace reviewed pins. [Independent RuntimeOnly native review](tests/node-compat/foundation-stream-consumers/independent-native-consumers-v2-normal-runtime-review-v1/README.md), index `b34b0d0c…08b9a`, passes7,247 finite references,1,164 frozen/1,162 original entries and its distinct4,650-file OpenSSL source tree. A fresh [four-variant reviewed pin document](tests/node-compat/foundation-stream-consumers/reviewed-native-v2-validation-bootstrap-pins-v2.json), SHA `93512520…a5d67b`, and [Root review](tests/node-compat/foundation-stream-consumers/native-v2-validation-bootstrap-root-review-v2.json), SHA `6359ca0b…470ce4`, preserve all three earlier reviewed pin objects exactly. [All four actual read-only bootstraps](tests/node-compat/foundation-stream-consumers/native-v2-validation-bootstrap-root-results-v2.json), Root9088, finish raw0. The old bdb/22fe authority, three-variant bfb family and checked-in null templates remain fixed. The [fresh release/follow-on source candidate](tests/node-compat/foundation-stream-consumers/release-gates-candidate-v1/README.md), index `a74dc603…9e5372`, now seals1,778 files/9,042 original inputs,23 reversible host edits, a102-module selected graph and complete physical tooling. All355 native bytes and176 inherited case/oracle/fixture files remain unchanged. Preparation records2,638 source checks,61 pure checks and parse-only syntax success; independent source review and actual exclusive publication remain required. It includes the eight new release stages and separate allocator/focused/getter scopes, with HTTP deferred. No RuntimeOnly component or host pass is claimed. [Root independent source review](tests/node-compat/foundation-stream-consumers/independent-release-gates-source-review-v1/README.md), index `852b4bb6…b84d2`, passes all1,778/9,042 rows,23 exact reversals,1,677 source origins and the actual tooling/selected graph. The [source-only activation authority](tests/node-compat/foundation-stream-consumers/release-gates-source-v1-root-review.json), SHA `a01a8711…7a5cc`, runs the unchanged publisher as Root94949/PID21607:raw0 in9.879 operational seconds. [Root publication verification](tests/node-compat/foundation-stream-consumers/release-gates-source-v1-root-results.json), SHA `39a90af4…06e12`, checks all1,726 indexed/1,727 actual generated files. Generated index `10d6df02…4289b` binds12,544 original/local input rows; [Independent generated-source review](tests/node-compat/foundation-stream-consumers/independent-release-gates-activated-v1-source-review-v1/README.md), index `7be057cd…7d4b7`, now passes the complete1,727-file/12,544-row closure and actual four-native lineage. Its first [actual read-only preflight](tests/node-compat/foundation-stream-consumers/release-gates-preflight-v1-root-failure-v2.json), Root76766/PID25354, fails raw1 in12.776 operational seconds before guest execution. `metadata-admission.admit` receives the frozen355 native-source tree, which lacks the configured checkout’s767 tooling dependencies and `tests/` directory. RuntimeOnly/GC are not started. CONSUMERS-RELEASE-CONTEXT-M1 is a missed source/generated-review mismatch; original a74dc/852b/10d6/7be records remain unchanged. A separate correction must authenticate and distinguish the configured native/tool root from the frozen runtime source root, with fresh source/publication review before retry. All new runtime/release/HTTP gates remain pending. [Independent failure audit](tests/node-compat/foundation-stream-consumers/independent-release-gates-preflight-v1-results-review-v1/README.md), index `ffafa473…29600`, confirms the raw1/empty stdout/1,165-byte stderr and both unstarted variants. The genuine host admission helpers executed; bootstrap completion is only a source control-flow inference in this failed run. No separate persisted bootstrap pass, guest/compiler/native-code or timing result is claimed. A [bounded context correction](tests/node-compat/foundation-stream-consumers/release-gates-context-amendment-v1/README.md), index `9080e48f…79b70`, adds five reversible bridge edits and an explicit two-root helper. [Independent source review](tests/node-compat/foundation-stream-consumers/independent-release-gates-context-source-review-v1/README.md), index `fc72ebac…b089a`, passes23/3,270 amendment and1,778/9,042 parent rows, both355 source roots and unchanged core/data contracts. Its [new source authority](tests/node-compat/foundation-stream-consumers/release-gates-context-v1-root-review.json), SHA `e05c4478…128fdf`, runs Root21799/PID29349 raw0 in8.899 operational seconds. [Root generated-v2 verification](tests/node-compat/foundation-stream-consumers/release-gates-context-v1-root-results.json), SHA `ba79b44f…36eb9`, passes1,727 indexed/1,728 actual files and12,569 union rows; generated index `562e4236…79250` awaits independent review before any retry. An [external planning-template erratum](tests/node-compat/foundation-stream-consumers/release-gates-context-v1-planning-template-erratum.json) records one inherited, unconfigured basename still saying v1; executable publisher requires v2 and that planning field grants no authority. Sealed bytes remain unchanged. The [independent generated-v2 review](tests/node-compat/foundation-stream-consumers/independent-release-gates-activated-v2-source-review-v1/README.md), index `97124320…6e48`, now passes the complete1,728-file/12,569-row context, both355 source roots,767 configured tools, four native tuples and103/196 graph. Root54698 is retrying only the actual read-only normal-OFF/RuntimeOnly/GC preflights against exact562e, with separate raw logs/terminals; no guest/component action is authorized by these reads. The [actual three-mode result](tests/node-compat/foundation-stream-consumers/release-gates-preflight-v2-root-results.json), SHA `170251e3…2cec7`, now finishes Root54698 raw0 in all modes: normal-OFF PID31713/32.536s, RuntimeOnly31933/31.953s, GC32059/26.963s, with complete224/228/220-byte JSON returns and empty stderr. [Independent actual-result review](tests/node-compat/foundation-stream-consumers/independent-release-gates-preflight-v2-results-review-v1/README.md), index `a17bd8ef…36d10`, passes all three and the current12,629-path source/native/tool/log closure. These are genuine read-only admission passes. A separate [release-OFF runtime authority](tests/node-compat/foundation-stream-consumers/release-gates-release-off-v1-root-authority.json), SHA `1c2c1b9d…2633f`, starts Root6561/PID33623 for eight fresh serial correctness stages under exact562e. The [actual release attempt](tests/node-compat/foundation-stream-consumers/release-gates-release-off-v1-failure-root-results-v2.json) stops Root6561/PID33623 raw1 after731.356 operational seconds: core/allocator/stream-web top jobs0, optional path/events/string-decoder/assert/querystring0, then util1. Four strict stages are not started. CONSUMERS-RELEASE-DATA-CLOSURE-M2 is a missing separately pinned Node-oracle producer source file in the final explicit util sourceFiles provenance list (distinct from its earlier oracle.sources builtin-hash check). Initial Root commentary incorrectly placed that failure before componentization; actual partial components and source ordering show util builds/calls occurred before line39. No completed util report/pass or independently recovered raw returns is inferred. All partial files/logs and successful stage reports remain preserved, without overall release acceptance or pass reuse; a bounded dynamic-data closure correction and fresh family/runtime retry are required. [Independent actual failure review](tests/node-compat/foundation-stream-consumers/independent-release-off-v1-failure-review-v1/README.md), index `584b9178…98a5`, validates1,933 hashes,195 regular outputs/nine links/16 components and the exact partial/raw1 scope, without decoding uncaptured util returns or adopting old passes. The [minimal report-data amendment](tests/node-compat/foundation-stream-consumers/release-gates-report-data-amendment-v1/README.md), index `b0eab614…94674`, now seals15/1,897 rows and41 source/pure checks: one immutable2251-byte producer DATA file (`fe48fc80…3c4ba`),69 explicit late reads,160/259 graph and fresh activated-v3/runtime namespaces. Current Node oracle and all runner/case/guest/native bytes remain unchanged. Independent source review and new publication/validation/runtime retry remain required. [Independent source review](tests/node-compat/foundation-stream-consumers/independent-release-gates-report-data-source-review-v1/README.md), index `8c3b7cc0…54043`, now passes12,621 unique hashes, complete1897/9042 contexts and all69 finite reads/160-row graph, with no owner action. A [new source-only authority](tests/node-compat/foundation-stream-consumers/release-gates-report-data-v1-root-review.json), SHA `25a200c5…61e1`, runs the unchanged publisher Root34763/PID45020 raw0 in8.946 operational seconds. [Root v3 publication verification](tests/node-compat/foundation-stream-consumers/release-gates-report-data-v1-root-results.json), SHA `e592056d…910c`, passes1,729 indexed/1,730 actual files,12,681 union rows and the exact2251-byte datum. Generated-v3 index `a986e9b2…64916` now passes [independent generated review](tests/node-compat/foundation-stream-consumers/independent-release-gates-activated-v3-source-review-v1/README.md), index `897d7496…0e6ea`:1,729 indexed/1,730 actual files, exact12,681-row union and14,289 unique input tuples. It verifies all69 actual caller/data reads, four native tuples and the sole new producer datum; no helper/runtime action is performed by that review. The [actual v3 admission result](tests/node-compat/foundation-stream-consumers/release-gates-preflight-v3-root-results.json), SHA `b7308ac4…2575cd`, finishes Root24109 raw0 for all three modes: normal-OFF PID48977/28.269s, RuntimeOnly49129/27.516s and GC49259/27.134s. All complete expected JSON returns and empty stderr are retained; admission helpers execute, with no guest/component/native compiler/host/timing action. [Independent v3 admission review](tests/node-compat/foundation-stream-consumers/independent-release-gates-preflight-v3-results-review-v1/results.json), index `4f49bddd…9f16f`, passes14,316 current input tuples and exactly those three outcomes. A [new release-OFF authority](tests/node-compat/foundation-stream-consumers/release-gates-release-off-v2-root-authority.json), SHA `207a4f92…85f7`, starts Root90406/PID50986 for the entire eight-stage batch under exacta986 and a fresh v3 runtime output. The [whole eight-stage retry](tests/node-compat/foundation-stream-consumers/release-gates-release-off-v2-root-results.json), SHA `bd402511…a57b7`, finishes Root90406/PID50986 raw0 in1,752.267 operational seconds, with empty outer stdout/stderr, clean controller/child0 and a final source recheck. All core/allocator/stream-web/optional/strict-sync/strict-runtime/strict-late/strict-callback jobs are fresh0, including util and all four previously unstarted strict stages. Root verifies346 regular outputs/13 output links/40 files matching*.component.wasm (occurrences, not unique binaries) and every producer report/completion/log hash; no old partial pass is reused. [Independent whole-release review](tests/node-compat/foundation-stream-consumers/independent-release-gates-release-off-v2-results-review-v1/results.json), index `75e18ca4…a390a`, passes13,078 current paths, all eight jobs/six optional modules,346 outputs/13 links and40 component occurrences. It independently reads zero top-level imports on those40 binaries. Typed observations include30 complete first/retained/fresh comparisons and eight paired fatal/discard cases;19 successful Wasmtime records retain hashes/decoded values without complete raw stdout, and core initializer excerpts are qualified. No unique trap-origin or global binary-uniqueness claim follows. The host controller prefix changes to v3; native/guest/runner case bodies and Node oracles stay unchanged.

A [source-only crypto inspection](docs/node-compat/crypto-native-source-notes-v1/README.md), index `570d84e0…4303c`, identifies reusable owned digest staging and the actual OpenSSL/ArrayBuffer transfer path. It also identifies a key-owner gap: CryptoKey stores released native key pointers but inherits an empty finalizer policy; the HMAC vector owner is discarded. [Independent source review](docs/node-compat/independent-crypto-native-source-notes-review-v1/README.md), index `1dd2fac2…04c02`, confirms the two note members/11 inputs and these ownership paths. It also records that CryptoKey overrides init_class directly, so a future owner fix must preserve that actual installation behavior. This remains source evidence with no runtime leak probe or source change. Key cleanup/secret lifetime must be resolved before reusing that path for Node Hmac/KeyObject; one-shot digest remains a separate candidate.

The [isolated CryptoKey owner candidate](tests/node-compat/foundation-crypto/key-owner-candidate-v1/README.md), index `216d0272…c47d0`, now seals four unapplied afterimages/18 reversible edits. It retains and cleanses owned HMAC vector storage, registers an undefined-safe foreground finalizer for vector/EVP owners, preserves actual constructor/global behavior and fixes the RSA ArrayBuffer allocator/null-view path. Two actual SDK147 Release frontend checks and37 source checks pass, with1,104 observed dependencies hashed after compilation. [Independent bounded source review](tests/node-compat/foundation-crypto/independent-key-owner-source-review-v1/README.md), index `a213a1e2…720e5`, passes35 files/1,185 inputs and all four afterimages. Full native/link/crypto/GC/lifetime integration remains required; BIGNUM error cleanup, other private copies and allocation/length policy are explicit follow-ons. No live source or existing engine is changed. The independent audit also identifies an existing prototype-as-key safety gap in sign/verify: initialized-key helpers assume reserved slots that the prototype lacks. Borrowing conclusions apply to factory-created keys; source guards must be reviewed before any such negative runtime probe. The separate [prototype-key guard candidate](tests/node-compat/foundation-crypto/prototype-key-guard-candidate-v1/README.md), index `73fbf4f2…da831`, now seals30 files/1,228 references. Two sign/verify conditions reject the intrinsic prototype through the existing invalid-key TypeError branch before slot helpers. Its four donor owner afterimages remain byte-exact; the combined source is five files/20 edits. Preparation records1,137 source/data checks, ten synthetic branch rows and one composed SDK147 Release frontend pass with1,089 post-only observed dependencies. [Independent delta source review](tests/node-compat/foundation-crypto/independent-prototype-key-guard-source-review-v1/README.md), index `f11a739c…1a648`, now passes all30/1,228 rows, exact two-edit reversal/control-flow checks and donor/review authentication. The first Root reader rejected the explicitly declared SDK clang++ alias; that raw failure remains preserved, and the corrected reader authenticates its exact target without executing it. Native/runtime integration remains required; no unsafe old path, key operation, GC, link or guest runs.

The [fresh native350 cost-pair data review](tests/node-compat/foundation-zlib/reviewed-cost-native-pair-v1/README.md), index `58c62276…66077`, now rehashes all2,048 ON/OFF frozen rows,350 source rows each and the separately streamed selected SDK archive/four headers. It grants no action authority or backend-version claim. Tooling v1 is [held](tests/node-compat/foundation-zlib/independent-cost-tooling-source-review-v1/README.md) on outside-binding environment selection and late descriptor capture. [Tooling v2](tests/node-compat/foundation-zlib/cost-tooling-candidate-v2/README.md), index `6793721e…0891b`, passes [independent source review](tests/node-compat/foundation-zlib/independent-cost-tooling-v2-source-review-v1/README.md), index `9fc93b14…4c364`, with those findings closed. Its first [actual private-copy authority](tests/node-compat/foundation-zlib/cost-source-publication-v2-root-authority.json) runs Root37530/PID16564 and [fails raw1 before copying](tests/node-compat/foundation-zlib/cost-source-publication-v2-precopy-failure-root-results.json), SHA `072dafb2…89457`, in1.923 operational seconds. All5,058 base source modes match;20 dynamic proof files are0644 but the publisher mistakenly checks their desired0600 output mode as source permissions. The destination remains absent. [Independent failure review](tests/node-compat/foundation-zlib/independent-cost-source-publication-v2-failure-review-v1/README.md), index `064b8d44…a5bd5`, confirms COST-TOOLING-M3. Existing source, permissions, authority, earlier source PASS and failed receipts remain unchanged; a new v3 separates source/output modes and adds a real0644→0600 text-copy check. No Node-zlib/fflate/oracle/bundle/component/guest or timing action had run before that corrected copy. The [v3 source correction](tests/node-compat/foundation-zlib/cost-tooling-candidate-v3/README.md), index `ff208e72…b36b8`, passes [independent source review](tests/node-compat/foundation-zlib/independent-cost-tooling-v3-source-review-v1/README.md), index `5fd8ea24…bb240`. A fresh [Root source-copy authority](tests/node-compat/foundation-zlib/cost-source-publication-v3-root-authority.json), SHA `3579dcb5…30524`, invokes the unchanged publisher. Root50439/PID20075 finishes raw0 in11.064 operational seconds. [Root output verification](tests/node-compat/foundation-zlib/cost-source-publication-v3-root-results.json), SHA `f292fc92…f67a7`, rehashes all10,187 indexed files and checks10,189 actual regular files,22 rebased links,471 private directories, exact source/output modes and distinct original/copy inodes. The actual index is `4621f7e7…7387b`; [Independent actual-copy review](tests/node-compat/foundation-zlib/independent-cost-source-publication-v3-results-review-v1/README.md), index `f3e17fc6…6f591`, now passes all10,189 files,5,092 independent source copies and all20 actual0644→0600 proof copies. This is a358,037,108-byte indexed source copy, not a codec or timing result. A [separate untimed Node authority](tests/node-compat/foundation-zlib/cost-node-oracle-v3-root-authority.json), SHA `31c57db9…2b150`, then invokes the exact published oracle entry under Node22.14. Root9280/PID21386 finishes raw0 in26.288 operational seconds. The [Root observation](tests/node-compat/foundation-zlib/cost-node-oracle-v3-root-results.json), SHA `b67a7de1…4f21b`, authenticates194 indexed/196 actual files,190 retained raw records and55 codec calls (30 encodes/25 decodes). It captures15 Node streams and30 case associations, an11,934,953-byte oracle and2,106,468-byte rendered module. [Independent actual oracle/render review](tests/node-compat/foundation-zlib/independent-cost-node-oracle-v3-results-review-v1/README.md), index `c0ec7f02…4957d`, passes all190 retained files,55 calls, full fixtures/streams/decoder-consumption records and byte-exact rendered-module reconstruction. The [Root reviewed-input capsule](tests/node-compat/foundation-zlib/reviewed-cost-node-oracle-v3/README.md), index `9de0a274…b5234`, rehashes all194 raw/18 peer files and contains exact independent oracle/module copies with a separate bounded review result. No fflate codec, component, guest or benchmark has executed. A minimal [source-bundle action wrapper](tests/node-compat/foundation-zlib/cost-bundle-action-candidate-v1/README.md), index `367e7960…7ce7c`, now supplies the missing CLI around the existing reviewed preflight/bundler functions. It authenticates its own source and published guard closure, accepts only the three fixed arms/new output, and retains unreviewed code/graphs. Parser-only validation and [independent source review](tests/node-compat/foundation-zlib/independent-cost-bundle-action-source-review-v1/README.md), index `70e2ac6b…06e90`, pass. A new [bundle-only Root authority](tests/node-compat/foundation-zlib/cost-bundle-v1-root-authority.json), SHA `0776fdf9…70572`, launches the unchanged wrapper367e as Root63317/PID24635. The [actual source-bundle capture](tests/node-compat/foundation-zlib/cost-bundle-v1-root-results.json), SHA `194d8ec8…17a8b`, finishes Root63317/PID24635 raw0 in91.995 operational seconds. All10 indexed/12 actual files hash correctly. Native source is2,139,474 bytes with Buffer/zlib residual imports; both FF sources are byte-identical2,158,735-byte bundles with Buffer only. Every bundle declares seven exports; physical source counts are11/12/12 and all virtual-ID arrays are empty. Three [per-arm source proofs](tests/node-compat/foundation-zlib/independent-cost-bundles-source-results-review-v1/native-on/index.json) now pass, with exact code/graphs, original source paths,7 exports and no virtual helpers: native index `d67a3411…aba7c`, FF-ON `4373b853…a91d5`, FF-OFF `5ebf8f2e…5826b`. The [shared source-bundle review](tests/node-compat/foundation-zlib/independent-cost-bundles-source-results-review-v1/README.md), index `955707ea…faaf6`, now seals20 files and passes the full12-output/10,187-publication-record closure, both1,024-row frozen native inventories and selected SDK references. These are source proofs, with no codec-provider execution or correctness transfer. A [new native-only component authority](tests/node-compat/foundation-zlib/cost-component-native-on-v1-root-authority.json), SHA `a515f2eb…86c16`, now launches actual build/ABI capture as Root53303/PID27236. That [first component attempt](tests/node-compat/foundation-zlib/cost-component-native-on-v1-failure-root-results.json) fails raw1 in23.401 operational seconds; owned worker27301 exits1 in950ms with its group cleaned up. The actual selected componentizer/splicer rejects the reserved WIT parameter name `record` in stage/validate. Nine partial files and both raw terminals/logs remain preserved; no completed component, emitted-import list, actual ABI or ordinary guest call is produced. COST-COMPONENT-WIT-M1 requires a versioned two-name WIT correction, actual old-fail/new-pass parser regression and fresh output/action before retry. Original a2fa/3279/a515 and the successful Node/source-bundle evidence remain unchanged. [Independent actual failure audit](tests/node-compat/foundation-zlib/independent-cost-component-native-on-v1-failure-review-v1/README.md), index `0075de18…610a7`, confirms141 finite inputs, all9 partials, persisted parent/worker1 and clean group shutdown. Published packager order places the WIT failure before Wizer/check_init; no ABI or Jco result is inferred. The [actual pinned WIT-parser regression](tests/node-compat/foundation-zlib/cost-component-wit-parameter-parser-regression-root-v1/README.md), index `5fe4a9a5…abb4b`, now demonstrates original raw1/corrected raw0 with only the two `record`→`input` parameter-name replacements. `wasm-tools1.235.0` creates a797-byte synthetic dummy metadata module; no StarlingMonkey guest or engine is run. A minor initial Root version assertion omitted the observed build suffix and stopped before embed; that preparation correction is retained. The [thin component correction](tests/node-compat/foundation-zlib/cost-component-wit-amendment-v1/README.md), index `e7252156…57caa`, now passes [independent source review](tests/node-compat/foundation-zlib/independent-cost-component-wit-source-review-v1/README.md), index `6d54fd8a…015a4`:20/48 rows, full donor/tooling indices, four reversals and the complete78-row prospective child-critical closure. The unchanged worker reads the new physical WIT; separate own/base source identities and fresh v2 outputs are explicit. [Native-only v2 authority](tests/node-compat/foundation-zlib/cost-component-native-on-v2-root-authority.json), SHA `96c8eec8…199e0`, launches Root47928/PID30570 for the corrected actual packager/ABI retry. Ordinary guest workloads and timing remain disallowed. The [v2 actual attempt](tests/node-compat/foundation-zlib/cost-component-native-on-v2-failure-root-results.json) finishes parent raw1 in30.863 operational seconds and owned worker30609/raw1 in5,099ms with clean group shutdown. It successfully retains a21,404,256-byte component (`3d194a73…b1229`), actual seven-function WIT/imports[], Jco seven-function metadata, core/glue/d.ts, then fails the static JS export checker because pinned Jco also emits `export const _util = {}`. Twenty partial files remain unaccepted; seven WIT functions and the extra glue helper must be validated separately in a bounded successor. [Independent actual-failure audit](tests/node-compat/foundation-zlib/independent-cost-component-native-on-v2-failure-review-v1/README.md), index `45ded562…49cbe`, verifies163 inputs/20 partials/78 critical tuples, retained WIT/metadata/d.ts/glue and parent/worker1. It does not claim a new peer binary-WIT decode or component acceptance. No ordinary guest workload or timing call runs, and the failed build is not relabelled successful. The [bounded glue correction source](tests/node-compat/foundation-zlib/cost-component-glue-amendment-v1/README.md), index `cf3110b3…5d794`, now records39 pure/captured-source AST checks and11 parse checks, including rejection by the old checker and exact function/helper classification by the proposed checker. Its host Rolldown parser library executes only for AST data parsing; generated JS, Jco transpile, componentizer and guest do not run. Fresh v3 output roots and separate own/WIT/base/tooling identities are explicit. [Independent source review](tests/node-compat/foundation-zlib/independent-cost-component-glue-source-review-v1/README.md), index `7cb9b2b9…c5c6c`, passes469 finite hashes,20/91 own rows, all donor/tooling indices, three reversals and78 prospective critical tuples. Its exact7-function/8-name helper policy remains a finite pinned-source check. After the consumer batch stops, [native v3](tests/node-compat/foundation-zlib/cost-component-native-on-v3-root-results.json) finishes Root49919/PID38397 raw0 in35.700 operational seconds; [FF-ON](tests/node-compat/foundation-zlib/cost-component-fflate-on-v3-root-results.json) and [FF-OFF](tests/node-compat/foundation-zlib/cost-component-fflate-off-v3-root-results.json) finish serially under Root78290/PIDs38958/39049 raw0 in41.571/51.159s. Components are21,404,160/21,450,767/21,419,907 bytes, each with25 indexed/27 actual files, imports[], seven WIT/metadata/d.ts functions and exactly eight JS names including empty `_util`. Root fully rehashes each index/membership. [Per-arm native artifact review](tests/node-compat/foundation-zlib/independent-cost-component-v3-results-review-v1/native-on/index.json), index `8199f3af…01b97`, [FF-ON](tests/node-compat/foundation-zlib/independent-cost-component-v3-results-review-v1/fflate-on/index.json) `72d1d507…c1e8d1`, and [FF-OFF](tests/node-compat/foundation-zlib/independent-cost-component-v3-results-review-v1/fflate-off/index.json) `1a3774fa…33e6ec` pass raw lifecycle, source/native/oracle/code/17-descriptor bindings, emitted records and unique core/component byte relation. The [shared artifact review](tests/node-compat/foundation-zlib/independent-cost-component-v3-results-review-v1/results.json), index `9ab82077…d9893`, now seals26 files and rechecks11,836 unique inputs across all three arms, including publication/native/source/critical/SDK closures and distinct raw terminal evidence. These are componentization/static ABI results, with no ordinary guest calls, new independent binary-WIT decode, target-host execution or performance conclusion. The separate [component-build source cut](tests/node-compat/foundation-zlib/cost-component-candidate-v1/README.md), index `a2fa62b3…22f9`, seals25 files/294 references with51 pure/317 source/12 parse checks. It uses the real selected componentizer,53512-byte adapter, seven scalar exports, imports[] audit and owned worker lifecycle; all actual component/oracle/bundle proof and action slots remain separate. Its explicit proposed64MiB artifact cap/600s operational ceiling need future action authority. [Independent component-source review](tests/node-compat/foundation-zlib/independent-cost-component-source-review-v1/README.md), index `3279eb04…66512`, now passes all25/294 rows,286 base members and five copied mechanisms. The later first actual componentizer call fails on the WIT parse error above; source-level review had not exercised a WIT parser. Actual ABI/imports/Jco/ordinary guest correctness remain unproved, and no transpiler or ordinary guest action runs.

## Detailed evidence and limits

Current position: **foundations-v13 is accepted, bounded**, through the
[Root classic acceptance receipt](tests/node-compat/foundation-classic-streams/production-acceptance-v13/README.md). Its [v12 parent](tests/node-compat/foundation-scheduler/production-acceptance-v12/README.md) remains historical evidence.
All private scheduler diagnostic and production gates pass, including fresh
eight-stage replay, allocator/focused GC and same-byte HTTP on both stock hosts.
The public API versions remain unchanged; no public process/nextTick/ALS API
was added. Known getter, Symbol, ownership, reset/reuse and performance limits
remain explicit. The original classic342 layer is applied: four Release variants are
frozen and three bounded classic component suites pass with independent reviews.
Its original-generation runtime gates and independent reviews are complete:40 replay,
20 followon,15 classic and one combined HTTP component occurrences. The
[runtime composition receipt](tests/node-compat/foundation-classic-streams/production-adoption-v1/runtime-gates-complete-v1.json)
does not claim76 globally unique binaries. New Node-host workload comparisons
retain14 trace counterexamples against the canonical factory. The unchanged
original342 component reproduces four minimal Node gaps on three retained
Jco calls and fresh Jco/Wasmtime, with independent result verification. The
expanded11-case run adds two object-encoding differences (six total); its
independent result review passes. The
[six-gap acceptance hold](tests/node-compat/foundation-classic-streams/production-adoption-v1/stream-trace-acceptance-hold-v2.json)
keeps the old-source counterexamples separate from corrected-source proof.
The [corrected source generation](tests/node-compat/foundation-classic-streams/production-adoption-v1/README.md#corrected-trace-source-generation)
retains four reviewed production freezes, 474 files each, and its reviewed
26-file runtime family with 6,414 consumed inputs and 22 tool links. The three
[corrected classic suites](tests/node-compat/foundation-classic-streams/production-adoption-v1/corrected-classic-runtime-root-results-v1.json)
finish at Root-observed exit 0, publishing 90/91/90 files and 15 component
occurrences. OFF/GC import nothing; RuntimeOnly imports only
`wasi:random/random@0.2.10`. The [independent all-four result review](tests/node-compat/foundation-classic-streams/independent-corrected-classic-results-review-v1/README.md),
index `8c3da4a2…41e8cc`, passes 19 ordinary groups, 48 deferred call/new cases,
17 overload refusals, three limits and 65 initializer failures per enabled suite,
plus retained/fresh state and failure controls. Disabled OFF passes eight
ESM/static-CJS denials without a component. The separately reviewed Node11 gate
adds one zero-import component occurrence. Main and successful clean-control
Wasmtime stdout bytes were not retained: the review checks parsed observations
and stdout hashes, not an independent decode of those missing streams. Fatal
raw streams are checked; generic traps do not identify error origin. GC covers
combined owners only. Original source/native packets and counterexamples stay
unchanged.

Diagnostic producer-v3 has successful [ON](tests/node-compat/foundation-classic-streams/production-adoption-v1/measurement-producer-v3-on-native-root-results.json)
and [OFF](tests/node-compat/foundation-classic-streams/production-adoption-v1/measurement-producer-v3-off-native-root-results.json)
build/freeze/read-only checks, each at exit 0 with 109 build steps and 525 frozen
files. Independent native reviews [ON `c05afb8d…`](tests/node-compat/foundation-classic-streams/independent-measurement-producer-v3-on-native-review-v1/README.md)
and [OFF `ca2debb8…`](tests/node-compat/foundation-classic-streams/independent-measurement-producer-v3-off-native-review-v1/README.md)
pass. Root's separate [ON-only pins](tests/node-compat/foundation-classic-streams/production-adoption-v1/reviewed-diagnostic-v3-on-pins.json)
(`2e9811a5…`) and [authority](tests/node-compat/foundation-classic-streams/production-adoption-v1/diagnostic-v3-on-root-review-receipt.json)
(`9681578e…`) do not constitute a measurement pair. A separate
[actual pair review](tests/node-compat/foundation-classic-streams/production-adoption-v1/diagnostic-v3-pair-root-review-receipt.json)
now authenticates both variants and their independent proofs, rechecking 525
frozen copies and 521 original references per variant. Its
[pair pins](tests/node-compat/foundation-classic-streams/production-adoption-v1/reviewed-diagnostic-v3-pair-pins.json)
are `f3626851…`; the earlier ON-only authority remains unchanged. This permits
source preparation, with timing still disabled.
The [correctness companion138a](tests/node-compat/foundation-classic-streams/measurement-correctness-candidate-v1/README.md),
mandatory [reporting amendment0558](tests/node-compat/foundation-classic-streams/measurement-correctness-reporting-amendment-v1/README.md)
and [source review c695](tests/node-compat/foundation-classic-streams/independent-measurement-correctness-source-review-v1/README.md)
remain bound to the [ce2f activator](tests/node-compat/foundation-classic-streams/measurement-correctness-activation-candidate-v1/README.md)
(19 files/6,908 inputs, 27 Root source checks and [peer ee4d5](tests/node-compat/foundation-classic-streams/independent-measurement-correctness-activation-source-review-v1/README.md)).
[Source activation and artifact preflight](tests/node-compat/foundation-classic-streams/production-adoption-v1/correctness-source-activation-and-preflight-root-results.json)
pass, creating family `4728c365…f33f49` (21 files/7,489 inputs), whose
[generated-family review634077e4](tests/node-compat/foundation-classic-streams/independent-measurement-correctness-family-review-v1/README.md) passes.

The [first full 20-workload/14-boundary attempt](tests/node-compat/foundation-classic-streams/production-adoption-v1/workload-timeout-attempt1-root-results.json)
(`e8165564…`, session90660) exits 1 after a 55-second Wasmtime child timeout.
It publishes no final result, completion or semantic counterexample. The
original timed-out case is unknown; unretained Jco observations cannot count as
passes. The [independent failure review c5a0a80f](tests/node-compat/foundation-classic-streams/independent-workload-timeout-failure-review-v1/README.md)
passes within that evidence scope. Separate fresh case0 Jco and Wasmtime
controls match the full Node oracle. A [separate fresh case5 control](tests/node-compat/foundation-classic-streams/production-adoption-v1/workload-public-case5-root-results.json)
(`793a2f0d…`, session16818) returns child exit 0 after 177.338 operational seconds
under a 600-second cap; its complete trace, setup and checksum equal Node case5.
This proves neither the original timeout's case/cause nor deadline adequacy for
all cases or a performance result. The original failure remains unchanged.

The [persistence amendment60a8687e](tests/node-compat/foundation-classic-streams/measurement-correctness-persistence-amendment-v1/README.md)
and [peer6fb6](tests/node-compat/foundation-classic-streams/independent-correctness-persistence-source-review-v1/README.md)
lead through the reviewed v2 activator to [source418ff8fe](tests/node-compat/foundation-classic-streams/measurement-correctness-activated-v2/README.md)
(22 files/7,542 inputs; [family peer c30b596a](tests/node-compat/foundation-classic-streams/independent-correctness-v2-family-review-v1/README.md)).
The [fresh full v2 run](tests/node-compat/foundation-classic-streams/production-adoption-v1/corrected-workload-v2-root-results.json)
finishes at Root-observed raw exit0 (session66794, receipt `6218afd5…`).
[Independent result review0f59a0da](tests/node-compat/foundation-classic-streams/independent-workload-v2-results-review-v1/README.md)
passes: all105 returned records match the complete original20 Node workload
rows and14 boundary observations, across three retained Jco rotations, fresh
Jco and21 fresh Wasmtime calls. All21 raw Wasmtime streams independently
double-decode exactly;632 completion files and final source/native/tool seals
are checked. Component29c7d954… is12,977,999 bytes with zero imports and two
public scalar exports. No old result is resumed or reused. The ON-only
diagnostic authority stays separate from production and measurement-pair
authority. scheduledCallbacks is the original workload counter; native queue/
work/empty counters are unavailable. This finite pass claims no performance,
GC/root isolation, reset/ALS, request reuse or full Node/Streams compatibility.

The separate [measurement-execution source4b6fdfa5](tests/node-compat/foundation-classic-streams/measurement-execution-candidate-v1/README.md)
has 43 files/7,004 inputs. [Independent review96bc44a3](tests/node-compat/foundation-classic-streams/independent-measurement-execution-source-review-v1/README.md)
requires mandatory M1 deadline/capture fixes and permits no activation. A
[new amendment](tests/node-compat/foundation-classic-streams/measurement-execution-deadline-amendment-v1/README.md) is sealed at index `b0975b54…` (25 files/7,112 inputs), with 36 source/reversal,
18 pure deadline and 11 syntax checks. Its [independent source review](tests/node-compat/foundation-classic-streams/independent-measurement-execution-deadline-source-review-v1/README.md)
passes (`9e602ec9…`). Root's fresh source/reversal and pure deadline checks
also pass, with seven syntax checks. Source activation of the mandatory
successor finishes at Root-observed exit 0 (session69131), publishing index
`1b801439…07612` with 35 files and 7,709 consumed inputs. Both read-only
variant preflights pass at exit 0 (session24691), recorded in the
[source and preflight receipt](tests/node-compat/foundation-classic-streams/production-adoption-v1/common-byte-v2-source-and-preflights-root-results.json).
The [independent family review](tests/node-compat/foundation-classic-streams/independent-common-byte-v2-family-review-v1/README.md)
passes (`4e986ca1…`). The [four-arm attempt25227](tests/node-compat/foundation-classic-streams/production-adoption-v1/common-byte-v2-stock-graph-failure-root-results.json) finishes at raw exit1 in the
host stock graph checker before stock componentization. The inventory has no
`provider` field; its three original guest paths are explicit sourceBeforeAfter
rows. Native-on, canonical-on and canonical-off completed their full arms.
[Independent reviewbf9fa2a6](tests/node-compat/foundation-classic-streams/independent-common-byte-v2-three-arm-failure-review-v1/README.md) verifies231 durable observations against
all14 Node oracles, identity/probes, raw calls and final source closure. A new
[stock-only correction and composition source](tests/node-compat/foundation-classic-streams/measurement-stock-composition-candidate-v1/README.md) passes
[independent reviewddbbe2a7](tests/node-compat/foundation-classic-streams/independent-stock-graph-composition-source-review-v1/README.md). Root source checks pass; a separate
[three-arm authorityafdbc0bc](tests/node-compat/foundation-classic-streams/production-adoption-v1/reviewed-common-byte-three-arms-for-stock-only-v1.json) permits fresh stock execution.
[Stock run91122](tests/node-compat/foundation-classic-streams/production-adoption-v1/common-byte-stock-only-root-results-v1.json) and [composition12839](tests/node-compat/foundation-classic-streams/production-adoption-v1/common-byte-composition-root-results-v1.json) finish
at exit0. [Independent actual reviewab100c83](tests/node-compat/foundation-classic-streams/independent-common-byte-stock-and-composition-results-review-v1/README.md) verifies all308
observations against14 Node cases, exact raw calls, component/graph data and
each arm origin. Both required actual-proof documents are indexed. Original
source1b801, arm records and parent exit1 stay unchanged; this is new composed
evidence, not a pass for the original failed run. Timing was still disabled at that preparation checkpoint. Checked-in future
authority templates stay NULL; the external timing phase does not exist and
no timing has run.

The [corrected replay producer8851](tests/node-compat/foundation-classic-streams/trace-replay-activation-candidate-v1/README.md)
passes [source review c373](tests/node-compat/foundation-classic-streams/independent-trace-replay-activation-source-review-v1/README.md)
and its source activation creates [family a08aec2d](tests/node-compat/foundation-classic-streams/production-adoption-v1/trace-replay-source-activation-root-results.json)
with 83 files and 2,293/2,292 root/capability inputs; [generated-family review8529](tests/node-compat/foundation-classic-streams/independent-trace-replay-family-review-v1/README.md) passes.
Root's [preflight environment failure](tests/node-compat/foundation-classic-streams/production-adoption-v1/trace-replay-preflight-attempt1-root-env-failure.json)
is preserved: native OFF/RuntimeOnly/GC pass, then Release OFF lacks the required
explicit `NODE_COMPAT_WASMTIME`. The [corrected-environment retry and combined preflights](tests/node-compat/foundation-classic-streams/production-adoption-v1/trace-replay-preflights-root-results.json)
pass without source/native changes or a guest in those preflight attempts.
The [fresh eight-stage replay](tests/node-compat/foundation-classic-streams/production-adoption-v1/corrected-release-replay-root-results.json)
then passes at Root-observed exit 0, covering six optional foundations and 40
component occurrences, including one fresh historical control. All import
nothing. Five allocator-GC/focused/getter follow-ons also pass, with
[20 component import audits](tests/node-compat/foundation-classic-streams/production-adoption-v1/corrected-followon-imports-root-results.json):
only the eight RuntimeOnly components import standard random@0.2.10.
Independent [replay6a67](tests/node-compat/foundation-classic-streams/independent-corrected-replay-results-review-v1/README.md)
and [follow-on d116](tests/node-compat/foundation-classic-streams/independent-corrected-followon-results-review-v1/README.md)
result reviews pass, including source/native/tool/completion seals and control
origins. These are occurrences, not globally unique binaries. Replay retains
eight fatal raw streams and one independently decoded alias return; 30 other
Wasmtime records have parsed-only or digest-only evidence. Follow-on allocator
GC has a parsed observation without raw stdout or digest; getter Node/Jco values
are parsed-only, while its Wasmtime return independently decodes. Getter/Symbol
parity remains false, GC covers combined owners and failed instances are discarded.

The [corrected HTTP source and whole-entry bundle](tests/node-compat/foundation-classic-streams/production-adoption-v1/corrected-http-source-and-bundle-root-results.json)
pass with17 expected imports and no bundled JS built-in adapters. The
[first packaging attempt](tests/node-compat/foundation-classic-streams/production-adoption-v1/corrected-http-packaging-attempt1-root-env-failure.json)
retains prepared inputs; build stderr asserts missing `NODE_COMPAT_WASM_TOOLS`
before output creation. Its outer terminal status was lost to context and is
not inferred. The [fresh same-input buildv2 and packaging audit](tests/node-compat/foundation-classic-streams/production-adoption-v1/corrected-http-package-root-results.json) finish at Root-observed raw0
(session71459, explicit tool): component24d76605… is64,058,731 bytes, with the
17-import application bundle and exact six standard WASI0.2.10 interfaces;
monotonic-clock duration is type-only, with no callable clock. Production
admission completion exists; the collector verifies25 artifact references and
the7,496-input closure, including a fresh static WIT audit. The
[independent packaging review](tests/node-compat/foundation-classic-streams/independent-corrected-http-package-review-v1/README.md)
passes (`62dbb34b…`), including the public component/core/type graph and actual
application bundle. A separate [Root phase](tests/node-compat/foundation-classic-streams/production-adoption-v1/corrected-http-component-phase-root-review-v1.json)
binds these exact bytes (`b7cfeb6b…`). Fresh Wasmtime/wash runs and their combined
audit finish at Root-observed exit0 in session60088. The
[combined Root receipt](tests/node-compat/foundation-classic-streams/production-adoption-v1/corrected-http-combined-root-results.json)
(`6c4eb6de…`) rechecks 29 evidence files and all 7,496 source rows. Each host
returns three successful responses and stops at exit0; both counter sequences
are1/1/1. The [independent final result review](tests/node-compat/foundation-classic-streams/independent-corrected-http-results-review-v1/README.md)
passes (`2f5df929…`), independently checking all six responses and the deployment,
configuration and source/native/tool evidence. No instance reuse or request
isolation is inferred.
Measurement is complete; targeted memory/startup, artifact/archive and acceptance remain incomplete; bounded v12 stays accepted and the roadmap is unfinished.
The completed [measurement](tests/node-compat/foundation-classic-streams/production-adoption-v1/common-byte-composed-timing-root-results-v1.json) finishes raw0:42 calibration/126 timed workers plus final source audit,1,037 output files. [Integrity review3843d019](tests/node-compat/foundation-classic-streams/independent-composed-timing-integrity-review-v1/README.md) and the [numerical analysis](docs/node-compat/classic-stream-measurement-v1/README.md) are separate evidence. The [Root strategy decision](tests/node-compat/foundation-classic-streams/production-adoption-v1/classic-implementation-strategy-root-decision-v2.json) retains the shared guest-JS stream state machine and native byte primitives; registered imports avoid a duplicate bundle and save7.85% measured component bytes, with no consistent same-engine warm-speed or memory advantage. The optional unused installation stays OFF. Stock-provider differences include a different provider/scheduler; FNV/validation stays timed and controls are not subtracted. Public RSS includes proof/V8 overhead, and raw timing-call compact returns were not retained. The separate18-worker process RSS supplement passes [independent result review](tests/node-compat/foundation-classic-streams/independent-process-rss-supplement-v2-results-review-v1/README.md); no private heap or production-engine performance claim follows.

Historical failures/counterexamples remain unchanged. The61-case [zlib corpus
and harness a7eca234](tests/node-compat/foundation-zlib/component-validation-candidate-v1/README.md) and
[control-evidence amendment fd3ec6ef](tests/node-compat/foundation-zlib/component-validation-control-evidence-amendment-v1/README.md)
retain the [240fdc77 source hold](tests/node-compat/foundation-zlib/independent-component-validation-source-review-v1/README.md).
The new [bootstrap/coverage amendment a376c32b](tests/node-compat/foundation-zlib/component-validation-bootstrap-coverage-amendment-v1/README.md)
(15 files/8,640 inputs) addresses the call-counter, native error-field-type and
repeated-namespace identity gaps and rebinds producer v3. Its [independent source
review654f077f](tests/node-compat/foundation-zlib/independent-component-validation-coverage-source-review-v1/README.md)
passes. The [v4 publisher rebindcd458](tests/node-compat/foundation-zlib/component-validation-v4-rebind-amendment-v1/README.md)
(8 files/8,770 inputs, nine publisher edits) passes [independent review74109e3f](tests/node-compat/foundation-zlib/independent-component-validation-v4-rebind-source-review-v1/README.md).
The a376 payload stays exact:61 Node cases,28 full-byte fixtures,40 bindings and
107 typed constants. Separate [Root validation-only pinsb61e1f38](tests/node-compat/foundation-zlib/reviewed-native-v4-validation-bootstrap-pins-v1.json)
and [review7274a874](tests/node-compat/foundation-zlib/native-v4-validation-bootstrap-root-review-v1.json) bind the three actual native variants; the
normal production selector stays closed. The first activation wrapper omitted
required arguments and stopped before publication. The corrected-argument
[attempt49004](tests/node-compat/foundation-zlib/validation-source-activation-attempt2-context-failure-root-results.json) then stops at a historical preparation-path
collection error; no source family or guest is published. A [context-only
amendmentf6f0e191](tests/node-compat/foundation-zlib/component-validation-preparation-context-amendment-v1/README.md) is sealed, but [review541b2779](tests/node-compat/foundation-zlib/independent-component-validation-preparation-context-source-review-v1/README.md) holds it on ZVCTX-M2:
the publisher treats an indexed-only peer as a preparation family and reads a
manifest that does not exist. The [Root origin correction](tests/node-compat/foundation-zlib/validation-source-activation-attempt2-root-origin-correction.json)
retains the original diagnosis and records this earlier observed failure; the
later relocated-bootstrap-path issue is independently confirmed. A new publisher
correction now distinguishes those family roles explicitly. The [indexed-peer successorbd66](tests/node-compat/foundation-zlib/component-validation-indexed-peer-amendment-v1/README.md) and [postseal inventory evidence5aa0](tests/node-compat/foundation-zlib/component-validation-indexed-peer-regression-evidence-v1/index.json) pass [independent source review6cbe](tests/node-compat/foundation-zlib/independent-component-validation-indexed-peer-source-review-v1/README.md): all8,904 inventory rows agree, required preparation manifests remain mandatory, and the indexed-only peer requires all five indexed files. Root [source activation-v3](tests/node-compat/foundation-zlib/validation-source-activation-v3-root-results.json) finishes raw0 and publishes family8868d212 (19 files/10,964 consumed inputs). Its [generated-family review999df5f8](tests/node-compat/foundation-zlib/independent-component-validation-v6-family-review-v1/README.md) holds on ZV6-M1: four component-harness loaders are physically absent from the native stage and omitted from the consumed manifest. The [tooling successor daa7d28a](tests/node-compat/foundation-zlib/component-validation-tooling-closure-amendment-v1/README.md) now passes [source review567c3214](tests/node-compat/foundation-zlib/independent-component-validation-tooling-closure-source-review-v1/README.md) and Root22 physical/source checks plus six syntax commands. [Activation-v4](tests/node-compat/foundation-zlib/validation-source-activation-v4-root-results.json) finishes raw0, publishing v7/d67971d0 (21 files/11,036 inputs). Its native configured root and fully sealed component-tool root are distinct. [Generated-family review178ab2d0](tests/node-compat/foundation-zlib/independent-component-validation-v7-family-review-v1/README.md) passes. The [first normal codec attempt](tests/node-compat/foundation-zlib/normal-codec-validation-attempt1-fixture-failure-root-results.json) then finishes raw1 during componentization: its snapshot uses unsupported Buffer.from(Array). No component, final result or deployed codec observation is published; the failure source recheck passes. The same input kind also occurs in constructor-refusal arguments and the ordinary-GC fixture. The [three-expression Uint8Array amendment b0ced580](tests/node-compat/foundation-zlib/component-validation-buffer-input-amendment-v1/README.md) passes12 Root host-only regression checks using explicit test doubles and [independent source reviewc277823a](tests/node-compat/foundation-zlib/independent-component-validation-buffer-input-source-review-v1/README.md). [Fresh source activation-v5](tests/node-compat/foundation-zlib/validation-source-activation-v5-root-results.json) finishes raw0 and publishes corrected v8/8af9a213 (21 files/11,107 inputs). [Generated-family review1e966afe](tests/node-compat/foundation-zlib/independent-component-validation-v8-family-review-v1/README.md) passes. [Normal validation-v2](tests/node-compat/foundation-zlib/normal-codec-validation-v2-root-results.json) finishes raw0 with283 bounded-profile codec observations over61 cases and1,544 completion artifacts. [GC validation-v1](tests/node-compat/foundation-zlib/gc-codec-validation-v1-root-results.json) finishes raw0 with three codec cases, combined-owner ordinary-GC and fresh Wasmtime checks,49 completion artifacts. Both components import nothing. [Independent normal reviewa36758db](tests/node-compat/foundation-zlib/independent-normal-codec-validation-v2-results-review-v1/README.md) and [GC review461dec9c](tests/node-compat/foundation-zlib/independent-gc-codec-validation-results-review-v1/README.md) pass. The [combined Root result review](tests/node-compat/foundation-zlib/reviewed-codec-validation-results-v1.json) retains22 Node/profile error-case differences (16 outcome/code, six additional errno-only), including11 originally unlabelled rows. The [per-case difference ledger](tests/node-compat/foundation-zlib/independent-normal-codec-validation-v2-results-review-v1/node-profile-difference-ledger.json) binds exact oracle/raw citations; no61-case Node parity is claimed. Source-coupled public VERNUM evidence does not rewrite metadata backend proof; operational admission remains closed. Separately, [actual disabled validation](tests/node-compat/foundation-zlib/disabled-selection-validation-root-results-v1.json) finishes raw0 with eight pre-componentization denials, five Buffer/stub observations and imports[]; [independent result review5b199668](tests/node-compat/foundation-zlib/independent-disabled-selection-results-review-v1/README.md) passes. This does not prove codec support or a unique cause for its generic direct-import rejection. The guest, driver, Node fixtures and native evidence remain unchanged.

The [independent timing-input review372256](tests/node-compat/foundation-classic-streams/independent-composed-timing-inputs-review-v1/README.md) passes all non-authority data checks for the unapproved timing candidate and four Root prerequisite reviews. The three issuance gates remain closed: candidate state, timingAllowed:false and NOT_ISSUED quiet window. No timing has run.

### Zlib preparation history

The following preparation record predates the current normal-v2 run; the overview above states the current gates. Failed attempts and source-only evidence remain separate from actual component results.

The [source activation-v3 receipt](tests/node-compat/foundation-zlib/validation-source-activation-v3-root-results.json) records raw exit0, new family8868d212 (19 indexed files/10,964 consumed inputs, two tool trees/22 links), and the unchanged three actual350 tuples. Root then found that the configured native stage lacks the component harness loaders (`toolchain.mjs`, `componentizer.mjs`, `profile-bundler.mjs` and `foundations/native-scalar-harness.mjs`). The input manifest also omits them. [Generated-family review999df5f8](tests/node-compat/foundation-zlib/independent-component-validation-v6-family-review-v1/README.md) confirms ZV6-M1; no known-failing component run was started. A separate, fully sealed component-tool closure is required while preserving actual native source authority. The [tooling successor daa7d28a](tests/node-compat/foundation-zlib/component-validation-tooling-closure-amendment-v1/README.md) is sealed (15 files/11,015 inputs). [Root checks](tests/node-compat/foundation-zlib/component-tool-closure-root-source-results-v1.json) pass22 physical/source checks and six syntax commands. [Independent source review567c3214](tests/node-compat/foundation-zlib/independent-component-validation-tooling-closure-source-review-v1/README.md) passes; [Fresh activation-v4](tests/node-compat/foundation-zlib/validation-source-activation-v4-root-results.json) finishes raw0 and publishes v7/d67971d0 (21 files/11,036 inputs). Generated-family review178ab passes; normal attempt1 raw1 fails at the unsupported array fixture before component publication. No deployed codec observation is available. Its configured native root remains separate from nine local tool modules, eight selected data/adapter files and package-resolution checks. The [three-input fixture amendmentb0ced580](tests/node-compat/foundation-zlib/component-validation-buffer-input-amendment-v1/README.md) is sealed and passes12 Root host-only checks using the actual frozen Buffer/zlib facades with explicit reference-hex/Node-codec test doubles. Old six constructor argument errors came from Buffer; the corrected68 zlib refusal assertions and snapshot/ordinary-GC conversions pass on the host. This is not native codec proof; [Independent source reviewc277823a](tests/node-compat/foundation-zlib/independent-component-validation-buffer-input-source-review-v1/README.md) passes; [Source activation-v5](tests/node-compat/foundation-zlib/validation-source-activation-v5-root-results.json) finishes raw0, publishing v8/8af9a213 (21 files/11,107 inputs); generated-family review is in progress. The [consumers proposal d768d712](tests/node-compat/foundation-stream-consumers/production-text-json-candidate-v1/README.md) covers only bounded text/JSON:355 proposed native inputs (five additions/two replacements),37 packet files/464 references,32 derivation and21 admission checks, no new C++ translation unit. Independent source review is underway; no live355 integration or native/guest execution has occurred. Positive Web input tests must select the existing `node:stream/web` iteration wrapper: raw global ReadableStream remains non-iterable in this profile.

The independent [disabled-build validation source](tests/node-compat/foundation-zlib/disabled-validation-candidate-v1/README.md) is prepared separately. Its own Buffer/stub smoke uses supported ArrayBuffer/Uint8Array inputs, so the normal-fixture error does not affect that source. Root15 synthetic/source assertions and [independent source review7ccc3c42](tests/node-compat/foundation-zlib/independent-disabled-validation-source-review-v1/README.md) pass. The [actual disabled run](tests/node-compat/foundation-zlib/disabled-selection-validation-root-results-v1.json) finishes raw0: eight bundler denials precede all componentization, and five Buffer/stub observations pass across three retained Jco calls, fresh Jco and fresh Wasmtime. Component154b43e4 is12,913,583 bytes with imports[] and one public scalar export;50 completion files plus one link are checked. The generic direct-native import refusal does not uniquely identify its cause. Independent result review is outstanding, with codec/backend proof and operational admission still closed. Host-only checks remain separate from this actual component evidence.

The [conditional integration56a6](tests/node-compat/foundation-zlib/integration-candidate-v1/README.md)
and [SDK syntax evidence e757/peer4ef](tests/node-compat/foundation-zlib/independent-sdk-syntax-review-v1/README.md)
remain bounded source/syntax evidence:350 proposed native paths, two syntax
commands and1,048 dependency files (2 CPP+1,046 headers), with static `MOZ_Z_*`
mapping. Old [3ff/dafaff Z350-M1](tests/node-compat/foundation-zlib/independent-native-integration-source-review-v1/README.md)
and [c65/89bc Z350-M2](tests/node-compat/foundation-zlib/independent-native-integration-v2-source-review-v1/README.md)
holds remain unchanged. The [two-identifier correction c92e](tests/node-compat/foundation-zlib/descriptor-shadow-amendment-v1/README.md)
and [producer v3 index3929e24d](tests/node-compat/foundation-zlib/native-integration-candidate-v3/README.md)
(81 files/2,146 inputs) pass [source reviewf471ec27](tests/node-compat/foundation-zlib/independent-native-integration-v3-source-review-v1/README.md).
[Root's eight source checks and isolated staging](tests/node-compat/foundation-zlib/native-integration-v3-root-stage-results.json)
pass (76544/964346f9), followed by [actual stage reviewc75f3484](tests/node-compat/foundation-zlib/independent-native-integration-v3-stage-review-v1/README.md):
869 exact copied rows =350 native+522 tooling−3 overlaps, plus the exact proposal
and isolated Git54b base. Original preparation context is retained.

The first ordinary Release normal-OFF attempt (Root62113) finishes at raw exit1.
It reaches the final108/108 copy entry and then postbuild evidence collection.
The actual CMake chain has one compiler `-o` and another for `wasm-opt`;
`codec.link_commands` counts both across the compound line and asserts. The
[Root failure receipt accf4b05](tests/node-compat/foundation-zlib/native-integration-v3-build-attempt1-failure-root-results.json)
retains11 references, recipe/launcher exit1 and completed cleanup. No standalone
CMake exit receipt was captured. The [independent failure reviewc319](tests/node-compat/foundation-zlib/independent-native-zlib-v3-build-failure-review-v1/README.md)
and [Root label clarification](tests/node-compat/foundation-zlib/native-integration-v3-build-failure-labels-root-clarification.json)
retain that distinction. Raw v3 engine62d8e6d8… remains unchanged and UNADMITTED
at9,995,287 bytes, with no metadata sidecar, freeze or backend/runtime proof.

The [v4 source d384af81](tests/node-compat/foundation-zlib/native-integration-candidate-v4/README.md)
(85 files/2,261 preparation inputs) passes [source review31d5408e](tests/node-compat/foundation-zlib/independent-native-integration-v4-source-review-v1/README.md).
[Root checks and staging](tests/node-compat/foundation-zlib/native-integration-v4-root-stage-results.json)
record nine source-check commands at0 (34385/42f14b), then plan/apply, staged
verification, factory and Git checks at0 (89971). The [independent actual-stage
review5d857788](tests/node-compat/foundation-zlib/independent-native-integration-v4-stage-review-v1/README.md)
passes:979 exact copies=350 native+632 tooling−3 overlaps,85 proposal files plus
index, ordinary Git54b clone and original-context preparation references.

The one-job ordinary Release normal-OFF retry finishes at exit0 (Root69972) from
`/tmp/starling-node-compat/zlib-source-v4`, with fresh `zlib-v4-build` and
`production-zlib-v4` namespaces and2GiB start/800MiB stop guards, without
DEBUG/OOM. The separate [four-file cache preseed47668](tests/node-compat/foundation-zlib/native-integration-v4-cache-preseed-root-results.json)
contains only three archive downloads and cbindgen; no engine, configuration,
source or old proof was copied. [Build, freeze and verification](tests/node-compat/foundation-zlib/native-integration-v4-normal-off-root-results.json)
finish at Root-observed exit0 (69972/30705/85956). Engine fb165689… is9,995,295
bytes; all1,024 frozen copies and1,022 original references rehash. The actual
350-source build records62 native units, four strict, six private and one separate
embedding command. [Independent ordinary native reviewba0451db](tests/node-compat/foundation-zlib/independent-native-zlib-v4-normal-off-review-v1/README.md) passes.
The [GC variant](tests/node-compat/foundation-zlib/native-integration-v4-gc-off-root-results.json) also finishes build/freeze/verification at exit0
(44299/71826/23840), with independent GC review pending. All ordinary frozen
copies remain unchanged after the expected shared build-cache reconfiguration.
[Independent GC review90e9e6e3](tests/node-compat/foundation-zlib/independent-native-zlib-v4-gc-off-review-v1/README.md) passes. The [disabled variant](tests/node-compat/foundation-zlib/native-integration-v4-disabled-off-root-results.json)
also finishes build/freeze/verification at exit0 (66192/28710/63712), and
[independent reviewac8d15ac](tests/node-compat/foundation-zlib/independent-native-zlib-v4-disabled-off-review-v1/README.md) confirms its61 native/five private
commands and kernel omission. All three frozen sets remain intact. Runtime backend proof
remains false/null/null; checked-in future pins stay NULL, while the external
Root authority permits validation only. No zlib guest has run. Runtime version, codec/cross-decode,
ownership/GC, components/hosts and costs remain future gates. Historical host/
ECHO vectors and syntax do not supply guest evidence. No installed `node:zlib`
support is claimed.

The initial A–E audit/template deliverables exist; the full roadmap is unfinished.

## Baseline and constraints

- StarlingMonkey HEAD: `54b3329b3ce818fd1f244e871e9c259b63667cda`.
  The profile includes working-tree changes; HEAD alone does not reproduce it.
  Accepted checkpoints record exact source inputs and artifact hashes.
- Compatibility oracle: Node.js **22.14.0**. Packaging baseline:
  ComponentizeJS **0.23.0** and Jco **1.40.0**, with the audited packaging
  corrections and exact revisions recorded in the
  [toolchain audit](docs/node-compat/toolchain-findings.md).
- Selected final standard interfaces: **WASI 0.2.10**. Pure profile components
  have no host imports; entropy and HTTP variants have explicit allowlists.
  No custom host service or Wasmtime/wasmCloud modification is permitted.
- Validated target hosts: stock Wasmtime **42.0.1** and official wasmCloud
  **2.11.0** local host. These are tested pins, not claims about every release.
- Test worlds: `starling:node-compat-test/profile@0.1.0` and the separately
  selected `starling:node-compat-http-test/profile@0.1.0` incoming-handler world.
  Application exports do not authorize custom host imports.

## Completed and verified, within the declared bounds

| Work | Completion evidence and limits |
| --- | --- |
| Architecture audit, API inventory, roadmap, initial templates | [Audit entry point](docs/node-compat/README.md), pinned Node export inventory, matrix, native/facade/stub templates and source integration findings exist. Initial templates remain labeled separately from subsequently compiled implementations. |
| Native Buffer and explicit unsupported module | Opt-in native byte processing plus a small facade, finite manifests, real module registration, aliases, selected static CommonJS lowering, canonical Buffer injection, and explicit `node:child_process` call/construction failures are implemented. Initial [allocation-r2 checkpoint](tests/node-compat/milestones/allocation-r2/README.md) records real component, ownership, initialization, and allocator evidence. Buffer remains a precisely bounded subset. |
| Capability separation and entropy | [Entropy-v1](tests/node-compat/milestones/entropy-v1/README.md) validates explicit entropy policy and standard imports. Pure components retain zero imports; random capability is selected separately. |
| Pure foundational modules | Bounded Path, EventEmitter, StringDecoder, Assert, Querystring and Util implementations have pinned manifests and real-component regressions. Their supported members and explicit refusals are recorded per module; namespace availability does not imply full module support. |
| Strict initialization and deployed failure boundaries | [v8](tests/node-compat/milestones/foundations-v8/README.md) and subsequent regressions cover formerly swallowed callback failures, initialization rejection, deployed fatal failure and handled controls. Failed deployed instances must be discarded. This does not implement Node process error events. |
| Bounded stream/web bridge | [v9](tests/node-compat/milestones/foundations-v9/README.md) validates native constructors, bounded UTF-8 codecs, iteration, selected DataView/BYOB behavior, controller guards, optional selection and both hosts. The [installed matrix supplement](tests/node-compat/foundation-stream-web/installed-matrix-v9.README.md) distinguishes tested members from mere constructor availability. Full classic-stream/consumer acceptance remains outstanding; current bounded classic gates are tracked below. |
| Protected abort listeners and combined regressions | The accepted [v10 checkpoint](tests/node-compat/milestones/foundations-v10/README.md) Events m0.10 adds bounded `addAbortListener`, native protected dispatch and receiver guards. Core remains m0.8; stream/web remains m0.9. This checkpoint contains 3,445 independently byte-verified evidence files, 33 complete reports, 304 native source inputs and four Release engine receipts. |
| v10 focused and full runtime gates | [Focused report](tests/node-compat/foundation-add-abort/production-native-m0.10/README.md) records 29 Node-derived groups, namespace/default/alias/CommonJS behavior, initializer failures, fatal/discard and handled reuse, Events-OFF admission, and valid native byte-kernel GC roundtrips. Full core/allocator, earlier foundations, stream/web and 24 strict-callback component regressions pass. |
| v10 HTTP on both target hosts | [HTTP-v10 evidence](tests/node-compat/foundations/http-v10.md) validates the same component bytes on both hosts, three requests each and clean shutdown. Its six standard 0.2.10 imports cover HTTP types, IO error/poll/streams, random and a type-only monotonic-clock dependency with no callable clock function. No other network/filesystem/process capability is inferred. |
| Earlier public allocation checkpoint: foundations-v11 | [v11](tests/node-compat/milestones/foundations-v11/README.md) accepts bounded m0.11 allocation after release, GC, focused and both-host HTTP gates. Its 1,746 copied evidence records and 304-input source archive remain unchanged. |
| Latest accepted checkpoint: foundations-v12 | [Acceptance](tests/node-compat/foundation-scheduler/production-acceptance-v12/README.md) covers the private scheduler layer, three production engines, separate diagnostic Release/GC, fresh eight-stage replay, allocator/focused gates and both-host HTTP. Root independently verifies 4,150 indexed files, 4,148 copied records, 212 external references and the unchanged v11 parent. Public API versions are unchanged. |
| Performance measurements with counterexamples retained | Matched Jco-adapter and private allocation-pair experiments are documented, including slower results, larger artifacts and higher memory observations. Measurements do not establish a universal native-code advantage. See [allocation work](tests/node-compat/foundation-alloc-unsafe/README.md) and the measured limitations below. |

Older accepted checkpoints and failed attempts remain unchanged. Later results
supersede only the explicitly identified claims; they do not erase prior evidence.

## Latest completed milestone: foundations-v12

**Accepted, bounded:** the [acceptance receipt](tests/node-compat/foundation-scheduler/production-acceptance-v12/acceptance-receipt.json)
is the current authority for the [frozen archive](tests/node-compat/milestones/foundations-v12/README.md).
The archive's pending labels preserve its earlier construction state; this
separate acceptance record advances status without rewriting evidence.

Root independently rehashed all **4,150 indexed files**, **4,148 copied records**
(163,492,404 bytes), **212 external references**, **4,881 input mappings** and
the unchanged **1,746-record v11 parent**. The current native inventory is 306:
299 v11 inputs unchanged, five changed and two queue files added, with three
external embedding inputs separate. Three production engines and two diagnostic
engines have distinct receipts and validation scopes.

Fresh production/control validation covers **61 components**: 60 current and one
historical delegated control. The **20 private diagnostic components** remain
separate. All eight normal-OFF stages pass with no earlier result reuse;
allocator GC, focused OFF/RuntimeOnly/GC and the safe getter observation pass
their bounded checks. Getter parity remains **false**. The same HTTP component
passes three requests per stock host and clean exit0, with exactly six selected
standard WASI 0.2.10 interfaces and a type-only clock dependency.

No public module version advanced: core/Buffer remains m0.11, Events m0.10 and
stream/web m0.9. Private ticks default OFF. Reset, ALS, request isolation,
first-ever classic startup, isolated VM-root proof and a performance advantage
remain unproved. The overall roadmap is unfinished.

## Previous public allocation milestone: foundations-v11

**Accepted, bounded:** [checkpoint](tests/node-compat/milestones/foundations-v11/README.md),
[full results](tests/node-compat/milestones/foundations-v11/results.json), and
[independent acceptance receipt](tests/node-compat/foundation-alloc-unsafe/production-adoption-m0.11/v11-acceptance-receipt.json).
Root independently rehashed all **1,746 copied files** (76,656,667 bytes), including
**33 full reports**, after the producer verified the exact plan and every copy.
The parent v10 archive remains unchanged. This completes the m0.11 milestone;
the full roadmap remains active.

The reviewed [11-file integration packet](tests/node-compat/foundation-alloc-unsafe/production-candidate-m0.11-v2/README.md)
was applied coherently. Four of 304 native inputs changed; the other 300,
protected abort-listener integration, CMake, build recipe, embedding and native
Buffer kernel remain unchanged. `allocUnsafe` now allocates through captured
Uint8Array directly after the same primary validation. It retains fresh zeroed
storage, no pool, a 16 MiB limit, truncation and the declared backing/view/error
contract. It adds no C++ allocator kernel, ownership transfer, host import or
supported Buffer method. The proposal packet's earlier UNAPPLIED label is
historical; the [adoption receipt](tests/node-compat/foundation-alloc-unsafe/production-adoption-m0.11/source-receipt.json)
records its actual application.

The [three-build receipt](tests/node-compat/foundation-alloc-unsafe/production-adoption-m0.11/native-build-results.json)
records exact source/configuration, compile commands and dependency evidence:

| v11 Release engine | SHA-256 |
| --- | --- |
| Entropy OFF | `1eb2b55a391e2bc83478fefee124a6f282cfed148cc0623754125f6c5e9b0458` |
| RuntimeOnly | `2e3731ce248be1d8ede0f5672dd87b48fb1731dfddb045bfaabaeea02534a36d` |
| Existing GC-stress instrumentation, entropy OFF | `b79fd7dba35288e233ec07134e490ddd2ae51f212a2be506ecd70a728f5e6bc4` |

[Source admission](tests/node-compat/foundation-alloc-unsafe/production-adoption-m0.11/source-admission-results.json)
passes eight generator checks, 328 module-admission checks, schema checks
including 19 malformed-manifest rejections, and the bundler contract. The
[eight-job release batch](tests/node-compat/foundation-alloc-unsafe/production-adoption-m0.11/release-gate-results.json)
passes core, allocator, stream/web, six earlier foundations and four strict
callback groups. Five earlier same-engine successes were byte-verified and
reused; three strict suites passed fresh retries.

The [allocator GC gate](tests/node-compat/foundation-alloc-unsafe/installed/gc-v11-results.json)
passes three retained Jco calls and fresh Wasmtime with eight valid native hex
roundtrips per call, checking brands, owned backing, shared views, zeroed/empty
allocation and snapshot state. The
[focused receipt](tests/node-compat/foundation-add-abort/production-native-m0.11/evidence-receipt.json)
covers four reports and 19 application components: OFF and RuntimeOnly each
pass 29 groups, with separate protected-owner GC and callback-return observation.
Eleven components import nothing; eight import only `wasi:random/random@0.2.10`.
Known getter parity remains **false** and GC still proves combined owners only.

[HTTP-v11](tests/node-compat/foundations/http-v11.md) passes three requests on each
stock target host with the same component
`634ce53e1ce976703d3df9b1fb869da61fbdb823cee56c6f9fd6e235e26c4b4a`,
63,635,975 bytes including test corpora. Both hosts stop with code 0 and counters
`[1,1,1]`; this proves neither same-instance reuse nor request isolation. The six
selected standard WASI 0.2.10 imports and type-only clock remain unchanged.
This is a correctness artifact, not a product-size comparison.

Failure history is preserved: the new allocator host runner initially omitted
`pathToFileURL`, and a later strict-runtime packaging attempt exhausted local
disk space. The corrected harness and fresh runtime retries pass; incomplete
attempts are not counted as passes. Byte/metadata-verified output compression
and the [duplicate-artifact recovery receipt](tests/node-compat/foundation-alloc-unsafe/production-adoption-m0.11/cow-bootstrap-results.json)
retain the evidence. Most space had recovered before that operation; its
35,856,384-byte observed delta is nonexclusive. Storage observations are not
guest memory or performance results.

Private paired allocation measurements remain contextual: candidate peak RSS
was higher in **29/30** comparisons, capacity higher in **4/30**, and the minimal
snapshot **8,513 bytes larger**. Seven slower controls, five control reversals
and only two independent processes per arm limit interpretation. No private
throughput result is transferred to this production engine, and no memory,
size or whole-application advantage is claimed.

## Current work in progress

The [classic342 source layer](tests/node-compat/foundation-classic-streams/production-adoption-v1/README.md)
is applied with a default-OFF flag. The coherent41-path adoption preserves the
306-input branch and existing embedding/standard-interface contracts. Root's
source checks and independent reviews remain recorded in the adoption ledger;
the original null-pin proposals stay unchanged.

All four actual Release variants are built, frozen and independently reviewed:
normal-OFF (`b8279ee1…`), RuntimeOnly (`1a3f4628…`), GC-OFF
(`f9f48f4f…`) and classic-disabled OFF (`27e625a7…`). Each has405 frozen
copies, native342/ext3 and native61/strict4 observations. CLASSIC is private to
the five profile TUs when enabled and absent in the disabled control. Each has
a separate AFTER-only embedding9d command witness. Normal-OFF was frozen before shared
project reconfiguration for GC. The [native build receipt](tests/node-compat/foundation-classic-streams/production-adoption-v1/native-build-results.json)
and [Root authority](tests/node-compat/foundation-classic-streams/production-adoption-v1/root-pin-review-receipt.json)
bind all four tuples. The disabled control passes eight ESM/CommonJS admission
denials without componentization; it is an actual fourth variant, not a projected
older receipt.

Three actual classic component suites finish with raw terminal0 and independent
evidence reviews:

| Suite | Published output hashes | Final component imports | Review |
| --- | --- | --- | --- |
| Normal-OFF, activated runtime-v2 | 90 | Five components, all imports[] | [Independent OFF review](tests/node-compat/foundation-classic-streams/independent-normal-off-component-review-v1/README.md) |
| RuntimeOnly, activated runtime-v3 | 91 | Five components, only `wasi:random/random@0.2.10` | [Independent Runtime/GC review](tests/node-compat/foundation-classic-streams/independent-runtime-gc-component-review-v1/README.md) |
| GC-OFF, activated runtime-v3 | 90 | Five components, all imports[] | [Independent Runtime/GC review](tests/node-compat/foundation-classic-streams/independent-runtime-gc-component-review-v1/README.md) |

Each suite covers19 Node22 ordinary groups,48 deferred call/new checks,
17 overload refusals, three buffered-state limits,65 expected initializer
failures, three retained main calls and fresh Jco/Wasmtime observations.
Separate deployed cases cover one fatal/discard and two caught/handled controls;
the caught initializer component is preserved. Snapshot identity is true only
on first/fresh calls and null on retained calls two/three, whose prior default
is777. The Jco fatal catcher exits0; Wasmtime's generic134 trap does not identify
the originating error. Only successful instances are reused. GC-OFF additionally
exercises eight valid native hex rounds per call with combined stream/listener/
decoder/Buffer owners; this does not isolate a VM queue or prototype key.

Earlier failures remain separate and preserved. Initial ESM `require()` placement
failed host bundling before componentization; the [explicit CJS amendment](tests/node-compat/foundation-classic-streams/harness-cjs-contract-amendment-v1/README.md)
retains the bundler contract. Runtime-v2 then hit exclusive creation of a shared
generated interface declaration; the [same-run identical-declaration amendment](tests/node-compat/foundation-classic-streams/shared-transpile-interface-amendment-v1/README.md)
allows only already-tracked byte-identical direct `interfaces/*.d.ts` reuse.
A collector's incorrect retained snapshot-identity assumption and the independent
reader's initial embedding ThinLTO assumption are preserved observer corrections,
not native or guest failures.

The fresh baseline replay-v3 now finishes **all eight stages with raw0** and
[independent result verification](tests/node-compat/foundation-classic-streams/independent-regression-v3-results-review-v1/README.md):
346 output files,40 final components (39 current and one fresh historical m0.8
control), all with zero imports. Historical controls and counterexamples remain
explicit. Replay-v1 first stopped before any child
because its owned parent directory was absent, then stopped at an absent copied
Path Node-oracle subprocess entry. The [registrar/Path amendment](tests/node-compat/foundation-classic-streams/registrar-ancestry-oracle-amendment-v1/README.md)
keeps old Node oracles unchanged, binds exact19eef→2848 Classic registrar ancestry,
and tests safe Node subprocesses into fresh output without old writes.
The new replay-v2 again passes core/allocator/stream-web and Path fresh, but stops
at Events' exact old strict-policy tag before that component is built.
Its partial raw0 stages are not a complete eight-stage pass or reusable acceptance.
The [five-tag/GC-schema amendment](tests/node-compat/foundation-classic-streams/exact-policy-tag-amendment-v1/README.md)
uses exact full Classic lineage equality and actual GC pin/config fields.
It audits all64 bodies and passes124 data-only checks.
[Replay producer-v3](tests/node-compat/foundation-classic-streams/replay-activation-candidate-v3/README.md)
and its independent source review pass: both amendments are mandatory,
57/64 inherited bodies remain identical, and seven host harness bodies change.
Guest/facade/oracle semantics and all four native artifacts are unchanged.
Root repeats124 tag/pin data checks and14 source groups, then publishes the
[new replay-v3 source family](tests/node-compat/foundation-classic-streams/production-regression-activated-v3/README.md)
with raw0:82 records,2,055 root/2,054 capability inputs and actual runtime-v3
delegation. The [independent generated-source review](tests/node-compat/foundation-classic-streams/independent-activated-regression-review-v3/README.md)
passes, and three actual native-mode admissions plus Release OFF preflight finish
raw0. The [fresh full eight-stage replay-v3](tests/node-compat/foundation-classic-streams/production-adoption-v1/release-replay-v3-root-results.json)
finishes terminal0 with all child exits0, six optional modules, complete input
rechecks and a final report seal. No earlier partial pass was reused.
The separate [allocator Release-GC](tests/node-compat/foundation-classic-streams/production-adoption-v1/allocator-gc-v3-root-results.json)
and focused [OFF](tests/node-compat/foundation-classic-streams/production-adoption-v1/focused-off-v3-root-results.json)/[RuntimeOnly](tests/node-compat/foundation-classic-streams/production-adoption-v1/focused-runtime-v3-root-results.json)
gates finish raw0. Each focused ordinary gate covers29 Node public groups,
eight expected initializer failures and five fatal/discard cases. The separate [focused combined-owner GC](tests/node-compat/foundation-classic-streams/production-adoption-v1/focused-gc-v3-root-results.json)
and [getter counterexample observation](tests/node-compat/foundation-classic-streams/production-adoption-v1/getter-v3-root-results.json)
also finish raw0. Getter parity remains false: Node1/1/0 versus Jco/Wasmtime0/0/0;
GC does not isolate individual root owners. [Independent followon verification](tests/node-compat/foundation-classic-streams/independent-followon-result-review-v1/README.md)
passes all five gates, deriving20 final components (allocator1, focused OFF8,
Runtime8, focused GC2, getter1). All OFF/GC imports are empty; Runtime imports
only standard random0.2.10. The actual source82/2,055/2,054, tool trees and all
four405-copy native freezes are rechecked without new guest execution.

The [combined HTTP proposal](tests/node-compat/foundation-classic-streams/classic-http-candidate-v1/README.md)
has63 sealed files/7,518 source inputs, all eight LIVE WIT/adapter inputs,
26 Root pure checks and an actual-entry host bundle with exactly17 native/WASI
imports. [Independent source review](tests/node-compat/foundation-classic-streams/independent-classic-http-source-review-v1/README.md)
passes. It adds ordinary classic19 to the unchanged baseline schema5/protected29
through a scoped wrapper of the real WASI handler. Root's prepare and packaging
jobs now finish raw0. The actual component is64,057,853 bytes,
`25eb1a1c7343519318ffc5a4519bc1dbd4cc1c23755a6b8fcc3bab479ffb6c7d`,
with the same `2fab5aab…` bundle, exact six standard0.2.10 imports, type-only
clock and no Preview1 import. [Independent pre-host review](tests/node-compat/foundation-classic-streams/independent-http-prehost-verification-v1/README.md)
passes, and a separate Root-reviewed external phase binds these exact original
paths and bytes. The first Wasmtime attempt fails after receiving HTTP because
Root enabled an optional historical intrinsic assertion whose diagnostic fields
this fixture does not export. Its raw1/logs/partial output are preserved in the
[attempt receipt](tests/node-compat/foundation-classic-streams/production-adoption-v1/http-wasmtime-attempt1-root-results.json);
no pass is counted for that attempt. A [fresh output wrapper](tests/node-compat/foundation-classic-streams/http-host-output-retry-candidate-v1/README.md)
passes13 Root source checks and [independent review](tests/node-compat/foundation-classic-streams/independent-http-host-output-retry-review-v1/README.md).
The [Wasmtime-v2 retry](tests/node-compat/foundation-classic-streams/production-adoption-v1/http-wasmtime-v2-root-results.json)
passes three HTTP200 responses and clean owned-host exit0. The unchanged wasmCloud wrapper passes three HTTP200 responses and clean
owned-host exit0 with the same component; its [Root capture](tests/node-compat/foundation-classic-streams/production-adoption-v1/http-wash-root-results.json)
records terminal0. The [final combined-host audit](tests/node-compat/foundation-classic-streams/production-adoption-v1/http-combined-root-results.json)
also finishes raw0, retaining all six combined responses and18 audited artifacts.
Both counters are[1,1,1], proving neither reuse nor isolation. The
[independent final evidence review](tests/node-compat/foundation-classic-streams/independent-combined-http-results-review-v1/README.md)
passes8,067 declared paths, all six raw-response assertion sets and18 artifact
records, including current native/tool/source seals and both official host
binaries/configurations. The local phase pin stays null and
sealed. This transport does
not implement `node:http`, and this corpus-heavy artifact is not a size comparison.

The [measurement extension proposal](tests/node-compat/foundation-classic-streams/measurement-extension-candidate-v1/README.md)
passes [independent source review and SDK syntax](tests/node-compat/foundation-classic-streams/independent-measurement-extension-review-v1/README.md)
with1,022 actual header dependencies; it has no admitted benchmark artifact or
result. The old-generation diagnostic producer/freezer/admission source packet has43 sealed
files/666 inputs, independent source review and72 Python/19 Node Root checks;
that old producer has no native-action result. A new common seven-scenario/three-control Node22
workload captures exact checksums and bounded traces at1/16 iterations. All
output byte/text/value assertions and checksums match, but14 ordinary host-model
trace comparisons differ: synchronous HWM-boundary write returns, event order
and object callback encodings remain counterexamples. Two failed host attempts
were ordinary assertion-diff formatting failures and are preserved; no guest or
fault-injection work ran. Bounded reporting retains the differences without
changing the canonical factory or stock scheduler. The sealed [workload source](tests/node-compat/foundation-classic-streams/measurement-workload-candidate-v1/README.md)
has58 files/5,297 inputs, actual native/canonical/stock source graphs and null
future pins. Both original canonical and stock providers retain14 trace gaps;
three controls match. Its independent source review is running.
The sealed [minimal reproduction source](tests/node-compat/foundation-classic-streams/stream-trace-regression-candidate-v1/README.md)
has15 files/6,015 inputs and eight Node/model cases; Root repeats13 source
checks and independent source review passes. Its [actual component result](tests/node-compat/foundation-classic-streams/production-adoption-v1/stream-trace-component-root-results.json)
finishes raw0 as a completed observation with Node parity false. The unchanged
b827 engine produces component f896b7c2… (12,933,484 bytes), imports[], three
retained calls and fresh Jco/Wasmtime with the same four Node differences:
synchronous64-byte writes at HWM64/63 and the two source-PassThrough event traces.
[Independent verification](tests/node-compat/foundation-classic-streams/independent-stream-trace-component-review-v1/README.md)
confirms the raw public Wasmtime result and completion chain. The [11-case successor](tests/node-compat/foundation-classic-streams/stream-trace-regression-candidate-v2/README.md)
adds ordinary one-argument/callback/UTF8 object-mode encoding probes with typed
undefined/null/string outputs. Its43 files/6,062 inputs and original eight
Node/model records pass Root rehashes;14 Root source checks and independent
delta review pass. Its [actual11-case result](tests/node-compat/foundation-classic-streams/production-adoption-v1/stream-trace-component-v2-root-results.json)
finishes raw0 as an observation with Node parity false and six differences:
the four original byte/event gaps plus one-argument/callback object encodings.
Guest hooks receive UTF8 for both, while Node receives undefined/null. The
explicit UTF8 control matches; payload identity and hook/user callback counts
match. Three retained calls and fresh Jco/Wasmtime agree, with imports[]. The
original eight actual records remain exact. [Independent result verification](tests/node-compat/foundation-classic-streams/independent-stream-trace-component-review-v2/README.md)
passes all11 observations, public binary/core/glue, raw Wasmtime decoding and
the source/native/output completion seals without another guest run.
The separate [semantic fix proposal](tests/node-compat/foundation-classic-streams/trace-semantics-candidate-v1/README.md)
has65 files/488 inputs and five transformed-writable edits, producing three
proposed generated-source afterimages. Node-host tests match20 workload cases,
eight minimal cases,14 boundary cases and the inherited19-case corpus. Ablation
shows the post-write return correction also restores the observed minimal event
order; an unnecessary broader scheduling experiment is preserved and excluded.
Object-mode encoding is the other model-verified correction. [Independent source review](tests/node-compat/foundation-classic-streams/independent-trace-semantics-source-review-v1/README.md)
confirms the three-file reconstruction and stored20+8+14 data; the legacy19
observed array was not retained, so only its owner assertion/reported equality
is corroborated until fresh actual gates. The first two workload Node failure
sources/facts are preserved, but their full raw stderr remains tool-history-only.
Original-workspace native342 and the four old pins remain unchanged. These are
source/model results, not installed-guest fix
proof. The [integration source proposal](tests/node-compat/foundation-classic-streams/trace-integration-candidate-v1/README.md)
has159 files/1,175 inputs, a new exact342 policy (339 unchanged+3 corrected),
recipe/admission/tooling afterimages and null future pins. Strict/protected
boundary tags and m0.12 exports remain exact. Root's read/hash/AST verifier
finishes raw0 and [independent source review](tests/node-compat/foundation-classic-streams/independent-trace-integration-source-review-v1/README.md)
passes. The [isolated checkout receipt](tests/node-compat/foundation-classic-streams/production-adoption-v1/trace-source-checkout-root-results.json)
records a detached54b3329 base plus exact339+3 native and two changed tooling
files, with the selector unchanged. It passes the original proposal's1175-input
preparation check and the separate checkout's342 native/92 tooling/copied159
checks. The original workspace and four old freezes stay unchanged. The first
new normal-OFF Release build finishes107 steps/raw0 and its freezer finishes
raw0, with474 actual copies (native342/external3). The
[Root native receipt](tests/node-compat/foundation-classic-streams/production-adoption-v1/trace-normal-off-native-root-results.json)
records engine d54446dc… (9,973,355 bytes), metadata bfaec95e… and freeze1f2a49ac….
All four corrected builds/freezes now finish raw0: OFF107 steps, RuntimeOnly107,
disabled-control107 and incremental GC16, with474 actual copies each.
[OFF](tests/node-compat/foundation-classic-streams/independent-trace-native-normal-off-review-v1/README.md),
[RuntimeOnly](tests/node-compat/foundation-classic-streams/independent-trace-native-runtime-review-v1/README.md)
and [disabled-control](tests/node-compat/foundation-classic-streams/independent-trace-native-disabled-review-v1/README.md)
artifact reviews pass, as does the [GC review](tests/node-compat/foundation-classic-streams/independent-trace-native-gc-review-v1/README.md). The OFF freeze precedes GC
reconfiguration. One-job/2GiB start/800MiB stop guards remain in force.
The four-label exporter remains unreviewed history. Root's separate reviewed
pin document is `182e8b72…fab5eb`; its review receipt is `ce88ac34…a8be0`.
[Runtime activation](tests/node-compat/foundation-classic-streams/production-trace-runtime-activated-v1/README.md)
finishes raw0, producing26 files and6,414 consumed inputs/22 tool links; index
`e1f87cd6…175b78` passes [independent family review](tests/node-compat/foundation-classic-streams/independent-trace-runtime-family-review-v1/README.md).
The [four runtime-family preflights](tests/node-compat/foundation-classic-streams/production-adoption-v1/trace-runtime-source-and-preflights-root-results.json)
and separately reviewed corrected Node11 gate pass. The three fresh corrected
classic suites and disabled admission control now pass the
[independent all-four review](tests/node-compat/foundation-classic-streams/independent-corrected-classic-results-review-v1/README.md)
(`8c3da4a2…41e8cc`): 15 classic component occurrences plus the separate Node11
component, with exact OFF/GC empty and RuntimeOnly random-only imports. It
rechecks 26/6,414 source/input files, 365 source mappings, four 474-file freezes,
15 static WIT audits and 12 core/component/glue relationships. Each enabled suite
retains 19/48/17/3/65 checks, three retained calls, fresh Jco/Wasmtime, snapshot
identity and default-before 65536 then 777, fatal-discard and two clean controls.
Only parsed main/clean Wasmtime success observations and stdout hashes remain;
raw stdout cannot be independently decoded. Fatal raw streams are retained and
generic traps do not identify origin; GC proves combined owners only.

The diagnostic-v2 metadata-import failure remains preserved. Diagnostic-v3 ON/OFF
native checks and both independent reviews now pass (109 steps/525 copies each).
The fresh persistence-enabled full20+14 run66794 now passes Root6218 and
independent0f59 review:105 full Node-exact returned records,632 completion files
and21 independently decoded raw Wasmtime streams. The original90660 failure
still has an unknown timed-out case and unretained Jco data. Separate case5
equality is not reused. Measurement source4b6/96bc and its reviewed M1 successor
now lead to actual source family1b801 with reviewed diagnostic pair and both
preflights. Family review4e986 passes; four-arm component correctness is running
and no timing is authorized.

Corrected replay sourcea08/peer8529 and the explicit-Wasmtime preflight retry
pass. The fresh eight-stage replay23947 and five follow-ons now pass independent
reviews6a67/d116:40+20 component occurrences, with separately identified historical
controls and raw-output availability limits. Only RuntimeOnly follow-ons import
random@0.2.10. The original Root environment failure, old-source passes and all
six actual trace counterexamples remain preserved. Corrected HTTP packaging71459
now finishes raw0 after a preserved missing-tool attempt with unknown outer
terminal status; its64,058,731-byte component has exact six0.2.10 interfaces and
type-only clock. Both-host HTTP, cost/artifact/archive and Root acceptance remain
open. Accepted checkpoint
remains bounded v12, with no full Node or performance claim.

The following records retain the completed v12 execution history; their passes
belong to those exact306-input engines, not the changed classic342 artifacts.

### Completed execution history for v12

The [fresh link1 Release build](tests/node-compat/foundation-scheduler/link1-execution-v1/release-native-results.json)
completes all 109 compile/link/copy steps and publishes engine
`46fc6588397bc7ca332369600fe3d561897001d79611b25d7dca1d9b462a373b`
(9,764,917 bytes). The [actual freeze/full preflight](tests/node-compat/foundation-scheduler/link1-execution-v1/release-freeze-results.json)
validates 345 copies, native306 + diagnostic2, native61/strict4/queue1 commands,
separate parent1+1 commands, and all four final-link witnesses. The original
normal configuration was frozen before any GC reconfiguration.

The [new ordinary component result](tests/node-compat/foundation-scheduler/link1-execution-v1/ordinary-release-results.json)
passes ten packaged artifacts, five expected initialization failures, three
paired successful controls and three fresh fatal/discard observations. Main
runs three retained Jco calls and fresh Wasmtime. All ten components emit zero
imports. The [32-input driver](tests/node-compat/foundation-scheduler/diagnostic-link1-driver-v2/README.md)
adds the exact live adapter to the pre/post seal and retains the full corpus;
56 host checks pass. [Independent verification](tests/node-compat/foundation-scheduler/link1-ordinary-release-verification-v1/README.md)
rehashes 494 canonical files/495 path references and confirms the recorded scope.
This is ordinary Release, without forced-GC proof or production acceptance.

The [separate Release-GC build](tests/node-compat/foundation-scheduler/link1-execution-v1/gc-native-results.json)
completes 16 incremental compile/link/copy steps and publishes
`949d24f653903923bb7055c441b7a5131922a787d94465f014d62a8d680b802b`
(9,766,466 bytes). Its [freeze/full preflight](tests/node-compat/foundation-scheduler/link1-execution-v1/gc-freeze-results.json)
passes the same 345-copy and command/witness checks, including the actual Buffer
GC macro. The [actual GC component result](tests/node-compat/foundation-scheduler/link1-execution-v1/gc-component-results.json)
now passes the complete ten-artifact/five-initializer/three-control/three-fatal
protocol, three retained main Jco calls and fresh Wasmtime, with zero imports.
All 32 inputs and the live adapter match before/after. Eight valid native hex
operations run while inline callback/object/unregistered-Symbol values are
pending, with actual kernel GC instrumentation enabled. Application strong
co-owners are removed; VM temporary retention is **uninstrumented**. This is not
isolated VM-root proof, reset/reuse support or production acceptance.
[Independent GC verification](tests/node-compat/foundation-scheduler/link1-gc-verification-v1/README.md)
confirms the frozen sources/configuration, all 32 inputs, ten zero-import
components and the actual GC flags without rerunning the guest.

The private tick scheduler is **source-applied** through the reviewed seven-file
[native layer and recipe](tests/node-compat/foundation-scheduler/production-adoption-v1/source-adoption-receipt.json).
All 306 intended native inputs match the layered policy. The existing traced
TaskQueue owns the bounded FIFO; the feature defaults OFF and adds no public
Node export or host capability. The
[finite admission adoption](tests/node-compat/foundation-scheduler/production-adoption-v1/admission-adoption-receipt.json)
passes **110** independent checks, including optional stream/web OFF and rejection
of diagnostic engines. Seven historical receipt selections remain unchanged.
These source/admission checks are separate from runtime proof.

The [production launcher review](tests/node-compat/foundation-scheduler/production-execution-v1/launcher-root-review.json)
checks its exact source, all eight unchanged lifecycle helpers, recipe869 and
all 306 current native inputs. Independent source review agrees. The actual
normal-OFF build completes all **107** steps with exit0 and engine
`6e5bc2ca3b3e3f7dccaa887003bc292e8a7abfbc5260691d1cda0114640dae84`
(9,759,293 bytes). The [native receipt](tests/node-compat/foundation-scheduler/production-execution-v1/normal-off-native-results.json)
and [actual freeze](tests/node-compat/foundation-scheduler/production-execution-v1/normal-off-freeze-results.json)
record 335 copied files, native306/external3, native61/strict4 and a separate
actual embedding command. Its raw Ninja evidence is **after-build only**;
no before-build witness is invented. The normal configuration is frozen before
GC reconfiguration. The freezer/exporter packet passes **85** fresh Root host
checks and independent source review. Unreviewed exports cannot activate
consumers. [Independent normal-OFF verification](tests/node-compat/foundation-scheduler/production-normal-off-verification-v1/README.md)
passes and the real finite selector admits eight manifests against frozen
sources. The separate RuntimeOnly build also completes **107** steps with exit0,
engine `479821f8eefbc6aacbfe9df8538c5ee0a8745e530a474ecee8cb34251c0a1943`
(9,766,342 bytes), and its [335-file freeze](tests/node-compat/foundation-scheduler/production-execution-v1/normal-runtime-freeze-results.json)
passes. [Independent RuntimeOnly verification](tests/node-compat/foundation-scheduler/production-normal-runtime-verification-v1/README.md)
confirms both entropy macros in all 62 native/embedding commands. GC-OFF
completes **16 incremental steps** with exit0, after the launcher validates the
normal-OFF freeze before reconfiguration. Its engine
`502320aaed8c78ace92d8d8d782a355307868beee707b22e03c96f67cd42c833`
(9,760,842 bytes) has a passing [335-file freeze](tests/node-compat/foundation-scheduler/production-execution-v1/gc-off-freeze-results.json)
and actual kernel GC flags. [Independent GC verification](tests/node-compat/foundation-scheduler/production-gc-off-verification-v1/README.md)
passes, including the preserved normal-OFF prerequisite freeze. All three native
jobs are terminal. Root's separate [actual pin review](tests/node-compat/foundation-scheduler/production-pin-review-v1/README.md)
rehashes all 335 copies per variant and all three independent proof packets.
The original candidate export stays **unreviewed** and unchanged. New common-v5,
OFF-v3 and release-v3 revisions now bind the reviewed data and sealed parent
indices, with 667/755/1,442 runtime inputs respectively. Root freshly passes
**227** host/source checks, rehashes all three indices and the fixed 778-input
capability closure, and passes the complete release read-only preflight.
Independent activation review and all five separate read-only admissions pass.
The actual serial eight-stage normal-OFF replay is now running with fresh
outputs and no prior runtime pass reuse. Sealed null-pin predecessors remain
unchanged. GC/focused/HTTP runtime gates and acceptance remain outstanding.

The [full eight-stage batch](tests/node-compat/foundation-scheduler/production-runtime-v1/off-release-root-results.json)
now passes with exit0: core Buffer/explicit-stub behavior, allocator, installed
stream/web, all six foundational modules and all four strict-callback suites.
Every report/completion/log hash matches and no earlier runtime pass is reused.
The [separate allocator GC gate](tests/node-compat/foundation-scheduler/production-runtime-v1/allocator-gc-root-results.json)
also passes on GC-OFF: three retained calls and fresh Wasmtime around eight
valid native hex roundtrips, with zero imports and post-run source checks.
Focused OFF and RuntimeOnly each pass 29 groups, eight initializer failures,
five fresh fatal cases and nine retained successful calls plus fresh Wasmtime
controls. OFF imports nothing; RuntimeOnly imports exactly
`wasi:random/random@0.2.10`. Focused GC also passes three retained calls/fresh
Wasmtime with eight native roundtrips; ownership remains **combined**, not
prototype-only Symbol proof. The safe getter observation reconfirms Node
`1/1/0` versus native `0/0/0`, with `nodeCompatibilityPassed:false`.

The [independent eight-stage verification](tests/node-compat/foundation-scheduler/production-runtime-verification-v1/README.md)
validates all reports/seals and 40 zero-import application components: **39
current production and one freshly packaged historical delegated control**.
The [separate focused/GC/getter verification](tests/node-compat/foundation-scheduler/production-focused-runtime-verification-v1/README.md)
passes: 20 current components, eight importing only standard random and twelve
importing nothing. Getter parity remains explicitly false.

HTTP packaging and [independent pre-host review](tests/node-compat/foundation-scheduler/production-http-prehost-verification-v1/README.md)
pass. Root [reviewed the actual component phase pin](tests/node-compat/foundation-scheduler/production-http-phase-review-v1/README.md)
and sealed the final capability index without changing any of the 778 prepack
inputs. Component `ccc87ae3f9a00195ae243fa1077a07f9cd68e5ad3a8220708400187eee7a2ba6`
(63,639,194 bytes, including test corpora) now passes three requests on each
stock host, both exiting0. The [combined audit](tests/node-compat/foundation-scheduler/production-runtime-v1/http-final-root-results.json)
passes with exactly six standard WASI 0.2.10 imports, only incoming-handler
exported, type-only clock and no callable clock import. Both counters are
`[1,1,1]`; reuse and request isolation remain unproved. Independent post-host
verification and Root archive acceptance subsequently pass. These passes do not complete
the roadmap or establish reset/reuse/ALS or a performance advantage.

The [third ordinary Release attempt](tests/node-compat/foundation-scheduler/production-adoption-v1/release-v4-build-results.json)
completed ten incremental steps from the verified partial project, publishing
engine `a49c920c83a5deb144c960f3d745f66b57754415546346c089b9f182d4b67f6b`
(9,764,903 bytes) and its full sidecar. The executed v2 freezer verifies **337**
source/configuration/dependency copies. Native61 compile commands come from the
database; one embedding and one diagnostic command come from raw Ninja.
Before/after configuration and parent-command bytes are identical.

The [ordinary real-component gate](tests/node-compat/foundation-scheduler/production-adoption-v1/ordinary-release-results.json)
passes **ten packaged components**, including three deliberately fatal deployed
fixtures, **five expected initialization failures**, **three paired successful
controls** and **three fresh-instance fatal-boundary observations**. Main runs
three retained Jco calls and fresh Wasmtime; all ten components emit **zero
imports**. Initial ESM, task/export and Promise-job ordering, 5,000 FIFO callbacks,
argument/queue/work limits, subsequent configured classic evaluation, INIT
completion before content and final binding pass their stated checks. The
[independent 462-file verification](tests/node-compat/foundation-scheduler/ordinary-release-verification-v1/README.md)
passes. This engine has `gcStress=false`: eight ordinary native hex operations
do not prove forced-GC ownership. First-ever classic startup, INIT tick priority,
original fatal-cause identity, actual reset and request isolation are not proved.
No post-fatal instance reuse occurs.

The [driver packet](tests/node-compat/foundation-scheduler/diagnostic-candidate-v1/README.md)
retains 27 indexed files and 24 consumed hashes, checked before and after the
run. Its historical `UNEXECUTED` filename is not its current execution status.
Its earlier adapter-seal limitation is historical; the new 32-input driver and
both diagnostic gates above supersede it. Finite production OFF/RuntimeOnly/GC
builds, all prior public regressions and both-host HTTP remain required before scheduler acceptance.
The production selector continues to reject diagnostic engines.

The [read-only linker audit](tests/node-compat/foundation-scheduler/link-resource-audit-v1/README.md)
found that one Ninja job did not bound LLD's own threading. The pinned SDK's
print-only Clang command forwards `--threads=1 --thinlto-jobs=1` while retaining
all other link arguments. The separately frozen
[link1 producer candidate](tests/node-compat/foundation-scheduler/diagnostic-producer-v3-link1/README.md)
passes 24 synthetic command cases, syntax and patch checks; Root rehashed all
30 indexed files and an [independent source review](tests/node-compat/foundation-scheduler/independent-link1-review-v1/README.md)
found no concrete blocker to the proposal. The exact
[diagnostic producer change is now source-applied](tests/node-compat/foundation-scheduler/link1-adoption-v1/source-adoption-receipt.json),
with [new finite consumers](tests/node-compat/foundation-scheduler/diagnostic-link1-consumers-v1/README.md).
Root independently passes **46** host checks, verifies all 31 consumed inputs
and rehashes both source packets. The new freezer authenticates four final-link
witnesses; the launcher retains eight unchanged lifecycle definitions and the
same capacity thresholds. Original frozen packets remain unchanged; their earlier
UNAPPLIED descriptions are historical. Native306, diagnostic2 and production
recipe869 are unchanged. Actual link1 builds/freezes and the ordinary guest pass
are now recorded above; earlier preparation-only statements remain historical.
Generated Clang flags are observed; spawned LLD arguments, thread counts and
resource benefits are unobserved. Both diagnostic gates pass; all production gates remain
required.
No memory benefit, performance gain or lower start guard is proved.
O3, ThinLTO and the complete functional test scope remain the selected baseline.

The [reset audit](tests/node-compat/foundation-scheduler/reset-design-v1/README.md)
finds a source-level lifetime hazard: `Engine::reset` clears owning task references
before `timers::reset` traverses raw pointers in `TIMERS_MAP`. The selected
ComponentizeJS embedding has no automatic `Engine::reset` call, so this is not
presented as a per-export failure. No reset experiment has run. Transactional
registration, traced cancellation ownership, idempotence, resource cleanup,
bounded jobs/finalizers and request epochs must precede safe reset/reuse and ALS.

### Preserved failures and execution history

- The [first diagnostic attempt](tests/node-compat/foundation-scheduler/production-adoption-v1/release-attempt-v1/receipt.json)
  linked all 109 native steps but rejected an incomplete compiler receipt. Its
  raw engine has no published sidecar and was never admitted or executed.
- The [second attempt](tests/node-compat/foundation-scheduler/production-adoption-v1/release-attempt-v2-interrupted/receipt.json)
  was interrupted during disk exhaustion; its native exit status was not saved.
  No successful build or specific native stop cause is inferred.
- The corrected producer captures actual parent-target Ninja commands before and
  after the build. The one-job v4 launcher requires 2 GiB to start and stops below
  800 MiB, with process-group cleanup and status preservation. Six benign host
  lifecycle checks pass; the subsequent ordinary Release success is separately
  recorded above. The subsequent link1 Release-GC build and component gate also
  pass, as separately recorded above.
- The first production-regression implementation passed 34 host checks, but
  final review found an unbound manifest/pin recheck. V2 and its initial review
  are preserved as superseded. V3 captures initial primitive digests and rejects
  changes before parsing or following new entries. Root independently passes
  all 41 checks, including seven owned-scratch seal cases; actual pins stayed
  null throughout and no runtime reached the defective path.

### Storage preparation, separate from runtime results

All completed passes below preserve logical bytes and required metadata with
independent postverification. No historical component was executed for storage
work, and native build intermediates were retained. Allocation reductions are
filesystem observations, not guest memory or throughput results.

| Completed operation | Verified observation |
| --- | --- |
| [59 mature v5–v7 artifacts](tests/node-compat/storage-compaction-mature-v5-v7/README.md) | 709,795,840-byte summed allocation reduction. |
| [92 earlier accepted artifacts](tests/node-compat/storage-compaction-earlier-adoption-v1/results.json) | 810,020,864-byte reduction; 71 witnesses unchanged. |
| [67 additional terminal public artifacts](tests/node-compat/storage-compaction-additional-public-adoption-v1/results.json) | 542,859,264-byte reduction; 63 witnesses unchanged. Failed/build-only/benchmark labels retained. |
| [20 newly passed ordinary Release artifacts](tests/node-compat/storage-compaction-current-release-corpus-adoption-v1/results.json) | 149,131,264-byte reduction; all 32 witnesses and the ordinary result hash unchanged; 40 temporary/rollback paths absent. No corpus rerun. |
| [72 accepted public Release engine files](tests/node-compat/storage-compaction-public-engines-adoption-v1/results.json) | 422,617,088-byte summed allocation reduction; all 38 witnesses and bytes/required metadata unchanged. Independent verification checks flags/link counts and 144 absent temporary/rollback paths. Recorded global free-space increase was only 261,779,456 bytes and is nonexclusive. No binary executed. |
| [Two Release input copy-on-write replacements](tests/node-compat/storage-cow-release-inputs-adoption-v1/results.json) | Both direct clonefile calls succeeded; source identities and all bytes/required metadata preserved, target inodes intentionally changed. Observed global free-space delta only 3,612,672 bytes, nonexclusive. No 722 MB or unique-extent recovery claim. |

The [v8–v10 audit](tests/node-compat/storage-candidate-audit-v8-v10/results.json)
found all 255 eligible artifacts already compressed and selected none. The
[SDK compression attempt](tests/node-compat/storage-compaction-release-sdk-adoption-v1/results.json)
rejected its temporary copy before adoption because the required compression flag
was absent; the original remained unchanged at that point and zero recovery is
counted. Later, the separate verified copy-on-write operation intentionally
changed the target inode while retaining its bytes and required metadata.
Global free space is volatile; nominal input sizes are not recovered capacity.

The subsequent [public-engine audit](tests/node-compat/storage-candidate-audit-public-engines-v1/README.md)
identified 72 ordinary accepted engines with 698,212,352 summed allocated bytes.
The reviewed [contingency helper](tests/node-compat/storage-compaction-public-engines-v1/README.md)
has now run successfully, after fresh preimage/quiescence/open-file checks.
Their current summed allocation is 275,595,264 bytes; the earlier source/dry-run
packet's UNAPPLIED description is historical. Its bytes and audit are unchanged.
The [declared native-output audit](tests/node-compat/storage-candidate-audit-public-native-inputs-v1/README.md)
adds 472 object/archive files across five completed public builds, 84,680,704
allocated bytes. The [final-link archive audit](tests/node-compat/storage-candidate-audit-public-link-archives-v1/README.md)
found all 140 in-root archives already counted, with no additional paths.
The original combined 782,893,056-byte ceiling preceded compressed output and
shared-block effects; it was not a recovery estimate. Additional storage
capacity was needed at that point. The user subsequently freed space and the
native start guard now passes. That later recovery is not attributed to these
filesystem operations.

### Preparation and remaining acceptance gates

Root's [corrected source-readiness receipt](tests/node-compat/foundation-scheduler/corrected-production-readiness-v1/README.md)
records **214 fresh host checks** and independent rehashes of all four source
packets and their 666/733/1,409/773 listed inputs. The separate
[activation correction review](tests/node-compat/foundation-scheduler/independent-activation-seal-correction-v2/README.md)
confirms the three rewired packets, unchanged predecessor files and preserved
case/control bodies. Those source-preparation predecessors retain null pins;
their reviewed-pin successors below supply the current execution gates.

| Packet | Completed preparation | Still required |
| --- | --- | --- |
| [Private tick scheduler](tests/node-compat/foundation-scheduler/production-adoption-v1/README.md) | Accepted in bounded v12 after diagnostic, three-engine production, fresh replay, focused/GC, both-host HTTP and independent archive gates. | Public `process`/nextTick/timers/ALS and safe reset/reuse remain outside this accepted internal layer. |
| [Production core/allocator activation v5](tests/node-compat/foundation-scheduler/production-regression-candidate-v5/README.md) | Reviewed actual pins, 667-input closure, 55 Root host checks and fresh core/allocator/GC gates; included in accepted v12. | Future source changes require new artifacts and gates. Earlier null-pin preparations remain unchanged. |
| [Normal OFF strict/Web activation v3](tests/node-compat/foundation-scheduler/production-followon-off-v3/README.md) | Reviewed parent binding, 755 inputs and 32 Root host checks. Stream/web and all four strict suites pass fresh; included in accepted v12. | New source changes need fresh validation. Earlier packets and controls remain unchanged. |
| [Fresh serial OFF replay v3](tests/node-compat/foundation-scheduler/production-release-runner-v3/README.md) | Reviewed parent indices, 1,442 inputs and 49 Root host checks. All eight stages and independent 40-component verification pass; included in accepted v12. | No reuse of these results as validation for a changed future engine. |
| [Capability activation v3](tests/node-compat/foundation-scheduler/production-followon-capability-v3/README.md) | Reviewed pins, sealed final index, 778-input closure, focused gates and both-host HTTP all independently verified; included in accepted v12. | Existing getter/Symbol/GC/reuse and capability limits remain declared. |
| [Classic streams](tests/node-compat/foundation-classic-streams/production-adoption-v1/README.md) | Corrected native/classic/Node11, replay40/follow-on20, full20+14, HTTP both hosts and308-observation composition pass independent reviews. The168-worker timing protocol, integrity and numerical reviews pass; bounded strategy is recorded. | Preserve the independently reviewed18-worker process RSS result and the artifact closure, resolve old-Root context dependencies and review bounded acceptance. Original failures and raw-output/combined-GC limits remain explicit; v12 is still the accepted checkpoint. |
| [Reset and request ownership](tests/node-compat/foundation-scheduler/reset-design-v1/README.md) | Seven task kinds and concrete ownership/cancellation/resource problems mapped; guarded traced-owner protocol and dependency-ordered ALS/reuse plan written. | Implement and validate transactional registration, safe timer ownership, resource cancellation, bounded jobs/finalizers and request epochs before exercising reset. Mixed real/immediate polling can require a callable clock capability beyond today's type-only HTTP clock import. |
| [Blob/File integration](tests/node-compat/foundation-stream-consumers/blob-integration-candidate/README.md) | Ownership/receiver correction candidate, source receipts, Node oracles and future test harness. | Native integration and guest validation; resolve constructor coercion, MIME/endings, File naming/time, Promise ordering, stream cancellation and lifetime gaps. Buffer Blob/File exports remain explicit refusals. |
| [Native compression](tests/node-compat/foundation-zlib/README.md) | Three actual350 builds/freezes pass independent review. Corrected v8 harness normal validation has283 bounded records/138 full-byte successes; GC has three codec records; disabled selection has eight bundler denials/five Buffer-stub records. All result reviews pass. | Operational admission,22 Node error-case differences/VERNUM release contract, matched codec cost, new350 selected-host/release regressions and archive gates remain. Metadata backend-proof fields stay false. Original failed native/harness/fixture attempts remain historical failures. |

The [roadmap completion audit](docs/node-compat/roadmap-completion-audit-v1/README.md) maps the initial A–E deliverables, all24 ledger gates and remaining phase dependencies. Its [independent reviewe2816746](docs/node-compat/roadmap-completion-audit-review-v1/README.md) passes the snapshot scope: all24 gates,52 references and local links are accounted for. It is a source/evidence inventory, not a new runtime validation.

### Consumer355 source and build history

Initial source-only stage (historical; superseded by the build/runtime states above):

The [consumers proposal](tests/node-compat/foundation-stream-consumers/production-text-json-candidate-v1/README.md) is source-only. Its [independent review](tests/node-compat/foundation-stream-consumers/independent-production-text-json-source-review-v1/README.md) holds on CONS355-M1: two post-link paths name a missing child codec-evidence.py instead of the authenticated parent350 helper. The [v2 successor](tests/node-compat/foundation-stream-consumers/production-text-json-candidate-v2/README.md) and [independent source review](tests/node-compat/foundation-stream-consumers/independent-production-text-json-v2-source-review-v1/README.md) now pass (39 files/506 inputs). Native355 payload bytes remain unchanged. [Actual SDK frontend checks](tests/node-compat/foundation-stream-consumers/sdk-registration-syntax-v1/README.md) pass consumer ON/OFF with empty diagnostics and1,036/1,035 dependency hashes. This is syntax/API evidence only; no355 configure/build/link/install or runtime action has run. The genuine355 producer is being prepared with distinct native/tool/original-preparation contexts. Positive Web inputs must select the existing node:stream/web iteration wrapper; raw global ReadableStream is not implicitly adapted.

The following records preparation checkpoints and completed build attempts; the current table above takes precedence over historical pending statements.

The [consumer355 producer](tests/node-compat/foundation-stream-consumers/native-integration-candidate-v1/README.md) is sealed at index `ab88215a…8e25`:53 files,3,357 preparation references,767 native-tool rows,50 pure checks and three syntax checks. All three planned variants keep zlib ON; the disabled variant disables only consumers. The source framework distinguishes configured, frozen and original preparation roots, and is not a component-packaging closure. The [independent producer review](tests/node-compat/foundation-stream-consumers/independent-native-integration-source-review-v1/README.md), index `6e24de20…f6c5bc`, holds C355-M1: the configured parent codec helper can execute before the current767 tool hashes are checked. Staging, native builds, installation and runtime validation remain unexecuted; the v1 packet remains held. The [v2 producer correction](tests/node-compat/foundation-stream-consumers/native-integration-candidate-v2/README.md), index `9edf31c1…3a378`, authenticates current tool dependencies at the start of the frozen reader. Its59 files/3,420 inputs,50 source checks,19 ordering/scratch checks and three syntax checks pass. The native355 payload is unchanged. [Independent v2 source review](tests/node-compat/foundation-stream-consumers/independent-native-integration-v2-source-review-v1/README.md), index `28300826…827811`, passes. Root [source review](tests/node-compat/foundation-stream-consumers/native-integration-v2-root-source-review.json) authorizes staging only. [Actual publication](tests/node-compat/foundation-stream-consumers/native-integration-v2-root-stage-results.json), Root session7465/PID11018, exits0 in6.090 operational seconds and publishes1,173 files at `/tmp/starling-node-compat/consumers-source-v2`, on genuine detached54b HEAD with no Git alternates. Root independently verifies its59 staged indexed files; [Full actual-stage review](tests/node-compat/foundation-stream-consumers/independent-native-integration-v2-stage-review-v1/README.md), index `371b7880…1b64d`, passes:1,173 overlay files plus508 genuine baseline files,3,420 original-context inputs and only three genuine documentation symlinks outside the consumed overlay. The [normal-OFF build review](tests/node-compat/foundation-stream-consumers/native-integration-v2-normal-off-build-root-review.json) authorizes one fresh Release build. That build ran under Root session4055/PID14781 with consumers/zlib ON, entropy OFF, one job and2GiB/800MiB disk guards. The [normal build/freeze/read-only verification](tests/node-compat/foundation-stream-consumers/native-integration-v2-normal-off-root-results.json) now finishes raw0 for all three commands:108 build steps,10,002,283-byte engine `661ef794…f0c79`, metadata `860e9521…62f92`, freeze `fadc83ce…26096`,1,164 frozen copies and1,162 original-reference entries. Its [independent native review](tests/node-compat/foundation-stream-consumers/independent-native-consumers-v2-normal-off-review-v1/README.md), index `b80489f4…124d6c`, passes:1,164 frozen files,1,162 pre-GC original entries,62/4/6 native command groups plus the separate embedding command, selected native codec/header/install order and complete locked dependency provenance. A separate [GC build review](tests/node-compat/foundation-stream-consumers/native-integration-v2-gc-off-build-root-review.json) follows the reviewer’s complete pre-GC original checkpoint; [GC build/freeze/read-only verification](tests/node-compat/foundation-stream-consumers/native-integration-v2-gc-off-root-results.json), Root sessions60577/57664/26486, also finishes raw0:17 incremental steps,engine `b378dea3…910e7` (10,003,832 bytes),metadata `675131c9…87672`,freeze `0268e073…1101e` and1,164 frozen files. [Independent GC native review](tests/node-compat/foundation-stream-consumers/independent-native-consumers-v2-gc-off-review-v1/README.md), index `010fbd51…a9db91`, passes the actual GC files/commands and rechecks all normal frozen copies; no guest-GC/root-isolation claim follows. The [consumer-OFF control](tests/node-compat/foundation-stream-consumers/native-integration-v2-disabled-off-build-root-review.json) ran under Root99558/PID39882 on its separate s0 project, with zlib ON and the same62/private6 layout; its [build/freeze/read-only verification](tests/node-compat/foundation-stream-consumers/native-integration-v2-disabled-off-root-results.json), Root99558/3263/24291, now finishes raw0:108 steps,engine `81ffa152…e5110` (9,995,242 bytes),metadata `8e05a705…f76ac`,freeze `9d6fd222…4a4e1` and1,164 frozen files. Independent control review is underway. All three native artifacts were exported into a separate unreviewed candidate document at exporter raw0; no admission or runtime proof was issued. Only the two expected shared normal CMake/compile-database originals may reconfigure; their retained snapshots and all frozen normal files remain strict. No component or guest has run. [Cache preparation attempt2](tests/node-compat/foundation-stream-consumers/native-integration-v2-cache-preseed-attempt2-root-results.json) separately copies four hash-verified download/tool cache files into the fresh build directory, with independent inodes. The initial helper failed before copying files because local Python lacks hashlib.file_digest; its [failed receipt](tests/node-compat/foundation-stream-consumers/native-integration-v2-cache-preseed-root-results.json) and empty-directory observation are retained. The corrected streaming-hash retry passes. No checked-out source, engine, metadata or codec evidence was copied.

## Outstanding work, in dependency order

Immediate execution priority remains Next.js response completion. The CDP
resource-stream comparison and qualified guest-stage DATA audits are complete
within their scopes; cloud's strict failure remains. Next implement/test the
Source-proposed V4 outer metadata classification in a separately versioned
observer, preserving the old V3 globaljoin:false result, strict assertions and
all failed samples. Use that evidence to choose any later React root/reader
instrumentation or justified native fix. Direct HTTP and Chrome arrayBuffer controls are complete within
their bounded scopes; the original full wasmCloud browser contract remains
failed. Lifecycle/resource/reuse, clean-machine reproduction, empirical cost and
production promotion follow that boundary investigation. The broader release
dependencies below remain open.

1. Preserve bounded foundations-v13, its v12 parent, historical failures and
   counterexamples. Corrected classic source promotion, declared archive scope,
   runtime/HTTP gates, timing and small-worker RSS reviews are complete. Keep the
   old twelve zlib contexts held; future executions need fresh context-aware
   families rather than rerunning or redirecting old preflights.
2. Complete consumer355 registered-module runtime validation: the normal190-observation/11-initializer run finishes raw0 after all three
   native and preflight gates pass. Its independent result review and GC4 review pass behind the
   reviewed-normal gate. The separate disabled8-
   denial/5-smoke gate and its independent result review pass. RuntimeOnly build/freeze/verify, independent review and four-variant read-only bootstrap pass; fresh full regression
   and same-artifact host gates remain, with their source integration plan
   being prepared separately. Zlib350 normal/GC/control results
   pass within their bounded contract; operational admission, the explicit
   22-case Node-difference contract, matched cost, RuntimeOnly and new-engine
   host/release gates remain. The new codec cost work is source-only. Broader
   streams, consumers, overloads, heap/teardown/ALS/reuse and performance require
   separate evidence.
3. Resolve Blob/File ownership and semantic gaps before promoting consumer
   byte/blob operations. Verify all affected fetch/FormData/clone callers.
4. Complete a correct AsyncLocalStorage propagation design and implementation:
   capture at actual promise/native-resource creation, restore around execution,
   trace tokens, restore prior context on every exit and release request owners.
   Isolated probes do not establish production propagation across `await`.
5. Integrate measured guest compression and suitable cryptographic primitives.
   Audit algorithm/key semantics, allocation bounds, entropy selection, lifetime
   and final component size. Correct the independently confirmed CryptoKey
   native-owner/finalizer gap before Hmac/KeyObject reuse; a bounded one-shot
   digest can be assessed separately. Reuse native web code only where semantics
   and ownership match.
6. Define independent optional filesystem, HTTP, DNS/socket and CLI profiles
   with per-export contracts, exact standard import allowlists and capability
   denial tests. Validate identical artifacts on both hosts. WASI P2 sockets
   provide **no TLS**; TLS requires a separately selected guest stack, trust and
   time policy. Process creation, IPC, V8/Inspector and Node worker behavior
   remain unavailable with the selected capabilities.
7. Close lifecycle and reuse gates: environment/clock/entropy snapshot policies,
   final post-binding initialization, live-handle restrictions, cancellation,
   component reuse and request-associated state. Run broader upstream coverage
   and final size/startup/memory/throughput comparisons for released variants.
   The [native body-task cancellation implementations](host-apis/wasi-0.2.0/host_api.cpp)
   explicitly lack a supported cancellation contract for `BodyWriteAllTask` and
   `BodyAppendTask`. Reset cancellation ownership and future callback reentrancy
   therefore remain open; an idle tick-queue check alone does not close them.
8. Expand APIs only with explicit manifest changes, Node differential tests,
   actual component tests, emitted-import checks and measured demand. Retargeting
   Node/WASI/hosts requires a new compatibility baseline.

## Known limitations and decisions to preserve

- **Node callback-return parity is false for an observed case.** Node reads a
  returned object's `then` getter for an ordinary and a fresh protected listener
  once each; native Jco/Wasmtime read neither. Already-aborted queued callbacks
  ignore the returned object on both. Observed counts are `1/1/0` versus `0/0/0`.
  Callable-then and rejection behavior was not tested by this observation;
  Node `addCatch`/returned-Promise/error-routing semantics remain unimplemented.
- Target `Symbol.dispose` is an unregistered well-known symbol; pinned Node uses
  `Symbol.for('nodejs.dispose')`. No global symbol-identity rewrite is claimed.
- The v10 GC test validates combined owners: the listener closure also retains
  the disposal symbol. It does not isolate prototype-only symbol liveness.
- HTTP request counters `[1,1,1]` prove neither same-instance reuse nor request
  isolation. Those lifecycle gates remain open.
- Buffer methods, encodings, allocation and stream support are bounded by their
  manifests. Deferred callable operations throw identifiable errors; importable
  namespaces and constructors are not evidence of complete API behavior.
- Full untouched upstream suites, complete EventTarget semantics, cross-realm
  behavior, general Promise result handling, process handlers, AsyncResource,
  complete Buffer support and complete Node compatibility are not verified.
- Uncompiled templates, host-only tests, private experiments and real-component
  evidence are separate evidence classes. A new engine requires fresh runtime
  gates; a source receipt alone does not validate it.

## Keeping this tracker current

Update this file when a packet is applied, a gate passes or fails, an accepted
checkpoint changes, or a blocker/decision is discovered. Record the concrete
artifact and validation scope, retain counterexamples, and move work to completed
only when its required gates have passed. Detailed logs and immutable receipts
belong in the linked evidence directories rather than being duplicated here.

The [correctness loader v2 source](tests/node-compat/foundation-zlib/cost-jco-correctness-candidate-v2/README.md), index `d2516c93…befeb`, seals51/493 rows with193 pure/parser,74 source/data and21 syntax checks. It implements the observed ESM/TLA/relative-core/package contract and a228-worker untimed schedule, while all actual proofs/action slots remain NULL. Independent source inspection finds a concrete pre-action boundary defect: Node cross-input retention accepts only Buffer, but the genuine stage decoder first supplies a plain Uint8Array. That would reach the JSON writer and fail before its codec call. [Independent source HOLD](tests/node-compat/foundation-zlib/independent-cost-jco-correctness-v2-source-review-v1/README.md), index `751147af…28ecd`, confirms51/493 rows,13 exact copies and the planned schedules while identifying ZLIB-JCO-CORRECTNESS-V2-M1. The immutable source stays held. A [thin v3 source successor](tests/node-compat/foundation-zlib/cost-jco-correctness-candidate-v3/README.md), index `0124b94f…8cb8c`, seals26 files/22 own references and three afterimages/28 reversible edits while retaining the complete51/493 donor unchanged. The actual callback snapshots precisely the ordinary Uint8Array/Buffer window before awaiting persistence. Preparation passes36 pure retention tests,1,333 source/data and five syntax checks, including genuine stageRecord DATA reproducing the old failure without a codec call. [Independent v3 source review](tests/node-compat/foundation-zlib/independent-cost-jco-correctness-v3-source-review-v1/results.json), index `abeb157a…aa5a`, passes all26/22 own and51/493 donor rows plus28 reversible edits, closing M1 within its source scope. The sealed template stays NULL. A separate [Root untimed authority](tests/node-compat/foundation-zlib/cost-jco-correctness-v3-root-authority.json), SHA `235d391b…7daf6`, binds the exact three actual artifact reviews and unchanged construction authorities. Root86618/PID49994 starts the first real Jco/Node correctness action with228 planned owned workers and a7500-second outer operational deadline. The [actual full correctness result](tests/node-compat/foundation-zlib/cost-jco-correctness-v3-root-results.json), SHA `8a9a2141…6a21d`, finishes Root86618/PID49994 raw0 in1,637.224 operational seconds. Root rehashes11,440 indexed/11,442 actual files and712,222,394 indexed bytes,228 raw0/clean worker terminals,360 primary observations,135 main crossdecode edges and separate FF-OFF15 encodings/15 fresh Node/45 guest edges. Index `e8da5ddb…5aa7e` and completion `d3e0bfb5…7d3e1` bind the complete20,237,274-byte result. Three retained/90 fresh/90 main guest/45 OFF guest processes are actual; all60 Node decoder edges retain full typed/input/output records through the corrected U8 binary boundary. [Independent full correctness review](tests/node-compat/foundation-zlib/independent-cost-jco-correctness-v3-results-review-v1/results.json), index `e03bb0db…48083`, now passes23,454 current input tuples, all3,828 complete primitive returns,1,980 full output payloads,60 fresh Node edges/160 U8/Buffer binary files and228 unique clean workers. Its [stable result contract](tests/node-compat/foundation-zlib/independent-cost-jco-correctness-v3-results-review-v1/result-contract.json), SHA `25411f2e…936f1`, records5,448 named entries/2,475 guest codec calls/495 untimed codec N1 calls and explicitly zero executed controls. Ownership/input/prior stability is verified as full returned bytes plus instrumented reports, with no post-exit heap inspection. Actual control workloads remain required before pilot/timing. Stock Wasmtime, native builds, source promotion, pilot and timing remain forbidden by this Jco action.

The [crypto native integration source](tests/node-compat/foundation-crypto/native-integration-candidate-v1/README.md), index `10a87c1d…26db`, seals38 files/1,271 bounded references for a genuine new355 identity: exactly five composed owner/guard replacements and350 unchanged native sources. New policy/recipe/named build-only validator/stage/freeze namespaces have NULL pins/actions, with no ordinary-selector reopening. Preparation records74 source/data, five negative models and19 syntax checks. The [independent v1 integration review](tests/node-compat/foundation-crypto/independent-crypto-owner355-native-integration-source-review-v1/README.md), index `109a929f…6f7c`, holds the JS context contract: Python authenticates configuredSourceRoot, but the JS wrapper drops it despite its documentation. No caller or native staging failure is inferred. A [v2 context successor](tests/node-compat/foundation-crypto/native-integration-candidate-v2/README.md), index `68b6f2a5…5575`, returns and rechecks the genuine configured/frozen roots, with fresh recipe/tool hashes and stage/build/freeze namespaces. All five native payloads and the full355 policy/helper remain unchanged. Preparation passes74 source/data,21 pure mapping fixtures and21 syntax checks without calling the helpers; [Independent correction review](tests/node-compat/foundation-crypto/independent-crypto-owner355-native-integration-v2-source-review-v1/results.json), index `ebbfda80…60dac`, passes44/1,323 rows,1,711 unique hashes and16 reversals, resolving the bounded context defect. The sealed template pins/actions stay NULL. A [separate source-stage authority](tests/node-compat/foundation-crypto/native-integration-v2-source-stage-root-authority.json), SHA `f7e168d2…22a1f`, runs the unchanged publisher as Root91711/PID50423 raw0 in1.387 operational seconds. [Root actual-copy verification](tests/node-compat/foundation-crypto/native-integration-v2-source-stage-root-results.json), SHA `a0654a8e…5d101`, checks all1,311 new copies, modes and distinct source/destination inodes, full355 native/922 tool rows and detached54b/no-alternates clone. [Independent actual-copy review](tests/node-compat/foundation-crypto/independent-native-integration-v2-stage-review-v1/results.json), index `8c0583a4…41c79`, passes all1,311 copies and2,632 unique file tuples, exact modes/inodes and clone metadata using read/hash checks only. A separate [normal Release/OFF build authority](tests/node-compat/foundation-crypto/native-integration-v2-normal-off-build-root-authority.json), SHA `e7a59da2…047b2`, starts Root62629/PID53008 with jobs1, GC/OOM/debug off,2GiB start/800MiB stop guards and a7200-second operational ceiling. The [actual normal-OFF native result](tests/node-compat/foundation-crypto/native-integration-v2-normal-off-build-root-results.json), SHA `0749a034…c8e28`, finishes Root62629/PID53008 raw0 in646.200 operational seconds, with owned build-group cleanup and empty stderr. Engine `36bd8508…ebc05` is10,002,820B; sidecar `8bafca1a…3ca37` is362,391B. Root rehashes all1,311 staged sources/modes after build and verifies full355+external3, exact five owner/guard replacements,62 native/4 strict/6 private/1 embedding commands, actual WebCrypto cache ON/install1/three changedCPP commands. An initial Root reader wrongly assumed WebCrypto was in the selected observed-option subset; its KeyError is retained separately and corrected by reading the authenticated CMake cache/build evidence. This is a reader-preparation error, not a native build failure. No new native artifact is independently accepted yet. A pre-execution freeze audit finds the unchanged freezer still expects the old CONSUMERS selector state, while the actual named admission returns CRYPTO_OWNER355. Freeze is held before any invocation/output pending a bounded separate correction; the build/staged source remains immutable. Link/lifetime/guarded-key tests and required private-copy/bounds follow-ons remain open; no new Node crypto export is implemented.

The [untimed correctness preparation](tests/node-compat/foundation-zlib/cost-jco-correctness-candidate-v1/README.md), index `61029551…f305a`, seals32 files/609 references with168 pure/data,210 source/data and16 syntax checks. It provides360 planned primary observations and135 planned provider edges, plus separate FF-OFF15/15/45 schedules and raw-before-assert collectors. These360 observations are distinct from the proposed360 timing workers. This source entry always refuses until an observed-glue loader and actual component/ABI proofs are implemented and reviewed; no provider, guest, codec or worker runs. The [Node-deviation contract proposal](tests/node-compat/foundation-zlib/node-deviation-contract-candidate-v1/README.md), index `de59758c…31469`, separately preserves all22 differences,11 original null labels and absent messages. It proposes classifications for explicit profile limits and six errno fix candidates; all runtime/policy/operational decisions remain unapproved.


The deviation proposal’s [qualified independent review](tests/node-compat/foundation-zlib/independent-node-deviation-contract-source-review-v1/README.md), index `8ccd5a15…28100`, passes6/129 data integrity and the22/100/22 row mappings, but holds its broad mutability wording: pinned Node already freezes `codes`. A [bounded wording amendment](tests/node-compat/foundation-zlib/node-deviation-contract-mutability-amendment-v1/README.md), index `b8ec1f65…9413a`, withdraws that claim and preserves all22 observations; no uncaptured prototype/own-property claim or runtime decision is introduced. Both policy proposals remain unapproved. [Independent bounded wording review](tests/node-compat/foundation-zlib/independent-node-deviation-mutability-source-review-v1/README.md) now passes7/eight reference hashes and both exact afterimage reversals, verifies pinned Node’s ObjectFreeze(codes), and confirms every other contract value unchanged. Only the narrow wording correction is accepted; no runtime or policy decision is made.

The [stock Wasmtime transport source proposal](tests/node-compat/foundation-zlib/cost-wasmtime-transport-candidate-v1/README.md), index `345ce70f…1be56`, inspects pinned42.0.1 help/source and exact wasm-wave dependency. It supplies WAVE string escaping, a strict typed-string stdout parser and argv accounting, with49 pure/40 data/two syntax preparation checks. Current ARG_MAX is1,048,576 bytes: the known largest retained Node gzip requires699,737 expression bytes, while the broader allowed1MiB compressed input needs1,398,104 base64 bytes alone and cannot fit that aggregate limit. These are DATA/accounting findings, not actual largest-record execution or per-argument proof. [Independent transport source review](tests/node-compat/foundation-zlib/independent-cost-wasmtime-transport-source-review-v1/results.json), index `ca663930…b7fd2`, passes29/52 source rows,78 unique paths,21 locked crate members and15 exact Node sizing models; no runtime feasibility is inferred. A separate [Root identity-only authority](tests/node-compat/foundation-zlib/cost-wasmtime-identity-v1-root-authority.json), SHA `7e79829f…c98a6`, runs three fresh stock Wasmtime42 processes as Root25871/PIDs67649/68741/69829. All finish raw0 with1102/1096/1096-byte complete stdout, empty stderr and observed owned-group cleanup. [Root typed-return validation](tests/node-compat/foundation-zlib/cost-wasmtime-identity-v1-root-results.json), SHA `2fa1e262…b74f0`, fsyncs raw files before decoding, validates all three WAVE-string/inner-JSON values and exact argv/environment accounting. Each first identity shows empty prepared/staged/retained state, one identity entry and zero codec/control calls. [Independent actual identity review](tests/node-compat/foundation-zlib/independent-cost-wasmtime-identity-v1-results-review-v1/results.json), index `49090a30…d94f5`, passes11,953 current tuples, retains independent fsynced raw copies and decodes the complete three WAVE strings/full inner identities. Exact argv/environment models are286/286/287 bytes. Root exports execute; reviewer runs read/hash/data code only. No string argument, stage/validate, codec, reuse or largest-record proof follows. Actual small/all-provider-largest host probes remain required with exact environment accounting and no truncated/skipped streams.

The [pre-execution crypto freeze-contract audit](tests/node-compat/foundation-crypto/independent-native-integration-v2-freeze-contract-review-v1/results.json), index `62cf4f2c…cbc912`, preserves91 original/staged source tuples and identifies the single old-state comparison. It also requires the corrected active freezer to be frozen under its actual bytes and keeps the old staged freezer explicitly as donor DATA; native recipe/policy/helper/tool922 identities need not change for that separate operation. The genuine verifier is a function API, not a CLI. A separate bounded freezer-source successor is being prepared with exact staged context, own/peer/Root authority checks, active/donor provenance and a14-group native evidence checklist. The old freezer is not executed, build inputs stay unchanged, and no frozen crypto artifact or runtime result is claimed.

The [first bounded ownership harness source](tests/node-compat/foundation-crypto/ownership-validation-candidate-v1/README.md), index `21816be7…2d0cd`, seals21 text files/75 inputs and82 static/data/two parse checks. It proposes four ordinary scalar exports and raw/JWK/retained/new-guard HMAC-SHA256 cases, full32-byte tags and input-window/key-copy observations, backed by the actual existing Promise/event-loop scalar bridge. Its within-one-export validate wrapper is separate from host interleaving or instance reuse. All native/component/tool/ABI/action slots remain NULL, with no crypto/Node-oracle/component/helper/guest execution. [Independent harness source review](tests/node-compat/foundation-crypto/independent-ownership-validation-source-review-v1/results.json), index `6918a280…075d9`, passes21/75 rows,87 unique paths and actual Promise bridge/refusal/counter contracts. No finalizer-count, isolated-root, all-copy-erasure or broader Node crypto claim follows.

The [corrected freezer source](tests/node-compat/foundation-crypto/native-freezer-source-amendment-v1/README.md), index `0ff37e52…ecccd`, passes [independent source review](tests/node-compat/foundation-crypto/independent-native-freezer-source-review-v1/results.json), index `aa25647e…4a06b`:13/65 rows,1,390 unique tuples and seven exact reversals. A [separate freeze authority](tests/node-compat/foundation-crypto/native-freezer-v1-normal-off-root-authority.json), SHA `9d41c006…6b81`, runs the actual corrected entry Root25578/PID79054 raw0 in9.588 operational seconds. A [read-only verifier authority](tests/node-compat/foundation-crypto/native-freezer-v1-normal-off-verify-root-authority.json), SHA `1e355a0c…f89ed`, authenticates all configured/source/control bytes and calls the genuine staged `verify_frozen_variant(normal-off, return_receipt_digest=True)` function as Root43902/PID80524 raw0 in4.169s. [Root combined freeze/verification](tests/node-compat/foundation-crypto/native-freezer-v1-normal-off-root-results.json), SHA `88cfe19d…d4bba`, checks1,390 frozen copies/1,387 originals,1,391 actual files, no symlinks, full355+external3 and actual active/donor tooling. Freeze receipt `d088286c…f7760` retains engine `36bd8508…ebc05`/10,002,820B and exact sidecar `8bafca1a…3ca37`. Backend proof remains false/null; no metadata is projected or rewritten. [Independent normal-OFF native provenance review](tests/node-compat/foundation-crypto/independent-native-crypto-owner355-v2-normal-off-review-v1/results.json), index `27b88cae…44f36`, passes8,821 unique files, all1,390 copies/1,387 originals and14 evidence groups, including actual SDK30/LLVM21/wrapper/optimizer chain,4,650 pinned OpenSSL sources/locked Rust and selected codec witnesses. Pure GNU archive-index decoding finds unique OPENSSL_cleanse and EVP_PKEY_free definitions in the selected linked archive; no symbol tool or crypto operation is run by the reviewer. A normal-original checkpoint protects all current original bytes and identifies exactly two prospective live CMake cache/DB exceptions for a future separately authorized reconfigure; all frozen copies stay strict. Reviewed bootstrap data and actual packaging/ABI/HMAC/lifetime validation remain separate gates. No key, crypto, GC, guest/host or timing operation runs in build/freeze/verification.

A separate [five-scope follow-on authority](tests/node-compat/foundation-stream-consumers/release-gates-followons-v2-root-authority.json), SHA `c64b28c5…8eeea`, starts Root90775/PID82335 for fresh serial allocator-GC/focused-OFF/focused-RuntimeOnly/focused-GC/getter checks under exacta986. Independent release review remains pending; these additional tests do not adopt its results as acceptance. Each scope has its own new output/controller/raw logs and30-minute inner/31-minute outer operational bound. The unused v1 authority is preserved: it incorrectly put a generated-index descriptor in the informational review field; v2 supplies the complete source-review pair before any action. HTTP, native builds, timing, source promotion and acceptance remain forbidden by this action.

The [all-provider argv DATA model](tests/node-compat/foundation-zlib/cost-all-provider-argv-model-v1-root-data.json), SHA `7ce260e8…27a6f`, authenticates the60 actual Node/native/FF-ON/FF-OFF records from the completed Root-observed correctness output, checks full encoded bytes/SHA and models each decoder component with the exact proposed one-variable environment. The largest is Node large-PRNG gzip:700,013/700,013/700,014 modeled argv/environment/pointer bytes for native/FF-ON/FF-OFF, all below current ARG_MAX. This runs only pure JSON/base64/hash/WAVE/accounting code; no guest/codec/host invocation, per-argument/kernel proof, accepted correctness transfer or action authority follows. Actual stock-Wasmtime small/largest input tests and actual controls remain gates before pilot/timing.

[Independent five-followon review](tests/node-compat/foundation-stream-consumers/independent-release-gates-followons-v1-results-review-v1/results.json), index `063abec9…b475c`, now verifies Root90775 all five raw0 scopes: allocator-GC82335/106.127s, focused-OFF83082/182.966s, RuntimeOnly84049/175.922s, focused-GC84800/159.509s and getter85675/125.458s. It rehashes12,985 paths,221 regular outputs/five links/20 component occurrences. RuntimeOnly eight components import only standard random@0.2.10; the other12 import nothing. Full16+4+9 Node arrays match across retained OFF/Runtime records, eight complete raw quoted returns decode,11 fatal/discard pairs and combined-owner GC commands match. Allocator-GC Wasmtime stdout is decoded-only. Getter observationCompleted remains true while Node compatibility remains false: Node1/1/0, guest0/0/0; it is a confirmed counterexample, not parity. HTTP, source promotion, timing and production acceptance remain open.

The [actual small/largest stock-Wasmtime string result](tests/node-compat/foundation-zlib/cost-wasmtime-strings-v1-root-results.json), SHA `4e37c006…e3e0f`, now finishes Root37792 with six fresh raw0/gone-group processes and complete6,232-byte small/1,404,206-byte large stdout records, empty stderr and12 full returned outputs equal to the64-byte/512KiB fixtures. The separate [Root codec-string authority](tests/node-compat/foundation-zlib/cost-wasmtime-strings-v1-root-authority.json), SHA `91d57160…917f5`, allows only those six validations. [Independent transport review](tests/node-compat/foundation-zlib/independent-cost-wasmtime-strings-v1-results-review-v1/results.json), index `663324c5…396d`, verifies23,596 inputs, all60 requests/180 per-arm argv models and the unique maximum:699,738 NUL-inclusive argument bytes and700,013/700,013/700,014 aggregate bytes accepted on this pinned Darwin/Wasmtime host. The [stable transport contract](tests/node-compat/foundation-zlib/independent-cost-wasmtime-strings-v1-results-review-v1/result-contract.json), SHA `bdd4fee8…208c4`, records six outer validates/30 named entries/12 codec calls/zero controls. Returned state stays prepared/staged with retained output; no idle/reset/reuse/interleaving, general per-argument/future-record/resource bound or performance claim follows. Actual controls remain required.

The [control supplement source](tests/node-compat/foundation-zlib/cost-jco-control-correctness-candidate-v1/README.md), index `ad0d651f…f7a23`, passes [independent source review](tests/node-compat/foundation-zlib/independent-cost-jco-control-source-review-v1/results.json), index `d6f72a45…7bb58`, after127 pure/206 data/seven parse preparation checks. It proposes three fresh sessions/726 returns/540 controls/zero codecs via narrow loader/collector afterimages. Its [first actual control authority](tests/node-compat/foundation-zlib/cost-jco-control-v1-root-authority.json), SHA `b805d8e1…7608c`, runs Root54743/PID91129 and [fails raw1 before any worker](tests/node-compat/foundation-zlib/cost-jco-control-v1-failure-root-results.json), SHA `1e1b07e4…6a38`, after196.405 operational seconds. COST-CONTROL-PARENT-DIRECTORY-M1:parent creates jobs but not the processes directory required by the genuine durable logger; lstat fails before launch record/spawn. Exact partials are one descriptor and failure.json, completedOrigins is empty and post-failure source audit passes. Read-only prerequisite helpers execute; no worker/generated module/guest control/codec runs. Prior correctness and transport proofs remain valid. [Independent actual failure review](tests/node-compat/foundation-zlib/independent-cost-jco-control-v1-failure-review-v1/results.json), index `534f2d86…429a5`, verifies558 files/530 descriptor-critical rows, exact raw1 and the pre-launch caller/callee path. It explicitly records the missed directory precondition in the old source PASS. A [thin v2 correction](tests/node-compat/foundation-zlib/cost-jco-control-correctness-candidate-v2/README.md), index `3b566083…d1ff1`, seals29 files/190 references, two afterimages/ten reversible edits and passes79 source/data, five parse and eight genuine benign-lifecycle checks. The old missing-dir path fails before launch; the prepared directory path runs one benign Node child at raw0 with cleanup and complete four-file closure. No guest/provider/preflight/control/codec runs during preparation. [Independent control-v2 source review](tests/node-compat/foundation-zlib/independent-cost-jco-control-v2-source-review-v1/results.json), index `20cb3efa…6bbdeb`, passes29/190 rows,228 unique hashes, ten reversals and the complete benign regression. A [new v2 Root authority](tests/node-compat/foundation-zlib/cost-jco-control-v2-root-authority.json), SHA `38f6a045…3ddef7`, starts Root4837/PID96423 against the fresh v2 output, with the same726-return/540-control/zero-codec schedule. The [actual v2 control result](tests/node-compat/foundation-zlib/cost-jco-control-v2-root-results.json), SHA `9b22479e…92dde`, now finishes Root4837/PID96423 raw0 in219.064 operational seconds. Root rehashes1,480 indexed/1,482 actual files and2,513,957 indexed bytes, all three clean worker terminals and the complete726-return/90-setup/270-distinct-case/540-control/zero-codec result. Index `723ccdb0…ce2ea`, results `6c9f9df2…62c59` and completion `06c26897…39249` are retained. Independent actual-control review is running; public FNV/sentinel/state/counter evidence does not expose internal copied buffers or prove independent heap reads. The original v1 failure and earlier control0 proof remain unchanged. Old source, authority, source PASS and failed files stay fixed.

The crypto exporter supports an explicit subset of labels. A [normal-only export authority](tests/node-compat/foundation-crypto/native-v2-normal-off-pin-export-v1-root-authority.json), SHA `13993e6f…b1cb4`, runs the actual staged exporter Root10542/PID89088 raw0 in3.313s, preserving [unreviewed candidate DATA](tests/node-compat/foundation-crypto/native-v2-normal-off-pin-candidate-v1.UNREVIEWED.json), SHA `cf05a57c…d56f`. Separate [reviewed normal-only pins](tests/node-compat/foundation-crypto/reviewed-native-v2-validation-bootstrap-pins-v1.json), SHA `e6bdb310…943a9`, and [Root build-input review](tests/node-compat/foundation-crypto/native-v2-validation-bootstrap-root-review-v1.json), SHA `071666bd…b0bb`, change only review state/flag and four native-proof fields; all other pin data stays exact and three variants remain NULL. [Root derivation/bootstrap receipt](tests/node-compat/foundation-crypto/native-v2-validation-bootstrap-root-results-v1.json), SHA `63471df1…9d4d8`, records the real cryptoOwnerBootstrapPreflight plus explicit recheck as Root41620/PID91553 raw0 in12.167s. The complete884,436-byte frame and finite summary preserve actual configured/frozen roots and full355 ownership metadata. Intermediate Python helper objects are not separately retained; their rechecks are code/clean-terminal supported. A post-reader != syntax typo is retained separately and corrected before any reader I/O; no product failure is inferred. [Independent pin/bootstrap review](tests/node-compat/foundation-crypto/independent-native-v2-validation-bootstrap-results-review-v1/results.json), index `c3fb6181…ad2b8`, now passes9,214 inputs, exact candidate/metadata/freeze reconstruction, six normal-pin review-field changes, other variants NULL and complete metadata/pin/11 selected manifests. Its [stable contract](tests/node-compat/foundation-crypto/independent-native-v2-validation-bootstrap-results-review-v1/result-contract.json), SHA `d1a59bf2…da746`, preserves the build-only scope. Internal helper objects, complete inherited environment and process-group-gone probes are not separately retained, so none are claimed. No engine, HMAC/key/crypto, GC, component, guest/host or timing operation runs here. The normal-only ownership component construction source is in preparation, with later ABI/loading/key-operation authorities still NULL.

The first [crypto ownership component construction template](tests/node-compat/foundation-crypto/ownership-component-candidate-v1/README.md), index `eb648e19…b5c30`, seals28 files/5,059 source references with39 pure/14,901 data/13 parse checks and no component/key action. It uses the genuine normal-only bootstrap and authenticated packaging roles, four proposed scalar exports and an explicitly closed future key-export path. Independent source inspection catches a construction caller/options defect before action: parent descriptor lacks adapter, while componentOptions dereferences d.adapter.path instead of using authenticated packaging.adapter. [Independent construction-source HOLD](tests/node-compat/foundation-crypto/independent-ownership-component-source-review-v1/results.json), index `57679053…89fb6`, verifies28/5,059 rows,5,088 unique paths and all4,934 physical packaging-role files/22 links, but withholds the required PASS on exactly CRYPTO-OWNER355-COMPONENT-ADAPTER-M1. The old template is held, with no actual component/native/crypto artifact failure inferred. A thin successor with an actual pure caller/options old-fail/new-pass seam test is being prepared after the control-directory fix; all key/component/loading/ABI/WT/runtime proof slots remain unfulfilled.

The [thin crypto adapter successor](tests/node-compat/foundation-crypto/ownership-component-candidate-v2/README.md), index `b03d1edb…34bc7`, seals20 files/5,097 references, three afterimages/23 exact reversals and15 actual-options caller pure/113 source-data/six parse checks. The genuine worker/options seam reproduces the old TypeError and succeeds with authenticated packaging.adapter, without invoking componentization or keys. New source/Root/output/peer V2 identities stay NULL pending independent correction review; old28-member donor/native/guest/WIT/tool bytes remain fixed. Independent source review is running. A separate source-only new355 HTTP integration/body-adapter audit is also in preparation; no new HTTP component or host pass is claimed.

The crypto b03 adapter correction closes the first pure caller/options defect, but source review finds a second pre-action context defect: its inherited bootstrapEntry descriptor points to the preparation repository. Identical code there derives the live old342 checkout via sibling Python helpers; the actual c3fb bootstrap proof used the configured355 staged executable. No component action is attempted. The next thin successor must keep original source provenance separate from the authenticated configured executable and bind the actual two-context bootstrap proof; native metadata/paths must not be projected or rewritten. The focused new355 HTTP analysis also confirms the inherited handler consumes direct WASI incomingRequest resources, not a Fetch Request.body. Any request-local ordinary-iterable consumer probes and later real wire-body adapter must be labeled separately; no wire-body support is inferred.

The focused [consumers355 HTTP integration source packet](tests/node-compat/foundation-stream-consumers/http-gate-candidate-v1/README.md), index `de518786…2fa10`, seals18 files/25 finite references with78 source/data/five parse checks. It is not a full execution closure or runner:publisher/whole closure/phase/host authorities stay NULL. The plan retains protected29/classic19 bodies and adds two per-request ordinary-iterable text/json fixtures, with exact6 standard0.2.10 interfaces/type-only clock and one-request-per-instance limitations. It explicitly distinguishes direct WASI incomingRequest resources from native Fetch Request.body and records the native cancellation TODO/no-op. No real wire-body adapter, resource-cancel cleanup proof, Blob/File support or new host result follows.
