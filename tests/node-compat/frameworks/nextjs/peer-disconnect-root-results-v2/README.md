# Unused V2 construction request

The construction request and launcher were prepared but never executed.
Independent review found that V2 allocated its AbortController after resource
ownership entry and before the handler's try/finally. A constructor throw could
skip both normal cleanup and the outer pre-entry cleanup.

V2 Source and this unused request remain unchanged. The narrow V3 successor
moves allocation inside the existing cleanup block. No V2 component, ordinary
export, fault/OOM test or peer workload exists from this request.
