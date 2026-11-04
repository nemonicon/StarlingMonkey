# Private-tick admission amendment: optional StreamWeb compilation

This UNAPPLIED source-only packet corrects the optional-TU assumption in frozen
[admission candidate v1](../admission-candidate-v1/README.md). It changes no live
selector, native source, recipe or accepted evidence. The original 82-test packet
is preserved and authenticated by the amendment receipt.

The reviewed `cmake/builtins.cmake` adds `stream-web-kernel.cpp` only when
`NODE_COMPAT_STREAM_WEB` is ON. Its definition is PRIVATE to `builtin_node_compat`:
the four permanent node-compat C++ files and the optional kernel receive
`NODE_COMPAT_STREAM_WEB=1`; runtime, other builtins and the embedding do not.
This differs from the strict, tick and protected-listener layout definitions.

The revised helper filters the kernel from both tick/protected all-TU coverage
when StreamWeb is OFF and checks the recorded kernel commands separately. An
enabled kernel must occur exactly once; an unselected kernel must be absent.
Requested and observed StreamWeb options must match the explicit boolean. The
private macro must match that selection on every affected target TU, remain
absent elsewhere, and cannot be represented by zero, an undefinition, a split
definition or duplicate definitions.

| Ticks | StreamWeb | Tick/protected native TUs | Strict native TUs | Embedding TUs |
| --- | --- | ---: | ---: | ---: |
| ON | ON | 61 | 4 | 1 |
| OFF | ON | 60 | 3 | 1 |
| ON | OFF | 60 | 4 | 1 |
| OFF | OFF | 59 | 3 | 1 |

The full source inventory remains 306 even when either optional C++ source does
not compile. The strict native subset contains the existing EventTarget, Engine
and EventLoop commands plus the selected tick queue; StreamWeb does not change
that subset. No dependency on StreamWeb is added to private ticks.

The [110 host-side tests](test-results.json) pass. They retain all v1 cases and
seven unchanged actual frozen legacy selections; add StreamWeb ON/OFF to all
tick/Event/GC combinations; exercise slim core-only selection with ticks ON/OFF;
and reject extra/missing kernel TUs, extra/missing kernel receipts and inconsistent
private macros or options. All new metadata and compiler-command strings are
explicitly synthetic. No compiler, engine, componentizer, VM, host or receiver
negative test runs. Real future engine-byte/configuration preflight is required.

For an independent rerun, set `NODE_COMPAT_ADMISSION_TEST_OUTPUT` to a new file
outside this frozen packet and use the pinned Node v22.14.0 executable to run
`test-admission.mjs`. Reports use exclusive creation and never overwrite an
existing result. Without that option the runner uses `test-results.json` beside
itself, which already exists in this frozen packet. The initial 110-test result
before this output-path option is preserved under `history/`.

[selector.UNAPPLIED.patch](selector.UNAPPLIED.patch) is the complete two-file
proposal against the unchanged live selector. The smaller
[amendment against v1](amendment-against-v1.UNAPPLIED.patch) changes only the helper
in a v1-staged source tree. These are alternative application forms. The staged
selector bytes are unchanged from v1.

The helper continues to authenticate the exact v1 `pins.json`, integration
policy and policy helper at their existing paths. The staged copies exist only
to load this source-only proposal unchanged during tests. Recipe 869d188…,
policy 98e80d36…, helper 78521fee…, the 306-to-304 ancestry and the independent
parent/current strict and protected policy maps are unchanged. Historical recipe
354cbc… admission is unchanged. Diagnostic engines still reject before branch
selection; private test IDs and public process remain absent. Reset/cancellation
remains OPEN. No native/runtime ordering, ALS, capability, performance, memory or
component-size result follows from this amendment.
