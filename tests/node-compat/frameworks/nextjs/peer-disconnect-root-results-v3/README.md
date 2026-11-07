# V3 component and pending runtime control

The V3 construction ran successfully: three commands and the original outer
controller exited0/clean. Component643742a2 is37,142,579 bytes and imports the
same thirteen standard WASI0.2.10 interfaces. The complete WIT world guard
remained unchanged.

`peer-v3-runtime-authority.json` was prepared for collectorV2 but never executed.
Independent review found a collector gate that could permit inspection after
a normal output path with an unexpected aborted signal and no observed I/O
abort. That request and collector remain unchanged. A fresh collector and
runtime request must correct the gate before any ordinary V3 workload runs.
