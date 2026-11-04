# Private build/correctness pair passed; timing pending

Both engines were built sequentially at the **same absolute project/build paths**
with the unchanged frozen-v8 recipe. The complete baseline engine/source/config
freeze preceded the two-file candidate switch. All actual flags, CMake cache/
compile-command hashes, external embedding inputs,29 held linked archives and
198 SDK/compiler/archive inputs match. The profile-code archive changes as
expected. Native files differ only in buffer-facade.mjs and its generated header.

| Arm | Engine SHA256 | Engine bytes | Minimal component bytes |
| --- | --- | ---: | ---: |
| Baseline | `ad9566a22f0fc265023304ac4dd955bfa7e9c209cf24a9be06522e6ed0f0ea77` | 9,732,337 | 12,054,311 |
| Direct candidate | `2332fcb49bd9ceb0e260b29ce572b425e1a5f4cf0127ac2eedefbe35a63b9279` | 9,732,323 | 12,062,824 |

The candidate engine is14B smaller and its retained minimal snapshot is8,513B
**larger**. These are exact artifact observations; snapshot byte determinism or
a component-size benefit has not been established.

Both installed corpora pass10 Node differential groups, five allocation-policy
groups,240 pure-JS refusal checks, six numeric-hook cases, exact BufferList
demand, retained Jco calls1/2, fresh Wasmtime42, owned snapshot/shared views,
native namespaces/bare aliases/default/global/static-CJS and eleven
initialization failures. Candidate hooks run zero times versus baseline once,
proving the changed body is actually installed. Ordinary behavior passes while
this explicit out-of-contract numeric-hook difference remains documented.

Both minimal components pass identical source/world/bundle/options/case inputs,
45 cases in each of two fresh Jco instances, full zero/no-pool checks at three
sizes, repeat-after-corpus and15 fresh Wasmtime cases per arm. Both emit **zero
imports**. This is native registration of the existing JS facade on captured
native Uint8Array; no new C++ allocator kernel is introduced.

The first minimal packaging attempt used an ambiguous old report field pointing
to Jco buffer.js rather than a Wasm preview1 adapter. It failed componentNew,
emitted no component, and is preserved in `../minimal-attempt1`. The approved
runner correction pins the same actual private-project Wasm adapter to
SHA98822428…fabcc0, and passes in a fresh output directory. Old accepted reports,
native engines, source/recipe/controller25-file checkpoint remain unchanged.

Full actual engine metadata,332-file freeze receipts per arm, actual build
configuration/commands, raw build/correctness logs and complete corpus reports
are retained here. The large engine/source artifacts remain under the receipt's
indexed private frozen paths; unchanged native ancestry is also recoverable from
the original v8 source checkpoint and reviewed patches. No OOM/fault/DEBUG/raw
memory work, production apply or performance execution is included.
