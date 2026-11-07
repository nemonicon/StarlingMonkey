# Retained SpiderMonkey prerequisite

The original CI artifact expires on2026-11-09 at20:11:07UTC. Root preserved its
exact existing ZIP in a [draft release](https://github.com/nemonicon/StarlingMonkey/releases/tag/untagged-cd26ac319548f5d6f9b0),
release437352699, without downloading, extracting or repacking the archive.
The draft requires repository authentication and remains unpublished.

The ZIP is227,965,139 bytes, SHA256 `abbbd37727631187ef20f5b9a2ee1d6d50dbf9ef6c1e5b45f9234f1a2f7c7f74`.
Its stable authenticated [release-asset API](https://api.github.com/repos/nemonicon/StarlingMonkey/releases/assets/719685339)
is separate from the expiring Actions artifact13536973897. The original
1449-member ZIP includes the matched guest library/headers, four Firefox FFI
source directories and CI evidence. Source is fork9dab3d6f plus SavedFrame
patch1a571a89, built by the driver atbb2526b7. The retained
[original CI DATA review](../spidermonkey-intl-build-v1/ci-patched-root-results-v1/README.md)
documents the exact nested archives and its validation limits.

`ci-artifact-metadata.json` records current connector metadata and expiry;
`draft-release-metadata.json` records GitHub's uploaded asset IDs, sizes and
digests. Root rehashed the local ZIP before/after upload. All three remote
asset digests match the local ZIP, checksum file and provenance JSON. A peer
independently matched those records and stream-hashed both nested tar members
without extraction. No remote ZIP round-trip download was performed.

`release-notes.md`, `SHA256SUMS` and `source-provenance.json` are the exact
prepared release content; the latter two were uploaded beside `artifact.zip`.
`retention-observation.json` records the actual preservation scope. GitHub's
connector supports artifact metadata but has no release-creation tool, so the
existing `gh` CLI created this reversible draft with explicit historical target,
prerelease status and `--latest=false`.

This removes dependence on the Actions artifact's three-day retention for an
authenticated restoration. Public distribution, full external-tool bootstrap,
fresh native engine/component builds, Next regressions and promotion remain
open. No component, guest, Next server or build ran for this retention step.
