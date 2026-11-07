#include "script_loader.h"
#include "encode.h"
#ifdef NODE_COMPAT_VM_DATA
#include "async_context_runtime.h"
#include "node_tick_queue.h"
#include "js/Realm.h"
#endif

#include <cstdio>
#include <js/CompilationAndEvaluation.h>
#include <js/Exception.h>
#ifdef NODE_COMPAT_MODULE
#include "../builtins/node-compat/next-fs-native.h"
#include <js/CallAndConstruct.h>
#include <js/CharacterEncoding.h>
#include <js/Equality.h>
#include <js/PropertyDescriptor.h>
#include <js/Proxy.h>
#include <js/Realm.h>
#include <jsapi.h>
#include <cstring>
#include <string_view>
#endif
#include <js/MapAndSet.h>
#include <js/ScriptPrivate.h>
#include <js/String.h>
#include <js/Value.h>
#include <jsfriendapi.h>
#include <sys/stat.h>

namespace {

api::Engine *ENGINE;
ScriptLoader *SCRIPT_LOADER;
bool MODULE_MODE = true;
std::string BASE_PATH;

JS::PersistentRootedObject moduleRegistry;
JS::PersistentRootedObject builtinModules;
JS::CompileOptions *COMPILE_OPTS;

mozilla::Maybe<std::string> PATH_PREFIX = mozilla::Nothing();

} // namespace

using host_api::HostString;

namespace ScriptLoaderErrors {
DEF_ERR(ModuleLoadingError, JSEXN_REFERENCEERR,
        "Error loading module \"{0}\" (resolved path \"{1}\"): {2}", 3)
DEF_ERR(BuiltinModuleExists, JSEXN_TYPEERR, "Builtin module \"{0}\" already exists", 1)
DEF_ERR(UnsupportedImportReferrer, JSEXN_TYPEERR,
        "Non-builtin import requires object loader referrer metadata with a string id", 0)
#ifdef NODE_COMPAT_MODULE
DEF_ERR(UnsupportedCjsFileUrl, JSEXN_TYPEERR,
        "CommonJS file URL import is unsupported: {0}", 1)
#endif
}; // namespace ScriptLoaderErrors

// A release-build type boundary, not a CommonJS/file-URL loader bridge.
static bool unsupported_import_referrer(JSContext *cx, JS::HandleValue module_id,
                                        const char *operation) {
  // A real getter/VM error or OOM must never be replaced by this diagnostic.
  if (JS_IsExceptionPending(cx)) {
    return false;
  }
  api::throw_error(cx, ScriptLoaderErrors::UnsupportedImportReferrer);
  if (!JS_IsExceptionPending(cx) || JS_IsThrowingOutOfMemory(cx)) {
    return false;
  }

  JS::RootedValue exception(cx);
  if (!JS_GetPendingException(cx, &exception) || !exception.isObject()) {
    return false;
  }
  JS::RootedObject object(cx, &exception.toObject());
  // Save/root the original exception and its associated stack; annotation APIs
  // run with no pending exception. On failure drop only the saved diagnostic,
  // preserving the new exception/OOM/uncatchable status exactly as produced.
  JS::AutoSaveExceptionState saved(cx);
  JS::RootedString code(cx, JS_NewStringCopyZ(cx, "ERR_SM_MODULE_IMPORT_REFERRER"));
  if (!code) {
    saved.drop();
    return false;
  }
  JS::RootedString operation_string(cx, JS_NewStringCopyZ(cx, operation));
  if (!operation_string) {
    saved.drop();
    return false;
  }
  if (!JS_DefineProperty(cx, object, "code", code, JSPROP_ENUMERATE) ||
      !JS_DefineProperty(cx, object, "module", module_id, JSPROP_ENUMERATE) ||
      !JS_DefineProperty(cx, object, "operation", operation_string, JSPROP_ENUMERATE)) {
    saved.drop();
    return false;
  }
  saved.restore();
  return false;
}

#ifdef NODE_COMPAT_MODULE
// New, UNCOMPILED guest loader internals. No public builtin/host export.
static JS::PersistentRootedObject fileurl_module_record;
static JS::PersistentRootedObject fileurl_url_record;
static JS::PersistentRootedValue fileurl_create_require;
static JS::PersistentRootedValue fileurl_to_path;
static JS::PersistentRootedValue fileurl_from_path;
static JS::PersistentRootedValue fileurl_url_string;
static size_t fileurl_namespaces = 0;
static bool fileurl_busy = false;
static constexpr size_t MaxFileUrlNamespaces = 8192;
static constexpr size_t MaxFileUrlBytes = 3 * builtins::node_compat::next_fs::MaxPathBytes + 8;

static bool fileurl_error(JSContext *cx, JS::HandleValue specifier,
                          const char *operation, const char *reason) {
  if (JS_IsExceptionPending(cx)) return false;
  api::throw_error(cx, ScriptLoaderErrors::UnsupportedCjsFileUrl, reason);
  if (!JS_IsExceptionPending(cx) || JS_IsThrowingOutOfMemory(cx)) return false;
  JS::RootedValue exception(cx);
  if (!JS_GetPendingException(cx, &exception) || !exception.isObject()) return false;
  JS::RootedObject object(cx, &exception.toObject());
  JS::AutoSaveExceptionState saved(cx);
  JS::RootedString code(cx, JS_NewStringCopyZ(cx, "ERR_SM_MODULE_FILE_URL_UNSUPPORTED"));
  if (!code) { saved.drop(); return false; }
  JS::RootedString op(cx, JS_NewStringCopyZ(cx, operation));
  if (!op) { saved.drop(); return false; }
  if (!JS_DefineProperty(cx, object, "code", code, JSPROP_ENUMERATE) ||
      !JS_DefineProperty(cx, object, "module", specifier, JSPROP_ENUMERATE) ||
      !JS_DefineProperty(cx, object, "operation", op, JSPROP_ENUMERATE)) {
    saved.drop(); return false;
  }
  saved.restore();
  return false;
}

