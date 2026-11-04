# Accepted bounded entropy-v1 checkpoint

`results.json` verifies the coupling of 21 copied full reports, two exact native
engine receipts and all report SHA-256 values. Both engines use the same 267
frozen source inputs. Secure entropy is either OFF or runtime-only; each mode
has an actual private deployed-entry barrier and guest OpenSSL bridge. No new
host service or host modification is used. No `node:crypto` exports are added.

For each mode, two real scalar components pass seven deterministic snapshot
rejections, eight owned-input differential cases against Node 22.14.0, repeated
and fresh instance calls, and stock Wasmtime42 execution. OFF emits zero
imports. Runtime-only emits exactly `wasi:random/random@0.2.10`. The explicit
repository Preview1 adapter is pinned; the npm default emitted0.2.12 and was
correctly refused. No interface-version substitution is used.

The minimal HTTP components import five standard 0.2.10 interfaces in OFF and
six with runtime secure random. Three requests per mode pass on each stock
Wasmtime 42.0.1 and official wash 2.11.0 local host. Runtime snapshot RSA import
failure is caught, and deployed RSA retry passes. The monotonic-clock dependency
is structurally type-only in these minimal HTTP worlds. Counters reset; these
runs do not prove same-instance HTTP reuse or request isolation.

A separate unchanged upstream integration component with 18 explicitly selected
standard 0.2.10 interfaces passes all ten routes/233 subtests on both hosts,
including 152 crypto subtests. wasmCloud grants only the two outgoing HTTP hosts
required by original fetch subtests. This broad regression world is separate
from the minimal HTTP worlds; it does not establish Node HTTP, DNS, sockets or
TLS support. Nineteen adapted Starling E2E cases and all 15 selected Componentize
builtin fixtures pass across the two policy modes. The OFF secure-random fixture
has an explicit intentional delta: coded denial replaces upstream deterministic
secure bytes. Nine strict initializer cases pass in OFF. Original failed mixed
policy and missing-host-environment attempts are retained in `diagnostics/`.

Both selected OpenSSL source caches were compared after the builds: every one
of 4,650 regular files and the exact file set match the pinned archive plus two
reviewed patches. v2 adds guards before and after compilation; v1 does not
retroactively claim those guards.

Optional Path is **not accepted in this checkpoint**: lexical vectors passed,
but the matcher used Unicode property escapes absent from the pinned Intl-free
SpiderMonkey build. The later finite-category correction and its acceptance
belong to foundations-v2. Production ALS, Node scheduling, lifecycle, remaining
foundations, compression/Node crypto and optional capabilities remain open.
