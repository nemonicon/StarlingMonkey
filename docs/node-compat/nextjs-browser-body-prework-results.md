# Chrome consumes the RSC body after prework

Updated 2026-11-08. The direct Chrome fetch/body control passes once on stock
wasmCloud and matched Node. It completes the preceding workload, consumes the
captured Server Action response with `arrayBuffer()`, and independently observes
CDP `loadingFinished`. The original comprehensive wasmCloud strict-browser
failure remains failed. Full portable Next acceptance remains false.

| Observation | Stock wasmCloud | Matched Node |
| --- | --- | --- |
| Original owner / deadline | 59256 / 600s | 59943 / 300s |
| Fixture HTTP cases | 24 pass | 24 pass |
| Portable cache / supplemental checks | 52 / 80 pass | 52 / 80 pass |
| Persisted generation | 1→2 | 1→2 |
| Stream chunks / shell / ready | 3 / 0 / 1 | 3 / 0 / 1 |
| Chrome fetch / arrayBuffer | Fulfilled / fulfilled | Fulfilled / fulfilled |
| Status / Content-Encoding | 200 / absent | 200 / absent |
| Browser entity bytes | 2,963 | 2,963 |
| Independent selected POST terminal | loadingFinished | loadingFinished |
| Page / console / failed-request errors | 0 / 0 / 0 | 0 / 0 / 0 |
| Browser / host / original-owner cleanup | Clean | Clean |

The request uses the current build's391 captured bytes without FormData
reserialization. Script sets five captured headers. Chrome generates the other
thirteen; every observed value matches its captured value after the declared
Host/Origin/Referer mapping. The public correlation header is absent. CDP
ExtraInfo supplies the actual headers, and the sole Playwright POST supplies
the391-byte body hash. Header casing/order and wire identity are not asserted.

Exactly two browser requests are observed: one synthetic navigation GET and
the real POST. The test harness fulfills the GET with a fixed scriptless
same-origin `/actions` document and data favicon, then removes its route before
fetch. It sends no application GET. Service workers are blocked. React, Next's
client router, hydration and form submission do not execute in this document.
This setup and its routing/cache history are explicit differences from the
failed full trial.

Both selected POSTs have CDP `hasUserGesture:true`. The pinned Playwright
`evaluateWithArguments` path requests `userGesture:true`; no explicit form/click
was performed. This corrects the prospective design's assumption of an absent
user gesture. The preserved Source/design snapshots retain that earlier text;
it must not be treated as an actual observation or cancellation explanation.

The cloud body SHA256 is
`319ff1ef3829018b516dbe7c7b8bd14e591b8a31111f04a33065faad05064f77`;
Node's is `9cdc0da738d571e1470b3fdbcc3c1fd1079c94acc7e8ce1de69cca26cdf775aa`.
Equal lengths do not imply equal bodies. The contract checks actual body
consumption and semantic markers, without a fixed2,963-byte success target.
The files are browser-exposed entity bytes. CDP encodedDataLength3,381/3,400
is a separate protocol count, not a body file size or wire digest. There is no
Node HTTP-parser completion, gzip or same-Store claim in this browser control.

The4MiB retained-body limit applies after arrayBuffer allocation. It does not
bound browser peak memory. Known body rejection remains a failed result with
no fabricated prefix file. Deadline, capture overflow, missing request/terminal,
publication or cleanup uncertainty prevents the matched suffix. Result, body,
receipt and one post-receipt stdout witness use durable publication. NetLog is
closed, synced and valid JSON; circular capture does not prove complete history.

The app, engine237c, inner6b20, served envelopee4c7 and13 selected standard
WASI0.2.10 interfaces are unchanged. Stock wash2.11.0 retains two configured
mounts, three guest environment values, self-origin egress, config inspection
before one dev, registration/TCP readiness without HTTP warmup, complete
lifetime stdout and normal SIGINT shutdown. The Node reference retains its
existing request bridge. Application physical modes do not prove WASI readonly
descriptor rights or retained instance/Store identity.

The [Root packet](../../tests/node-compat/frameworks/nextjs/next-rsc-browser-body-prework-root-results-v1/README.md)
records Source/API reviews`eefe5b3a`/`b401c4d4`, all three actual syntax checks,
fresh binding`a8e8084e` with2,056 protected inputs, independent binding
review`05ad2412` and preparation`29f9fe96`. Source checkpoint`2cc06c56` is pushed.
Both preactivation observer/serialization corrections preserve exact preimages
and inverses. Root's
[terminal DATA check](../../tests/node-compat/frameworks/nextjs/next-rsc-browser-body-prework-root-results-v1/root-terminal-data-check.json)
rehashes both bodies and checks the declared outcomes. The
[independent runtime gate](../../tests/node-compat/frameworks/nextjs/next-rsc-browser-body-prework-root-results-v1/independent-runtime-gate-review.json)
(`03955d93`) passes, including actual request/body bytes, all managed headers,
gesture flags, publication and cleanup. The
[primary DATA review](../../tests/node-compat/frameworks/nextjs/next-rsc-browser-body-prework-root-results-v1/actualreview.json)
(`bc79b811`) also passes, including both physical35-byte canonical generation2
records with no pending file. Cloud config/dev stdout is complete at2,717/
22,686 bytes, with normal SIGINT0 shutdown and quiescent final stderr. The
[raw index](../../tests/node-compat/frameworks/nextjs/next-rsc-browser-body-prework-root-results-v1/raw-records/index.json)
(`44f69415`) retains239 payloads/6,882,196 bytes. App/cache/native/tool binaries
and the whole browser bundle are explicitly omitted, with existing guarded
proofs retained for those scopes.

Together with the [ordinary HTTP identity control](nextjs-identity-response-prework-results.md),
this shows complete responses for two explicitly different consumers after
prework. It does not identify the initiator of the original full-browser abort
or establish reliability. Next inspect the original React/router path with a
separately versioned observer while preserving strict worker01ca and every
original assertion. Lifecycle/resource/reuse, clean-machine reproduction,
empirical cost and production promotion remain separate gates.

The [next-boundary Source audit](../../tests/node-compat/frameworks/nextjs/next-rsc-browser-body-prework-root-results-v1/next-boundary-source-audit.md)
locates the pinned CDP `Network.streamResourceContent` API and recommends one
separately versioned observer alongside the unchanged strict workload. It can
retain browser-resource data and a terminal; it cannot observe React root
settlement, reader completion or cancellation initiator. Command support,
buffering/timing effects and complete capture remain actual-test gates. No new
observer runner has been implemented or launched.

The portable saved-sample regression check is:

```sh
python3 -I -B tests/node-compat/frameworks/nextjs/next-rsc-browser-body-prework-root-results-v1/check-retained.py
```

It passes against all239 retained payloads, request/body/terminal/publication
and prework records, both in the working tree and in an isolated241-file copy
from actual staged Git blobs. Every staged payload equals the retained bytes.
The [checker peer](../../tests/node-compat/frameworks/nextjs/next-rsc-browser-body-prework-root-results-v1/independent-retained-checker-review.json)
(`c424ab34`) verifies its Source and exact three-pin inverse. The
[Git-mode result](../../tests/node-compat/frameworks/nextjs/next-rsc-browser-body-prework-root-results-v1/retained-check-git-mode-result.json)
records Root's separate execution. The check starts no runtime and leaves
fullNextAccepted:false. Fresh host/browser tests still require the pinned
artifacts and a new reviewed output namespace.
