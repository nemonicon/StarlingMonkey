Read-only review of the preserved capability-v1 seal `6e611622…`: **HOLD for
incomplete source closure**, not runtime acceptance. All44 indexed entries and
764 listed inputs match; the v3 parent22 entries and current306 native-policy
inputs are unchanged. No helper/test, compiler, packager, guest or host ran.

The HTTP builder reads eight live repository inputs missing from its input seal:
seven `host-apis/wasi-0.2.10/wit/deps/*/package.wit` files copied into the parser
directory, plus the live Preview1 adapter. The adapter has an inherited exact
prehash but is later passed as a path for reopening. Old frozen/control copies
and future frozen `sourceRoot` verification do not bind those live paths. Their
observed hashes and uses are recorded in [review.json](review.json). Root chose
a new v2 sibling; this v1 packet and review remain historical evidence.

The earlier malformed HTTP pin-root issue is corrected in the final v1 source:
canonical NUL-free roots/children are required and the ancestor walk terminates
explicitly. The owner's75 host checks include malformed-path cases; I reviewed
their source/results without rerunning them.

No other concrete source blocker was identified in finite variant admission,
actual inner guard replacement, primitive pin/manifest rechecks before following
rows, fresh outputs, full29/getter/Symbol/combined-GC limits, exact scalar random
and six HTTP/type-only-clock contracts, or preserved same-byte both-host audit.
These are source findings. All actual engine/component pins remain null and
artifact-success/runtime paths are unexecuted.
