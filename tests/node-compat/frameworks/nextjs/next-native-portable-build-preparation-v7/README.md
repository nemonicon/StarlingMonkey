This Source-only policy successor selects Mat5's six-file read-based Fetch
resource cleanup on the existing 40ee file-URL loader. The selected recipe is
825 files (435 native, 387 support, 3 embedding), 7,554,682 bytes. The Mat5
index must be reviewed and sealed before this policy is final.

`run.py`, `prepare.py`, `cargo-selection.py` and the generator-facing local
`portable.py` are byte-identical to BuilderV6. The root-authority template is
also unchanged. Only `portableSourcePolicy` and the identical Cargo helper's
own absolute path change. The external V2 admission API, actual offline Cargo
proof, all 21 base-file checks, tool/Python roles, CMake/Rust/offline/jobs flags,
7200s build monitor and 3GiB start/1GiB phase floors are unchanged.

Default preparation is read-only. Explicit fresh output writes only preparation
JSON; any generator/build needs a separate late Root authority and fresh proof.
No old materialization, generator result, build metadata, engine, component,
import-function count or runtime outcome is projected onto the new Source.
All operational Source slots remain null and actionsAllowed remains false.

`test-source.py` compares the actual Source bytes and fixed policy fields and
parses Python text. It does not import preparation/action entrypoints, create
source payloads or execute Node, Cargo, a compiler, engine or guest.
