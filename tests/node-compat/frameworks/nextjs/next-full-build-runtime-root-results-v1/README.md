# First application trial on the full native build

This is the first V9 request-regression trial on component
`4afeeb76ebf54f10c263dfbc36dd6a074d5aae6ee53b022df3245998c89292e8`
(37,218,693 bytes), engine `02a6601d…`, full metadata `9e960c41…`.
It is **strictly failed**, not a runtime acceptance of the passing native build.

Root used the existing V9 actor, unchanged V5 guest entry, fresh unchanged
2,181-file Next app, shared `3dcc…` supplemental helper, normal browserV3 and
the same thirteen standard WASI0.2.10 imports. The full-build guard consumes
the genuine full metadata/build/constructor wires, all825 copies,80 native
compile rows plus separate embedding, six clean build phases and whole-world
bookends. It explicitly binds CMake's one generated `null.cpp` outside the
native source root. The1GiB start guard and original600-second process owner
remain in force. Read-only guard checks cover genuine full-build DATA,
14 invalid metadata/path cases, capacity boundaries and Python syntax; they
invoke no actor or constructor.

Actual run `full02a-next-requests-v9-first` completed raw1, with clean owned
groups and protected inputs. The owned server stopped by its planned SIGINT
and exited0. The client preserves these separate outcomes:

| Gate | Actual result |
| --- | --- |
| Six supplemental concurrency/body/recovery cases | 80/80 checks pass |
| Individual HTTP contracts | 24/24 pass |
| Incremental Suspense | Five chunks, shell0/ready2, passes |
| Browser functions | Both interactions pass |
| Cache revalidation | Generation1→1, fails |
| Strict browser capture | Action POST7 `ERR_ABORTED`, missing decoded body/finished/sizes, fails |

Result `c6e867686251e987202bd6b995433667d75dc953aac8cbf00ef68991ce86ad90`
is9,124 bytes. The actual output lives at
`/private/tmp/starling-node-compat/next-wasmtime-deployment-full02a-next-requests-v9-first`,
with its original owner under the `-external-root` sibling. Root's command
streams and whole-world receipt are retained here. Independent physical DATA
review checks the failed gates rather than converting them to a pass.

The build/reconstruction was a real success; this application trial did not
resolve the cache or browser gaps. No retry, failure filter, interface widening,
host modification, production promotion or unique failure cause is claimed.
Next work is a separately versioned native instrumentation control and a
deployed-only JS-global affinity diagnostic. Neither waives this failed run.
