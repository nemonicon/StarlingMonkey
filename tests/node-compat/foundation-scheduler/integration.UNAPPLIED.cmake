# SOURCE-ONLY DELTA, NOT an applied build file. No new engine was built.
# Add option validation while processing cmake/builtins.cmake, then the source
# selection AFTER CMakeLists.txt creates the existing starling-raw.wasm target.
option(NODE_COMPAT_INTERNAL_TICKS "Select private bounded guest tick scheduler" OFF)
if(NODE_COMPAT_INTERNAL_TICKS)
  if(NOT TARGET builtin_node_compat)
    message(FATAL_ERROR "NODE_COMPAT_INTERNAL_TICKS requires ENABLE_BUILTIN_NODE_COMPAT=ON")
  endif()
  target_compile_definitions(extension_api INTERFACE NODE_COMPAT_INTERNAL_TICKS=1)
  # This target already compiles runtime/event_loop.cpp and runtime/engine.cpp.
  target_sources(starling-raw.wasm PRIVATE runtime/node_tick_queue.cpp)
endif()
# No dependency on timers, IO polling, environment, clocks, or node:process.
# Installation is an explicit EventLoop::init call, before install_builtins.
# A selected classic-stream factory receives create_private_callable(cx) as one
# private argument; it is never define_builtin_module('node:process', ...).
