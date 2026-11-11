# Native response-clone cancellation build

The fresh engine compiles, links and passes core Wasm validation. Its SHA-256 is
`e3075c14ec903831fb43dd305fb9c21eeaeb99a0d0a71c052fbda3a914faa965`
(31,353,161 bytes). This directory records build evidence; it does not establish
guest cancellation behavior or production acceptance.

The original build runner exits 1 after successful compilation because its
post-build predicate incorrectly requires every compilation unit to be among the
copied sources. The actual compilation database has 79 copied native units and
one existing CMake-generated empty `null.cpp`, plus a separate embedding command.
The preceding build has the same generated unit. Both selected CMake sources and
the exact generated input/output arguments are verified in
`generated-tu-source-data-review.json`.

`original-build-records/` preserves the failed result, original metadata, original
outer exit 1, six successful native phases, successful offline Cargo check and
their logs. It contains 2,315 payloads (3,855,415 stored bytes; 21,077,941 expanded).
Large records use deterministic gzip. Binaries are not included.

Run the portable regression check from a checkout:

```sh
python3 -I -B tests/node-compat/async-context/next-clone-cancel-native-root-results-v1/check-original-build-saved.py
```

The checker requires the original failure, verifies every saved payload and the
79/1 partition, and reads no original absolute paths. It also passes from an
isolated copy of 2,317 actual staged Git blobs. It refuses optimized Python before
payload reads. It verifies engine descriptors, not the omitted engine binary.
The CMake payloads are not in that fixed packet; the checker verifies their
recorded hashes, while the separate source/data review records the source lines.

`closed-collection-v2-records/` separately retains the successful corrected
collection and core validation commands. The corrected collector verifies all
52 metadata fields, 825 copied inputs, 11 tool trees, configuration, Rust/link
inputs and all remaining post-build gates. It admits only the exact empty
generated unit. It preserves the original failed result and phase provenance;
only the metadata kind and compilation classification change. This review
does not invoke the engine or rerun compilation.

Actual component construction and Node differential results belong in the
sibling `next-clone-cancel-component-root-results-v1` directory. Engine admission,
both-host execution, full Next.js regression, resource lifetime and cost checks
remain separate gates.
