# First actual Intl CI library baseline

[GitHub run 42272037547](https://github.com/nemonicon/StarlingMonkey/actions/runs/42272037547)
completed successfully at repository commit
`dc7bad5c36306368fd8a2816136f02f959aed0ee`. GitHub's published artifact
`13534080477`, `spidermonkey-147-intl-42272037547-1`, has ZIP SHA256
`ae81c73ecb7b9e93eb08e265d64836e68e3d838d9bbc8bb602ca79a3cbc8342f`
and size 227,191,494 bytes. The normalized primary API responses are retained.

All 17 phases record original 0af and f751 raw exit zero with completed cleanup,
no timeout, signals, errors, forced cleanup or remaining observed processes.
The review joined all 85 terminal/worker/log descriptors, 1,247 process records
and 2,114 disk samples. The 34 outer monitor streams are empty; actual command
output is retained separately in each `command.log`.

All phase authorities identify the exact historical
[build driver](https://github.com/nemonicon/StarlingMonkey/blob/dc7bad5c36306368fd8a2816136f02f959aed0ee/tests/node-compat/frameworks/nextjs/spidermonkey-intl-build-v1/build.py),
SHA256 `a5486e5011284fcdad6945952b2d088387effb50c49a86395d1fb296af9ae108`,
12,953 bytes. `historic-build-driver.py` preserves those bytes as DATA; the reader
never imports or executes it. The mutable current driver is not an identity
substitute. The source revision command reports Firefox fork commit
`9dab3d6f643e926a340c391ea30968e940390dec`; the final Git diff command is empty.
This records a tracked-source diff check, not an inventory of every untracked
input or cryptographic CI build attestation.

The retained mozconfig selects the Intl API, WASI target, Release/no-debug,
disabled bootstrap/tests/shell and thin LTO. Generated headers define
`JS_HAS_INTL_API=1` and `MOZ_ICU4X=1`; the generated irregexp makefile contains
`-DV8_INTL_SUPPORT`. The static member list contains 533 objects; the actual
merged library contains those same objects followed by 22 additional objects.
Generated build dependencies and the member list include 176 ICU common objects,
191 ICU i18n objects and `icu_data.o`. This is generated build/recorded member
evidence, not a claim that every compiler argv was captured.

Both tar archives were streamed without extracting the 637 MB library to disk:

| External archive | SHA256 | Bytes |
| --- | --- | ---: |
| `spidermonkey-static-release-intl.tar.gz` | `2508af52c38510b56d711bc37a0ffb5a32450a1dc2847787eebf62f09a4ca062` | 222,772,017 |
| `intl-ffi-sources.tar.gz` | `34bf9d2a988584d18563bf246ed80e112b287e9b2313d2fed700a21926d2d31b` | 2,828,437 |

All 596 distribution files match their reported hashes, including the installed
Intl header and `libspidermonkey.a`:
`aeacbf587694fe42e3d611fd187a7855cf552ced9f01e47b85a7bf5857df06e5`,
637,121,194 bytes. Parsing its archive headers reproduced the complete 555-member
raw `llvm-ar t` list, including ICU data. All 1,127 reported FFI files match;
three separately labeled upstream Cargo provenance files also occur in that tar.
The original `libjs_static.a` binary is not part of the uploaded distribution;
its 533-member list is recorded command evidence.

Recorded free space started at 88,822,759,424 bytes and ended at
77,543,546,880. The minimum sample was 77,543,563,264, above the 4 GiB floor;
the start exceeded the 20 GiB requirement. Sampling does not establish an exact
peak requirement or justify fitting this build into the current local capacity.

The ZIP's complete 1,376-file set and all hashes were checked. Every one of its
1,374 UTF-8 text payloads is retained losslessly in `text-evidence.tar.gz`
(1,367,046 uncompressed bytes). `payload-index.json` records every original
entry. Only the two binary tar archives remain external references. The first
collector's 1,000-member limit refused before extraction; its empty evidence
directory and this minor collection history remain distinct from the successful
1,376-entry collection.

Run the portable, standard-library-only checker from any checkout:

```sh
python3 -B check.py
```

To additionally repeat the streaming binary DATA verification, supply a directory
containing the two tar archives:

```sh
python3 -B check.py --binary-root /path/to/archives
```

Write checker output outside this indexed directory. `curation.*.log` records
the original complete streaming review; `portable-check.*.log` records the
text-only check. Neither command invokes a build tool, interpreter payload,
engine, guest, componentizer, Cargo or native helper.

The actual result remains **guest-library-built-engine-and-runtime-pending**.
The new single Rust aggregate, coherent native engine relink, regex execution and
full Next.js runtime remain separate work. This review does not accept a runtime,
change the standard WASI world or either host, or establish all-input pre-build
authentication. The reviewer authored earlier Intl/Cargo preparation sources and
did not operate this CI build.
