# Production HTTP component: independent pre-host review

The observed component `ccc87ae3…`,63,639,194 bytes, passes this read-only
artifact/source review. It is bound to the actual RuntimeOnly engine479821f8,
its335 frozen copies, the held778-input capability seal and exact audit/bundle/
input hashes. This is not a successful HTTP request or target-host result.
The HTTP phase pin remained null and the final capability index absent during
review; Root owns their later adoption and same-byte host gates.

The independent binary reader finds exactly six standard0.2.10 root imports
and only wasi:http/incoming-handler as an export. It directly checks clock
instance type5: only the duration u64 type, with no function declaration or
export. The recorded WIT/type graph agrees. Three embedded core modules have
no clock or Preview1 imports; the87 native core imports match the packaging
audit. This narrow parser does not repeat full Component Model validation or
execute wasm-tools.

The first verifier incorrectly expected the embedded native core's entire hash
to equal the raw final-core input hash. That source/assertion is preserved in
[history/attempt1](history/attempt1/failure.json). Independent section comparison
shows all11 noncustom type/import/export/code/data section payloads identical;
Jco wrapping changes custom metadata only (four custom sections become three).
The raw input and embedded core retain separately recorded exact hashes. No
component failure, artifact change or repackaging was inferred or performed.

All eight live computed inputs match the recorded before/after-copy checks and
current source seal; copied seven WIT files match their originals. The final
admission completion records a full778-input recheck. Packager source/core/lock
provenance, adapter selection,49 fixture/oracle modules and the protected16+4+9
corpus remain bound. No native JS facade, fatal runner or adapter fallback was
inlined. Incoming HTTP type/resource constructors do not grant outgoing-handler,
DNS, sockets, TLS, filesystem, CLI/environment or callable clocks.

Known getter-count Node1/1/0 versus guest0/0/0, Symbol.dispose registry identity
and GC co-ownership qualifications remain. Request counters establish neither
host instance reuse nor request isolation; reset/ALS/request cleanup and full
Node HTTP remain open. [results.json](results.json) records1141 read/hash paths
and all limits. No guest, host runtime, compiler, native build, packager, Ninja
or validation-tool command was executed by this verifier.
