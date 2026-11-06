# Full Next standalone packaging diagnostic

This is an isolated **host-only** prototype against the exact retained Next16.4.5 build from `2026-11-06-post-77659217-replay`, Node22.14.0 and Rolldown1.2.16. The original three diagnostic runs did not change the production bundlers, fixture or any baseline. A separately authorized production bug fix and its fresh checks are recorded below. The diagnostic never imports/evaluates an application or generated bundle, starts a server, invokes ComponentizeJS, builds native code or runs a guest. All original outputs remain unadmitted diagnostics.

The [summary](results.json) and twelve byte-exact text receipts in `evidence/` preserve three clean bounded host processes:14 bundle attempts,4 diagnostic bundles and10 refusals. Each process had a180-second deadline, raw exit0, empty stderr, no termination signals/timeouts and no remaining owned group. Expected packaging refusals are recorded inside the successful diagnostic process. Generated bundles, including the22.67MB broad scan, remain external; their hashes are retained.

The actual generated standalone entry is ESM, not an ordinary CommonJS file. It imports `node:path`, `node:url` and `node:module`, constructs `module.createRequire(import.meta.url)`, changes cwd/process environment, then calls the genuine Next `startServer`. Removing the old strict transform produces a one-module bundle with the real loader still present; it has not bundled Next. Seven unguarded `process` references and two unadmitted native imports remain. Existing `next-standalone` Wasm probes only import this entry and expose export keys under `run()->string`; they do not implement an HTTP-serving workload.

Rolldown already handles ordinary `.js` CommonJS package sources, lazy module caches and package-relative imports. The existing official `esmExternalRequirePlugin` owns native CJS-default bridging. The prototype uses that mechanism, explicit `node` resolution conditions and production NODE_ENV. It does not supply a runtime `require`, process shim, builtin adapter or host service.

One concrete production-policy defect was confirmed: checking the **requested string** for `.node` before resolution rejects Next's `./stream-ops.node`, `./react-server.node` and `./debug-channel-server.node`. Actual resolution yields ordinary `.node.js` files for all three. The prototype's real resolver accepts those targets while separately identifying a real Darwin sharp `.node` binary. Production code was unchanged during those original experiments. An unresolved `react-server-dom-webpack/server.node` is also not proof of a native binary: unresolved package-subpath policy must stay distinct from executable-file classification.

The complete installed-package exploratory scan reached1772 modules and emitted41 Node builtin imports,28 absent from v13, plus161 source loader uses and61 warnings. Its generated code still has unprovided ambient references. It explicitly externalized Node/asset edges for analysis and is **not** a closed or guest-admissible bundle. In particular, that result is not transferred to the traced standalone tree.

The final replay resolves the server library exactly through `createRequire(actualStandalonePath).resolve(...)`, without evaluating it. The resolved `start-server.js` is `2beb0e08…/25819`. Even with all Node and asset edges diagnostic-only, Rolldown refuses four genuine missing relative files in the traced tree: `lib/upgrade/nudge`, `pages/_app`, `pages/_document` and `pages/_error`. Those exist in the broader install but were omitted by the runtime trace. The final scan reached932 transform inputs and64 loader uses; no server bundle or acceptance was manufactured. The strict-v13 variant separately refuses `node:url` at the standalone entry and `node:os` at the server-library root.

The smallest honest packaging change is to retain the original finite profile contract, use the already-existing general CommonJS package mode and official external-require bridge, and classify executable assets **after resolution**. This does not remove the need for an explicit module-registry/createRequire/require.resolve/cache/page-file policy. Dynamic Next require hooks and computed page loading remain real requirements. Full HTTP also requires genuinely implemented/admitted process, filesystem, URL, async context and server/transport APIs; the real `startServer` calls `http.createServer`/`server.listen`. No subset renderer is substituted for the full app.

The first diagnostic reproduced the request-suffix mistake; its exact script is kept in `preparation-history/first-run.mjs`. The next used the broad installed package context, retained as `installed-package-run.mjs`. The final script uses exact standalone resolution. All original raw reports remain intact, including the mistaken and narrower results.

To repeat the final **host-only** diagnostic while the exact retained external build/toolchain exists, choose an absent output directory:

```sh
/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node tests/node-compat/frameworks/nextjs/standalone-bundler-diagnostic-v1/run.mjs /private/tmp/starling-node-compat/next-standalone-bundler-diagnostic-v1-UNIQUE
```

Run it under a finite owned-process deadline as in the retained180-second terminal receipts. It refuses changed generated-artifact hashes and does not install/rebuild missing inputs. The Source transform ledger describes observed inputs, not complete physical package-resolution closure. Broad scans and unprovided optional branches do not prove every recorded dependency is needed on every production request.

## Production resolved-target fix

The authorized harness fix now lives in `framework-package-bundler-v2.mjs`. Asset-looking literal requests use the real resolver and reject an actual `.node`/`.wasm` target or unresolved/external asset. A load guard also rejects executable targets hidden behind ordinary package main/exports names. Explicit native manifests, aliases, the official external-require bridge and all final import/loader/environment checks remain in force. The original finite profile bundler and retained corpora are unchanged.

[Fresh validation](resolved-assets-fix-results.json) records16 focused real-resolution/bundle checks plus all28 existing host package differential tests, all passed with two clean raw0 processes. Focused checks use the exact three Next source hashes, ordinary `.node.js`/`.wasm.js` sources with canonical Buffer imports, an actual sharp addon, native/Wasm binaries including hidden package exports/main, unknown package/asset requests, and native/host-adapter escape attempts. The existing host test evaluates bounded toy modules on Node; the focused test evaluates no application or bundle. One expected unknown-package resolver warning is retained in focused stderr.

All three actual Next targets now resolve to JavaScript. The debug-channel module bundles under the existing policy; stream-ops reaches unadmitted `async_hooks`; react-server reaches unresolved `react-server-dom-webpack/server.node`. These are genuine subsequent blockers, not full Next acceptance. No compiler, native build, componentization or guest operation occurred.

Reusable host-only commands, each with a fresh external output path and finite process deadline:

```sh
/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node tests/node-compat/frameworks/nextjs/standalone-bundler-diagnostic-v1/test-resolved-assets.mjs /private/tmp/starling-node-compat/next-resolved-assets-v1-UNIQUE
/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node tests/node-compat/frameworks/package-bundler-execution-v1/host-test-v2.mjs /private/tmp/starling-node-compat/package-bundler-v2-resolved-asset-regression-UNIQUE
```
