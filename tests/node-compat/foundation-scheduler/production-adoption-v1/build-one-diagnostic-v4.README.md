# Diagnostic launcher v4: reviewed source, no native launch

[build-one-diagnostic-v4.py](build-one-diagnostic-v4.py) is a new sibling; v1-v3
remain unchanged. Its native-producer main has never run. The exact recipe stays
`1e2f15d1…`; source/build directories deliberately reuse the existing v2 project,
while future external logs use scheduler-v4 and normal artifacts/evidence use
short `r4`. GC keeps its unattempted no-tag identity. Output creation is exclusive
and requires2GiB before making its directory. Ninja/OpenSSL/Binaryen/Rayon/Cargo
worker limits are1. The monitor stops below800MiB, subject to sampling races.

Six [benign host lifecycle checks](launcher-v4-host-checks-v3/results.json) pass:
capacity/no-directory and collision, TERM leader exit with surviving grandchild,
already-exited ESRCH, monitor exception plus simulated ENOSPC publication,
external repeated TERM, and incomplete final-observation classification. Only
controlled Python child sessions ran; no producer/compiler/guest/network call
or actual disk-fill operation ran.

The launcher signals only the tracked new-session group. Cleanup checks the group
independently of leader status, tolerates ESRCH, and uses bounded TERM/KILL/reap.
SIGTERM during child handoff is recorded and acted on once ownership is known;
repeated TERM cannot interrupt bounded cleanup. The previous handler is restored.
Raw child status is preserved separately; monitor/cleanup/storage/observation
failure prevents a completed-evidence success. A result-write failure still emits
the full status on stdout. Unconfirmed cleanup is incomplete, not a success.

Earlier source/check reports remain in launcher-v4-history. The second report
retains a post-KILL EPERM observation despite completed cleanup; the revised
source reaps its own leader before group probes, and the latest checks require
no cleanup errors. No old report was silently replaced. See the
[source receipt](build-one-diagnostic-v4.source-review.json) and
[frozen index](launcher-v4-index.json). Root review is required before the actual
native launch; these checks add no compatibility, GC, reuse or performance proof.
