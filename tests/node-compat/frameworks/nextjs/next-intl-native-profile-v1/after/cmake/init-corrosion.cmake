# Ensure that corrosion-rs is initialized, so we can use it or depend on variables it sets.
# NOTE: This file must not be called `corrosion.cmake`, because otherwise it'll be called recursively instead of the
# same-named one coming with Corrosion.

set(Rust_CARGO_TARGET wasm32-wasip1)
# Necessary to make cross-compiling to wasm32-wasi work for crates with -sys dependencies.
set(Rust_CARGO_TARGET_LINK_NATIVE_LIBS "")

file(STRINGS "${CMAKE_CURRENT_SOURCE_DIR}/rust-toolchain.toml" Rust_TOOLCHAIN REGEX "^channel ?=")
string(REGEX MATCH "[0-9.]+" Rust_TOOLCHAIN "${Rust_TOOLCHAIN}")
option(NODE_COMPAT_PREINSTALLED_RUST "Use explicitly selected existing Rust tools without rustup setup" OFF)
if(NODE_COMPAT_PREINSTALLED_RUST)
    foreach(tool Rust_COMPILER Rust_CARGO)
        if(NOT IS_ABSOLUTE "${${tool}}" OR NOT EXISTS "${${tool}}" OR IS_DIRECTORY "${${tool}}" OR IS_SYMLINK "${${tool}}")
            message(FATAL_ERROR "${tool} must be an absolute existing regular direct tool")
        endif()
    endforeach()
    if(NOT DEFINED Rust_RESOLVE_RUSTUP_TOOLCHAINS OR Rust_RESOLVE_RUSTUP_TOOLCHAINS)
        message(FATAL_ERROR "Preinstalled Rust requires Rust_RESOLVE_RUSTUP_TOOLCHAINS=OFF")
    endif()
    # FindRust prioritizes rustup whenever Rust_TOOLCHAIN is defined, even if
    # toolchain resolution is disabled. Keep the source channel as evidence,
    # then let its real direct-compiler discovery branch run.
    set(NODE_COMPAT_PREINSTALLED_RUST_CHANNEL "${Rust_TOOLCHAIN}" CACHE STRING "Source-selected Rust channel" FORCE)
    unset(Rust_TOOLCHAIN)
    unset(Rust_TOOLCHAIN CACHE)
    unset(Rust_RUSTUP)
    unset(Rust_RUSTUP CACHE)
else()
    execute_process(COMMAND rustup toolchain install ${Rust_TOOLCHAIN})
    execute_process(COMMAND rustup target add --toolchain ${Rust_TOOLCHAIN} wasm32-wasip1)
endif()

CPMAddPackage("gh:corrosion-rs/corrosion@0.5.1")
string(TOLOWER ${Rust_CARGO_HOST_ARCH} HOST_ARCH)
