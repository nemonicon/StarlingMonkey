# Intl guest-library build

Next.js is blocked by the actual no-Intl SpiderMonkey 147 Unicode regex
failures retained in `../regexp-unicode-probe-root-results-v1/actual-review/`.
This manual CI path builds the same fork commit with Intl enabled. It preserves
the application's source, standard WASI world, adapter and host.

`cmake/spidermonkey.cmake` now has opt-in `SPIDERMONKEY_BUILD_FROM_SOURCE` and
`SPIDERMONKEY_INTL` selectors. Defaults retain the existing prebuilt/no-Intl
behavior. Explicit Intl distributions require the generated configuration
macro; that check alone does not prove their ABI, Rust link closure or runtime
behavior. Fresh source selection verifies commit
`9dab3d6f643e926a340c391ea30968e940390dec` before Mach. The tiny CMake project
reuses this module and its existing merged-library target, avoiding a complete
StarlingMonkey configure solely to build this prerequisite.

`check-config.py` executes six genuine CMake configuration cases with owned
fixtures. `configuration-checks.json` records their successful evaluation,
including four intended rejection cases. No source fetch, compiler, Mach or
guest execution occurs in these tests. Fixtures are deleted afterwards.

The dedicated `.github/workflows/spidermonkey-intl.yml` is manual, read-only to
repository contents and artifact-only. It has no release/deployment step and
preserves the existing release workflow. The public fork's Actions are already
enabled. Standard `ubuntu-24.04` runner image revisions and host tool hashes
are observed inputs, not claims of a reproducible frozen operating-system
image. Action commits, Python minor release, SDK archive digest, source commit,
Rust and cbindgen versions are explicit.

`build.py` uses the existing authenticated owned-process and disk-floor
controllers. Private Mach state, Cargo/Rustup and temporary directories are
under a new run root. HOME is inherited. It requires 20 GiB initially and stops
at 4 GiB; those are conservative policies, not measured build peaks. No global
runner directories are removed. Generated mozconfig disables bootstrap and
uses one build job. Every command's raw status, log, process cleanup and disk
samples are retained. Failed configuration/compiler diagnostics are retained.
The disk floor is sampled during child commands; direct parent source/archive
packaging checks it at its boundaries. Mach's native Python packages and uv
fetch path are disabled, so absent vendored prerequisites fail visibly.

A successful library build stages dereferenced coherent headers and the actual
merged static archive, retaining archive member lists. The exact upstream
backend source expands ICU common/i18n/data objects into `libjs_static.a`;
blindly appending additional ICU archives risks duplicates. Actual archive
members and generated backend files must still confirm the observed closure.
ICU4X/unicode-bidi FFI must join StarlingMonkey's existing single Rust aggregate
in the subsequent engine build. This library job does not claim that join.

After a successful artifact: authenticate/download it, resolve and lock the
single Rust aggregate, rebuild the whole experimental engine against the new
headers, validate actual imports, then rerun the 12-case Unicode differential,
all 16 dependency controls and the unchanged full Next.js 24 HTTP/action plus
two browser contract. Preserve the old failures. Next.js remains unsuccessful
until those actual runtime gates pass.
