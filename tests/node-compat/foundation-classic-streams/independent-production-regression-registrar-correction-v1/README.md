# Source-review correction: registrar ancestry

The earlier review747ba missed a cross-layer host-oracle guard. Assert, Querystring
and Util native Node oracle data all pin full register.cpp BEFORE19eef…, while
the valid classic342 source layer changes that file to AFTER2848…. The inherited
native-scalar helper still demands exact BEFORE and therefore fails before any
componentization. This is a harness admission defect, not a native artifact failure.

A new reviewed amendment must accept the exact before→after ancestry only after
the real342 gate, retaining forceStrictMode and all facade/guest/oracle byte pins.
Old oracle files, source81c, review747ba, replay118999 and accepted reports remain
unchanged. Root assigned that amendment separately. The combined HTTP oracle
construction does not make this full-registrar comparison and is unaffected.

No guest, compiler or runtime test ran to identify this source contradiction.
[results.json](results.json) records the exact hashes and narrows the earlier
no-blocker conclusion; its byte-seal, reverse-proof and authority findings stand.
