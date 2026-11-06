This is a compact unapplied ALS CMake-guard correction over actual composed
Next Source432, preserving all earlier ALS Source and both failed build roots.
It changes one existing cmake/builtins.cmake path. No native C++, JS, manifest,
export, source count or target policy changes. The localized before/after and
whole afterimage are indexed here; Root must compose a genuine new Source root.

Actual build attempt2 fixed the missing templates but still failed configure:
the ALS guard treated NODE_COMPAT_STRICT_INITIALIZATION as a CMake variable.
The actual producer declares it only via target_compile_definitions(extension_api
INTERFACE NODE_COMPAT_STRICT_INITIALIZATION=1). The new guard reads that real
target's INTERFACE_COMPILE_DEFINITIONS and requires the exact enabled marker
using IN_LIST. Node compatibility, extension_api and private ticks are still
required. Missing or disabled target policy refuses; setting an unrelated CMake
variable true cannot bypass it. The original strict compile definition remains
unchanged, and ALS remains defaultOFF. No policy is weakened.

test-policy.py ran ten small actual CMake policy configurations with LANGUAGES
NONE and interface-only targets. It includes exact guard snippets extracted from
the before/after Source and the genuine producer definition call. The old actual
marker/unset-variable case fails; the corrected case passes. Missing/disabled
marker, forged true variable, missing targets and disabled ticks fail. The test
retains every full argv/stdout/stderr/exit observation; only its own disposable
scratch build directories are removed. No native project was configured, no
compiler/linker or original monitor/helper ran, and no engine/guest was invoked.
This test writes into its own new family and refuses existing result folders;
do not rerun it against this sealed packet.

failed-build-attempt2 preserves exact configure log/phase/terminal plus finite
original result/metadata descriptors and fields. The original failure stays
FAILED_UNACCEPTED: configure inner/outer1, original2100 inputs unchanged, no
engine/native build target phase. Configuration had compiler/dependency setup;
it is not described as zero original compiler activity. The author's preparation
does not mutate either old WORK or composed Source. Free space was observed and
recorded without cleanup.

Root can publish Sourcev4 with the same432 path count and this one CMake change;
all unchanged C++ frontend evidence keeps its actual original identity. Installed
generator checks and a fresh build authority remain Root's actions. The existing
buildcandidate-v3 runner/386-support plan need no code changes; Root selects a
fresh WORK. This Source has no actual native build, runtime or admission authority.
