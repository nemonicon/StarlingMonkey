# Chrome body-consumption control after unchanged prework

This is a Source-only design. The reported identity raw controls both return0
cleanly, with24/52/80/generation1→2/streaming followed by complete2,963-byte HTTP
bodies. Their independent review remains separate evidence. The original cloud
strict browser POST failure stays failed; no gzip, cancellation, Store or
reliability cause follows from the positive raw controls.

## Smallest selected setup

Keep the current no-compress application, inner component6b20, served envelopee4c7,
stock wasmCloud2.11.0 and matched bridged Node. Reuse byte-identical
[`prework.mjs`](../next-rsc-identity-prework-client-v1/prework.mjs) and its four
authenticated consumers. Complete and durably publish that exact workload before
starting Chrome; a collected semantic failure may continue, while incomplete
collection may not. Use a new client suite with fullOriginalContractExecuted:false
and fullNextAccepted:false, leaving01ca untouched.

Use the existing pinned Playwright1.64.1 / Chrome156.0.8078.81 resolution,
ephemeral context, CDP/NetLog and normal-close machinery from
[`browser-check.mjs`](../next-fs-callback-no-compress-browser-v1/browser-check.mjs#L148).
The new context blocks service workers and has no public-header injection,
persistent profile, cookies or new browser package. Root must freshly protect the
same six selected tool/package references; the executable hash is not an entire
Chrome-bundle hash.

Navigate once to the actual origin's exact `/actions` URL, fulfilling **only this
synthetic navigation GET/document** with a fixed empty HTML document containing
no scripts or resources. Require the callback to identify the main-frame
navigation, consume it exactly once, then explicitly await `unroute` before the
POST. Assert actual `location.origin`, `location.href`, an empty script list and
one synthetic fulfillment. Any unexpected interception fails the control. This
is declared test-harness content, not an application response or new guest
service, and creates no workload HTTP GET.

The pinned SDK supports `page.route(...,{times:1})` and `page.unroute` in
[`coreBundle.js`63254–63288](</private/tmp/starling-node-compat/nextjs-16.4.5-v13-post-77659217-replay/browser-tools/node_modules/playwright-core/lib/coreBundle.js:63254>).
Its routing enables protocol interception and disables cache while active
(37460 onward); removing the route before POST matters. Record that bootstrap
interception/cache effect rather than claiming an entirely interception-free
session. `page.setContent` alone is unsuitable: its implementation uses
document.open/write/close at25126–25144 and does not change an about:blank
document into the target security origin. A real same-origin API navigation is
an alternative, but would add an explicit workload request; it is not selected.

## Request fidelity and limits

The current [captured request](../next-fs-callback-no-compress-wasmcloud-root-results-v1/identity-request-capture.json)
contains391 bytes, its actual multipart boundary and action402ef. Decode those
bytes to a Uint8Array; do not rebuild FormData or text-encode a new body.
Fetch accepts BufferSource bodies and copies their bytes. Its request-header
guard excludes browser-controlled names; this prevents replaying the Node
flat-header array directly. [Fetch Standard](https://fetch.spec.whatwg.org/#forbidden-request-header).

| Captured group | Selected handling |
| --- | --- |
| Accept, Content-Type, next-action, next-router-state-tree, Accept-Language | Set these five captured values through ordinary window.fetch. Preserve the captured Content-Type boundary. |
| Public correlation header | Remove it, matching the selected raw replay policy; no replacement or public join. |
| Host, Connection, Content-Length, Origin, Referer, Accept-Encoding, six Sec-* fields, User-Agent | Omit these thirteen from script headers. Let the pinned browser generate them; record every observed difference. |

The forbidden subset includes Host/Connection/Content-Length/Origin/Referer/
Accept-Encoding and Sec-*; User-Agent is deliberately left browser-generated
without assuming every implementation accepts its override. Header casing,
ordering and connection history cannot be preserved as wire identity. The
synthetic `/actions` URL supplies the normal same-origin referrer context.
Keep ordinary fetch defaults rather than adding cache:no-store, keepalive or an
abort signal. Use manual HTTP redirects so an unexpected redirect fails rather
than creating another request. The expected response is200, text/x-component,
absent Content-Encoding and the existing x-action-redirect value.

After unroute, call genuine `window.fetch` once and immediately await that
response's `arrayBuffer()`, keeping both objects live in the evaluated function.
No React decoder, router action, form click, navigation waiter, fetch override,
APIRequestContext or second body consumer is selected. The returned bytes are
browser-exposed entity data, not TCP/chunk framing. A fulfilled arrayBuffer
requires full body consumption; an allocation failure can reject it.
[Fetch Body mixin](https://fetch.spec.whatwg.org/#dom-body-arraybuffer).

A4MiB retained-result cap is checked **after** arrayBuffer allocation. It is not
a browser peak-memory or preallocation bound; arrayBuffer has no byte-limit
argument. Keep an absolute20-second browser-attempt deadline and bounded cleanup,
plus the existing original cloud600/Node300 owners. Timeout/overflow/unknown
terminal is a collection failure, never an accepted cancellation. No abort or
context close occurs before success/failure or the real deadline.

## Evidence and interpretation

Enable Network/Page and request/response ExtraInfo observations before synthetic
navigation. Preserve complete semantic CDP payloads, bounded counts and NetLog,
including the real POST's headers, postData bytes, loader/frame IDs, response
headers, data counters and loadingFinished/loadingFailed. Synthetic document
events have their own explicit role. Within the CDP namespace, select exactly one
actual POST and pair ExtraInfo by that protocol request ID; do not merge it with
Playwright IDs or NetLog sources by timing.

Require the fetch/body outcome **and** a known independent network terminal
before closing. A fulfilled body accompanied by loadingFailed remains failed.
The pinned SDK's finished promise alone is insufficient: loadingFinished37714
and loadingFailed37729 both resolve request completion, and
Response.body14439–14552 later obtains its bytes through getResponseBody37805.
Use passive events here; do not use that second body API to manufacture the
arrayBuffer result. Preserve console/page/request errors without filtering.

Publish a browser-body file only for a fulfilled, bounded arrayBuffer. A rejected
body has no fabricated partial file or all-observed-byte claim. A4MiB/CDP limit,
deadline, missing ExtraInfo/terminal, abnormal browser close or publication error
must stop the matched suffix as collection uncertainty. A known body rejection
with complete observer publication and normal closure can remain a collected
failed comparison outcome. Finalize body/result/receipt and one stdout witness
using the existing durable publication primitive, but do not reuse Node-only
response.complete/socket-close/raw-capture fields as browser facts.

The minimum implementation is one new client with the unchanged prework helper,
the existing server transports with a new suite/permission selection, and the
existing Root ownership/guard pattern with truthful browser publication gates.
No new framework, engine, host, component, application build or strict-worker
change is needed. Exact header/body observations must be checked before treating
the result as this intended semantic request.

If both arms consume the body successfully, the result narrows the failure to a
different declared consumer/setup path; it does not identify React, navigation,
GC, scheduling, connection reuse or host completion as cause. The synthetic
document, omitted React/assets/counter UI, browser-managed headers and lack of a
user gesture are explicit differences from01ca. A failure can motivate the next
browser/network boundary audit, but still does not establish an initiator or
harmless abort. The original strict failure remains the acceptance result.

No retained function, browser, helper, Node, CLI or host was run for this design.
R authored related fixture/client/diagnostic Source; B independently checks the
browser API and fidelity boundaries. Runtime and authority remain unissued here.
