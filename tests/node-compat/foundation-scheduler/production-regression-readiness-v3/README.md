# Production regression source readiness, v3

Root independently passed all 41 host checks, rehashed all 22 source-packet
files and 665 consumed inputs, and verified the independent source review.
The seven additional checks use owned scratch text files; no real engine is
admitted or executed. [Results](results.json) record the exact scope.

V3 fixes the discovered v2 seal gap by binding pin and manifest bytes to captured
primitive digests before parsing or following changed manifest entries. V2 and
its initial review remain preserved and superseded. No runtime reached that
branch because actual production pins are still null.

The common preflight and three runners are implemented preparation. The
successful fixed-artifact branch, real production pins, new native engines,
component tests, remaining strict/Events/Web/RuntimeOnly suites and both-host
HTTP validation remain required. This is not compatibility acceptance.
