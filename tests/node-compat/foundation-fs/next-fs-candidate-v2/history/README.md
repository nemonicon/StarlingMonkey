Attempt1: Node refused an illegal strict directive with a destructured parameter; the factory now has a simple parameter and destructures inside.

Attempt2: real selected Stats Date comparison found Node rounds milliseconds (primary Node internal-fs-utils.js dateFromMs); the facade now uses Math.round before Date construction.

Attempt3: actual classic UTF8 stream with one-byte chunks stalled under synchronous read completion (Node exits13 for unsettled top-level await). Read completion now uses the actual supplied private-next-tick seam, which lets classic maybeReadMore clear its active-turn flag before a decoder emits an empty partial-character result. No classic production code changed.

Attempt4 passed31 tests and is retained before adding five targeted ownership/Node-stream checks. Current results supersede that test set. No compiler or guest ran in any attempt.
