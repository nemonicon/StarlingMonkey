# Portable cache: first real application checks

The bounded cache scenario works in the actual Wasm application. The complete
application contract remains failed on Wasm. The first Node host control failed
through its compatibility loader; a separately corrected StockV2 control now
passes the same cache scenario and full original suite. The Wasm/control
comparison still does not establish Node parity.

## Pinned artifacts and scope

- Node22.14.0, Next16.4.5, React/ReactDOM19.3.1; ComponentizeJS0.23.0,
  Jco1.40.0; stock Wasmtime42.0.1.
- Corrected native engine2251f11a/full metadataafb14d8a; real-Next component
  `4e6582ee…`,37,235,395 bytes, construction review7381338c.
- Exactly13 selected standard WASI0.2.10 imports and only incoming-handler
  export. Native app/cache access uses existing standard filesystem preopens;
  no custom host service or host modification was added.
- Genuine standalone buildabdca858/inventoryf8058b47:2,186 files,
  48,755,844 bytes,427 directories excluding root. Exact handlerc1013ea6 and
  genuine Next FileSystemCache delegate are traced; generated configuration uses
  `../cache-handler.cjs`, memory cache0. Build DATA review163133f1 corrects only
  the earlier review's authorship attribution; original36414e4a is retained.
- Fixture31 files preserves28 parent files, changes config and adds the handler
  and one GET/POST nonce route. Legacy routes, UI, dependencies and lock remain
  unchanged. Server JavaScript executes in SpiderMonkey inside Wasm; the host
  Node build and ordinary browser JavaScript are separate phases.

## First trial, retained failed control and corrected control

| Gate | Wasm trial | Node host V1 | Corrected Node host V2 |
|---|---|---|---|
| Five cache requests | Pass,52 checks | Fail, all five HTTP500 |Pass,52 checks |
| Original HTTP contracts |24/24 pass |23 base requests observed; only public asset passes; action submission unobserved |24/24 pass |
| Legacy cache generation |1→1, fail |Unobserved |1→2, pass |
| Supplemental concurrency/body/recovery |80 checks pass |Fails on500 responses |80 checks pass |
| Incremental stream |Five chunks, shell0/ready2, pass |Unobserved |Five chunks, shell0/ready2, pass |
| Functional browser interactions |Both pass |Unobserved |Both pass |
| Strict browser acceptance |Fail, Server Action `ERR_ABORTED` |Unobserved |Pass, errors empty |
| Ownership/protected inputs |Clean/preserved |Clean/preserved |Clean/preserved |
| Overall |Failed |Failed |Passed, one sample |

Root73058 observes native original87752/600 finish raw1/clean. Result06ce2d99
and client65bee544 preserve every gate. Independent outcome review969e99fa and
primary reviewb860b1f2 pass as DATA reviews of that failed overall result.
Root78336 observes Node V1 original88210/300 finish raw1/clean. Result266d62ef and
review5e709e41 retain its five complete21-byte `Internal Server Error` bodies,
partial original suite and unobserved later gates. Neither V1 arm was retried.
After a separate versioned control correction and accepted real VM seam,
Root81654 observes original92341/300 finish raw0/clean. Resultede853eb and
independent DATA reviewd739eacc retain the corrected control's positive gates.
It does not reclassify either earlier failure or establish browser reliability.

The five native responses have delivered body lengths113,113,70,113,113. The
first nonce equals the repeat, the nonce changes after the POST revalidation,
and the final repeat equals the new value. All statuses are200, complete and
within the64KiB bound. These are Fetch-delivered, gzip-decoded bodies; socket
EOF and compressed wire bytes are not inferred from them. The same shared
collector Sourcea7b401d5 serves both arms and saves every raw case before
validation.

