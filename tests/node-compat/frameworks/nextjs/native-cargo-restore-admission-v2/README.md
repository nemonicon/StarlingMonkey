This is a read-only admission correction for the unchanged held
`native-cargo-restore-v1` producer and its original receipts. It cannot stage or
copy sources, run Cargo, acquire archives, compile, or execute an engine/guest.
Python 3.11+ is required; pinned build Python 3.9 is unchanged.

The actual first source stage returned0 and copied all3,506 payload files and463
child directories. Its V1 readback failed `ValueError: owned root identity`:
APFS reported root.nlink6 before the receipt was created and7 afterward, with
the same device/inode/mode0700 and exact payloads. The original V1 Source,
receipt, process result and failed reader outcome remain unchanged. There is
no second source stage or retroactive V1-reader pass.

V2 compares historical root device/inode/mode0700. It reports the original and
current link counts separately and does not treat a pre-publication nlink as a
stable identity across publication or filesystems. It retains the current root's
full physical row, including its current nlink, through the final within-read
guard. File nlink1 checks, all child-directory identity checks, exact complete
membership (3,506 payloads +receipt +463 child directories), producer binding,
all original donor/config/metadata bookends, rendered paths and exact84 lock
remain required.

The new reader calls the authenticated V1 module's genuine APIs in their original
context. It does not patch or rebind producer functions/globals and never catches
an old reader failure as admission. Tests compare the retained critical call
order and the absence of file reads after the final guard.

```sh
python3.12 -I -B tests/node-compat/frameworks/nextjs/native-cargo-restore-admission-v2/admit.py --plan
```

The exported `admit_restore(receipt_ref)` accepts the original receipt's explicit
`{path,sha256,bytes}` descriptor. Its role return keeps `sourceIndex` as original
producerV1 and adds a distinct `admissionSourceIndex` for this reader. Paths,
physical records, lock/config roles and `rootLinkCountObservation` are freshly
checked. `actualCargoMetadata` remains null and
`sourceProcessExecutionAttested` remains false. Actual source-stage process
evidence and future offline Cargo metadata require separate Root bindings.

The default and `--plan` authenticate metadata without reading a restored tree.
An explicit `--receipt DESCRIPTOR_JSON` performs read-only admission; it does
not produce a new receipt or rewrite the original. `test-admit.py` runs small
root-identity DATA/AST checks. Its explicit `--actual-regression` reads the
genuine Root-pinned original receipt and process record, reproduces the V1
reader refusal and requires V2's full current admission to pass. This is a DATA
read, with no Source-stage rerun, Cargo or target workload.
