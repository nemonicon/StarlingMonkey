# Hash/Hmac complete-return DATA comparator

This is source-only reusable validation for the unchanged fixture V2 (index
`16b195e6…`) and the already retained Node 22.14 oracle (Root `5a449c2a…`, DATA
review `aa9a3ef4…`). It neither imports the fixture nor invokes crypto, a provider,
an embedding, generated code, Wasmtime, an admission helper, or an oracle.
Actual guest/component/Root slots remain `null` in `references.json`.

The caller must authenticate the complete source family and all actual inputs,
and durably retain each entire typed raw string or unexpected return/throw plus
process evidence **before** this comparator. A validation exception cannot stand
in for the missing raw evidence. These functions grant no process, component,
runtime, snapshot, alias-resolver, provider, erasure or security authority.

```js
import {
  validateHashHmacNodeOracle,
  compareHashHmacReturn,
  compareHashHmacSequence,
} from './comparator.mjs';

const oracle = validateHashHmacNodeOracle(nodeRawStrings, { fixtureManifest });
const checked = compareHashHmacReturn(retainedWholeRawString, {
  expectedCallOrdinal: 1,
  nodeAcceptedRecords: oracle.acceptedByOrdinal[0],
  fixtureManifest,
});
// checked = { record: completeParsedRecord, rawString, comparison }
```

`compareHashHmacSequence({nodeRawStrings, guestRawStrings, fixtureManifest})`
requires exactly three Node strings (ordinals 1/2/3) and seven guest strings
(retained Jco 1/2/3, fresh Jco 1, three fresh Wasmtime 1). It does not invoke or
attribute those transports. The caller must prove the actual schedule. Ordinals
are checked as returned, never replaced or normalized. All four fresh ordinal-1
guest records must equal the first complete guest JSON, including diagnostics.

The comparator enforces exact ordered 20 accepted IDs and all typed values,
complete SHA256/RFC HMAC answers, input/chunk/window/output ownership flags and
terminal behavior. Hash repeated digest must throw; Hmac repeated digest must
return an empty string/Buffer. Only finalized error **messages** are diagnostic
for Node parity: they are retained completely, while error names, codes and all
other positive fields are compared. Opaque/missing/unexpected positive returns
or cleanup throws are rejected.

The eight native policy records are checked separately. The retained stock Node
oracle accepts six operations refused by the bounded native profile, and its
invalid-receiver code is `null`; those observations remain intact. Native
refusal names/codes, zero algorithm conversions, and required cleanup digest are
enforced without claiming Node parity. All 13 alias booleans, 68 namespace names,
71 default names and complete typed descriptors are validated. Native named and
default binding types and frozen default flags follow the genuine facade; Node
descriptor/object identity is separate DATA, not a native equality target.

The nine native numeric constants follow the pinned guest OpenSSL headers in
`references.json`, including OpenSSL 3.0.17's header number `805306640`. Node's
whole constants record is kept separately. No backend/provider identity follows
from these header numbers. `expectedNativeConstants`, if supplied, must equal
the fixed table; it cannot weaken the expectations.

Run read/hash-only input validation before host-only tests:

```sh
python3 tests/node-compat/foundation-crypto/node-crypto-hash-hmac-data-comparator-candidate-v1/check-inputs.py
/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node tests/node-compat/foundation-crypto/node-crypto-hash-hmac-data-comparator-candidate-v1/test-comparator.mjs
```

The tests read three actual retained Node strings and create clearly labeled
**synthetic** native strings. They exercise strict counts/IDs/types, independent
native policy expectations, full hex values, aliases/constants, duplicate JSON
keys, malformed/oversize data, unchanged ordinals and whole same-ordinal guest
comparison. The first synthetic descriptor model copied Node's deprecated
`Cipher=undefined`; its raw failure is retained, then the model was corrected to
the actual facade's callable surface. No actual native guest observations or
fresh crypto/oracle results were produced. Source preparation and raw command
outputs are retained; `command-observations.json` reports host DATA/grammar
subprocess exits only, with no invented monitored workload evidence.
