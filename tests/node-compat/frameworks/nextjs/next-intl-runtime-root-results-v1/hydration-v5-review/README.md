# Actual native Next hydration V5: first and repeat

Both recorded stock Wasmtime runs passed separately. Each completed all 24 HTTP
checks, cache invalidation from generation 1 to 2, five-chunk incremental delivery
(shell chunk 0, ready chunk 2), and both browser interactions. Each browser run
has zero page errors, console errors, failed requests and collector errors.
The counter changed from 0 to 1 after the real click; the real server-action
submission reached its expected result. Both original parents and clients exited
0, and each owned Wasmtime server stopped with requested SIGINT, exit 0, no
forced cleanup and no surviving owned groups. Stderr is only the Serving HTTP
line. These results are retained separately, not averaged or normalized.

The same experimental component `55f05e3d` ran in both: engine `4623640b`, entry
`c43117a4`, entry Source `34c35012`. The deployment Source is `dd05c177`, and the
browser worker Source is `b7f4ff00` (worker `e007...`). V5 waits for actual page
load and an own data React handler before the same click/submission, with the
same 20-second per-test limit and strict error gates. It does not call the
handler manually, modify the app, relax failures or change the engine. Exact
source families and authorities are retained. The first original runtime result
is `ba3b4d5f`; the repeat is `6790ebf0`. The second issued request and the current
regression wrapper are retained as provenance; the curator never invoked them.

Each run retains its complete 136-event browser trace, 14 response-finished
observations and response-header records, two PNG screenshots, and ten decoded
body captures. Nine script fetches match five exact pinned source hashes; four
shared scripts were fetched in both browser contexts, and the counter page
script in the counter context. The tenth body is the actual POST RSC response.
The two RSC bodies are each 2,963 decoded bytes but have distinct hashes and
encoded sizes (first 1,534 bytes, repeat 1,537). They are not required to be byte
equal to each other or to the separate matched Node control. All raw values are
preserved. Playwright response.body provides decoded bytes; request.sizes
provides encoded byte counts. Wire-body hashes are explicitly unavailable.

`data.tar.gz` losslessly retains 187 unique original records (3,801,888 bytes),
including both complete runtime/client/response/monitor trees, body captures,
screenshots, issued authorities, four direct current Source families, the
unchanged request contract/app hash inventory and selected constructor DATA.
The unchanged constructor's complete raw three-phase/parent proof remains in
the separately closed body-context-v4-review; only its exact index and review
are referenced here. Its current result, typed whole return, audit and emitted
WIT are retained and joined to this component. No constructor was rerun, and no
recursive historical proof closure, app tree, engine/component/native archive,
SDK, or cache state was copied. Network-delivered JavaScript bodies are actual
observations rather than reconstructed app copies.

The curator checked 41 selected tool/Source/artifact references and every retained
original before/final collection. It also checked both current 2,218-file app
copies against the unchanged original inventory: equal hashes, independent
single-link inodes, files 0444 and directories 0555. Those are physical modes;
they do not prove read-only WASI descriptor rights. The component's raw WIT and
131 typed import pairs still select exactly 13 standard WASI 0.2.10 interfaces
and only wasi:http/incoming-handler as export. Actual host argv, component,
issued authority, loopback origin and owned monitor join the browser observations
to stock Wasmtime. The browser's generic wasmBrowserRun=null remains unchanged.

Run `python3 -B -I check.py` for a portable DATA-only read. It verifies the
closed family/bundle hashes, roles, monitors, independent unchanged 23-request
contract plus actual action POST, cache/chunk bytes, readiness/interaction
observations, strict browser gates and decoded asset hashes. The initial reader
mistake requiring identical compressed RSC sizes in both runs is preserved under
preparation-failures. The corrected reader preserves each actual value. No
engine, compiler, browser, server or guest is invoked by the reader.

This is a successful bounded regression for this unchanged fixture app and this
experimental component. The failed V4 run remains failed in its original packet.
The reviewer authored AsyncResource and FS-options facades; this is actual DATA
review, not independent certification of those Sources. No same-instance identity
across requests, reset/resnapshot safety, general Node conformance, performance,
cost, production security, external deployment, wasmCloud warm-instance support,
or public-profile adoption is established. The matched stock Node control is a
separate retained result.