static bool fileurl_content_realm(JSContext *cx, JSObject *object) {
  auto *expected = JS::GetObjectRealmOrNull(ENGINE->global());
  return expected && JS::GetCurrentRealmOrNull(cx) == expected &&
         JS::GetObjectRealmOrNull(object) == expected;
}

static bool fileurl_own_data(JSContext *cx, JS::HandleObject object, const char *name,
                             JS::MutableHandleValue value, JS::HandleValue specifier) {
  JS::Rooted<mozilla::Maybe<JS::PropertyDescriptor>> descriptor(cx);
  if (!JS_GetOwnPropertyDescriptor(cx, object, name, &descriptor)) return false;
  if (descriptor.isNothing() || !descriptor->isDataDescriptor() || !descriptor->hasValue())
    return fileurl_error(cx, specifier, "module_file_url", "Required own DATA property unavailable");
  value.set(descriptor->value());
  return true;
}

static bool fileurl_own_callback(JSContext *cx, JS::HandleObject object, const char *name,
                                 JS::MutableHandleValue value, JS::HandleValue specifier) {
  if (!fileurl_own_data(cx, object, name, value, specifier)) return false;
  if (!value.isObject() || js::IsProxy(&value.toObject()) ||
      !JS::IsCallable(&value.toObject()) || !fileurl_content_realm(cx, &value.toObject()))
    return fileurl_error(cx, specifier, "module_file_url", "Genuine same-realm callable unavailable");
  return true;
}

// Called only by real builtin registration, before the application entry runs.
// Captured originals are private roots; public Module require hooks remain live.
static bool fileurl_capture_builtin(JSContext *cx, const char *id, JS::HandleValue builtin) {
  const bool module = std::strcmp(id, "node:module") == 0;
  const bool url = std::strcmp(id, "node:url") == 0;
  if (!module && !url) return true;
  if (!builtin.isObject() || js::IsProxy(&builtin.toObject()) ||
      !fileurl_content_realm(cx, &builtin.toObject()))
    return fileurl_error(cx, JS::UndefinedHandleValue, "module_file_url_capture", "Builtin record unavailable");
  JS::RootedObject record(cx, &builtin.toObject());
  JS::RootedValue a(cx), b(cx), constructor(cx), prototype(cx), string(cx);
  if (module) {
    if (!fileurl_own_callback(cx, record, "createRequire", &a, JS::UndefinedHandleValue)) return false;
    fileurl_module_record = record;
    fileurl_create_require = a;
  } else {
    if (!fileurl_own_callback(cx, record, "fileURLToPath", &a, JS::UndefinedHandleValue) ||
        !fileurl_own_callback(cx, record, "pathToFileURL", &b, JS::UndefinedHandleValue) ||
        !fileurl_own_callback(cx, record, "URL", &constructor, JS::UndefinedHandleValue)) return false;
    JS::RootedObject ctor(cx, &constructor.toObject());
    if (!fileurl_own_data(cx, ctor, "prototype", &prototype, JS::UndefinedHandleValue)) return false;
    if (!prototype.isObject() || js::IsProxy(&prototype.toObject()))
      return fileurl_error(cx, JS::UndefinedHandleValue, "module_file_url_capture", "Native URL prototype unavailable");
    JS::RootedObject proto(cx, &prototype.toObject());
    if (!fileurl_own_callback(cx, proto, "toString", &string, JS::UndefinedHandleValue)) return false;
    fileurl_url_record = record;
    fileurl_to_path = a;
    fileurl_from_path = b;
    fileurl_url_string = string;
  }
  return true;
}

static bool fileurl_call(JSContext *cx, JS::HandleValue receiver, JS::HandleValue function,
                         JS::HandleValue argument, JS::MutableHandleValue value) {
  JS::RootedValueArray<1> args(cx);
  args[0].set(argument);
  return JS::Call(cx, receiver, function, args, value);
}

static bool fileurl_string(JSContext *cx, JS::HandleValue path,
                           JS::MutableHandleValue value, JS::HandleValue specifier) {
  JS::RootedValue receiver(cx, JS::ObjectValue(*fileurl_url_record)), url(cx);
  if (!fileurl_call(cx, receiver, fileurl_from_path, path, &url)) return false;
  if (!url.isObject() || !fileurl_content_realm(cx, &url.toObject()))
    return fileurl_error(cx, specifier, "module_file_url", "Native URL result unavailable");
  if (!JS::Call(cx, url, fileurl_url_string, JS::HandleValueArray::empty(), value)) return false;
  if (!value.isString())
    return fileurl_error(cx, specifier, "module_file_url", "Native URL string unavailable");
  return true;
}

