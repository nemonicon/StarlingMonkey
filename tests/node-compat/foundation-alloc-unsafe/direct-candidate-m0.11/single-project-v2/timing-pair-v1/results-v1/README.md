# Private direct-allocation pair: lower allocUnsafe times, no memory/size win

The direct candidate has lower allocUnsafe call and construction times at all
three sizes in **both** arm orders in this one matched run. The observed change
is the complete return-expression replacement, not an isolated zero-fill effect.
It remains a registered JavaScript facade using captured native Uint8Array;
**no new C++ allocator kernel** is involved. This is private experimental evidence,
not production adoption, whole-application performance or complete Buffer support.

[Full raw reports](./raw/results.json), [process-median analysis](./analysis-results.json)
and [the independent post-run audit](./post-audit.json) preserve60 fresh workers,
all raw stdout/stderr and progress. Every worker passed checksum assertions, every
raw report matches and every stderr is empty. The frozen15-file input/source
checkpoint is unchanged: post-run checks cover5 sources,8 receipts,10 engine/
component/transpiled artifacts,586 native inputs,664 complete freeze files and
228 linked/SDK inputs. Root and peers held builds/tests/generators during the
authorized window. Apple M2/macOS arm64, Node22.14/V8-hosted Wasm through Jco1.40.

Each table cell lists the **process median of seven correlated batches** for
order0/order1. Order0 runs baseline→candidate; order1 candidate→baseline. There
are **n2 independent processes per arm/scenario**, not14 independent samples.
Ratios above1 mean the direct candidate has lower time.

| Operation | Size | Baseline µs/iteration, orders0/1 | Direct µs/iteration, orders0/1 | Baseline/direct median time, orders0/1 |
| --- | ---: | ---: | ---: | ---: |
| allocUnsafe call | 64B | 2.094 / 2.145 | 1.011 / 1.001 | 2.071 / 2.143 |
| allocUnsafe call | 4KiB | 2.718 / 2.724 | 1.452 / 1.604 | 1.872 / 1.698 |
| allocUnsafe call | 512KiB | 21.462 / 21.117 | 14.512 / 15.127 | 1.479 / 1.396 |
| new allocUnsafe | 64B | 2.234 / 2.235 | 1.117 / 1.134 | 2.000 / 1.971 |
| new allocUnsafe | 4KiB | 2.900 / 2.800 | 1.653 / 1.724 | 1.754 / 1.624 |
| new allocUnsafe | 512KiB | 21.826 / 23.292 | 14.202 / 14.878 | 1.537 / 1.565 |
| Buffer.alloc | 64B | 1.481 / 1.760 | 1.476 / 1.490 | 1.004 / 1.181 |
| Buffer.alloc | 4KiB | 2.028 / 2.553 | 1.985 / 2.360 | 1.022 / 1.082 |
| Buffer.alloc | 512KiB | 20.005 / 22.321 | 19.968 / 22.032 | 1.002 / 1.013 |
| new Uint8Array | 64B | 0.461 / 0.507 | 0.462 / 0.499 | 0.997 / 1.015 |
| new Uint8Array | 4KiB | 0.947 / 1.062 | 0.834 / 1.123 | 1.136 / 0.946 |
| new Uint8Array | 512KiB | 12.825 / 21.846 | 14.148 / 13.240 | 0.906 / 1.650 |
| Reuse control | 64B | 0.399 / 0.430 | 0.405 / 0.450 | 0.985 / 0.956 |
| Reuse control | 4KiB | 0.599 / 0.612 | 0.587 / 0.714 | 1.020 / 0.857 |
| Reuse control | 512KiB | 2.293 / 5.288 | 2.594 / 2.391 | 0.884 / 2.211 |

All12 changed-allocator order comparisons favor the direct candidate. All seven
candidate slowdowns occur in controls: Uint8Array64B/order0,4KiB/order1,
512KiB/order0; reuse64B/both orders,4KiB/order1,512KiB/order0. All three
Uint8Array controls and reuse4KiB/512KiB reverse direction with order.
Buffer.alloc's body is unchanged yet its measured ratios reach1.181. These
observations show drift/context sensitivity without identifying a cause.
The very short reuse512KiB batches vary from about0.147ms to0.338ms. No control
subtraction, significance, steady-state guarantee or platform-general claim is
made from this n2 shared-desktop run.

## Memory, startup and artifact counterexamples

There is **no uniform memory reduction**. Candidate process peakRSS is higher in
29 of30 order comparisons, including controls. Two conspicuously low process
watermarks remain in the data without exclusion or explanation:

* Candidate allocUnsafe64B/order0 peak192,592KiB, versus265,984KiB in order1.
* Baseline Buffer.alloc64B/order1 peak189,232KiB, versus255,856KiB in order0.

PeakRSS includes input verification, V8 compilation/code/runtime, allocator
retention and background effects. It does not isolate guest live memory or the
allocation primitive. Public linear capacities are mostly equal:

* At4KiB allocUnsafe call and Buffer.alloc, candidate capacity is68,812,800B
  versus baseline68,747,264B: **65,536B larger** in both orders (four comparisons).
* At4KiB new allocUnsafe, candidate capacity is68,812,800B versus baseline
  69,795,840B:983,040B smaller in both orders.
* At64B both are9,502,720B;512KiB allocation workloads both reach68,222,976B.
  The reuse512KiB control reaches14,221,312B and eight observed growth boundaries
  in both arms; it allocates one array per batch, none per iteration.

The observer only reads public exported Memory.buffer.byteLength outside timers.
Capacities are not resident/live heap and growth boundaries are a lower bound,
**not in-Wasm grow attempts/failures**. No raw memory, byte view or private ABI is
accessed. Across30 processes per arm, compile/binding-load ranges13.05–17.64ms
baseline versus13.21–20.57ms direct, and instantiation2.71–4.52ms versus2.70–4.04ms.
These overlapping observations justify no startup-win claim. First batches are
reported separately per scenario, not treated as single-allocation latency.

Exact retained minimal components are12,054,311B baseline and12,062,824B direct:
the direct snapshot is **8,513B larger**, despite its engine being14B smaller.
Snapshot byte determinism and any component-size benefit are unproved. The
earlier failed adapter-path packaging attempt and successful fresh-directory
correction remain preserved; neither native engine nor full installed corpus
failed. No accepted historical checkpoint, runner or input was rewritten.

## Precisely bounded conclusion

This run supports continuing review of the complete direct-allocation expression
within the selected contract: primary type/finite/raw16MiB/truncation validation,
own errors, brand/views/call/new/zero/no-pool behavior and ordinary limits all
passed both actual installed corpora before timing. The explicitly different
out-of-contract Number.isInteger/isFinite hooks remain documented. No genuine
OOM/fault/DEBUG behavior is tested.

Every timed iteration writes/reads only two positions plus length; requested-byte
volume is not a full-buffer read/write or stream throughput measurement. Shared
desktop load/frequency/thermal state and two independent processes limit the
result. This is V8-hosted Wasm, not Wasmtime throughput, a current-Jco-adapter
comparison, or a numerical transfer of older v8 observations. Before production
adoption, accepted m0.9 changes need a common, separately receipted rebase plus
required native/GC/target-host regressions. Classic Streams and Blob work remain
separate.
