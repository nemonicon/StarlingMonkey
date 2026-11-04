# Completed public Release build outputs: bounded read-only inventory

The exact whitelist contains **472 paths/distinct inodes**, **83,736,256 logical
bytes** and **84,680,704 summed allocated bytes**. All are declared object/archive
outputs in five completed public projects: current accepted v11 Release-GC and
RuntimeOnly, accepted v5 OFF and RuntimeOnly, and accepted v3 Path OFF. V11's
ordinary OFF and GC receipts share a mutable build directory; only the matching
current GC configuration is counted, once. This is inventory, not compression.

Every selected project's actual CMake cache and compile database match its
terminal engine sidecar's digests. Frozen v11 copies also match. Earlier v3/v5
freezes retained digest-pinned sidecars without separate configuration copies;
this audit captures the matching actual bytes as new witnesses. Exact engine
hashes, sidecar hashes, command records and configuration names appear in
[results.json](results.json).

Selection uses the compile database's exact `-o` operands, recorded actual
embedding compilation operands, and existing `.a` targets returned by read-only
`ninja -t targets all`. `ninja -t commands starlingmonkey_embedding` captures their
command metadata without running the commands. Full raw text is retained under
`ninja-metadata/`; it is never evaluated. Files must be regular outputs inside
the exact project directory, with pre-terminal mtimes, stable stat identity,
full present hashes and required metadata. These are present object hashes, not
invented historical per-object digests.

Together with the separate [72-engine inventory](../storage-candidate-audit-public-engines-v1/README.md),
the combined summed-allocation ceiling is **782,893,056 bytes**, below the
requested 1 GB whitelist target. It is not a recovery estimate: compressed
output remains nonzero, and shared/COW extents are not measured. Neither a
720 MB recovery nor satisfaction of the 2 GiB launch guard follows. No broader
Cargo/cache, source, SDK/tool, private, DEBUG/OOM, fault, probe, candidate or
diagnostic project output was added to make the total larger.

No compiler, native link, build, component, guest or compression operation was
executed. All existing paths and bytes remain unchanged apart from ordinary
read-atime effects. The first unfrozen reader assumed older prefix-named frozen
configuration files existed; its source, partial read-only command witnesses and
error are preserved in `history/`. The final reader instead verifies their
actual sidecar-pinned digests and publishes new audit copies.
