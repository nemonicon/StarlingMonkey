"""Read-only/inert stock namespace and exact source derivation checks."""
from pathlib import Path
import ast
import difflib
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
DONOR = BASE / 'browser-hydration-matched-host-candidate-v6'
count = 0


def check(value):
    global count
    if value is not True:
        raise ValueError('Source derivation check ' + str(count + 1))
    count += 1


def descriptor(path):
    raw = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))


after = (HERE/'run-stock.mjs').read_text()
before = (DONOR/'run-stock.mjs').read_text()
extra_import = "\nimport {collectPortableCache,validatePortableCache} from '../next-portable-cache-http-collector-v1/collector.mjs';"
block = "  result.portableCache=await collectPortableCache({origin:result.origin,output:join(root,'portable-cache')});\n  await save(); // Whole five-request raw capture precedes semantic comparison.\n  result.portableCacheValidation=validatePortableCache(result.portableCache);\n  await save();\n"
check(after.count(extra_import) == after.count(block) == 1)
check(after.index(block) < after.index('  result.supplemental = await collectSupplemental'))
old_prefix = '/private/tmp/starling-node-compat/next-browser-hydration-stock-v6'
prefix = '/private/tmp/starling-node-compat/next-portable-cache-stock-v1'
inverse = after.replace(extra_import,'').replace(block,'').replace(' && result.portableCacheValidation?.passed === true;',';').replace(prefix,old_prefix)
check(inverse == before)
owner = (HERE/'run-owned.py').read_text()
check(owner.replace(prefix,old_prefix) == (DONOR/'run-owned.py').read_text())
tree = ast.parse(owner)
function = next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='derive_invocation')
env = dict(Path=Path,re=re)
exec(compile(ast.Module(body=[function],type_ignores=[]),str(HERE/'run-owned.py'),'exec'),env)
plan = json.loads((HERE/'plans.json').read_bytes())
authority = dict(state='ROOT_NEXT_BROWSER_PHASE_MATCHED_HOST_AUTHORIZED_V1',arm='stock',runId='source-inert')
output,monitor,argv = env['derive_invocation'](authority,plan,HERE)
check(str(output) == prefix+'-source-inert' and str(monitor) == str(output)+'-monitor')
check(argv == [plan['node']['path'],str(HERE/'run-stock.mjs'),str(output),plan['standaloneSource'],plan['browserTools'],'source-inert'])
for value in ['', 'x\n', '../x', 'A', 'x'*49, None, 1]:
    try:
        env['derive_invocation'](dict(authority,runId=value),plan,HERE)
    except (AssertionError,TypeError):
        check(True)
    else:
        raise ValueError('unsafe inert namespace accepted')
for field in ['outputRoot','monitorOutputRoot','argv']:
    try:
        env['derive_invocation'](dict(authority,**{field:'x'}),plan,HERE)
    except AssertionError:
        check(True)
    else:
        raise ValueError('Root override accepted')
check(plan['arms']['stock']['timeoutSeconds'] == 300)
check(plan['expectedApplication']['files'] == 2186 and plan['expectedApplication']['directories'] == 427 and plan['expectedApplication']['directoryInventoryExcludesRoot'] is True)
check(plan['arms']['stock']['browserSource']['path'] == str(BASE/'next-portable-cache-native-candidate-v1/browser-check.mjs'))
check(plan['portableCacheProfile']['legacyGenerationCounterGatePreserved'] is True)
check(plan['requiredObservations'] == json.loads((DONOR/'plans.json').read_bytes())['requiredObservations'])
for row in json.loads((HERE/'derivation.json').read_bytes())['executableRows']:
    check(descriptor(Path(row['before']['path'])) == row['before'] and descriptor(Path(row['after']['path'])) == row['after'])
patch = ''.join(''.join(difflib.unified_diff((DONOR/name).read_text().splitlines(True),(HERE/name).read_text().splitlines(True),fromfile=DONOR.name+'/'+name,tofile=HERE.name+'/'+name)) for name in ['run-owned.py','run-stock.mjs'])
check(patch == (HERE/'donor-delta.patch').read_text())
print(json.dumps(dict(sourceOnly=True, checks=count, actualDeriveFunctionInertInputsOnly=True, helperOrActorInvoked=False)))
