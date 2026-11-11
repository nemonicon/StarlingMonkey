# Next.js outer observer V4

Updated 2026-11-11. V4 builds and passes seven HTTP probes inside a real
component on Wasmtime 42.0.1. This closes the observer metadata test gate;
the comprehensive Next.js browser failure remains unresolved.

V3 discarded correlation classification when a method or path was outside its
allowlist. V4 preserves the independently observed header state and distinguishes
an exact target path, another present path, and an absent path. It retains the
same standard WASI getters, fields-child release, one owned request/outparam
transfer and post-import stdout operation. It does not read the request body.

The new observer is 5,771 bytes. Its composition with the unchanged 37,156,919-byte
diagnostic inner component validates. Raw child bytes, shared nominal resources,
sibling instances and the inner handler's explicit canonical post-return were
checked. The composed external surface remains exactly 13 WASI 0.2.10 interfaces:
io/error, io/poll, io/streams; clocks/monotonic-clock, clocks/wall-clock;
http/types, http/outgoing-handler; cli/stdout, cli/stderr, cli/environment;
random/random; filesystem/types and filesystem/preopens. The sole export is
wasi:http/incoming-handler@0.2.10. No host or engine modification was made.

The original 900-second owner (PID 22795) completed with exit 0, no timeout,
forced cleanup, signals or surviving observed processes. Each of seven fresh
Wasmtime processes handled one request and exited normally after SIGINT. All
HTTP responses and stdout captures completed; input checks passed before and
after the run.

| Request | Header input | Observed path status | Observed correlation |
|---|---|---|---|
| POST /actions | One valid value | present-target | valid, count 1 |
| POST /actions | Missing | present-target | missing, count 0 |
| POST /other | One valid value | present-other | valid, count 1 |
| POST /actions?probe=1 | One valid value | present-other | valid, count 1 |
| POST /actions | Two values | present-target | duplicate, count 2 |
| POST /actions | Uppercase value | present-target | invalid, count 1 |
| HEAD /actions | Missing | present-target | missing, count 0; method unknown |

All responses have the diagnostic fixture's expected status 405. POST bodies
match its expected JSON; HEAD has zero received body bytes. These responses test
metadata and forwarding, rather than application endpoint acceptance.

Independent Source review and composition review are recorded alongside the
[primary metadata review](../../tests/node-compat/frameworks/nextjs/next-standard-handler-observer-v4-root-results-v1/actual-metadata-runtime-review.json).
The [raw packet](../../tests/node-compat/frameworks/nextjs/next-standard-handler-observer-v4-root-results-v1/raw-records/index.json)
retains 70 files / 2,233,749 bytes, including complete host/owner captures,
response bodies, per-case results, the emitted WIT and composition skeleton.
The portable checker reads only that packet:

```sh
python3 -I -B tests/node-compat/frameworks/nextjs/next-standard-handler-observer-v4-root-results-v1/check-retained-v2.py
```

The finite wire model covers 48 variants, with a maximum of 314 bytes within the
512-byte record buffer. Absent path, getter failure, allocator exhaustion and
the per-instance record limit have no new real-host coverage. Fixed 64 KiB guest
memory does not bound host allocation; lowering large metadata can still trap
before forwarding. The historical model-source and mistyped-digest preflight
refusals occurred before target launch and remain saved with their corrections.

The tested observer is now also composed around the unchanged Next.js inner
component `6b2084d0`. The new envelope `9da63790` is 37,298,765 bytes; all four
composition/validation/inspection steps pass with the same 13 standard imports.
The [Next composition review](../../tests/node-compat/frameworks/nextjs/next-standard-handler-observer-v4-root-results-v1/actual-next-v4-composition-review.json)
verifies raw children and canonical structure; nine tool records are retained.
The [independent composition peer](../../tests/node-compat/frameworks/nextjs/next-standard-handler-observer-v4-root-results-v1/next-composition-data-peer.json)
also passes.
This envelope has not yet run the Next.js workload.

The hardened saved-data reader checks file-size bounds before payload reads,
canonical paths and read bookends. It passes both the current packet and an
isolated 72-file copy reconstructed from actual staged Git blobs; optimized
Python is refused. The initial reader and its evidence remain preserved.

Next, prepare a fresh V4 runtime binding and repeat the unchanged strict browser
workload. Only that fresh V4 sample can use the revised
join policy; the seven unknown V3 POSTs cannot be retrospectively classified.
Absent path, unknown method/getter and incomplete or ambiguous capture still
block joining. The [client-consumer Source audit](../../tests/node-compat/frameworks/nextjs/next-standard-handler-observer-v4-root-results-v1/client-consumer-source-audit.md)
maps the captured browser bundle to the selected action/Flight reader code.
React root settlement remains distinct from reader EOF, and no cancellation
cause is established. Lifecycle, resource retirement/reuse, clean-machine
reproduction, cost measurements and production promotion remain outstanding.
