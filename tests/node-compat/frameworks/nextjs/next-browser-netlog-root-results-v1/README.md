# Current strict-browser NetLog pair

The native full-suite result remains failed; the prepared Node control passes.
Native Root64c124/session65557 terminates1 (4eabc5), original57224/600. Stock
Root8ab627/session19401 terminates0 (2fecb4), original57521/300. Both owned groups
are clean, and native cleanup/protection precedes stock. Coordinated DATA
reviewf3d7a9ab binds independent browser/NetLog reviewa3707d8c, all actual owners,
current native/world protection and independently checked application copies.

| Gate | Native D990/476b/f805 | Prepared Node22.14.0 |
| --- | --- | --- |
| Five persistent-cache requests /52 checks | Pass | Pass |
| Six supplemental cases /80 checks | Pass | Pass |
|24 HTTP and five stream chunks | Pass | Pass |
| Two functional browser interactions | Pass | Pass |
| Legacy cache generation | **Fail:1→1** | Pass:1→2 |
| Strict response body/finished/sizes | **Fail: three POST7 ERR_ABORTED errors** | Pass |
| Whole experiment | **Fail / raw1** | Pass / raw0 |

Native result91880401 and stock result723cc5c6 preserve every gate. The shared
browser workerf19d6c42 adds only standard Chrome NetLog startup logging to the
existing strict interaction protocol: default capture mode,16-MiB circular
target,20-MiB final-file ceiling and the original deadlines/assertions. Both
use isolated browser profiles. Source indicesc7be23d9/e697c715/db0b4eb3 retain
their historical pre-execution scope. Logging can perturb timing; a valid JSON
log does not prove that its entire history survived the circular buffer.

Native NetLogfb5facde is889,535 bytes/3,331 events; stockf2b8ea10 is899,717
bytes/3,413. Held analyzer2e577030 finds one exact-origin POST/actions
URL_REQUEST candidate in each, with one explicit dependency hop. Selected
events contain no explicit negative net error; upload initialization reports0.
Native browser/CDP records nevertheless report abort, while stock records
loading completion. Empty NetLog read-body/CORS/request end parameters do not
establish HTTP/gzip EOF, CRC validity, cancellation absence or a unique cause.
Source IDs have meaning within their own logs; they are not Playwright/CDP or
private WASI instance IDs. No cross-clock alignment is asserted.

`native-netlog-analysis-wrong-origin.json` is a preserved DATA-authoring error:
the first analysis supplied an incorrect port and found no candidate. The
explicit correction uses the origin in the actual client descriptor and retains
the corrected analysis separately. This did not rerun an application, browser,
HTTP request or host. The original failed result is unchanged.

The prepared Node arm uses the existing StockV2 VM provider/default main-context
loader and owned cache-parent prerequisite, outside the guest capability profile.
The native artifact still imports only the selected13 standard WASI0.2.10
interfaces and exports incoming-handler. No custom host service is introduced.
This pair establishes neither reliability nor full Node/Next compatibility.

## Retained checks

`retained-raw-data-v1` retains92 byte-identical payloads/5,601,728 bytes,
manifest056dabc2. Both complete browser output directories include the NetLogs,
four screenshots and response/CDP records. Finite owner records, results,
protocol/grants, reviews and the wrong-origin correction are included. App,
cache, native source, component, engine, package and tool payloads are omitted;
the native/world/app protection claims remain documentary within this corpus.

From the repository root:

```sh
python3 tests/node-compat/frameworks/nextjs/next-browser-netlog-root-results-v1/check-retained-data.py
```

The portable reader authenticates bytes and membership and independently rebuilds
the selected NetLog context and failed/passed outcome from retained DATA. It
reads no original absolute paths and invokes no Node, browser, guest or network.
Historical inode/mode identities are documentary; Git does not preserve those
permissions. The separately retained original `retained-raw-data-v1/check.py`
also checks the original private copy modes and passed on the original volume
(Rootb124d3); it is not the portable checkout command.

See [completion controls and next work](../../../../../docs/node-compat/nextjs-completion-controls-2026-11-08.md).
