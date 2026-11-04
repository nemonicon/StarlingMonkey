SOURCE-ONLY three Buffer input corrections. The actual bounded m0.11 Buffer.from
accepts Uint8Array, not Array. Root's normal run55534 stopped during component
initialization at the snapshot's unsupported Array argument, before any component
or codec case result was published. Root receipt7460b94d and failed output/logs
are preserved. This is a fixture-input mistake, not a native codec failure.

Exactly three guest expressions change: constructor-refusal argument[1], snapshot
bytes[0,1,2,3,254,255], and ordinary-GC loop[i] are each wrapped in new Uint8Array
before Buffer.from. The full guest afterimage reverses exactly to actual v7.
No native/Buffer contract, codec corpus61, Node oracle28 files, constants107,
exports40, driver/counter/error assertions, tool closure, Root authority or native
metadata changes. No arbitrary Array support is added.

The concrete publisher derives from daa7 with three exact reversible changes:
fresh output component-validation-activated-v8; override only component.mjs with
this corrected afterimage; identify daa7 and this input amendment separately.
The indexed-peer collector, six preflight/root-separation edits, physical tool
closure/helper and all payloads besides component.mjs are byte-identical. It
still uses the genuine350 validation bootstrap and explicit original/staged
contexts. No source activation/bootstrap/verifier, native build, componentizer,
guest, host target or timing action ran for this proposal.

The small authorized HOST regression imports the actual frozen350 Buffer facade
and unsupported helper (hashes match its normal engine source manifest), together
with the existing JS reference hex kernel. It proves old Array rejection and
new Uint8Array success for all three argument shapes. It evaluates the actual
guest prefix with the actual frozen zlib facade/constant generator and an explicit
HOST NODE CODEC TEST DOUBLE. This reproduces the old snapshot rejection without
a codec call and the six wrongly attributed Buffer construction errors. The
corrected prefix yields all68 zlib refusal records with exact own fields, a
six-byte snapshot roundtrip, and eight ordinary-GC fixture conversions. Only three
small Node codec calls run; this is NOT native/backend/component or GC proof.
The injected Node backend version is a host observation, never a guest version.

The sealed disabled89a fixture was inspected read-only: it has no Buffer.from
Array literal. Its ArrayBuffer+offset and Uint8Array-copy forms are unaffected;
window.set([1,2,3]) is ordinary TypedArray#set. No disabled-source edit is needed.

host-regression.mjs can be rerun only as an explicitly labelled host test with a
fresh NODE_COMPAT_ZLIB_BUFFER_FIXTURE_HOST_OUTPUT. Its source/inputs/raw structured
result are sealed here. Root must review and independently verify new activated
v8 source before any real componentization. Operational350 admission stays CLOSED.
