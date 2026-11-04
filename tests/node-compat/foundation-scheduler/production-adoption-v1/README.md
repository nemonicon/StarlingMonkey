# Private scheduler integration progress

Latest accepted compatibility checkpoint: **foundations-v12**, through the
[separate Root acceptance receipt](../production-acceptance-v12/README.md).
The private scheduler layer passes diagnostic and production gates with
independent verification. Public APIs are unchanged; reset and reuse remain OPEN.
No public process, nextTick global, AsyncLocalStorage or host capability is added.
Current overall status is in [progress.md](../../../../progress.md).

Current production execution gates now pass: three independently verified
engines, fresh eight-stage OFF replay, allocator GC, focused OFF/RuntimeOnly/GC
and same-byte HTTP on both stock hosts. See the
[runtime receipts](../production-runtime-v1/http-final-root-results.json),
[eight-stage verification](../production-runtime-verification-v1/README.md)
and [focused verification](../production-focused-runtime-verification-v1/README.md).
The v12 archive and independent final acceptance now pass. Getter parity,
Symbol identity, combined-owner GC and reset/reuse/ALS limitations are retained.

The [link1 execution receipts](../link1-execution-v1/README.md) record separate
Release `46fc6588…` and Release-GC `949d24f6…` builds and 345-copy freezes. Each
passes ten zero-import components, five rejected initializers, three paired
controls, three fatal/discard observations, retained Jco and fresh Wasmtime.
All32 inputs, including the live Preview1 adapter, match before/after. Separate
[ordinary](../link1-ordinary-release-verification-v1/README.md) and
[GC](../link1-gc-verification-v1/README.md) checks authenticate the evidence.
Actual GC kernel flags are confirmed; VM temporary retention is uninstrumented.
No reset, first-ever classic startup, reuse or production proof is inferred.
The preceding v4 engine results below remain historical evidence.

The [v4 build](release-v4-build-results.json) completed ten incremental steps
from the verified partial project and froze the 9,764,903-byte engine
`a49c920c83a5deb144c960f3d745f66b57754415546346c089b9f182d4b67f6b`.
The v2 freezer verified 337 source/configuration/dependency copies, 306 native
plus two diagnostic inputs, 61 native database commands and two parent commands
from raw Ninja. Before/after configuration and parent-command bytes match.

The [ordinary component result](ordinary-release-results.json) records ten
packaged components, including three deliberately fatal deployed fixtures,
five expected initialization failures and three paired successful controls.
Main executes three retained Jco calls and a fresh Wasmtime instance. All ten
components emit zero imports. The
[independent verification](../ordinary-release-verification-v1/README.md)
rehashes 462 files. Ordering, FIFO wrap, limits, INIT completion before content,
final binding and subsequent configured classic evaluation pass their stated
checks. `gcStress=false`: ordinary native byte operations do not prove forced GC.
First-ever classic startup, INIT tick priority, original fatal-cause identity,
actual reset and request isolation are not proved. No post-fatal reuse occurs.

The [native/source adoption](source-adoption-receipt.json) applies seven reviewed
files and the layered production recipe, fixing 306 source inputs. The
[finite admission adoption](admission-adoption-receipt.json) follows Root's
independent [110 passing source-only checks](root-admission-v2-110.json), including
optional stream/web OFF and unchanged historical selections. Production admission
continues to reject diagnostic engines. These checks are not runtime proof.

The first [diagnostic producer](diagnostic-producer-adoption-receipt.json) compiled
and linked all 109 native steps, then rejected its incomplete compiler receipt.
The parent diagnostic target was absent from the directory-local CMake database.
The [preserved attempt](release-attempt-v1/receipt.json) includes actual Ninja
target commands and the raw artifact's hash. No sidecar was published and the
artifact was never executed.

The [corrected producer adoption](diagnostic-producer-v2-adoption-receipt.json)
captures actual parent-target Ninja commands and native configuration before and
after the build. Root's [five parser checks](root-parent-command-parser-v2.json)
use the preserved real command text. Its fresh retry was interrupted during a
sharp decrease in available filesystem space; saving the launcher's result then
failed with `ENOSPC`. The [second attempt](release-attempt-v2-interrupted/receipt.json)
preserves its input/configuration evidence without guessing the native exit
status. No build or guest process remains active.

The v12 checkpoint gates are complete. The next work is classic-stream producer/
admission integration; reset and ALS remain separate. The user freed storage; capacity exceeds the unchanged
2 GiB start guard. The
[linker audit](../link-resource-audit-v1/README.md) shows that one Ninja job did
not limit LLD's own threading. The
[concurrency proposal](../diagnostic-producer-v3-link1/README.md)
passes 24 synthetic command cases, syntax and patch checks. Its exact
[producer adoption](../link1-adoption-v1/source-adoption-receipt.json) and
[new consumers](../diagnostic-link1-consumers-v1/README.md) now exist with 46
independent host checks and 31 verified inputs. The successor driver32 and both
actual diagnostic gates pass as recorded above; no resource benefit or
lower launch threshold is established.

The [driver source packet](../diagnostic-candidate-v1/README.md) is now frozen;
Root and the [independent review](../independent-driver-review-v2/README.md)
verified all 27 indexed files and 24 consumed input hashes. Its ordinary Release
execution is recorded above; the newer driver32 also passes Release-GC.
Production variants remain pending. The
[reviewed v4 launcher](root-launcher-v4-review.json)
requires 2 GiB available before starting, uses one job and preserves native status
even if result storage fails. Six benign host lifecycle checks cover process-group
cleanup, termination and error reporting; these host checks themselves do not
execute a native build. The launcher subsequently completed the Release build.
Its short
`r4` tag fits normal Release filenames; the GC variant has no room for an
additional tag.

The v1/v2 launcher and freezer files are separate revisions. V1 execution and
source reviews remain historical. The v2 freezer has now executed successfully
for ordinary Release; it verifies native306 + diagnostic2, three embedding
inputs, native61 plus parent1+1 commands and dependency evidence before exclusive
copying. Failed attempts, source checks and diagnostic passes remain distinct
from production acceptance.