static bool fileurl_cache_entry(JSContext *cx, JS::HandleObject require,
                                JS::HandleString filename, bool *found,
                                JS::MutableHandleValue exports, JS::HandleValue specifier) {
  *found = false;
  JS::RootedValue cache(cx);
  if (!fileurl_own_data(cx, require, "cache", &cache, specifier)) return false;
  if (!cache.isObject() || js::IsProxy(&cache.toObject()) ||
      !fileurl_content_realm(cx, &cache.toObject()))
    return fileurl_error(cx, specifier, "module_file_url", "Genuine CommonJS cache unavailable");
  JS::RootedObject table(cx, &cache.toObject());
  JS::RootedId key(cx);
  if (!JS_StringToId(cx, filename, &key)) return false;
  JS::Rooted<mozilla::Maybe<JS::PropertyDescriptor>> descriptor(cx);
  if (!JS_GetOwnPropertyDescriptorById(cx, table, key, &descriptor)) return false;
  if (descriptor.isNothing()) return true;
  if (!descriptor->isDataDescriptor() || !descriptor->hasValue() || !descriptor->value().isObject())
    return fileurl_error(cx, specifier, "module_file_url", "Unsupported CommonJS cache record");
  JS::RootedObject record(cx, &descriptor->value().toObject());
  if (js::IsProxy(record) || !fileurl_content_realm(cx, record))
    return fileurl_error(cx, specifier, "module_file_url", "Cross-realm or proxy cache record");
  JS::RootedValue loaded(cx);
  if (!fileurl_own_data(cx, record, "loaded", &loaded, specifier)) return false;
  if (!loaded.isBoolean() || !loaded.toBoolean())
    return fileurl_error(cx, specifier, "module_file_url", "In-progress CommonJS target is deferred");
  if (!fileurl_own_data(cx, record, "exports", exports, specifier)) return false;
  *found = true;
  return true;
}

struct FileUrlScope {
  FileUrlScope() { fileurl_busy = true; }
  ~FileUrlScope() { fileurl_busy = false; } // No JSAPI/allocation in error cleanup.
  FileUrlScope(const FileUrlScope &) = delete;
  FileUrlScope &operator=(const FileUrlScope &) = delete;
};

static bool is_file_url_request(std::string_view value) {
  return value.size() >= 5 && (value[0] == 'f' || value[0] == 'F') &&
         (value[1] == 'i' || value[1] == 'I') && (value[2] == 'l' || value[2] == 'L') &&
         (value[3] == 'e' || value[3] == 'E') && value[4] == ':';
}

