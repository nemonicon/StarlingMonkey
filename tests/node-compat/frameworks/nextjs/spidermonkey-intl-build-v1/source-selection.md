# SpiderMonkey Intl source selection

Read-only primary-source checks on 2026-11-06 found no Intl-enabled guest
distribution or standalone source package in the pinned StarlingMonkey release.
No large archive, Firefox checkout, sparse checkout or build was performed for
this assessment.

The [release API](https://api.github.com/repos/bytecodealliance/StarlingMonkey/releases/tags/libspidermonkey_FIREFOX_147_0_4_RELEASE_STARLING)
lists exactly these three uploaded assets. Sizes and SHA-256 values below are
published API metadata, rather than hashes of new downloads.

| Asset | Bytes | SHA-256 |
| --- | ---: | --- |
| [debug](https://github.com/bytecodealliance/StarlingMonkey/releases/download/libspidermonkey_FIREFOX_147_0_4_RELEASE_STARLING/spidermonkey-static-debug.tar.gz) | 154324310 | `49a5b610dace59331bc699ac53a99d9f4c3b4579441efa66147aa8e96b4ffcee` |
| [release](https://github.com/bytecodealliance/StarlingMonkey/releases/download/libspidermonkey_FIREFOX_147_0_4_RELEASE_STARLING/spidermonkey-static-release.tar.gz) | 184568633 | `c57dc83d93dc04198882b44fea49cd3cb01e0b267bf99fae3b058cb158da684b` |
| [release_weval](https://github.com/bytecodealliance/StarlingMonkey/releases/download/libspidermonkey_FIREFOX_147_0_4_RELEASE_STARLING/spidermonkey-static-release_weval.tar.gz) | 185640018 | `f108286a1b9c35aeee89a803b073175a077633ffea5bbe4c3b85fcc85230dba0` |

The [release tag](https://api.github.com/repos/bytecodealliance/StarlingMonkey/git/ref/tags/libspidermonkey_FIREFOX_147_0_4_RELEASE_STARLING)
resolves to StarlingMonkey commit `9dda8ba7fcda2e17c6795d402f0478cf4c1f7f37`.
Its [build module](https://github.com/bytecodealliance/StarlingMonkey/blob/9dda8ba7fcda2e17c6795d402f0478cf4c1f7f37/cmake/spidermonkey.cmake)
explicitly selects `--without-intl-api`; its release workflow uploads these
three static distributions. This is recipe evidence for their no-Intl policy,
not a new forensic inspection of every uploaded archive.

The genuine source remains
[`bytecodealliance/firefox`](https://github.com/bytecodealliance/firefox/tree/9dab3d6f643e926a340c391ea30968e940390dec),
tag `FIREFOX_147_0_4_RELEASE_STARLING`, exact commit
`9dab3d6f643e926a340c391ea30968e940390dec` (milestone `147.0.4`). The matching
fork release API returned 404. GitHub's commit tarball endpoint responds, but
its HEAD response supplied no archive size or published SHA-256; its ETag is
not treated as an archive digest. Two exact Mozilla `mozjs-147.0.4.tar.xz`
release paths also returned 404. These finite checks do not establish that no
other public source package exists.

The fork has a real
[`js/src/make-source-package.py`](https://github.com/bytecodealliance/firefox/blob/9dab3d6f643e926a340c391ea30968e940390dec/js/src/make-source-package.py)
(12050 bytes, SHA-256
`fd92c50f50621bcc9076f0f7dbd630a6958f01e5da80375d6922d95b3cf88047`).
It generates `mozjs-147.0.4.tar.xz` using rsync staging and tar, and rewrites
the root Cargo workspace/path patches. Its closure includes all `js/src`,
public JS headers, build/config/Mach Python support, mfbt/NSPR/memory/mozglue,
fdlibm/zlib/fmt, selected testing/tools files, all vendored Rust and most
vendored Python. Intl adds ICU, ICU C API, segmenter data and bidi sources.
Root `Cargo.toml` is an additional packager input. This canonical closure is
not a measured minimal build closure.

Although the packager excludes `intl/icu/source/data`, it retains
[`config/external/icu/data/icudt78l.dat`](https://api.github.com/repos/bytecodealliance/firefox/contents/config/external/icu/data/icudt78l.dat?ref=9dab3d6f643e926a340c391ea30968e940390dec):
15660880 bytes, Git blob SHA-1
`9a8c6136b565b2e6e9375e57405b4c0c499d1254` (not SHA-256). The exact backend
places ICU common/i18n/data into the static JS library. Actual generated
backend/archive membership must confirm this after building; the existing
22 extra-object merge alone is not evidence of Intl closure. ICU4X/bidi must
also join the engine's single Rust aggregate separately.

The initial CI path deliberately reuses the existing module's **full shallow
checkout**, verifies the exact commit before Mach, and explicitly selects
source build plus Intl. Merely omitting `SPIDERMONKEY_BINARIES` would otherwise
allow the existing no-Intl release download. A filtered sparse checkout plus
the genuine packager is a possible later optimization, not an executed or
validated recipe. Rsync filters cannot be copied directly into Git sparse
rules: their matching/precedence semantics differ, and packaging also has
generated/Cargo-rewrite inputs.

The Linux SDK input is [WASI SDK 30 x86_64 Linux](https://github.com/WebAssembly/wasi-sdk/releases/download/wasi-sdk-30/wasi-sdk-30.0-x86_64-linux.tar.gz),
119449290 bytes, published SHA-256
`0507679dff16814b74516cd969a9b16d2ced1347388024bc7966264648c78bfb`.
CI requires **20 GiB free initially and stops below 4 GiB**. These are
conservative policy thresholds, not measured build peaks or sufficient-space
guarantees. Compressed asset sizes and the ICU data size do not bound full
source/Git, object, ThinLTO, Rust and staging peaks, so the metadata does not
justify reducing this to the roughly 4.6 GiB local headroom. No global runner
cleanup or version switch is part of this selection.

A new library artifact remains experimental until coherent headers/archive
closure, the single Rust aggregate, a fresh full engine and the retained
Unicode/dependency/full Next.js runtime contracts pass. This note grants no
build or runtime authority.
