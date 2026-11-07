# Captured Server Action transport control

Root ran exactly the two predeclared arms in protocolfbaeecc9: native first,
then matched Node after native terminal cleanup/protection checks. Both complete
raw0/clean/protected. These are **transport-only passes**, not full Next runtime
acceptance or acceptance of any previous browser/cache failure.

The native arm uses unchanged4afe component/full02a engine/9e960 metadata/V5
entry, the fresh2,181-file app and the same thirteen standard WASI0.2.10 imports
on stock Wasmtime42.0.1. The control uses Node22.14.0 and the same app/bridge.
There is no browser or navigation. Each sends one POST with the captured
391-byte body (ad790726…17ab), action ID, form fields and observed header map.
Referer changes to the leased origin. Host, Origin, Accept-Encoding:gzip,
Connection:keep-alive and Content-Length are explicit diagnostic additions;
they were not all observable in the earlier Playwright header map.

| Observed boundary | Native | Node control |
| --- | --- | --- |
| Original owner | 85941 /600s, raw0 | 86190 /300s, raw0 |
| HTTP status/framing | 200/chunked, complete | 200/chunked, complete |
| Encoded gzip bytes | 1,488 | 1,489 |
| Captured response wire bytes | 1,956 | 1,997 |
| Decoded opaque Flight bytes /ISIZE | 2,963 | 2,963 |
| CRC32 | 2240993554 | 898968594 |
| One normal-final gzip member | Pass | Pass |
| Dechunked bytes equal Node HTTP encoded body | Pass | Pass |
| Request/response/socket/cap/cleanup errors | Empty | Empty |

HTTP message end and final raw-data-listener capture occur before deliberate
private-Agent destruction. The peer socket did not end first: it remained a
keepalive connection, which the client then closed. Do not equate HTTP EOF
with server socket close. Full decoded payload hashes differ and are preserved;
equal length does not imply equal opaque Flight semantics.

Native result7e442334/8,123 bytes and stock result910cdddd/78,985 bytes remain
at the protocol's fresh output roots. Wire/framing/gzip checks run before client
cleanup, with partial raw/encoded prefixes retained before validation. Existing
1GiB admission, original600/300s owners and20s/2MiB wire+encoded/4MiB decoded
bounds remain. No retry, app/host/native change or interface widening occurred.

This shows that the selected native producer can complete this action response
when the client drains it without navigation. It does not trace the earlier
browser's cancellation cause, prove reliability/native resource destruction, or
parse React Flight/application semantics. The separate cache1→1 failures remain.
Independent/coordinated DATA verification passes. The sealed182-member packet
capsule passes its portable/current reader and Root independently reads every
archive member and live original. These DATA checks have their own records
under the [Root results](../../tests/node-compat/frameworks/nextjs/next-action-wire-root-results-v1/).