static JSObject *get_cjs_file_url_module(JSContext *cx, JS::HandleObject request,
                                        JS::HandleValue specifier) {
  if (JS_IsExceptionPending(cx)) return nullptr;
  if (!fileurl_content_realm(cx, request)) {
    fileurl_error(cx, specifier, "module_file_url", "Cross-realm import is deferred"); return nullptr;
  }
  if (!builtins::node_compat::next_fs::check_deployed(cx, "module.fileURLImport")) return nullptr;
  if (JS::GetModuleRequestType(cx, request) != JS::ModuleType::JavaScript) {
    fileurl_error(cx, specifier, "module_file_url", "Non-JavaScript import attributes are deferred"); return nullptr;
  }
  if (fileurl_busy) {
    fileurl_error(cx, specifier, "module_file_url", "Reentrant file URL import is deferred"); return nullptr;
  }
  FileUrlScope scope;
  if (!fileurl_module_record || !fileurl_url_record || fileurl_create_require.isUndefined() ||
      fileurl_to_path.isUndefined() || fileurl_from_path.isUndefined() || fileurl_url_string.isUndefined()) {
    fileurl_error(cx, specifier, "module_file_url", "Private builtin callbacks were not captured"); return nullptr;
  }
  auto raw = core::encode(cx, specifier);
  if (!raw) return nullptr;
  std::string_view url(raw.ptr.get(), raw.len);
  if (raw.len > MaxFileUrlBytes || std::memchr(raw.ptr.get(), 0, raw.len) ||
      !url.starts_with("file:///") || url.find_first_of("?#") != std::string_view::npos) {
    fileurl_error(cx, specifier, "module_file_url", "Only bounded canonical local file URLs without query/fragment are selected"); return nullptr;
  }
  for (size_t i = 0; i + 2 < url.size(); ++i) {
    if (url[i] == '%' && url[i + 1] == '2' && (url[i + 2] == 'f' || url[i + 2] == 'F')) {
      fileurl_error(cx, specifier, "module_file_url", "Encoded path separator is unsupported"); return nullptr;
    }
    if (url[i] == '%' && url[i + 1] == '5' && (url[i + 2] == 'c' || url[i + 2] == 'C')) {
      fileurl_error(cx, specifier, "module_file_url", "Encoded path separator is unsupported"); return nullptr;
    }
  }
  JS::RootedValue receiver(cx, JS::ObjectValue(*fileurl_url_record)), decoded(cx), normalized(cx);
  if (!fileurl_call(cx, receiver, fileurl_to_path, specifier, &decoded)) return nullptr;
  if (!decoded.isString()) {
    fileurl_error(cx, specifier, "module_file_url", "File URL decoder returned a nonstring"); return nullptr;
  }
  auto path = core::encode(cx, decoded);
  if (!path) return nullptr;
  std::string_view path_view(path.ptr.get(), path.len);
  if (!path.len || path.len > builtins::node_compat::next_fs::MaxPathBytes ||
      path_view.front() != '/' || std::memchr(path.ptr.get(), 0, path.len) || !path_view.ends_with(".cjs")) {
    fileurl_error(cx, specifier, "module_file_url", "Only bounded absolute .cjs files are selected"); return nullptr;
  }
  if (!fileurl_string(cx, decoded, &normalized, specifier)) return nullptr;
  int32_t comparison = 0;
  if (!JS_CompareStrings(cx, specifier.toString(), normalized.toString(), &comparison)) return nullptr;
  if (comparison != 0) {
    fileurl_error(cx, specifier, "module_file_url", "Noncanonical file URL spelling is deferred"); return nullptr;
  }
  builtins::node_compat::next_fs::Metadata st{};
  if (!builtins::node_compat::next_fs::stat_path(cx, path.ptr.get(), path.len, true, &st)) return nullptr;
  if (st.type != 6) {
    fileurl_error(cx, specifier, "module_file_url", "File URL must name a regular file"); return nullptr;
  }
  JS::UniqueChars canonical;
  size_t canonical_length = 0;
  if (!builtins::node_compat::next_fs::realpath(cx, path.ptr.get(), path.len, &canonical, &canonical_length)) return nullptr;
  if (!std::string_view(canonical.get(), canonical_length).ends_with(".cjs")) {
    fileurl_error(cx, specifier, "module_file_url", "Canonical target must retain .cjs extension"); return nullptr;
  }
  JS::RootedString filename(cx, JS_NewStringCopyUTF8N(cx, JS::UTF8Chars(canonical.get(), canonical_length)));
  if (!filename) return nullptr;
  JS::RootedValue canonical_path(cx, JS::StringValue(filename)), canonical_url(cx);
  if (!fileurl_string(cx, canonical_path, &canonical_url, specifier)) return nullptr;
  static constexpr char prefix[] = "\0cjs-file-url:";
  JS::RootedString tag(cx, JS_NewStringCopyN(cx, prefix, sizeof(prefix) - 1));
  if (!tag) return nullptr;
  JS::RootedString key_string(cx, JS_ConcatStrings(cx, tag, canonical_url.toString()));
  if (!key_string) return nullptr;
  JS::RootedValue key(cx, JS::StringValue(key_string)), cached(cx);
  if (!JS::MapGet(cx, moduleRegistry, key, &cached)) return nullptr;
  if (!cached.isUndefined()) {
    if (!cached.isObject()) { fileurl_error(cx, specifier, "module_file_url", "Invalid private module cache value"); return nullptr; }
    return &cached.toObject();
  }
  if (fileurl_namespaces >= MaxFileUrlNamespaces) {
    fileurl_error(cx, specifier, "module_file_url", "File URL namespace limit reached"); return nullptr;
  }
  receiver.setObject(*fileurl_module_record);
  JS::RootedValue require_value(cx), resolve_value(cx), resolved(cx), existing(cx), exports(cx), cached_exports(cx);
  if (!fileurl_call(cx, receiver, fileurl_create_require, canonical_path, &require_value)) return nullptr;
  if (!require_value.isObject() || js::IsProxy(&require_value.toObject()) ||
      !JS::IsCallable(&require_value.toObject()) || !fileurl_content_realm(cx, &require_value.toObject())) {
    fileurl_error(cx, specifier, "module_file_url", "createRequire returned an unsupported value"); return nullptr;
  }
  JS::RootedObject require(cx, &require_value.toObject());
  if (!fileurl_own_callback(cx, require, "resolve", &resolve_value, specifier) ||
      !fileurl_call(cx, JS::UndefinedHandleValue, resolve_value, canonical_path, &resolved)) return nullptr;
  if (!resolved.isString()) { fileurl_error(cx, specifier, "module_file_url", "Resolver returned a nonstring"); return nullptr; }
  if (!JS_CompareStrings(cx, filename, resolved.toString(), &comparison)) return nullptr;
  if (comparison != 0) { fileurl_error(cx, specifier, "module_file_url", "Resolver retargeted the canonical file"); return nullptr; }
  bool found = false;
  if (!fileurl_cache_entry(cx, require, filename, &found, &existing, specifier)) return nullptr;
  if (!fileurl_call(cx, JS::UndefinedHandleValue, require_value, canonical_path, &exports)) return nullptr;
  if (!fileurl_cache_entry(cx, require, filename, &found, &cached_exports, specifier)) return nullptr;
  bool same = false;
  if (!found) { fileurl_error(cx, specifier, "module_file_url", "Require did not retain a completed cache record"); return nullptr; }
  if (!JS::SameValue(cx, exports, cached_exports, &same)) return nullptr;
  if (!same) { fileurl_error(cx, specifier, "module_file_url", "Require result does not match its successful cache record"); return nullptr; }
  if (exports.isObject() && !fileurl_content_realm(cx, &exports.toObject())) {
    fileurl_error(cx, specifier, "module_file_url", "Cross-realm CommonJS export is deferred"); return nullptr;
  }
  JS::RootedObject module(cx, JS::CreateDefaultExportSyntheticModule(cx, exports.get()));
  if (!module) return nullptr;
  JS::RootedValue module_value(cx, JS::ObjectValue(*module));
  if (!JS::MapSet(cx, moduleRegistry, key, module_value)) return nullptr;
  ++fileurl_namespaces;
  return module;
}
#endif

class AutoCloseFile {
  FILE *file;

public:
  explicit AutoCloseFile(FILE *f) : file(f) {}
  ~AutoCloseFile() { release(); }

  AutoCloseFile(const AutoCloseFile &) = default;
  AutoCloseFile(AutoCloseFile &&) = delete;

  AutoCloseFile &operator=(const AutoCloseFile &) = default;
  AutoCloseFile &operator=(AutoCloseFile &&) = delete;

