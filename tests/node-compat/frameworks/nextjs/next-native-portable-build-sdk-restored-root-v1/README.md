# Full native build after exact SDK directory restoration

The first V3 build admission failed before WORK creation or compilation: its
WASI SDK inventory was missing two empty directories. The original issued
authority, terminal1, stderr and failed observation remain unchanged.

`sdk-directory-restoration.json` records the exact repair. The pinned SDK
archive and old inventory both declare only mode0755 empty `include/c++` and
`include/c++/v1` directories in that subtree. All common entries match; no
payload file, inventory or held Source changed. Root restored those two
directories and the unchanged authenticator now accepts all ten tool trees.

This fresh unissued authority differs from the prior draft only in WORK path
and provenance prose. The launcher differs only in its concrete draft digest;
all operational functions, Source d434, Cargo selection, tool pins, disk guards,
deadlines and prohibited actions remain unchanged. It executes in its own real
Source context, with no module/global rebinding. No automatic retry or failure
filter is introduced. Any new build must retain its own original ownership and
complete actual compilation evidence. This preparation alone proves no engine
or guest result.

The new build completes with exit0 and passes the coordinated independent
[actual build DATA review](actual-build-review.json), SHA6638fc6c…/14,274 bytes.
All825 final copies match, the actual compile database has80 native TUs
(79 C++/1 C) plus one separate embedding compile, and all1,078 fresh link-input
descriptors match. Six phases and the outer owner finish raw0/clean. All1,825
protected file references and ten whole current trees/15,766 entries remain
unchanged. The original SDK failure remains preserved.

New engine02a6601d… is31,324,563 bytes; actual full metadata9e960c41… is
4,877,968 bytes. This verifies a full native build using the pinned previously
built SpiderMonkey/ICU distribution; it does not claim SpiderMonkey itself was
rebuilt here. No component, ordinary engine export, host instantiation, runtime
acceptance or production promotion follows from this build DATA gate.
