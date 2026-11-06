# Raw-string caller working-directory correction

This minimal successor retains the V2 authority/result/audit wires. Root must
issue a new authority bound to this Source index and fresh output prefix
`/private/tmp/starling-node-compat/next-native-component-v3`. Actual engine and
metadata remain late Root inputs; no engine, package, adapter or world changes.

Only the construction Node command now runs with cwd equal to this held caller
directory. Its owned TMPDIR stays `outputRoot/tmp`; validate and WIT commands
still run from the output root. Node verifies cwd at entry/final and the wrapper
records actual command cwd. The output root must lie outside the held Source.

The genuine installed API's raw-string branch sets `sourcePath=sourceName`, then
if its temporary sourcesDir descends from cwd it slices that short filename by
the absolute cwd length. The prior output-root cwd therefore emptied source.js;
the runtime fell back to missing ./index.js after builtins installed. The prior
enginec2 construction result288b2e91 and raw terminal/stderr remain unchanged.

Running from held Source outside output/tmp skips that faulty package branch,
preserving the real source.js argument and the API's sourcesDir-only Wizer root
mapping. No custom runtimeArgs, source rewriting, invented loader, package patch
or host/world widening is used. The exact WIT-only official tool preopen fix and
full return capture remain unchanged. App contents are still runtime-only.

`test-raw-path.mjs` extracts and executes only the genuine installed API path/
argv preparation statements with the actual inert platform helper. Seven host
DATA cases reproduce the empty old script and show the new nonempty script and
proper mapdir. It imports no componentizer and runs no Wasm/Wizer/engine/guest.
The shared capture helper is byte-identical to V2; its18 capture tests and seven
WIT-data negatives remain inherited. No native rebuild or actual retry occurred
in Source preparation. Root must review and authorize the next bounded attempt.
