# Native clone-cancellation regression

The first repaired-engine sample passes on Wasmtime 42.0.1 against Node 22.14.0.
This fixes the bounded cancellation failure observed with engine `237c4e5a`.
It does not yet establish the result on wasmCloud or pass the full Next.js
workload with the changed engine. Production remains foundations-v13.

| Check | Actual result |
|---|---|
| Request context before cancellation | Eight groups, 95 assertions match Node |
| Both cloned branches cancel | Source called once with both original reasons; both promises wait for source settlement |
| Source later rejects false | Both cancellation promises reject with exactly false |
| Source later rejects an object | Both reject with the original object identity |
| One branch cancels; sibling reaches EOF | No source cancellation; canceled branch fulfills after EOF |
| One branch cancels; sibling errors | Cancellation fulfills; sibling reads reject with the original error |
| Request context after cancellation | Eight groups, 95 assertions match Node |
| Public AsyncResource constructor | Named/default bindings retain their explicit identifiable unsupported error |

The differential compares every shared cancellation observation with the
retained Node reports. Context execution metadata is validated separately;
all other context fields are compared without projection. The runtime sends
exactly four GETs: `/context`, `/clone-cancel`, `/clone-cancel-followups`,
`/context`. All return HTTP 200 with complete bodies of 17,379 / 3,041 / 4,691 /
17,379 bytes. The host exits normally after SIGINT. Original runtime owner
76401/120 and comparison owner 76491/30 both exit 0 with complete cleanup.

The changed native source is `request-response.cpp` afterimage `0431184d`.
Engine `e3075c14` is 31,353,161 bytes; component `7c227997` is 37,268,017 bytes.
The component is constructed with the separately selected recovered compiler,
the pinned preview1 adapter and the closed `next-http` WIT world. Construction,
core/component validation, emitted-WIT inspection and independent engine
admission pass. No old fixed-engine metadata is projected onto this build.

The emitted component imports exactly these standard interfaces, all at
**0.2.10**:

- `wasi:cli/{environment,stdout,stderr}`
- `wasi:clocks/{monotonic-clock,wall-clock}`
- `wasi:random/random`
- `wasi:filesystem/{types,preopens}`
- `wasi:io/{error,poll,streams}`
- `wasi:http/{types,outgoing-handler}`

Its only export is `wasi:http/incoming-handler@0.2.10`. This run mounts no
application directory and disables host TCP, UDP and IP-name lookup. No custom
host capability or host modification is introduced.

[The retained packet](../../tests/node-compat/async-context/next-clone-cancel-component-root-results-v1/raw-records/index.json)
contains 99 payloads / 3,350,245 stored bytes, including the original closed
commands, HTTP bodies, Node reports, source and differential result. Engine and
component binaries are omitted. The old failing component, original native
post-collection failure and corrected collection remain separate immutable
records. The [native build record](../../tests/node-compat/async-context/next-clone-cancel-native-root-results-v1/README.md)
explains the generated-unit classification correction.

Recheck the captured sample from a checkout with:

```sh
python3 -I -B tests/node-compat/async-context/next-clone-cancel-component-root-results-v1/check-saved.py
```

This recomputes the typed Node/guest comparisons, HTTP completeness, saved
command cleanup and emitted imports using repository files only. It passes both
the working tree and an isolated copy of 101 actual staged Git blobs. Optimized
Python is refused before payload reads. It validates retained evidence; it does
not rerun or verify the omitted binaries.

Next gates are the same lifecycle sample on stock wasmCloud 2.11.0, the unchanged
comprehensive Next.js app on both target hosts, resource-lifetime/reuse checks,
repeatability, clean-checkout reproduction and cost measurements. A healthy
second context response does not prove same-Store identity or native resource
retirement. No broad Node/Buffer compatibility or production promotion follows
from this sample.
