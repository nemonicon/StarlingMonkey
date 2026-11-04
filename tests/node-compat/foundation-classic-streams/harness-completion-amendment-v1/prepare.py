"""Produce new afterimages; never edit the immutable integration candidate."""
from pathlib import Path
import difflib
import hashlib
import json

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / 'integration-candidate-v1'
BEFORE = '949a9c8ca9310341db2351fbad8e314d1c13101f82d5c08806237a5f8a2cc0c6'
INDEX = '5826a3dfc8d79ebbbbd139665dd06f9f493af3aa6f48302f2865611591fcff6d'

def digest(data): return hashlib.sha256(data).hexdigest()

def main():
    assert digest((PARENT / 'index.json').read_bytes()) == INDEX
    old = (PARENT / 'harness/component-driver.mjs').read_text()
    assert digest(old.encode()) == BEFORE
    text = old
    edits = []
    def replace(a, b, count=1):
        nonlocal text
        assert text.count(a) == count, (a, text.count(a))
        text = text.replace(a, b)
        edits.append({'old': a, 'new': b, 'count': count})
    replace("import { deployedFatal, deployedCleanControls } from './deployed-fixtures.mjs';",
            "import { deployedFatal, deployedCleanControls } from './deployed-fixtures.mjs';\nimport { trackedWriter, publishCompletion } from './completion.mjs';")
    replace("  await mkdir(output,{recursive:true});\n", "  await mkdir(output,{recursive:true});\n  const tracked=trackedWriter(output);\n  const writeOutput=tracked.write;\n")
    count = text.count('await writeFile(')
    assert count == 13, count
    replace('await writeFile(', 'await writeOutput(', count)
    replace("import { readFile, writeFile, mkdir, symlink } from 'node:fs/promises';", "import { readFile, mkdir, symlink } from 'node:fs/promises';")
    replace("  try {\n    if(variant==='disabled-off') {", "  let completedReport;\n  try {\n   execution: {\n    if(variant==='disabled-off') {")
    replace("      await writeOutput(join(output,'results.json'),JSON.stringify({schemaVersion:1,variant,\n        status:'FUTURE_CLASSIC_DISABLED_ADMISSION_GATE_PASSED',engineSha256:metadata.engineSha256,\n        pin,failures,componentizerInvoked:false,componentBuilt:false,hostExecuted:false},null,2)+'\\n',{flag:'wx'});\n      return;",
            "      completedReport={schemaVersion:1,variant,\n        status:'FUTURE_CLASSIC_DISABLED_ADMISSION_GATE_PASSED',engineSha256:metadata.engineSha256,\n        pin,failures,componentizerInvoked:false,componentBuilt:false,hostExecuted:false};\n      break execution;")
    replace("    assert.deepEqual(caught.interfaceAudit.emittedImports,selectedInterfaces);\n    await admission.recheck();\n    const report=", "    assert.deepEqual(caught.interfaceAudit.emittedImports,selectedInterfaces);\n    const caughtComponentPath=join(output,'initializer-caught-control.component.wasm');\n    await writeOutput(caughtComponentPath,caught.component,{flag:'wx'});\n    await admission.recheck();\n    const report=")
    replace("      caughtInitializerControl:{sourceSha256:", "      caughtInitializerControl:{componentPath:caughtComponentPath,sourceSha256:")
    replace("    await writeOutput(join(output,'results.json'),JSON.stringify(report,null,2)+'\\n',{flag:'wx'});\n  } finally { await admission.recheck(); }\n}",
            "    completedReport=report;\n   }\n  } finally { await admission.recheck(); }\n  assert(completedReport,'A completed semantic gate must provide its report');\n  await publishCompletion({output,report:completedReport,paths:tracked.paths});\n}")
    assert "writeOutput(join(output,'results.json')" not in text
    assert text.index('await publishCompletion(') > text.rindex('finally { await admission.recheck(); }')
    restored = text
    for edit in reversed(edits):
        assert restored.count(edit['new']) == edit['count']
        restored = restored.replace(edit['new'], edit['old'])
    assert restored == old
    path = HERE / 'proposed/harness/component-driver.mjs'
    with path.open('x') as stream: stream.write(text)
    (HERE / 'before').mkdir(exist_ok=False)
    with (HERE / 'before/component-driver.mjs').open('x') as stream: stream.write(old)
    helper = (HERE / 'proposed/harness/completion.mjs').read_text()
    patch = ''.join(difflib.unified_diff(old.splitlines(True), text.splitlines(True), fromfile='a/harness/component-driver.mjs', tofile='b/harness/component-driver.mjs'))
    patch += ''.join(difflib.unified_diff([], helper.splitlines(True), fromfile='/dev/null', tofile='b/harness/completion.mjs'))
    with (HERE / 'harness-completion.UNAPPLIED.patch').open('x') as stream: stream.write(patch)
    proof = {'schemaVersion': 1, 'state': 'SOURCE_ONLY_REVERSIBLE_COMPLETION_AMENDMENT',
             'parentIndexSha256': INDEX, 'beforeSha256': BEFORE, 'afterSha256': digest(text.encode()),
             'helperSha256': digest(helper.encode()), 'patchSha256': digest(patch.encode()),
             'edits': edits, 'reverseRestoresExactParent': True, 'oldWriteCallsTracked': count,
             'newCaughtControlArtifactPreserved': True, 'guestOrNativeExecuted': False}
    with (HERE / 'transformation-proof.json').open('x') as stream: json.dump(proof, stream, indent=2); stream.write('\n')
    print(json.dumps({k:v for k,v in proof.items() if k != 'edits'}))

if __name__ == '__main__': main()
