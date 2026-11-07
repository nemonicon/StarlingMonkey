# Preserved first full-Next harness failure

Root80f2c2/session49028 finishes raw1 (terminal577209), original PID42322 with
the unchanged600-second owner. Resultabe0e953 preserves the failure; owner/world
reviewa19a6b43 confirms clean ownership and unchanged world. Wasmtime42341 starts
and stops normally with SIGINT/exit0. Client42361 exits1 before its first HTTP
request, and no client result is produced. Every Next application gate is
unobserved in this attempt.

The unchanged client `run-contracts.mjs:13` requires the original
`/private/tmp/starling-node-compat/next-wasmtime-deployment-<runId>/client` path.
Source7b719ac1 changed its plan prefix. The resulting assertion is retained in
client stderr c6a6cb6e/1,072 bytes; the parent's later missing-client-result
ENOENT is secondary. Root and the Source reviewers missed this consumer
constraint. This is a harness configuration failure, without a new application
compatibility conclusion.

The complete failed Source, authority4853261d, result, streams and final guards
remain unchanged. A separate SourceV2 restores the original prefix while keeping
all six operational files and assertions byte-identical. The corrected attempt
uses a fresh runId/output and the same accepted d990/476b/22f component; it needs
no new native build or component construction. No retry or success is attributed
to this preserved attempt.
