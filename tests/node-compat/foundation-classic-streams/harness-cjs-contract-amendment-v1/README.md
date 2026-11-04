This source-only amendment corrects the classic guest fixture's use of the
existing static CommonJS contract. It does not change native code, the bundler,
the completion amendment, or any sealed predecessor.

The actual normal-OFF attempt stopped in profile-bundler.mjs before invoking
componentization because guest.mjs contained four require() calls in an ESM
file. The unchanged bundler permits those calls only in explicit .cjs input.
The original stderr is preserved under failure-evidence/. A componentizer module
had already been loaded by the driver, but no componentization operation,
application component or guest invocation completed in that attempt.

The new cjs-bindings.cjs contains exactly four admitted literal builtin requires
and exports their values as one record. The ESM guest default-imports the record
and destructures the same four variable names. Its graph/identity assertions and
the separate ordinary19 check body are unchanged. Two exact reversible edits
restore the parent guest hash. No public runtime require() is installed.

The actual host bundler check reads the reviewed normal-OFF342 metadata and
selected manifests. It confirms the old fixture is refused and the new fixture
retains exactly node:stream, node:stream/promises, node:buffer, node:events and
node:util. The lowered .cjs.native-profile.mjs module is present; no facade or
JavaScript builtin adapter is bundled. Neither bundle was executed. The new
fixture and this index must enter a new activation family's consumed seal.
The existing completion driver/helper remain mandatory.

Preparation-history records two source-check expectation failures: a comment
matched a simple require-text assertion, and a module-ID assertion initially
expected the original CJS filename instead of the bundler's existing synthetic
filename. Both preceded the final successful host-bundle check. No native
build, componentizer operation, application guest or target host ran here.
