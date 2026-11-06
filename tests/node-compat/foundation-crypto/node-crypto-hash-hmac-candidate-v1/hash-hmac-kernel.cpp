// UNCOMPILED SOURCE TEMPLATE. Not installed in any current native artifact.
#include "builtin.h"
#include "js/ArrayBuffer.h"
#include "js/ArrayBufferMaybeShared.h"
#include "js/MemoryFunctions.h"
#include "js/experimental/TypedData.h"
#include <openssl/core_names.h>
#include <openssl/crypto.h>
#include <openssl/evp.h>
#include <openssl/params.h>
#include <openssl/provider.h>
#include <openssl/rsa.h>
#include <openssl/opensslv.h>
#include <cstring>
#include <memory>
#include <new>

namespace builtins::node_compat {
namespace {
constexpr size_t MaxMessage = 16 * 1024 * 1024, MaxKey = 1024 * 1024;
constexpr size_t MaxTotal = 64 * 1024 * 1024, DigestSize = 32;
// Copy baseline is the default. Enabling borrowing requires explicit review of
// this exact SDK/OpenSSL/provider build and later runtime/GC/import evidence.
#ifndef NODE_CRYPTO_AUDITED_BORROW
#define NODE_CRYPTO_AUDITED_BORROW 0
#endif
DEF_ERR(CryptoInput, JSEXN_TYPEERR, "Unsupported native crypto input or state", 0)
DEF_ERR(CryptoFailure, JSEXN_ERR, "Native SHA256 operation failed", 0)
DEF_ERR(CryptoLimit, JSEXN_RANGEERR, "Native SHA256 profile limit exceeded", 0)
static bool error(JSContext *cx, const JSErrorFormatString &format) {
  return api::throw_error(cx, format);
}
struct MdFree { void operator()(EVP_MD *p) const { EVP_MD_free(p); } };
struct CtxFree { void operator()(EVP_MD_CTX *p) const { EVP_MD_CTX_free(p); } };
struct MacFree { void operator()(EVP_MAC *p) const { EVP_MAC_free(p); } };
struct MacCtxFree { void operator()(EVP_MAC_CTX *p) const { EVP_MAC_CTX_free(p); } };
struct State {
  bool hmac = false;
  size_t total = 0;
  // Contexts are destroyed before their algorithm owners (reverse order).
  std::unique_ptr<EVP_MD, MdFree> md;
  std::unique_ptr<EVP_MAC, MacFree> mac;
  std::unique_ptr<EVP_MD_CTX, CtxFree> digest;
  std::unique_ptr<EVP_MAC_CTX, MacCtxFree> auth;
};
struct SensitiveBytes {
  JS::UniqueChars storage;
  size_t length = 0;
  ~SensitiveBytes() { if (storage) OPENSSL_cleanse(storage.get(), length); }
  bool allocate(JSContext *cx, size_t n) {
    // One owned byte even for an empty key: EVP_MAC_init(nullptr, 0) means
    // reinitialize, whereas a nonnull pointer with length zero is an empty key.
    storage.reset(static_cast<char *>(JS_malloc(cx, n ? n : 1)));
    if (!storage) { JS_ReportOutOfMemory(cx); return false; }
    length = n;
    return true;
  }
};
static void retire(JSObject *obj) {
  JS::Value slot = JS::GetReservedSlot(obj, 0);
  if (!slot.isUndefined()) {
    auto *state = static_cast<State *>(slot.toPrivate());
    JS::SetReservedSlot(obj, 0, JS::UndefinedValue());
    delete state;
  }
}
static void finalize(JS::GCContext *, JSObject *obj) { retire(obj); }
static const JSClassOps StateOps = { .finalize = finalize };
// Native pointers are NOT JS heap edges; no traced JS Value is hidden here.
// This foreground finalizer owns/deletes State, unlike auto-traced JS slots.
static const JSClass StateClass = {
  "PrivateNodeSha256State", JSCLASS_HAS_RESERVED_SLOTS(1) | JSCLASS_FOREGROUND_FINALIZE,
  &StateOps
};
static State *get_state(JSContext *cx, JS::HandleValue value) {
  if (!value.isObject() || JS::GetClass(&value.toObject()) != &StateClass) {
    error(cx, CryptoInput); return nullptr;
  }
  JS::Value slot = JS::GetReservedSlot(&value.toObject(), 0);
  if (slot.isUndefined()) { error(cx, CryptoInput); return nullptr; }
  return static_cast<State *>(slot.toPrivate());
}
static bool fixed_u8(JSContext *cx, JS::HandleValue value,
                     JS::MutableHandleObject view, JS::MutableHandleObject backing,
                     size_t maximum, size_t *length) {
  if (!value.isObject()) return error(cx, CryptoInput);
  view.set(&value.toObject());
  bool shared = false;
  uint8_t *ignored = nullptr;
  if (!JS_GetObjectAsUint8Array(view, length, &shared, &ignored) || shared ||
      JS::IsResizableArrayBufferView(view)) return error(cx, CryptoInput);
  // Materialization can allocate. Root both objects before borrowing.
  backing.set(JS_GetArrayBufferViewBuffer(cx, view, &shared));
  if (!backing) return false;
  if (shared || JS::IsDetachedArrayBufferObject(backing) ||
      JS::IsResizableArrayBufferMaybeShared(backing)) return error(cx, CryptoInput);
  if (*length > maximum) return error(cx, CryptoLimit);
  return true;
}
static bool copy_window(JSContext *cx, JS::HandleObject view, size_t length,
                        SensitiveBytes &owned) {
  if (!owned.allocate(cx, length)) return false;
  bool bad = false;
  {
    JS::AutoCheckCannotGC nogc(cx);
    bool shared = false;
    const auto *p = JS_GetUint8ArrayData(view, &shared, nogc);
    bad = shared || JS_GetTypedArrayByteLength(view) != length || (length && !p);
    if (!bad && length) std::memcpy(owned.storage.get(), p, length);
  }
  return bad ? error(cx, CryptoInput) : true;
}
static bool default_allocators() {
  CRYPTO_malloc_fn a; CRYPTO_realloc_fn r; CRYPTO_free_fn f;
  CRYPTO_get_mem_functions(&a, &r, &f);
  return a == CRYPTO_malloc && r == CRYPTO_realloc && f == CRYPTO_free;
}
static bool default_provider(const OSSL_PROVIDER *p) {
  return p && std::strcmp(OSSL_PROVIDER_get0_name(p), "default") == 0;
}
static bool issue(JSContext *cx, std::unique_ptr<State> state, JS::MutableHandleValue out) {
  JS::RootedObject handle(cx, JS_NewObjectWithGivenProto(cx, &StateClass, nullptr));
  if (!handle) return false; // state remains owned on every allocation failure
  JS::SetReservedSlot(handle, 0, JS::PrivateValue(state.release()));
  out.setObject(*handle);
  return true;
}
static std::unique_ptr<State> allocate_state(JSContext *cx) {
  std::unique_ptr<State> state(new (std::nothrow) State());
  if (!state) JS_ReportOutOfMemory(cx);
  return state;
}
static bool create_hash(JSContext *cx, unsigned argc, JS::Value *vp) {
  auto args = JS::CallArgsFromVp(argc, vp);
  if (!default_allocators()) return error(cx, CryptoFailure);
  auto state = allocate_state(cx);
  if (!state) return false;
  state->md.reset(EVP_MD_fetch(nullptr, "SHA256", "provider=default"));
  state->digest.reset(EVP_MD_CTX_new());
  if (!state->md || !state->digest || EVP_MD_get_size(state->md.get()) != DigestSize ||
      !default_provider(EVP_MD_get0_provider(state->md.get())) ||
      EVP_DigestInit_ex2(state->digest.get(), state->md.get(), nullptr) != 1)
    return error(cx, CryptoFailure);
  return issue(cx, std::move(state), args.rval());
}
static bool create_hmac(JSContext *cx, unsigned argc, JS::Value *vp) {
  auto args = JS::CallArgsFromVp(argc, vp);
  if (!args.requireAtLeast(cx, "privateCreateHmac", 1)) return false;
  JS::RootedObject view(cx), backing(cx);
  size_t length;
  if (!fixed_u8(cx, args[0], &view, &backing, MaxKey, &length)) return false;
  SensitiveBytes key;
  if (!copy_window(cx, view, length, key)) return false;
  if (!default_allocators()) return error(cx, CryptoFailure);
  auto state = allocate_state(cx);
  if (!state) return false;
  state->hmac = true;
  state->mac.reset(EVP_MAC_fetch(nullptr, "HMAC", "provider=default"));
  if (!state->mac || !default_provider(EVP_MAC_get0_provider(state->mac.get())))
    return error(cx, CryptoFailure);
  state->auth.reset(EVP_MAC_CTX_new(state->mac.get()));
  char digest[] = "SHA256", properties[] = "provider=default";
  OSSL_PARAM params[] = {
    OSSL_PARAM_construct_utf8_string(OSSL_MAC_PARAM_DIGEST, digest, 0),
    OSSL_PARAM_construct_utf8_string(OSSL_MAC_PARAM_PROPERTIES, properties, 0),
    OSSL_PARAM_construct_end()
  };
  if (!state->auth || EVP_MAC_init(state->auth.get(),
      reinterpret_cast<const unsigned char *>(key.storage.get()), length, params) != 1 ||
      EVP_MAC_CTX_get_mac_size(state->auth.get()) != DigestSize)
    return error(cx, CryptoFailure);
  // The pinned default provider copies key bytes. No JS/key pointer is stored.
  // key's logical bytes are cleansed on success and every error return.
  return issue(cx, std::move(state), args.rval());
}
static int update_state(State *s, const uint8_t *p, size_t n) {
  if (!n) return 1;
  return s->hmac ? EVP_MAC_update(s->auth.get(), p, n)
                 : EVP_DigestUpdate(s->digest.get(), p, n);
}
static bool update(JSContext *cx, unsigned argc, JS::Value *vp) {
  auto args = JS::CallArgsFromVp(argc, vp);
  if (!args.requireAtLeast(cx, "privateUpdate", 2)) return false;
  State *s = get_state(cx, args[0]);
  if (!s) return false;
  JS::RootedObject handle(cx, &args[0].toObject()), view(cx), backing(cx);
  size_t length;
  if (!fixed_u8(cx, args[1], &view, &backing, MaxMessage, &length)) return false;
  if (s->total > MaxTotal - length) return error(cx, CryptoLimit);
  int ok = 0;
#if NODE_CRYPTO_AUDITED_BORROW
  if (!default_allocators()) { retire(handle); return error(cx, CryptoFailure); }
  bool changed = false;
  {
    // Only the audited default SHA256/HMAC update executes here. It consumes
    // bytes synchronously, without JS entry or a retained input pointer.
    JS::AutoCheckCannotGC nogc(cx);
    bool shared = false;
    const uint8_t *p = JS_GetUint8ArrayData(view, &shared, nogc);
    changed = shared || JS_GetTypedArrayByteLength(view) != length || (length && !p);
    if (!changed) ok = update_state(s, p, length);
  }
  if (changed) { retire(handle); return error(cx, CryptoInput); }
#else
  SensitiveBytes owned;
  if (!copy_window(cx, view, length, owned)) { retire(handle); return false; }
  ok = update_state(s, reinterpret_cast<const uint8_t *>(owned.storage.get()), length);
#endif
  if (ok != 1) { retire(handle); return error(cx, CryptoFailure); }
  s->total += length;
  args.rval().setUndefined();
  return true;
}
static bool digest(JSContext *cx, unsigned argc, JS::Value *vp) {
  auto args = JS::CallArgsFromVp(argc, vp);
  if (!args.requireAtLeast(cx, "privateDigest", 1)) return false;
  State *s = get_state(cx, args[0]);
  if (!s) return false;
  JS::RootedObject handle(cx, &args[0].toObject());
  JS::RootedObject out(cx, JS_NewUint8Array(cx, DigestSize));
  if (!out) { retire(handle); return false; }
  unsigned char bytes[DigestSize] = {};
  size_t n = 0; unsigned int md_n = 0;
  const int ok = s->hmac ? EVP_MAC_final(s->auth.get(), bytes, &n, sizeof(bytes))
                        : EVP_DigestFinal_ex(s->digest.get(), bytes, &md_n);
  if (!s->hmac) n = md_n;
  retire(handle); // finalizer later sees undefined; native state freed once
  if (ok != 1 || n != DigestSize) {
    OPENSSL_cleanse(bytes, sizeof(bytes));
    return error(cx, CryptoFailure);
  }
  {
    JS::AutoCheckCannotGC nogc(cx);
    bool shared = false;
    auto *p = JS_GetUint8ArrayData(out, &shared, nogc);
    MOZ_ASSERT(!shared && p);
    std::memcpy(p, bytes, DigestSize);
  }
  OPENSSL_cleanse(bytes, sizeof(bytes));
  args.rval().setObject(*out);
  return true;
}
} // namespace
JSObject *create_crypto_hash_hmac_kernel(JSContext *cx) {
  JS::RootedObject result(cx, JS_NewPlainObject(cx));
  if (!result) return nullptr;
  JS::RootedObject constants(cx, JS_NewPlainObject(cx));
  if (!constants) return nullptr;
  auto number = [&](const char *name, double n) {
    JS::RootedValue value(cx, JS::NumberValue(n));
    return JS_DefineProperty(cx, constants, name, value,
                             JSPROP_ENUMERATE | JSPROP_READONLY | JSPROP_PERMANENT);
  };
  // Real guest-header values, not numbers borrowed from the host Node binary.
  // These constants do not enable RSA operations or attest cipher availability.
  if (!number("OPENSSL_VERSION_NUMBER", OPENSSL_VERSION_NUMBER) ||
      !number("RSA_PKCS1_PADDING", RSA_PKCS1_PADDING) ||
      !number("RSA_NO_PADDING", RSA_NO_PADDING) ||
      !number("RSA_PKCS1_OAEP_PADDING", RSA_PKCS1_OAEP_PADDING) ||
      !number("RSA_X931_PADDING", RSA_X931_PADDING) ||
      !number("RSA_PKCS1_PSS_PADDING", RSA_PKCS1_PSS_PADDING) ||
      !number("RSA_PSS_SALTLEN_DIGEST", RSA_PSS_SALTLEN_DIGEST) ||
      !number("RSA_PSS_SALTLEN_MAX_SIGN", RSA_PSS_SALTLEN_MAX_SIGN) ||
      !number("RSA_PSS_SALTLEN_AUTO", RSA_PSS_SALTLEN_AUTO)) return nullptr;
  JS::RootedValue constants_value(cx, JS::ObjectValue(*constants));
  if (!JS_DefineProperty(cx, result, "constants", constants_value, 0)) return nullptr;
  static const JSFunctionSpec methods[] = {
    JS_FN("createHash", create_hash, 0, JSPROP_ENUMERATE),
    JS_FN("createHmac", create_hmac, 1, JSPROP_ENUMERATE),
    JS_FN("update", update, 2, JSPROP_ENUMERATE),
    JS_FN("digest", digest, 1, JSPROP_ENUMERATE), JS_FS_END
  };
  return JS_DefineFunctions(cx, result, methods) ? result.get() : nullptr;
}
} // namespace builtins::node_compat
