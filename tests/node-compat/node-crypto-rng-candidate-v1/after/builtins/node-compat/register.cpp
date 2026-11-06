// Opt-in registration for the bounded Node v22.14.0 profile.
#include "builtin.h"
#include "js/CallAndConstruct.h"
#include "js/CompilationAndEvaluation.h"
#include "js/SourceText.h"
#include "factories.generated.h"
#ifdef NODE_COMPAT_CRYPTO_RANDOM
#include "event_loop.h"
#endif
#ifdef NODE_COMPAT_TIMERS
#include "node-timers-factory.generated.h"
#include "../web/timers.h"
#endif
#ifdef NODE_COMPAT_FS
#include "fs-factories.generated.h"
#include "next-fs-native.h"
#endif
#ifdef NODE_COMPAT_NEXT_STARTUP
#include "next-startup-factory.generated.h"
#include "script_loader.h"
#include "event_loop.h"
#endif
#ifdef NODE_COMPAT_MODULE
#include "module-factory.generated.h"
#endif
#ifdef NODE_COMPAT_CRYPTO_HASH_HMAC
#include "crypto-factory.generated.h"
#include "../web/crypto/crypto.h"
#include "../web/crypto/subtle-crypto.h"
#endif
#ifdef NODE_COMPAT_ZLIB
#include "zlib/factories.generated.h"
#endif
#ifdef NODE_COMPAT_STREAM_CONSUMERS
#include "stream-consumers/factories.generated.h"
#endif
#ifdef NODE_COMPAT_CLASSIC_STREAMS
#include "classic-streams/factories.generated.h"
#include "event_loop.h"
#endif
#ifdef NODE_COMPAT_PATH
#include "path-factories.generated.h"
#endif
#ifdef NODE_COMPAT_EVENTS
#include "events-factories.generated.h"
#include "../web/event/event-target.h"
#include "js/Symbol.h"
#endif
#ifdef NODE_COMPAT_STRING_DECODER
#include "string-decoder-factories.generated.h"
#endif
#ifdef NODE_COMPAT_ASSERT
#include "assert-factories.generated.h"
#endif
#ifdef NODE_COMPAT_QUERYSTRING
#include "querystring-factories.generated.h"
#endif
#ifdef NODE_COMPAT_UTIL
#include "util-factories.generated.h"
#endif
#ifdef NODE_COMPAT_STREAM_WEB
#include "stream-web-factories.generated.h"
#endif

