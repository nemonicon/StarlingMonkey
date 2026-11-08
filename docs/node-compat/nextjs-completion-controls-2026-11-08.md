# Current response-completion controls

Two new normal-input controls pass on the cleanup generation. They preserve the
failed full Next result2fb8d5fd: legacy generation1→1 and strict browser POST7
`ERR_ABORTED` remain failed. Neither control runs a browser or establishes the
abort's cause.

| Control | Actual result | Limit |
| --- | --- | --- |
| Captured391-byte action POST, current D990/f805 Wasm app | Complete chunked HTTP message; one gzip member; CRC3836962956;2,963 decoded bytes | Fully drained without navigation; opaque Flight bytes |
| Same POST, prepared Node22 control | Complete chunked HTTP message; one gzip member; CRC1384681350;2,963 decoded bytes | Prepared host/provider; decoded bytes differ from native |
| Generated gzip composition, current1b4f component |53-byte and2-MiB plaintexts decode exactly; CRC/ISIZE/HTTP completion pass against independent Node builtin reference | Generated responses, without Next/internal redirect/native-append branch proof |

The action-wire original owners52331/600 and52580/300 exit0/clean. Native result
df55c48c/transportee6c24ad and prepared Node resultc8b1c642/transport8b4b2161
retain one POST each. Native wire/encoded lengths are1,956/1,488; Node lengths
1,998/1,490. Both report HTTP message EOF; peer socket EOF is false because the
diagnostic uses keep-alive and destroys its private agent after final capture.
Equal decoded lengths do not mean byte equality or successful React parsing.
Coordinated DATA review52fa402d binds independent owner/wire reviewb6d0e86a and
the native/world/current-app-copy evidence.

The gzip composition original53251/600 and both180-second child owners exit0,
with current inputs and world preserved. Resultc98f5472 and validation24c188d8
pass. The2-MiB guest member is2,097,810 bytes; Node's is2,097,815. Both decode to
the same deterministic plaintext and CRC1029736345. Large-response public
write(false), drain, pause and resume counters are each16; input-write(false)
is32. Backpressure coverage is observed rather than inferred from payload size.
Coordinated DATA review86220bbe binds owner/world/public-log review11c365a3.

The public log demonstrates the completion distinction: gzip writable `finish`
occurs at2,065,955 compressed bytes, while readable `end` occurs at2,097,810,
after the final drain. The remaining31,855 bytes arrive before response end,
finish and close. This supports the tested public ordering; it counts no
private WASI finish calls or resources. Diagnostic logging may affect scheduling.

## Repeatable retained checks

The [wire corpus](../../tests/node-compat/frameworks/nextjs/next-action-wire-cleanup-root-results-v1/README.md)
retains33 files/671,933 bytes. The
[gzip corpus](../../tests/node-compat/frameworks/nextjs/next-response-gzip-composition-runtime-root-results-v1/README.md)
retains39 files/6,350,276 bytes. Standalone Python checkers authenticate the
payloads and reuse the held HTTP/gzip DATA parser without Node, guest or network
execution. The gzip checker makes only a derived temporary path-relocated JSON
view; retained originals remain byte-identical. App/binary/full native proof
payloads and physical checkout identities are not reproduced by these corpora.

## Browser NetLog comparison

Keep native runtime changes behind a discriminating observation. The client
[Source audit](nextjs-server-action-next-steps.md) permits Flight-root/UI
completion before transport EOF but found no explicit cancellation in the
inspected production action path. A separate Chrome NetLog pair now completes
with the same interactions, assertions and deadlines. Native result91880401
still fails legacy generation1→1 and the three strict POST7 `ERR_ABORTED`
checks; prepared Node result723cc5c6 passes every declared gate in one sample.
All52 persistent-cache,80 supplemental,24 HTTP, five stream and two functional
browser checks pass on both arms. Original owners57224/600 and57521/300 terminate
cleanly with raw1 and raw0 respectively. Coordinated DATA reviewf3d7a9ab binds
independent browser/NetLog reviewa3707d8c.

Chromium
documents startup capture and its size limit in
[its capture instructions](https://new.chromium.org/for-testers/providing-network-details/).
The diagnostic retains default capture mode, a requested16-MiB circular buffer
and a20-MiB final-file ceiling. The native889,535-byte log contains3,331 events;
Node's899,717-byte log contains3,413. Each contains one exact-origin POST/actions
URL_REQUEST candidate. In the selected request plus one explicit dependency hop,
neither has an explicit negative net error; upload initialization reports0.
Native public browser/CDP records still report abort, while Node records loading
completion. Empty read-body/CORS/request end parameters do not establish HTTP or
gzip EOF, CRC validity, absence of cancellation, or a unique failure cause.

The initial native DATA analysis used the wrong origin and found no candidate.
That report and its authoring correction are retained; the corrected report uses
the origin from the actual client result. No actor was rerun for this correction.
Missing or evicted history remains unobserved; logging can perturb timing.
Network source IDs identify records within one log, never private WASI instances;
Playwright/CDP IDs and timestamps are not equated with them. See the
[NetLog results and retained checks](../../tests/node-compat/frameworks/nextjs/next-browser-netlog-root-results-v1/README.md).

## Next investigation

The positive completion controls and the inconclusive NetLog boundary do not
justify a speculative runtime patch. The current D990/f805 pair now passes the
bounded stock wasmCloud cold8 contract, raw0/clean/protected; coordinated DATA
review0ed0e4c2 passes that scope. Full Wasmtime browser/cache failures remain open, with
per-request guest state distinct from shared durable cache behavior.
The [pinned host audit](nextjs-wasmcloud-mount-egress-source-note.md)
records fresh P2 Store creation, read/write mount descriptor rights and the
explicit deny-all HTTP egress policy. Broader self-HTTP/action tests need a
separately selected exact-origin policy and retain the original acceptance gates.

The matched browser `Accept-Encoding: identity` diagnostic now completes with
every original strict gate. Native resulte0deb8d2 still fails legacy1→1 and
three strict POST7 ERR_ABORTED checks; prepared Node result0e560a52 passes.
Both verify explicit NetLog send headers and absent response Content-Encoding.
Original owners65026/600 and65237/300 terminate cleanly with raw1/raw0;
coordinated DATA review8151dc47 binds independent browser/owner review27751124. See the
[identity results](../../tests/node-compat/frameworks/nextjs/next-browser-identity-root-results-v1/README.md).

Simply requesting identity was insufficient in this sample. The context-wide
setting also changes navigation and assets; changed transfer sizes/timing limit
a causal interpretation. Pinned Next filters this header from its internal
forwarded request, so this does not prove inner native-fetch encoding or append
selection. Next is a Source-only bounded deployed guest completion diagnostic
using existing public response events and adapter EOF/disposal/finish returns.
It needs no additional body reader, fetch wrapper, native change or INIT I/O.
Separate request objects and lane-local diagnostic tokens must not be treated
as private identities or unique causal joins. No such trace component has run.
