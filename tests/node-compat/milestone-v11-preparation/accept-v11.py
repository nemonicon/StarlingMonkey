#!/usr/bin/env python3
"""Verify bounded v11 evidence read-only; --apply requires the reviewed plan SHA."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shlex
import shutil
import stat

REPO = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BASE = Path("/tmp/starling-node-compat/foundations-v11")
FREEZE = BASE / "native-freeze"
TESTS = REPO / "tests/node-compat"
FOCUSED = TESTS / "foundation-add-abort/production-native-m0.11"
ADOPTION = TESTS / "foundation-alloc-unsafe/production-adoption-m0.11"
DESTINATION = TESTS / "milestones/foundations-v11"
STAGE = DESTINATION.with_name(".foundations-v11-staging")
RECIPE = "354cbc8c5317bf14f022fd14a9687e382b99c2141135629b56bb541ef6308754"
CORE = "sm-node-22.14.0-m0.11"
MACRO = "-DNODE_COMPAT_EVENTS_ADD_ABORT_LISTENER=1"
HTTP_IMPORTS = sorted(["wasi:http/types@0.2.10", "wasi:io/error@0.2.10", "wasi:io/poll@0.2.10",
 "wasi:io/streams@0.2.10", "wasi:random/random@0.2.10", "wasi:clocks/monotonic-clock@0.2.10"])
JOBS = {"core", "allocator", "stream-web", "optional", "strict-sync", "strict-runtime", "strict-late", "strict-callbacks"}
BINARY_SUFFIXES = {".wasm", ".cwasm", ".o", ".obj", ".a", ".so", ".dylib", ".exe", ".pyc", ".zip", ".gz", ".tar", ".bin"}
SKIP_DIRS = {"node_modules", "__pycache__", ".git", "target"}
SOURCE_BINARY_ASSETS = {}
# Byte-equivalent utilities from the reviewed v10 producer (92c0c97d...), no import/execute of it.
def sha(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()

def json_file(path):
    assert_regular(path)
    return json.loads(Path(path).read_text())

def assert_regular(path):
    path = Path(path)
    value = path.lstat()
    assert stat.S_ISREG(value.st_mode) and not stat.S_ISLNK(value.st_mode), path
    return value

def no_link_components(path, root):
    path, root = Path(path), Path(root)
    relative = path.relative_to(root)
    cursor = root
    assert not cursor.is_symlink(), cursor
    for part in relative.parts:
        cursor /= part
        assert not cursor.is_symlink(), cursor

def binary(path):
    path = Path(path)
    if path.suffix.lower() in BINARY_SUFFIXES:
        return True
    with open(path, 'rb') as stream:
        magic = stream.read(4)
    return magic in {b'\0asm', b'\x7fELF', b'\xcf\xfa\xed\xfe', b'\xce\xfa\xed\xfe', b'\xfe\xed\xfa\xcf', b'MZ\x90\0'}

def entries_without_links(root, omitted):
    root = Path(root)
    assert root.is_dir() and not root.is_symlink(), root
    for parent, directories, names in os.walk(root, followlinks=False):
        retained = []
        for name in sorted(directories):
            path = Path(parent) / name
            if path.is_symlink() or name in SKIP_DIRS:
                omitted.append({'path': str(path), 'reason': 'symlink-or-generated-dependency-directory'})
            else:
                retained.append(name)
        directories[:] = retained
        for name in sorted(names):
            path = Path(parent) / name
            value = path.lstat()
            if not stat.S_ISREG(value.st_mode) or stat.S_ISLNK(value.st_mode):
                omitted.append({'path': str(path), 'reason': 'not-a-regular-nonsymlink-file'})
            else:
                yield path

def fatal_assertions(value):
    assert value['jcoChild']['status'] == 0
    assert 'EXPECTED_FATAL_DISCARD' in value['jcoChild']['stdout']
    assert value['wasmtime']['status'] != 0
    assert 'unreachable' in value['wasmtime']['stderr']

load = json_file

def pinned_file(entry):
    assert entry and entry.get('path') and entry.get('sha256'), 'Final evidence pin missing'
    path = Path(entry['path'])
    if not path.is_absolute():
        path = REPO / path
    assert path.is_file() and not path.is_symlink()
    assert sha(path) == entry['sha256'], path
    return load(path)

def validate_native(pins):
    """Verify three new configurations; never add historical Events-OFF here."""
    assert set(pins['engines']) == {'off-foundations', 'runtime-foundations', 'gc-foundations'}
    engines = []
    for label, expected in pins['engines'].items():
        path = FREEZE / (label + '.engine.wasm')
        metadata = load(str(path) + '.build.json')
        assert sha(path) == metadata['engineSha256'] == expected['sha256']
        assert sha(str(path) + '.build.json') == expected['metadataSha256']
        assert metadata['buildRecipeSha256'] == sha(REPO / 'tests/node-compat/build-engine.sh') == RECIPE
        assert len(metadata['sourceManifest']) == 304
        assert len(metadata['componentizeSourceManifest']) == 3
        assert metadata['observedCMakeOptions']['CMAKE_BUILD_TYPE'] == 'Release'
        assert metadata['observedCMakeOptions']['WEVAL'] == 'OFF'
        assert metadata['observedCMakeOptions']['USE_WASM_OPT'] == 'ON'
        assert metadata['observedCMakeOptions']['NODE_COMPAT_LOCKED_RUST'] == 'ON'
        for field in ['profileEnabled', 'pathEnabled', 'eventsEnabled', 'stringDecoderEnabled',
                      'assertEnabled', 'querystringEnabled', 'utilEnabled', 'streamWebEnabled']:
            assert metadata[field] is True, field
        assert metadata['gcStress'] is (label == 'gc-foundations') and not metadata['oomTesting']
        assert metadata['entropyPolicy'] == ('runtime-only' if label == 'runtime-foundations' else 'off')
        assert metadata['protectedAbortListenerEnabled'] and metadata['strictInitialization']
        assert metadata['strictEventExceptionPolicy']['version'] == 'sm-uncaught-event-v3-protected-abort-v2'
        assert metadata['protectedAbortListenerPolicy']['patchSha256'] == '0d314f14e1eba2ed5ff1eed592697d5f6fab2be37d9568281ffec43864e2c3a1'
        assert not metadata['wptSupportEnabled'] and not metadata['debuggerEnabled']
        assert metadata['sourceInputsCapturedBeforeBuild'] and metadata['componentizeSourcesCapturedBeforeBuild']
        assert metadata['buildRecipeCheckedBeforeAndAfterBuild'] and metadata['generatedRustProject']['cargoBuildLocked']
        core = next(item for item in metadata['selectedModuleManifests']
                    if item['path'] == 'builtins/node-compat/export-manifest.node-v22.14.0.json')
        assert core['profileVersion'] == CORE
        for item in metadata['sourceManifest']:
            assert not Path(item['path']).is_absolute() and '..' not in Path(item['path']).parts
            assert sha(REPO / item['path']) == sha(FREEZE / 'source' / item['path']) == item['sha256']
        for item in metadata['componentizeSourceManifest']:
            assert sha(FREEZE / 'componentize-source' / item['path']) == item['sha256']
        for path, value in pins['coreSourceSha256'].items():
            assert next(item['sha256'] for item in metadata['sourceManifest'] if item['path'] == path) == value
        assert sha(FREEZE / (label + '-CMakeCache.txt')) == metadata['cmakeCacheSha256']
        assert sha(FREEZE / (label + '-compile_commands.json')) == metadata['compileCommandsSha256']
        commands = load(FREEZE / (label + '-compile_commands.json'))
        cpp = [item['path'] for item in metadata['sourceManifest']
               if item['path'].endswith('.cpp') and item['path'].startswith(('builtins/', 'runtime/'))]
        layout = [item['command'] for item in commands
                  if any(item['file'].endswith('/' + path) for path in cpp)]
        assert len(layout) == 60 and layout == metadata['protectedAbortListenerPolicy']['actualLayoutCompileCommands']
        embedding = metadata['actualEmbeddingCompileCommands']
        assert len(embedding) == 1 and all(MACRO in shlex.split(command) for command in layout + embedding)
        engines.append(metadata)
    assert all(item['sourceManifest'] == engines[0]['sourceManifest'] for item in engines)
    assert all(item['componentizeSourceManifest'] == engines[0]['componentizeSourceManifest'] for item in engines)
    old = load(REPO / 'tests/node-compat/milestones/foundations-v10/off-foundations.engine.wasm.build.json')
    expected = {item['path']: item['sha256'] for item in old['sourceManifest']}
    assert len(pins['nativeChangesFromV10']) == 4
    for item in pins['nativeChangesFromV10']:
        assert expected[item['path']] == item['before']
        expected[item['path']] = item['after']
    assert {item['path']: item['sha256'] for item in engines[0]['sourceManifest']} == expected
    return engines

def validate_release(entry, off_sha):
    report = pinned_file(entry)
    assert report['state'] == 'passed' and len(report['jobs']) == 8
    assert {job['name'] for job in report['jobs']} == JOBS
    for job in report['jobs']:
        assert job['code'] == 0 and job['signal'] is None
        assert sha(job['reportPath']) == job['reportSha256']
        assert sha(job['logPath']) == job['logSha256']
        assert sha(job['runner']) == job['runnerSha256'] and job['emittedImports'] == []
        if job['name'] != 'optional':
            assert load(job['reportPath'])['engineSha256'] == off_sha
    assert sum(job['finalComponentAudits'] for job in report['jobs'] if job['name'].startswith('strict-')) == 24
    # Finalization must also authenticate v3's five reused successful reports,
    # six optional module reports/ten audits, and actual per-job source snapshots.
    return report

def validate_reports(pins):
    assert not DESTINATION.exists() and not STAGE.exists(), "Never overwrite an archive or failed stage"
    required = ["focusedOff", "focusedRuntime", "focusedGc", "callbackReturn", "focusedReceipt",
                "httpAudit", "wasmtimeHttp", "wasmcloudHttp", "httpSummary", "httpIndex"]
    assert all(pins["finalEvidence"].get(key) for key in required), "Final HTTP/report pins are pending"
    engines = validate_native(pins)
    by_label = {key: value for key, value in pins["engines"].items()}
    files, reports = {}, {}
    def register(name, entry):
        value = pinned_file(entry)
        files[name] = Path(entry["path"])
        if not files[name].is_absolute():
            files[name] = REPO / files[name]
        reports[name] = value
        return value
    for name, entry in pins["knownReports"].items():
        if entry:
            register(name, entry)
    for name in required:
        register(name, pins["finalEvidence"][name])
    release = validate_release(pins["knownReports"]["releaseEight"], by_label["off-foundations"]["sha256"])
    assert sum(bool(job.get("reusedVerifiedPass")) for job in release["jobs"]) == 5
    assert {job["name"] for job in release["jobs"] if not job.get("reusedVerifiedPass")} == {
        "strict-runtime", "strict-late", "strict-callbacks"}
    prior = release["reusedEvidence"]
    assert sha(prior["priorPath"]) == prior["priorIndexSha256"] and prior["priorState"] == "failed"
    assert [item["name"] for item in prior["failedAttempts"]] == ["strict-runtime"]
    for job in release["jobs"]:
        files["release-" + job["name"]] = Path(job["reportPath"])
        reports["release-" + job["name"]] = load(job["reportPath"])
    optional = reports["release-optional"]
    assert optional["state"] == "passed" and len(optional["modules"]) == 6
    assert optional["nativeInputsVerifiedBeforeAfter"] and optional["nativeInputs"] == 304
    assert sum(module["finalComponentAudits"] for module in optional["modules"]) == 10
    for module in optional["modules"]:
        assert module["code"] == 0 and module["emittedImports"] == []
        assert sha(module["reportPath"]) == module["reportSha256"]
        files["optional-" + module["name"]] = Path(module["reportPath"])
        reports["optional-" + module["name"]] = load(module["reportPath"])
    allocator_gc = reports["allocatorGc"]
    assert allocator_gc["state"] == "installed-m0.11-ordinary-release-moving-gc-pass"
    assert allocator_gc["engineSha256"] == by_label["gc-foundations"]["sha256"]
    assert allocator_gc["engineReceiptSha256"] == by_label["gc-foundations"]["metadataSha256"]
    assert allocator_gc["coreExpectations"]["coreVersion"] == CORE
    assert allocator_gc["coreExpectations"]["allocUnsafePolicy"] == "zeroed-no-pool-direct-u8-v1"
    assert allocator_gc["sourceFilesVerified"] == 304 and allocator_gc["interfaceAudit"]["emittedImports"] == []
    assert "-DNODE_COMPAT_GC_STRESS=1" in shlex.split(allocator_gc["compileCommand"])
    assert [call["calls"] for call in allocator_gc["calls"]] == [1, 2, 3]
    assert all(call["roundtrips"] == 8 for call in allocator_gc["calls"])
    assert allocator_gc["wasmtime"]["observed"]["roundtrips"] == 8
    focused = reports["focusedReceipt"]
    assert focused["state"] == "BOUNDED_M11_NATIVE_FOCUSED_EVIDENCE_COMPLETE_WITH_CONFIRMED_CALLBACK_RETURN_LIMITATION"
    assert focused["allThreeNativeInputManifestsIdentical"] and focused["all304FrozenAndCurrentSourcesVerified"]
    assert focused["nativeSourceManifest"] == engines[0]["sourceManifest"]
    assert len(focused["engines"]) == 3 and {item["label"] for item in focused["engines"]} == set(by_label)
    assert len(focused["validationSourceFiles"]) == 17
    assert len({item["path"] for item in focused["validationSourceFiles"]}) == 17
    for item in focused["validationSourceFiles"]:
        assert sha(FOCUSED / item["path"]) == sha(FOCUSED / item["saved"]) == item["sha256"]
    assert sha(FOCUSED / "README.md") == focused["readmeSha256"]
    expected_reports = {"native-off-results.json": 8, "native-runtime-results.json": 8,
                        "native-gc-results.json": 2, "callback-return-results.json": 1}
    assert len(focused["reports"]) == 4 and {item["path"] for item in focused["reports"]} == set(expected_reports)
    for item in focused["reports"]:
        assert sha(FOCUSED / item["path"]) == sha(item["externalPath"]) == item["sha256"]
    assert len(focused["components"]) == 19
    assert len({Path(item["path"]).resolve() for item in focused["components"]}) == 19
    for name, number in expected_reports.items():
        assert sum(item["report"] == name for item in focused["components"]) == number
    for item in focused["components"]:
        assert sha(item["path"]) == item["sha256"]
        assert item["emittedImports"] == (["wasi:random/random@0.2.10"]
            if item["report"] == "native-runtime-results.json" else [])
    oracle = load(FOCUSED / "source-freeze/node-results.json")
    for name, label in [("focusedOff", "off-foundations"), ("focusedRuntime", "runtime-foundations")]:
        report = reports[name]
        assert report["state"] == "M11_ORDINARY_NATIVE_ADD_ABORT_LISTENER_PASSED"
        assert report["engineSha256"] == by_label[label]["sha256"]
        assert report["preflight"]["sourceFilesVerified"] == 304 and report["preflight"]["actualLayoutCompileCommands"] == 60
        assert report["preflight"]["coreVersion"] == CORE and report["preflight"]["guardNegativesAllowed"]
        assert report["publicNodeGroups"]["total"] == 29
        assert len(report["initializers"]) == 8 and len(report["fatal"]) == 5
        assert all(item["message"] for item in report["initializers"])
        for group in ["main", "aliases", "benign"]:
            assert [item["calls"] for item in report[group]["calls"]] == [1, 2, 3]
        for observed in report["main"]["calls"] + [report["main"]["freshWasmtime"]["observed"]]:
            for field in ["publicCases", "nestedOnceCases", "receiverCases"]:
                assert observed[field] == oracle[field]
            assert len(observed["namespace"]["names"]) == 16 and observed["namespace"]["defaultNamed"]
            assert len(observed["profileErrors"]["errors"]) == 7 and observed["profileErrors"]["hooks"] == 0
            assert observed["snapshot"]["signalThis"] and observed["snapshot"]["currentTarget"]
        for value in report["fatal"]:
            fatal_assertions(value)
    gc = reports["focusedGc"]
    assert gc["state"] == "M11_RELEASE_MOVING_GC_COMBINED_OWNER_GATE_PASSED"
    assert gc["engineSha256"] == by_label["gc-foundations"]["sha256"]
    assert "-DNODE_COMPAT_GC_STRESS=1" in shlex.split(gc["actualKernelCommand"])
    assert [item["calls"] for item in gc["clean"]["calls"]] == [1, 2, 3]
    for item in gc["clean"]["calls"] + [gc["clean"]["freshWasmtime"]["observed"]]:
        assert item["completed"] == 8 and item["receiver"] and item["contextRestored"]
        assert item["disposalCalls"] == 0 and item["nestedOnceCases"] == oracle["nestedOnceCases"]
    assert "M11_ROOTED_AFTER_8" in gc["initializer"]["message"]
    fatal_assertions(gc["fatal"])
    gap = reports["callbackReturn"]
    assert gap["observationCompleted"] is True and gap["nodeCompatibilityPassed"] is False
    assert gap["node"]["observed"] == {"ordinary": 1, "protectedSignal": 1, "alreadyAborted": 0}
    assert gap["jco"]["observed"] == gap["wasmtime"]["observed"] == {
        "ordinary": 0, "protectedSignal": 0, "alreadyAborted": 0}
    symbol = reports["focusedOff"]["targetSymbolIdentity"]
    assert symbol["node"]["registryKey"] == "nodejs.dispose" and symbol["target"]["registryKey"] is None
    historical = pins["historicalEventsOff"]
    assert historical["historical"] and not historical["newM11Engine"] and not historical["identicalM11SourceManifest"]
    old = pinned_file(historical["report"])
    assert old["state"] == "M10_ACTUAL_EVENTS_OFF_ADMISSION_PASSED" and old["engineSha256"] == historical["engineSha256"]
    assert old["actualLayoutMacro"] == "ABSENT"
    files["historical-m10-events-off"] = Path(historical["report"]["path"])
    audit = reports["httpAudit"]
    seal = reports["httpComponentPins"]
    assert audit["engineSha256"] == by_label["runtime-foundations"]["sha256"]
    assert audit["componentSha256"] == seal["componentSha256"] == pins["httpComponentSha256"]
    assert sha(audit["componentPath"]) == pins["httpComponentSha256"]
    assert audit["componentBytes"] == seal["componentBytes"] == pins["httpComponentBytes"]
    assert sorted(audit["emittedImports"]) == HTTP_IMPORTS
    assert audit["emittedExports"] == ["wasi:http/incoming-handler@0.2.10"]
    assert audit["clockDependency"]["typeOnly"] and audit["clockDependency"]["callableImports"] == []
    assert audit["clockDependency"]["coreClockImports"] == []
    inputs = reports["httpInputs"]
    assert inputs["state"] == "HTTP_V11_INPUTS_FROZEN_BEFORE_PACKAGING" and len(inputs["sourceFiles"]) == 24
    for item in inputs["sourceFiles"]:
        assert sha(REPO / item["path"]) == item["sha256"]
    for name in ["wasmtimeHttp", "wasmcloudHttp"]:
        report = reports[name]
        component_sha = report["component"]["sha256"] if name == "wasmcloudHttp" else report["componentSha256"]
        assert component_sha == pins["httpComponentSha256"] and len(report["responses"]) == 3
        assert report["process"]["stopped"] and report["process"]["exitStatus"] == {"code": 0, "signal": None}
        assert [response["body"]["componentInstanceRequestCount"] for response in report["responses"]] == [1, 1, 1]
        for response in report["responses"]:
            assert response["status"] == 200
            native = response["body"]["native"]
            assert native["coreVersion"] == CORE and native["allocUnsafePolicy"] == "zeroed-no-pool-direct-u8-v1"
            assert native["allocUnsafePrimordialCalls"] == {"integerCalls": 0, "finiteCalls": 0, "truncatedLength": 3}
            foundation = native["foundations"]
            assert foundation["schema"] == 5 and len(foundation["aliases"]["aliases"]) == 14
            for field in ["publicCases", "nestedOnceCases", "receiverCases"]:
                assert foundation["protectedAbort"][field] == oracle[field]
            assert foundation["streamWeb"]["passed"] and foundation["streamWeb"]["iterations"] == 67
    assert reports["wasmcloudHttp"]["host"]["unmodifiedOfficialBinary"]
    assert reports["wasmcloudHttp"]["host"]["version"] == "2.11.0"
    assert sha(reports['wasmcloudHttp']['component']['deployedPath']) == pins['httpComponentSha256']
    assert sha(reports['wasmcloudHttp']['host']['binaryPath']) == reports['wasmcloudHttp']['host']['binarySha256']
    assert reports["httpSummary"]["state"] == "HTTP_V11_BOTH_UNMODIFIED_HOSTS_PASSED"
    assert reports["httpIndex"]["state"] == "HTTP_V11_BOTH_HOSTS_FROZEN_SOURCE_AND_EVIDENCE_INDEX"
    for item in reports["httpIndex"]["files"]:
        assert sha(item["path"]) == item["sha256"]
    admission = reports["sourceAdmission"]
    assert admission['state'] == 'post-application-source-admission-passed'
    assert admission['node'] == 'v22.14.0' and sha(admission['nodePath']) == admission['nodeSha256']
    assert admission['sourceReceiptSha256'] == sha(files['sourceAdoption'])
    expected_checks = {'builtins/node-compat/generate-factories.mjs',
                       'tests/node-compat/module-selection-test.mjs',
                       'tests/node-compat/manifest-test.mjs', 'tests/node-compat/bundle-test.mjs'}
    assert len(admission['checks']) == 4 and {item['script'] for item in admission['checks']} == expected_checks
    for item in admission['checks']:
        assert item['exitCode'] == 0 and sha(REPO / item['script']) == item['scriptSha256']
    selected_check = next(item for item in admission['checks'] if item['script'].endswith('/module-selection-test.mjs'))
    assert selected_check['observed'] == '328 passed; zero failures; build-time manifest/receipt/bundle selection only'
    cow = reports["cowBootstrap"]
    assert cow["state"] == "three-new-raw-artifact-paths-restored-byte-and-metadata-exact"
    assert len(cow["rows"]) == 3 and cow["freeBefore"] == 2040545280
    assert cow["observedFreeDelta"] == 35856384 and cow["inodeCtimeBirthtimePreserved"] is False
    assert all(row["sha256"] == by_label[row["label"]]["sha256"] for row in cow["rows"])
    # Historical source-adoption/build files are provenance, not runtime passes.
    return files, reports, engines, focused, gap

def prepare_plan(files, reports, engines, pins):
    plan, omitted, source_queue = {}, [], []
    native_assets = pins["requiredSourceBinaryAssets"]
    parent = REPO / "tests/node-compat/milestones/foundations-v10"
    parent_summary = load(parent / "results.json")
    assert sha(parent / "results.json") == pins["parentV10ResultsSha256"]
    assert native_assets == parent_summary["requiredSourceBinaryAssets"] and len(native_assets) == 5
    for item in parent_summary["copiedEvidence"]:
        assert sha(parent / item["path"]) == item["sha256"], ("Parent archive changed", item["path"])
    def private_tree(path):
        parts = [part.lower() for part in Path(path).parts]
        return any(part in {"bench", "optimization", "weval-experiment", "utf8-direct",
                            "text-decoder-private", "production-candidate-m0.11",
                            "production-candidate-m0.11-v2", "direct-candidate-m0.11",
                            "single-project-v2", "timing-pair-v1", "matched"}
                   or part.startswith(("m011-", "direct-candidate", "single-project", "timing-", "matched-"))
                   for part in parts)
    def add(source, destination, expected=None, native_asset=None, provenance=False):
        source, destination = Path(source), PurePosixPath(destination)
        assert not destination.is_absolute() and ".." not in destination.parts
        assert_regular(source)
        if private_tree(source) and not provenance:
            raise AssertionError(("Unapproved private/candidate/timing source copy", source))
        is_binary = binary(source)
        if not is_binary:
            with source.open("rb") as stream:
                block = stream.read(65536)
            try:
                block.decode("utf-8")
                is_binary = b"\0" in block
            except UnicodeDecodeError:
                is_binary = True
        if is_binary:
            if native_asset not in native_assets:
                omitted.append({"path": str(source), "reason": "generated-output-or-other-binary"})
                return
            assert sha(source) == native_assets[native_asset]
            assert str(destination) == "source/" + native_asset
        digest = sha(source)
        if expected is not None:
            assert digest == expected, source
        key = str(destination)
        record = {"source": str(source), "destination": key, "sha256": digest, "bytes": source.stat().st_size}
        if key in plan:
            assert plan[key]["sha256"] == digest, ("Copy closure collision", key)
        else:
            plan[key] = record
    def tree(root, destination):
        root = Path(root)
        assert root.is_dir() and not root.is_symlink()
        for directory, directories, names in os.walk(root, followlinks=False):
            keep = []
            for name in sorted(directories):
                path = Path(directory) / name
                if path.is_symlink() or name in SKIP_DIRS or private_tree(path) or "candidate" in name.lower():
                    omitted.append({"path": str(path), "reason": "dependency-symlink-or-unselected-tree"})
                else:
                    keep.append(name)
            directories[:] = keep
            for name in sorted(names):
                path = Path(directory) / name
                if path.is_symlink() or not path.is_file():
                    omitted.append({"path": str(path), "reason": "not-regular-nonsymlink"})
                    continue
                add(path, str(PurePosixPath(destination) / path.relative_to(root).as_posix()))
    def source_file(path):
        path = Path(path)
        if not path.is_absolute():
            path = REPO / path
        if path.name.endswith('.cjs.native-profile.mjs'):
            path = path.with_name(path.name[:-len('.native-profile.mjs')])
        if private_tree(path):
            omitted.append({"path": str(path), "reason": "reference-only-unselected-private-source"})
            return
        if not path.is_file() or path.is_symlink():
            return
        if not path.is_relative_to(TESTS):
            return
        key = "harness/" + path.relative_to(TESTS).as_posix()
        before = len(plan)
        add(path, key)
        if len(plan) != before and path.suffix in {".mjs", ".js", ".cjs", ".py", ".sh"}:
            source_queue.append(path)
    # Complete current native inputs, their source attribution and original configurations.
    for item in engines[0]["sourceManifest"]:
        no_link_components(FREEZE / "source" / item["path"], FREEZE / "source")
        add(FREEZE / "source" / item["path"], "source/" + item["path"], item["sha256"], item["path"])
    for item in load(FREEZE / "licenses.json")["files"]:
        add(FREEZE / "source" / item["path"], "source/" + item["path"], item["sha256"])
    tree(FREEZE / "componentize-source", "componentize-source")
    for path in sorted(FREEZE.iterdir()):
        if path.is_file() and not path.is_symlink():
            add(path, path.name)
    for label, engine in zip(pins["engines"], engines):
        audit = engine["openssl"]["completeSourceAudit"]
        assert audit["beforeAndAfterBuild"] and audit["sourceFilesVerified"] == 4650
        add(FREEZE / (label + "-openssl-before.json"), "dependency/" + label + "-openssl-before.json", audit["beforeReportSha256"])
        # This mutable build-path receipt is also captured immutably per label by the freezer.
        add(FREEZE / (label + "-openssl-receipt.txt"), "dependency/" + label + "-openssl-receipt.txt", engine["openssl"]["receiptSha256"])
        assert sha(FREEZE / (label + "-Cargo.lock")) == engine["generatedRustProject"]["lockSha256"]
        assert sha(FREEZE / (label + "-Cargo.toml")) == engine["generatedRustProject"]["manifestSha256"]
    for name, path in files.items():
        add(path, "reports/" + name + ".json")
    # Preserve successful generated text and both incomplete failed attempts. No Wasm is copied.
    for name in ["release-gates-v1", "release-gates-v2", "release-gates-v3",
                 "allocator-gc-v1", "add-abort-off", "add-abort-runtime", "add-abort-gc",
                 "callback-return-observation", "http-joint"]:
        tree(BASE / name, "generated-text/" + name)
    for path in sorted(BASE.iterdir()):
        if path.is_file() and path.suffix in {".json", ".log"}:
            add(path, "raw/" + path.name)
    tree(ADOPTION, "adoption")
    tree(FOCUSED, "harness/foundation-add-abort/production-native-m0.11")
    indexed_sets = [(reports["httpIndex"], TESTS / "foundations", "http")]
    for root in sorted(TESTS.glob("storage-compaction-v11-pass*")):
        assert sha(root / "index.json") == pins["storageIndexes"][root.name]
        tree(root, "storage/" + root.name)
        index = load(root / "index.json")
        for item in index.get("files", []):
            path = Path(item["path"])
            if not path.is_absolute():
                path = root / path
            assert sha(path) == item["sha256"], path
        indexed_sets.append((index, root, root.name))
        # Some verified historical controls are dictionary keys rather than
        # file-list rows; authenticate and retain each explicit text control.
        def prior_controls(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    if key.startswith('tests/node-compat/storage-') and isinstance(child, str) and re.fullmatch(r'[0-9a-f]{64}', child):
                        path = REPO / key
                        add(path, 'historical-storage-controls/' + path.relative_to(TESTS).as_posix(), child)
                    prior_controls(child)
            elif isinstance(value, list):
                for child in value: prior_controls(child)
        for path in root.rglob('*.json'):
            if path.is_file() and not path.is_symlink(): prior_controls(load(path))
    # Copy indexed text using explicit namespaces. An index reference never
    # grants recursive access to a private tree or opaque output binary.
    storage_roots = [Path('/tmp/starling-node-compat') / name for name in pins['storageIndexes']]
    known_sources = {Path(record['source']).resolve() for record in plan.values()}
    for index, index_root, namespace in indexed_sets:
        for item in index.get('files', []):
            path = Path(item['path'])
            if not path.is_absolute():
                path = index_root / path
            assert sha(path) == item['sha256']
            resolved_path = path.resolve()
            if resolved_path in known_sources:
                continue
            if private_tree(path):
                omitted.append({**item, 'path': str(path), 'reason': 'reference-only-indexed-private-proposal'})
                continue
            if binary(path):
                omitted.append({**item, 'path': str(path), 'reason': 'reference-only-indexed-binary'})
                continue
            if path.is_relative_to(BASE):
                add(path, 'indexed-external/' + namespace + '/' + path.relative_to(BASE).as_posix(), item['sha256'])
                known_sources.add(resolved_path)
            elif path.is_relative_to(REPO):
                add(path, 'indexed-repository/' + path.relative_to(REPO).as_posix(), item['sha256'])
                known_sources.add(resolved_path)
            else:
                owner = next((root for root in storage_roots if path.is_relative_to(root)), None)
                if owner is not None:
                    add(path, 'storage-external/' + owner.name + '/' + path.relative_to(owner).as_posix(), item['sha256'])
                    known_sources.add(resolved_path)
                else:
                    omitted.append({**item, 'path': str(path), 'reason': 'reference-only-external-tool-or-historical-input'})
    # The actual official-wash configuration is not necessarily indexed.
    wash = reports['wasmcloudHttp']
    config_path = Path(wash['configPath'])
    assert config_path.is_relative_to(BASE) and load(config_path) == wash['configuration']
    add(config_path, 'host-configuration/wash-project-config.json')
    command = wash['command']
    user_config = Path(command[command.index('--user-config') + 1])
    assert user_config.is_relative_to(BASE) and load(user_config) == {}
    add(user_config, 'host-configuration/empty-user-config.json')
    add(Path(wash['process']['logPath']), 'raw/official-wash.log')
    run_report = Path(wash['process']['logPath']).parent / 'host-results.json'
    add(run_report, 'host-configuration/run-host-results.json', sha(files['wasmcloudHttp']))
    omitted.append({'path': wash['component']['deployedPath'], 'sha256': pins['httpComponentSha256'],
                    'reason': 'reference-only-validated-deployed-component-binary'})
    omitted.append({'path': wash['host']['binaryPath'], 'sha256': wash['host']['binarySha256'],
                    'reason': 'reference-only-validated-official-host-binary'})
    # Only these authenticated private proposal files are copied as source provenance.
    packet = TESTS / "foundation-alloc-unsafe/production-candidate-m0.11-v2"
    for name, digest in pins["candidateProvenanceFiles"].items():
        add(packet / name, "proposal-provenance/" + name, digest, provenance=True)
    # Explicit current runtime sources/oracles; never recursively traverse candidate/private trees.
    for family in ["foundation-path", "foundation-events", "foundation-string-decoder",
                   "foundation-assert", "foundation-querystring", "foundation-util"]:
        for path in sorted((TESTS / family).iterdir()):
            if path.is_file() and not path.is_symlink() and path.suffix not in {".wasm", ".cwasm"}:
                source_file(path)
    for directory in ["fixtures", "legacy-stream-web-test-sources"]:
        tree(TESTS / directory, "harness/" + directory)
    core_failures = reports['release-core']['initializationFailures']
    assert len(core_failures) == 4
    for item in core_failures:
        path = (TESTS / 'fixtures' / item['fixture']).resolve()
        assert path.is_relative_to((TESTS / 'fixtures').resolve()) and path.is_file()
        source_file(path)
    for path in sorted(TESTS.iterdir()):
        if path.is_file() and not path.is_symlink():
            source_file(path)
    for name in ['package.json', 'package-lock.json']:
        source_file(TESTS / 'toolchain' / name)
    for item in reports["httpInputs"]["sourceFiles"]:
        source_file(REPO / item["path"])
    # Resolve recorded relative manifests against their actual module bases.
    # These exact per-file witnesses include computed negative fixture names;
    # no broad candidate directory is traversed.
    def consumed(records, base, allowed_root, role):
        for record in records:
            name = record.get('path', record.get('name'))
            assert name and record.get('sha256'), (role, record)
            path = (base / name).resolve()
            assert path.is_relative_to(allowed_root.resolve()), (role, path)
            assert sha(path) == record['sha256'], (role, path)
            source_file(path)
    stream_base = TESTS / 'foundation-stream-web/production-candidate'
    consumed(reports['release-stream-web']['sourceManifest'], stream_base,
             TESTS / 'foundation-stream-web', 'stream-web sourceManifest')
    for family, field in [('path', 'sourceManifest'), ('string-decoder', 'sourceManifest'),
                          ('events', 'sourceFiles'), ('assert', 'sourceFiles'),
                          ('querystring', 'sourceFiles'), ('util', 'sourceFiles')]:
        base = TESTS / ('foundation-' + family)
        consumed(reports['optional-' + family][field], base, base, family + ' recorded sources')
    for name, digest in pins['consumedOracleFiles'].items():
        source = REPO / name
        assert sha(source) == digest, source
        source_file(source)
    raw_alias = reports['optional-events']['rawAliasFixture']
    raw_alias_source = Path(raw_alias['componentPath']).with_name('native_events_aliases.source.mjs')
    add(raw_alias_source, 'consumed-fixtures/events-raw-alias.source.mjs', raw_alias['sourceSha256'])
    allocator = reports['release-allocator']
    consumed(allocator['sourceFiles'], TESTS / 'foundation-alloc-unsafe/installed',
             TESTS / 'foundation-alloc-unsafe', 'installed allocator sourceFiles')
    parent_checks = TESTS / 'foundation-alloc-unsafe/checks.mjs'
    assert sha(parent_checks) == allocator['originalChecksSha256']
    source_file(parent_checks)
    allocator_gc = reports['allocatorGc']
    gc_runner = TESTS / 'foundation-alloc-unsafe/installed/run-gc-v11.mjs'
    assert sha(gc_runner) == allocator_gc['runnerSha256']
    source_file(gc_runner)
    gc_pins = Path(allocator_gc['fixedGCAdmission']['path'])
    assert sha(gc_pins) == allocator_gc['fixedGCAdmission']['sha256']
    source_file(gc_pins)
    gc_source = files['allocatorGc'].parent / 'source.mjs'
    add(gc_source, 'consumed-fixtures/allocator-gc.source.mjs', allocator_gc['sourceSha256'])
    # The actual external BufferList source is caller-demand provenance only.
    def find_demand(value):
        if isinstance(value, dict):
            if isinstance(value.get('path'), str) and value['path'].endswith('/buffer_list.js'):
                return value
            for child in value.values():
                found = find_demand(child)
                if found: return found
        elif isinstance(value, list):
            for child in value:
                found = find_demand(child)
                if found: return found
        return None
    demand = find_demand(allocator)
    assert demand and demand['sha256'] == 'c8a1206970857cf3d1df0b8dfa54be336b93fce9ecafdcc3e630f25b6f4415d7'
    demand_path = Path(demand['path'])
    add(demand_path, 'external-source-provenance/readable-stream/buffer_list.js', demand['sha256'])
    package = demand_path.parents[3]
    package_info = load(package / 'package.json')
    assert package_info['name'] == 'readable-stream'
    lock = load(TESTS / 'toolchain/package-lock.json')
    assert any(name.endswith('node_modules/readable-stream') and value.get('version') == package_info['version']
               for name, value in lock['packages'].items())
    add(package / 'package.json', 'external-source-provenance/readable-stream/package.json')
    add(package / 'LICENSE', 'external-source-provenance/readable-stream/LICENSE')
    # Actual report runner/source paths seed a per-file source dependency closure.
    def witnesses(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if isinstance(item, str) and item.startswith(str(TESTS) + "/"):
                    source_file(item)
                witnesses(item)
        elif isinstance(value, list):
            for item in value:
                witnesses(item)
    for report in reports.values():
        witnesses(report)
    # Include concrete relative file dependencies and data-oracle literals, without
    # evaluating JS/Python or treating metadata references as tree-copy permission.
    visited = set()
    literal = re.compile(r"""(?P<quote>['"])(?P<path>[^'"\n]+\.(?:mjs|cjs|js|json|wit|py|sh|h|cpp|cmake|patch|lock|toml))(?P=quote)""")
    while source_queue:
        path = source_queue.pop()
        if path in visited:
            continue
        visited.add(path)
        for match in literal.finditer(path.read_text()):
            value = match.group("path")
            if "://" in value or value.startswith(("node:", "starling:")):
                continue
            value = value.replace('${repo_root}', str(REPO)).replace('$repo_root', str(REPO))
            value = value.replace('${here}', str(path.parent)).replace('$here', str(path.parent))
            for base in [path.parent, path.parent.parent, TESTS]:
                candidate = (base / value).resolve()
                if candidate.is_relative_to(TESTS):
                    source_file(candidate)
    # Exact current docs and preparation/history are small text witnesses, not execution claims.
    tree(REPO / "docs/node-compat", "docs/node-compat")
    if (REPO / "progress.md").exists():
        add(REPO / "progress.md", "docs/progress.md")
    tree(HERE / "history", "acceptance-preparation/history")
    add(HERE / "README.md", "acceptance-preparation/README.md")
    add(HERE / "draft-pins.json", "acceptance-preparation/final-pins.json")
    add(HERE / "accept-v11.py", "accept-v11.py")
    add(REPO / "LICENSE", "LICENSE")
    expected_sources = {item["path"] for item in engines[0]["sourceManifest"]}
    assert sum(key.startswith("source/") and key[7:] in expected_sources for key in plan) == 304
    assert all(not private_tree(item["source"]) or item["destination"].startswith("proposal-provenance/")
               for item in plan.values())
    assert all(not item["destination"].endswith((".wasm", ".o")) or
               (item["destination"].startswith("source/") and item["destination"][7:] in native_assets)
               for item in plan.values())
    return plan, omitted, {"path": "../foundations-v10/results.json",
                          "sha256": pins["parentV10ResultsSha256"],
                          "allParentCopiedEvidenceRehashed": len(parent_summary["copiedEvidence"]),
                          "role": "Immutable parent/historical controls; not additional current m11 engines"}


def main():
    global SOURCE_BINARY_ASSETS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--expected-plan", help="Exact plan SHA from reviewed default verification")
    parser.add_argument("--show-plan", action="store_true")
    args = parser.parse_args()
    pins = load(HERE / "draft-pins.json")
    SOURCE_BINARY_ASSETS = pins["requiredSourceBinaryAssets"]
    files, reports, engines, focused, gap = validate_reports(pins)
    plan, omitted, parent = prepare_plan(files, reports, engines, pins)
    ordered = [plan[key] for key in sorted(plan)]
    plan_sha = hashlib.sha256(json.dumps(ordered, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    summary = {"state": "VERIFIED_BOUNDED_V11_PLAN_ONLY_NO_STAGE", "files": len(plan),
               "bytes": sum(item["bytes"] for item in ordered), "planSha256": plan_sha,
               "nativeInputs": 304, "currentEngines": 3, "nativeChangesFromV10": 4,
               "focusedApplications": 19, "sourceBinaryExceptions": 5,
               "generatedEngineOrApplicationBinariesCopied": False,
               "nodeCallbackReturnParity": False, "nodeSymbolDisposeRegistryParity": False,
               "httpComponentSha256": pins["httpComponentSha256"],
               "httpComponentBytes": pins["httpComponentBytes"], "parentReference": parent}
    if args.show_plan:
        summary["copyPlan"] = ordered
        summary["omittedPaths"] = omitted
    if not args.apply:
        print(json.dumps(summary, indent=2))
        return
    assert args.expected_plan == plan_sha, "Apply requires the exact reviewed read-only plan SHA"
    assert not DESTINATION.exists() and not STAGE.exists()
    STAGE.mkdir(parents=True)
    copied = []
    for item in ordered:
        source, target = Path(item["source"]), STAGE / item["destination"]
        assert_regular(source)
        assert sha(source) == item["sha256"], ("Source changed before copy", source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target, follow_symlinks=False)
        assert_regular(target)
        assert sha(target) == item["sha256"] and target.stat().st_size == item["bytes"]
        copied.append({"path": item["destination"], "sha256": item["sha256"],
                       "bytes": item["bytes"], "original": item["source"]})
    for item in engines[0]["sourceManifest"]:
        assert sha(STAGE / "source" / item["path"]) == sha(REPO / item["path"]) == item["sha256"]
    for item in copied:
        path = STAGE / item['path']
        assert_regular(path)
        assert sha(path) == item['sha256'] and path.stat().st_size == item['bytes'], path
    assert sha(REPO / "tests/node-compat/build-engine.sh") == RECIPE
    result = {"schema": 1, "state": "accepted-bounded-foundations-v11-with-confirmed-node-deviations",
              "acceptedAtUtc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "nodeVersion": "v22.14.0", "coreVersion": CORE, "eventsVersion": "sm-node-22.14.0-m0.10",
              "currentEngines": pins["engines"], "identicalCurrentNativeInputs": 304,
              "nativeChangedFromV10": 4, "nativeUnchangedFromV10": 300,
              "historicalEventsOffControl": pins["historicalEventsOff"], "parentReference": parent,
              "recipeSha256": RECIPE, "readOnlyPlanSha256": plan_sha,
              "boundedFunctionalGatesPassed": True, "completeNodeCompatibility": False,
              "callbackReturnObservationCompleted": True, "nodeCallbackReturnParity": False,
              "callbackReturnCounterexample": {"node": gap["node"]["observed"],
                  "jco": gap["jco"]["observed"], "wasmtime": gap["wasmtime"]["observed"]},
              "nodeSymbolDisposeRegistryParity": False, "focusedCounts": focused["counts"],
              "httpComponentSha256": pins["httpComponentSha256"], "httpComponentBytes": pins["httpComponentBytes"],
              "emittedHTTPImports": HTTP_IMPORTS, "httpRequestsEachHost": 3,
              "sameInstanceHTTPReuseEstablished": False, "performanceTransferred": False,
              "sourceBinaryAssets": SOURCE_BINARY_ASSETS, "generatedEngineOrApplicationBinariesCopied": False,
              "copiedEvidence": copied, "omittedPaths": omitted,
              "limitations": [
                  "Fresh callback-return then getter parity is false; counts are getter reads only, not callable-then/rejection tests.",
                  "Target Symbol.dispose registry identity differs from Node and is not rewritten.",
                  "GC combines callback/signal/closure-held Symbol owners; prototype-only liveness and OOM/fault behavior are unproved.",
                  "Fatal instances are discarded; no failure reuse, process handler, ALS, request teardown or complete Node/EventTarget/Buffer/stream claim.",
                  "HTTP counters1/1/1 do not establish instance reuse; monotonic clock is type-only, random is explicitly selected.",
                  "No outgoing HTTP, DNS, sockets, TLS, filesystem or CLI capabilities follow from these tests.",
                  "Five successful release reports were byte-verified reused same-engine results; three strict suites reran after storage failure.",
                  "Missing host import, ENOSPC attempts, storage/COW receipts and copied source history are not additional passing runtime gates.",
                  "Most storage recovery occurred before COW bootstrap; its35,856,384B delta is a nonexclusive observation, not extent or guest performance proof.",
                  "Old private timings are not transferred; no current memory, size or throughput advantage is claimed.",
                  "Historical m10 Events-OFF/parent controls are not a fourth current engine or identical m11 manifest."
              ]}
    (STAGE / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    (STAGE / "README.md").write_text("# Bounded foundations v11 checkpoint\n\n"
        "Three current Release engines share304 native inputs and corem0.11. "
        "Known callback-return and disposal-symbol Node parity is false. "
        "Historical Events-OFF remains separate; see results.json and acceptance-preparation/README.md. "
        "Engines/components remain external; five exact versioned host-API source assets are included.\n")
    STAGE.rename(DESTINATION)
    print(json.dumps({**summary, "state": result["state"], "milestone": str(DESTINATION)}, indent=2))


if __name__ == "__main__":
    main()
