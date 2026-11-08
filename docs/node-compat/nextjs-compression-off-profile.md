# Next compression-off diagnostic profile

Updated 2026-11-08. The new application builds successfully and now passes the
[full browser contract once on Wasm and Node](nextjs-compression-off-full-results.md). This is a standard Next configuration experiment,
not a native zlib fix or a replacement for the failed compression-enabled run.

The [fixture config](../../tests/node-compat/frameworks/nextjs/next-fs-callback-no-compress-app-build-v1/fixture/next.config.mjs)
adds only `compress: false` to the persisted-callback V2 application. The other
34 files and cache tracing exclusion remain exact. Source index`5c280e4b`
seals43 payloads/109,241 bytes. The builder changes only its fixture selector;
the original four monitored phases, Node/npm pins and native/world guards stay
in use. Source reviews and syntax checks pass.

The four original owners36534/120,36554/120,36565/600 and36633/900 complete
successfully; Root receipt`9d8c6bbb` reports buildPassed:true and runtimeExecuted:false.
The standalone inventory records2,196 files/48,805,615 bytes/431 child directories,
no symlinks or source cache. Both emitted required-server-files configs contain
compress:false and the preserved tracing exclusion. These are build/config
observations. The subsequent full browser run observes no Content-Encoding
header on either Server Action response.

The pinned guest and Node startup paths consume the emitted Next configuration.
Next's router installs dynamic compression only when compress is not false.
The existing engine, component, observer envelope, host adapters and selected13
standard WASI0.2.10 interfaces can be reused. No new guest service, engine
construction or host modification is proposed.

The build review, root identity and HTML/script asset pins are verified.
Fresh namespaces and bindings run the unchanged24HTTP/cache52/supplemental80/
generation/stream and both strict browser tests once on each declared host; both
pass. Future runs need new declared output namespaces and current input bindings.
Keep all original predicates and raw failures. This sample narrows the tested
application profile; it does not establish reliability or a compression, bridge,
backpressure, timing or cancellation cause. Full Next acceptance remains false.

Build evidence is in the [Root packet](../../tests/node-compat/frameworks/nextjs/next-fs-callback-no-compress-root-results-v1/README.md).
The [raw-after-prework result](nextjs-rsc-prework-response-results.md) explains
why this is the next bounded dimension. The production acceptance checkpoint
remains foundations-v13.

[Primary build review](../../tests/node-compat/frameworks/nextjs/next-fs-callback-no-compress-root-results-v1/actual-build-review.json)
(`9106545f`) and the [independent build/config gate](../../tests/node-compat/frameworks/nextjs/next-fs-callback-no-compress-root-results-v1/independent-build-gate-review.json)
(`d4194323`) pass. The [retained build records](../../tests/node-compat/frameworks/nextjs/next-fs-callback-no-compress-root-results-v1/build-records/index.json)
contain92 payloads/2,795,484 bytes, rehashed by Root. The new build has new action
identifiers: the earlier391-byte replay fixture remains bound to the old build
and must not be silently reused for this application.

[Fresh asset selection](../../tests/node-compat/frameworks/nextjs/next-fs-callback-no-compress-root-results-v1/asset-selection.json)
(`05c965a6`) and its [independent DATA review](../../tests/node-compat/frameworks/nextjs/next-fs-callback-no-compress-root-results-v1/independent-asset-selection-review.json)
(`a9fe908f`) verify five modern client scripts, four actions scripts forming an
exact subset, and excluded noModule scripts against the current HTML/inventory.
These records issue no runtime authority.
