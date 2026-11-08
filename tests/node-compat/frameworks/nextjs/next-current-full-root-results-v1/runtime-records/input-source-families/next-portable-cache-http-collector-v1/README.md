# Shared portable-cache HTTP collector

This Source helper supplies one fixed five-request nonce check for the new
portable-cache fixture. It is intended to be imported by both future matched
Node and native clients as one physical file. It has no CLI, and import performs
no requests or output writes. Integration and actual application results remain
unexecuted here.

```js
const capture = await collectPortableCache({origin, output});
// collect has exclusively written every raw body/case record and observations.json.
const validation = validatePortableCache(capture);
// The parent saves validation separately and retains its original required gates.
```

`origin` must be a canonical `http://127.0.0.1:PORT` origin with an explicit
nonzero port. `output` must be a fresh canonical absolute directory whose parent
already exists. Existing paths, including links, refuse. The default store uses
directory mode0700 and exclusive files mode0600. The two optional dependency
injections, `fetchImpl` and `store`, are explicitly labelled in the capture and
are used by the pure tests; they supply no actual-application proof.

The exact order is GET first, GET repeat, POST revalidate, GET after, GET
after-repeat, all at `/api/portable-cache`. Each has one20s window spanning
fetch, delivered-body reads and bounded cleanup, a64KiB retained body cap, manual
redirect handling and no retry, sleep or polling. A transport/read/cancel/lock
error remains in its case; the collector attempts all five cases. On an
overflow it retains the first64KiB and records the larger delivered count.
On a partial read it retains every delivered byte up to the cap and the original
read error. Body completion means the Fetch body reader reported completion;
these bytes establish neither compressed-wire framing nor socket EOF.

The collector saves each `<id>.body` and `<id>.json`, then the complete raw
`observations.json`, before any nonce semantics. A collection storage failure
throws the original value, with best-effort capture attachment only when that
value permits. An initialization failure has zero collected records and no
attachment. Storage failure cannot admit an incomplete run. Headers are the
Fetch-exposed header pairs, with their usual
normalization, rather than raw wire headers.

The pure validator requires five exact case identities, HTTP200, complete
within-cap bytes, no transport or cleanup errors, JSON media type, exact raw
hash/base64/count joins and complete UTF8 JSON. GET has exactly the fixture
marker plus a64-character lowercase hexadecimal nonce. POST has exactly its
acknowledgement marker and `portable-fetch-v1` tag. First equals repeat; after
differs from first and equals after-repeat. The result always says
`actualNextExecutionVerified:false`; actual parent ownership, Source/app pins
and original gates are required independently. Original24HTTP, lexical cache
generation, stream, strict2browser and six supplemental cases are unchanged.
Neither this new nonce check nor a future success accepts an older failure.

Direct pinned-Node grammar checks pass for both files. The92 ordinary host pure
assertions pass using injected responses and an in-memory output store, including
wrong nonce/status/marker/tag, malformed bytes, overflow, partial reader failure,
falsy primary/cleanup errors, frozen storage-error identity and
missing-case/integrity refusal. The initial88-check result and command record
remain as preparation history; the final four checks cover attachment refusal.
A constructed
TimeoutError only checks numeric diagnostic serialization; no elapsed timeout,
network, real output/cache filesystem, Next, browser or guest runs in these tests.
Raw outputs and exact final commands are retained in `source-checks-final.json`.
These local
checks have no original monitor or OS sandbox attestation.
