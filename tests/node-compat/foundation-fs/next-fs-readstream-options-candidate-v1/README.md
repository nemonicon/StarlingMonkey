# ReadStream options forwarded by actual Next/send

**Source candidate; target afterimages remain uncompiled/unadopted.** The held V7
engine and every existing Source family remain unchanged.

Actual Next's static-asset request fails with
`node:fs.createReadStream.root is outside this bounded profile`. Its loaded
`next/dist/compiled/send/index.js` copies every enumerable send option into the
ReadStream options, then sets the actual inclusive `start`/`end`. Pinned Node22's
`internal/fs/streams.js` first uses `copyObject` (a `for-in` copy), then consumes
filesystem/Readable options. `root` and the finite send-policy keys selected here
are unused by those consumers. Exact primary sources and callsites are retained
in `primary/` and `demand.json`; source presence does not claim every option was
observed at runtime.

`normalizeReadStreamOptions` preserves enumerable getters and inherited enumerable
keys, reads accepted entries once, and uses a null-prototype result. It strips
only the finite send-only keys: root, acceptRanges, cacheControl, etag, dotfiles,
hidden, extensions, immutable, index, lastModified, maxAge, maxage and from.
It never coerces their values or treats root as filesystem containment. Next/send
still resolves the real file path first; standard preopen rights remain enforced
by the original native provider.

Meaningful fields (including start/end, highWaterMark, encoding and signal) pass
to the original implementation and retain its existing validation. Unsupported
fd/fs/flags/mode/close policies and unknown hooks remain explicit refusals.
Symbols, unknown/prototype-setter keys and unsupported options are not universally
ignored. Existing size, range, ownership, cancellation and phase limits remain.
This does not claim all Node option coercion, accessor-call ordering or extension
hooks. In particular, Node's encoding/signal validation may read getters more
than this normalizer; only the selected observable behavior is tested.

Two integration forms use the same normalizer:

1. Four existing native-source afterimages update the facade, manifest,
   generator and generated header to FS profile `sm-node-22.14.0-m0.21`.
   The existing C++ provider/flags, paths and embedding are unchanged; there are
   no new native source paths or host interfaces. The generator retains V7's
   explicit non-enumerable dependency handling. Inventory/schema/validator files
   under `after/` are byte-identical generation context, not additional deltas.
2. `installReadStreamOptionsFacade(fs)` is a pure guest entry hook for the current
   mutable **CJS/default** fs object. It installs callable ReadStream/FileReadStream
   aliases and createReadStream that delegate to the original real stream with
   normalized options. The derived prototype retains the same Readable state and
   native-handle instance, including ordinary subclasses. Installation performs
   no IO and is idempotent; it refuses replaced bindings on a later call.

Use the entry hook with the genuine default binding before the unchanged app
loads, then invoke streams only after the normal deployed bootstrap:

```js
import fs from 'node:fs';
import {installReadStreamOptionsFacade} from './readstream-options.mjs';
installReadStreamOptionsFacade(fs);
```

Already-captured or frozen **ESM named bindings remain the old functions**; the
installer does not pretend to update them. A stream created through the new CJS
constructor remains an instance of the original ReadStream. The future native
afterimages reconcile freshly-created ESM/default bindings. The entry hook's
pure normalization occurs before delegation to the original deployed guard;
option-getter order at INIT is therefore not promised. No implicit IO, native
handle or host state is captured during installation, and original IO guards
still refuse INIT calls. No reset/restore API is added.

Pinned Node22 host checks pass **21 cases** with real host filesystem IO through
the existing explicitly test-only provider and actual classic Readable. They
cover the old refusal, all selected send keys, exact Node range/bytes, getters
including falsy throws, inherited keys, prototype protection, retained refusals,
UTF8/cancellation, default installation/aliases/subclassing and the named-ESM
deviation. All 24 opened descriptors close; active handles end at zero. This is
host control evidence, not native/guest/full-Next proof.

Generation and installed `--check` pass in this candidate's actual directory;
four host commands have original 0af raw-zero/clean receipts in `host-raw.tar.gz`.
Original V7 source/tool hashes remain unchanged. An initial Python driver token
spacing error occurred before any command or private work creation; its original
source and raw syntax error are preserved. The active driver was corrected,
then the single host check sequence ran once.

Root must review/select the entry facade or compose the four afterimages before
any target action. Current V7 remains unfixed until that integration is actually
constructed/run. No app rewrite, new host import, native build, SDK frontend,
componentizer, guest stream or HTTP request was run by this candidate authoring.
