# Browser resource bytes during the strict Server Action failure

Updated 2026-11-08. The unchanged strict workload still fails on stock wasmCloud
and passes on matched Node. The new CDP observer works on the pinned Chrome and
retains2,963 response bytes in each run. Cloud ends with loadingFailed/canceled;
Node ends with loadingFinished. Cloud's artifact remains an observed prefix,
regardless of its length. Full portable Next acceptance remains false.

| Observation | Stock wasmCloud | Matched Node |
| --- | --- | --- |
| Original owner / deadline / raw exit | 67923 / 600s / 1 | 68512 / 300s / 0 |
| HTTP / portable / supplemental | 24 / 52 / 80 pass | 24 / 52 / 80 pass |
| Persisted generation | 1→2 | 1→2 |
| Stream chunks / shell / ready | 3 / 0 / 1 | 3 / 0 / 1 |
| Functional UI / assets | Pass / pass | Pass / pass |
| Original strict browser contract | Failed | Passed |
| Capture errors / failed requests | 3 / 1 | 0 / 0 |
| Streaming command / buffered prefix | Fulfilled / 0 bytes | Fulfilled / 0 bytes |
| Binary payload events / observed bytes | 1 / 2,963 | 1 / 2,963 |
| Selected terminal | loadingFailed, canceled:true | loadingFinished |
| Observer collection / complete resource | Complete / false | Complete / true |
| Browser / host / original-owner cleanup | Clean | Clean |

The cloud command starts at the first scoped request and returns before any
selected binary data event. Its empty buffered prefix and one binary piece are
retained without count-to-byte reconstruction. The piece's SHA256 is
`bcdd42019f3f13afb45e21a23d9cd04dad6faa71a51f2dc14fc750a4904808d4`.
Node's is `ff23a7fa880500332730bddc3757c95d452c1107c075e053d72674f11dcd3897`.
Equal lengths do not imply equal bodies. Complete observer collection means the
available evidence was recorded; it does not turn loadingFailed into completion.
Neither artifact is wire/chunk framing or an observation of React reader EOF.

This capture's cloud CDP order is request54, ExtraInfo55–56, response57, binary
data58, loadingFailed59, then same-document navigation60. Node records request53,
ExtraInfo54–55, response56, data57, loadingFinished58, then same-document
navigation59. These are protocol event sequences in their respective sessions,
not cross-clock causality. The earlier uninstrumented failure had a different
history/failure order. No navigation initiator, MPA, harmless cancellation or
host/transport cause is established.

The actual fresh multipart requests both contain391 bytes, with different
boundaries and hashes: cloud `699eca17…`, Node `e186412b…`. Both match their
Playwright/CDP evidence and contain the three expected semantic parts for the
manifest-selected submitFixture action. They are not replays of the earlier
`47423fde…` body. The manifest contains two actions; selection uses export,
source filename and route worker. Public nonce, actual headers and one CDP ID
qualify each observation without claiming physical host/request identity.

The new observer does not enter the original strict predicate. Worker01ca's
functional tests, body/sizes/finished capture,20-second limits, screenshot and
drain/close sequence remain preserved in the separate derivative. Extra
DevTools buffering/IPC/file publication can affect scheduling; this sample is
not a reliability measurement or a runtime fix.

All app/engine/component/served-envelope inputs remain the same: compression-off
app9106, engine237c, inner6b20 and envelopee4c7. The guest still selects13
standard WASI0.2.10 interfaces. No host modification or guest service was added.
Stock wasmCloud retains its existing configuration/mount/environment/self-origin
and normal shutdown rules. The Node bridge is unchanged. Physical application
modes do not establish WASI readonly rights or same-Store execution.

Source checkpoint`959454bc` is pushed. The
[Root packet](../../tests/node-compat/frameworks/nextjs/next-rsc-stream-observer-root-results-v1/README.md)
includes six actual syntax checks,17 actual host-Node synthetic groups, exact
preactivation corrections, Source/API reviews and the fresh2,060-input union.
The first preparation's stock-schema KeyError is retained and explicitly
qualifies the earlier Source passes; the one-span correction and successful
second preparation are separate records. No target trial was replaced.

