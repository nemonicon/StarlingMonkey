This dormant SOURCE packet implements `retainedSecretBootstrapPreflight({configDescriptor})` in its real original directory. It imports Node built-ins only, writes no files, launches no processes, and never imports or calls the original one-shot API, original verifier/helper, or serialized historical callable. Importing it launches nothing. The new Root config and independent Source-peer slots remain null until separately reviewed and issued.

The API authenticates its complete own Source family, declared physical input ledger, fixed source/proof families, the actual 8298/88b1/12662 bootstrap review and the full unchanged 41-field fc86 DATA. It rehashes all referenced source, tool, library and protection inputs, requires exact retained output/frozen membership, checks private frozen modes and independent frozen/original inodes, and preserves old normal membership. All 75 raw metadata fields and eleven full manifests remain intact. Original API, configured source, original build, frozen native/embedding source and selected frozen engine are separate physical roles.

The returned record is new and finite:

```js
{
  schemaVersion: 1,
  kind: 'retained-secret355-bootstrap-v1',
  sourceIndex,
  actualReview,
  historicalBootstrap, // full unchanged deeply frozen DATA
  currentVerification: {
    helperInvocations: 0,
    originalApiInvocations: 0,
    historicalRecheckInvocations: 0,
    processesSpawned: 0,
    filesCreated: 0,
    // current Source/config/protection facts and closed action flags
  },
  recheck // fresh closure over this API's read/hash/context checks only
}
```

The old `historicalBootstrap.currentCompleteVerifierCalls === 1` remains a historical fact inside its unchanged object. It is not a new current call count or admission state. The record does not spread or decorate that historical object. Its recheck is newly created and returns undefined after current checks; the old function is neither deserialized nor reused. Initial and final/failure checks repeat full protection; if both primary work and final protection fail, both errors are retained in an AggregateError. The API uses host SHA-256 only for file evidence, with no application cryptography or keys.

`future-component-caller-contract.json` gives exact record checks, physical field mappings and caller ordering. A new separately reviewed 355-aware caller must authenticate this Source/config/peer before import, use the full historical metadata/manifests with its actual frozen engine path, and await the new recheck before and in final/failure paths around any independently authorized operation. Read-only verification does not grant a component, engine, guest, key, GC, backend, module or runtime action. Old c3fb/GC/342 selectors, source-context rebinding and metadata projections are forbidden.

Preparation may read/hash existing evidence, parse Source and run extracted pure guards on synthetic DATA. It must not invoke this real preflight, its fresh recheck, or any historical API/helper/callable. `prepare-source.py` copies only the exact original read/hash primitives into the new original module; operational donor bodies are excluded. `test-pure.mjs` evaluates only extracted pure guard/record functions and never imports the actual API. Grammar checks execute no module. Actual current-verification results remain absent.
