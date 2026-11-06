// Private native guest FS provider. UNCOMPILED Source; no embedding/host API.
#ifndef STARLING_NODE_COMPAT_NEXT_FS_NATIVE_H
#define STARLING_NODE_COMPAT_NEXT_FS_NATIVE_H

#include "js/TypeDecls.h"
#include "js/Utility.h"
#include <cstddef>
#include <cstdint>

namespace builtins::node_compat::next_fs {
constexpr size_t MaxFileBytes = 16 * 1024 * 1024;
constexpr size_t MaxPathBytes = 4096;
constexpr size_t MaxDirectoryEntries = 4096;
constexpr size_t MaxSymlinks = 32;

// Values are the actual wasi:filesystem/types@0.2.10 descriptor-type enum.
struct Metadata {
  uint8_t type = 0;
  uint64_t size = 0;
  uint64_t links = 0;
  bool has_atime = false, has_mtime = false, has_ctime = false;
  double atime_ms = 0, mtime_ms = 0, ctime_ms = 0;
};

// Every provider checks EngineInitialized +the real deployed-entry bit before
// inspecting path bytes, allocating native storage or calling a WASI import.
bool check_deployed(JSContext* cx, const char* operation);
bool read_bytes(JSContext* cx, const char* path, size_t path_length,
                JS::UniqueChars* bytes, size_t* length);
bool stat_path(JSContext* cx, const char* path, size_t path_length,
               bool follow, Metadata* result);
bool realpath(JSContext* cx, const char* path, size_t path_length,
              JS::UniqueChars* canonical, size_t* canonical_length);
bool cwd(JSContext* cx, JS::UniqueChars* value, size_t* length);

// read_bytes returns JS_malloc-owned storage and a trailing NUL outside logical
// bytes. All WASI resources are already closed. A caller may transfer successful
// ownership to a JS ArrayBuffer or an appropriate owned SourceText buffer;
// it must not borrow an inline GC buffer across compilation/GC instead.
} // namespace builtins::node_compat::next_fs
#endif
