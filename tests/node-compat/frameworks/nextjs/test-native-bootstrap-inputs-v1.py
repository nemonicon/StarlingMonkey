#!/usr/bin/env python3
"""Finite metadata DATA checks; no acquisition, extraction, tools or target actions."""
import ast
import copy
import hashlib
import importlib.util
import json
import pathlib
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("bootstrap_check", HERE / "check-native-bootstrap-inputs-v1.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def main():
    original = json.loads(module.MANIFEST.read_text())
    result = module.validate(original)
    assert result["metadataValidated"] and not result["cleanMachineRestorationProved"]
    cases = []

    def reject(name, mutate):
        value = copy.deepcopy(original)
        mutate(value)
        try:
            module.validate(value)
        except ValueError:
            cases.append(name)
        else:
            raise AssertionError("accepted invalid metadata: " + name)

    reject("build-claim", lambda d: d["scope"].__setitem__("full825NativeBuildExecuted", True))
    reject("restore-claim", lambda d: d["scope"].__setitem__("cleanMachineRestoreProved", True))
    reject("signed-url", lambda d: d["artifacts"][0]["acquisition"].__setitem__("url", "https://example.com/archive?token=not-a-real-token"))
    reject("credential-url", lambda d: d["artifacts"][0]["acquisition"].__setitem__("url", "https://placeholder@example.com/archive"))
    reject("source-traversal", lambda d: d["sourceRecords"]["materializer"].__setitem__("path", "../materialize.py"))
    reject("source-hash", lambda d: d["sourceRecords"]["materializer"].__setitem__("sha256", "0" * 64))
    reject("role-count-projection", lambda d: d["generation"]["counts"].__setitem__("build-support", 386))
    reject("duplicate-artifact", lambda d: d["artifacts"].append(d["artifacts"][0]))
    reject("wrong-zip", lambda d: d["artifacts"][0].__setitem__("sha256", "0" * 64))
    reject("public-draft-claim", lambda d: d["artifacts"][0]["acquisition"]["authenticatedMirror"].__setitem__("published", True))
    reject("mirror-roundtrip-claim", lambda d: d["artifacts"][0]["acquisition"]["authenticatedMirror"].__setitem__("remoteRoundTripVerified", True))
    reject("unknown-container", lambda d: d["artifacts"][1]["acquisition"].__setitem__("containerArtifact", "missing"))
    reject("tar-traversal", lambda d: d["artifacts"][1]["acquisition"].__setitem__("member", "../archive.tar.gz"))
    reject("final-lock-mutated", lambda d: d["cargo84"]["packages"][0].__setitem__("version", "99.0.0"))
    reject("icu-feature-removed", lambda d: d["cargo84"]["icuCapiFeatures"].pop())
    reject("vendor-checksum-omitted", lambda d: d["cargo84"]["checksumMembers"].pop())
    reject("registry-count", lambda d: d["cargo84"].__setitem__("registryPackages", 76))
    reject("vendor-files-count", lambda d: d["cargo84"].__setitem__("vendorSourceFiles", 2354))
    reject("unlocked-npm", lambda d: d["packaging"]["npmPackages"][0].__setitem__("integrity", ""))
    reject("npm-transport-row-substitution", lambda d: d["packaging"]["npmPackages"][0].__setitem__("resolved", "https://registry.npmjs.org/incorrect/-/incorrect-0.0.0.tgz"))
    optional_index = next(i for i, row in enumerate(original["packaging"]["npmPackages"])
                          if row.get("optional") is True)
    reject("npm-boolean-is-not-integer", lambda d:
           d["packaging"]["npmPackages"][optional_index].__setitem__("optional", 1))
    reject("private-package-is-public-npm", lambda d: d["packaging"]["packageEntry"].__setitem__("sha256", "0" * 64))
    reject("mixed-rust-roles", lambda d: d["officialRustComponentMetadata"].reverse())
    reject("unobserved-rust-payload", lambda d: d["officialRustComponentMetadata"][0]["components"][0].__setitem__("payloadVerified", True))
    reject("missing-restore-step", lambda d: d["restorationOrder"].pop())
    # Every payload pin must reach an actual retained witness, even when the
    # release API supplies no published digest. No private payload is opened.
    for index, row in enumerate(original["artifacts"]):
        reject("artifact-witness-" + row["id"],
               lambda d, i=index: d["artifacts"][i].__setitem__("sha256", "0" * 64))
    with tempfile.TemporaryDirectory(prefix="bootstrap-metadata-test-") as tmp:
        path = pathlib.Path(tmp).resolve() / "payload.txt"
        content = b"small owned DATA fixture\n"
        path.write_bytes(content)
        row = {"sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content)}
        assert module.verify_file(path, row) == row
        try:
            module.verify_file(path, {**row, "sha256": "0" * 64})
        except ValueError:
            cases.append("explicit-local-wrong-bytes")
        else:
            raise AssertionError("local mismatch accepted")
    tree = ast.parse((HERE / "check-native-bootstrap-inputs-v1.py").read_text())
    imported = {n.names[0].name for n in ast.walk(tree) if isinstance(n, ast.Import)}
    assert "subprocess" not in imported and "urllib.request" not in imported
    print(json.dumps({"metadataPositive": result, "refusalCases": cases,
                      "refusalCount": len(cases), "tinyLocalPositive": True,
                      "checkerAstParsed": True, "toolOrNetworkOrTargetActions": False}, indent=2))


if __name__ == "__main__":
    main()
