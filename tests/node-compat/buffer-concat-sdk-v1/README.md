# Actual Buffer.concat SDK syntax

The native candidate at index `1c7b431e` passed the actual WASI SDK30/SM147
`clang++ -fsyntax-only` check: compiler exit0, empty stdout/stderr and clean
owned group4005. The command preserves the genuine parent target's Release
flags, invokes its actual compiler directly and substitutes only the candidate
translation unit; it emits an owned dependency file and no object or engine.

The original Root reporting driver exits1 **after** the successful compiler:
its preservation comprehension refers to an undefined `key`. The exact executed
source is retained in `attempt1-driver.py`. A separate read-only collection
compares the before/current source/index/compiler/database/monitor descriptors,
checks the raw terminal/streams and captures1020 dependency hashes. It does not
rerun the compiler or relabel the original driver as successful.

[Collected result](results/results.json) and byte-exact authority, terminal,
streams and dependencies are retained. Header hashes were captured after
compilation; this is not a whole-SDK before/after preservation proof. No native
kernel, guest, explicit GC/fault, linker or component ran. Observable Buffer
behavior still needs actual component differential tests.

`run.py` now corrects the reporting comprehension for future fresh-output runs;
the original attempt and its external output remain unchanged. The earlier
pre-dispatch Python grammar typo invoked no compiler and created no output.