  bool release() {
    bool success = true;
    if (file && file != stdin && file != stdout && file != stderr) {
      success = (fclose(file) == 0);
    }
    file = nullptr;
    // Clang analyzer complains about the stream leaking when stream is stdin, stdout, or stderr.
    // NOLINTNEXTLINE(clang-analyzer-unix.Stream)
    return success;
  }
};

// strip off the given prefix when possible for nicer debugging stacks
static std::string strip_prefix(std::string_view resolved_path,
                                mozilla::Maybe<std::string> path_prefix) {
  if (!path_prefix) {
    return std::string(resolved_path);
  }

  const auto &base = *path_prefix;
  if (!resolved_path.starts_with(base)) {
    return std::string(resolved_path);
  }

  return std::string(resolved_path.substr(base.size()));
}

struct stat s;

static std::string resolve_extension(std::string resolved_path) {
  if (stat(resolved_path.c_str(), &s) == 0) {
    return resolved_path;
  }

  if (resolved_path.ends_with(".js")) {
    return resolved_path;
  }

  std::string with_ext = resolved_path + ".js";
  if (stat(with_ext.c_str(), &s) == 0) {
    return with_ext;
  }
  return resolved_path;
}

static std::string resolve_path(std::string_view path, std::string_view base) {
  size_t base_len = base.size();
  while (base_len > 0 && base[base_len - 1] != '/') {
    base_len--;
  }
  size_t path_len = path.size();

  // create the maximum buffer size as a working buffer
  std::string resolved_path;
  resolved_path.reserve(base_len + path_len + 1);

  // copy the base in if used
  size_t resolved_len = base_len;
  if (!path.empty() && path[0] == '/') {
    resolved_len = 0;
  } else {
    resolved_path.assign(base.substr(0, base_len));
  }

  // Iterate through each segment of the path, copying each segment into the resolved path,
  // while handling backtracking for .. segments and skipping . segments appropriately.
  size_t path_from_idx = 0;
  size_t path_cur_idx = 0;
  while (path_cur_idx < path_len) {
    // read until the end or the next / to get the segment position
    // as the substring between path_from_idx and path_cur_idx
    while (path_cur_idx < path_len && path[path_cur_idx] != '/') {
      path_cur_idx++;
    }
    if (path_cur_idx == path_from_idx) {
      break;
    }
    // . segment to skip
    if (path_cur_idx - path_from_idx == 1 && path[path_from_idx] == '.') {
      path_cur_idx++;
      path_from_idx = path_cur_idx;
      continue;
    }
    // .. segment backtracking
    if (path_cur_idx - path_from_idx == 2 && path[path_from_idx] == '.' && path[path_from_idx + 1] == '.') {
      path_cur_idx++;
      path_from_idx = path_cur_idx;
      if (resolved_len > 0 && resolved_path[resolved_len - 1] == '/') {
        resolved_len--;
      }
      while (resolved_len > 0 && resolved_path[resolved_len - 1] != '/') {
        resolved_len--;
      }
      // Resize string to match resolved_len
      resolved_path.resize(resolved_len);
      continue;
    }
    // normal segment to copy (with the trailing / if not the last segment)
    if (path_cur_idx < path_len && path[path_cur_idx] == '/') {
      path_cur_idx++;
    }

    // Copy segment equivalent to: strncpy(resolved_path + resolved_len, path + path_from_idx, path_cur_idx - path_from_idx);
    resolved_path.append(path.substr(path_from_idx, path_cur_idx - path_from_idx));
    resolved_len += path_cur_idx - path_from_idx;
    path_from_idx = path_cur_idx;
  }

  return resolve_extension(std::move(resolved_path));
}

static JSObject *get_module(JSContext *cx, JS::SourceText<mozilla::Utf8Unit> &source,
                            std::string_view resolved_path, const JS::CompileOptions &opts) {
  RootedObject module(cx, JS::CompileModule(cx, opts, source));
  if (!module) {
    return nullptr;
  }
  RootedValue module_val(cx, ObjectValue(*module));

  RootedObject info(cx, JS_NewPlainObject(cx));
  if (!info) {
    return nullptr;
  }

  RootedString resolved_path_str(cx, JS_NewStringCopyN(cx, resolved_path.data(), resolved_path.size()));
  if (!resolved_path_str) {
    return nullptr;
  }

  RootedValue resolved_path_val(cx, StringValue(resolved_path_str));
  if (!JS_DefineProperty(cx, info, "id", resolved_path_val, JSPROP_ENUMERATE)) {
    return nullptr;
  }

  SetModulePrivate(module, ObjectValue(*info));

  if (!MapSet(cx, moduleRegistry, resolved_path_val, module_val)) {
    return nullptr;
  }

  return module;
}

static JSObject *get_module(JSContext *cx, std::string_view specifier,
                            std::string_view resolved_path, const JS::CompileOptions &opts) {
  RootedString resolved_path_str(cx, JS_NewStringCopyN(cx, resolved_path.data(), resolved_path.size()));
  if (!resolved_path_str) {
    return nullptr;
  }

  RootedValue resolved_path_val(cx, StringValue(resolved_path_str));
  RootedValue module_val(cx);
  if (!JS::MapGet(cx, moduleRegistry, resolved_path_val, &module_val)) {
    return nullptr;
  }

  if (!module_val.isUndefined()) {
    return &module_val.toObject();
  }

  JS::SourceText<mozilla::Utf8Unit> source;
  if (!SCRIPT_LOADER->load_resolved_script(cx, specifier, resolved_path, source)) {
    return nullptr;
  }

  return get_module(cx, source, resolved_path, opts);
}

