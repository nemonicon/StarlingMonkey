# Native stack capture prototype

This is the C++ half only, derived from the current V6 startup file. The
[mapping](mappings.json) records the exact before/after hashes for the single
installed path `builtins/node-compat/next-startup.cpp`. Existing
`NODE_COMPAT_NEXT_STARTUP` selection and `create_next_startup_kernel` remain;
the only new private method is `captureFrames(limit, startAfter)`. Existing
deployed-only environment, FS, clock and stdio guards are unchanged.

The private contract accepts a finite integer limit from 0 through 128 without
coercing other values. Zero returns an empty array before capture or
`startAfter` validation. Otherwise an omitted/undefined `startAfter` is allowed;
a supplied target must be callable and a genuine `JSFunction`. Callable
proxies/wrappers raise identifiable `ERR_SM_NODE_UNSUPPORTED` TypeError.

The pinned [Stack API](https://github.com/bytecodealliance/firefox/blob/9dab3d6f643e926a340c391ea30968e940390dec/js/public/Stack.h)
requires a positive `MaxFrames`. Its actual
[capture implementation](https://github.com/bytecodealliance/firefox/blob/9dab3d6f643e926a340c391ea30968e940390dec/js/src/vm/SavedStacks.cpp#L1356-L1451)
consumes that budget while searching for the target and only recognizes
`JSFunction` targets. This prototype therefore uses a separate 512-frame
native capture/search budget when a target is supplied, then emits at most the
requested 128 records. A missing/beyond-budget target raises
`ERR_SM_NODE_STACK_LIMIT` RangeError. That is an explicit bounded deviation
from Node's empty result for an unknown target. No `AllFrames` capture or
unbounded fallback is used.

Every emitted record contains only `{source, functionName, line, column}`.
The five SavedFrame accessors receive the current realm's principals and
exclude self-hosted frames. Any `AccessDenied` becomes
`ERR_SM_NODE_STACK_ACCESS_DENIED`; empty source/line-zero observations are not
replaced with inferred locations. Function names may be null. Column uses the
SDK's `TaggedColumnNumberOneOrigin::oneOriginValue()` representation. No stack
string parsing, eval/receiver/native flags or filename heuristics are present.

Stack, parent, target, names, array, records and property values are GC-rooted.
`AutoHoldPrincipals` brackets the principal pointer. SavedFrame strings are
wrapped into the current realm with `JS_WrapValue`. Records use own data
properties, and array elements use `JS_DefineElement`, avoiding inherited
array setters. SavedFrame objects never escape through the returned records.
This function can allocate/GC or throw, but obtains no WASI handles, clocks,
entropy or other resources; pure INIT capture is permitted independently of
the existing deployed-only methods.

The one actual SDK 30/SpiderMonkey 147 frontend completed **raw 0**, clean
owned groups, empty stdout/stderr, under the original 60-second monitor. The
actual C2 compile-database row supplied all defines/includes; only `-o`/`-c`
were removed, with syntax/dependency flags and a file-only VFS overlay added.
The overlay preserves the original virtual filename for relative includes.
[Plan](sdk-observation/plan.json), [terminal](sdk-observation/monitor/terminal.json)
and [result](sdk-observation/result.json) are exact retained text copies.
Seventeen selected source/API/tool inputs matched before/final. The actual
dependency file lists 1,034 paths, but those paths were **not all independently
preauthenticated**; this observation claims no new whole-SDK preservation
attestation. No object, link, engine or guest execution occurred.

This remains an existing-API syntax prototype, **not the final Error fix**.
The public SavedFrame API cannot establish `isEval` provenance. Root/B's
separate guest SpiderMonkey change must retain that Boolean and expose a new
principal-filtered getter/capability macro. A later native successor must use
the genuine getter and reject old headers with a compile-time guard. The JS
CallSite/lazy Error facade, coherent rebuilt library/engine and actual guest
regressions remain separate work. Original V5/V6 inputs are untouched.
