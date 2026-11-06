# Actual Module kernel SDK syntax

The v2 Module candidate's unchanged native kernel passed actual SDK30/SM147
`clang++ -fsyntax-only`: raw0, empty streams and clean owned group5054.
[Result](results/result.json) retains the exact command, source/index/compiler
descriptors, raw terminal and1045 dependency hashes.

The command derives genuine native target flags from the parent compilation
database, explicitly adds `NODE_COMPAT_MODULE=1`, and puts the real proposed
ScriptLoader/entropy declaration headers before the parent include paths. It is
a new kernel frontend check, not a command from an already configured Module
CMake build. Declared input descriptors match before and after. Header dependency
hashes are captured after compilation; there is no whole-SDK preservation claim.

No object, engine link, module call or guest ran. The changed ScriptLoader
implementation and registrar are not compiled by this command. Full native
integration, actual WASI/libc cwd/preopens and filesystem behavior remain open.
