    if(NOT TARGET builtin_node_compat OR NOT NODE_COMPAT_INTERNAL_TICKS OR NOT NODE_COMPAT_STRICT_INITIALIZATION)
        message(FATAL_ERROR "Native ALS requires Node compatibility and private tick checkpoints")
    endif()
