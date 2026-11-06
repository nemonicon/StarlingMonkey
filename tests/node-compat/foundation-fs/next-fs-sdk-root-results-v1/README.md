The three actual WASI-SDK frontends for the direct-P2 filesystem kernel,
registration and deployed-policy accessor all finished raw0, with empty output
and clean owned groups. The exact [plan](../next-fs-sdk-syntax-v1/plan.json) uses
the pinned SpiderMonkey147 headers and actual9aec compile flags plus
`NODE_COMPAT_FS=1`. V3's safe constant-inspection amendment preserves V2's native
filesystem kernel byte-for-byte.

The retained result contains3,080 postcompile dependency records. These are
hashes captured **after** the commands, not a whole-SDK before/after protection
claim. The declared source/compiler/database/monitor inputs were preserved.
No object, link, engine or guest was executed. This result does not establish
runtime Buffer ownership, native GC behavior, preopen path routing, symlinks,
mount rights, stream cancellation or Next's nested cache layout.

Run `python3 -B -I tests/node-compat/foundation-fs/next-fs-sdk-root-results-v1/check-evidence.py`
to recheck the portable copied raw evidence without replaying the compiler.
The full result and small raw streams/dependency files are retained under
`evidence/`; `root-result.json` identifies the original outer monitor and Root
authority. The dormant runner requires a fresh output generation for any new
execution. Source bodies and earlier findings remain unchanged.
