This is an **executed standard-WASI deployment probe**, not a StarlingMonkey or
Next.js execution result. The C guest and selected `profile.wit` build a93,929-byte
component, SHA256 `32830d393ceccc7aaf7f399bd6816ab54928cc240db9b228352b3f16d2f1d720`.
The emitted component has exactly ten standard WASI0.2.10 interface imports and
one `wasi:http/incoming-handler` export. It uses no Preview1 adapter or custom
service. See [the actual audit](results/build/component-audit.json).

Stock Wasmtime42.0.1 passes three requests with default instance counters1,1,1
and three with explicit `--max-instance-reuse-count 32 --idle-instance-timeout 60s`
counters1,2,3. Official wasmCloud2.11.0 `wash dev` passes three requests with
counters1,1,1. All host processes finish raw0 with clean owned groups. The tested
operations are configured environment, random samples, wall/monotonic clocks
and1ms polling, application read/denied create, and writable-cache create/write/
read/link/second-link EEXIST/rename/unlink. Both hosts return no initial cwd.

The app read-only check uses owned Unix555/444 modes; both preopens advertise
flags33. This does not establish individually narrowed WASI mount rights. The
cache is mounted at `/cache` for this probe. Next needs an explicit nested cache
mount and possibly additional narrowly selected writable paths; these layouts
are not yet validated by this control. Random sample differences are not an
entropy-quality measurement. Three sequential reuse requests do not establish
warm lifecycle behavior under concurrency, cancellation, expiry or load.

The pinned [Wasmtime command source](https://github.com/bytecodealliance/wasmtime/blob/v42.0.1/src/commands/serve.rs)
documents its reuse options. The pinned [wasmCloud pool source](https://github.com/wasmCloud/wasmCloud/blob/bc5acfb8e15f7d6d199ca940354d82e590c2d5ff/crates/wash-runtime/src/engine/instance_pool.rs)
has an opt-in warm-instance policy. `wash dev` main's ephemeral configuration is
not the normal warm-workload deployment path. **Warm deployment of this component
on wasmCloud remains unexecuted**; neither host was patched to force reuse.

`results/summary.json` indexes55 copied files/80,706 bytes, including raw results,
owned-process terminals and failed preparation history. Attempt1 failed compilation
on an undeclared tuple-free helper. Attempt2 built and validated, then its text
audit falsely matched Preview1 names in DWARF. Attempt3 checks actual import
declarations and passes. Those failures are retained without relabeling.

Run `python3 -B -I tests/node-compat/host-capabilities/probe-v1/check-evidence.py`
for a data-only regression check. `build.py` and `run-owned.py` are the reusable
actual build/host runners; they require the exact pinned local toolchain paths,
fresh external output directories and their checked inputs. Rebuild and rerun
with new output roots to obtain new execution evidence. Existing results are
immutable observations, not a claim that another host version will behave alike.
