"""Syntax-only check for the unapplied guard; never edits production/builds an engine."""
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[3]
ENGINE = Path(os.environ.get("NODE_COMPAT_ENGINE", "/tmp/starling-node-compat/foundations-v6/native-freeze/off-foundations.engine.wasm"))
SOURCE = Path(os.environ.get("NODE_COMPAT_ENGINE_SOURCE_ROOT", "/tmp/starling-node-compat/foundations-v6/native-freeze/source"))
digest = lambda data: hashlib.sha256(data).hexdigest()
metadata = json.loads(Path(str(ENGINE) + ".build.json").read_text())
assert digest(ENGINE.read_bytes()) == metadata["engineSha256"]
pins = json.loads((HERE / "native-controller-receiver-pins.json").read_text())
patch = (HERE / "native-controller-receiver.UNAPPLIED.patch").read_bytes()
assert digest(patch) == pins["patchSha256"]
temporary = Path(tempfile.mkdtemp(prefix="stream-web-controller-syntax-", dir="/tmp/starling-node-compat"))
for entry in pins["files"]:
    source = SOURCE / entry["path"]
    assert digest(source.read_bytes()) == entry["baseSha256"]
    target = temporary / entry["path"]
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
subprocess.run(["patch", "-p1", "-d", str(temporary)], input=patch, check=True)
for entry in pins["files"]:
    assert digest((temporary / entry["path"]).read_bytes()) == entry["proposedSha256"]
database = json.loads(Path(metadata["compileCommandsPath"]).read_text())
unit = next(entry for entry in database if entry["file"].endswith("/transform-stream-default-controller.cpp"))
original = shlex.split(unit["command"])
arguments = []
index = 0
while index < len(original):
    item = original[index]
    if item == "-o":
        index += 2
        continue
    if item == "-c":
        index += 1
        continue
    if item == unit["file"]:
        item = str(temporary / "builtins/web/streams/transform-stream-default-controller.cpp")
    arguments.append(item)
    index += 1
arguments += ["-fsyntax-only", "-I" + str(SOURCE / "builtins/web/streams")]
completed = subprocess.run(arguments, cwd=unit["directory"], capture_output=True, text=True)
report = {"scope": "UNAPPLIED native controller guard; actual SDK/header syntax only", "engineSha256": metadata["engineSha256"],
          "patchSha256": pins["patchSha256"], "temporarySource": str(temporary), "command": arguments,
          "exitCode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr,
          "syntaxOnly": True, "linked": False, "productionApplied": False}
(HERE / "native-controller-syntax-results.json").write_text(json.dumps(report, indent=2) + "\n")
assert completed.returncode == 0, completed.stderr
print(json.dumps({"syntaxOnly": True, "exitCode": 0, "productionApplied": False}))
