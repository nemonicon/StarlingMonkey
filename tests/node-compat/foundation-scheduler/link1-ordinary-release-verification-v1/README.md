# Link1 ordinary Release diagnostic: independent verification

This packet independently reads existing frozen build and component evidence.
It does not import a preflight/runner/packager or run a compiler, Node oracle,
host command, component or guest. The latest accepted compatibility checkpoint
remains v11. The new private diagnostic is separate from production admission.

The fixed normal engine is
`46fc6588397bc7ca332369600fe3d561897001d79611b25d7dca1d9b462a373b`,
9,764,917 bytes, with metadata `99ee415e…`, recipe `24e5dc9a…` and freeze receipt
`c0d04828…`. Normal configuration, native database, parent Ninja commands,
wrapper and four final-link witness files are read only from the label-specific
immutable freeze. No mutable original normal configuration is dereferenced
while the separate GC build reuses that project.

The verifier checks all345 copied files, native306+diagnostic2, three external
embedding inputs, actual61 native commands and parent1+1 commands. It parses
the final-target Ninja command as data and binds generated Clang `-Wl` flags,
Release/ThinLTO/post-wasm-opt arguments and frozen wrapper/tool records. Spawned
LLD arguments, actual thread counts and resource benefits remain unobserved.

The corrected driver-v2 has32 pre/post inputs, including the exact **live**
repository Preview1 adapter path. Its current bytes, fixed input freeze, driver
index and immutable native-consumer ledger are read and hashed. The separate
[production correction note](../production-release-adapter-closure-correction-v1/README.md)
preserves the earlier production-seal omission; this diagnostic correction
does not implicitly amend those unactivated production packets.

Ten actual components, their generated core/modules/declarations, source and
15 original/actual glue pairs are bound to the result. A narrow binary-section
reader independently checks zero top-level imports; it does not repeat complete
Component Model type validation. Recorded Node phases, three retained main Jco
calls and fresh Wasmtime, configured subsequent classic evaluation, INIT before
content, late binding, five initialization failures, three successful controls
and three fresh fatal/discard boundaries are checked without replaying them.

Ordinary pending-entry native hex operations and application queue ownership
do not prove forced GC. First-ever classic startup, INIT-before-jobs priority,
hidden fatal-cause identity, reset, ALS, request teardown and post-fatal reuse
remain unproved. Generic traps are boundary observations. Existing stdout/
stderr and Root's separately preserved observer-label mistake are evidence
inputs; the mistaken observer assertion is not a driver failure.

[results.json](results.json) records exact checks, artifact scope and the full
read hash closure. [verify.py](verify.py) writes only this new packet. No earlier
packet, live source, frozen input or recorded run result is edited.
