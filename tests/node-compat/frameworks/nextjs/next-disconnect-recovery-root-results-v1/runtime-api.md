# Probe runtime API

Fixed order Wasmtime600 → cloud600 → matched stock300. Actor CLI remains `node run-wasmtime.mjs AUTH`, `node deploy-cloud.mjs AUTH`, `node run-stock.mjs OUTPUT APP_SOURCE UNUSED_TOOLS RUN_ID AUTH`. Client CLI is `node run-client.mjs ORIGIN OUTPUT UNUSED_TOOLS RUN_ID`. Exact prefixes are `/private/tmp/starling-node-compat/next-disconnect-recovery-{arm}-v1`; exact runIds `disconnect-recovery-{arm}-first`. Per-client output is host output plus `/client`.

New authority states: ROOT_NEXT_DISCONNECT_RECOVERY_{WASMTIME,CLOUD,HOST}_AUTHORIZED_V1. New permission disconnectRecoveryProbeAllowed=true, controlOnly=true, browserAllowed=false, rscStreamObserverAllowed=false. Existing actual guest/standard-handler/host permission fields retain their target-specific meanings; Node guest/engine execution stays denied.

Client suite NEXT_DISCONNECT_RECOVERY_CLIENT_V1 has controlOnly=true/fullOriginalContractExecuted=false/fullNextAccepted=false. Actor copies probeExecuted, collectionComplete and cleanupComplete before checking status/pass. Successful bounded collection has19 cycles/114 declared calls. These are probe completion fields only, not the old HTTP24/cache52/supp80/UI/fullOriginal gates. Unknown publication/capture/cleanup/globaldeadline stops the suffix. Known retained protocol or semantic failure can be reviewed and continued by Root without retries or pass rewriting.

Exact pure admission helper and baseline construction/tool/browser data roles are reused unchanged; documentary browser refs do not imply browser invocation. All selected app/cache/source/capture/lifecycle contracts remain the prior passing ones. Actual new client/index, Source indexes/plans, fresh protected union and authorities remain pending until Root metadata preparation.
