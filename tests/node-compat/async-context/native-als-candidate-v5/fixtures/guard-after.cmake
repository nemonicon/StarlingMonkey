    if(NOT TARGET builtin_node_compat OR NOT TARGET extension_api OR NOT NODE_COMPAT_INTERNAL_TICKS)
        message(FATAL_ERROR "Native ALS requires Node compatibility and private tick checkpoints")
    endif()
    # Strict initialization is an INTERFACE compile definition, not a CMake
    # option. Check the actual producer target rather than an unset variable.
    get_target_property(NODE_COMPAT_ALS_EXTENSION_DEFINITIONS extension_api INTERFACE_COMPILE_DEFINITIONS)
    if(NOT "NODE_COMPAT_STRICT_INITIALIZATION=1" IN_LIST NODE_COMPAT_ALS_EXTENSION_DEFINITIONS)
        message(FATAL_ERROR "Native ALS requires strict initialization on extension_api")
    endif()
    unset(NODE_COMPAT_ALS_EXTENSION_DEFINITIONS)
