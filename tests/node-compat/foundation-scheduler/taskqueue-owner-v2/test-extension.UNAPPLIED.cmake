# Future isolated ComponentizeJS project include; never included by live recipe.
# Same add_builtin mechanism used by async-context/probe.cmake, with an explicit
# test-only guest module instead of a global. No change to any production record.
option(ENABLE_BUILTIN_DIAGNOSTICS_INTERNAL_TICKS "Select isolated scheduler test guest module" OFF)
if(ENABLE_BUILTIN_DIAGNOSTICS_INTERNAL_TICKS AND NOT NODE_COMPAT_INTERNAL_TICKS)
  message(FATAL_ERROR "Tick diagnostic requires NODE_COMPAT_INTERNAL_TICKS=ON")
endif()
add_builtin(diagnostics::internal_ticks DISABLED_BY_DEFAULT
  SRC "${CMAKE_CURRENT_LIST_DIR}/test-extension.UNCOMPILED.cpp")