static JSObject *get_builtin_module(JSContext *cx, HandleValue id, HandleObject builtin) {
  RootedValue module_val(cx);
  MOZ_ASSERT(id.isString());
  if (!JS::MapGet(cx, moduleRegistry, id, &module_val)) {
    return nullptr;
  }
  if (!module_val.isUndefined()) {
    return &module_val.toObject();
  }

  JS::CompileOptions opts(cx, *COMPILE_OPTS);
  opts.setFile("<internal>");
  JS::SourceText<mozilla::Utf8Unit> source;

  std::string code = "const { ";
  JS::RootedIdVector props(cx);
  GetPropertyKeys(cx, builtin, JSITER_OWNONLY, &props);

  size_t length = props.length();
  bool firstValue = true;
  for (size_t i = 0; i < length; ++i) {
    if (firstValue) {
      firstValue = false;
    } else {
      code += ", ";
    }

    code += "'";
    const auto &prop = props[i];
    JS::RootedValue key(cx, js::IdToValue(prop));
    if (!key.isString()) {
      return nullptr;
    }
    auto key_str = core::encode(cx, key);
    code += std::string_view(key_str.ptr.get(), key_str.len);
    code += "': ";

    code += "e";
    code += std::to_string(i);
  }

  code += " } = import.meta.builtin;\nexport { ";

  firstValue = true;
  for (size_t i = 0; i < length; ++i) {
    if (firstValue) {
      firstValue = false;
    } else {
      code += ", ";
    }

    code += "e";
    code += std::to_string(i);

    code += " as '";
    const auto &prop = props[i];
    JS::RootedValue key(cx, js::IdToValue(prop));
    if (!key.isString()) {
      return nullptr;
    }
    auto key_str = core::encode(cx, key);
    code += std::string_view(key_str.ptr.get(), key_str.len);
    code += "'";
  }
  code += " }\n";

  if (!source.init(cx, code.c_str(), strlen(code.c_str()), JS::SourceOwnership::Borrowed)) {
    return nullptr;
  }

  RootedObject module(cx, JS::CompileModule(cx, opts, source));
  if (!module) {
    return nullptr;
  }
  module_val.setObject(*module);

  RootedObject info(cx, JS_NewPlainObject(cx));
  if (!info) {
    return nullptr;
  }

  if (!JS_DefineProperty(cx, info, "id", id, JSPROP_ENUMERATE)) {
    return nullptr;
  }

  SetModulePrivate(module, ObjectValue(*info));

  // This generated wrapper has no requested modules: import.meta is metadata,
  // not an import declaration. Complete its empty graph before publishing it.
  // ContinueDynamicImport expects this phase to have finished before linking;
  // returning a freshly compiled module leaves it in SpiderMonkey's New state.
  // The zero-dependency LoadRequestedModules callback completes synchronously.
  if (!JS::LoadRequestedModules(
          cx, module, JS::UndefinedHandleValue,
          [](JSContext *, JS::Handle<JS::Value>) { return true; },
          [](JSContext *cx, JS::Handle<JS::Value>, JS::Handle<JS::Value> error) {
            JS_SetPendingException(cx, error);
            return true;
          }) ||
      JS_IsExceptionPending(cx)) {
    return nullptr;
  }

  if (!MapSet(cx, moduleRegistry, id, module_val)) {
    return nullptr;
  }

  return module;
}

