# UNAPPLIED benchmark-only CMAKE_PROJECT_ComponentizeJS_INCLUDE payload.
# ComponentizeJS includes Starling/add_as_subproject and the embedding builtin
# before project(ComponentizeJS), so add_builtin and prerequisite targets exist.
option(ENABLE_BUILTIN_DIAGNOSTICS_CLASSIC_BENCHMARK "Enable private classic benchmark guest binding" OFF)
if(ENABLE_BUILTIN_DIAGNOSTICS_CLASSIC_BENCHMARK)
  if(NOT NODE_COMPAT_INTERNAL_TICKS)
    message(FATAL_ERROR "Classic benchmark requires NODE_COMPAT_INTERNAL_TICKS=ON")
  endif()
  if(NOT TARGET builtin_node_compat OR NOT NODE_COMPAT_EVENTS OR NOT NODE_COMPAT_STRING_DECODER)
    message(FATAL_ERROR "Classic benchmark requires existing native Buffer, Events and StringDecoder")
  endif()
endif()
add_builtin(diagnostics::classic_benchmark DISABLED_BY_DEFAULT
  SRC "${CMAKE_CURRENT_LIST_DIR}/benchmark-extension.cpp"
  DEPENDENCIES builtin_node_compat)
