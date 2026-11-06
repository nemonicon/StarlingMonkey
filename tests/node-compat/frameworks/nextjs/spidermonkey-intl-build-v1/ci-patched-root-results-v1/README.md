# Patched Intl CI guest-library baseline

[Run 42281671898](https://github.com/nemonicon/StarlingMonkey/actions/runs/42281671898)
completed at `bb2526b7e862ad7d8f93254beac41dc48b0fa349`. Published artifact
`13536973897` has ZIP SHA256
`abbbd37727631187ef20f5b9a2ee1d6d50dbf9ef6c1e5b45f9234f1a2f7c7f74`,
227,965,139 bytes. Normalized primary GitHub responses and the exact historical
21,034-byte driver (`a390f1a6ab88e7513d0ee58f565ed2c18e1a82d1fd8267a280c452494ce6caa3`)
are retained. No historical driver or patch program is executed by the checker.

All **22** original CI phases record raw zero and clean 0af/f751 termination.
The complete text evidence contains 1,257 owned-process observations and 1,772
disk samples. The lowest sample is 77,542,998,016 bytes; start/end readings are
88,821,727,232 / 77,542,973,440. These exceed the recorded 20 GiB start and 4 GiB
stop thresholds; samples do not establish a precise peak-space requirement.

The guest source is the exact Firefox fork commit
`9dab3d6f643e926a340c391ea30968e940390dec` plus patch
`1a571a891cffd3b81b463c922212f8a4ab1dd1f42b717da4cac5c401445bc9b1`.
All 27 indexed patch-packet files match. Its 112 Source/pure checks are historical
records, not 27 native tests or checks rerun here. The four actual before,
after and final files match their retained afterimages; filesystem modes remain
0600. The complete 11,489-byte full-index Git diff reconstructs those exact
afterimages, including original/new blob SHA1s and Git index modes 100644. Initial
and final source revisions remain the fork commit; the final NUL name list names
exactly those four files. Untracked/ignored-file absence is not inferred.

Generated Intl/ICU4X definitions and irregexp's `-DV8_INTL_SUPPORT` remain present.
The installed `SavedFrameAPI.h` byte-equals the patch afterimage and declares
`GetSavedFrameIsEval` with `JS_HAS_SAVEDFRAME_IS_EVAL=1`; installed configuration
headers match the reported distribution and generated definitions.

All 1,449 ZIP entries are correlated by the published ZIP hash and exact member
hashes. Every one of the **1,447 text payloads**, totaling 2,092,940 bytes, is
losslessly retained in `text-evidence.tar.gz`. The two binary tar archives remain
external references inside the original ZIP:

| Archive | SHA256 | Bytes |
| --- | --- | ---: |
| `spidermonkey-static-release-intl-savedframe-eval.tar.gz` | `e1f1e208f565982c0abfb48ed705018f91467cb26255b54fa17709e14c2855b5` | 222,806,343 |
| `intl-ffi-sources.tar.gz` | `753089e4313fb6445000185c9c22ea9bd84b01805f3436a5edd21fef229a397a` | 2,828,302 |

They were streamed directly from the ZIP without a second large archive or
library copy. All 596 distribution files and all 1,127 FFI files match their CI
rows; the FFI tar also contains three labeled upstream Cargo provenance files.
The 637,175,630-byte merged library has SHA256
`ca04fe5e1673676d9085e86c9354b2cce0dd91f0f839f01b5c8eacdfb8b82d75`.
Parsing its archive headers reproduced the entire 555-member command output:
the 533-member static list followed by 22 objects. ICU common/i18n/data members
remain present. Generated makefiles and recorded commands do not constitute
complete per-compiler argv preauthentication.

Root separately authorized one read-only SDK30 `llvm-nm` metadata query under
the original 0af monitor, capped at 120 seconds. It returned zero, cleaned its
owned process and preserved all selected input hashes. The SDK binary was matched
to its original authenticated archive member. The full raw output is retained in
`symbol-raw.tar.gz`; it reports one **defined external text symbol**:

```text
_ZN2JS19GetSavedFrameIsEvalEP9JSContextP12JSPrincipalsNS_6HandleIP8JSObjectEEPbNS_20SavedFrameSelfHostedE
```

The definition belongs to `Unified_cpp_js_src27.o` in this exact new library.
This is symbol-table metadata, not an invocation or proof of function semantics.
It makes no independent attestation of the tool's dynamic system-library closure.

Run the portable DATA checker, with output outside this indexed directory:

```sh
python3 -B check.py
```

To repeat the optional nested-archive DATA check without extracting a binary:

```sh
python3 -B check.py --artifact-zip /path/to/artifact.zip
```

The first local curation attempt expected SHA fields on the extraction record's
binary-reference rows, which intentionally omit them. Its original reader/logs
and partial text bundle are preserved. `curate-v2.py` instead obtains binary
hashes from the actual CI result and verifies the complete ZIP streams. No CI
command was rerun; the first attempt was a reviewer collection-schema error.

This remains **guest-library-built-engine-and-runtime-pending**. No engine,
component, guest, Next app, SavedFrame function or archive member was executed
by this review. Native full linkage, runtime semantics and component imports
remain separate checks; unchanged stock-host/world behavior is not inferred from
a library build. The first 17-phase CI baseline is preserved unchanged. This
review is retained post-execution DATA, not cryptographic CI attestation or a
claim that every producer input was authenticated before compilation.
