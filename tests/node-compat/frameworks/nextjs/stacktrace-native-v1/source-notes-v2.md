# Native eval-provenance successor

[after-v2/next-startup.cpp](after-v2/next-startup.cpp) is a separate, uncompiled
successor of the held v1 capture prototype. [mappings-v2.json](mappings-v2.json)
records five exact edits and verifies that reversing them restores v1's
complete bytes. The original startup file and v1 syntax observation remain
unchanged.

The new file requires `JS_HAS_SAVEDFRAME_IS_EVAL == 1` in the actual included
SavedFrame header. It calls the new principal-filtered
`JS::GetSavedFrameIsEval(cx, principals, frame, &isEval, Exclude)` and emits
`isEval` only after **all** accessor results are `Ok`. Unknown provenance or
principal refusal returns `AccessDenied` in the proposed guest API; its false
output default is never accepted as an ordinary-frame observation. The native
helper throws the existing identifiable `ERR_SM_NODE_STACK_ACCESS_DENIED`
instead. No filename, stack-string or missing-data inference is introduced.

The dependency is the authenticated
[guest patch](spidermonkey-patch/index.json), index
`531bcc7e777b8451d903da23c13bc6e3a005d2a63e90aab1569167d9d25b8a23`;
its proposed `js/public/SavedFrameAPI.h` has SHA-256
`fc3b58f8706814517ae9c12a218c0df6a4df943874f59cdf70054e7f7db75934`.
All 27 indexed patch payloads were read/hash-checked before this integration.
That patch is Source only. Its matching guest library does not exist yet.

Rooting, principal holding, string wrapping, plain own records, 128 emitted
frames/512 target-search budget, proxy refusal and resource-free operation are
unchanged from v1. The existing startup selection/kernel is reused; no CMake,
builtin or host-service interface is added. All existing deployed-only guards
remain intact.

No v2 compiler or guest command ran. V1's actual old-SDK syntax success does
not transfer to this API. A macro flag or substituted header alone cannot
provide the missing library symbol or establish coherent layout/provenance.
The complete guest patch, matching headers/library, new native producer,
frontend/link/engine checks and actual guest/Next regressions remain required.
The 64 passing host facade tests use genuine Node CallSites and establish
their stated host semantics only.
