# Fresh app runtime preparation

The first isolated host build produced a new2,181-file standalone app. Its
[actual build review](../next-app-build-root-results-v1/actual-review/README.md)
passes; this directory does not yet contain a runtime result for that app.

`run-full-next-fresh-app.py` is the previously executed V6 diagnostic guard
wrapper with only its actor selector changed to the new V7 native runtime
Source. It preserves genuine native metadata/constructor joins, the complete
standard0.2.10 world guard and the original bounded owned runner. It neither
constructs a component nor compiles native code. Preparation AST parsing passes;
no runtime is claimed from that check.

The fresh native V7, browser V3 and matched-Node V3 Sources are now sealed and
independently reviewed. Their indices are bd785648/3720,5faa8f5d/3219 and
41361ae1/3071 respectively. Root rehashed all20 browser,19 stock and23 native
payloads. C's independent
review also ran31 native inert checks,20 stock read-only/inert checks and18
observer checks; no actor, copy or server ran. Late native and stock Root input
documents are issued here, without an actual runtime invocation.

Root requires at least1GiB free before launch as a conservative start admission,
not a measured peak or continuous monitor floor. The original actor timeouts,
process ownership and protected-input policies stay unchanged. The full
24HTTP/cache/stream/2browser assertions, strict zero-error gate and existing
timeouts remain. The Node control retains source modes; the native owned copy
uses0444/0555 plus a separately owned writable cache. Neither physical policy
proves read-only WASI descriptor rights.

The reusable native regression command requires the retained private component,
tools and fresh application:

```sh
python3 -I -B tests/node-compat/frameworks/nextjs/run-fresh-next-regression.py --run-id FRESH
```

Use a fresh lowercase ID of at most48 characters. `--prepare-only` writes a new
request and starts no runtime; it deliberately skips the launch-space gate.
The command pins these reviewed inputs, keeps a new output/observation and
complete native/constructor/world guard for each run, and never automatically
retries or overwrites evidence. It runs the native arm only. The matched Node
arm is separately selected through the held stockV3 runner/input document; it
has its own fixed fresh output root and300s owner.

The first real `--prepare-only` check exited0, writing request3facd984/14040.
Neither output/outer directory nor world-guard receipt exists. An inert check
with free bytes mocked to0 refuses before a request or actor; it is not an
actual disk-pressure workload. Duplicate preparation is refused and preserves
the request. AST and C's independent read-only grant/CLI reviews pass. See
`cli-preparation-observation.json` and complete raw preparation logs. Actual
free space at preparation was280,678,400 bytes, below the launch floor; no live
fresh-app trial has run.

Old55f05 passes, the first integrated1c31 browser failure and its later positive
paired CDP trial remain distinct retained observations. A fresh app pass will
not establish the cause or reliability of that earlier abort. No old inventory,
file identity, build/action ID or result is retargeted.