The cache ends with two FETCH entry files and ten tag epochs. The portable
entry matches the final nonce and its current epoch associations. This is
bounded persistence/coherence evidence for the declared portable key/tag.
It does not independently prove the legacy key's invalidation. That legacy
route's value comes from a module-local `++misses`; recomputation in another
module instance can still produce1. The observed1→1 remains a failed original
gate, without a new Store-identity or sole-cause claim.

The browser's functional result is positive, but its action POST records
`ERR_ABORTED` for body, response completion and sizes. All three strict errors
remain failures. Earlier successful samples and complete captured-POST
transport diagnostics do not establish a cause or accept this failure.

## Control harness gap and verified correction

The Node control uses the existing CommonJS compatibility loader and HTTP
bridge. Its evaluator calls Node `compileFunction` without an
`importModuleDynamically` option. Next's newly selected cache-handler load uses
dynamic import and produces `ERR_VM_DYNAMIC_IMPORT_CALLBACK_MISSING`.
Unsupported `node:module.findSourceMap` diagnostics are also retained. This is
a control-adapter failure, not evidence that Node itself lacks dynamic imports.

A separate StockV2 Source correctiondf257054 uses the pinned Node22
public `vm.constants.USE_MAIN_CONTEXT_DEFAULT_LOADER` option. Node22 marks that
option experimental; it is proposed only for the matched host test harness.
Natural dynamic imports use Node's
main ESM loader, whose cache is distinct from the compatibility require cache;
that distinction must remain explicit. See the [pinned Node VM documentation](https://nodejs.org/download/release/v22.14.0/docs/api/vm.html#vmconstantsuse_main_context_default_loader).
The control also creates an explicitly private `.next/cache` parent after its
owned-copy reset, as required by the handler profile. That second issue was
Source-based, not the observed cause of the V1 failure. No Next/application or
Wasmtime code changed.

The Root-owned VM seam reproduces the old error and imports/constructs a real
default-exported CJS class through the corrected option. Original91470/120
finishes0/clean; resultb75a4064/review0ac120ab also verify repeated namespace
identity, real Node require identity and the separate candidate require cache.
The197-byte experimental warning is retained unfiltered; no Node VM flags,
HTTP, Next, browser or guest execute in that seam. It gates the subsequent
StockV2 application control. Original V1 records and all old assertions remain
unchanged.

## Capability and lifecycle limits

The native owned app copy remains byte-identical and physically0444/0555,
including a separately declared empty cache mountpoint. The writable cache root
is0700. Actual cache files are0644 and children0755; the corrected Node control
also creates0644 files beneath its0700 parent. The facade passes no explicit
mode option to `mkdirSync` or `writeFileSync`. An earlier Root-originated
source-mode attribution in the retained969e/b860 reviews was incorrect; the
[external correction](../../tests/node-compat/frameworks/nextjs/next-portable-cache-native-root-results-v1/cache-mode-source-correction.json)
preserves their bytes and all actual outcomes. No ignored-mode failure was
tested. The selected pinned filesystem WIT has no POSIX mode parameter in
`open-at` and no mode field in `descriptor-stat` (the [selected WIT](../../tests/node-compat/frameworks/nextjs/regexp-unicode-probe-candidate-v1/deps/wasi-filesystem-0.2.10/package.wit)); requested modes must not be
claimed as implemented permissions. These host observations do not prove a
cause, WASI rights attenuation or arbitrary POSIX filesystem compatibility.

The profile is cooperative and bounded:64 entry slots/associations, ten read
epoch tags, mutations only for two primary FETCH tags,148-file/8,429,568 logical
byte ceiling. Route-cache writes/ISR persistence and implicit path invalidation
remain deferred. It adds no raw sockets, TLS, DNS or process services. Cross-
request JavaScript identity, GC/resource bounds, reuse reliability, wasmCloud
validation, clean-machine reproduction and performance remain separate gates.

Current component/app byte counts are measured artifacts, not startup, memory
or throughput benchmarks. Foundations-v13 remains the accepted production
checkpoint; complete Node, Buffer and Next compatibility are not claimed.
