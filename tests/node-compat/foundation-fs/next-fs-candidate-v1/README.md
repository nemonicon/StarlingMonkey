UNSEALED, UNCOMPILED WIP ONLY.

See checkpoint-status.json for exact completed Source and unfinished publicStream/factory/registration/build/test gates. No index or SourcePASS is issued. The private native provider and handle code have not been compiled or executed. Production files and all existing artifacts are unchanged.

ActualAPI choice is standard WASI0.2.10 filesystem/types+preopens directly, not a fake filesystem or custom host service. All acquisitions require the existing real deployed bit and EngineInitialized. SDK libc headers expose a cached preopen population/register path but no reset API; direct resources avoid relying on that snapshot state. Root must configure real standard preopens/rights/cwd. Provider-owned JS_malloc bytes can be adopted by actual SDK147 ArrayBuffer ownership API without another wholefile Buffer copy.

Remaining publicReadStream must hold one real descriptor across reads, use the actual installed classicReadable, push bounded chunks/backpressure and close on EOF/error/destroy. No eager read-whole or reopen-perchunk substitute counts as implementation. ALS callback resource capture must use actual native queue/task hooks when integrated; no JS .then/context patch.

The source-family-only Node audit extracted fs builtins from the authenticated Node22 binary. Upstream code/license are DATA references; the guest receives no process.binding API. No native compile/link/engine/guest or hostFS scratch workload ran.
