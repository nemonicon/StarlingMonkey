# Independent component v3 artifact review

All three completed v3 arms pass this independent READ/HASH/DATA review. The
per-arm `results.json` records use the exact finite artifact-review contract in
the separately sealed `cost-jco-correctness-candidate-v2` source. Each record is
indexed exactly once by its own per-arm index. Those records review construction
artifacts and do not authorize subsequent guest calls.

The reviewer ran only the new standard-library Python reader in this packet.
It did not import or execute owner scripts, Node, Jco, Wasm tools, parser
libraries, generated JavaScript, engines, codecs, guest exports or hosts. WIT
and declarations were compared as complete fixed text; Wasm files were read as
opaque bytes. There is no claim of a fresh binary-WIT decode. The retained
owner-emitted WIT, Jco metadata and component import-audit record are separately
hashed and cross-bound to the actual component. The entire generated core
occurs exactly once in each component at byte offset 13, with 1,059 other bytes.
That byte relation does not establish runtime behavior.

Each actual parent has 25 indexed files and 27 actual regular files. Each
worker has 17 indexed files and 19 actual regular files. Both exact membership
sets include only the indexed files plus their index and completion. Raw outer
and owned-child terminal records are checked separately. All outer/owned raw
statuses are zero, deadlines did not expire, the owned process closed without
signals/errors, and its group was recorded gone. Elapsed values are retained
only as operational status records and are not performance observations.

The emitted WIT and declaration files contain the seven scalar ABI functions.
Jco metadata describes those same seven functions and no imports. The generated
JavaScript has those seven static function exports plus the distinct exact
terminal empty ordinary-object `_util` declaration. `_util` occurs once in the
entire generated text. The actual same-directory package file is exactly
`{"type":"module"}` followed by a newline. No generated module was imported.

The common context review rehashes the component/glue, corrected WIT, original
component donor, tooling and guest source indexes; 91 preparation descriptors
are treated only as DATA. It rehashes all 10,187 published regular files and
checks the exact publication membership, 22 internal symlinks and 471
directories. Both immutable native tuples include their engines, metadata,
freeze receipts, 1,024 frozen copies each, 350 native inputs and three external
embedding inputs. Five explicitly reviewed SDK references are rehashed,
including the archive. Old mutable original caches and historical consumed
manifests are not followed. The source peer, actual pair proof, oracle/render
proof, actual bundle source proofs, physical/virtual bundle sources and all 78
per-arm critical descriptors are authenticated independently as files.

The native metadata backend proof remains exactly
`{"verified":false,"version":null,"vernum":null}`. Ordinary350 admission stays
CLOSED. Componentization initialization occurred in the authorized owner build;
ordinary guest calls, correctness, fresh Wasmtime string transport, operational
admission, source promotion, pilot and timing are not established by this
packet. Failed v1 and v2 attempts remain historical and are not accepted here.

`source-review.json` and `rehashed-common-inputs.json` describe the common source
scope. Each arm has its independent result, artifact witnesses and rehashed
inputs. `external-statuses.json` and byte-preserved evidence copies retain the
outer/owned status scope separately. `results.json` binds the three capsules.
