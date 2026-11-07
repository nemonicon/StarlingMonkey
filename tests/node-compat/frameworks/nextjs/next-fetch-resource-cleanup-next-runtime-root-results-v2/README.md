# Corrected full Next.js trial on cleanup476b

The comprehensive trial executes the real prebuilt Next16.4.5
application in SpiderMonkey/Wasm on stock Wasmtime42.0.1. Overall acceptance
**fails**. Node22.14.0 runs the host test client; Chrome runs ordinary client JS.
Declared React/ReactDOM dependencies are19.3.1; the captured Next-vendored browser
runtime contains19.3.0-canary-278794d7-20261002. See the
[version and consumption audit](../../../../../docs/node-compat/nextjs-server-action-next-steps.md).

| Gate | Actual result |
| --- | --- |
| Persistent-cache scenario | Five requests,52 checks pass |
| Original HTTP contracts |24 pass, including action submission |
| Supplemental concurrency/body/recovery |80 checks pass |
| Incremental stream | Five chunks; shell0/ready2; complete |
| Browser counter and Server Action interaction | Both functionally pass |
| Legacy cache counter |1→1; fails |
| Strict browser capture | POST7 ERR_ABORTED; body/finished/sizes errors |
| Ownership, source app and world protection | Clean/preserved |

Root6b9eb7/session80305 completes raw1 (terminale5ed43), original43391/600.
Result2fb8d5fd/12,866 bytes and client55d29476/275,259 bytes retain the outcome.
There are no page, console or client transport errors; strict request-failure
capture remains failed. Complementary owner/world/current-role review31017ce2
checks its declared finite scope. Coordinated outcome reviewc3a8b95b verifies
the DATA and explicitly preserves trialAccepted/fullNextAccepted:false.

Source16d093e7 restores the client's required original output prefix, preserving
all six operational files from the failed pre-HTTP configuration attempt.
JSON-only preparationcec1b4 produces authority98a39cc9 with1,781 protected
descriptors, including1,650 genuine source/target records. The accepted fresh
componentd990ecc1/37,241,086 bytes uses engine476b1c1d/metadata22f1d456,
INIT review9256cdd5 and unchanged73b/1e49 V5 entry. It retains exactly thirteen
standard WASI0.2.10 imports and only incoming-handler; no custom host capability
or host modification is added. The app remains the same31-file fixture/f805
standalone inventory. All failed earlier attempts remain unchanged.

## Offline evidence check

The retained directory contains all62 client files, including both screenshots,
plus seven Root/world records:69 payload files/1,555,648 bytes. Manifest0e0a8e28
records byte identities and original locations. Root independently compared
every copy against its original (`retained-raw-root-readback.json`). From the
repository root:

```sh
python3 tests/node-compat/frameworks/nextjs/next-fetch-resource-cleanup-next-runtime-root-results-v2/check-retained-data.py
```

The Python reader authenticates every retained byte and checks the recorded
passing subsets and both expected failures. Its own first authoring error and
correction are documented separately. It runs no JS, browser, component or
network request. Historical inode/mode records do not reproduce checkout
identity or permissions. The app, binaries, most monitor records and full
native protection inputs are omitted. New runtime checks require fresh grants
and outputs through the existing sealed runner, never reuse this failed sample
as a fresh result.

This sample does not establish browser reliability, private Store identity,
resource counts or a cause for either failure. The same engine's sixteen module
cases and eight public Fetch groups pass separately. Next work investigates
request/module state and Server Action response completion before broadening
native API scope. Foundations-v13 remains the accepted production checkpoint.
