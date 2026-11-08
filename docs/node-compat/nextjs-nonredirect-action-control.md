# Non-redirecting Server Action control

The new `/action-value` page uses React `useActionState` and a real Server Action
to return and render one bounded string on the same page. It exercises ordinary
action-response consumption without a redirect. Existing redirect fixtures and
their failed strict results remain intact.

The first fixed Wasm→Node bridge comparison completes once per arm. Both render
the returned value, capture all five authenticated script bodies and capture one
POST200 with an89-byte decoded body, fulfilled `response.finished()` and complete
transfer-size observations. Neither records a failed request or observer error.
Both controls nevertheless fail their unchanged browser-error predicate: the
new fixture supplied an invalid HTML `pattern`, producing a console error.
The [runtime DATA review](../../tests/node-compat/frameworks/nextjs/next-nonredirect-action-root-results-v1/actual-runtime-review.json)
retains those failed results and the [raw packet](../../tests/node-compat/frameworks/nextjs/next-nonredirect-action-root-results-v1/runtime-records/manifest.json).

HTML compiles this attribute in UnicodeSets mode. The corrected fixture uses
`(?:[a-z0-9]|-)+`, keeping the server validator, action, React consumer and all
other33 fixture files unchanged. It retains the browser console-error gate.
See the [HTML Standard](https://html.spec.whatwg.org/multipage/input.html#the-pattern-attribute).
All264 host-Node pattern checks pass. A genuine separate v2 Next build completes;
its runtime comparison remains pending.

Both versions use pinned Next16.4.5, React19.3.1 and Node22.14.0. The Wasm arm
reuses the unchanged experimental `6b20` component inside `e4c7`; no native
engine, component or host modification is needed. The deployed lazy loader reads
the separately built mounted app. All thirteen external imports remain standard
WASI0.2.10. The Node comparison uses the same request bridge and module provider
as the earlier comparison; it is not a pristine standalone-server control.

The worker preserves the original network observer,20-second deadline and
500ms/2s capture drains. Each fresh version requires genuine app inventory,
generated asset pins, source/constructor/composition admission and new output
paths. Its controllers refuse to overwrite evidence. These control-only results
do not rerun or accept the full24HTTP/cache/stream/browser contract, resolve the
earlier redirect failure, establish a cancellation cause, or promote production
beyond foundations-v13. Existing diagnostic route classifiers do not admit
`/action-value`; no public guest/native/outer join is claimed for this route.
