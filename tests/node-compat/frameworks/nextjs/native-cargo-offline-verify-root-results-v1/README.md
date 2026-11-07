# First metadata verifier launch: pre-entry failure

The held verifier V1 Source passed its 77 local DATA checks, independent source
review and Root's genuine read-only source/stage/authority joins. Its first
operational launch nevertheless exits 1 before authority admission, output
creation, monitor/worker startup or Cargo execution.

`launch-process.json` retains the actual pinned Python3.11 `-I -B` argv and
exit code. Raw stdout is empty; stderr retains the traceback. Python's
`sys.flags.isolated` is integer `1`; the guard's `and` expression returns that
integer, which the strict `need(value is True)` rejects. The command correctly
sets isolation and disables bytecode writes. This is a checker defect.

`launch-classification.json` records the observed failure and absent requested
output. V1 Source, authority, read-only results and failure are preserved.
A separately reviewed successor must correct both operational entry guards
before a genuinely new metadata query can run. No Cargo metadata, compiler,
native build or runtime acceptance follows from this attempt.
