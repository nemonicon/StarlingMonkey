#!/usr/bin/env python3
"""Read-only metadata check, Python >=3.11. Never downloads, extracts or runs tools."""
import argparse
import hashlib
import json
import pathlib
import re
import stat
import tarfile
import tomllib
import urllib.parse

HERE = pathlib.Path(__file__).resolve().parent
REPOSITORY = HERE.parents[3]
MANIFEST = HERE / "native-bootstrap-inputs-v1.json"
SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def require(condition, detail):
    if not condition:
        raise ValueError(detail)


def relative_path(value):
    require(isinstance(value, str), "relative path must be text")
    p = pathlib.PurePosixPath(value)
    require(not p.is_absolute() and p.as_posix() == value and
            value not in ("", ".") and ".." not in p.parts,
            "unsafe/noncanonical relative path: " + value)
    return p


def descriptor(value):
    require(isinstance(value, dict) and isinstance(value.get("sha256"), str) and
            SHA256.fullmatch(value["sha256"]) and
            type(value.get("bytes")) is int and value["bytes"] >= 0,
            "invalid hash/size descriptor")


def digest_file(path):
    # Streaming only; optional local verification can include a large archive.
    h = hashlib.sha256()
    count = 0
    with path.open("rb") as stream:
        while True:
            block = stream.read(1024 * 1024)
            if not block:
                break
            count += len(block)
            h.update(block)
    return {"sha256": h.hexdigest(), "bytes": count}


def verify_file(path, expected):
    descriptor(expected)
    absolute = path.absolute()
    require(absolute.resolve(strict=True) == absolute,
            "file must have a canonical path without symlink components: " + str(path))
    before = path.stat()
    require(stat.S_ISREG(before.st_mode), "not a regular file: " + str(path))
    actual = digest_file(path)
    after = path.stat()
    require((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns,
             before.st_ctime_ns) ==
            (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns,
             after.st_ctime_ns), "file changed while reading: " + str(path))
    require(all(actual[k] == expected[k] for k in actual),
            "hash/size mismatch: " + str(path))
    return actual


def urls_are_stable(value):
    if isinstance(value, dict):
        for item in value.values():
            urls_are_stable(item)
    elif isinstance(value, list):
        for item in value:
            urls_are_stable(item)
    elif isinstance(value, str) and value.startswith(("http://", "https://")):
        url = urllib.parse.urlsplit(value)
        require(url.scheme == "https" and url.netloc and not url.username and
                not url.password and not url.query,
                "only stable HTTPS URLs without credentials/query: " + value)


def package_rows(packages):
    fields = ("name", "version", "source", "checksum")
    return [{k: row[k] for k in fields if k in row} for row in packages]


