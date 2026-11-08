# Public gzip response composition: actual result

The two-case profile passes in the real component1b4feb75 on engine476b/22f.
Root0c9d20/session6769 terminates0 (4ef9a5), original53251/600. Both180-second
phase owners and Wasmtime stop cleanly; current native/world guards pass before
and after. Resultc98f5472 and validation24c188d8 retain the raw comparison.
Coordinated DATA review86220bbe binds owner/world/public-log review11c365a3.

The53-byte control and deterministic2-MiB plaintext decode exactly against an
independently written Node22 builtin-zlib file reference. The large guest gzip
is2,097,810 bytes versus Node's2,097,815; both validate one member, CRC1029736345,
ISIZE2,097,152 and complete HTTP framing/socket end. Compressed byte identity
is not required. Actual public response write(false), drain, pause and resume
counters are each16; input-write(false) is32. This is observed backpressure.

Public writable finish records2,065,955 compressed bytes, then readable end
records2,097,810 before response end/finish/close. Those are public stream facts,
without a private WASI finish count. Generated responses do not prove Next's
internal redirect-fetch/native-append branches, the cause of the browser abort,
resource counts, reliability, Node parity or full Next acceptance. Diagnostic
stdout logging deliberately affects scheduling.

Source10f496d6 derives fifteen actual bindings from INITab6a0c61/98ca3f7c and
input92aa/ee72. JSON-only preparation0ed891 issues1b69cead with31 fixed metadata
values,39 build roles,17 constructor Source roles and1,742 protected descriptors
(1,650 actual source/target records). Two phase grants have no parent hash cycle.
One file-reference phase precedes one standard Wasmtime server/two GETs. The
host uses explicit --no-logging-prefix, reuse128/idle60, no app/fixture mounts
and no guest environment overrides. All13 imports remain standard WASI0.2.10.

## Offline retained check

Manifest11d9a1b9 records39 byte-identical files/6,350,276 bytes: complete reference
and wire directories plus selected owner/controller/world observations. From
the repository root:

```sh
python3 tests/node-compat/frameworks/nextjs/next-response-gzip-composition-runtime-root-results-v1/check-retained-data.py
```

The checker authenticates every byte and calls the held Python DATA verifier.
It creates only temporary copies with explicitly relocated file descriptors;
all retained original JSON stays unchanged. Python decodes the recorded gzip;
no Node, guest, server or network is run. Historical physical identities/modes
and omitted binaries/app/SDK/full-monitor/native proof are not reproduced.
New actual checks require fresh grants and outputs through the held runner.

Full Next baseline2fb8d5fd remains failed at legacy generation and strict action
capture. The [control comparison](../../../../../docs/node-compat/nextjs-completion-controls-2026-11-08.md)
and [progress](../../../../../progress.md) preserve those separate scopes.
