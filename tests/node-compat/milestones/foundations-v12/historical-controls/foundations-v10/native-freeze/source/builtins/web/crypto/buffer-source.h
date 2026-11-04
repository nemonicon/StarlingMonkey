#ifndef BUILTINS_WEB_CRYPTO_BUFFER_SOURCE_H
#define BUILTINS_WEB_CRYPTO_BUFFER_SOURCE_H

#include "builtin.h"
#include "js/ErrorReport.h"
#include "js/MemoryFunctions.h"
#include <cstring>
#include <utility>

namespace builtins::web::crypto {

// Owned native bytes survive JS getters, promise allocation, GC and host calls.
// Raw key copies are wiped before their JS::FreePolicy owner releases storage;
// message copies avoid an unnecessary additional byte pass.
class CopiedBufferSource {
  JS::UniqueChars storage_;
  size_t length_ = 0;
  bool sensitive_ = false;

  void clear() {
    if (sensitive_ && storage_) {
      volatile char *bytes = storage_.get();
      for (size_t i = 0; i < length_; ++i) bytes[i] = 0;
    }
    storage_.reset();
    length_ = 0;
  }

public:
  CopiedBufferSource(JS::UniqueChars storage, size_t length, bool sensitive)
      : storage_(std::move(storage)), length_(length), sensitive_(sensitive) {}
  CopiedBufferSource(CopiedBufferSource &&other) noexcept
      : storage_(std::move(other.storage_)), length_(std::exchange(other.length_, 0)),
        sensitive_(other.sensitive_) {}
  CopiedBufferSource &operator=(CopiedBufferSource &&other) noexcept {
    if (this != &other) {
      clear();
      storage_ = std::move(other.storage_);
      length_ = std::exchange(other.length_, 0);
      sensitive_ = other.sensitive_;
    }
    return *this;
  }
  CopiedBufferSource(const CopiedBufferSource &) = delete;
  CopiedBufferSource &operator=(const CopiedBufferSource &) = delete;
  ~CopiedBufferSource() { clear(); }

  std::span<uint8_t> bytes() const {
    if (!length_) return {};
    return {reinterpret_cast<uint8_t *>(storage_.get()), length_};
  }
};

inline bool validate_crypto_buffer_source(JSContext *cx, JS::HandleValue value,
                                         const char *description) {
  if (!value.isObject() ||
      !(JS_IsArrayBufferViewObject(&value.toObject()) || JS::IsArrayBufferObject(&value.toObject()))) {
    return api::throw_error(cx, api::Errors::InvalidBuffer, description);
  }
  JS::RootedObject object(cx, &value.toObject());
  size_t ignored_length = 0;
  bool shared = false;
  uint8_t *ignored_data = nullptr;
  if (JS_IsArrayBufferViewObject(object)) {
    js::GetArrayBufferViewLengthAndData(object, &ignored_length, &shared, &ignored_data);
  } else {
    JS::GetArrayBufferLengthAndData(object, &ignored_length, &shared, &ignored_data);
  }
  // BufferSource (unlike getRandomValues' AllowShared input) excludes shared
  // views. No payload pointer escapes validation or survives a JS callback.
  if (shared) return api::throw_error(cx, api::Errors::InvalidBuffer, description);
  return true;
}

inline std::optional<CopiedBufferSource> copy_crypto_buffer_source(
    JSContext *cx, JS::HandleValue value, const char *description, bool sensitive = false) {
  if (!validate_crypto_buffer_source(cx, value, description)) return std::nullopt;
  JS::RootedObject object(cx, &value.toObject());
  size_t length = 0;
  bool shared = false;
  uint8_t *ignored_data = nullptr;
  if (JS_IsArrayBufferViewObject(object)) {
    js::GetArrayBufferViewLengthAndData(object, &length, &shared, &ignored_data);
  } else {
    JS::GetArrayBufferLengthAndData(object, &length, &shared, &ignored_data);
  }
  JS::UniqueChars copy;
  if (length) {
    copy.reset(static_cast<char *>(JS_malloc(cx, length)));
    if (!copy) {
      JS_ReportOutOfMemory(cx);
      return std::nullopt;
    }
  }
  bool changed = false;
  {
    JS::AutoCheckCannotGC no_gc(cx);
    size_t current_length = 0;
    bool current_shared = false;
    uint8_t *data = nullptr;
    if (JS_IsArrayBufferViewObject(object)) {
      js::GetArrayBufferViewLengthAndData(object, &current_length, &current_shared, &data);
    } else {
      JS::GetArrayBufferLengthAndData(object, &current_length, &current_shared, &data);
    }
    changed = current_shared || current_length != length || (length && !data);
    if (!changed && length) std::memcpy(copy.get(), data, length);
  }
  if (changed) {
    api::throw_error(cx, api::Errors::InvalidBuffer, description);
    return std::nullopt;
  }
  return CopiedBufferSource(std::move(copy), length, sensitive);
}
} // namespace builtins::web::crypto

#endif
