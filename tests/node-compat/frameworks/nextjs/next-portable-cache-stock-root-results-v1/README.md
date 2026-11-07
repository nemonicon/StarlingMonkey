# Retained failed matched-host control

Source69323666 runs once as Root78336/original88210/300, raw1/clean/protected.
Result266d62ef/review5e709e41 retain all five500 responses,23 base HTTP requests
(one public asset pass), failed supplemental observations and the assertion
before action submission. Cache comparison, streaming and browser gates are
unobserved, not inferred failures or successes.

The primary error is `ERR_VM_DYNAMIC_IMPORT_CALLBACK_MISSING`: the existing
host compatibility loader calls Node compileFunction without its dynamic-import
option. Unsupported findSourceMap warnings remain raw. This is a control-loader
gap, not lack of Node support or a portable guest capability failure.

A separate reviewed StockV2 plus real VM seam fixes that control and later
passes its declared gates. Source and results here remain unchanged. The
Native [V1 packet](../next-portable-cache-native-root-results-v1/actual-data-v1/README.md)
retains these failed records without substituting V2.
