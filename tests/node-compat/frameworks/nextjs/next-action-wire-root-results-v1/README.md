# Exact captured action transport control

Protocolfbaeecc9 declares one native then one stock Node arm. Both actual arms
are terminal0/clean/protected: native7e442334/8123 and stock910cdddd/78985.
Native uses unchanged4afe/full02a/9e960/V5; stock uses Node22.14.0. Each sends
one captured391-byte action POST through the same reviewed common client.
No browser, new native build, app rewrite or constructor runs.

Both HTTP200 chunked messages complete normally. Raw framing dechunking equals
the separately collected encoded body; a single gzip member passes DEFLATE
completion, CRC32 and ISIZE. Native retains1956 wire/1488 encoded/2963 decoded
bytes; stock1997/1489/2963. HTTP end/capture validation precede client-owned
Agent destruction. Peer socket EOF is false on keepalive; subsequent client
closure is identified separately. All error arrays are empty.

Native owner85941 retains600s and stock86190 retains300s;1GiB start guards and
protected input/app-copy/world checks remain. Root's explicit native-terminal
receipt precedes the stock command. Root retains its actual command streams;
both output paths are fixed by the protocol and cannot be reused.

These are transport-only observations. `fullNextAcceptance` and
`applicationSemanticsValidated` are false. Opaque Flight is retained without
inventing a React parser. Explicit diagnostic header additions/substitutions
are recorded in the common Source. Earlier cache/browser failures remain
failed; no unique abort cause, reliability or resource-teardown claim follows.
See the [findings](../../../../../docs/node-compat/nextjs-action-transport-2026-11-07.md)
for exact scope and remaining work.
