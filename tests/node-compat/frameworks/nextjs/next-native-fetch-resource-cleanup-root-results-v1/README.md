This directory holds execution preparation and later DATA for the separately
sealed native Fetch cleanup candidate. It is not an accepted engine or runtime
result. The current experimental engine/component and their failed full Next
trial remain unchanged.

Actual progress: V1 stopped before Popen because its owned-monitor output
directory did not exist. V2 creates that directory and preserves the V1 WORK;
its three compiler exits are 0, 0 and 1, with clean ownership and unchanged
source/tools/failed-WORK guards. Three ignored nodiscard results cause the third
TU failure. GeneratorV5's ten installed checks pass. Both failures remain
preserved; a separate source correction is required before the full build.

That separate SourceV2 correction is now sealed. Fresh Mat6/Builder8 select
only its18-byte change over the previous composition. FrontendV3 completes
0/0/0 with clean ownership and unchanged source/tool/failed-V2 guards;
independent DATA review passes. No object, linked engine or guest success
is inferred from this frontend result.

`run-frontends.py` is a Root-owned three-TU frontend driver, initially dormant
until its concrete input map is pinned. It derives actual compiler commands
from the retained successful build's Ninja log, checks them against the real
compile database, removes only dependency/object output flags and redirects
only the selected source/include prefix. It retains the existing compiler
wrapper, flags and original 180-second owned monitor per command. It creates
fresh private working/output directories and records before/final source and
complete SDK/SpiderMonkey tree guards. A compiler error remains distinct from
an ownership failure; unknown ownership after a monitor exception is not clean.

Source materialization, concrete selection admission, generator checks,
frontend compilation, link, component construction and public guest tests each
need separate actual evidence. No prior engine
metadata or import count may be retargeted to accept this source. Files in this
directory will record those results as work proceeds; the held candidate's
historical null execution slots stay unchanged.

No host modification, new WASI interface, forced GC, DEBUG, fault injection,
reset, resnapshot or production promotion is part of this step. The broader
roadmap and outstanding work remain in `progress.md` and the Next.js roadmap.
