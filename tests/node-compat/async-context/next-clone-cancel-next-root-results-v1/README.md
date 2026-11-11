# Real Next entry with the repaired engine

The unchanged real Next entry `022fccdf` constructs successfully with admitted
engine `e3075c14` and the separately recovered compiler. Component `bfb106fe`
is 37,274,386 bytes. Its validation, emitted-WIT inspection and complete
initialization review pass: exactly 13 selected standard WASI 0.2.10 imports,
the sole incoming-handler export, complete returned import/typed-value graph,
empty initialization environment and only the WIT parser preopen.

The original constructor, validator and WIT commands all finish with exit 0
and complete cleanup. `raw-init-records/` preserves 44 payloads / 2,881,709
stored bytes. The component binary is omitted.

No application is mounted during initialization and no ordinary export is
called. This result does not prove that the application serves correctly.
The unchanged standalone application will be mounted for the full workload.
The observer envelope `f1c32f45` now composes successfully and passes component
validation and structural review. Both embedded components match their input
bytes exactly; nominal resource types, inner post-return behavior and the same
13 standard external imports are preserved. Original composition owner 81368
and review owner 82292 exit 0 with clean cleanup. Both-host full serving,
unchanged strict browser tests, resource retirement and cost checks remain
outstanding.

`raw-composition-records/` retains 59 payloads (3,213,306 stored bytes), including
both original owners, the four composition-tool captures, structural evidence
and fresh host-tool version/identity checks. Large JSON and skeleton files use
deterministic gzip. Binaries and the full compiler/build input closure are
omitted explicitly. Root independently verifies every retained payload and its
expanded hash. This packet does not establish full application execution.

The new selection policy explicitly binds the changed native cancellation
source. It does not reinterpret the historical fixture's old source pin as
proof for the new engine. The prior passing sample and all failures remain
unchanged.
