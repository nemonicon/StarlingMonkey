# Exact current ordinary Release corpus: source and dry run only

This helper selects exactly10 components and their10 directly referenced Jco
cores from the newly passed ordinary Release corpus. It authenticates inventory
6845fa7e… / index02f6f560…, final reportc865931b… and its independent verification,
plus component/source/JavaScript binding witnesses. There is no directory walk or
discovery of additional binaries. Engines, frozen source/configuration, SDKs and
older private/debug/OOM/unsafe data are not targets.

This is the specifically authorized ordinary Release diagnostic corpus, whose
application imports, canonical string signatures and late interface signature
were already verified. Files are read as data; the helper does not rerun any
component, execute a guest or promote diagnostic results to production or Node
compatibility claims.

The adoption/rollback loop is byte-identical to reviewed helper0c69a1bc…. It
requires matching logical SHA, required metadata and stable preimage; keeps the
verified original inode under a rollback link until replacement verification;
and checks `free >= 2*logicalBytes +64 MiB` before each fresh temporary. That guard
does not reserve capacity or establish the separate2 GiB native-launch gate.

The dry run completed with20 eligible files, one exact root and32 closure
witnesses. It compressed0 files and reported0 failures. The fresh frozen preimage
is recorded in `dry-run-results.json`. No apply was executed by this packet.

Root must review the source/dry-run packet and repeat exact-file quiescence before
any separately authorized `--apply --expected-inventory ...` operation. A fresh
output journal preserves any subsequent failure; prior corpus reports and
accepted source/index files remain unchanged.
