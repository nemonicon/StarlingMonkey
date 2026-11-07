# Server Action response-consumption investigation

The corrected cleanup native sample still reaches the action-result UI while its POST 7 ends `net::ERR_ABORTED`. The pinned client Source permits the UI/root Flight result to resolve before response EOF, but the inspected production action path contains no explicit response-reader cancellation or POST AbortSignal. This explains why functional success and failed transport observation can coexist; it does **not** identify the cancellation or missing-completion cause. The strict failure remains failed.

This investigation read only the completed native/StockV2 captures and pinned local Source. No JavaScript, Node, browser, HTTP, compiler, guard, evaluator or fault probe ran, and no application/host/runtime code changed.

## Version and Source selection

The application dependencies declare Next **16.4.5**, React **19.3.1** and ReactDOM **19.3.1**. Its captured App Router browser bundles actually contain Next's vendored React **`19.3.0-canary-278794d7-20261002`**. `createVendoredReactAliases` selects `next/dist/compiled/react` and `react-server-dom-webpack/client.browser` for the browser client (lines 289–315). That wrapper selects the production Flight client. Both captured shared chunks contain the canary version, and the 241,744-byte chunk contains the action reducer/Flight exports. Native and StockV2 captured the same shared asset hashes.

This is a browser-client finding. It does not establish one React version for every server layer or replace the declared package versions with a broad server-version claim.

## Inspected consumption chain

Paths below are relative to the `node_modules` Source root listed in the hash table.

1. `next/dist/client/components/router-reducer/reducers/server-action-reducer.js`, `fetchServerAction` (44–79), encodes the form arguments and sends POST with `Accept: text/x-component`, action ID and router-state headers. Its fetch init has method/headers/body and **no signal**. `segment-cache/fetch.js:21–28` forwards this init to browser fetch; the optional testing-lock path also forwards it.
2. The reducer reads `x-action-redirect` and content type (107–151), then awaits `createFromFetch` (152–157). For the internal redirect it uses `processFetch` to handle the optional completeness-marker stream. It reads the root fields and proceeds to the redirect/navigation (235–255, 298–331). The redirected action promise is rejected with a *handled redirect* error, and seeded navigation receives a NULL HMR signal (326). This rejection is control flow, not a fetch abort call.
3. The production Flight client, `createFromFetch` (2078–2088), starts `startReadingFromStream` and immediately returns `getChunk(response, 0)`. Model-chunk initialization can fulfill that root (764–781, 806–859, 902–908) while the reader continues asynchronously (1966–2076). There is no `reader.cancel()` or AbortController in this response-reading loop. Read errors call `reportGlobalError` (876–885); already fulfilled root/UI data need not be undone by a later read error.
4. `app-router.js`, `HistoryUpdater` (73–112), writes `history.pushState`/`replaceState`. Its full-page fallback separately uses `location.assign`/`replace` (253–271). `app-router-instance.js` marks superseded actions discarded (151–166), without aborting their fetch there. `redirect-boundary.js:57–68` recognizes the reducer's handled redirect and avoids another router push.

The cancellation matches found elsewhere have narrower roles. `fetch-server-response.js:386–479` closes/cancels a wrapper for a **dev-server, enabled HMR-cancellation flag and supplied signal**; the action chain above supplies no such signal. Its static/shell cache-clone cancellation at 295–342 concerns unused clones, and action responses are explicitly not written into the segment cache (reducer 307–314). React's `processReply` AbortController at 157–188 belongs to request-argument serialization, not the response decoder. These are not evidence that the production action deliberately cancels this POST after history changes.

## Current native versus prepared StockV2

The native browser record is `05cd3b4de0138e1818d5f8b8bd8ec1b672e82e95bc9ba55fd9c9405091aad61d` /224,752 bytes at `/private/tmp/starling-node-compat/next-wasmtime-deployment-cleanup-476b-next-corrected/client/browser/result.json`. The prior prepared Node StockV2 record is `3fd40d1cea4544f89fa29e2390a5e28b12468dcb899928a3c16a5976be1ae61e` /229,111 bytes at `/private/tmp/starling-node-compat/next-portable-cache-stock-v2-portable-cache-stock-v2-first/browser/result.json`. The arm identity comes from parent process/component records, rather than browser-origin telemetry alone.

Both send a 391-byte form with action `4018730ebe8dc9bc100be933e21dabdfa132c639ab`, fields `_1_$ACTION_ID_<id>`, `_1_value=browser-action`, and `0=["$K1"]`. Raw body hashes differ (`cc609fbe…` native, `974a4ff6…` StockV2) with their multipart boundaries. Both receive HTTP 200, `text/x-component`, gzip/chunked, the same no-store/vary/cache/prerender values and `/action-result?value=browser-action;push`. Stock additionally records explicit Connection/Keep-Alive response headers; those differences alone establish no fault.

The following are observer-arrival deltas from each capture's own Playwright POST-response event, **not** cross-process performance measurements or browser causal timestamps:

