# Secret-owner component construction, fresh v2 phase

This successor corrects the explicit packaging environment that stopped the v1
attempt before output creation. It uses new source, config, authority, output
and monitor contexts. The v1 source, raw failure and independent failure review
remain unchanged. The failure review grants no retry authority.

The actual API is `buildSecretComponent({configDescriptor})`. Authentication
still reads and hashes the complete inherited closure before any custom import.
Both required packaging paths are bound by the new Root authority and checked
individually before the retained API or packaging helper is imported. Successful
construction records those two authenticated paths; no whole environment or
credential values are recorded. A future external launcher must set the exact
paths and retain its actual child arguments, environment-policy observation,
raw streams, deadline, terminal and cleanup evidence.

The full original guarded guest and WIT are byte-identical. All four cases,
including the guarded prototype case, remain future runtime requirements. The
complete real 355-file native frame, three external embedding sources, 75-field
metadata and eleven manifests remain intact. Native, embedding and packaging
roles remain separate. The original read-only API is repeatable; its historical
one-shot callable is not rerun or deserialized.

Construction permits initialization only. It must invoke no ordinary guest
exports, keys, crypto workloads or generated-module imports. Node `crypto` stays
unadmitted. The original selected componentizer still audits its result before
returning it; an internal audit refusal can leave no returned component bytes.
No new finalizer or raw-component capture API is invented here.

`test-source.mjs` checks the environment and authority seams using inert function
definitions only. `check-source.py` verifies the full declared closure and family
membership without invoking owner APIs. Actual component construction, artifact
review and the full retained/fresh runtime suite remain separate unexecuted
gates until their explicit new authority and evidence exist.
