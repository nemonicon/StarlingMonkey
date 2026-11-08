# Preserved preparation failure

Root's first JSON preparation (faa419, raw1) stops in `context()` before loading
the full-native/world guards, issuing an authority or launching any actor.
`preparation.stdout.log` is empty; `preparation.stderr.log` retains the complete
1,032-byte assertion traceback.

The command uses the pinned canonical Cellar Python3.11 executable. On this
installation `sys.executable` reports `/opt/homebrew/opt/python@3.11/bin/python3.11`,
which resolves to that same Cellar executable. The wrapper incorrectly passes
the unresolved alias into its canonical-file reader. Root's separate read-only
Python identity observation35c1c3 confirms both paths; this is a launcher error,
not an engine, guest or wasmCloud failure.

Both original Source files and raw outputs remain unchanged. A separate
`wasmcloud-cold-root-results-v6` successor resolves `sys.executable` before the
existing strict file/hash comparison. The held cold actor Source01a939fa is
unchanged. No runtime result or acceptance follows from this failed preparation.