| Recorded event | Corrected native | StockV2 |
| --- | ---: | ---: |
| Action-result main-frame URL event | +7.431 ms | +4.283 ms |
| POST terminal | requestfailed +41.641 ms | requestfinished +1.316 ms |
| Explicit context-close phase starts | +74.217 ms | +50.186 ms |
| Body / response.finished / sizes | three abort failures | all captured/fulfilled |

CDP identifies the action-result navigation as **`Page.navigatedWithinDocument`**, not a recorded full-document unload. Native CDP delivers three data events of 2,395 +293 +275 = **2,963 decoded bytes**, then `Network.loadingFailed` with `canceled:true`; no loadingFinished is recorded for that POST. StockV2 records 2,963 decoded bytes, loadingFinished and body SHA-256 `5652e9efa08e70591b1da9a8390833b5fd99a7662c58964fe23d200fc5cdb03f` before its history navigation.

The native failure is recorded before the harness explicitly closes its context. History navigation precedes it, which is correlation rather than a cancellation callsite. Equal decoded lengths do not prove equal payload bytes, complete Flight semantics, a valid native gzip trailer, or HTTP EOF: native `response.body()` and encoded sizes remain unavailable. Both functional browser cases pass; the native strict browser gate and legacy cache 1→1 gate remain false. The earlier successful no-navigation wire controls used an earlier component/application cohort and cannot supply this sample's missing EOF evidence.

## Next discriminating boundary

Before changing Next, the guest, compression, host behavior or assertions, obtain evidence for the current action's **transport EOF versus local cancellation boundary**. A bounded follow-up can reuse the existing reviewed action-wire control mechanism with the current D990/f805 cohort and captured form/headers, fully draining without navigation and checking HTTP framing plus gzip CRC/ISIZE. It would need its own genuine Source binding/Root grant; none was prepared or run here. A successful drain would still leave the browser cancellation origin unresolved. A failed drain would expose a producer/framing invariant to investigate. Existing failures and gates must remain available in either outcome.

## Exact local Source hashes

Source root: `/private/tmp/starling-node-compat/next-portable-cache-app-build-v1-first/application/node_modules/`. These files had unchanged physical read bookends. The table is a finite Source reference list, not a package/tree execution attestation.

| Relative file | Bytes | SHA-256 |
| --- | ---: | --- |
| `next/package.json` | 3188 | `76f5b7ef447577c2855eee017ae8a47aeefc1e4c95e71387b66c2671283682c8` |
| `react/package.json` | 1242 | `9cc9c3de5441a2eea7f41f52f3f2a15a4fc51f90c0b72741f0d7638643a85e67` |
| `react/cjs/react.production.js` (version at 565) | 18040 | `0b5529981841afa1b58c76ba85c29bb681ff5f07cd8cde6a10b967d3915b8e1c` |
| `next/dist/compiled/react/cjs/react.production.js` (version at 565) | 18065 | `dbffee51e4b1dce16f20b1b964325cec696cf8897c7cd16fff174dc9e3e94139` |
| `next/dist/build/create-compiler-aliases.js` | 30896 | `e23179f25cd5f9c3caea5279f7c455eed47678b7b6694f86eb4c5b874f11fccb` |
| `next/dist/client/components/router-reducer/reducers/server-action-reducer.js` | 20696 | `45d9f7de636d847174881f3005082d5bce90399c745fba2dc3fd4ea402832950` |
| `next/dist/client/components/segment-cache/fetch.js` | 1379 | `378770d930578c5103083c029f8e388c4315ec67666d5843b2ddfc8af9469061` |
| `next/dist/client/components/router-reducer/fetch-server-response.js` | 29577 | `fba387124134c7becf61938ca1ce38738220a554a97931ad745ed4976c989a51` |
| `next/dist/client/components/app-router.js` | 25900 | `453b67488a13ff8c365e8c6ea7c6f3d6f9dd302afe37062c6a0e625d6e340fd4` |
| `next/dist/client/components/app-router-instance.js` | 11229 | `679a2c335d4a849eb14c997d80ddd356fbd7789f50c0777ceabd0525d1e77807` |
| `next/dist/client/components/redirect-boundary.js` | 3588 | `88861b4754b13c7d235974e7d05b960f5247b3bdbc86a01e2eb7dc06ff81455a` |
| `next/dist/compiled/react-server-dom-webpack/client.browser.js` | 254 | `4225884493381174db42ea47deef8b52ec41e358e63b49acd4929fe2f97f7a69` |
| `next/dist/compiled/react-server-dom-webpack/cjs/react-server-dom-webpack-client.browser.production.js` | 66983 | `0d40cfb00481266eb93a204bcb86265619493908f29d049817c6cc7a97ffe30f` |

Actual shared browser assets: `794-ceeb732a1a81bc27.js`, 241,744 bytes, SHA-256 `55e42a1727ceefd5974b3ba5d35ce152d56f1a46f73f038d82b7fe8c1fe7f8fc`; `4bd1b696-c7408084347438ae.js`, 203,721 bytes, SHA-256 `7d5ccf185a6f85ab38ce400a7f10aa0a3496eb4e9aee1e500a85e01c4222fcec`. Both arms' captured bodies match those declared source asset pins. No React Flight payload was evaluated by this investigation.
