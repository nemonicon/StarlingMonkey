# Independent corrected production regression source review

V3 index `3064605fbf043c26e3d1bc85378b91d68c98be4034f4b6c5cf0f30f964ac61a2`
passes this source review with no remaining concrete blocker found. All 22
indexed files and all 665 consumed inputs were independently rehashed. All 21
preserved v2 entries still match index `705e0823…`; none was rewritten.

This review **supersedes the earlier v2 no-blocker conclusion**. The owner found
a concrete gap after that conclusion: the final recheck followed the current
manifest without binding it to the pre-run manifest digest. The reviewer missed
that gap. The v2 source packet and [initial review](../independent-production-regression-review-v2/README.md)
remain historical records. Null actual pins prevented any real-artifact run
from reaching the affected branch; no runtime or native failure is claimed.

V3 captures primitive expected pins and manifest digests before a run. Its final
recheck compares pins first, then reads the manifest once and checks the exact
buffer's digest **before parsing or following rows**. It checks each file's hash
and length using that manifest. Private expected digests and copied frozen-file
rows keep later checks independent of returned report objects and pin buffers.
The owner's seven scratch-data cases cover matching state, changed listed bytes,
replacement manifest plus matching data, rejection before parsing/following new
rows, changed pins and returned-object mutation. Its 41 host results were read,
not rerun by this review; they establish no real artifact admission.

Admission, null pins, all three wrapper bodies and both generated allocator
runners are byte-identical to v2. Independently reversing their declared edits
again restores both original v11 runner byte sequences, including the GC guest
and historical v7/v10 controls. The existing finite selector and native safety
helpers remain the authoritative downstream checks after fixed-artifact proof.

This is readiness of source preparation for core, allocator and allocator GC.
Actual reviewed production pins, a compatible real freeze, the positive artifact
branch, remaining module/strict/HTTP gates and all runtime results remain future
work. There is no diagnostic metadata projection, new engine admission, scheduler
ownership/ALS/reset proof or lower launch guard. No owner file was edited, and no
candidate helper/test, compiler, build, link, guest or storage operation was run.

[review.json](review.json) binds this correction and the reviewed source hashes.
