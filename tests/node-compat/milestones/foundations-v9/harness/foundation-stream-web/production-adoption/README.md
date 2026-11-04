# m0.9 source adoption and native validation

The reviewed v2 integration is applied. [The source receipt](source-receipt.json)
preserves all22 after hashes and patch b007aec515b39022ef60449a6d7ad2458a48ad98910a8ae0d287952f40f8d146.
Eight generators,320 admission cases and19 configure/no-clobber cases pass.
These source/configuration results do not establish engine execution.

The separately built corrected stream/web-OFF, entropy-OFF ordinary Release
engine now passes the [native controller gate](native-controller-off-receipt.json).
Its [full report](native-controller-off-results.json) records exact302 source
inputs, stock Wasmtime42, three retained Jco calls and a fresh Wasmtime call.
Each invocation tests six state/prototype cases and16 other invalid receivers
using original native methods, with no Node wrappers. Final imports are empty.
No old unsafe prototype/DataView path, DEBUG, OOM or private memory access runs.

The OFF engine also rejects both `node:stream/web` and `stream/web` during
actual component initialization. The separate [OFF admission report](off-module-admission-results.json)
records both guest resolver errors and both bundler denials. No JavaScript adapter
fallback or successful component is counted for those failures.

The [installed ON gate](installed-native-receipt.json) now passes on the separate
new stream/web-ON, entropy-OFF engine. Its [full report](installed-native-results.json)
covers the finite18 exports, actual10 global and3 hidden native constructor
identities, native brands, canonical/bare/default/CJS/cache relationships, queued
snapshot streams,41 constructor/250 codec/four cancellation/24 BYOB guard/12 view/
six controller/67 iteration/26 DataView cases, explicit profile limits, captured
intrinsics and own error metadata. Three retained Jco calls and fresh Wasmtime
pass with zero imports; seven top-level componentizations reject as expected.
The uncached deployed-alias fixture has separate component/host results.

Known min1/fixed-unshared/local-layout/UTF8 restrictions and controller signal,
Proxy, released-reader code and constructor metadata gaps remain explicit. Both
compression constructors are callable/constructible deferred errors. This is
bounded `node:stream/web`, not full Web/Node streams or a classic Stream module.
Prior module/strict regressions and joint HTTP portability remain in progress.
Accepted v8 remains the release checkpoint until those gates complete.
