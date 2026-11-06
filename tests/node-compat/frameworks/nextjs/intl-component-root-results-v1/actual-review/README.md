# Four actual Intl component constructions

The Unicode, structured-stack, dependency and full Next entries all completed
their authorized **INIT-only construction** with the new V7 engine. Each has
three raw-zero owned phases—componentize/INIT, component validation and emitted
WIT—and a raw-zero outer controller. All 154 captured process records join their
terminal receipts; cleanup, signal, timeout and error fields are clean.

| Entry | Component SHA256 | Bytes |
| --- | --- | ---: |
| Unicode probe | `028ffec4e41b04395d5be02fd4b6909b2eb576eb9515d8b482a139357eb9e494` | 37,133,473 |
| Structured-stack probe | `0669b7af46647ed07be06cb2282d05a997db04265e30ab493e1677578f05717a` | 37,121,383 |
| Dependencies | `0cfdc29111bc4ca9deb9a92e4edab0c29c13f42953ff4206448f912e6f334f08` | 37,159,718 |
| Full Next | `b91ab067473181eb81996d36ecd0c30edcd151cf66467c97adb89fd69b825adf` | 37,136,170 |

All bind engine `e7baa5a9201ac8d81005294fc02cd463d75b61e43b95158512985feba995b1a5`
and whole native metadata
`cb473c7230102712b71399a70184988934cebae85d3efea6c50beecf039ed36d`.
The exact Root authority, caller index, entry/source index, plan and raw output
roles remain explicit. Original result states remain
`NEXT_NATIVE_COMPONENT_CONSTRUCTION_PASSED_UNREVIEWED_V2`; this separate DATA
review does not edit those records.

Each complete emitted world imports exactly the same 13 standard interfaces at
0.2.10 and exports only `wasi:http/incoming-handler@0.2.10`. They cover CLI
environment/stdout/stderr, clocks, random, IO poll/error/streams, filesystem
types/preopens and HTTP types/outgoing-handler. No custom or external Preview1
import occurs in the emitted interface graph. Resource types and signatures are
preserved in the complete raw WIT, rather than replaced with a list of names.
This does not infer runtime mount rights or ordinary behavior from the imports.

Every entire typed API return graph is retained. Its component Uint8Array length,
hash and file descriptor match the actual external binary. Its typed import array
reconstructs all 131 exact `(interface, function)` pairs in the separately saved
return. The `debug` return is typed undefined. This is actual API-return DATA,
not a reconstructed component or a fabricated transport.

`data.tar.gz` losslessly holds all 308 selected text records, including every raw
constructor output and outer-monitor file, the four full native-metadata input
copies, typed graphs, WIT, original authorities and small source/provenance roles.
Large component, engine and adapter bytes are external hash references. Curation
rehashed 314 original text/binary references before/final; no binary was copied.
The constructors' broader input bookends remain recorded source-coupled evidence,
not a fresh independent replay of the entire toolchain closure.

Run the portable standard-library-only reader, writing output outside this
indexed directory:

```sh
python3 -B check.py
```

It authenticates the whole text bundle, all three phase receipts and the outer
JSONL sequence (three exact monitor PID bookends followed by the final result).
It never imports the historic constructor, invokes a tool or executes an engine.

Reviewer-local collection failures are preserved: identical-byte shared files
needed distinct original-path roles; the actual graph tag is lowercase `object`;
and the real outer stdout contains four JSONL rows. The corrected reader uses
those observed schemas without changing any original output or rerunning a
constructor. Failed readers/logs remain distinct from the successful DATA review.

Construction includes the authorized guest INIT/snapshot operation. This review
itself performed no construction, engine, guest or ordinary request action.
Ordinary Unicode, stack, dependency and full unchanged Next runtime tests remain
separate; no production-profile, snapshot/reuse, security or cost acceptance is
claimed. The reviewer authored predecessor fixtures/callers and did not operate
these four Root constructions.