def validate(data, repository=REPOSITORY):
    require(data["schemaVersion"] == 1 and data["state"] ==
            "NATIVE_BOOTSTRAP_ACQUISITION_CHECK_MANIFEST_SOURCE_ONLY_V1", "schema/state")
    scope = data["scope"]
    require(scope["metadataOnly"] is True and
            all(scope[k] is False for k in ("cleanMachineRestoreProved",
                "full825NativeBuildExecuted", "checkerAcquiresOrExtractsOrExecutesTools",
                "unconstrainedCargoOrNpmResolutionAllowed")), "metadata-only scope")
    urls_are_stable(data)
    records = data["sourceRecords"]
    require(len({r["path"] for r in records.values()}) == len(records), "duplicate record path")
    documents = {}
    for key, row in records.items():
        p = repository / relative_path(row["path"])
        verify_file(p, row)
        if p.suffix == ".json":
            documents[key] = json.loads(p.read_text())
    selection = documents["portableSourceSelection"]
    generation = data["generation"]
    require(generation["counts"] == selection["expectedCounts"] ==
            {"native-policy-source": 435, "build-support": 387,
             "componentize-embedding": 3}, "source role counts")
    require(generation["files"] == selection["expectedFiles"] == 825 and
            generation["bytes"] == selection["expectedBytes"] and
            generation["roleContentSha256"] == selection["roleContentSha256"], "source identity")
    artifacts = {a["id"]: a for a in data["artifacts"]}
    require(len(artifacts) == len(data["artifacts"]), "duplicate artifact id")
    for row in artifacts.values():
        descriptor(row)
        acquisition = row["acquisition"]
        if "containerArtifact" in acquisition:
            require(acquisition["containerArtifact"] in artifacts, "unknown container")
            relative_path(acquisition["member"])
        if "record" in acquisition:
            require(acquisition["record"] in records, "unknown acquisition record")
    native = documents["nativeAuthority"]
    ci = data["publicCiMetadata"]["artifacts"]
    require(len(ci) == 1, "one selected CI artifact")
    tool_plan = documents["nativeToolPlan"]
    constructor = documents["constructorPlan"]
    packager_tools = documents["packagerToolCut"]
    node_acquisition = documents["nodeAcquisition"]
    public_source = documents["componentizeSourceOrigin"]
    witnesses = {
        "sm-patched-ci-zip": {"sha256": ci[0]["digest"].removeprefix("sha256:"),
                              "bytes": ci[0]["size_in_bytes"]},
        "sm-distribution-tar": documents["patchedCiReview"]["binaryAudit"][0],
        "sm-ffi-tar": documents["patchedCiReview"]["binaryAudit"][1],
        "openssl-archive": next(r["source"] for r in tool_plan["archiveCopies"]
                                if r["role"] == "openssl"),
        "cpm-module": tool_plan["cpmModule"],
        "native-cbindgen": tool_plan["cbindgen"],
        "node22-archive": node_acquisition["archive"],
        "working-node-executable": node_acquisition["existingNode"],
        "componentize-source-archive": public_source["originalCapturedArchive"],
        "private-splicer61685": constructor["pins"]["privateSplicer"],
        "selected-adapter-d30": constructor["pins"]["adapter"],
        "adapter-input988": next(r for r in documents["adapterInputReferences"]["files"]
                                 if r["path"].endswith("/preview1-adapter-release/wasi_snapshot_preview1.wasm")),
    }
    for ident in ("wasi-sdk", "binaryen", "wasm-tools", "wasmtime", "weval"):
        witnesses[ident + "-archive"] = native["reusedTrees"][ident]["archive"]
    for ident, field in (("sm-static-library", "smLibrary"),
                         ("sm-savedframe-header", "smSavedFrameHeader"),
                         ("sm-intl-header", "smConfigHeader"),
                         ("sm-confdefs-header", "smConfdefsHeader")):
        witnesses[ident] = native[field]
    for tool in ("cargo", "rustc"):
        witnesses["engine-" + tool] = native[tool]
        witnesses["packager-" + tool] = packager_tools[tool]
    require(set(witnesses) == set(artifacts), "complete artifact witness map")
    for ident, witness in witnesses.items():
        require(all(artifacts[ident][k] == witness[k] for k in ("sha256", "bytes")),
                "retained payload hash/size witness: " + ident)
    for ident, field in (("sm-static-library", "smLibrary"),
                         ("sm-savedframe-header", "smSavedFrameHeader"),
                         ("sm-intl-header", "smConfigHeader"),
                         ("sm-confdefs-header", "smConfdefsHeader"),
                         ("engine-cargo", "cargo"), ("engine-rustc", "rustc")):
        require(all(artifacts[ident][k] == native[field][k] for k in ("sha256", "bytes")),
                "native authority identity: " + ident)
    ci = data["publicCiMetadata"]["artifacts"]
    require(len(ci) == 1 and ci[0]["id"] == 13536973897 and
            ci[0]["workflow_run"]["id"] == 42281671898 and
            ci[0]["workflow_run"]["head_sha"] == data["spiderMonkey"]["ciHead"], "CI identity")
    archive = artifacts["sm-patched-ci-zip"]
    require(ci[0]["digest"] == "sha256:" + archive["sha256"] and
            ci[0]["size_in_bytes"] == archive["bytes"], "CI ZIP identity")
    release = documents["draftMirror"]
    mirror = archive["acquisition"]["authenticatedMirror"]
    asset = next(a for a in release["assets"] if a["id"] == mirror["assetId"])
    require(release["id"] == mirror["releaseId"] == 437352699 and
            release["draft"] is True and release["prerelease"] is True and
            release["published_at"] is None and
            release["target_commitish"] == data["spiderMonkey"]["ciHead"], "draft release identity")
    require(asset["id"] == 719685339 and asset["state"] == "uploaded" and
            asset["url"] == mirror["apiUrl"] and
            asset["digest"] == mirror["serverDigest"] == "sha256:" + archive["sha256"] and
            asset["size"] == archive["bytes"] and
            mirror["requiresRepositoryAuthentication"] is True and
            mirror["draft"] is True and mirror["published"] is False and
            mirror["remoteRoundTripVerified"] is False, "authenticated mirror scope")
    for ident, binary in zip(("sm-distribution-tar", "sm-ffi-tar"),
                             documents["patchedCiReview"]["binaryAudit"]):
        require(all(artifacts[ident][k] == binary[k] for k in ("sha256", "bytes")),
                "nested archive identity")
    for ident in ("wasi-sdk", "binaryen", "wasm-tools", "wasmtime", "weval", "openssl", "cpm"):
        row = artifacts[ident + ("-module" if ident == "cpm" else "-archive")]
        release = next(r for r in data["publicReleaseMetadata"] if r["id"] == ident)
        asset = next(a for a in release["assets"] if a["id"] == row["acquisition"]["assetId"])
        require(asset["size"] == row["bytes"] and asset["apiUrl"] == row["acquisition"]["apiUrl"] and
                asset["browserDownloadUrl"] == row["acquisition"]["url"] and
                asset["digest"] == row["acquisition"]["publishedDigest"] and
                asset["digest"] in (None, "sha256:" + row["sha256"]), "release asset identity")
    origin = documents["componentizeSourceOrigin"]
    source = artifacts["componentize-source-archive"]
    require(origin["originalAndPublicArchiveBytesEqual"] is True and
            source["acquisition"]["url"] == origin["acquisition"]["argv"][-1] and
            all(source[k] == origin["acquisition"]["archive"][k] for k in ("sha256", "bytes")) and
            source["regularFiles"] == origin["tar"]["regularFiles"] == 270,
            "public Componentize byte acquisition")
    ffi = documents["ffiManifest"]
    require(data["ffi"]["commit"] == ffi["commit"] and
            data["ffi"]["rootTreeSha1"] == ffi["rootTreeSha1"] and
            data["ffi"]["roots"] == ffi["selectedRoots"] and
            data["ffi"]["files"] == ffi["expectedFileCount"] == 1127 and
            data["ffi"]["bytes"] == ffi["expectedSourceBytes"] == 11364714,
            "four exact FFI source trees")
    cargo = data["cargo84"]
    index = {r["path"]: r for r in documents["cargoPayloadIndex"]["entries"]}
    require(len(index) == len(documents["cargoPayloadIndex"]["entries"]), "duplicate Cargo payload")
    bundle = repository / records["cargoTextBundle"]["path"]
    selected = [cargo["lock"], *cargo["checksumMembers"]]
    with tarfile.open(bundle, "r:gz") as archive_file:
        names = archive_file.getnames()
        require(len(names) == len(set(names)) == len(index) and set(names) == set(index),
                "Cargo text bundle membership")
        contents = {}
        for row in selected:
            name = row.get("member", row.get("path"))
            relative_path(name)
            require(name in index and all(row[k] == index[name][k] for k in ("sha256", "bytes")),
                    "Cargo member descriptor")
            member = archive_file.getmember(name)
            require(member.isfile() and member.size == row["bytes"] <= 2 * 1024 * 1024,
                    "Cargo selected member bounds")
            raw = archive_file.extractfile(member).read()
            require(hashlib.sha256(raw).hexdigest() == row["sha256"], "Cargo text member hash")
            contents[name] = raw
        locked = tomllib.loads(contents[cargo["lock"]["member"]].decode())["package"]
        aggregate = tomllib.loads(archive_file.extractfile("v2/project/Cargo.toml").read().decode())
    require(package_rows(locked) == cargo["packages"] and len(locked) == cargo["packageCount"] == 84,
            "exact84 locked packages")
    counts = [sum(p.get("source", "").startswith(prefix) for p in locked) for prefix in ("registry+", "git+")]
    require(counts == [cargo["registryPackages"], cargo["gitPackages"]] == [75, 1] and
            len(locked) - sum(counts) == cargo["pathPackages"] == 8, "package source counts")
    require(len(cargo["checksumMembers"]) == cargo["vendorPackages"] == 76 and
            len({r["path"] for r in cargo["checksumMembers"]}) == 76, "vendor checksum metadata")
    checksums = [json.loads(contents[r["path"]]) for r in cargo["checksumMembers"]]
    audit = documents["cargoOfflineAudit"]
    require(sum(len(r["files"]) for r in checksums) == cargo["vendorSourceFiles"] == 2278 and
            sum(r.get("package") is None for r in checksums) == 1 and
            audit["vendorChecksums"] == {"packages": 76, "files": 2278,
                "bytes": cargo["vendorSourceBytes"], "allRecordedChecksumsMatch": True},
            "actual vendor checksum evidence (not current payload verification)")
    require(cargo["rootDependencies"] == list(aggregate["dependencies"]) and
            cargo["icuCapiFeatures"] == aggregate["dependencies"]["icu_capi"]["features"] ==
            ["any_provider", "compiled_data", "segmenter", "calendar"], "actual aggregate feature selection")
    packaging = data["packaging"]
    packager_lock = tomllib.loads((repository / records["packagerCargoLock"]["path"]).read_text())
    require(package_rows(packager_lock["package"]) == packaging["cargoPackages"], "packager locked graph")
    for row in packaging["npmPackages"]:
        require(row["resolved"].startswith("https://registry.npmjs.org/") and
                row["integrity"].startswith("sha512-"), "fixed npm transport/integrity")
    require(len({p["lockKey"] for p in packaging["npmPackages"]}) == len(packaging["npmPackages"]),
            "duplicate npm row")
    tool_cut = documents["packagerToolCut"]
    hidden_lock = next(r["descriptor"] for r in tool_cut["jsToolchain"]["files"]
                       if r["relativePath"] == "node_modules/.package-lock.json")
    require(packaging["npmLock"] == hidden_lock, "historical npm lock descriptor")
    lock_record = records[packaging["npmInstalledLockRecord"]]
    lock_provenance = documents[packaging["npmInstalledLockProvenanceRecord"]]
    require(all(lock_record[k] == hidden_lock[k] for k in ("sha256", "bytes")) and
            lock_provenance["original"] == hidden_lock and
            lock_provenance["retained"] == {
                "path": pathlib.PurePosixPath(lock_record["path"]).name,
                "sha256": hidden_lock["sha256"], "bytes": hidden_lock["bytes"]} and
            lock_provenance["state"] == "CAPTURED_INSTALLED_NPM_LOCK_DATA_NOT_NPM_CI_ROOT_LOCK" and
            lock_provenance["npmCiRootLock"] is False and
            lock_provenance["privateGeneratedPackageRebuilt"] is False,
            "retained installed-state npm lock provenance")
    installed_lock = documents[packaging["npmInstalledLockRecord"]]
    npm_fields = ("version", "resolved", "integrity", "os", "cpu", "optional")
    npm_rows = [{"lockKey": key, **{f: row[f] for f in npm_fields if f in row}}
                for key, row in installed_lock["packages"].items() if "resolved" in row]
    require(json.dumps(npm_rows, sort_keys=True, separators=(",", ":")) ==
            json.dumps(packaging["npmPackages"], sort_keys=True, separators=(",", ":")) and len(npm_rows) ==
            lock_provenance["packageRows"] == 78,
            "exact normalized78 installed-state npm transport rows")
    for name, version in packaging["versions"].items():
        rows = [r for r in packaging["npmPackages"]
                if r["lockKey"].endswith("/node_modules/@bytecodealliance/" + name)]
        require(len(rows) == 1 and rows[0]["version"] == version, "selected npm version")
    constructor = documents["constructorPlan"]
    require(packaging["packageInventory"] == constructor["packageInventory"] and
            packaging["packageEntry"] == constructor["pins"]["packageEntry"] and
            all(artifacts["private-splicer61685"][k] ==
                constructor["pins"]["privateSplicer"][k] for k in ("sha256", "bytes")) and
            all(artifacts["selected-adapter-d30"][k] ==
                constructor["pins"]["adapter"][k] for k in ("sha256", "bytes")),
            "working private constructor package/adapter pins")
    require([r["version"] for r in data["officialRustComponentMetadata"]] == ["1.88.0", "1.96.1"],
            "separate engine/packager toolchains")
    for row in data["officialRustComponentMetadata"]:
        require(SHA256.fullmatch(row["metadataSha256"]) and len(row["components"]) == 4,
                "Rust official component metadata")
        for component in row["components"]:
            require(SHA256.fullmatch(component["sha256"]) and component["bytes"] is None and
                    component["payloadVerified"] is False and component["available"] is True,
                    "Rust metadata is not a downloaded payload")
    require([r["step"] for r in data["restorationOrder"]] == list(range(1, 9)), "restoration order")
    require(len({r["id"] for r in data["remainingGaps"]}) == len(data["remainingGaps"]) >= 4,
            "explicit remaining gaps")
    return {"metadataValidated": True, "sourceRecordsVerified": len(records),
            "artifactPins": len(artifacts), "aggregateLockedPackages": len(locked),
            "vendorChecksumMetadataRecords": 76, "cleanMachineRestorationProved": False,
            "payloadsAcquiredExtractedOrToolsExecuted": False,
            "availabilityReprobed": False,
            "actionsArtifactExpiresAt": ci[0]["expires_at"],
            "draftMirrorRequiresAuthentication": True,
            "npmTransportRowsRederived": len(packaging["npmPackages"]),
            "npmTransportRowsRederivedFromRetainedInstalledLock": True,
            "npmCiOrPrivatePackageRebuildProved": False,
            "officialRustComponentRowsReported": 8,
            "officialRustChannelPayloadRehashed": False,
            "officialRustArchivePayloadsVerified": False,
            "remainingGaps": [r["id"] for r in data["remainingGaps"]]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=pathlib.Path, default=MANIFEST)
    parser.add_argument("--repository", type=pathlib.Path, default=REPOSITORY)
    parser.add_argument("--plan", action="store_true", help="also print finite restoration order")
    parser.add_argument("--verify-local", action="append", default=[], metavar="ID=CANONICAL_FILE",
                        help="explicitly hash an already-owned payload; never acquire or extract")
    args = parser.parse_args()
    data = json.loads(args.manifest.read_text())
    result = validate(data, args.repository)
    artifacts = {a["id"]: a for a in data["artifacts"]}
    result["localPayloadsVerified"] = []
    for spec in args.verify_local:
        ident, separator, value = spec.partition("=")
        require(separator and ident in artifacts and value, "use --verify-local ID=CANONICAL_FILE")
        verify_file(pathlib.Path(value), artifacts[ident])
        result["localPayloadsVerified"].append(ident)
    if args.plan:
        result["restorationOrder"] = data["restorationOrder"]
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
