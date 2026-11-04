This is an **unapproved source/data proposal** for the partial `sm-node-22.14.0-m0.13` zlib profile. It inventories all 22 observed Node differences from the reviewed normal validation; it changes no runtime, manifest, admission policy, metadata or prior result. All action, promotion and acceptance fields remain false or null.

`contract.proposal.json` keeps every original ledger row, including all 11 null deviation labels, and adds a separate proposed disposition. The combined reviewed result is `f08a702c…`; the normal independent index is `a36758db…`. The 22 cases comprise 16 outcome/code differences and six additional errno-only differences. `ZLIB_VERNUM` is a separate constant difference, not a twenty-third error case. This packet references data and primary source files; it is not a packaging snapshot or rerunnable native/guest context.

| Cases | Proposed treatment | Recorded difference |
| --- | --- | --- |
| 7, 10, 24, 27, 41, 44 | Future error-decoration fix candidate | Node has no errno on these output-limit RangeErrors; current native errors have own numeric errno `1`. |
| 12, 29, 46 | Explicit absolute output limit | Node returns 16,777,217 bytes; the profile rejects output above 16 MiB. |
| 15, 16, 32, 33, 49, 50 | Explicit strict stream/member and trailing-data limit | Profile refuses with `ERR_SM_ZLIB_TRAILING_DATA_UNSUPPORTED`; Node returns bytes. Gzip multi returns 512 bytes; the other five cases return 256. |
| 51 | Explicit dictionary limitation | Profile `ERR_SM_ZLIB_DICTIONARY_UNSUPPORTED` differs from Node `Z_NEED_DICT`; both recorded errno values are `2`. |
| 52, 53 | Explicit input limit and validation precedence | Profile refuses over 1 MiB before codec work; Node respectively succeeds or reports `Z_DATA_ERROR`. |
| 56 | Strict-integer decision still required | Profile `ERR_OUT_OF_RANGE` differs from Node `ERR_BUFFER_TOO_LARGE` for `maxOutputLength: 1.5`. |
| 58 | Explicit option upper bound | Profile rejects a limit above 16 MiB even when actual output is small; Node succeeds. |
| 59 | Explicit option subset | Profile refuses `level`; Node accepts it. |
| 60 | Explicit byte-only input domain | Profile refuses strings; Node accepts them. |

The proposed finite domain is six synchronous functions, fixed attached unshared ArrayBuffer/view byte windows of at most 1 MiB, and at most 16 MiB output. The only option is an ordinary own-data `maxOutputLength`, currently integer 1 through 16 MiB. Options are checked before input. One complete format-selected stream/member must consume all input; dictionaries and trailing bytes are unsupported. The other 31 callables and constructing the six supported functions explicitly refuse. Arbitrary proxies, async/streaming/Brotli/CRC32 and complete Node zlib compatibility are outside this scope. Frozen default/constants/codes also differ from Node mutability.

The six errno-only cases are semantic-fix candidates, not necessary resource restrictions. A future error-form change must be reviewed separately: the current native/facade distinction and validation guards cannot be silently relaxed. Nine observed native output-limit cases (the six plus 12/29/46) would need coverage if errno decoration changes. The fractional-option decision must likewise be explicit; a source rule is not evidence of Node parity.

Guest error messages were **not recorded** in these error records. Node messages are preserved as observed data; no guest message or message-equality expectation is invented. Node own-property flags and profile/module/operation fields were not captured by its oracle. Encoded byte identity is not required; the prior review separately compared 138 successful full-byte observations. Those are historical bounded results, not new codec execution or a blanket compatibility pass.

The public constant was observed as `4880`, versus Node's `4865`. The pinned source verifies linked `zlibVersion()` against `ZLIB_VERSION` before exposing the header number. This supports only the documented source-coupled inference; no private version string was returned. The historical `runtimeBackendProof: {verified:false,version:null,vernum:null}` remains unchanged. Numeric Infinity and the other 106 typed constants retain their prior observed scope.

Pinned local Node primary sources come from revision `5d2feb257bcee090e57900eb51720171a6aa92f3` (v22.14.0). Relevant locations are `lib/zlib.js:160` (input conversion), `:233` (max-output option), `:443` (output-limit RangeError), `:632`/`:644` (level/dictionary); `src/node_zlib.cc:857` (gzip member loop); and the concatenated-gzip, trailing-garbage, dictionary and max-output tests. Node's own zlib header and license are bound by hash. The actual frozen 350 facade/kernel/bounded-codec/constants match their immutable source ancestry byte for byte; none is changed or invoked.

Run only the data checker if needed:

```sh
python3 tests/node-compat/foundation-zlib/node-deviation-contract-candidate-v1/check-contract.py --output /a/fresh/owned/report.json
```

It rehashes bounded references, compares the 22 existing Node records and all cited guest error records, preserves original rows, and rejects missing/duplicate/relabelled rows, invented messages, unknown classifications or invented authority/backend proof. It imports no project helper and executes no Node, codec, native, guest or host operation. Root must decide the proposed limitations and any future semantic fix before a separate changed implementation/validation contract can be considered. Operational 350 admission, source promotion and release acceptance remain closed.
