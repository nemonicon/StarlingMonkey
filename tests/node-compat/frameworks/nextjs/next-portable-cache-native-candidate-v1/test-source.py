"""Read-only source derivation checks, never an actor or helper invocation."""
from pathlib import Path
import ast
import difflib
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
DONOR = BASE / 'wasmtime-deployment-guard-candidate-v1'
count = 0


def check(value):
    global count
    if value is not True:
        raise ValueError('Source derivation check ' + str(count + 1))
    count += 1


def read(name):
    return (HERE / name).read_text()


def descriptor(path):
    raw = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))


for name in ['deploy.mjs', 'run-owned.py', 'app-policy.mjs']:
    check((HERE / name).read_bytes() == (DONOR / name).read_bytes())
ast.parse(read('run-owned.py'))
after = read('run-contracts.mjs')
before = (DONOR / 'run-contracts.mjs').read_text()
extra_import = "\nimport {collectPortableCache,validatePortableCache} from '../next-portable-cache-http-collector-v1/collector.mjs';"
block = "  result.portableCache=await collectPortableCache({origin:result.origin,output:join(root,'portable-cache')});\n  await save(); // Whole five-request raw capture precedes semantic comparison.\n  result.portableCacheValidation=validatePortableCache(result.portableCache);\n  await save();\n"
check(after.count(extra_import) == after.count(block) == 1)
check(after.index(block) < after.index('  result.supplemental=await collectSupplemental'))
inverse = after.replace(extra_import, '').replace(block, '').replace('&&result.portableCacheValidation?.passed===true;', ';').replace('./browser-check.mjs', '../browser-hydration-candidate-v3/browser-check.mjs')
check(inverse == before)
check("result.originalContractPassed=result.passed;" in after)
check('result.http.length===24&&result.http.every(x=>x.passed)&&result.cacheInvalidation?.passed===true' in after)
check('result.streaming?.incrementalDeliveryObserved===true&&result.browserExit?.code===0&&result.browser?.passed===true' in after)
worker = read('browser-check.mjs')
old_worker = (BASE / 'browser-hydration-candidate-v3/browser-check.mjs').read_text()
match = re.search(r'const assetPins=(.*?);', worker)
old_match = re.search(r'const assetPins=(.*?);', old_worker)
check(worker[:match.start(1)] + old_match.group(1) + worker[match.end(1):] == old_worker)
pins = json.loads(match.group(1))
plan = json.loads(read('plan.json'))
inventory = json.loads(Path(plan['applicationInputs']['path']).read_bytes())
check(len(pins) == 5)
for pin in pins:
    member = pin['path'].replace('/_next/', '.next/', 1)
    row = next(r for r in inventory['files'] if r['path'] == member)
    raw = (Path(inventory['root']) / member).read_bytes()
    check(pin['sha256'] == row['sha256'] == hashlib.sha256(raw).hexdigest() and pin['bytes'] == row['bytes'] == len(raw))
check(sum(a != b for a, b in zip(pins, json.loads(old_match.group(1)))) == 2)
check(plan['expectedComponent'] == {'sha256': '4e6582eed8b60ed6da94c9c1454c8fd1cb1f1c5e5f4df15aaa27ddb5b0bb94ca', 'bytes': 37235395})
check(plan['applicationSchema']['files'] == 2186 and plan['applicationSchema']['directoriesExcludingRoot'] == 427 and plan['applicationSchema']['ownedDirectoriesIncludingRoot'] == 429)
check(plan['applicationSchema']['additionalDirectories'] == ['.next/cache'])
check(plan['deadlines'] == json.loads((DONOR / 'plan.json').read_bytes())['deadlines'])
check(plan['requiredObservations'] == json.loads((DONOR / 'plan.json').read_bytes())['requiredObservations'])
check(plan['portableCacheProfile']['legacyGenerationCounterGatePreserved'] is True and plan['portableCacheProfile']['actualRun'] is None)
check(all(plan[k] is None for k in ['actualRootAuthority','actualConstructionResult','actualComponent','actualComponentAudit','actualDeployment','runId']))
derivation = json.loads(read('derivation.json'))
for row in derivation['executableRows']:
    check(descriptor(Path(row['before']['path'])) == row['before'] and descriptor(Path(row['after']['path'])) == row['after'])
patch = ''.join(''.join(difflib.unified_diff((DONOR/name).read_text().splitlines(True),read(name).splitlines(True),fromfile=DONOR.name+'/'+name,tofile=HERE.name+'/'+name)) for name in ['deploy.mjs','run-owned.py','app-policy.mjs','run-contracts.mjs'])
check(patch == read('donor-delta.patch'))
print(json.dumps(dict(sourceOnly=True, checks=count, grammarOrHelperOrActorInvoked=False)))
