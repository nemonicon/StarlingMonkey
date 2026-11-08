# Stock wasmCloud response boundary: finite follow-up

The compression-off cloud trial remains failed. Its clean original owner47197/600
returns1; functional UI succeeds, while the qualified server-action POST7 records
HTTP200, absent Content-Encoding, unavailable body/sizes and `net::ERR_ABORTED`.
This failure does not require a gzip response. It establishes neither harmless
cancellation nor an application, consumer, host or private-Store cause.

The accompanying [finite DATA/Source review](response-boundary-data-review.json)
pins thirteen files/1,889,043 bytes. Its SHA256 is
`b5e4f87aece94565f94070d963bece28bbe0890acd8abdb1d0585f9a1a68f392`
(14,318 bytes). It is analysis, not a runtime acceptance or replay. The browser
result is `4b8af225…`/234,269 bytes; NetLog is `8b0674ea…`/975,128 bytes/3,845 events.

## What the retained browser records show

Within the server-action CDP namespace, request `47636.14` has request event45,
response46 and dataReceived47, followed by same-document navigation48 and
loadingFailed49. The response is HTTP200, text/x-component and chunked, with
`x-action-redirect: /action-result?value=browser-action;push` and no
Content-Encoding. Event47 reports dataLength2,963 and encodedDataLength2,996;
these are counters, not retained response-body bytes or a body hash.

Event48 is `Page.navigatedWithinDocument`, `navigationType: historyApi`, to
`/action-result?value=browser-action`. Its frame matches the POST/response frame,
and the POST/response retain the initial actions loader. No subsequent Document
request or `Page.frameNavigated` appears in this retained test. Event49 marks the
fetch `canceled:true`, `net::ERR_ABORTED`. This supports an observed SPA history
update; it does not show a new-document/MPA navigation or identify a cancellation
initiator.

The independent Playwright namespace qualifies request7 by test, POST and path.
Node-clock trace127 records the history URL,129 the request failure,135 capture
drain,136 context-close start and137 page-close. Thus the observed failure
precedes the harness's explicit drain/close. The three body/finished/sizes errors
refer to this one failed request; they are not three independently failed POSTs.
The [unchanged worker](../next-fs-callback-no-compress-browser-v1/browser-check.mjs#L222)
performs functional work and the bounded capture drain before closing its context;
its strict [final predicate](../next-fs-callback-no-compress-browser-v1/browser-check.mjs#L317)
remains unchanged and failed.

NetLog send3685 uniquely matches retained `POST /actions`, Host50798 and the
declared public nonce8. The same local NetLog source227/start1042558362/type1
contains the matching START_JOB and200 headers. Filtered-read events3709/3713/
3717/3721/3725 report843+1552+167+126+275=2,963 bytes. Upload-init3683 explicitly
reports **net_error:0**, total391; there is no negative/nonzero net_error or
CANCELLED record in that source. It ends with READ_BODY END3729, CORS END3730 and
REQUEST_ALIVE END3731. These records do not independently prove HTTP framing EOF,
body equality, host completion or a cancellation cause. NetLog is finalized JSON
from a circular capture; global history completeness is not established. CDP,
Playwright and NetLog IDs/clocks remain separate namespaces, with no private
identity join.

## What the pinned Next/React Source supports

The actual captured router script matches the deployed
`794-ceeb732a1a81bc27.js`, SHA256 `55e42a17…`/241,744 bytes. At zero-based byte12642
its fetch wrapper is exactly `function n(e,t){return fetch(e,t)}`; that script URL
also appears in the CDP request initiator stack. The matching package
[`fetchServerAction`](</private/tmp/starling-node-compat/next-fs-callback-no-compress-app-build-v1-first/application/node_modules/next/dist/client/components/router-reducer/reducers/server-action-reducer.js:44>)
builds a POST with method/headers/body and no abort signal at75–79. At151–159 it
awaits React's decoded root, rather than an explicit whole-body EOF.

The reducer has real hard-navigation paths for external redirects and missing or
string Flight data at243–279; its internal seeded route at298–327 can navigate
within the document. The pinned
[`app-router` MPA effect](</private/tmp/starling-node-compat/next-fs-callback-no-compress-app-build-v1-first/application/node_modules/next/dist/client/components/app-router.js:243>)
uses `location.assign/replace`. The retained events do not show that effect
executing. No Flight body was retained for this failed POST, so this audit does
not independently decode which model fields selected a reducer branch.

React's
[`createFromFetch`](</private/tmp/starling-node-compat/next-fs-callback-no-compress-app-build-v1-first/application/node_modules/next/dist/compiled/react-server-dom-webpack/cjs/react-server-dom-webpack-client.browser.production.js:2078>)
starts the body reader and returns chunk0. Its reader1966–2076 continues calling
`read()` until `done`, separately from root-model resolution. No explicit
response-reader cancellation was established in this inspected action path.
The actual standalone config has `cacheComponents:false`; therefore the
[`processFetch` identity arm](</private/tmp/starling-node-compat/next-fs-callback-no-compress-app-build-v1-first/application/node_modules/next/dist/client/components/router-reducer/fetch-server-response.js:235>)
applies rather than its optional cached-navigation clone handling. The separate
halting/cancel decoder475–479 is dev/HMR gated. These Source facts do not prove
every runtime branch or explain Chromium's cancellation classification.

## Smallest next diagnostic

Prepare a separately versioned **identity-response raw-after-prework control on
stock wasmCloud with a matched Node control**. The current failed capture retains
the exact391-byte multipart request and NetLog send headers, now separately
retained in [the request capture](identity-request-capture.json), so the request
need not be invented or reserialized. Bind this actual app/action ID and envelope;
select an explicit origin-bound header policy, then run the unchanged non-browser
prework before one raw POST without React or redirect following.

Reuse the existing bounded durable raw-publication and owned-cleanup protocol,
but version the client to require absent Content-Encoding and record complete
identity body/end/`response.complete`; do not label identity bytes as gzip or
fabricate CRC checks. A complete raw result would narrow the producer-versus-
consumer boundary on this host, without accepting the failed browser gate or
identifying a cause. A later separate Chrome fetch-to-arrayBuffer control could
then distinguish a browser consumer boundary from the React action path. Neither
control may replace or weaken01ca.

No runner, authority, helper, guard, Node, browser, CLI or target was invoked by
this audit. R authored related guest/client/fixture/helper and diagnostic Source;
the review discloses that relationship. Earlier compressed/global failures and
`fullNextAccepted:false` remain unchanged.
