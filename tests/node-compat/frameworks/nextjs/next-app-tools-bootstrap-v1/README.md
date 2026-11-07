# Official npm tool acquisition — no package execution

This actual acquisition restored **npm10.9.2** from the official Node22.14.0
macOS ARM64 distribution into a new private prefix. It did not run Node, npm,
an install, Next, a compiler or a guest. Those statements describe this
acquisition phase; a later separately authorized app-build operation is distinct
and cannot be inferred from this record.

Discovery found no matching archive or npm-cli in the scoped private tree. The
old historical Node prefix had lost its npm directory. Local Homebrew npm11.11.0
has compatible engine metadata but is a different package-manager generation
with no same-release acquisition pin found. It was not selected or changed.
`discovery.json` records the scope; it is not a whole-disk absence claim.

The [official published SHASUMS](https://nodejs.org/download/release/v22.14.0/SHASUMS256.txt)
and [release page](https://nodejs.org/en/blog/release/v22.14.0) were consulted.
The downloaded `node-v22.14.0-darwin-arm64.tar.xz` is24,386,052 bytes and matches
published SHA256
`4e845cb71b4e897289312743b2e31c405a8a48720655404d82a4dce23fc43527`.
Official HTTPS/checksum verification is retained; OpenPGP signature verification
was not performed or claimed.

`acquire.py` manually reads archive members and writes **only**
`lib/node_modules/npm`. It rejects unsafe/duplicate paths, special files,
hardlinks, escaping links and overwrites. Relative internal symlinks are allowed
only after verifying targets inside the complete extracted tree; this actual
npm archive has none. The inventory contains2379 regular files,562 directories,
zero links and11,690,702 file bytes, with exact archive-derived SHA/byte/mode
records. Hidden files are included. `npm-inventory.json.gz` losslessly retains
the934,025-byte inventory; package sources and the archive remain private.

The official108,619,024-byte `bin/node` member was streamed through SHA256,
**not extracted**. It exactly matches the existing selected Node binary
`e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0`.
The original binary's full hash and filesystem identity remain unchanged.
No old Node/tools, package prefix, HOME or global npm config was modified.

The new npm CLI is:

```text
/private/tmp/starling-node-compat/next-app-tools-bootstrap-v1/lib/node_modules/npm/bin/npm-cli.js
SHA256 8e5f6f3429f8cdbe693cdc29904e9d5a7b127a494bd15c804bd54c7403bfcbe7
54 bytes
```

This is npm's real entry into its complete bundled package, not a copied facade
or shim. Future use still requires the app CLI's actual version probes and
before/final tool/source guards. This recipe requires an existing selected Node;
it does not install a Node executable on a clean machine.

Actual free space was1,325,461,504→1,280,770,048 bytes. New regular storage was
37,014,556 bytes before the final result file. The separate acquisition policy
checks1GiB free initially, during download/extraction and finally, bounds archive
and npm expansion at64MiB each and total private output at128MiB. It does not
change any native-build/constructor/app preflight floor or prove continuous
global capacity. A later app-build capacity refusal remains separate evidence.

`acquisition-observation.json` is the actual successful typed result; all HTTP
headers/URLs, published checksum, archive and extracted inventory descriptors,
Node hash/identity and capacity observations are retained. Root independently
rehashed the official archive, checksum, Node, CLI/package and all2379 npm files,
modes and exact membership. `check.py` is an additional inert data reader:

```sh
python3 -B -I check.py
python3 -B -I check.py --current
```

The portable form checks retained checksum/inventory/result joins. `--current`
also reads the original private archive, complete npm tree and unchanged Node;
it executes no package or tool. No executable/package payload is committed here.
The data reader was authored by the acquisition actor, not an independent
Source peer. Root's separate readback is additional evidence. No app-build,
clean-machine build, operating-system hermeticity or runtime acceptance is
granted by acquiring these tools.
