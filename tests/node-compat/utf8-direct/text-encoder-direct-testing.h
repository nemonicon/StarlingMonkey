// Private experiment only: no JavaScript control or host service is exposed.
// This file is copied beside the PRIVATE patched TextEncoder source.
#ifndef STARLING_UTF8_DIRECT_TESTING_H
#define STARLING_UTF8_DIRECT_TESTING_H
#if !defined(STARLING_UTF8_DIRECT_OOM_TESTING) || !defined(NODE_COMPAT_OOM_TESTING)
#error "Dedicated private OOM build required"
#endif
#if !defined(DEBUG) && !defined(JS_OOM_BREAKPOINT)
#error "A real SpiderMonkey failure simulator is required"
#endif
#include "js/Exception.h"
#include "js/Utility.h"
#include <array>
#include <utility>
namespace builtins::web::text_codec::direct_testing {
enum class Point : size_t { Linearize, Array, Count };
inline std::array<bool,static_cast<size_t>(Point::Count)> fired{};
class FaultScope {
  JSContext* cx_;
  uint32_t previous_thread_=0;
  bool armed_=false;
 public:
  FaultScope(JSContext* cx,Point point):cx_(cx){
    const auto index=static_cast<size_t>(point);
    if(api::Engine::get(cx)->state()!=api::EngineState::Initialized || fired[index])return;
    previous_thread_=js::oom::GetThreadType();
    MOZ_RELEASE_ASSERT(js::oom::simulator.targetThread()==js::THREAD_TYPE_NONE);
    js::oom::SetThreadType(js::THREAD_TYPE_MAIN);fired[index]=true;armed_=true;
    js::oom::simulator.simulateFailureAfter(js::oom::FailureSimulator::Kind::OOM,1,js::THREAD_TYPE_MAIN,true);
  }
  void finish(bool failed){
    if(!armed_)return;
    const bool tripped=js::oom::HadSimulatedOOM();
    js::oom::simulator.reset();
    js::oom::SetThreadType(static_cast<js::ThreadType>(previous_thread_));armed_=false;
    MOZ_RELEASE_ASSERT(tripped,"TextEncoder allocation checkpoint not reached");
    MOZ_RELEASE_ASSERT(failed,"TextEncoder unexpectedly recovered selected allocator failure");
    MOZ_RELEASE_ASSERT(JS_IsThrowingOutOfMemory(cx_),"TextEncoder failure is not a real pending OOM");
  }
  ~FaultScope(){MOZ_RELEASE_ASSERT(!armed_);}
};
template<Point point,typename Operation> auto allocate(JSContext* cx,Operation operation){
  FaultScope scope(cx,point);auto result=operation();scope.finish(!result);return result;
}
} // namespace builtins::web::text_codec::direct_testing
#endif
