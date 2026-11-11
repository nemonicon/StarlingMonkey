# Stock wasmCloud clone-cancellation regression

The repaired native engine passes the bounded lifecycle comparison on stock
wasmCloud 2.11.0 against Node 22.14.0. Four complete HTTP 200 responses match
the Wasmtime entity bodies byte for byte: two context runs with 95 assertions
each, cloned-branch cancellation, and four rejection/EOF/error followups.
Runtime owner 80219 and differential owner 80391 both exit 0 with clean shutdown.
The effective configuration has no mounts, guest environment or outgoing allowlists.

Recheck the retained evidence without the original build directory:

```sh
python3 -I -B tests/node-compat/async-context/next-clone-cancel-wasmcloud-root-results-v2/check-saved.py
```

The checker verifies all 59 payloads (288,118 bytes), original command cleanup,
complete captures, typed Node comparisons, host configuration and the 13 selected
standard WASI 0.2.10 imports. It passes both this checkout and an isolated copy
of 61 actual staged Git files (335,193 bytes). Optimized Python is rejected
before payload reads. Engine/component binaries are omitted; the checker does
not execute a host or prove native resource retirement, instance reuse or full
Next.js acceptance.

The V1 failed attempt remains separately retained. Its validator incorrectly
required empty configuration fields which the pinned host omits during JSON
serialization. V2 accepts only those source-defined empty-field omissions.
