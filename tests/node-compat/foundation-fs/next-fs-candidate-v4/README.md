# Explicit native dependency transfer in the FS generator

This Source-only successor changes exactly two installed files:
`builtins/node-compat/generate-fs-factory.mjs` and its generated
`fs-factories.generated.h`. The generated wrapper now explicitly passes
`kernel`, `Buffer`, `Readable` and `nextTick` instead of spreading the native
argument object. C++ defines those four properties with flags0: they are
non-enumerable DATA, so the old spread lost all four values.

The actual first corrected-path construction reached Wizer but failed while
installing builtins at factory line56, `ReadStreamImpl extends Readable`.
That failed output and FSv2/v3 remain unchanged. `failure-and-audit.json` binds
the exact raw failure and Source joins. The finite generated-factory scan found
only FS copying native arguments this way; other matching HTTP spreads operate
on serialized JSON inventory constants. This is not a whole-program guarantee.

`test-native-record.mjs` evaluates the actual preserved and corrected generated
wrappers against a C++-shaped non-enumerable/writable/configurable dependency
record. Nine cases reproduce the old TypeError at line56, construct the corrected
wrapper before any kernel IO, verify supplied Readable/Buffer/kernel/nextTick
identities and owned-buffer window, leave descriptors unchanged, avoid an
unrelated getter and refuse a missing Readable without fallback. It uses host
Node Buffer/Readable and a labeled in-memory kernel contract; it is not native
SpiderMonkey, standard WASI or guest proof.

The copied existing FS host suite also passes all41 cases with no retained
handles. It retains the prior real host FS/stream/Next atomic-cache controls and
their explicit TEST-ONLY dependencies and limits. The generator and --check
passed under pinned Node22; two grammar checks passed. Tests that write host
result files must not be rerun in this sealed family. The separate native-record
test is read-only with respect to Source and can be rerun as a host regression.

`composer-mappings.json` gives exactly two mappings with installedPath, exact V5
before bytes and afterimage descriptors. The five other after/ files are
byte-identical generator support inputs, not overlays. Apply only those two
overlays to a new Source successor; do not replace the whole registrar or
modify prior native/build/failed component packets. The existing435 native
paths, C++ bodies, flags, manifest and public experimental m0.20 policy are
unchanged. Root's new installed check must invoke this genuine FS --check.

No new SDK/compiler/build/link/Wizer/engine/guest action occurred here. Native
embedding of the changed header, component INIT and full Next runtime remain
pending separate actual Root phases. This fixes argument transfer and grants
no production-profile or runtime acceptance.
