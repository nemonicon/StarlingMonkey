# Applied m0.10 source and bounded runtime evidence

The reviewed27-file v2 patch is applied. [The source receipt](source-receipt.json)
preserves its exact after hashes. It adds finite `addAbortListener` bindings,
protected native listener ordering, actual callback receivers, initialized-slot
guards and fresh records for removed once listeners. The private key is a traced
reserved SymbolValue on the existing prototype; no new static GC root is added.
Every affected C++ translation unit and embedding must share the derived layout
macro because AbortSignal slot offsets also change.

The [native evidence](../production-native-m0.10/README.md) now covers four
frozen304-input engines, both ordinary entropy modes,29 Node-derived groups,
aliases/CJS/snapshot/own errors, fatal/discard and handled reuse, eight ordinary
Release GC roundtrips and actual Events-OFF import denials. No receiver negative
runs on guard-absent OFF or old engines. The [joint HTTP gate](../../foundations/http-v10.md)
passes both unmodified hosts with identical component bytes and six selected
standard0.2.10 imports. Final checkpoint archiving is separate.

This is partial compatibility. Fresh returned-object `then` getters are read
by Node but ignored by the native EventTarget. Already-aborted queued callback
returns are correctly discarded. Node returned-Promise/thenable `addCatch`
and process error routing remain unimplemented. The target's well-known
Symbol.dispose also differs from Node's registry symbol. These are recorded
counterexamples, not normalized successes. General EventTarget/ALS/request
teardown and allocation-failure behavior remain outside the bounded proof.

The [configure-harness correction](cmake-harness-correction-v1/validation-receipt.json)
preserves the first failed run: an old artifact namespace caused a timeout
instead of exercising overwrite protection. Its corrected rerun passes19
cases against recipe354cbc8c… and CMake0155eae9…. Only the test fixture changed;
the304 compiled inputs and recipe stayed unchanged.
