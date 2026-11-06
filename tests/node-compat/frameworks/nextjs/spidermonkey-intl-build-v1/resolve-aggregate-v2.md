# Explicit compatible-family seed reconciliation

This genuine successor preserves `resolve-aggregate.py`, the failed work v1,
original Cargo 101/stderr and all current source inputs. Use a fresh work v2
and Root config/authority binding the new helper descriptor. It executes no
Cargo, compiler or guest command. The original three-command plan, HOME policy,
six actual root dependencies, single staticlib and source/checksum guards are
unchanged. No unused dependency is introduced to pin a transitive package.

The first real Cargo resolution rejected simultaneously locked semver-compatible
smallvec 1.14.0 and 1.15.1. The Source V2 seed makes these **explicit** choices:

| Package | Fork seed | Selected old pin |
| --- | --- | --- |
| displaydoc | 0.2.4 | 0.2.5 |
| proc-macro2 | 1.0.101 | 1.0.94 |
| quote | 1.0.40 | 1.0.39 |
| serde | 1.0.227 | 1.0.218 |
| serde_derive | 1.0.227 | 1.0.218 |
| smallvec | 1.15.1 | 1.14.0 |
| syn | 2.0.106 | 2.0.99 |
| unicode-ident | 1.0.6 | 1.0.17 |
| zerofrom | 0.1.4 | 0.1.5 |
| zerofrom-derive | 0.1.3 | 0.1.6 |

`cargo-seed-reconciliation-v2.json` retains 33 exact-fork parent-manifest
identities and 59 declared dependency requirements. Existing old constraints
remain internally unchanged. The selected old pins satisfy the inspected fork
requirements except the deliberately excluded exact SerdeCore edge. For
example, fork syn requires proc-macro2≥1.0.91, and fork serde_derive requires
syn≥2.0.81; selected 1.0.94/2.0.99 satisfy those bounds. Distinct incompatible
major/zero-minor families, including ICU 1.5/2.0, stay separate.

Do not redirect SerdeCore's exact `serde_derive=1.0.227` edge to an incompatible
version. Choosing old serde/derive together makes fork serde_core unreachable.
V2 redirects reachable callers, walks from the six actual aggregate roots and
prunes unreachable fork rows; it explicitly fails if a SerdeCore exact edge
would remain reachable. Tests require all 49 old identities to survive, every
listed compatible family to have one selected version, and the old exact
serde/derive pair to stay intact.

This remains an **untrusted seed**, not a Cargo solution. Root must run real
online metadata under the reviewed monitor, retain its complete outputs and
then apply the DATA audit. The audit now also rejects any actual shared-family
selection that differs from this explicit table. Any required further change
must be reviewed from the actual conflict; latest releases or merely
same-major versions are not silently accepted. Vendor/offline/native gates
remain closed until their separate genuine results pass.
