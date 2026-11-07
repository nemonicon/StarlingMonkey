# Peer-disconnect diagnostic Source and Node reference

Held, uncompiled and unexecuted guest Source. The only network workload here is
the explicitly authorized pinned Node22.14.0 **localhost reference** under the
original owned 0af monitor, cap180s. It completed on its first attempt, raw0 and
clean. No WASI guest, componentizer, engine, native build, DEBUG, GC/OOM pressure,
fault injection or reset ran. Future target/Root/review slots in `plan.json` are
NULL. This is not an implementation of peer-linked Request.signal.

The guest exports only `incomingHandler` in the existing `next-http` world8025:
13 standard WASI0.2.10 imports, eight fully referenced WIT files, no custom host
service. The generated raw entry inlines own modules and the held neutral/fresh
readiness join. INIT declares functions and creates readiness metadata only;
bootstrap, ALS state, actual streams and timers are ordinary-call only. No app,
FS mounts, keys or entropy workload is needed. Root must separately review and
grant construction and runtime.

## Genuine adapter and observations

`adapter-diagnostic.mjs` is an explicit descendant of held
`next-component-candidate-v3/adapter-descendant.mjs`, with whole diff and input
descriptors. It preserves that adapter's EOF/error/drop/finish policy: direct or
own-data ComponentError.payload `closed` closes input; unknown/falsy throws keep
identity; real error-resource debug calls are synchronous and resources disposed;
normal EOF still consumes IncomingBody.finish and immediately disposes its
**uninspected** future. Output errors cancel the actual response reader and
rethrow. No AbortController or resource prototype patch is introduced.

Logs surround actual operations. `input-read-invocation-attempt` is emitted
**before** blockingRead, so it does not prove the host entered or suspended that
read. `input-read-returned` records actual received bytes; failed logs surround
only the actual read import. `dispose-returned` is emitted only after the real
Symbol.dispose call returns. It does not attest native registry counts or object
destruction. The donor drop helper propagates throws; the diagnostic keeps that
policy. Reader-cancel and pre-entry cleanup suppressions are labelled separately.
As in the donor, a throwing sequential finalizer can prevent later drops; missing
finally/inspection evidence is failure or inconclusive, never guaranteed cleanup.

An initial grammar preimage is retained for the two guest-only files. After the
TCP reference completed, success logging was moved outside actual dispose/write
try blocks and read-failure logging narrowed around blockingRead itself, so a
logger failure cannot be mislabelled as failure of an already-returned import.
The final two files passed separate owned Node grammar checks. No TCP reference
was repeated; its actual common/handler/Node backend bytes are unchanged and the
reader joins those bytes to the original source ledger. Original phase records
and original before/final descriptors remain historical evidence, not a claim
that every later authoring file still has its earlier digest.

## Bounded controls and actual Node result

The shared Web handler uses real public streams and the selected real ALS/timer
backend. Upload declaration8192, partial prefix1024, output at most8×4096 bytes,
one active producer timer and no intervals. Per-factory request/event caps are
12/192. The25ms producer yield is pacing, not a guarantee that the peer closed
before a particular write. No JS global context stack or Promise patch exists.

The Node-only adapter uses actual http, net, Readable.toWeb, Web streams and
AsyncLocalStorage. It contains no fake WASI resource backend. All connections
target its one fresh exclusive127.0.0.1 listener with an OS-selected port.
`end`/`destroySoon` are ordinary close APIs, not packet-level FIN/RST attestation.
Real Node request/response events retain Node labels and are never translated
into fabricated WASI stream variants.

The first actual reference, origin `http://127.0.0.1:64252`, retained all six
requests and163 events:

| Case | Actual observation |
| --- | --- |
| Healthy upload |8192 bytes, HTTP200, complete=true |
| Healthy output |HTTP200,32768 bytes, exact eight finite chunks |
| Partial upload |1024 bytes returned, next read invocation attempted, client end; Node read ECONNRESET; handler catch/finally; automatic Node HTTP400 retained |
| Upload inspection |HTTP200, same JS first-label, ordinal4, retained history |
| Output close |Client retained first4096 bytes then destroySoon; a later actual write callback failed ERR_STREAM_DESTROYED; producer and reader cancel returned |
| Output inspection |HTTP200, same JS first-label, ordinal6, retained history |

The shared Request had no peer-linked signal and remained un-aborted even though
Node's own request emitted aborted. This is a measured **baseline gap**, not a
Node/WASI transport-parity success. Both inspect replies show JS-factory
continuity only. The partial-body reader.cancel rejected with the original
ECONNRESET and was explicitly retained as a suppressed secondary failure.
Final sockets0, waiters0, forced cleanup=false. All six original phases and two
final grammar phases were0/clean with original terminal fields checked.

Future actual guest acceptance must retain the full raw client bytes, stderr and
typed outcomes first. Input `closed` alone is not HTTP completion proof. Output
cancellation coverage requires an actual later write/flush failure plus observed
cancel/finally paths; if all bounded writes queue successfully, that case is
inconclusive. A different/discarded Store or changed factory tag leaves
after-return cleanup inconclusive. No idle independent disconnect signal,
native owner expiry, post-Store-death disposal, snapshot/reset, GC-root release,
overlapping same-Store HTTP or full-Next/adoption claim follows.

## Portable DATA check

Run `python3.12 -B -I check.py` from any directory. It authenticates the indexed
Source/retained bytes, all eight owned terminal/stream/argv joins, whole Node
stdout/stderr events and actual client HTTP/chunked bodies. It executes no JS,
process, network, custom Source or guest. `host-raw.tar.gz` contains all40 raw
text files losslessly (391955 expanded bytes); no binary/SDK/app payload.
`run-host.py` is the historical single-use authoring driver, not the portable
check command. Existing raw outputs are preserved and must not be overwritten.

The author also wrote the earlier context fixture and selected facade; this
packet is Source preparation and host reference evidence, not independent guest
certification. The accepted design and WIT/host limitations are recorded in
[the lifecycle plan](../../../../../docs/node-compat/nextjs-context-lifecycle-plan.md#peer-disconnect-design-review-2026-11-07).