bool module_load_hook(JSContext *cx, JS::HandleScript referrer, JS::HandleObject module_reques,
                      JS::HandleValue hostDefined, JS::HandleValue payload, uint32_t lineNumber,
                      JS::ColumnNumberOneOrigin columnNumber) {
#ifdef NODE_COMPAT_VM_DATA
  JS::Realm* data_realm = JS::GetCurrentRealmOrNull(cx);
  if (!core::async_context::is_data_realm(data_realm))
    data_realm = JS::GetObjectRealmOrNull(module_reques);
  if (!core::async_context::is_data_realm(data_realm) && referrer) {
    JS::RootedValue marker(cx, JS::GetScriptPrivate(referrer));
    if (marker.isObject()) data_realm = JS::GetObjectRealmOrNull(&marker.toObject());
  }
  if (core::async_context::is_data_realm(data_realm)) {
    core::async_context::note_data_realm_async(data_realm);
    return core::InternalTickQueue::fail(cx, JSEXN_TYPEERR,
        "ERR_SM_NODE_VM_ASYNC", "Dynamic import from node:vm data realm is deferred");
  }
#endif
  RootedString specifier(cx, GetModuleRequestSpecifier(cx, module_reques));
  if (!specifier) {
    return false;
  }

  RootedValue path_val(cx, StringValue(specifier));
  auto path = JS_EncodeStringToUTF8(cx, specifier);
  if (!path) {
    return false;
  }

  RootedValue builtin_val(cx);
  if (!MapGet(cx, builtinModules, path_val, &builtin_val)) {
    return false;
  }
  if (!builtin_val.isUndefined()) {
    RootedValue specifier_val(cx, StringValue(specifier));
    RootedObject builtin_obj(cx, &builtin_val.toObject());
    // Share one module-record cache key only for explicitly registered aliases
    // whose builtin values are the exact same object. Other builtin IDs retain
    // their original module records and import.meta lookup keys.
    if (!std::string_view(path.get()).starts_with("node:")) {
      RootedString node_prefix(cx, JS_NewStringCopyZ(cx, "node:"));
      if (!node_prefix) {
        return false;
      }
      // Concatenate JS strings so Unicode and embedded NULs are not truncated.
      RootedString canonical_specifier(cx, JS_ConcatStrings(cx, node_prefix, specifier));
      if (!canonical_specifier) {
        return false;
      }
      RootedValue canonical_id(cx, StringValue(canonical_specifier));
      RootedValue canonical_builtin(cx);
      if (!JS::MapGet(cx, builtinModules, canonical_id, &canonical_builtin)) {
        return false;
      }
      if (canonical_builtin.isObject() && &canonical_builtin.toObject() == builtin_obj.get()) {
        // This outer root remains live across module compilation/allocation.
        specifier_val.set(canonical_id);
      }
    }
    RootedObject result(cx, get_builtin_module(cx, specifier_val, builtin_obj));
    if (!result) {
      return false;
    }
    return FinishLoadingImportedModule(cx, referrer, module_reques, payload, result, false);
  }

#ifdef NODE_COMPAT_MODULE
  if (is_file_url_request(std::string_view(path.get()))) {
    RootedObject result(cx, get_cjs_file_url_module(cx, module_reques, path_val));
    if (!result) return false;
    return FinishLoadingImportedModule(cx, referrer, module_reques, payload, result, false);
  }
#endif

  RootedValue ref_priv(cx);
  if (referrer) {
    ref_priv = JS::GetScriptPrivate(referrer);
  }

  if (!ref_priv.isObject()) {
    return unsupported_import_referrer(cx, path_val, "module_load_hook");
  }

  RootedObject info(cx, &ref_priv.toObject());
  RootedValue parent_path_val(cx);
  if (!JS_GetProperty(cx, info, "id", &parent_path_val)) {
    return false;
  }
  if (!parent_path_val.isString()) {
    return unsupported_import_referrer(cx, path_val, "module_load_hook");
  }

  HostString str = core::encode(cx, parent_path_val);
  auto resolved_path = resolve_path(path.get(), str.ptr.get());

  JS::CompileOptions opts(cx, *COMPILE_OPTS);
  auto stripped = strip_prefix(resolved_path, PATH_PREFIX);
  opts.setFileAndLine(stripped.c_str(), 1);
  RootedObject result(cx, get_module(cx, path.get(), resolved_path, opts));
  if (!result) {
    return false;
  }
  return FinishLoadingImportedModule(cx, referrer, module_reques, payload, result, false);
}

bool module_metadata_hook(JSContext *cx, HandleValue ref_priv, HandleObject meta_obj) {
  if (!ref_priv.isObject()) {
    return unsupported_import_referrer(cx, JS::UndefinedHandleValue, "module_metadata_hook");
  }
  RootedObject info(cx, &ref_priv.toObject());
  RootedValue parent_id_val(cx);
  if (!JS_GetProperty(cx, info, "id", &parent_id_val)) {
    return false;
  }
  if (!parent_id_val.isString()) {
    return unsupported_import_referrer(cx, JS::UndefinedHandleValue, "module_metadata_hook");
  }
  RootedValue builtin_val(cx);
  if (!MapGet(cx, builtinModules, parent_id_val, &builtin_val)) {
    return false;
  }
  if (builtin_val.isUndefined()) {
    return false;
  }
  JS_SetProperty(cx, meta_obj, "builtin", builtin_val);
  return true;
}

ScriptLoader::ScriptLoader(api::Engine *engine, JS::CompileOptions *opts,
                           mozilla::Maybe<std::string> path_prefix) {
  MOZ_ASSERT(!SCRIPT_LOADER);
  ENGINE = engine;
  SCRIPT_LOADER = this;
  COMPILE_OPTS = opts;
  PATH_PREFIX = std::move(path_prefix);
  JSContext *cx = engine->cx();
  moduleRegistry.init(cx, JS::NewMapObject(cx));
  builtinModules.init(cx, JS::NewMapObject(cx));
#ifdef NODE_COMPAT_MODULE
  fileurl_module_record.init(cx);
  fileurl_url_record.init(cx);
  fileurl_create_require.init(cx);
  fileurl_to_path.init(cx);
  fileurl_from_path.init(cx);
  fileurl_url_string.init(cx);
  fileurl_namespaces = 0;
  fileurl_busy = false;
#endif
  MOZ_RELEASE_ASSERT(moduleRegistry);
  MOZ_RELEASE_ASSERT(builtinModules);
  JSRuntime *rt = JS_GetRuntime(cx);
  SetModuleLoadHook(rt, module_load_hook);
  SetModuleMetadataHook(rt, module_metadata_hook);
}

#ifdef NODE_COMPAT_MODULE
bool ScriptLoader::lookup_registered_builtin(JSContext *cx, JS::HandleString id,
                                              JS::MutableHandleValue result) {
  JS::RootedValue key(cx, JS::StringValue(id));
  return JS::MapGet(cx, builtinModules, key, result);
}
#endif

bool ScriptLoader::define_builtin_module(const char *id, HandleValue builtin) {
  JSContext *cx = ENGINE->cx();
  RootedString id_str(cx, JS_NewStringCopyZ(cx, id));
  if (!id_str) {
    return false;
  }
  RootedValue module_val(cx);
  RootedValue id_val(cx, StringValue(id_str));
  bool already_exists = false;
  if (!MapHas(cx, builtinModules, id_val, &already_exists)) {
    return false;
  }
  if (already_exists) {
    return api::throw_error(cx, ScriptLoaderErrors::BuiltinModuleExists, "id");
  }
  if (!MapSet(cx, builtinModules, id_val, builtin)) {
    return false;
  }
#ifdef NODE_COMPAT_MODULE
  if (!fileurl_capture_builtin(cx, id, builtin)) return false;
#endif
  return true;
}

