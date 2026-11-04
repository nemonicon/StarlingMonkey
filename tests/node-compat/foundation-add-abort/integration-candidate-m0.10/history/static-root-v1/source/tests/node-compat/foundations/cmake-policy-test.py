"""Configure real feature guards; unrelated builtin targets are mocked."""
import datetime
import hashlib
import json
import os
import pathlib
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[3]
features = ["PATH", "EVENTS", "STRING_DECODER", "ASSERT", "QUERYSTRING", "UTIL", "STREAM_WEB"]
reports = []
with tempfile.TemporaryDirectory(prefix="sm-foundations-cmake-") as directory:
    temporary = pathlib.Path(directory)
    source = temporary / "source"
    source.mkdir()
    (source / "builtins").symlink_to(root / "builtins", target_is_directory=True)
    mock = source / "mock"
    mock.mkdir()
    (source / "empty.cpp").write_text("int sm_foundations_cmake_guard;\n")
    (mock / "add_builtin.cmake").write_text('''function(add_builtin)
 if(ARGV0 STREQUAL "builtins::node_compat" AND ENABLE_BUILTIN_NODE_COMPAT)
  add_library(builtin_node_compat STATIC "${CMAKE_CURRENT_SOURCE_DIR}/empty.cpp")
 endif()
endfunction()
''')
    (source / "CMakeLists.txt").write_text('''cmake_minimum_required(VERSION 3.25)
project(FoundationGuards LANGUAGES CXX)
add_library(extension_api INTERFACE)
add_library(builtin_web_text_codec INTERFACE)
add_library(builtin_web_event INTERFACE)
add_library(builtin_web_abort INTERFACE)
add_library(builtin_web_queue_microtask INTERFACE)
add_library(builtin_web_streams INTERFACE)
list(PREPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/mock")
include("''' + str(root / "cmake/builtins.cmake") + '''")
if(TARGET builtin_node_compat)
 get_target_property(defs builtin_node_compat COMPILE_DEFINITIONS)
 file(WRITE "${CMAKE_BINARY_DIR}/definitions.txt" "${defs}")
endif()
''')
    cases = [("default-core-on", True, [], True), ("all-on", True, features, True),
             ("all-off-without-core", False, [], True)]
    for feature in features:
        cases.extend([(feature.lower() + "-on", True, [feature], True),
                      (feature.lower() + "-without-core", False, [feature], False)])
    for name, core, selected, accepted in cases:
        flags = ["-DENABLE_BUILTIN_NODE_COMPAT=" + ("ON" if core else "OFF")]
        flags.extend("-DNODE_COMPAT_" + feature + "=ON" for feature in selected)
        build = temporary / name
        process = subprocess.run(["cmake", "-S", str(source), "-B", str(build), *flags],
                                 text=True, capture_output=True)
        assert (process.returncode == 0) == accepted, (name, process.stdout, process.stderr)
        definitions = (build / "definitions.txt").read_text().split(";") if (build / "definitions.txt").exists() else []
        if accepted:
            for feature in features:
                assert ("NODE_COMPAT_" + feature + "=1" in definitions) == (feature in selected), (name, definitions)
        else:
            assert "NODE_COMPAT_" + selected[0] + " requires ENABLE_BUILTIN_NODE_COMPAT=ON" in process.stderr
        reports.append(dict(name=name, flags=flags, accepted=accepted,
                            definitions=definitions, exitCode=process.returncode))

    # An occupied artifact must fail before any fetching/configuration. Do not
    # use a real accepted engine as the sentinel or modify its receipt.
    node = os.environ["NODE_COMPAT_NODE"]
    for occupied in ["engine", "receipt"]:
        work = temporary / ("occupied-" + occupied)
        artifact = work / "artifacts/starlingmonkey_embedding.abi-i32-i64-v1.entropy-entry-v1-strict-callback-v3.OFF.path-0.events-0.string-decoder-0.assert-0.querystring-0.util-0.stream-web-0.no-clobber.wasm"
        artifact.parent.mkdir(parents=True)
        sentinel = pathlib.Path(str(artifact) + (".build.json" if occupied == "receipt" else ""))
        contents = b"preserve exact sentinel bytes\n"
        sentinel.write_bytes(contents)
        environment = {key: value for key, value in os.environ.items() if not key.startswith("NODE_COMPAT_")}
        environment.update(NODE_COMPAT_NODE=node, NODE_COMPAT_BUILD_ROOT=str(work), NODE_COMPAT_ARTIFACT_TAG="no-clobber")
        process = subprocess.run(["bash", str(root / "tests/node-compat/build-engine.sh")],
                                 env=environment, text=True, capture_output=True, timeout=20)
        assert process.returncode != 0 and "Refusing to overwrite" in process.stderr, process.stderr
        assert sentinel.read_bytes() == contents
        assert not any(work.glob("componentize-*")), "Guard ran after creating a source tree"
        reports.append(dict(name="existing-" + occupied + "-rejected", exitCode=process.returncode,
                            sentinelPreserved=True, rejectedBeforeSourcePreparation=True))

report = dict(schema=1, atUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
              kind="Real cmake/builtins.cmake guards with unrelated target creation mocked; configure only. Real recipe sentinel rejection; no engine compilation.",
              sourceSha256=hashlib.sha256((root / "cmake/builtins.cmake").read_bytes()).hexdigest(),
              recipeSha256=hashlib.sha256((root / "tests/node-compat/build-engine.sh").read_bytes()).hexdigest(), cases=reports)
(pathlib.Path(__file__).parent / "cmake-policy-results.json").write_text(json.dumps(report, indent=2) + "\n")
print("Foundation CMake/recipe guards:", len(reports), "PASS")
