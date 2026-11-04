# Correction: live Preview1 adapter omitted from production seals

Root's resolved-path audit found a missing live input in the common-v3,
followon-OFF and 1,405-input release runner seals. Their inputs do not resolve to
the repository Preview1 adapter that the packager reopens. Its explicit
`988224…` prepackaging hash does not provide the missing post-run live-file seal.
This note independently confirms that bounded finding and supersedes the earlier
complete-input-closure approval.

The original packet indexes remain unchanged. Reversible source-body edits,
53 host checks, redirected Path oracle output equality and unchanged original
files retain their stated scope. No production positive artifact branch reached
execution because actual pins remained null. No native or guest failure follows.

The separate diagnostic driver-v2 now includes the exact live adapter among its
32 inputs. That correction does not implicitly amend the production runner
packets. Their next activation revision must coherently add the live adapter
with new actual production306 freezes/pins and the existing primitive-digest
pre/post checks. This note implements no such activation or source rewrite.

[review.json](review.json) records exact resolved-path comparisons and frozen
packet digests. No old packet, source body or receipt was changed, and no
compiler, packager, build or guest was run.
