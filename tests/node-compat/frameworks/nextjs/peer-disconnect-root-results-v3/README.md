# V3 component and actual observed-I/O control

The V3 construction ran successfully: three commands and the original outer
controller exited0/clean. Component643742a2 is37,142,579 bytes and imports the
same thirteen standard WASI0.2.10 interfaces. The complete WIT world guard
remained unchanged.

`peer-v3-runtime-authority.json` was prepared for collectorV2 but never executed.
Independent review found a collector gate that could permit inspection after
a normal output path with an unexpected aborted signal and no observed I/O
abort. That request and collector remain unchanged.

CollectorV3 corrects that one gate and passes independent review. The fresh
`peer-v3-runtime-authority-collector-v3.json` request then ran once: raw0, clean
owned shutdown and protected inputs unchanged. Both independent fresh cohorts
passed healthy upload/output, their real peer-close case, signal checks and
fourth-call same-factory JS inspection. Eight raw responses are retained.

The partial upload aborts Request.signal with the same error seen by its body
reader. The output `closed` case records abort, producer/reader cancellation,
lock release, ordered disposal calls and explicit handled normal return before
inspection. Fresh inspection requests remain unaborted. Resultf25bed1f is
1,127,253 bytes. The [portable actual DATA review](actual-review/README.md)
retains263 records and passes readback;289 current descriptors are checked
separately. Known upload cancel rejection and host transport error text remain
visible, with no successful-upload-cancel or empty-stderr claim.

This validates the isolated JS adapter over genuine native APIs. The full Next
component55f05 remains unchanged and needs a separate integration/regression.
No native resource counts, physical Store identity, teardown-after-Store-death,
idle-peer notification, trailer completion, performance or promotion follows.
