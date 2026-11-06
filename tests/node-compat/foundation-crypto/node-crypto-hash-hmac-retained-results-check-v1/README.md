Run the portable retained-data check with pinned Node22.14.0:

```sh
/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node tests/node-compat/foundation-crypto/node-crypto-hash-hmac-retained-results-check-v1/check-results.mjs tests/node-compat/foundation-crypto/node-crypto-hash-hmac357-runtime-validation-v1
```

Exit0 means both arms contain seven complete retained guest strings with ordinals1,2,3,1,1,1,1, validated by sealed a6 comparator `compareHashHmacSequence`:14 guest records,280 accepted comparisons,112 separate native policy checks. Exit1 means missing, changed, malformed, incompatible or semantically failing records. JSON summary goes to stdout; errors go to stderr. Redirect output outside the immutable indexed dataset.

The directory form verifies every indexed payload, exact whole membership (including nested indexes), regular files and recorded SHA256/byte lengths before importing the pinned pure comparator+contract. It checks the real Node four-frame JSONL `observed.type/value` structure, literal Jco strings, and Wasmtime decoded `type/value/expectedCallOrdinal`. It never follows historical original paths embedded in retained JSON. A relocated same-byte dataset works. Files and membership are rechecked before returning.

The CLI also accepts a JSON manifest with exact top-level keys `schemaVersion:1`, `comparator:{module:descriptor,contract:descriptor}`, `fixtureManifest:descriptor`, `nodeOracleStdout:descriptor`, and `arms:[{id,jcoRetained:[descriptor,descriptor,descriptor],jcoFresh:descriptor,wasmtimeDecoded:[descriptor,descriptor,descriptor]},...]`. The exact arm IDs are `bundled` and `raw-fixture`. Each descriptor is `{path,sha256,bytes}`; paths may be absolute or relative to the manifest. All seven guest roles per arm must name distinct files. Comparator/contract/fixture version hashes are fixed; the comparator must retain its real adjacent `contract.mjs` dependency. Explicit manifests authenticate their selected descriptors, while the directory form additionally authenticates all indexed evidence.

Namespace object identity is reported as observed, separately from the finite accepted-value comparison. Current bundled records observe identitytrue (bundler canonicalization), while raw native imports observefalse versus Node'strue. The checker preserves that deviation without claiming whole Node parity. Provider identity, runtime backend identity, public admission, freeze, snapshot, reuse, security and cost acceptance remainfalse. SHA256 is used only to authenticate files; no new Hash/Hmac workload, oracle, process, component, Wasmtime, native engine or guest call runs.

Meaningful DATA tests, including actual records, relocation, missing/tampered files, duplicate arms/roles, changed returns, wrong ordinals/types and version/dependency mismatches:

```sh
/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node tests/node-compat/foundation-crypto/node-crypto-hash-hmac-retained-results-check-v1/test-check-results.mjs
```

This checks retained records and manifest consistency. It does not independently reconstruct component provenance, process cleanup, native ownership/erasure or all historical authority proofs; those remain the separately retained reviews. A newly authored index/hash manifest is not itself independent authority.
