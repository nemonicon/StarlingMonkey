# Final Clang archive operands: bounded read-only closure

All five completed public build roots from the [previous exact inventory](../storage-candidate-audit-public-native-inputs-v1/README.md)
were queried with read-only `ninja -t commands
starling-raw.wasm/starling-raw.wasm`. The captured text is parsed as data. Each
selected final Clang stage has 30 literal `.a` operands: 29 occurrences inside
its build root and one excluded SDK `libspidermonkey.a` operand outside it.

The five roots yield **140 distinct inside-root archives**. Their full hashes,
stat identity, ownership/mode/timestamp, allocation, flags, ACL and xattr digests
match the previous 472-file inventory. **Zero additional paths and zero additional
allocated bytes** were found. This includes the declared custom-copied Rust and
OpenSSL archives. Repeated operands and canonical `/tmp`/`/private/tmp` aliases
are deduplicated. Shared/COW extents remain unknown.

The combined engine-plus-native-input summed-allocation ceiling therefore stays
**782,893,056 bytes**. It is not a recovery estimate, and it establishes neither
720 MB recovery nor satisfaction of the 2 GiB launch guard. No broader directory
crawl, SDK content inspection or additional scope is proposed by this audit.

[results.json](results.json) binds terminal sidecars and matching current cache/
database digests, raw Ninja witnesses, the selected exact wrapper/`-o` stage,
Release/ThinLTO/post-link flags and every selected archive. Only Ninja's read-only
command tool and metadata readers ran. No captured command, compiler, linker,
build, guest or compression helper was executed; no existing bytes were changed.
