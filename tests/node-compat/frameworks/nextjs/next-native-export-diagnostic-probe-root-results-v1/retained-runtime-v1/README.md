# Retained fixed17 direct-WASI diagnostic runtime DATA

This corpus retains one completed `probe-237c-first` runtime sample: all 17 case directories, their data/owner streams and records, the complete outer owner namespace, the final result/authority and both held runtime reviews. It contains 300 copied payload files totaling 1,005,362 bytes, within an 8 MiB aggregate payload fence. The manifest and two reader documents are additional files, outside that payload count. Nineteen historical namespaces describe the whole work directory, the outer owner directory and each of the 17 cases.

The primary review is `91e961ab3887b696fefb7262afa3bb8df12c045fa663dd5b0f1ea009cbbfca52`; its complementary owner/capture review is `77fbda3f7b88e5452a0790050a2b171cf4d2c9fd6fc41313032a9d02d2d1409d`. Original owners and retained final metadata report all 18 owners raw-zero/clean, 17 distinct fresh Wasmtime children, 17 complete finalized stdout captures, 17 HTTP bodies and 16 native records. These observations are checked again by the reader, rather than accepted solely from summary booleans.

`manifest.json` pins every copied byte, original descriptor, historical original file identity and complete namespace. Original absolute paths are documentary lookup keys. The reader never opens them. Copies use portable regular-file modes 0644/0755; directory mode is 0755. Historical original modes, device/inode values and timestamps are documentary and are not imposed on a Git checkout. The reader checks current copy identity, distinct inodes, single links, hash, size, complete file/directory membership and read/final bookends independently. Historical stdout capture identities are compared only to the retained original identity records, never to copied inodes.

The standalone Python standard-library reader validates all declared sizes and the total before any payload read. It checks the fixed schedule, all original start/terminal/argv/cap/authority/owned-record joins, child ownership and SIGINT-zero status, complete EOF/write/sync-close capture metadata, final stderr descriptors, HTTP/body boundaries, both held reviews, selected indexed Source families and the standard-world audit. It does not import, evaluate or call any retained Source, helper, guard, analyzer, Node, Wasmtime, compiler or target.

For each body it parses duplicate-key-free ASCII JSON and recomputes every typed fixture field from the retained case contract. Only after complete stdout capture gates, it parses strict native ASCII JSON lines (at most 512 bytes including LF), recomputes required fields and per-case cardinality, checks fixed static argument routes and permits the contract's two rope-expression alternatives. Repeated observations remain ambiguous. The `/none` zero-record case is a bounded absence observation; attempted cases require a record. These are literal fixture arguments, not the incoming GET path/header metadata.

Engine/component binaries, the 4,859,956-byte native metadata, 5,596,754-byte constructor authority, SDK/package/tool trees and 1,650 native Source-pair payloads are intentionally omitted. Small construction/full-build review documents, the world guard and component audit are retained as explicit delegations. The corpus does not re-prove those omitted payloads. Copied runtime/probe/native/world Source families are byte witnesses only. Their historical uncompiled/NULL/Source-only prose remains unchanged and is not a claim about later actual outputs.

After Root/C Source review, Root can run the reader once from any ordinary checkout or copied corpus:

```sh
python3 -I -B /absolute/path/to/retained-runtime-v1/check.py
```

No arguments or original filesystem paths are required. The command prints JSON to stdout and writes nothing. Save any receipt outside this directory so that the closed corpus namespace remains unchanged. At this Source publication cutoff, R has parsed its own reader with Python AST only and has not executed the reader or its functions. Original/copy byte hashing and physical/namespace bookends were performed by a separate curation program, not by this checker. First checker execution remains pending independent Source review.

The accepted scope is the fixed17 direct-WASI diagnostic sample only. Response fixture flags and the ordinary 524,288-byte allocation do not prove GC, physical string/Store/resource identity, universal harmlessness, native C return, post-return completion, host/TCP completion, cause, Node parity or full Next acceptance. The successful ordinary-call marker is below those later boundaries. No new action is authorized by this corpus.

R authored native/per-case Source and complementary reviews; C independently checked case semantics and coordinated the final runtime review. Root alone invoked the original runtime and guards. Reader Source and copied-DATA integrity review are separate from target execution.
