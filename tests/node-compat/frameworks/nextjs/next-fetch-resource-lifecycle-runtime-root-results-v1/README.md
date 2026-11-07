# Public Fetch lifecycle comparison on cleanup476b

The first actual run finishes with raw exit0 under the original600-second owner
(Root tool4bbfd8/session45152, terminal87c9a3; original PID40184). Both separately
owned phases exit0, the Node server remains alive across them, and normal server
shutdown passes. The whole native/world checks pass before and after. Controller
result9f043eeb records all eight public groups passing against the independent
Node22.14.0 reference. Coordinated DATA review705270ee passes, binding the
complementary owner/world review37ab2610. C's later context readback3f77 is
explicitly postlaunch; Root's own672e2d preflight preceded execution.

Sealed runtime41ad0bd9 uses seven unchanged operational/model modules and two
unchanged grant templates. JSON-only preparatione1517c derives authoritydf18f1d8
from the genuine lifecycle INIT4b3b0f43/e0bb7bc6 and full build41857258/476b/22f:
31 metadata fields,39 build roles and1,743 protected descriptors, including
1,650 actual source/target records. Three separate phase grants share explicit
loopback origins without a parent-hash cycle. Root read-only preflightb0cdc0
finishes0 and actual actor admission repeats the genuine checks.

One host GET produces eleven guest outgoing Fetch requests/eight declared groups:
ordinary EOF and metadata, text/JSON/arrayBuffer readers and second-read errors,
four sequential reads, clone with one branch cancelled and the other drained,
pending-read cancellation, and cancellation after a read. The same existing
Next standalone server supplies both reference and guest phases; the guest has
no app/fixture mount. All thirteen emitted capabilities remain standard WASI0.2.10.
This is public behavior evidence, without a native resource count or a full
Next.js, private Store identity, complete cancellation or causation claim.

`retained-raw-data-v1/manifest.json` records twelve byte-identical copies of the
actual response/reference, controller/owner records and verifier streams
(46,035 bytes). It records original locations and modes separately from the
repository copies. It omits binaries, the application, most monitor logs and
source/tool payloads; it cannot reproduce their current integrity or execution.
The existing sealed DATA verifier can check the retained public observations
offline, from the repository root:

```sh
python3 tests/node-compat/frameworks/nextjs/next-fetch-resource-lifecycle-probe-candidate-v1/verify-data.py \
  --capture tests/node-compat/frameworks/nextjs/next-fetch-resource-lifecycle-runtime-root-results-v1/retained-raw-data-v1/guest-response.json \
  --node-reference tests/node-compat/frameworks/nextjs/next-fetch-resource-lifecycle-runtime-root-results-v1/retained-raw-data-v1/node-reference.json
```

That command reads DATA only. A new actual execution requires fresh grants and
output locations using the sealed actor; historical authority/run outputs stay
unchanged. No full Next acceptance or production promotion follows from this run.
