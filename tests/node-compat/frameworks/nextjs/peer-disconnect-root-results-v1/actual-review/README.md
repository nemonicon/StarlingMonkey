# Peer disconnect: valid inconclusive observation

Independent DATA review passes **for the preserved inconclusive result**. The
original collector and outer monitor exited raw1, with clean owned groups and
protected inputs unchanged. `observationsValid`, `functionChecksPassed` and
`withinExportIoPathsObserved` are true. `coverageComplete` and
`collectorAccepted` remain false. This packet does not relabel that outcome.

Two separate fresh stock Wasmtime42 processes used the same component, sequentially.
Each first passed an actual 8192-byte upload and exact eight-chunk/32768-byte
output. These are independent upload-close and output-close cohorts, not retries.
Both used localhost, reuse32/idle60s, no app/Source/cache mount, and the selected
standard host interfaces. Both processes exited0 after planned owned SIGINT.

| Actual case | Retained observation |
| --- | --- |
| Upload close | Declared8192/prefix1024; subsequent read invocation attempted; ordinary client.end; real WASI `last-operation-failed`; handler caught an Error whose debug message contains `HttpProtocolError`; complete HTTP400 returned. |
| Upload inspection | Known normal handler path permitted one inspection. HTTP200 retained the same JS first-label/history at ordinal4. This establishes no native cleanup count. |
| Output close | Client received the first4096 bytes, then called ordinary destroySoon. The second actual write failed with WASI `closed`; adapter-failed, producer cancel, response-reader cancel and finally were observed. |
| Output after-return | Invocation outcome remained unknown. No inspection was attempted. The owned host was discarded; after-return cleanup is inconclusive. |

All seven raw HTTP responses, complete decoded bodies, socket events, stderr,
structured snapshots and classifications are retained. The reader validates raw
framing/body bytes and actual event ordering. The upload/output cohort logs have
155/118 guest events. Host lines are retained without inventing a per-request
host completion or discard marker. An adapter-finally marker on a rethrow path
does not authorize reuse. A read-attempt marker does not prove the host entered
or suspended blockingRead. Ordinary end/destroySoon are not packet-level FIN/RST
attestation, and accepted writes are not peer-receipt proof.

The complete earlier Node22.14 localhost reference remains separately retained:
one original180s command with `--unhandled-rejections=strict`, six requests and
163 events. Its ECONNRESET/ERR_STREAM_DESTROYED observations are Node categories;
they are not converted into fabricated WASI enums. This review reruns no oracle,
client, server, Wasmtime, constructor, engine or guest.

Component `faef5c87fb611ba892485e0ab92efce3127047a3b6a44fe6f6bb09af42aa301b`
(37,142,088 bytes) was constructed with engine `4623640b…` and genuine incremental
metadata `726d69cf…`. Complete API own shape/import tuples, raw WIT, three actual
started commands and all original monitor streams are retained. All constructor
commands and its parent were raw0/clean. The 8025 whole-world guard records
28 members/eight WIT files unchanged. Actual external imports are thirteen
selected standard interfaces, all0.2.10; only the resource-typed incoming-handler
is exported. Native ancestry remains the accepted one-fresh-TU incremental
generation, not a new eighty-TU build or a projected metadata frame.

Run `python3 -B -I check.py` for an inert portable verification. `--current` also
rehashes the 212 selected original descriptors while available. `data.tar.gz`
losslessly retains 186 files (2,740,446 expanded bytes, about268KB compressed),
including whole current metadata, finite Source families and original Node/TCP
records. No component/engine binary, SDK, native archive, app or recursive build
history is copied. Current before/final protection covers finite hashes and
declared Source-family membership, not filesystem identity or all-time integrity.
`preparation.json` records the reader's initial omitted Node flag; only the
unsealed reader was corrected, and all actual evidence remained unchanged.

The reviewer authored earlier native ALS and constructor tooling and reviewed
the current Source; R authored this diagnostic/collector and Root executed it.
This is an independent readback of those executions, not an independent proof
of the native foundations.

The baseline Request.signal remains unlinked to the peer and observed false.
Typed `httpErrorCode` extraction and IncomingBody.finish trailer completion are
absent. Disposal-return logs, JS history and finite I/O paths do not prove native
resource/queue counts, root release, Store-death cleanup, physical Store identity,
idle disconnect signaling, overlapping same-Store HTTP, snapshot/reset safety,
full Next acceptance or production adoption.
