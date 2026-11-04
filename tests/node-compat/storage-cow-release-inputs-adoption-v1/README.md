# Release input copy-on-write execution

Two direct clonefile calls succeeded. Independent verification confirms identical
logical bytes and required metadata, unchanged source identities, distinct new
target inodes, and removal of all recorded temporary and rollback files. The
observed global free-space change is only 3,612,672 bytes and is nonexclusive;
no unique-extent or 722 MB recovery claim is made.

[Results](results.json) link the independent postverification. The earlier
compression rejection is separate and unchanged. No compiler, library or guest
execution occurred in this storage operation.
