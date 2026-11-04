# Production artifact tools: independent source review

No remaining concrete source-contract blocker was found in the five recorded
source hashes. This review is separate from Root's actual native execution and
from any future freeze, actual-pin adoption or component acceptance.

The source implements production recipe869/native306/external3 with61 actual
native commands, four strict commands and one separate embedding command. The
freezer calls the actual finite source selector before engine access, captures
only actual after-build Ninja embedding evidence, validates all destinations
before exclusive copying and rehashes copies/originals. Schema1 matches both
reviewed consumers. Rust/OpenSSL evidence and attribution are preserved;
libcrypto remains an explicit reference. The tooling adapter copy does not
replace the live adapter runtime seal.

One review finding was corrected before this seal: receipt bytes and digest are
now captured together, checked before/after validation, and the exporter uses
that captured digest. The launcher retains its existing three-value validation
API and separately reviewed lifecycle. Export states remain unreviewed and
cannot activate either consumer pin selector.

Fresh independent host runs passed67 Python and17 Node checks. They use pure
metadata/commands, old sidecars without engine access and tiny owned text-copy
fixtures. No launcher/freezer/exporter main, compiler, packager, Wasmtime or guest
runs here. Copy failures remain nontransactional and no fault/durability proof
is claimed. No runtime, reset/ALS/reuse, capability, API or resource benefit is
inferred. [results.json](results.json) records hashes, the resolved finding,
contracts, test reports and limits. The reviewed sources and old evidence were
not modified by this reviewer.
