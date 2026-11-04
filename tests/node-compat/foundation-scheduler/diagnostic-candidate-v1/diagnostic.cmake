# Isolated diagnostic producer only; never included by the production recipe.
option(ENABLE_BUILTIN_DIAGNOSTICS_INTERNAL_TICKS "Enable private scheduler test guest modules" OFF)
if(ENABLE_BUILTIN_DIAGNOSTICS_INTERNAL_TICKS AND NOT NODE_COMPAT_INTERNAL_TICKS)
  message(FATAL_ERROR "Private diagnostic modules require NODE_COMPAT_INTERNAL_TICKS=ON")
endif()
add_builtin(diagnostics::internal_ticks DISABLED_BY_DEFAULT
  SRC "${CMAKE_CURRENT_LIST_DIR}/test-extension.cpp")
