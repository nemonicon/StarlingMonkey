Proposed main-README addendum: optional future guest regression entry point.

`run-guest-regression.py` is an **unexecuted Source-only convenience fork** of
executed `run-guest-check.py` SHA256
`f1554ab33fc9442f8fbfb59fea9c6bc2d8e2cba8f280b188099ed898c40ac1be`.
The original script and its first guest11/41 result/records remain unchanged.
No help, preparation, helper, Node, guard or target execution has been performed
by this fork's author. Root owns all later execution.

After Source review, Root may explicitly choose a fresh ID and separately
prepare then run it, using its existing pinned Python3.11 with `-I -B`:

```
python3.11 -I -B run-guest-regression.py --prepare --run-id regression-001
python3.11 -I -B run-guest-regression.py --run --run-id regression-001
```

Use the script's actual absolute path or run from this Root-results directory.
`--run-id` is required for either mode and must wholly match
`[a-z0-9][a-z0-9-]{0,47}`:1–48 lowercase ASCII letters/digits/hyphens, starting
with a letter/digit. Invalid IDs refuse before helper loading or outputs.
`--help` exits through argparse before any helper/admission/action.

Each preparation exclusively reserves `guest-runs/<run-id>/` and writes
`cache-overlap-runtime-authority.json` and `runtime-preparation.json` there.
An existing run directory, even empty, refuses a new preparation. Run mode
requires exactly those two canonical ordinary files, their genuine matching
run/controller/actor/review selection, and fresh actor work/monitor paths.
Owner completion/error receipts go to that same run directory as
`runtime-owner-result.json`. Existing receipts, additional files, work or
monitor directories refuse reuse. Partial/error records are retained; nothing
is removed, overwritten, retried or reclaimed automatically. A failed
preparation needs Root inspection and a new ID for another preparation.

The temporary output remains the actor's actual `outputPrefix + '-' + runId`,
with its original `-external-root` monitor suffix. The actor, plan, constructor,
engine and complete metadata admission are unchanged. The twelve actual DATA
roles, eleven flags,1GiB floor, original180-second owner, exact Source-family
joins, before/final genuine guards, complete bounded capture and original
error-preservation path are retained. Preparation still uses the original
runtime authority schema; it launches no actor. Run mode performs one actor
invocation only. This script schedules no repetitions or comparison campaign,
waives no original cache/application gate, and supplies no fullNext or
reliability acceptance. The existing actual guest11/41 pass is separate DATA,
not evidence that this convenience fork has run.