void ScriptLoader::enable_module_mode(bool enable) { MODULE_MODE = enable; }

bool ScriptLoader::load_resolved_script(JSContext *cx, std::string_view specifier_sv,
                                        std::string_view resolved_path_sv,
                                        JS::SourceText<mozilla::Utf8Unit> &script) {
  std::string specifier_str(specifier_sv);
  std::string resolved_path_str(resolved_path_sv);

  const auto *specifier = specifier_str.c_str();
  const auto *resolved_path = resolved_path_str.c_str();

  FILE *file = fopen(resolved_path, "r");
  if (!file) {
    return api::throw_error(cx, ScriptLoaderErrors::ModuleLoadingError, specifier, resolved_path,
                            std::strerror(errno));
  }

  AutoCloseFile autoclose(file);
  if (fseek(file, 0, SEEK_END) != 0) {
    return api::throw_error(cx, ScriptLoaderErrors::ModuleLoadingError, specifier, resolved_path,
                            "can't read from file");
  }
  size_t len = ftell(file);
  if (fseek(file, 0, SEEK_SET) != 0) {
    return api::throw_error(cx, ScriptLoaderErrors::ModuleLoadingError, specifier, resolved_path,
                            "can't read from file");
  }

  UniqueChars buf(js_pod_malloc<char>(len + 1));
  if (!buf) {
    return api::throw_error(cx, ScriptLoaderErrors::ModuleLoadingError, specifier, resolved_path,
                            "out of memory while reading file");
  }
  size_t cc = fread(buf.get(), sizeof(char), len, file);
  if (cc != len) {
    return api::throw_error(cx, ScriptLoaderErrors::ModuleLoadingError, specifier, resolved_path,
                            "error reading file");
  }

  return script.init(cx, std::move(buf), len);
}

bool ScriptLoader::load_script(JSContext *cx, std::string_view path,
                               JS::SourceText<mozilla::Utf8Unit> &script) {

  std::string resolved;
  if (BASE_PATH.empty()) {
    auto pos = path.find_last_of('/');
    if (pos != std::string::npos) {
      BASE_PATH = path.substr(0, pos + 1);
    } else {
      BASE_PATH = "./";
    }
    resolved = path;
  } else {
    resolved = resolve_path(path, BASE_PATH);
  }
  return load_resolved_script(cx, path, resolved, script);
}

bool ScriptLoader::eval_top_level_script(std::string_view path,
                                         JS::SourceText<mozilla::Utf8Unit> &source,
                                         MutableHandleValue result,
                                         MutableHandleValue tla_promise) {
  JSContext *cx = ENGINE->cx();

  JS::CompileOptions opts(cx, *COMPILE_OPTS);
  auto stripped = strip_prefix(path, PATH_PREFIX);
  opts.setFileAndLine(stripped.c_str(), 1);

  JS::RootedScript script(cx);
  RootedObject module(cx);
  if (MODULE_MODE) {
    // Disabling GGC during compilation seems to slightly reduce the number of
    // pages touched post-deploy.
    // (Whereas disabling it during execution below meaningfully increases it,
    // which is why this is scoped to just compilation.)
    JS::AutoDisableGenerationalGC noGGC(cx);
    module = get_module(cx, source, path, opts);
    if (!module) {
      return false;
    }
    RootedValue hostDefined(cx, ObjectValue(*module));
    if (!LoadRequestedModules(
            cx, module, hostDefined,
            [](JSContext *cx, JS::Handle<JS::Value> hd) {
              JS::RootedObject mod(cx, &hd.toObject());
              return JS::ModuleLink(cx, mod);
            },
            [](JSContext *cx, JS::Handle<JS::Value>, JS::Handle<JS::Value> error) {
              JS_SetPendingException(cx, error);
              return true;
            })) {
      return false;
    }
    if (JS_IsExceptionPending(cx)) {
      return false;
    }
  } else {
    // See comment above about disabling GGC during compilation.
    JS::AutoDisableGenerationalGC noGGC(cx);
    script = JS::Compile(cx, opts, source);
    if (!script) {
      return false;
    }
  }

  // TODO(performance): verify that it's better to perform a shrinking GC here,
  // as manual testing indicates. Running a shrinking GC here causes *fewer* 4kb
  // pages to be written to when processing a request, at least for one fairly
  // large input script.
  //
  // A hypothesis for why this is the case could be that the objects allocated
  // by parsing the script (but not evaluating it) tend to be read-only, so
  // optimizing them for compactness makes sense and doesn't fragment writes
  // later on.
  // https://github.com/fastly/js-compute-runtime/issues/222
  if (ENGINE->state() == api::EngineState::ScriptPreInitializing) {
    JS::PrepareForFullGC(cx);
    JS::NonIncrementalGC(cx, JS::GCOptions::Shrink, JS::GCReason::API);
  }

  // Execute the top-level module script.
  if (!MODULE_MODE) {
    return JS_ExecuteScript(cx, script, result);
  }

  if (!ModuleEvaluate(cx, module, tla_promise)) {
    return false;
  }

  JS::RootedObject ns(cx, JS::GetModuleNamespace(cx, module));
  result.setObject(*ns);
  return true;
}
