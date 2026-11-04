# Protected listener replay on the actual m0.11 core

The fresh OFF, RuntimeOnly and Release GC engines pass the focused protected
listener gates. Events remains m0.10; this replay verifies its coexistence with
the newly compiled m0.11 core. The accepted m0.10 evidence is unchanged.

Both ordinary entropy variants pass 29 pinned Node groups (16 public, four
nested-once and nine receiver cases), finite 16-name exports/defaults/static
CommonJS and aliases, own coded errors, snapshots, three retained calls each
for main/aliases/handled controls, and three fresh Wasmtime controls. Eight
initializers reject and five deployed fatal cases fail on Jco and Wasmtime;
fatal instances are discarded. Handled-later rejection controls survive reuse.

The GC replay passes three retained calls and fresh Wasmtime, eight valid public
hex roundtrips per clean call, post-GC registration/disposal/nested once and
receiver restoration, plus a latched initializer object and deployed fatal
control. This uses the existing rooted Release Shrink boundaries. The signal,
callbacks, ordinary/protected/once records, disposers and closure-held Symbol
are combined owners; this does not isolate prototype-only Symbol liveness or
establish ALS, request teardown, OOM or fault behavior.

There are 19 emitted application components: eight OFF, eight RuntimeOnly, two
GC and one fresh callback-return observation. Eleven import nothing; the eight
RuntimeOnly components import only `wasi:random/random@0.2.10`. The audited
packager component is tooling and is not counted as an application. Tests use
pinned Node 22.14.0, the audited v2 componentizer, Jco 1.40 and stock Wasmtime
42.0.1. This focused report does not establish HTTP-host behavior or performance.

The fresh safe counterexample remains **false Node parity**: returned-object
`.then` getter reads are Node ordinary/protected/already-aborted `1/1/0`, versus
`0/0/0` on both native hosts. Every getter returns `undefined`; no callable-then
or rejecting-getter test is implied. Target `Symbol.dispose` is the actual
well-known nonregistry symbol, while Node uses `Symbol.for('nodejs.dispose')`.
Neither difference is normalized away. No full Node/EventTarget/process,
returned-Promise routing, AsyncResource or compatibility claim follows.

`engine-pins.json` admits only the three new byte- and sidecar-pinned engines,
their exact frozen source root and recognized five-file m0.11 core contract.
The unchanged protected ten sources, all 304 inputs, frozen configurations and
actual 60 layout commands plus embedding macro are verified before any receiver
negative. Seventeen saved validation inputs are recorded in
`validation-source-freeze.json`. The Node oracle and public cases are unchanged
from the accepted previous replay.

Two copied ancestry files are deliberately **never executed here**:
`freeze-engine.py` and `run-off-control.mjs`. The actual m0.11 engine freezer is
under `foundation-alloc-unsafe/production-adoption-m0.11`. Events-OFF remains the
explicit historical m0.10 admission control; it is not a fourth m0.11 engine or
an identical new source manifest. No old/Events-OFF prototype negative ran.

Full reports are mirrored beside this README and indexed by
`evidence-receipt.json`. Component/core/engine binaries remain external. No
DEBUG, fault simulation, private memory inspection or malformed ABI call ran.
