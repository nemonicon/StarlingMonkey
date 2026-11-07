Experimental SpiderMonkey prerequisite retained from CI run [42281671898](https://github.com/nemonicon/StarlingMonkey/actions/runs/42281671898).

This draft preserves the exact original CI ZIP, whose Actions retention expires
on 2026-11-09 at 20:11:07 UTC. No archive was repacked and no build was rerun.
It contains the guest static library, matching installed headers, Firefox FFI
sources and the original build evidence.

- Original artifact ID: `13536973897`.
- ZIP: `artifact.zip`, 227,965,139 bytes.
- SHA256: `abbbd37727631187ef20f5b9a2ee1d6d50dbf9ef6c1e5b45f9234f1a2f7c7f74`.
- Build-driver commit: `bb2526b7e862ad7d8f93254beac41dc48b0fa349`.
- Guest source: [bytecodealliance/firefox at 9dab3d6f643e926a340c391ea30968e940390dec](https://github.com/bytecodealliance/firefox/tree/9dab3d6f643e926a340c391ea30968e940390dec).
- Applied [SavedFrame patch](https://github.com/nemonicon/StarlingMonkey/blob/bb2526b7e862ad7d8f93254beac41dc48b0fa349/tests/node-compat/frameworks/nextjs/stacktrace-native-v1/spidermonkey-patch/saved-frame-is-eval-v1.patch): SHA256 `1a571a891cffd3b81b463c922212f8a4ab1dd1f42b717da4cac5c401445bc9b1`.

`SHA256SUMS` checks the ZIP; `source-provenance.json` records its two nested
archive identities and the merged library identity. The retained
[CI DATA review](https://github.com/nemonicon/StarlingMonkey/tree/e0adca1ca961a481fada2aaf09383fbaf647eb7f/tests/node-compat/frameworks/nextjs/spidermonkey-intl-build-v1/ci-patched-root-results-v1)
and the later repository review document the separate build and runtime scopes.

The draft is a retained prerequisite for the experimental Next profile. Its
publication status, complete clean-machine bootstrap, fresh full engine build
and production promotion remain separate decisions and validation gates.
