# Real filesystem cache overlap checks

The first pinned Node22.14.0 reference run passes all eleven fixed groups and
41 assertions. Original owner65596 exits0 without signals, timeout or forced
cleanup. All2,186 standalone application files (48,755,844 bytes/427 directories)
and the selected inputs are unchanged before/after execution. The
[actual result](runs/first/result.json), [owner terminal](runs/first/owner/terminal.json)
and [Root result](runs/first/root-result.json) retain the first run separately.

The suite uses unchanged cache handler `c1013ea6`, genuine Next16.4.5 delegate
`427a5a07` and real Next nodeFs helper `6bc8642f`. Filesystem, entropy, hashes,
Buffer and clocks are real Node operations. There are no dependency fakes or
handler changes. Source review covers the final suite `51de8ea2`; the pre-review
`b741a775` image is retained under `source-history/`, with only actual-use report
flag timing corrected before the first execution.

For a fresh Node check using the same private artifact pins and existing
original-process owner:

```sh
python3 -I -B tests/node-compat/frameworks/nextjs/next-persistent-cache-overlap-root-results-v1/run-node-check.py --run-id next-check
```

Use a fresh lowercase run ID; existing output paths are refused. The launcher
requires the pinned artifacts and preserves each result. It does not provide
clean-machine bootstrap. The suite's [standalone CLI](../next-persistent-cache-overlap-tests-v1/README.md)
also accepts an explicit application root and fresh test path. The initial
Source-only comments in that frozen fixture describe its publication cutoff;
the actual Node result is recorded here.

Guest component construction now completes raw0/clean as `66a3ed9e`
(37,239,204 bytes). The [coordinated INIT DATA review](actual-construction-review.json)
verifies all four owners/eight streams, complete typed return graph, 131 observed
import tuples across the selected thirteen standard WASI0.2.10 interfaces and
incoming-handler-only export. Only the official WIT parser preopen is present,
with env{} and no cache/suite/app work during INIT. Fifty-four finite INIT
records/275,126 bytes are copied under `construction-records/`; binaries, package
and native metadata payloads are explicitly omitted from that curation.

The first real guest runtime now passes all eleven groups/41 assertions in one
GET, original owner69109/180 seconds/raw0/clean. HTTP200 delivers9,307 complete
bytes; Wasmtime child69125 stops normally, stdout is completely captured
(zero bytes), and source/owned copies remain unchanged. The
[coordinated differential DATA review](actual-runtime-review.json) verifies
exact assertion labels, statuses and details against Node, and independently
hashes all23 guest plus23 Node fixture files. Their canonical records agree
after only generated epoch-token and lastModified normalization; pending bytes
agree exactly. Fifty-eight finite runtime/fixture records (129,191 bytes) are
retained under `runtime-records/`, alongside the original Node records.

This establishes the fixed helper subset on Node and stock Wasmtime, through
the actual guest CJS/filesystem/crypto/Buffer profile. Computation-gap overlap does not test
simultaneous filesystem syscalls, other processes, crash durability or CAS.
Original full Next acceptance remains false, including its legacy generation
failure and retained intermittent browser failures. No production promotion is
made by these helper tests.

For future fresh guest checks, the [convenience CLI](run-guest-regression.README.md)
requires an explicit run ID and preserves separate preparation/owner records.
It is Source reviewed and its `--help` passes; its operational modes have not
launched another target. The first accepted guest sample used the original
controller. Both paths still require the pinned private artifacts.

The stock wasmCloud actor now passes whole Source review. Its three mounts use
the existing stock configuration mechanism, with empty guest environment and
egress policy. JSON-only preparation issues a fresh4,550-byte authority, without
starting the host. Its one-request runtime and differential result remain pending.

The first stock attempt is retained as a pre-dev harness failure:
[failure review](actual-wasmcloud-v1-review.json). Config-show omits an empty
environment config map; no host dev command, HTTP request or cache suite runs.
The separate v2 validator accepts exactly `{}` or `{config:{}}`, matching the
pinned Rust serialization rule and preserving the same empty policy. Source
review and fresh JSON preparation pass; v2 runtime remains pending.

The subsequent fixed v2 stock wasmCloud2.11.0 run passes all eleven groups/41
assertions under original owner72460/180 seconds, raw0/clean. Complete HTTP200
delivers9,307 bytes; both config and dev stdout captures finalize completely,
and dev stops normally. The [independent stock-host differential review](actual-wasmcloud-v2-review.json)
verifies every assertion detail against Node/Wasmtime and all23 cache payloads
after only generated epoch/timestamp normalization. It verifies the effective
empty environment, deny-all egress and three exact mounts. Thirty-nine finite
runtime/fixture records/106,157 bytes are retained under `wasmcloud-v2-records/`.
The initial failure remains unchanged. This closes the selected host gate for
the fixed helper subset; full Next.js and global runtime acceptance remain false.
