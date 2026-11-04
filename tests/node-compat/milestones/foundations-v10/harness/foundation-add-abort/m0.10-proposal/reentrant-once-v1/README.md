# Removed once-listener record: separate unapplied correction

The ordinary pinned Node22 oracle confirms the proposed m0.10 implementation
needs an additional record-identity correction. No original or proposed
Starling guest path was executed. The accepted strict-v3 memory-safety fix and
its engine/source/proof records are unchanged.

[node-results.json](node-results.json) records four passing public-API cases:
ordinary once, protected addAbortListener once, protected once after an outer
stopImmediatePropagation, and an ordinary remove/re-add control. All events are
valid synthetic Event instances; no actual controller abort, fault injection,
private memory, DEBUG or malformed carrier is involved.

The counterexample has earlier listener A followed by once listener B. During
the outer abort dispatch, A performs a nested synthetic abort dispatch. B runs
inside that nested dispatch and re-registers itself. Node's observed order is:

```text
earlier:outer
earlier:nested
later:nested
later:readded
earlier:after-nested
earlier:second
later:second
earlier:third
```

B does not run again in the outer traversal. This is evidence for this precise
nested scenario, not a claim that Node uses a frozen full listener snapshot.
Pinned Node event_target.js uses a linked list: dispatch caches the next record,
Listener.remove marks the old record removed and unlinks it, and a subsequent
registration allocates a distinct Listener. The outer traversal retains the
removed old record and skips it. The public oracle tests both protected and
ordinary registrations without consulting Node private state.

The source-only Starling trace differs. EventTarget::invoke_listeners clones
RefPtr records into a rooted vector. The nested once dispatch marks B's record
R removed before calling B. Existing strict-v3 add_listener re-addition then
resets R.removed=false and moves that same RefPtr to the target list's end.
The outer vector still owns R, so the outer iteration can invoke it again.
The m0.10 protected flag does not prevent this revival; protected R can also run
after the outer listener calls stopImmediatePropagation.

[native-removed-once-record-v1.patch](native-removed-once-record-v1.patch) is a
separate proposal applied **after** the original protected-option and receiver
patches in an isolated source copy. Only the selected derived feature changes.
When an equal removed record is found, it drops the target-list reference and
uses the existing fresh-record allocation/initialization/checked-append path.
The old R stays removed and remains owned/traced by any active dispatch clone;
the newly registered R2 is absent from those existing vectors. Macro-OFF code
retains the accepted v3 branch exactly. Active duplicate records still retain
their existing once/protected flags.

The patch adds no JS-visible API, host interface, allocation mechanism or
asynchronous task. It reuses the existing new-listener path, including its
reported append failure. Allocation failure and guest behavior remain
unexecuted; no new allocator-success claim follows from this proposal.

[syntax-results.json](syntax-results.json) records two actual SDK30/SM147
syntax-only checks (feature selected and feature OFF, both strict). The helper
first revalidates the immutable original proposal receipt and all its listed
source/patch/check hashes. It does not alter those records, link an engine or
run a guest. The new source receipt pins the sole additional CPP delta and the
exact Node oracle/source evidence.

Before integration, root must review this separate patch with the protected
listener proposal and require the same four valid cases in an actual new
ordinary Release component. General EventTarget ordering, registration getter
timing, pre-stopped propagation, arbitrary list mutation and AbortSignal
lifetime limitations remain open as documented in the original proposal.
