# To avoid conflicts caused by multiple definitions of the same symbols,
# we need to build all Rust crates as part of a single staticlib.
# This is done by synthesizing a Rust crate that depends on all the others,
# and contains `pub use` statements for each of them.
#
# You might ask why we don't just do all of this in Rust itself, without CMake
# involved at all.
# A key reason is that this setup enables us to add Rust crates wherever we'd also
# be able to add C++ libraries, and have them all be built together.
# Notably, this way we can have host-API implementations that include Rust code,
# while keeping the host-API implementation fully self-contained, without changes
# outside its own folder.

set(RUST_STATICLIB_RS "${CMAKE_CURRENT_BINARY_DIR}/rust-staticlib.rs" CACHE INTERNAL "Path to the Rust staticlibs bundler source file" FORCE)
set(RUST_STATICLIB_TOML "${CMAKE_CURRENT_BINARY_DIR}/Cargo.toml" CACHE INTERNAL "Path to the Rust staticlibs bundler Cargo.toml file" FORCE)
set(RUST_STATICLIB_LOCK "${CMAKE_CURRENT_BINARY_DIR}/Cargo.lock" CACHE INTERNAL "Path to the Rust staticlibs bundler Cargo.toml file" FORCE)

configure_file("runtime/crates/staticlib-template/rust-staticlib.rs.in" "${RUST_STATICLIB_RS}" COPYONLY)
# PROPOSED single-aggregate Intl join. SPIDERMONKEY_INTL is declared by
# cmake/spidermonkey.cmake (default OFF); no SM library is built here.
set(NODE_COMPAT_INTL_FIREFOX_SOURCE "" CACHE PATH "Authenticated full or reduced exact9dab Intl source layout")
set(NODE_COMPAT_INTL_LOCKFILE "" CACHE FILEPATH "New reviewed combined aggregate lock; old locks are not interchangeable")
if(SPIDERMONKEY_INTL)
    if(NOT SM_TAG STREQUAL "FIREFOX_147_0_4_RELEASE_STARLING")
        message(FATAL_ERROR "Intl147 Rust join requires the matching SpiderMonkey fork/tag")
    endif()
    foreach(relative IN ITEMS intl/icu_capi/Cargo.toml intl/bidi/rust/unicode-bidi-ffi/Cargo.toml intl/icu_segmenter_data/Cargo.toml)
        if(NOT EXISTS "${NODE_COMPAT_INTL_FIREFOX_SOURCE}/${relative}")
            message(FATAL_ERROR "Missing authenticated Intl source: ${relative}")
        endif()
    endforeach()
    file(STRINGS "${SM_INCLUDE_DIR}/js-config.h" INTL147_HEADER_MARKER REGEX "^#[ \t]*define[ \t]+JS_HAS_INTL_API[ \t]+1[ \t]*$")
    if(NOT INTL147_HEADER_MARKER)
        message(FATAL_ERROR "Intl147 Rust join requires coherent Intl-enabled SpiderMonkey headers/library")
    endif()
    if(NOT "$ENV{CARGO_NET_OFFLINE}" STREQUAL "true" OR NOT EXISTS "$ENV{CARGO_HOME}/config.toml")
        message(FATAL_ERROR "Intl147 requires the reviewed private offline merged-vendor Cargo configuration before Corrosion metadata")
    endif()
    configure_file("runtime/crates/staticlib-template/Cargo.intl.toml.in" "${RUST_STATICLIB_TOML}" @ONLY)
else()
    configure_file("runtime/crates/staticlib-template/Cargo.toml.in" "${RUST_STATICLIB_TOML}")
endif()
if(SPIDERMONKEY_INTL)
    if(NOT EXISTS "${NODE_COMPAT_INTL_LOCKFILE}")
        message(FATAL_ERROR "Intl147 combined lock has not been issued")
    endif()
    configure_file("${NODE_COMPAT_INTL_LOCKFILE}" "${RUST_STATICLIB_LOCK}" COPYONLY)
else()
    configure_file("runtime/crates/staticlib-template/Cargo.lock" "${RUST_STATICLIB_LOCK}" COPYONLY)
endif()

# The audited compatibility recipe opts into Corrosion's existing lock mode.
# Other embeddings retain their existing default configuration.
option(NODE_COMPAT_LOCKED_RUST "Require the versioned aggregate Rust lockfile" OFF)
if(SPIDERMONKEY_INTL AND NOT NODE_COMPAT_LOCKED_RUST)
    message(FATAL_ERROR "Intl147 requires the new combined locked aggregate")
endif()
set(RUST_STATICLIB_LOCK_MODE "")
if(NODE_COMPAT_LOCKED_RUST)
    set(RUST_STATICLIB_LOCK_MODE LOCKED)
endif()

corrosion_import_crate(
        ${RUST_STATICLIB_LOCK_MODE}
        MANIFEST_PATH ${RUST_STATICLIB_TOML}
        CRATES "rust-staticlib"
        NO_LINKER_OVERRIDE
)

# Add a Rust library to the staticlib bundle.
function(add_rust_lib name path)
    add_library(${name} INTERFACE)
    target_include_directories(${name} INTERFACE "${path}")
    file(APPEND $CACHE{RUST_STATICLIB_TOML} "${name} = { path = \"${path}\", features = [${ARGN}] }\n")
    string(REPLACE "-" "_" name ${name})
    file(APPEND $CACHE{RUST_STATICLIB_RS} "pub use ${name};\n")
endfunction()

# These two crates are needed by SpiderMonkey:
add_rust_lib(rust-encoding "${CMAKE_CURRENT_SOURCE_DIR}/crates/rust-encoding")
add_rust_lib(rust-hooks "${CMAKE_CURRENT_SOURCE_DIR}/crates/rust-hooks")

# The rust-hooks crate needs a supporting CPP file
add_library(rust-hooks-wrappers STATIC "${CMAKE_CURRENT_SOURCE_DIR}/crates/rust-hooks/src/wrappers.cpp")
target_link_libraries(rust-hooks-wrappers PRIVATE spidermonkey)
add_library(rust-crates STATIC ${CMAKE_CURRENT_BINARY_DIR}/null.cpp)
target_link_libraries(rust-crates PRIVATE rust_staticlib rust-hooks-wrappers)

# Add crates as needed here:
add_rust_lib(rust-url "${CMAKE_CURRENT_SOURCE_DIR}/crates/rust-url")
add_rust_lib(multipart "${CMAKE_CURRENT_SOURCE_DIR}/crates/rust-multipart" "\"capi\", \"simd\"")

if(SPIDERMONKEY_INTL)
    # add_rust_lib currently always enables defaults. Append this dependency
    # explicitly to preserve the upstream default-features=false contract.
    add_library(icu_capi INTERFACE)
    target_include_directories(icu_capi INTERFACE "${NODE_COMPAT_INTL_FIREFOX_SOURCE}/intl/icu_capi")
    file(APPEND $CACHE{RUST_STATICLIB_TOML} "icu_capi = { path = \"${NODE_COMPAT_INTL_FIREFOX_SOURCE}/intl/icu_capi\", default-features = false, features = [\"any_provider\", \"compiled_data\", \"segmenter\", \"calendar\"] }\n")
    file(APPEND $CACHE{RUST_STATICLIB_RS} "pub use icu_capi;\n")
    add_rust_lib(unicode-bidi-ffi "${NODE_COMPAT_INTL_FIREFOX_SOURCE}/intl/bidi/rust/unicode-bidi-ffi")
endif()
