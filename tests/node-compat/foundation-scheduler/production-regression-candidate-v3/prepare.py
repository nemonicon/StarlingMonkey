"""Generate packet-only sibling bodies; never edit original v11 files."""
from pathlib import Path
import hashlib
import json
import os
import re

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
SOURCES = {
    'allocator':'tests/node-compat/foundation-alloc-unsafe/installed/run-component-v11.mjs',
    'allocator-gc':'tests/node-compat/foundation-alloc-unsafe/installed/run-gc-v11.mjs',
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def generate(name,original):
    old = REPO/SOURCES[name]
    target = HERE/'runners'/(name+'.mjs')
    text = original
    changes = []

    def replace(before,after,count=1):
        nonlocal text
        assert text.count(before) == count,(name,before,text.count(before))
        text = text.replace(before,after)
        changes.append({'before':before,'after':after,'count':count})

    for match in list(re.finditer(r"from (['\"])(\.[^'\"]+)\1",original)):
        spec = match.group(2)
        source = (old.parent/spec).resolve()
        if source.name == 'production-v11-preflight.mjs' or spec.endswith('production-native-m0.10/preflight.mjs'):
            continue
        relative = os.path.relpath(source,target.parent).replace(os.sep,'/')
        if not relative.startswith('.'):
            relative = './'+relative
        replace(match.group(0),'from '+match.group(1)+relative+match.group(1),original.count(match.group(0)))
    if name == 'allocator':
        replace("import {verifyProductionV11} from '../../foundation-add-abort/production-v11-preflight.mjs';",
                "import {verifyProductionTicks} from '../preflight.mjs';")
        replace('const newEnginePreflight=await verifyProductionV11();','const newEnginePreflight=await verifyProductionTicks({gcStress:false});')
        replace('const here=dirname(fileURLToPath(import.meta.url)),parent=dirname(here);',
                "const here=resolve(dirname(fileURLToPath(import.meta.url)),'../../../foundation-alloc-unsafe/installed'),parent=dirname(here);")
        replace('...h.evidence,coreExpectations:policy,','...h.evidence,productionTickAdmission:newEnginePreflight.report,coreExpectations:policy,')
        replace("join(here,'native-component-v11-results.json')","join(h.output,'allocator-summary.json')")
    else:
        replace("import { preflight as protectedPreflight } from '../../foundation-add-abort/production-native-m0.10/preflight.mjs';",
                "import { verifyProductionTicks } from '../preflight.mjs';")
        replace("const here=dirname(fileURLToPath(import.meta.url)), repository=resolve(here,'../../../..');",
                "const here=resolve(dirname(fileURLToPath(import.meta.url)),'../../../foundation-alloc-unsafe/installed'), repository=resolve(here,'../../../..');")
        replace("'sm-uncaught-event-v3-protected-abort-v2'","'sm-uncaught-event-v3-protected-abort-v2-private-ticks-v1'")
        replace('const admitted=await protectedPreflight({gcStress:true});','const admitted=await verifyProductionTicks({gcStress:true});')
        replace("const pinsPath=join(here,'production-v11-gc-pins.json'),pinBytes=await readFile(pinsPath),pins=JSON.parse(pinBytes);",
                'const pinsPath=admitted.pinsPath,pinBytes=admitted.pinBytes,pins=admitted.pin;')
        replace("assert.equal(pins.state,'new-native-gc-build-reviewed');","assert.equal(pins.state,'reviewed-real-production-freeze');")
        replace('protectedAdmission:admitted.report,','productionTickAdmission:admitted.report,')
        replace("join(here,'gc-v11-results.json')","join(output,'allocator-gc-summary.json')")
    restored = text
    for change in reversed(changes):
        assert restored.count(change['after']) == change['count']
        restored = restored.replace(change['after'],change['before'])
    assert restored == original,'No undeclared changes are permitted'
    return text,changes


def main():
    ancestry = json.loads((HERE/'ancestry.json').read_text())
    expected = {row['path']:row['sha256'] for row in ancestry['inputs']}
    result = []
    for name,path in SOURCES.items():
        source = (REPO/path).read_bytes()
        assert sha(source) == expected[path]
        text,changes = generate(name,source.decode())
        destination = HERE/'runners'/(name+'.mjs')
        destination.write_text(text)
        result.append({'name':name,'original':path,'originalSha256':sha(source),
                       'generated':str(destination.relative_to(HERE)),'generatedSha256':sha(text.encode()),
                       'changes':changes,'reverseDeclaredEditsRestoresOriginalBytes':True})
    (HERE/'runner-transformations.json').write_text(json.dumps({'state':'PACKET_ONLY_DECLARED_ADMISSION_PATH_AND_REPORT_EDITS','runners':result},indent=2)+'\n')
    print(json.dumps({'runners':len(result),'oldFilesModified':False}))


if __name__ == '__main__':
    main()
