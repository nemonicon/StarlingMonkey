This is an unapplied, conditional source proposal for six bounded synchronous
node:zlib operations. No new kernel object, native library, engine, component or
guest has been built or executed. Current 342-source installations, recipes,
admission files and corrected checkouts are untouched.

The proposed native module has exactly the pinned 39 named bindings plus default,
registered under node:zlib and zlib from the same factory record. Six sync byte
operations are partial; the other 31 callables explicitly refuse call/new. Sync
constructors also refuse new. The optional m0.13 manifest preserves the facade's
1 MiB input / 16 MiB output limits, ordinary maxOutputLength-only options,
single-member/no-trailing/dictionary refusal and frozen data/default deviations.
No streaming, async, Brotli, CRC32, string-input or complete Node parity is claimed.

The backend policy follows fadfc: reuse the selected guest SpiderMonkey codec if
linkage and runtime identity succeed. Private native backendInfo compares the
linked zlibVersion() with ZLIB_VERSION and returns numeric ZLIB_VERNUM. Constants
and the legacy default property both use that result. The new constant source
contains no substituted Node4865 or guessed guest4880. Z_MAX_CHUNK remains numeric
Infinity. The actual guest version, archive/link authority and all new engine
pins remain NULL. A native mismatch fails registration and every codec call.

Ordinary llvm-nm inspected the selected 147 Release archive
298b85501657189dc66139242abf5aeb4e981b8db7c37cc5a69d1151ec40aacc.
All seven required definitions use MOZ_Z_* names. The actual header chain is
zlib.h → zconf.h → mozzconf.h; the latter maps those function names. Raw and
generic z_* names are absent from that audit. The proposal requires the whole
header chain and rejects generic Z_PREFIX mixing. Static definitions do not
prove linker extraction, visibility, selected compile macro ABI or runtime
version. No second codec, find_package(ZLIB), -lz or host service is added.

The existing staged-input safety baseline is preserved. Native staging allocates
before borrowing JS bytes; input is reacquired/copied inside NoGC. The codec owns
malloc/realloc/free output. One explicit copy publishes complete output into a
rooted JS-owned Uint8Array; Buffer.from(ArrayBuffer, offset, length) shares that
fresh backing. This is source copy accounting, not a minimum-copy, zero-copy,
unavoidable-copy or performance claim. Codec allocations, realloc overlap and
staging are outside the output cap. No borrow optimization is proposed.

Exact reversible source afterimages use the actual evaluate_factory and
Engine::define_builtin_module APIs with rooted kernel/Buffer arguments. CMake
adds one conditional native source and private flag on builtin_node_compat,
default OFF, reusing its existing spidermonkey linkage. Factory generation uses
the current manifest validator and strict script form. The proposed full child
manifest is derived from corrected trace342; it cannot be validated by either
old342 helper or pins. The selector afterimage deliberately rejects all hinted
new zlib ON/OFF lineages until a reviewed child producer/source policy and actual
codec proof exist. Old unhinted selection logic remains unchanged.

Checks so far are source-only: manifest/factory generation and parsing, 68 ECHO
routing/data/refusal checks, deterministic source derivations and static archive
observations. The historical 86 codec host vectors ran system zlib1.2.12; the
earlier JSAPI SDK syntax and facade host checks are separate historical evidence.
None is a guest pass. The changed native source has not had a new SDK syntax or
link test. All existing sealed parent packets remain unchanged.

Future gates are explicit: independently review this source packet; authenticate
actual zlib/zconf/mozzconf headers, archive, compile and final link commands;
perform separately approved native syntax/build/freezer work; run real guest
zlibVersion/header agreement and public constant checks; prove finite ESM/alias/
CommonJS/default behavior; compare Node cross-decode and decoded byte results
rather than compressed-byte identity; test malformed/truncated/dictionary/
multi-member/trailing/limit errors and retained/fresh ownership/GC behavior;
audit emitted imports on both stock hosts; then measure size/memory/cost if
authorized. Missing linkage stops the integration rather than selecting another
codec to imitate Node's constant. No DEBUG/OOM/reset/raw-memory work is included.
