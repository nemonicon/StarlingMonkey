# Fixed Next completion comparison

The fixed ten-trial comparison completed. Both prepared Node controls pass;
one of eight guest trials passes the original full contract. The other seven
retain failed generation counters, and three also fail strict browser completion.
These exploratory samples establish neither a fix nor reliability.

The [coordinated DATA review](../../tests/node-compat/frameworks/nextjs/next-completion-comparison-root-results-v1/actual-cohort-review.json)
(`3929a4af`) verifies these outcomes while retaining failed overall acceptance.
The [ownership/browser review](../../tests/node-compat/frameworks/nextjs/next-completion-comparison-root-results-v1/actual-owner-browser-review.json)
and [marker review](../../tests/node-compat/frameworks/nextjs/next-completion-comparison-root-results-v1/actual-marker-review.json)
cover their separate scopes. Root independently checks all eight stdout hashes
and captured marker arrays. Portable raw-DATA retention and both current/Git-mode
offline checks pass.

## Exact scope and outcomes

The unchanged standalone Next 16.4.5 application, engine `476b1c1d`, default
browser worker and original assertions run in the declared order below. Each
trial has a fresh server, app copy, cache and browser contexts. The original
owners retain 600-second native and 300-second Node limits under the original
7,200-second cohort owner. All ten authorities existed before trial 1. Each
trial ran once, with no replacements or extra repetitions.

| Trial | Arm | Response logger | Explicit neutral await | Strict browser | Legacy generation | Original suite |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Node, block1 | N/A | N/A | Pass | 1→2 | Pass |
| 2 | A, block1 | Off | Off | Pass | 1→1 | Fail |
| 3 | B, block1 | Off | On | Pass | 1→2 | Pass |
| 4 | C, block1 | On | Off | Fail | 1→1 | Fail |
| 5 | D, block1 | On | On | Pass | 1→1 | Fail |
| 6 | Node, block2 | N/A | N/A | Pass | 1→2 | Pass |
| 7 | D, block2 | On | On | Fail | 1→1 | Fail |
| 8 | C, block2 | On | Off | Fail | 1→1 | Fail |
| 9 | B, block2 | Off | On | Pass | 1→1 | Fail |
| 10 | A, block2 | Off | Off | Pass | 1→1 | Fail |

A selects component `d990ecc1`; B `59a88505`; C `c6ae13b9`; D `dda80e61`.
The B/D entries each add only `await` to the corresponding A/C neutral-handler
return. C/D share the response logger. The earlier cd60 child-handler observer,
holder allocation and fulfillment logger are absent from these arms.
The original async return already adopted the Promise; an added await changes
scheduling and is not a missing-adoption fix.

Every trial passes 24 HTTP cases, 52 persistent-cache checks, 80 supplemental
checks, five incremental stream chunks and both functional browser interactions.
The guest components retain exactly 13 selected standard WASI 0.2.10 interface
imports and only the incoming-handler export. These entry variants add no host
capability. Independent DATA review hashes the current app and each owned copy,
cache records, protected text and metadata. Large binary/tool payloads are
explicitly delegated to their accepted build/INIT records and actual guards;
this review does not rebuild or rerun them.

The [fixed plan](../../tests/node-compat/frameworks/nextjs/next-completion-comparison-root-results-v1/plan.json),
[cohort authority](../../tests/node-compat/frameworks/nextjs/next-completion-comparison-root-results-v1/cohort-authority.json)
and [actual cohort result](../../tests/node-compat/frameworks/nextjs/next-completion-comparison-root-results-v1/cohort-result.json)
retain every ordered sample. `driverCompleted:true` records complete collection;
`originalAllPassed:false` preserves the failed application gates. No full Next
or production acceptance follows from the outer raw0.

## Implications and next work

Strict browser completion is A 2/2, B 2/2, C 0/2 and D 1/2 in this cohort. Two samples
per arm do not estimate reliability or establish a logging/await effect. Earlier
A/C failures and the separate cd60 positive remain unchanged. B/block1's full
pass does not waive B/block2's counter failure or establish request affinity.

The browser review's completed-DATA inspection places all three failed
POST7 terminals before capture drain and explicit context close, in each
observer's own arrival clock. All pre-close drains report complete. This gives
no support for a longer context-shutdown wait as the next intervention; it does
not identify the cancellation cause or align guest, browser and NetLog clocks.

All four C/D samples contain 54 response-site records, six at each of nine
positive sites, despite their different browser outcomes. No catch, logger
error, truncation or malformed frame is observed. These derived counts do not
account for every call or authenticate physical request/instance identities.
Complete adapter-site markers remain narrower than export-Promise, event-loop,
host task or transport completion. A/B do not select that logger, so its absence
there is inapplicable to completion claims. D retains the old record schema;
the historical C whole-entry/no-added-await contract does not describe D.

The [retained corpus and reader](../../tests/node-compat/frameworks/nextjs/next-completion-comparison-root-results-v1/retained-raw-data-v1/README.md)
contain 1,332 payload files/32,007,325 bytes. Run `python3 -I -B check.py` in that
directory to verify copied DATA without original paths or target execution.
Root's [actual offline check](../../tests/node-compat/frameworks/nextjs/next-completion-comparison-root-results-v1/retained-data-check.json)
passes, as does the separate Git-mode check. Omitted binaries, app/cache trees
and full 52/80-case semantics are explicitly outside that replay's scope.

Next prioritize a comprehensive second-host profile with an exact self-origin
egress rule and the unchanged application checks, plus explicit persistent-cache
overlap/error tests. Keep the original generation-counter failure separate from
the [portable request-state contract](nextjs-request-state-contract.md).
No native patch, default-entry change, broader retry campaign or production
promotion is selected from this exploratory comparison.
