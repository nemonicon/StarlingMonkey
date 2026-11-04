# Native crypto source notes (unimplemented)

This is a source inspection, not a new Node module, compiled patch, crypto test,
performance result or operational approval. Existing checkpoint/runtime metadata
and all native source files are unchanged. No crypto function, key import,
allocator stress, GC/OOM probe or guest was executed for this note.

The existing `SubtleCrypto::digest` validates the BufferSource, normalizes its
algorithm and then obtains an owned `CopiedBufferSource`; it returns a Promise.
`CryptoAlgorithmDigest` eventually reaches the guest OpenSSL `EVP_Digest` helper.
Its result uses JS_malloc plus JS::NewArrayBufferWithContents with
CallerMustFreeMemory and releases the native owner only after success. These
are actual existing mechanisms to assess for a future bounded synchronous
`crypto.hash`; the Promise-returning public WebCrypto method cannot satisfy
Node's synchronous contract by itself. No new embedding API is proposed here.

`CopiedBufferSource` stages bytes before any borrowed payload access, rechecks
length/shared state and copies within AutoCheckCannotGC. Its sensitive-copy
mode wipes that particular native staging allocation. It does not establish
zeroization of caller-owned JS buffers, OpenSSL internals or every key copy.
Detached/resizable/shared and getter-order policy must be bounded explicitly
for any new Node surface rather than inherited by assumption.

A concrete key-ownership gap blocks blind reuse for Node Hmac/KeyObject:
CryptoKey::createHMAC stores data.release()->data() as a private slot, discarding
the vector owner; createRSA/createECDSA/createEd25519 likewise release EVP_PKEY
owners into private slots. CryptoKey inherits BuiltinNoConstructor<CryptoKey>,
which uses BuiltinImpl's DefaultClassPolicy with empty JSClassOps. Neither
CryptoKey header nor implementation declares a finalizer. The reviewed source
therefore supplies no registered cleanup owner for these native key slots.
This is source evidence, not a measured leak/GC result or a claim about an
unobserved runtime failure. The temporary hmacSignature EVP contexts already
use RAII, which does not repair the longer-lived CryptoKey owner.

A future fix must retain a recoverable owner, handle partially initialized
slots, free EVP_PKEY exactly once and wipe owned raw secret bytes before release.
BuiltinNoConstructor currently accepts one template parameter; inventing a
second policy argument would not compile. The repository's FinalizableClassPolicy
uses background finalization, so a real change must resolve thread/finalizer
policy and every CryptoKey producer and consumer before adopting it. Do not
silently change the existing no-constructor/global-install behavior.

Recommended dependency order: derive the exact crypto export inventory from
pinned Node22.14; choose a finite one-shot digest contract first; compile a
native guest entry through existing add_builtin/registration mechanisms;
validate vectors, byte windows/ownership/refusals, snapshot/retained/fresh
component behavior and imports[]; measure whole-component cost before release.
Incremental Hash/Transform semantics, copy/finalize behavior and all Hmac/key
APIs remain separate follow-ons behind the key-owner correction. Entropy, key
generation and TLS are not enabled by deterministic digest support. Any OpenSSL
initialization/entropy route and final imports still require actual validation.

Existing integration tests contain digest vectors and HMAC key import/sign
semantics; their presence is not proof that this new Node contract works or that
key lifetime is validated. No full crypto or Node compatibility is claimed.
