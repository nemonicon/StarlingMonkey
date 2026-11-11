# Native clone-cancellation repair: build readiness

The native cancellation fix **compiles and passes its first real-component
comparison on Wasmtime**. See the [new runtime results](nextjs-clone-cancel-results.md).
The earlier real component still fails the cancellation comparison recorded in
[the lifecycle results](nextjs-lifecycle-results.md). Production remains
foundations-v13, and experimental engine 237c is unchanged.

The [candidate patch](../../tests/node-compat/async-context/response-clone-cancel-native-candidate-v1/clone-cancel.patch)
uses the existing SpiderMonkey stream and Promise APIs. Its shared cancellation
promise waits for the original source cancellation, preserves the two ordered
reason objects and adopts rejection, including falsy values. Source review
passes; the first Wasmtime sample now matches Node for the bounded cases below.

Four additional Node 22.14.0 references are captured:

| Case | Observed Node behavior |
|---|---|
| Both branches cancel; source later rejects false | One source call; both promises wait and reject with exactly false |
| Both branches cancel; source later rejects an object | Both promises reject with the original object identity |
| First branch cancels; sibling reaches EOF | No source cancellation; first cancellation fulfills after EOF |
| First branch cancels; sibling errors | First cancellation fulfills; sibling reads reject with the original error |

The new component guest contains these unchanged shared cases, the original
cancellation case and the 95-check request-context suite. Its Node syntax check
passes. The four-call collector will request context, cancellation, followups,
then context again. That first Wasmtime run now passes all four responses. The
collector retains the V2 Content-Length fix, which passed real TCP tests for
truncated, complete and chunked responses. Those TCP checks do not prove guest
semantics or resource retirement.

The native build prerequisites are restored in fresh directories:

- Six official tool archives match historical SHA/size pins. The first
  materializer failed because macOS-created symlink modes differed; its raw
  failure is retained. V2 applies the declared link modes and successfully
  inventories all six trees, including 31 WASI SDK symlinks.
- The selected SpiderMonkey SDK matches all 596 file hashes and 13 directory
  modes. Its patched Intl/SavedFrame library is preserved. The public SDK served
  only as an exact header donor. 242 Intl headers came from the pinned Firefox
  source; cbindgen 0.29.1 reproduced the final generated bidi header byte-for-byte.
- Native Rust 1.88 matches 155 selected file payloads. Two installation receipts
  were reproduced to their exact historical bytes; no new rustup installation
  is claimed. Corrosion 0.5.1 matches 193 non-Git source files. Missing Git metadata
  was not recreated.
- The fresh 825-input engine recipe changes exactly one native C++ file. All ten
  genuine installed generator checks pass. The new Cargo project uses the
  previous actual manifest/staticlib and unchanged lock, with four base-crate
  paths relocated to the fresh source.

Run the repository-only recovery check with:

```sh
python3 -I -B tests/node-compat/async-context/clone-cancel-recovery-root-results-v1/check-recovery-saved.py
```

It validates 885 retained payloads totaling 5,698,413 bytes, the recorded recovery
outcomes, the four Node references and ten generator results. It deliberately
preserves the historical artifact API 404, the first header fetch's unresolved
generated header, and the first tool materialization failure. It reads only
retained repository files. Tool binaries are not included; a passing reader
does not recreate the SDK or execute a component.

Fresh offline Cargo verification and all six native phases now pass. Engine
`e3075c14` is 31,353,161 bytes. The original build runner's post-collection check
fails on an existing empty CMake-generated unit; that failure remains intact.
A separate collector verifies exactly 79 recipe units plus that generated unit,
the separate embedding command and all remaining checks. Its complete corrected
52-field metadata is `c7e225af`. The [build evidence and saved regression check](../../tests/node-compat/async-context/next-clone-cancel-native-root-results-v1/README.md)
record both outcomes.

Independent engine admission, complete component-input preparation, construction,
component validation and the first lifecycle differential now pass. The emitted
imports are exactly the selected standard WASI 0.2.10 interfaces.
Next: run the same lifecycle regression on stock wasmCloud and rerun the bounded
full Next workload on both target hosts. Same-Store identity, resource retirement, repetition,
cost measurements and production promotion remain separate gates.
