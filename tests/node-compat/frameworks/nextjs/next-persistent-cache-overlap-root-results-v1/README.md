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

Guest runtime remains pending. The separate new entry will run
the same suite through the actual guest CJS/filesystem profile after deployed
bootstrap, using the existing engine and selected standard WASI world. Node
success does not establish guest parity. Computation-gap overlap does not test
simultaneous filesystem syscalls, other processes, crash durability or CAS.
Original full Next acceptance remains false, including its legacy generation
failure and retained intermittent browser failures. No production promotion is
made by these helper tests.
