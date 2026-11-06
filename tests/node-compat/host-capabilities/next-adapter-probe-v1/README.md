# Actual selective Preview1 adapter C control

This real SDK30 C component passed one stock Wasmtime42 deployment with three
HTTP requests. It uses adapter `d30ade5b…/49672`, not a JavaScript engine or the
Next application. The emitted component `aaf10de8…/126896` has twelve standard
imports, every version `0.2.10`; only the unused selected HTTP outgoing handler
pruned. No external Preview1/custom/unselected imports were admitted. Actual
`wasm-tools component new` performed typed semver composition; no interface name
or version was manually rewritten.

The raw core contains all ten intended Preview1 imports. All three requests
observed stdout/stderr writes of 13 bytes and corresponding actual host log
markers, `BADF` (8) for stdin fdstat/read, real `/app/message.txt` preopen/open/
read/close, wall/monotonic time and resolutions, and secure randomness. The
existing direct Preview2 HTTP/environment/clocks/filesystem/cache operations
also passed. Retained counters were `[1,2,3]`. Whole response bytes precede the
observer's semantic assertions. The Wasmtime process exited0 after intentional
SIGINT; the original0af parent monitor was clean0 without timeout or cleanup.

`plan.json` and `authority.json` bind the executed six-command build. The actual
SDK's C declarations are retained in `checked-p1-declarations.json`. Generated
standard ABI bodies remain unchanged; only the unused CLI-run export wrapper
and old-world force-link tail are removed. `profile.wit` and its seven dependency
packages are exact copies of the selected Next world. The complete SDK10114
regular files/31 aliases/366304928 bytes, selected tools, Source and adapter were
checked before/final. These byte bookends do not attest OS system libraries or
all host state.

Before deployment, review caught an unexecuted observer count typo: its marker
assertions expected12 rather than13. The original `run-wasmtime.mjs` and original
build-pinned files remain unchanged. `host-preparation-correction.json` records
that history; the separate `run-host.py`, `host-plan.json`, `host-authority.json`
and `run-wasmtime-corrected.mjs` performed the single deployment. Do not execute
the superseded `run.py host` branch. Both output roots are already used and the
drivers refuse them; this record is not an instruction to rerun guests.

Portable data verification, without compiling or running any guest:

```sh
python3 -B tests/node-compat/host-capabilities/next-adapter-probe-v1/check-results.py
python3 -B tests/node-compat/host-capabilities/next-adapter-probe-v1/check-results.py --originals
```

The checker validates exact family membership, byte-exact raw command/terminal/
stream copies, full WIT and core WAT, all three raw response bodies, cleanup and
semantic observations. Nine synthetic DATA mutations must refuse. It was
written by the same author/operator; it is not an independent review or a
second guest run. `--originals` additionally hashes external original copies,
selected pins and binaries and the full-input ledger files; it does not rehash
every inherited ledger row. Full input ledgers and binary artifacts remain
external by descriptor rather than being copied into Git.

The original0af monitor sampled Node77422 and its final owned group; the
short-lived Wasmtime77424 was not separately sampled. The host observer retained
its actual spawn PID and exit0 and waited for termination. No universal process
claim is made. `/app` was physically0555 with a0444 fixture; Wasmtime preopens
used default rights. This does not prove explicit ReadOnly capability policy,
nested `.next/cache`, wasmCloud pooling, all adapter functions, native engine
packaging, the unused outgoing HTTP handler or the full Next application.
