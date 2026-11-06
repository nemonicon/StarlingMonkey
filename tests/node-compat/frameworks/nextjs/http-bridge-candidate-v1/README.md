# Full Next HTTP bridge control

This candidate hosts the **actual unchanged Next 16.4.5 custom-server router**
behind ordinary Web Request/Response messages. Its bridge uses real Node-shaped
Readable/Writable request/response classes, events, headers, cancellation and
backpressure. These are bounded implementation sources, not full `node:http`.
There is no raw socket listener in the guest bridge. The virtual transport's
HTTPS flag describes the incoming scheme; it does not implement TLS sockets.

## Executed results

Node 22.14.0 hosts all runs below. The original 53 MiB traced standalone tree is
copied to a fresh owned directory for each run. Only that copy's cache is reset;
application source and Next configuration are preserved. Real host FS, crypto,
process, streams, timers and AsyncLocalStorage remain in use. **No Next Wasm
component has been built or run by these tests.**

| Run | HTTP | Browser | Other observations |
| --- | --- | --- | --- |
| v1 | 0/22 observed; process exits1 | Not reached | Real Next exposed null-prototype request headers and missing `_implicitHeader`; final asset request times out. Original failures and sources retained. |
| v2 | 24/24; exits0 | Not run | Corrected bridge, cache1→2, five actual stream chunks with shell0/ready2. |
| v3-browser | 24/24; exits0 | 2/2, error-free | Real hydrated counter click and actual form-action POST/redirect, incremental Suspense and cache1→2. |
| module-v1 | 24/24; exits0 | 2/2, error-free | All application CommonJS loading goes through the candidate Module core:406 JS files compiled,412 modules cached; actual Module identity holds. Host FS/compiler/builtins/globals remain test-only providers. |

[Three bridge runs](results/summary.json) retain108 copied files/275,808 bytes.
[Full candidate-loader run](module-results/summary.json) retains47 files/198,961
bytes. These include original results, monitors, raw bodies/chunks, browser
records and screenshots. Absolute original paths in raw records remain intact;
the summary maps them to byte-exact portable copies. Large application copies,
node_modules and external tool executables are excluded. The monitor reports
clean owned groups for all four attempts, including the failed first run.

The loader integration uses [the sealed Module core](../../../foundation-module/node-module-candidate-v1/README.md)
via the explicitly test-only `module-host-provider.mjs`. It does not modify the
host's Module methods. Next's require hook operates on the candidate's genuine
mutable Module methods, and generated webpack chunks are loaded through it.
This strengthens host loader evidence; native IO/compilation and complete guest
loading remain unverified. Root source review separately found a missing packaged
inventory dependency in that candidate's generator; a successor is required.

`test-bridge.mjs` passes21 focused host checks. The separate standard WASI HTTP
adapter passes13 ownership/translation model cases: body EOF, unread-body close,
empty/large output, duplicate cookies, own-resource transfer, pre-transfer status
failure, IO diagnostic disposal, cancellation and failure cleanup. A fake-resource
test initially collided with the incoming request's `consume` method; renaming
the harness's own ownership operation corrected that test. These models do not
prove a WASI implementation or native resource behavior.

## Repeatable checks

With pinned Node 22.14.0, the following run without a server, browser or guest:

```sh
node tests/node-compat/frameworks/nextjs/http-bridge-candidate-v1/test-bridge.mjs
node tests/node-compat/frameworks/nextjs/http-bridge-candidate-v1/test-wasi-adapter.mjs
node tests/node-compat/frameworks/nextjs/http-bridge-candidate-v1/check-results.mjs
node tests/node-compat/frameworks/nextjs/http-bridge-candidate-v1/check-results.mjs tests/node-compat/frameworks/nextjs/http-bridge-candidate-v1/module-results
```

The evidence checker rehashes copies and checks complete contract bodies,
headers, actions, cache changes, decoded stream ordering and browser results.
It validates retained observations; it does not rerun the application. A fresh
actual application run uses an absent output directory and the retained external
standalone build/browser tools:

```sh
python3 -B -I tests/node-compat/frameworks/nextjs/http-bridge-candidate-v1/run-owned-host.py /private/tmp/starling-node-compat/next-http-bridge-UNIQUE /private/tmp/starling-node-compat/nextjs-16.4.5-v13-post-77659217-replay/browser-tools
python3 -B -I tests/node-compat/frameworks/nextjs/http-bridge-candidate-v1/run-owned-module-host.py /private/tmp/starling-node-compat/next-http-bridge-module-UNIQUE /private/tmp/starling-node-compat/nextjs-16.4.5-v13-post-77659217-replay/browser-tools
```

The owned launchers enforce the pinned Node and monitor hashes and300-second
deadline. Browser tools are optional. Installed dependencies and source build
must exist; these commands do not install or rebuild them. `prepare-module-host.py`
records how the separate module experiment was derived from the executed bridge
control; it refuses overwriting its generated file.

## Guest work outstanding

`wasi-adapter.mjs` uses only standard `wasi:http/types@0.2.10` resource operations
supplied by its real caller, plus standard streams/clocks/errors. `profile.wit`
and `guest-smoke.mjs` are **uncompiled templates**. The smoke is a dependency
control, explicitly not the full Next app. It currently needs the proposed native
Buffer.concat. This folder has no emitted component/import report.

Before the real app can use this adapter, implement/admit actual guest Module,
FS/process/URL/HTTP/compression/crypto and native AsyncLocalStorage. The native
HTTP factory must invoke the genuine fresh-request resource boundary; no identity
fallback may stand in for context propagation. Verify standard resource ownership,
native stream backpressure, snapshot/resumption and retained-instance cache
behavior in real components on both stock target hosts. Follow the
[Next priority roadmap](../../../../../docs/node-compat/nextjs-priority-roadmap.md).
