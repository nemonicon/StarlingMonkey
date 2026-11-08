# Current-cohort action transport pair

Both transport-only trials pass. Native Root9da74a/session64082 terminates0
(56a517), original52331/600; prepared Node Root04097a/session2709 terminates0
(a12a3f), original52580/300. Protocol ordering requires native cleanup and
protection before Node starts; Root809f55 confirms that boundary. All captured
inputs, current native/world and owned application copies remain preserved.
Coordinated DATA review52fa402d binds owner/wire reviewb6d0e86a.

The actual current391-byte POST is reused on D990/476b22f/f805 and a prepared
Node22.14.0 reference. Native resultdf55c48c/transportee6c24ad and Node
resultc8b1c642/transport8b4b2161 retain HTTP200, complete chunked messages and
single gzip members with valid CRC/ISIZE. Native wire/encoded/decoded lengths
are1,956/1,488/2,963; Node lengths are1,998/1,490/2,963. Decoded bytes and CRCs
differ. Encoded equality is checked between raw dechunking and Node HTTP data
within each arm, without a cross-arm byte-equality assertion.

This checks HTTP message EOF. Both peerSocketEndObserved values are false under
keep-alive; private agent disposal follows finalized capture. Flight bytes stay
opaque. There is no browser, React parser, application-semantic or unique-cause
claim, and the original cache/browser failures remain failed.

Held common596792c5, native owner2e33f8de and Node owner2c95a071 preserve original
prefixes and acceptance gates. The Node arm uses the held StockV2 default-loader
provider and owned cache-parent prerequisite. It is a prepared reference outside
the guest profile. Native imports remain the selected standard13 WASI0.2.10
interfaces; no custom host service or host modification is introduced.

## Offline check

`retained-raw-data-v1` contains33 byte-identical payloads/671,933 bytes, manifest
9f5c3b56. It includes both complete transport directories and selected
root/monitor/protocol/grant/world records. From the repository root:

```sh
python3 tests/node-compat/frameworks/nextjs/next-action-wire-cleanup-root-results-v1/check-retained-data.py
```

The checker authenticates every retained byte, then reuses the pinned Python
HTTP/gzip DATA parser. It runs no Node, guest or HTTP call and evaluates no
Flight payload. Original checkout inode/mode identities and omitted app,
binary, SDK and full-native protection payloads are not reproduced. A fresh
actual run needs new explicit grants, safe runIds and outputs.

The [completion-control comparison](../../../../../docs/node-compat/nextjs-completion-controls-2026-11-08.md)
records how these positive controls constrain further investigation while
preserving the full-suite rejection.
