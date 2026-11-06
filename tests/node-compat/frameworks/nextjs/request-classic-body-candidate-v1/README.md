Measured Next JSON POST correction, Source plus host-only differential evidence.

Actual engine462/nativeUTF16 entryV2 completed22/24 HTTP assertions. JSON POST
returned400 with exactly {"marker":"NEXT_JSON_BAD_INPUT"}; the fixture awaited
request.text() successfully and its JSON.parse refused. The actual text was not
logged. Unchanged Next fromNodeNextRequest passes its original classic incoming
message directly into NextRequest BodyInit. The actual native extract_body handles
Web ReadableStream but not async iterables; unrecognized objects fall through USV
string encoding. This is a source-coupled attribution, not a logged body/decoder
observation. The host Source-contract model demonstrates the same failure without
claiming to execute native C++.

request-classic-body.mjs is a pure guest profile installer. It recognizes only
actual instances of the selected classic Readable and delegates conversion to the
already implemented Readable.toWeb. This adds no stream implementation, buffering
shortcut, native API, CMake flag, host adapter or WIT capability. It retains ToWeb's
existing16 active-adapter/16MiB chunk/64MiB cumulative limits and fixed byte-mode
ownership/encoding policy. Other BodyInit values and generic async iterables are
left to the genuine native Request; no new universal async-iterable support is
claimed. Next supplies duplex:'half'; the native constructor's broader RequestInit
support and getter ordering remain unchanged, not upgraded to universal Undici.

A construct-only Proxy targets the genuine native Request; ordinary call behavior,
name/length/prototype/static descriptors are forwarded. The genuine native
prototype is shared and its constructor data descriptor points at the current
public constructor, preserving clone/instanceof and NextRequest subclass new.target.
A fresh empty forwarding init dictionary avoids frozen original-body invariants;
getters retain the original init receiver and body is read once. Native methods are
not replaced. Proxy Function.toString reflects a Proxy rather than the original
constructor source. Installation creates no reader, stream, Promise, task or IO.
The returned restore closure is for testing/explicit rollback, not implicit cleanup.

If native construction refuses after conversion, the newly acquired Web stream is
cancelled through a captured intrinsic, retiring the ToWeb owner. The synchronous
primary thrown identity is preserved; any secondary cleanup refusal is logged with
REQUEST_CLASSIC_BODY_CLEANUP_FAILURE. This is not a promise of successful cleanup
when user destroy/removeListener hooks themselves refuse. Successful consumption,
cancellation and stream error paths use the existing ToWeb semantics and budgets.

The22 actual pinned Node22.14 host checks use the actual selected classic JS and
ToWeb implementation with a clearly TEST-only host byte kernel and Node Web APIs.
They compare the real fixture POST with stock Node for ASCII/Unicode/empty input,
check split UTF8/visible windows, unchanged invalid-JSON refusal, body delegates,
clone/subclass metadata, frozen/nonenumerable init, getter identity/receiver/order,
constructor-refusal retirement, cancellation and source-error identity. The helper
does not patch host globalThis.Request; the private test world is restored and the
shared prototype constructor descriptor is restored. This is not a native/guest
Request or body ownership proof. A separate Root-authorized component/runtime
attempt is required. Old failing outputs, app, engine and entries remain unchanged.

entry-install.fragment.mjs imports the real selected node:stream Readable and
inlines the helper byte-for-byte except its export keyword. Root owns composition,
late construction and the unchanged full24 HTTP+2 browser/cache/strict-stream gates.
