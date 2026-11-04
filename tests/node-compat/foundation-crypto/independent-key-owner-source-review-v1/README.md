The bounded source/API/allocator/GC-policy review of `key-owner-candidate-v1`
(`216d0272…`) passes. The four afterimages remain unapplied. This review grants no
integration, build, link, key, crypto, GC, guest, OOM, reset or runtime authority.

All35 indexed files and1,185 original-context references match their declared
bytes. The four source afterimages reconstruct and reverse exactly through18
edits, and an independently generated unified patch matches the owner patch.
Live and configured355 preimages remain unchanged. `reader.py` is a data reader;
it imports no owner function and runs no compiler or target runtime.

The finalizer has a real class hook and the actual147 foreground flag. Its two
private owner slots are checked independently, cleared before deletion, and do
not depend on initialized Algorithm or Type fields. It performs no JS allocation
or callback. The class retains eight reserved slots, and its native owners
contain no JS edges; ordinary JS-valued slots remain engine-traced. The actual
SDK permits nursery allocation of finalized classes only with SKIP_NURSERY,
which this candidate does not set. The supplied exact147 ObjectKind and JSObject
witnesses support foreground, zone-thread finalization.

I additionally checked the exact147 [native-object creation source](https://raw.githubusercontent.com/bytecodealliance/firefox/FIREFOX_147_0_4_RELEASE_STARLING/js/src/vm/NativeObject-inl.h)
and [slot initialization source](https://raw.githubusercontent.com/bytecodealliance/firefox/FIREFOX_147_0_4_RELEASE_STARLING/js/src/vm/NativeObject.h):
creation initializes used slots through `initSlots`, whose fixed and dynamic
paths initialize them as Undefined. This substantiates the empty-prototype and
partial-factory case by source inspection; it is not an observed GC result.

All four factories retain native ownership through fallible JS work and transfer
it only at the final private-slot publication. HMAC now publishes the recoverable
vector owner. Its local/import-error and finalizer deleter cleanses current
logical bytes before deleting the vector. It does not erase spare capacity,
decoded JWK strings, earlier input copies or other provider copies. The span
uses the vector’s actual size instead of the former int32 slot conversion; large
lengths and the OpenSSL int conversion still require a separate bounds policy.

The eight sign/verify bodies are byte-exact. Their borrowed vector/EVP access is
synchronous, takes HandleObject keys, and is backed by SubtleCrypto RootedObject
variables in the caller. This rooting conclusion applies to factory-created
keys. RSA’s exponent buffer now pairs JS_malloc with FreePolicy, retains its
owner on failed ArrayBuffer adoption, releases only after successful adoption,
and checks the rooted Uint8Array before dereference. These match the actual SDK
allocator/adoption contract. The constructor rejection, ctor_length0, global
installation override, property specifications and four getter prototype guards
are preserved.

The pinned OpenSSL3.0.17 implementation already frees and nulls a newly allocated,
initially-null `EVP_PKEY_fromdata` output on import failure. Immediate RAII at both
sites is defensible ordering; the stored source does not demonstrate a leak at
those existing failure paths. OPENSSL_cleanse linkage and actual finalizer/wipe
execution remain unproved.

The two stored SDK command/result records are coherent with the actual frozen
Release compile prototypes and a four-file VFS overlay. They report syntax-only
exit0, retain O3/NDEBUG/no-exceptions/wasm32-WASI flags, and contain no diagnostic
warnings or errors. The1,104 logical compiler-dependency union matches both
stored dependency files and current physical bytes. Those dependencies were
hashed after the frontend only. I did not rerun either compiler command, observe
its original terminal status, or infer an object, link, engine or runtime pass.

Required BIGNUM partial-extraction ownership, private-copy erasure, and
allocation/length follow-ons stay open. An additional pre-existing source concern
is recorded in `findings.json`: the public getters reject CryptoKey.prototype,
but sign/verify key admission uses the class predicate, which also recognizes
that prototype, before internal helpers assume initialized slots. Prototype-as-key
negative behavior needs a separate source guard audit before any such runtime
case. No negative probe ran, and this concern is not introduced by the owner
delta.

The existing four355 native tuples are historical inputs. Changed crypto bytes
must receive a fresh source lineage/recipe/admission integration and actual new
build/freeze/link reviews. No old helper can accept them by metadata projection.
No full crypto ownership completion, all-copy erasure, isolated rooting,
finalizer-count, cryptographic correctness, bounded allocation or performance
claim follows from this source review.
