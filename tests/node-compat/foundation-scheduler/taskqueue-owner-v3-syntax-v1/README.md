# Isolated v3 diagnostic syntax supplement

The **one changed diagnostic TU passes** the approved SDK syntax check, with
zero diagnostics. [results.json](results.json) records the command and compiler.
It uses the identical frozen v11 Release/`-Werror` flags, v2 staged header overlay,
and `NODE_COMPAT_INTERNAL_TICKS=1`; only the diagnostic source input differs.
The four unchanged queue/event-loop/Engine/embedding TUs were not recompiled.

The [v2](../taskqueue-owner-v2/index.json) and [v3](../taskqueue-owner-v3/index.json)
source packets and indices remain byte-identical. Their source-only status is
preserved historically; this separate receipt records the later syntax result.
No linking, new engine, live apply, guest, foreign-callback probe, DEBUG or fault
test occurred. Reset/cancellation safety remains OPEN. Successful syntax does not
establish scheduling behavior, installation or zero emitted component imports.
