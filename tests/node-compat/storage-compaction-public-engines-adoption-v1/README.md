# Accepted public engine compression execution

All 72 exact-whitelist ordinary Release engines were compressed and independently
postverified. Logical bytes and required metadata are unchanged; all 38 witnesses
match and all 144 recorded temporary/rollback paths are absent.

[Results](results.json) record a 422,617,088-byte reduction in summed file
allocations. The observed global free-space change was only 261,779,456 bytes
and is nonexclusive. Shared extents and unrelated activity prevent treating
nominal sizes or file-block sums as recovered global capacity. Available space
remained below the 2 GiB native build guard.

No engine, compiler, linker or guest was executed. This filesystem operation
adds no compatibility, guest-memory or throughput result. Earlier audit and
source/dry-run packets retain their historical bytes and labels.