#ifdef NODE_COMPAT_ASYNC_LOCAL_STORAGE
#include "async-hooks-factory.generated.h"
#include "async_context_runtime.h"
#endif
namespace builtins::node_compat {
JSObject *create_kernel(JSContext *cx);
#ifdef NODE_COMPAT_NEXT_STARTUP
JSObject *create_next_startup_kernel(JSContext *cx);
#endif
#ifdef NODE_COMPAT_MODULE
JSObject *create_module_kernel(JSContext *cx);
#endif
#ifdef NODE_COMPAT_CRYPTO_HASH_HMAC
JSObject *create_crypto_hash_hmac_kernel(JSContext *cx);
#ifdef NODE_COMPAT_CRYPTO_RANDOM
JSObject *create_crypto_random_kernel(JSContext *cx);
#endif
#endif
#ifdef NODE_COMPAT_ZLIB
namespace zlib_profile { JSObject *create_kernel(JSContext *cx); }
#endif
#ifdef NODE_COMPAT_STREAM_WEB
JSObject *create_stream_web_kernel(JSContext *cx);
#endif

static bool evaluate_factory(JSContext *cx, const char *source_text,
                             JS::HandleValue argument, JS::MutableHandleValue result) {
  JS::CompileOptions options(cx);
  options.setFileAndLine("<node-profile-factory>", 1);
  // Canonical facades are ESM. Their generated script form must retain strict
  // receiver semantics, particularly ordinary calls to StringDecoder().
  options.setForceStrictMode();
  JS::SourceText<mozilla::Utf8Unit> source;
  if (!source.init(cx, source_text, strlen(source_text), JS::SourceOwnership::Borrowed)) return false;
  JS::RootedValue factory(cx);
  if (!JS::Evaluate(cx, options, source, &factory)) return false;
  JS::RootedValueArray<1> arguments(cx);
  arguments[0].set(argument);
  return JS::Call(cx, JS::UndefinedHandleValue, factory, arguments, result);
}

#ifdef NODE_COMPAT_MODULE
static bool install_module(api::Engine *engine) {
  auto *cx=engine->cx();
  JS::RootedObject kernel(cx,create_module_kernel(cx));if(!kernel)return false;
  JS::RootedValue value(cx,JS::ObjectValue(*kernel)),record(cx);
  if(!evaluate_factory(cx,kModuleFactorySource,value,&record))return false;
  return engine->define_builtin_module("node:module",record) &&
         engine->define_builtin_module("module",record);
}
#endif

#ifdef NODE_COMPAT_CRYPTO_HASH_HMAC
static bool install_crypto_hash_hmac(api::Engine *engine, JS::HandleValue buffer_constructor) {
  auto *cx = engine->cx();
  JS::RootedObject kernel(cx, create_crypto_hash_hmac_kernel(cx));
  JS::RootedObject argument(cx, JS_NewPlainObject(cx));
  if (!kernel || !argument) return false;
  JS::RootedValue kernel_value(cx, JS::ObjectValue(*kernel));
  JS::RootedValue webcrypto(cx), subtle(cx);
  // install_builtins follows CMake declaration order: native WebCrypto was
  // installed before Node compatibility, and application code has not run.
  if (!JS_GetProperty(cx, engine->global(), "crypto", &webcrypto)) return false;
  if (!webcrypto.isObject()) {
    JS_ReportErrorASCII(cx, "ERR_SM_NODE_PROFILE_INITIALIZATION: native Crypto is unavailable");
    return false;
  }
  JS::RootedObject webcrypto_object(cx, &webcrypto.toObject());
  if (JS::GetClass(webcrypto_object) != &builtins::web::crypto::Crypto::class_) {
    JS_ReportErrorASCII(cx, "ERR_SM_NODE_PROFILE_INITIALIZATION: wrong native Crypto class");
    return false;
  }
  if (!JS_GetProperty(cx, webcrypto_object, "subtle", &subtle)) return false;
  if (!subtle.isObject() || JS::GetClass(&subtle.toObject()) != &builtins::web::crypto::SubtleCrypto::class_) {
    JS_ReportErrorASCII(cx, "ERR_SM_NODE_PROFILE_INITIALIZATION: native SubtleCrypto is unavailable");
    return false;
  }
  if (!JS_DefineProperty(cx, argument, "kernel", kernel_value, 0) ||
      !JS_DefineProperty(cx, argument, "Buffer", buffer_constructor, 0) ||
      !JS_DefineProperty(cx, argument, "webcrypto", webcrypto, 0) ||
      !JS_DefineProperty(cx, argument, "subtle", subtle, 0)) return false;
#ifdef NODE_COMPAT_CRYPTO_RANDOM
  JS::RootedObject random_kernel(cx,create_crypto_random_kernel(cx));
  JS::RootedObject random_tick(cx,core::EventLoop::create_internal_next_tick(cx));
  if(!random_kernel||!random_tick)return false;
  JS::RootedValue random_value(cx,JS::ObjectValue(*random_kernel)),random_tick_value(cx,JS::ObjectValue(*random_tick));
  if(!JS_DefineProperty(cx,argument,"rng",random_value,0)||!JS_DefineProperty(cx,argument,"nextTick",random_tick_value,0))return false;
#endif
  JS::RootedValue value(cx, JS::ObjectValue(*argument)), module(cx);
  if (!evaluate_factory(cx, kCryptoHashHmacFactorySource, value, &module)) return false;
  return engine->define_builtin_module("node:crypto", module) &&
         engine->define_builtin_module("crypto", module);
}
#endif

#ifdef NODE_COMPAT_ASYNC_LOCAL_STORAGE
static bool install_async_local_storage(api::Engine* engine) {
  auto* cx = engine->cx();
  JS::RootedObject kernel(cx, core::async_context::create_kernel(cx));
  if (!kernel) return false;
  JS::RootedValue argument(cx, JS::ObjectValue(*kernel)), module(cx);
  if (!evaluate_factory(cx, kAsyncLocalStorageFactorySource, argument, &module)) return false;
  return engine->define_builtin_module("node:async_hooks", module) &&
         engine->define_builtin_module("async_hooks", module);
}
#endif
#ifdef NODE_COMPAT_PATH
static bool install_path(api::Engine *engine) {
  auto *cx = engine->cx();
  JS::RootedValue graph(cx);
  if (!evaluate_factory(cx, kPathFactorySource, JS::UndefinedHandleValue, &graph)) return false;
  JS::RootedObject object(cx, &graph.toObject());
  JS::RootedValue root(cx), posix(cx), win32(cx);
  if (!JS_GetProperty(cx, object, "root", &root) ||
      !JS_GetProperty(cx, object, "posix", &posix) ||
      !JS_GetProperty(cx, object, "win32", &win32)) return false;
  return engine->define_builtin_module("node:path", root) &&
         engine->define_builtin_module("path", root) &&
         engine->define_builtin_module("node:path/posix", posix) &&
         engine->define_builtin_module("path/posix", posix) &&
         engine->define_builtin_module("node:path/win32", win32) &&
         engine->define_builtin_module("path/win32", win32);
}
#endif

#ifdef NODE_COMPAT_EVENTS
static bool install_events(api::Engine *engine, JS::MutableHandleValue installed_module) {
  auto *cx = engine->cx();
  JS::RootedSymbol key(cx, builtins::web::event::EventTarget::node_abort_resist_key());
  if (!key) {
    JS_ReportErrorASCII(cx, "ERR_SM_NODE_PROFILE_INITIALIZATION: protected EventTarget key unavailable");
    return false;
  }
  JS::RootedValue argument(cx, JS::SymbolValue(key));
  JS::RootedValue module(cx);
  if (!evaluate_factory(cx, kEventsFactorySource, argument, &module)) return false;
  installed_module.set(module);
  return engine->define_builtin_module("node:events", module) &&
         engine->define_builtin_module("events", module);
}
#endif

#ifdef NODE_COMPAT_STRING_DECODER
static bool install_string_decoder(api::Engine *engine, JS::HandleValue buffer_constructor,
                                   JS::MutableHandleValue installed_module) {
  JS::RootedValue module(engine->cx());
  if (!evaluate_factory(engine->cx(), kStringDecoderFactorySource, buffer_constructor, &module)) return false;
  installed_module.set(module);
  return engine->define_builtin_module("node:string_decoder", module) &&
         engine->define_builtin_module("string_decoder", module);
}
#endif

#ifdef NODE_COMPAT_ASSERT
static bool install_assert(api::Engine *engine) {
  auto *cx = engine->cx();
  JS::RootedValue graph(cx);
  if (!evaluate_factory(cx, kAssertFactorySource, JS::UndefinedHandleValue, &graph)) return false;
  JS::RootedObject object(cx, &graph.toObject());
  JS::RootedValue root(cx), strict(cx);
  if (!JS_GetProperty(cx, object, "root", &root) ||
      !JS_GetProperty(cx, object, "strict", &strict)) return false;
  return engine->define_builtin_module("node:assert", root) &&
         engine->define_builtin_module("assert", root) &&
         engine->define_builtin_module("node:assert/strict", strict) &&
         engine->define_builtin_module("assert/strict", strict);
}
#endif

#ifdef NODE_COMPAT_QUERYSTRING
static bool install_querystring(api::Engine *engine, JS::HandleValue buffer_constructor) {
  JS::RootedValue module(engine->cx());
  if (!evaluate_factory(engine->cx(), kQuerystringFactorySource, buffer_constructor, &module)) return false;
  return engine->define_builtin_module("node:querystring", module) &&
         engine->define_builtin_module("querystring", module);
}
#endif

#ifdef NODE_COMPAT_UTIL
static bool install_util(api::Engine *engine) {
  auto *cx = engine->cx();
  JS::RootedValue graph(cx);
  if (!evaluate_factory(cx, kUtilFactorySource, JS::UndefinedHandleValue, &graph)) return false;
  JS::RootedObject object(cx, &graph.toObject());
  JS::RootedValue root(cx), types(cx);
  if (!JS_GetProperty(cx, object, "root", &root) ||
      !JS_GetProperty(cx, object, "types", &types)) return false;
  return engine->define_builtin_module("node:util", root) &&
         engine->define_builtin_module("util", root) &&
         engine->define_builtin_module("node:sys", root) &&
         engine->define_builtin_module("sys", root) &&
         engine->define_builtin_module("node:util/types", types) &&
         engine->define_builtin_module("util/types", types);
}
#endif

#ifdef NODE_COMPAT_STREAM_WEB
static bool install_stream_web(api::Engine *engine) {
  auto *cx = engine->cx();
  // install() already entered the content realm; existing web prerequisites
  // precede this builtin in declaration/install order. Capture no live streams.
  JS::RootedObject kernel(cx, create_stream_web_kernel(cx));
  if (!kernel) return false;
  JS::RootedValue argument(cx, JS::ObjectValue(*kernel));
  JS::RootedValue module(cx);
  if (!evaluate_factory(cx, kStreamWebFactorySource, argument, &module)) return false;
  return engine->define_builtin_module("node:stream/web", module) &&
         engine->define_builtin_module("stream/web", module);
}
#endif

#ifdef NODE_COMPAT_CLASSIC_STREAMS
static bool install_classic_streams(api::Engine *engine, JS::HandleValue buffer_constructor,
                                    JS::HandleValue events_module, JS::HandleValue decoder_module,
                                    JS::MutableHandleValue installed_module) {
  auto *cx = engine->cx();
  // CONTENT realm is already entered by install(). Native prerequisite globals
  // and the retained factory records precede this call; no module-loader getter.
  JS::RootedObject argument(cx, JS_NewPlainObject(cx));
  if (!argument) return false;
  JS::RootedObject next_tick(cx, core::EventLoop::create_internal_next_tick(cx));
  if (!next_tick) return false;
  JS::RootedValue tick_value(cx, JS::ObjectValue(*next_tick));
  if (!JS_DefineProperty(cx, argument, "Buffer", buffer_constructor, 0) ||
      !JS_DefineProperty(cx, argument, "events", events_module, 0) ||
      !JS_DefineProperty(cx, argument, "nextTick", tick_value, 0)) return false;
  JS::RootedObject decoder(cx, &decoder_module.toObject());
  JS::RootedValue value(cx);
  if (!JS_GetProperty(cx, decoder, "StringDecoder", &value) ||
      !JS_DefineProperty(cx, argument, "StringDecoder", value, 0)) return false;
  for (const char *name : {"AbortSignal", "AbortController"}) {
    if (!JS_GetProperty(cx, engine->global(), name, &value) ||
        !JS_DefineProperty(cx, argument, name, value, 0)) return false;
  }
  if (!JS_GetProperty(cx, engine->global(), "Symbol", &value) || !value.isObject()) return false;
  JS::RootedObject symbol(cx, &value.toObject());
  if (!JS_GetProperty(cx, symbol, "dispose", &value) ||
      !JS_DefineProperty(cx, argument, "disposeSymbol", value, 0) ||
      !JS_GetProperty(cx, symbol, "asyncDispose", &value) ||
      !JS_DefineProperty(cx, argument, "asyncDisposeSymbol", value, 0)) return false;
  JS::RootedValue argument_value(cx, JS::ObjectValue(*argument)), graph_value(cx);
  if (!evaluate_factory(cx, kClassicStreamsFactorySource, argument_value, &graph_value)) return false;
  JS::RootedObject graph(cx, &graph_value.toObject());
  JS::RootedValue root(cx), promises(cx);
  if (!JS_GetProperty(cx, graph, "root", &root) ||
      !JS_GetProperty(cx, graph, "promises", &promises)) return false;
  installed_module.set(root);
  return engine->define_builtin_module("node:stream", root) &&
         engine->define_builtin_module("stream", root) &&
         engine->define_builtin_module("node:stream/promises", promises) &&
         engine->define_builtin_module("stream/promises", promises);
}
#endif

#ifdef NODE_COMPAT_FS
static bool install_fs(api::Engine* engine, JS::HandleValue buffer_constructor,
                       JS::HandleValue streams_module) {
  auto* cx=engine->cx();
  JS::RootedObject argument(cx,JS_NewPlainObject(cx));
  JS::RootedObject kernel(cx,next_fs::create_kernel(cx));
  JS::RootedObject tick(cx,core::EventLoop::create_internal_next_tick(cx));
  if(!argument||!kernel||!tick)return false;
  JS::RootedObject streams(cx,&streams_module.toObject());JS::RootedValue readable(cx);
  if(!JS_GetProperty(cx,streams,"Readable",&readable))return false;
  JS::RootedValue kernel_value(cx,JS::ObjectValue(*kernel)),tick_value(cx,JS::ObjectValue(*tick));
  if(!JS_DefineProperty(cx,argument,"kernel",kernel_value,0)||
     !JS_DefineProperty(cx,argument,"Buffer",buffer_constructor,0)||
     !JS_DefineProperty(cx,argument,"Readable",readable,0)||
     !JS_DefineProperty(cx,argument,"nextTick",tick_value,0))return false;
  JS::RootedValue value(cx,JS::ObjectValue(*argument)),graph_value(cx);
  if(!evaluate_factory(cx,kFsFactorySource,value,&graph_value))return false;
  JS::RootedObject graph(cx,&graph_value.toObject());JS::RootedValue root(cx),promises(cx);
  if(!JS_GetProperty(cx,graph,"root",&root)||!JS_GetProperty(cx,graph,"promises",&promises))return false;
  return engine->define_builtin_module("node:fs",root)&&engine->define_builtin_module("fs",root)&&
         engine->define_builtin_module("node:fs/promises",promises)&&engine->define_builtin_module("fs/promises",promises);
}
#endif

#ifdef NODE_COMPAT_ZLIB
static bool install_zlib(api::Engine *engine, JS::HandleValue buffer_constructor) {
  auto *cx = engine->cx(); // install() already entered the content realm.
  JS::RootedObject kernel(cx, zlib_profile::create_kernel(cx));
  if (!kernel) return false;
  JS::RootedObject argument(cx, JS_NewPlainObject(cx));
  if (!argument) return false;
  JS::RootedValue kernel_value(cx, JS::ObjectValue(*kernel));
  if (!JS_DefineProperty(cx, argument, "kernel", kernel_value, 0) ||
      !JS_DefineProperty(cx, argument, "Buffer", buffer_constructor, 0)) return false;
  JS::RootedValue argument_value(cx, JS::ObjectValue(*argument)), module(cx);
  if (!evaluate_factory(cx, kZlibFactorySource, argument_value, &module)) return false;
  return engine->define_builtin_module("node:zlib", module) &&
         engine->define_builtin_module("zlib", module);
}
#endif

#ifdef NODE_COMPAT_STREAM_CONSUMERS
static bool install_stream_consumers(api::Engine *engine) {
  auto *cx = engine->cx(); // install() already entered CONTENT before user code.
  JS::RootedObject argument(cx, JS_NewPlainObject(cx));
  if (!argument) return false;
  JS::RootedValue value(cx);
  for (const char *name : {"TextDecoder", "ArrayBuffer", "Uint8Array", "DataView"}) {
    if (!JS_GetProperty(cx, engine->global(), name, &value)) return false;
    if (!value.isObject()) {
      JS_ReportErrorASCII(cx, "ERR_SM_NODE_PROFILE_INITIALIZATION: stream consumers native dependency unavailable");
      return false;
    }
    if (!JS_DefineProperty(cx, argument, name, value, 0)) return false;
  }
  JS::RootedValue argument_value(cx, JS::ObjectValue(*argument)), module(cx);
  if (!evaluate_factory(cx, kStreamConsumersFactorySource, argument_value, &module)) return false;
  return engine->define_builtin_module("node:stream/consumers", module) &&
         engine->define_builtin_module("stream/consumers", module);
}
#endif

#ifdef NODE_COMPAT_NEXT_STARTUP
static bool startup_argument(JSContext* cx,JS::HandleObject argument,const char* key,JS::HandleValue value){return JS_DefineProperty(cx,argument,key,value,0);}
static bool startup_builtin(JSContext* cx,JS::HandleObject argument,const char* key,const char* id){
 JS::RootedString name(cx,JS_NewStringCopyZ(cx,id));JS::RootedValue value(cx);if(!name||!ScriptLoader::lookup_registered_builtin(cx,name,&value)||!value.isObject())return false;
 JS::RootedObject record(cx,&value.toObject());bool has=false;if(!JS_HasOwnProperty(cx,record,"default",&has))return false;if(has&&!JS_GetProperty(cx,record,"default",&value))return false;
 return startup_argument(cx,argument,key,value);
}
static bool install_next_startup(api::Engine* engine,JS::HandleValue buffer_constructor){
 auto* cx=engine->cx();JS::RootedObject kernel(cx,create_next_startup_kernel(cx)),argument(cx,JS_NewPlainObject(cx));if(!kernel||!argument)return false;
 JS::RootedValue value(cx,JS::ObjectValue(*kernel));if(!startup_argument(cx,argument,"kernel",value)||!startup_argument(cx,argument,"Buffer",buffer_constructor))return false;
 if(!startup_builtin(cx,argument,"EventEmitter","node:events")||!startup_builtin(cx,argument,"querystring","node:querystring")||!startup_builtin(cx,argument,"paths","node:path/posix"))return false;
 for(const char* name:{"URL","URLSearchParams"})if(!JS_GetProperty(cx,engine->global(),name,&value)||!startup_argument(cx,argument,name,value))return false;
 JS::RootedObject tick(cx,core::EventLoop::create_internal_next_tick(cx));if(!tick)return false;value.setObject(*tick);if(!startup_argument(cx,argument,"nextTick",value))return false;
 JS::RootedValue argument_value(cx,JS::ObjectValue(*argument)),graph_value(cx);if(!evaluate_factory(cx,kNextStartupFactorySource,argument_value,&graph_value)||!graph_value.isObject())return false;
 JS::RootedObject graph(cx,&graph_value.toObject());
 for(const char* id:{"process","os","url"}){if(!JS_GetProperty(cx,graph,id,&value))return false;std::string canonical=std::string("node:")+id;if(!engine->define_builtin_module(canonical.c_str(),value)||!engine->define_builtin_module(id,value))return false;}
 if(!JS_GetProperty(cx,graph,"startup",&value)||!engine->define_builtin_module("starling:node-startup",value))return false;
 if(!JS_GetProperty(cx,graph,"process",&value)||!value.isObject())return false;JS::RootedObject process_record(cx,&value.toObject());
 if(!JS_GetProperty(cx,process_record,"default",&value))return false;
 return JS_DefineProperty(cx,engine->global(),"process",value,0);
}
#endif

#ifdef NODE_COMPAT_TIMERS
static bool install_node_timers(api::Engine* engine){
 auto* cx=engine->cx();JS::RootedObject kernel(cx,builtins::web::timers::create_node_timer_kernel(cx)),argument(cx,JS_NewPlainObject(cx));if(!kernel||!argument)return false;
 JS::RootedValue value(cx,JS::ObjectValue(*kernel));if(!startup_argument(cx,argument,"kernel",value)||!startup_builtin(cx,argument,"util","node:util"))return false;
 if(!JS_GetProperty(cx,argument,"util",&value)||!value.isObject())return false;JS::RootedObject util(cx,&value.toObject());
 if(!JS_GetProperty(cx,util,"promisify",&value)||!value.isObject())return false;JS::RootedObject promisify(cx,&value.toObject());
 if(!JS_GetProperty(cx,promisify,"custom",&value)||!value.isSymbol()||!startup_argument(cx,argument,"promisifyCustom",value))return false;
 for(const char* name:{"AbortSignal","EventTarget"})if(!JS_GetProperty(cx,engine->global(),name,&value)||!startup_argument(cx,argument,name,value))return false;
 if(!JS_GetProperty(cx,engine->global(),"Symbol",&value)||!value.isObject())return false;JS::RootedObject symbol(cx,&value.toObject());
 if(!JS_GetProperty(cx,symbol,"dispose",&value)||!value.isSymbol()||!startup_argument(cx,argument,"disposeSymbol",value))return false;
 JS::RootedValue input(cx,JS::ObjectValue(*argument)),result(cx);if(!evaluate_factory(cx,kNodeTimersFactorySource,input,&result)||!result.isObject())return false;
 JS::RootedObject graph(cx,&result.toObject());if(!JS_GetProperty(cx,graph,"root",&value)||!engine->define_builtin_module("node:timers",value)||!engine->define_builtin_module("timers",value))return false;
 if(!JS_GetProperty(cx,graph,"promises",&value)||!engine->define_builtin_module("node:timers/promises",value)||!engine->define_builtin_module("timers/promises",value))return false;
 if(!JS_GetProperty(cx,graph,"globals",&value)||!value.isObject())return false;JS::RootedObject globals(cx,&value.toObject());
 for(const char* name:{"setTimeout","setInterval","setImmediate","clearTimeout","clearInterval","clearImmediate"})if(!JS_GetProperty(cx,globals,name,&value)||!JS_DefineProperty(cx,engine->global(),name,value,0))return false;
 return true;
}
#endif

bool install(api::Engine *engine) {
  auto *cx = engine->cx();
  // Existing install_builtins() executes in the CONTENT realm before user code.
  // Its ScriptLoader already exists. Avoid Engine::eval_toplevel() here, whose
  // lifecycle assertion requires initialization to have finished.
  JSAutoRealm realm(cx, engine->global());
  JS::RootedObject kernel(cx, create_kernel(cx));
  if (!kernel) return false;
  JS::RootedValue kernel_value(cx, JS::ObjectValue(*kernel));
  JS::RootedValue buffer_module(cx);
  if (!evaluate_factory(cx, kBufferFactorySource, kernel_value, &buffer_module)) return false;
  if (!engine->define_builtin_module("node:buffer", buffer_module) ||
      !engine->define_builtin_module("buffer", buffer_module)) return false;
  JS::RootedValue child_module(cx);
  if (!evaluate_factory(cx, kChildProcessFactorySource, JS::UndefinedHandleValue, &child_module)) return false;
  if (!engine->define_builtin_module("node:child_process", child_module) ||
      !engine->define_builtin_module("child_process", child_module)) return false;
  // Public Buffer is selected explicitly for this profile. Registering both
  // specifiers preserves object/function identities; module namespace records
  // themselves are per-specifier in the existing loader.
  JS::RootedObject buffer_namespace(cx, &buffer_module.toObject());
  JS::RootedValue buffer_constructor(cx);
  if (!JS_GetProperty(cx, buffer_namespace, "Buffer", &buffer_constructor)) return false;
#ifdef NODE_COMPAT_CRYPTO_HASH_HMAC
  if (!install_crypto_hash_hmac(engine, buffer_constructor)) return false;
#endif
#ifdef NODE_COMPAT_PATH
  if (!install_path(engine)) return false;
#endif
#ifdef NODE_COMPAT_EVENTS
  JS::RootedValue events_module(cx);
  if (!install_events(engine, &events_module)) return false;
#endif
#ifdef NODE_COMPAT_STRING_DECODER
  JS::RootedValue decoder_module(cx);
  if (!install_string_decoder(engine, buffer_constructor, &decoder_module)) return false;
#endif
#ifdef NODE_COMPAT_CLASSIC_STREAMS
  JS::RootedValue streams_module(cx);
  if (!install_classic_streams(engine, buffer_constructor, events_module, decoder_module, &streams_module)) return false;
#endif
#ifdef NODE_COMPAT_FS
  if(!install_fs(engine,buffer_constructor,streams_module))return false;
#endif
#ifdef NODE_COMPAT_ASSERT
  if (!install_assert(engine)) return false;
#endif
#ifdef NODE_COMPAT_QUERYSTRING
  if (!install_querystring(engine, buffer_constructor)) return false;
#endif
#ifdef NODE_COMPAT_UTIL
  if (!install_util(engine)) return false;
#endif
#ifdef NODE_COMPAT_STREAM_WEB
  if (!install_stream_web(engine)) return false;
#endif
#ifdef NODE_COMPAT_ZLIB
  if (!install_zlib(engine, buffer_constructor)) return false;
#endif
#ifdef NODE_COMPAT_STREAM_CONSUMERS
  if (!install_stream_consumers(engine)) return false;
#endif
#ifdef NODE_COMPAT_ASYNC_LOCAL_STORAGE
  if (!install_async_local_storage(engine)) return false;
#endif
#ifdef NODE_COMPAT_MODULE
  if (!install_module(engine)) return false;
#endif
#ifdef NODE_COMPAT_NEXT_STARTUP
  if(!install_next_startup(engine,buffer_constructor))return false;
#endif
#ifdef NODE_COMPAT_TIMERS
  if(!install_node_timers(engine))return false;
#endif
  return JS_DefineProperty(cx, engine->global(), "Buffer", buffer_constructor, 0);
}
} // namespace builtins::node_compat
