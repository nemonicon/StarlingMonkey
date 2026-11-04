# Based on https://stackoverflow.com/a/72187533
set(OPENSSL_VERSION 3.0.17)
set(OPENSSL_HASH "SHA256=dfdd77e4ea1b57ff3a6dbde6b0bdc3f31db5ac99e7fdd4eaf9e1fbb6ec2db8ce")
include(ExternalProject)

if (CMAKE_GENERATOR STREQUAL "Unix Makefiles")
    set(MAKE_COMMAND "$(MAKE)")
else()
    find_program(MAKE_COMMAND NAMES make gmake)
endif()

# CFLAGS below replaces OpenSSL's default optimization flags, so set them per build type.
if (CMAKE_BUILD_TYPE STREQUAL "Debug")
    set(OPENSSL_BUILD_FLAGS --debug -O0 -g)
elseif (CMAKE_BUILD_TYPE STREQUAL "RelWithDebInfo")
    set(OPENSSL_BUILD_FLAGS --release -O2 -g)
elseif (CMAKE_BUILD_TYPE STREQUAL "MinSizeRel")
    set(OPENSSL_BUILD_FLAGS --release -Os)
else()
    set(OPENSSL_BUILD_FLAGS --release -O3)
endif()

# Source and build identity include the actual patch contents and policy flags.
# A changed patch path alone does not invalidate CPM/ExternalProject caches.
file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/deps/patches/getuid.patch" OPENSSL_GETUID_PATCH_SHA256)
file(SHA256 "${CMAKE_CURRENT_SOURCE_DIR}/deps/patches/rand.patch" OPENSSL_RAND_PATCH_SHA256)
set(OPENSSL_RAND_SEED getrandom)
set(OPENSSL_PROFILE_FLAGS "")
if(ENABLE_BUILTIN_NODE_COMPAT)
    set(OPENSSL_RAND_SEED none)
    set(OPENSSL_PROFILE_FLAGS -DSTARLING_NODE_ENTROPY_PROFILE=1)
endif()
string(SHA256 OPENSSL_BUILD_KEY
    "${OPENSSL_HASH};${OPENSSL_GETUID_PATCH_SHA256};${OPENSSL_RAND_PATCH_SHA256};${ENABLE_BUILTIN_NODE_COMPAT};${NODE_COMPAT_ENTROPY_MODE};${OPENSSL_RAND_SEED};${OPENSSL_BUILD_FLAGS};${WASI_SDK_PREFIX}")
set(OPENSSL_INSTALL_DIR ${CMAKE_BINARY_DIR}/deps/OpenSSL-${OPENSSL_BUILD_KEY})
set(OPENSSL_INCLUDE_DIR ${OPENSSL_INSTALL_DIR}/include)

CPMAddPackage(NAME
        OpenSSL
        URL https://openssl.org/source/old/3.0/openssl-${OPENSSL_VERSION}.tar.gz
        URL_HASH ${OPENSSL_HASH}
        CUSTOM_CACHE_KEY ${OPENSSL_BUILD_KEY}
        PATCHES
            ${CMAKE_CURRENT_SOURCE_DIR}/deps/patches/getuid.patch
            ${CMAKE_CURRENT_SOURCE_DIR}/deps/patches/rand.patch
        DOWNLOAD_ONLY TRUE
)
# Check the actual applied code, not just a stamp or the patch file's pathname.
file(SHA256 "${OpenSSL_SOURCE_DIR}/crypto/rand/rand_lib.c" OPENSSL_APPLIED_RAND_SHA256)
if(NOT OPENSSL_APPLIED_RAND_SHA256 STREQUAL "e8c853b5d609b5b13f3a63ddcd88047a37fb75afa59e88d1950907c5a85bcd95")
    message(FATAL_ERROR "Unexpected OpenSSL rand_lib.c after pinned patches")
endif()
ExternalProject_Add(
        OpenSSL
        PREFIX ${CMAKE_BINARY_DIR}/deps/openssl-build-${OPENSSL_BUILD_KEY}
        SOURCE_DIR ${OpenSSL_SOURCE_DIR}
        CONFIGURE_COMMAND
        CC="clang" CFLAGS="--sysroot=${WASI_SDK_PREFIX}/share/wasi-sysroot" ${OpenSSL_SOURCE_DIR}/config
        --prefix=${OPENSSL_INSTALL_DIR}
        --openssldir=${OPENSSL_INSTALL_DIR}
        -static -no-sock -no-asm -no-ui-console -no-egd
        -no-afalgeng -no-tests -no-stdio -no-threads no-dso
        -D_WASI_EMULATED_SIGNAL
        -D_WASI_EMULATED_PROCESS_CLOCKS
        -D_WASI_EMULATED_GETPID
        -DHAVE_FORK=0
        -DNO_SYSLOG
        -DNO_CHMOD
        -DOPENSSL_NO_SECURE_MEMORY
        ${OPENSSL_PROFILE_FLAGS}
        ${OPENSSL_BUILD_FLAGS}
        --with-rand-seed=${OPENSSL_RAND_SEED}
        --prefix=${OPENSSL_INSTALL_DIR}
        --cross-compile-prefix=${WASI_SDK_PREFIX}/bin/
        linux-x32
        BUILD_COMMAND ${MAKE_COMMAND}
        TEST_COMMAND ""
        INSTALL_COMMAND ${MAKE_COMMAND} install_sw
        INSTALL_DIR ${OPENSSL_INSTALL_DIR}
        BUILD_BYPRODUCTS ${OPENSSL_INSTALL_DIR}/libx32/libcrypto.a
)

# We cannot use find_library because ExternalProject_Add() is performed at build time.
# And to please the property INTERFACE_INCLUDE_DIRECTORIES,
# we make the include directory in advance.
file(MAKE_DIRECTORY ${OPENSSL_INCLUDE_DIR})

add_library(OpenSSL::Crypto STATIC IMPORTED GLOBAL)
set_property(TARGET OpenSSL::Crypto PROPERTY IMPORTED_LOCATION ${OPENSSL_INSTALL_DIR}/libx32/libcrypto.a)
target_include_directories(OpenSSL::Crypto INTERFACE ${OPENSSL_INCLUDE_DIR})
add_dependencies(OpenSSL::Crypto OpenSSL)

# Build receipt consumed by the audited engine recipe after configure/build.
file(WRITE "${CMAKE_BINARY_DIR}/openssl-profile-receipt.txt"
    "version=${OPENSSL_VERSION}\narchive=${OPENSSL_HASH}\nprofile=${ENABLE_BUILTIN_NODE_COMPAT}\nentropy=${NODE_COMPAT_ENTROPY_MODE}\nrandSeed=${OPENSSL_RAND_SEED}\nsourceKey=${OPENSSL_BUILD_KEY}\nsourceDir=${OpenSSL_SOURCE_DIR}\ninstallDir=${OPENSSL_INSTALL_DIR}\nrandPatchSha256=${OPENSSL_RAND_PATCH_SHA256}\nappliedRandSha256=${OPENSSL_APPLIED_RAND_SHA256}\nbuildFlags=${OPENSSL_BUILD_FLAGS};${OPENSSL_PROFILE_FLAGS}\n")
