# Unapplied private m0.11 direct-allocation pair

This checkpoint contains a reviewable source optimization candidate and host
semantic checks. **No native engine/component has been built, no performance
execution has run, and no production source is changed.** The measured v8 m0.8
counterexample and all historical reports remain immutable.

The private pair starts from frozen v8 engine
`e16c19fc567753517d7b61b65372dd7dc86de8f839e7acab959b5cf5eaf294c9` and293
verified source inputs. Both arms carry the same coordinator-reserved private
`sm-node-22.14.0-m0.11` manifest/helper metadata. This is a private experiment,
not two interchangeable production receipts selected by version alone.
[source-receipt.json](./source-receipt.json) pins all61 copied Node-compat files
in ancestry/baseline/candidate forms and the complete293-input ancestry.

## Exact change

The baseline retains:

```js
return unsafeApply(unsafeAlloc, Buffer, [unsafeTrunc(length)]);
```

The candidate changes only that return expression:

```js
return tagTrusted(new U8(unsafeTrunc(length)));
```

Existing primary type, captured finite, raw-limit and truncation validation,
captured error constructors and own error fields stay byte-identical. `U8` is
the existing trusted installation-time constructor capture; `tagTrusted` is the
existing private prototype/WeakSet-brand path. No API, C++ byte kernel, borrowed
pointer, allocator handoff, shared memory, pool or host capability is added.
`Buffer.alloc` remains unchanged. Unused `unsafeAlloc`/`unsafeApply` captures and
the historical m0.8 comment remain in **both** private arms to isolate the single
expression. They are not an exposed alternate allocator or installer.

[direct-from-common.patch](./direct-from-common.patch) changes exactly the facade
expression and its generated core literal/digest. All other copied files,
including helper, manifest, optional headers, registrar and native buffer.cpp,
match between arms. [common-m0.11-from-v8.patch](./common-m0.11-from-v8.patch)
creates the common private version metadata from frozen v8;
[candidate-m0.11-from-v8.patch](./candidate-m0.11-from-v8.patch) is the combined
unapplied alternative. Do not apply both alternatives in sequence. All three
patches pass `git apply --check` against isolated source copies. Both generators
and `--check` pass using the existing dependency-free generator.

The source removes the captured-alloc invocation, secondary `size()` validation
and explicit `fillBytes(...,0)` from this operation. A successful paired
measurement would attribute a result to **that complete expression change**, not
identify which removed cost dominates. No part of the existing v8 slowdown is
attributed to fill, validation or native execution without the new matched pair.

## Ownership and observable contract

Fresh typed-array length allocation already zero-initializes storage; the
candidate retains that guarantee without a second fill. The stable
[ECMA-2622025 typed-array allocation](https://262.ecma-international.org/16.0/#sec-allocatetypedarraybuffer)
creates an ArrayBuffer through the standard allocator; its
[byte data-block operation](https://262.ecma-international.org/16.0/#sec-createbytedatablock)
initializes every byte to zero. Supporting local SpiderMonkey147 public
typed-array documentation and exact hash are retained in
[the API proof](./api-proof.md).

The same finite nonnegative raw-size16MiB cap is enforced before truncation.
Fractions, signed zero, ordinary call/new/bind/derived/new-target behavior,
arity/name/prototype attributes, genuine WeakSet branding, fresh exact backing at
offset0, empty allocation independence, shared slice/subarray views, poolSize
independence and supported error kinds/codes remain the selected contract.
The allocation is JS-owned; the ordinary VM references/closure keep the result,
constructor and branding machinery reachable. There is no embedding pointer to
root, pin, detach, transfer or free. Small `.buffer` materialization stays deferred
until observable access through the same existing trusted path.

Removing secondary validation **changes out-of-contract mutable numeric-hook
behavior**. The baseline consults ambient `Number.isInteger` and an additional
ambient `Number.isFinite` inside captured Buffer.alloc. The candidate uses the
already captured primary finite/truncation functions and does not make either
secondary call. The host report explicitly checks both hooks returning false,
returning true and throwing a sentinel:

* Baseline invokes each hook once. A throwing hook escapes unchanged; false
  isInteger yields the existing `fractional size` coded refusal; false isFinite
  yields the existing secondary RangeError path.
* Candidate invokes neither hook and returns a zeroed length3 Buffer for valid
  input3.75 in each case.

This is not exact preservation under arbitrary mutations of Number/global
objects. Invalid ordinary API inputs still fail the unchanged captured primary
validation with the same own `code/module/operation` fields. Other Buffer
validation paths retain their existing primordial assumptions. No new genuine
OOM/Error-allocation behavior is claimed; allocation failures propagate without
catch/fallback, and OOM/fault/DEBUG execution is outside this work.

## Completed host gates and remaining review

[host-results.json](./host-results.json) passes four forms: baseline/candidate ESM
and exact generated factories evaluated as strict scripts. Each form runs the
same10 Node differential groups, five installed allocation-policy groups,
240 safely scoped pure-JS refusal call/new checks (all91 existing own prototype
functions), six numeric-hook cases, and positive species/mapped-brand/descriptor
checks. Default/export descriptor order and frozen object relationships match.
The reference kernel is an explicit host-only test double; the direct allocator
uses real host Uint8Array, and no crypto/hex kernel operation is involved. Web
constructor setup and ordinary Node oracles stay outside poison windows. No
Node native codec/error oracle or actual child-process capability runs under
inherited Error-field poison.

`stage.mjs --check` verifies source/patch receipts without mutation. `run-host.mjs`
repeats only host semantic checks. Native linkage, installed namespaces/aliases/
CJS, snapshot resumption, target instantiation and performance remain untested
for this candidate. The [dependency-ordered plan](./plan.json) requires review
before any private build, exact native/lib/recipe matching, full installed corpus
reuse before timing, and a separate coordinated timing window.

Parallel m0.9 work is not silently included or overwritten. These sources pin
v8 ancestry; before any production promotion, common accepted changes require a
separately reviewed/re-receipted rebase in **both** arms and rerun semantic/native
gates. No actual core manifest/version or active receipt selector is edited here.
