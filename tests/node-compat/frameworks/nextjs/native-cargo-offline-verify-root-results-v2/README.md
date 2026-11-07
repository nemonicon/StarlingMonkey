# Actual offline metadata query on relocated sources

The reviewed V2 verifier ran one genuine offline, locked Cargo metadata query
on 2026-11-07. The Root launch, original 300-second process owner, worker and
Cargo all exit 0. Both cleanup checks pass, stderr is empty, and source/tool
bookends remain unchanged. No build command, engine or guest was requested.
The original V1 pre-entry failure remains in its separate results folder.
Independent review also passes the genuine result, current physical bookends
and every retained archive member; `peer-review.json` records that report.

The literal command uses pinned Cargo 1.88 and the restored project:

```text
cargo metadata --manifest-path <restored-root>/project/Cargo.toml
  --format-version 1 --filter-platform wasm32-wasip1 --offline --locked
```

The actual argv, executable digest, private environment and input authorities
are retained. HOME/USER/LOGNAME remain inherited; Cargo home, target and temporary
directories are fresh and external to the restored source. A real `rustc`
information-query process was sampled by the original monitor. Process sampling
does not prove an exhaustive process count or absence of any other process.

`actual-readback.json` records Root's independent read-only checks. New metadata
SHA256 `65544c7b180112e645902ff961db1198ea6d8699a78462cd6e935933ab3de08d`
contains 352,680 bytes. It matches all 84 logical package identities, selected
features, dependency aliases/kinds/edges and six root dependencies against the
authenticated original graph. All manifest paths bind to the fresh restored
roles. The exact final lock remains unchanged. No old metadata was retargeted.

Admission observed 694,898,688 free bytes; the worker's minimum sample was
688,005,120 bytes and the final boundary observed 685,953,024. These retain the
metadata-specific 512 MiB start / 384 MiB phase limits. They do not relax the
1 GiB application or 3 GiB full native build start guards or measure peak cost.

`metadata-output.tar.gz` retains all 23 finite output files (4,351,460 decoded
bytes). `payload-index.json` binds every member to its original absolute path,
size and digest, and lists the four original directories. Raw process records,
metadata, source-before/source-after, environment and private config are included.
The archive changes no payload paths and is DATA only: it cannot recreate live
source identities or attest execution by itself. Read it without extracting
over original paths. The exact source receipt is separately preserved in the
source-restoration results folder.

For a future query, use `native-cargo-offline-verify-v2/run.py` with a fresh
run ID/output and a new concrete Root authority; retain all failures. Its default
mode is read-only. `--inspect-receipt` checks an explicitly supplied live restored
tree without running Cargo. The current V3 builder change plan still needs an
implemented, reviewed consumer of this proof. A full native build and complete
Next regression on its newly constructed artifact remain outstanding.