The [Root terminal DATA check](../../tests/node-compat/frameworks/nextjs/next-rsc-stream-observer-root-results-v1/root-terminal-data-check.json)
rehashes both request/resource artifacts and records their separate outcomes.
Its simple newline-line shapes are not a validated Flight parser or an EOF
test. The [primary DATA review](../../tests/node-compat/frameworks/nextjs/next-rsc-stream-observer-root-results-v1/actual-runtime-review.json)
(`7c181b42`) and [independent gate](../../tests/node-compat/frameworks/nextjs/next-rsc-stream-observer-root-results-v1/independent-runtime-gate-review.json)
(`73c73690`) verify the split outcome. The
[raw index](../../tests/node-compat/frameworks/nextjs/next-rsc-stream-observer-root-results-v1/raw-records/index.json)
(`304e67db`) retains331 payloads/10,242,832 bytes, rehashed by Root. Both
physical35-byte generation2 records are canonical with no pending file. Cloud
config/dev stdout is complete at2,709/30,288 bytes. Bulk app/cache/native/tool
binaries are explicitly omitted under their existing guarded proofs.

The next gate is to inspect existing public guest-completion stages against this
qualified POST before adding instrumentation or changing the engine. A Source
audit is checking the actual compiled response path and ownership/finish calls.
Even a successful guest finish return would not establish React EOF or identify
who canceled the browser request. Lifecycle/resource/reuse, clean-machine
reproduction, empirical cost and production promotion remain separate work.

The [compiled-path audit](../../tests/node-compat/frameworks/nextjs/next-rsc-stream-observer-root-results-v1/native-response-lifetime-source-audit.md)
and its [Source peer](../../tests/node-compat/frameworks/nextjs/next-rsc-stream-observer-root-results-v1/native-response-lifetime-source-peer.json)
locate the active direct-WASI pump. A separate native close function ignores a
finish error result, but the current response pump does not call that function.
That is a general error-propagation defect, not an established fix for this abort.
The [public-stage DATA review](../../tests/node-compat/frameworks/nextjs/next-rsc-stream-observer-root-results-v1/public-completion-stage-data-review.md)
witnesses the named public guest POST's completion sites. Seven unknown outer
POST records still block the global join. Repeated tokens/sequences do not
identify a physical instance. A successful named API-return witness is neither
a global browser/host join nor proof of React completion.

The [outer-observer Source audit](../../tests/node-compat/frameworks/nextjs/next-rsc-stream-observer-root-results-v1/outer-observer-metadata-source-audit.md)
finds that V3 deliberately clears correlation for paths outside its exact
allowlist, even after successful standard metadata reads. The old records do
not retain which other paths they represented. A separately versioned V4 is
proposed to distinguish target/other/absent paths and preserve header
classification independently, with the same standard calls and ownership.
V3's existing join remains false; no new observer has been implemented or run.
The [Source proposal peer](../../tests/node-compat/frameworks/nextjs/next-rsc-stream-observer-root-results-v1/outer-observer-metadata-source-peer.json)
(`ebdd744b`) checks the original branches, ownership and bounded V4 proposal
without implementing or executing it.

Portable saved-failure regression check:

```sh
python3 -I -B tests/node-compat/frameworks/nextjs/next-rsc-stream-observer-root-results-v1/check-retained.py
```

It passes on all331 copied payloads and an isolated333-file copy from actual
staged Git blobs. It requires this cloud sample to remain strict/full failed
and incomplete, with Node passed and complete. It starts no targets and never
opens the recorded original paths. Optimized Python is explicitly refused so
assertions cannot disappear. [Git-mode execution](../../tests/node-compat/frameworks/nextjs/next-rsc-stream-observer-root-results-v1/retained-check-git-mode-result.json)
and [optimized-mode refusal](../../tests/node-compat/frameworks/nextjs/next-rsc-stream-observer-root-results-v1/retained-check-optimized-refusal.json)
are separate Root checks. Fresh target checks still need the pinned artifacts
and a new reviewed output namespace.

The [checker Source peer](../../tests/node-compat/frameworks/nextjs/next-rsc-stream-observer-root-results-v1/retained-checker-source-peer.json)
(`e6c76bb7`) and [three-pin DATA peer](../../tests/node-compat/frameworks/nextjs/next-rsc-stream-observer-root-results-v1/retained-checker-binding-peer.json)
(`409899a0`) perform no checker execution. The
[public-stage DATA peer](../../tests/node-compat/frameworks/nextjs/next-rsc-stream-observer-root-results-v1/public-completion-stage-data-peer.json)
(`1a0853ba`) independently corroborates the named witness and blocked global
join without transferring body-completion or physical-identity claims.
