# FS callback fixture v2: exclude traced build cache

This separate Source version changes only `next.config.mjs` from v1: the actual
pinned Next tracer excludes `./.next/cache/**` for `/api/cache`. V1 built normally
but traced eight cache files/74,976,273 bytes and is retained as not deployable.
No artifact is manually filtered. The native empty writable-cache admission stays
unchanged; the actual V2 inventory and absence of build/cache state must be reviewed.

All34 other fixture files, including helper4818/route4dc9/c101 handler, are byte
identical to V1. The original global-counter fixture/results remain unchanged.
This is a separately versioned sequential persisted-data app contract, not a
claim of cross-request JS globals, CAS, crash durability or full Next support.

The builder changes one catalogue-path literal. Exact versions and original
Node/Npm/Next four monitored phases/caps remain fixed. Source metadata actual
build/runtime fields stay NULL; Root owns later binding and execution.
