# Corrected output namespace for cleanup Next runtime

V1 (`7b719ac1…`) failed before its first HTTP case: its new plan prefix disagreed with the unchanged client's fixed path assertion at `run-contracts.mjs:13`. Client exit was 1, stdout was empty and no client result was created. The failed parent result `abe0e953…`, original terminal `a2d97725…` and 1,072-byte client stderr `c6a6cb6e…` remain unchanged and are explicit protected references here.

V2 restores the original `/private/tmp/starling-node-compat/next-wasmtime-deployment` prefix. A fresh Root runId isolates the next output. All six operational files are byte-identical to V1, including the fixed assertion. Every component/constructor/native/application/helper/browser binding, timeout, host flag and acceptance gate is unchanged: actual D990/9256/476b/22f, the five portable-cache cases, original 24 HTTP cases, six supplemental cases, legacy generation increase, five stream chunks and both strict browser cases. No assertion is waived and no app, guest or engine changes are introduced.

The plan changes only Source state, restored prefix, append-only prior Source/failure protection and four preserved-failure descriptors. The browser descriptor still names the preserved V1 Source copy; the V2 physical browser copy is byte-identical and protected by V2's own family index. All runtime action/result slots remain NULL.

The narrow Python Source check reads the actual client literal and checks the derived `<prefix>-<safe-runId>/client` path. It does not parse or execute JavaScript, invoke a process/guard/actor or claim a successful Next result. B missed this coupling when authoring V1; C's earlier peer missed it too. V1 and its failure are preserved. Root owns the concrete authority and any later run.
