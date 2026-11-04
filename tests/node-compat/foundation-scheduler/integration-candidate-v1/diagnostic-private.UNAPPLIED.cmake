# Separate future private test producer only. Never included by the production
# recipe above. Select the REVIEWED V3 diagnostic, never the historical V2 CPP.
option(ENABLE_BUILTIN_DIAGNOSTICS_INTERNAL_TICKS "Enable isolated tick test guest modules" OFF)
if(ENABLE_BUILTIN_DIAGNOSTICS_INTERNAL_TICKS AND NOT NODE_COMPAT_INTERNAL_TICKS)
  message(FATAL_ERROR "Diagnostic tick modules require NODE_COMPAT_INTERNAL_TICKS=ON")
endif()
add_builtin(diagnostics::internal_ticks DISABLED_BY_DEFAULT
  SRC "${CMAKE_CURRENT_LIST_DIR}/../taskqueue-owner-v3/test-extension.UNCOMPILED.cpp")
