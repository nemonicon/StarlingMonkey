This engineering decision selects truthful backend-version constants for a future
bounded `node:zlib` implementation. It does not install or validate that module.
The sealed facade-v1 remains an unchanged compatibility-inventory template.

Reuse the selected guest zlib backend if linking and runtime verification succeed.
Expose its actual numeric `ZLIB_VERNUM`, with an explicit Node22 deviation, rather
than reporting Node's version for a different library. Do not add a second codec
solely to match this version number. A future integration must evaluate the
resulting component size and codec behavior before promotion.

The fresh pinned Node22.14 observation reports backend
`1.3.0.1-motley-82a5fec` and numeric4865 (`0x1301`). The audited Release header
declares `1.3.1` and4880 (`0x1310`). These are source/header observations; this
packet has not linked or called the guest codec. A future native build must
authenticate the actual header, archive and link command, and verify the linked
`zlibVersion()` against the selected header before its constants are admitted.
If they disagree, stop the integration rather than publishing a guessed value.

Keep the pinned Node inventory immutable. A new versioned profile overlay must
record the actual backend value and its typed deviation. The proposed private
JSAPI factory input may carry verified backend data; it is not an existing
embedding API or a new public Node export. Both `constants.ZLIB_VERNUM` and the
legacy default-object property must use that same number. Preserve numeric
`Z_MAX_CHUNK = Infinity`; JSON null is not a valid replacement. The observation
records its type and nonfinite representation explicitly.

This decision adds no host capability and does not broaden the facade's proposed
six synchronous byte-only operations. Async/streaming/Brotli/dictionary behavior
and the other deferred functions remain outside that proposal. Existing native
web compression code is only source context; its ownership paths are not reused.

Required implementation gates remain: a new facade/constant overlay, native
integration using real registration/CMake mechanisms, link/runtime backend
identity, finite export/default checks, actual component Node cross-decode and
roundtrip tests, malformed-input/output-limit/GC tests, and measured cost. Compare
decoded bytes and the bounded contract; do not require identical compressed bytes
across codec versions. Preserve strict single-member/trailing-input and option
deviations. Header inspection and the Node probe are neither guest results nor
evidence of installed `node:zlib` support.
