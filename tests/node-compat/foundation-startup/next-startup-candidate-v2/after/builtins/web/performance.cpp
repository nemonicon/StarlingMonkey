#include "performance.h"
#include <chrono>
#ifdef NODE_COMPAT_NEXT_PERFORMANCE
#include "node-compat-entropy.h"
#include "host-apis/wasi-0.2.10/bindings/bindings.h"
#include "js/BigInt.h"
#endif

namespace {
using FpMilliseconds = std::chrono::duration<float, std::chrono::milliseconds::period>;
} // namespace



namespace builtins::web::performance {

std::optional<std::chrono::steady_clock::time_point> Performance::timeOrigin;

#ifdef NODE_COMPAT_NEXT_PERFORMANCE
namespace {
// Per-Wasm-instance state. Install/INIT reads no clock. A deployed resnapshot
// is not admitted: there is deliberately no reset, setter or inherited origin.
bool startup_origin_ready=false;
uint64_t startup_mono_origin=0,startup_last_monotonic=0;
double startup_unix_origin_ms=0;
DEF_ERR(StartupPerformanceState,JSEXN_ERR,"Deployed performance bootstrap is required",0)
DEF_ERR(StartupPerformanceClock,JSEXN_ERR,"Invalid bounded performance clock sample",0)
bool clock_error(JSContext* cx,const JSErrorFormatString& format,const char* code){
 api::throw_error(cx,format);JS::RootedValue ex(cx);if(!JS_GetPendingException(cx,&ex)||!ex.isObject())return false;JS_ClearPendingException(cx);JS::RootedObject error(cx,&ex.toObject());JS::RootedString text(cx,JS_NewStringCopyZ(cx,code));if(!text)return false;JS::RootedValue v(cx,JS::StringValue(text));if(!JS_DefineProperty(cx,error,"code",v,JSPROP_ENUMERATE))return false;JS_SetPendingException(cx,ex);return false;
}
bool require_deployed(JSContext* cx){auto* engine=api::Engine::get(cx);if(engine&&engine->state()==api::EngineState::Initialized&&builtins::node_compat::entropy::deployed_execution_started())return true;return clock_error(cx,StartupPerformanceState,"ERR_SM_NODE_PERFORMANCE_INITIALIZATION");}
bool require_started(JSContext* cx){if(!require_deployed(cx))return false;if(!startup_origin_ready)return clock_error(cx,StartupPerformanceState,"ERR_SM_NODE_STARTUP_REQUIRED");return true;}
}
// This genuine new JSNative is installed ONLY on the private startup kernel.
// No public method can supply an epoch, reset an origin or mark startup ready.
bool Performance::start_deployed(JSContext* cx,unsigned argc,JS::Value* vp){
 auto args=JS::CallArgsFromVp(argc,vp);if(!require_deployed(cx))return false;
 if(startup_origin_ready){JS::Rooted<JS::BigInt*> n(cx,JS::NumberToBigInt(cx,startup_mono_origin));if(!n)return false;args.rval().setBigInt(n);return true;}
 const uint64_t before=wasi_clocks_monotonic_clock_now();
 wasi_clocks_wall_clock_datetime_t wall{};wasi_clocks_wall_clock_now(&wall);
 const uint64_t after=wasi_clocks_monotonic_clock_now();
 // Standard wall-clock is Unix seconds+nanos. Date's finite epoch range is a
 // declared bound, not an invented host epoch for the monotonic counter.
 if(after<before||wall.nanoseconds>=1000000000||wall.seconds>8640000000000ULL||(wall.seconds==8640000000000ULL&&wall.nanoseconds!=0))return clock_error(cx,StartupPerformanceClock,"ERR_SM_NODE_PERFORMANCE_CLOCK");
 const uint64_t midpoint=before+(after-before)/2;
 const double epoch_ms=static_cast<double>(wall.seconds)*1000.0+static_cast<double>(wall.nanoseconds)/1000000.0;
 if(epoch_ms>8640000000000000.0)return clock_error(cx,StartupPerformanceClock,"ERR_SM_NODE_PERFORMANCE_CLOCK");
 JS::Rooted<JS::BigInt*> n(cx,JS::NumberToBigInt(cx,midpoint));if(!n)return false;
 // Commit only after validation and the fallible return-value allocation.
 startup_mono_origin=midpoint;startup_last_monotonic=midpoint;
 startup_unix_origin_ms=epoch_ms;startup_origin_ready=true;
 args.rval().setBigInt(n);return true;
}
#endif


// https://w3c.github.io/hr-time/#dom-performance-now
bool Performance::now(JSContext *cx, unsigned argc, JS::Value *vp) {
  METHOD_HEADER(0);
#ifdef NODE_COMPAT_NEXT_PERFORMANCE
  if(!require_started(cx))return false;
  const uint64_t current=wasi_clocks_monotonic_clock_now();
  if(current<startup_last_monotonic)return clock_error(cx,StartupPerformanceClock,"ERR_SM_NODE_PERFORMANCE_CLOCK");
  // Subtract in integer space first: large absolute nanoseconds never pass
  // through float32 or lose a small elapsed delta in double cancellation.
  const double elapsed=static_cast<double>(current-startup_mono_origin)/1000000.0;
  startup_last_monotonic=current;args.rval().setNumber(elapsed);return true;
#else
  MOZ_ASSERT(Performance::timeOrigin.has_value());

  auto finish = std::chrono::high_resolution_clock::now();
  auto duration = FpMilliseconds(finish - Performance::timeOrigin.value()).count();

  JS::RootedValue elapsed(cx, JS::Float32Value(duration));
  args.rval().set(elapsed);
  return true;
#endif
}

bool Performance::timeOrigin_get(JSContext *cx, unsigned argc, JS::Value *vp) {
#ifdef NODE_COMPAT_NEXT_PERFORMANCE
  METHOD_HEADER(0);
  if(!require_started(cx))return false;
  args.rval().setNumber(startup_unix_origin_ms);return true;
#else
  MOZ_ASSERT(Performance::timeOrigin.has_value());
  METHOD_HEADER(0);
  auto time = FpMilliseconds(Performance::timeOrigin.value().time_since_epoch()).count();
  JS::RootedValue elapsed(cx, JS::Float32Value(time));
  args.rval().set(elapsed);
  return true;
#endif
}

const JSFunctionSpec Performance::methods[] = {JS_FN("now", now, 0, JSPROP_ENUMERATE), JS_FS_END};

const JSPropertySpec Performance::properties[] = {
    JS_PSG("timeOrigin", timeOrigin_get, JSPROP_ENUMERATE),
    JS_STRING_SYM_PS(toStringTag, "performance", JSPROP_READONLY), JS_PS_END};

const JSFunctionSpec Performance::static_methods[] = {JS_FS_END};
const JSPropertySpec Performance::static_properties[] = {JS_PS_END};

bool Performance::create(JSContext *cx, JS::HandleObject global) {
  JS::RootedObject performance(
      cx, JS_NewObjectWithGivenProto(cx, &Performance::class_, Performance::proto_obj));
  if (!performance) {
    return false;
  }
  if (!JS_DefineProperty(cx, global, "performance", performance, 0)) {
    return false;
  }
  if (!JS_DefineProperties(cx, performance, properties)) {
    return false;
  }
  return JS_DefineFunctions(cx, performance, methods);
}

bool Performance::init_class(JSContext *cx, JS::HandleObject global) {
  return init_class_impl(cx, global);
}

bool install(api::Engine *engine) {
  if (!Performance::init_class(engine->cx(), engine->global())) {
    return false;
  }
  if (!Performance::create(engine->cx(), engine->global())) {
    return false;
  }
  return true;
}

} // namespace builtins::web::performance


