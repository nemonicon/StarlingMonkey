# Ordinary Release scheduler diagnostic: independent evidence verification

This packet rehashes and checks **existing** reports/artifacts. It does not run
the diagnostic driver, componentizer, Node oracle, compiler, Wasmtime, or a guest;
it does not modify live/frozen inputs. The latest accepted checkpoint remains
v11. This private Release diagnostic is not a production-admitted module.

[verify.py](verify.py) checks the frozen engine SHA
`a49c920c83a5deb144c960f3d745f66b57754415546346c089b9f182d4b67f6b`
(9,764,903 bytes), metadata SHA `c9bb8690…`, all337 frozen copies, the
306+2 native/diagnostic source partitions, recipe1e2f15d1 and three external
embedding inputs. Actual61 native compile-database commands include the queue
member; the strict subset has four commands. The two parent-target commands
come from exact before/after Ninja stdout, not the native JSON database. Frozen
CMake cache, database and parent-command bytes agree before/after and match
metadata; Release/strict/tick/entropy flags are present. **GC-stress is false.**

The frozen24 test inputs are independently rehashed before/after this reading,
and match the report and original input freeze. The pinned driver records its
own historical pre/post checks; this verification checks their frozen source
and present bytes without replaying that historical execution. All27 original
candidate-index entries, packager witnesses, Node/Wasmtime binary digests and
raw run logs are also bound by the result closure.

The ten actual component/source digests agree with the report. Recorded WIT and
interface audits select/import nothing. An independent narrow binary-section
reader verifies zero top-level component imports against the documented
[Component Model binary layout](https://github.com/WebAssembly/component-model/blob/main/design/mvp/Binary.md).
It does not repeat full type validation or parse function implementations.
Generated Jco modules and their referenced core binaries are hashed as evidence.

The recorded three retained main calls and fresh Wasmtime call match pinned
Node ESM/task/job phase arrays. Configured classic execution matches its Node
oracle only for the subsequent configured evaluation; first-startup classic
priority remains unproved. INIT observes one tick before content; its explicitly
recorded generated-glue append is not a public initializer option or proof of
before-jobs priority. Late binding reports getter/tick/job/job-tick order.

Five initialization failures are preserved, along with all15 original/actual
glue pairs. Three successful controls cover a caught throw, a rejection handled
in a microtask and exactly65,536 callbacks in a checkpoint. Three paired
fresh-instance failures report generic boundary failure/discard. They do not
establish the hidden original exception cause, recoverability or post-fatal
reuse. No Engine reset, cancellation, request teardown, public process or ALS
support follows. Queue-only application ownership plus eight ordinary pending
hex operations is an ordinary Release observation; it is not forced-GC proof.

[results.json](results.json) records the verification and complete hash closure;
[index.json](index.json) freezes this independent packet. The first unfrozen
reader iteration resolved package-relative packager paths against the wrong
directory; [its note](verification-attempt-1.json) preserves that reader error.
No result/index or guest failure was produced by that iteration. Only this
verifier's path resolution was corrected; no driver, production or frozen file
was changed.
