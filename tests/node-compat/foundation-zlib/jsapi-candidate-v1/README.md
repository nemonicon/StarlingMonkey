# Native zlib JSAPI wrapper proposal

This is an **uninstalled, unlinked template**, not `node:zlib` support. It adds
no CMake option, registry entry, JS facade, public export or host import. The
parent owned-byte kernel and its 86 host vectors remain unchanged. The final translation unit passes the accepted v12 SDK30/SM147 Release syntax
command with empty diagnostics. No object or linked guest exists; real target
execution is required before selecting this code.

The private `run(Uint8Array, format, encode, outputLimit)` contract covers only
the parent's defaults: one complete zlib/gzip/raw member, at most 1 MiB input
and 16 MiB output. It refuses shared, resizable and detached backing. The future
facade must normalize string/BufferSource overloads and observable options,
preserve Node Buffer identity, declare six synchronous exports precisely, and
provide explicit refusals for the rest of the pinned Node22 inventory.

The input and backing objects are rooted. Staging allocates before acquiring a
payload pointer, then bytes are reacquired and copied inside a no-GC scope.
No borrowed JS pointer reaches the codec. Codec storage remains malloc/free
owned; the result is copied once into a rooted JS-owned Uint8Array. Native
partial bytes never escape on failure. No allocator transfer or zero-copy
claim is made. Allocation failure returns immediately with an OOM exception.

The error mapping is a proposal: truncation/data errors use zlib codes;
dictionary and trailing/multiple-member rejection have explicit profile codes.
Messages, errno details, options/coercion, constructor/callback behavior, GC,
limits, gzip headers and concatenation deviations require Node22 differential
and target tests. The existing native web compression classes are not invoked.
No DEBUG/OOM/fault/private-memory experiment is part of this template.

[Source receipt](source-receipt.json) records the final source and exact SDK
command/results. [Independent source review](source-review.json) reports no
concrete blocker within this template scope. The earlier syntax source/result
remains under history/first-syntax; its primitive-number boxing check was
corrected before the final syntax run. The output cap bounds result bytes,
not peak memory, codec allocations, staging or realloc overlap.
