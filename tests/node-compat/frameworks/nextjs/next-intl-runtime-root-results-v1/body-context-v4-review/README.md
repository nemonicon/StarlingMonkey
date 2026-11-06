# Actual Next body-context V4 baseline

The original constructor passed all three commands and its parent. The actual
stock Wasmtime deployment remains **failed overall**: all 24 HTTP contracts,
cache invalidation 1 to 2, and the five-chunk incremental stream passed, but the
browser counter timed out. The browser server-action test passed. Browser data
retains zero page errors, zero console errors, one ERR_ABORTED action request,
and one response-finished collector rejection after browser closure. These
observations do not establish the cause of the counter timeout.

The runtime parent and client exited 1. The owned Wasmtime server stopped with
requested SIGINT, exit 0, no forced cleanup, and no remaining owned groups.
Its complete 40-byte stderr is only the Serving HTTP line. The existing Source
and actual-failure states are preserved; a successful DATA reader does not turn
them into a complete Next pass.

`data.tar.gz` losslessly holds 182 unique retained records (1,518,333 bytes):
all constructor API return graphs, options, input roles, raw command streams and
monitors; the complete runtime/client/response data; the 87-event browser trace
and all 13 response-finished observations in its original JSON; the original
18,559-byte server-action PNG; and all five raw base64 stream chunks. It also
includes the issued Root authorities/callers, the three current indexed entry,
constructor and deployment Source families, selected ancestor Source descriptors
and facade inputs, and the unchanged request contract/app inventory. No separate
Playwright ZIP trace existed in this run. No application tree, engine, component,
SDK, cache state, or native archive payload is copied.

The exact actual chain is Source index `34c35012`, entry `c43117a4`, component
`55f05e3d`, engine `4623640b`, constructor result `959a1fe4`, runtime result
`52999e30`, runtime Root authority `4602f977`. The component's whole typed return
describes its captured bytes and all 131 import pairs. The three command
monitors plus parent show construction/validation/WIT success. Raw WIT imports
are exactly the 13 selected standard WASI 0.2.10 interfaces, and the only export
is wasi:http/incoming-handler. Runtime authority, component, entry, source,
server argv, loopback origin, and the parent owned process evidence join this
to the actual stock Wasmtime target. Generic browser field wasmBrowserRun=false
is retained; it is not used to misclassify this target as a host-only test.

The curator rehashed all 182 selected original records and 12 external artifacts
before/final collection. The current 2,218 original/copy app files also matched
their recorded hashes; copies were independent single-link inodes, files 0444
and directories 0555. These physical modes do not prove read-only WASI preopen
rights. Operation-time source protection remains the original caller's recorded
guard evidence, rather than an all-time filesystem/process attestation. This
reader does not replay the full native build input closure.

Run `python3 -B -I check.py` for a portable DATA-only read. It checks all retained
hashes/membership, exact issued roles, owned terminals and streams, whole typed
return/WIT, independent 23-base-request plus action-POST semantics, chunk bytes,
cache values, browser trace/error counts, and the still-failed original outcome.
The first reader mistake (assuming every passing HTTP row has a failures key)
is preserved under preparation-failures; the corrected reader uses that field
only if present. No constructor, server, browser, compiler or guest is invoked.

The reviewer authored the AsyncResource and ReadStream-options facades. This
relationship is disclosed; this packet independently reads actual retained DATA
and is not independent certification of those Sources. No full Next acceptance,
same-instance identity, snapshot/reset safety, security, cost, full Node parity,
or public admission is granted.
