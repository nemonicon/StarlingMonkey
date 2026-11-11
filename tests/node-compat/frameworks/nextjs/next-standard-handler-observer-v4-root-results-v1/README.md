# V4 observer build and component metadata evidence

The seven real-component probes pass on Wasmtime 42.0.1 under original owner
22795/900. The [result report](../../../../../docs/node-compat/nextjs-observer-v4-results.md)
describes the exact cases, standard imports and limits. Full Next.js acceptance
remains false.

`actual-v4-composition-review.json` records the seven successful build/tool steps,
unchanged inner bytes, shared nominal resources and canonical call structure.
`actual-metadata-runtime-review.json` records the separately executed seven HTTP
cases. The Source packets retain their historical unexecuted/NULL labels;
these external records provide actual evidence without rewriting their history.

Run the saved regression check from the repository root:

```sh
python3 -I -B tests/node-compat/frameworks/nextjs/next-standard-handler-observer-v4-root-results-v1/check-retained-v2.py
```

It verifies the closed 70-file packet, raw canonical metadata, HTTP bodies,
request headers, stdout completeness, host shutdown and original-owner cleanup.
It opens no original absolute paths and launches no host. Replaying the actual
host workload requires fresh output/run namespaces; the retained one-shot
controllers refuse to overwrite old observations.

The hardened v2 reader additionally bounds reads before allocation and checks
canonical paths and read bookends. Current and isolated staged-Git copies pass;
the original reader remains unchanged for its historical review. The tested
observer is also composed with the original Next inner: envelope `9da63790`
passes four tool steps and the structural review in
`actual-next-v4-composition-review.json`. Next HTTP/browser execution with this
envelope is still pending.

`source-history` preserves donor, unbound and corrected preimages. The initial
model preflight and builder-binding refusal both precede Node/host execution.
Their corrected attempts and exact binding inverses are recorded separately.
The earlier V3 join refusal and strict browser failure remain unchanged.
