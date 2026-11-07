"""Read-only Source/inert namespace checks; no VM/fixture/app invocation."""
from pathlib import Path
import ast
import difflib
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
OLD = BASE/'next-portable-cache-stock-candidate-v1'
count = 0


def check(value):
    global count
    if value is not True:
        raise ValueError('Source check ' + str(count + 1))
    count += 1


def ref(path):
    raw = path.read_bytes()
    return dict(path=str(path),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))


actor = (HERE/'run-stock.mjs').read_text()
old_actor = (OLD/'run-stock.mjs').read_text()
addition = "  // Required owned parent for the explicit portable FETCH profile.\n  const ownedCacheParent=join(application,'.next/cache');\n  await mkdir(ownedCacheParent,{mode:0o700});\n  const ownedCacheStat=await lstat(ownedCacheParent);\n  assert(ownedCacheStat.isDirectory()&&!ownedCacheStat.isSymbolicLink());\n  assert.equal(await realpath(ownedCacheParent),ownedCacheParent);\n  assert.equal(ownedCacheStat.mode&0o777,0o700);\n  result.ownedPortableCacheParent={path:ownedCacheParent,mode:0o700,createdAfterOwnedReset:true};\n"
oldprefix = '/private/tmp/starling-node-compat/next-portable-cache-stock-v1'
prefix = '/private/tmp/starling-node-compat/next-portable-cache-stock-v2'
check(actor.count(addition) == 1)
check(actor.replace(addition,'').replace(prefix,oldprefix).replace('./module-host-provider.mjs','../http-bridge-candidate-v1/module-host-provider.mjs') == old_actor)
check(actor.index("await rm(join(application, '.next/cache')") < actor.index(addition) < actor.index('const moduleObservations'))
check(actor[actor.index('  result.portableCache='): ] == old_actor[old_actor.index('  result.portableCache='):])
owner = (HERE/'run-owned.py').read_text()
check(owner.replace(prefix,oldprefix) == (OLD/'run-owned.py').read_text())
tree = ast.parse(owner)
derive = next(x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name=='derive_invocation')
env = dict(Path=Path,re=re)
exec(compile(ast.Module(body=[derive],type_ignores=[]),'actual_pure_namespace','exec'),env)
plan = json.loads((HERE/'plans.json').read_bytes())
old_plan = json.loads((OLD/'plans.json').read_bytes())
authority = dict(state='ROOT_NEXT_BROWSER_PHASE_MATCHED_HOST_AUTHORIZED_V1',arm='stock',runId='source-inert')
output,monitor,argv = env['derive_invocation'](authority,plan,HERE)
check(str(output)==prefix+'-source-inert' and str(monitor)==str(output)+'-monitor')
check(argv==[plan['node']['path'],str(HERE/'run-stock.mjs'),str(output),plan['standaloneSource'],plan['browserTools'],'source-inert'])
for invalid in ['', 'x\n', '../x', 'A', 'x'*49, None]:
    try:
        env['derive_invocation'](dict(authority,runId=invalid),plan,HERE)
    except (AssertionError,TypeError):
        check(True)
    else:
        raise ValueError('invalid namespace accepted')
for field in ['requiredObservations','browserTimingPolicy','expectedApplication','applicationInputs','applicationBuildResult','applicationBuildReview','applicationRootIdentity','applicationRootIdentityEvidence','portableCacheProfile','supplemental']:
    check(plan[field] == old_plan[field])
check(plan['arms']['stock']==old_plan['arms']['stock'] and plan['arms']['stock']['timeoutSeconds']==300)
check(plan['hostVmDynamicImportPolicy']['actualSeamTest'] is None and plan['hostVmDynamicImportPolicy']['actualApplicationRun'] is None)
check(plan['ownedPortableCacheParent']['mode']==0o700 and plan['ownedPortableCacheParent']['sourceDerivedPreconditionNotObservedV1Cause'] is True)
provider = (HERE/'module-host-provider.mjs').read_text()
check("import {compileFunction, constants as vmConstants} from 'node:vm';" in provider)
check("{filename, importModuleDynamically: vmConstants.USE_MAIN_CONTEXT_DEFAULT_LOADER}" in provider)
check('experimental-vm-modules' not in actor and 'experimental-vm-modules' not in owner)
check("'node:sea', 'node:sqlite', 'node:test', 'node:test/reporters'" in provider)
check('observations.candidateSynchronousRequireCacheRemainsSeparate = true' in provider)
for descriptor in [plan['preservedFailedV1SourceIndex'],plan['preservedFailedV1DataReview'],plan['hostVmDynamicImportPolicy']['provider']]:
    check(ref(Path(descriptor['path']))==descriptor)
check(plan['hostVmDynamicImportPolicy']['provider'] in plan['protectedInputs'])
check(plan['preservedFailedV1SourceIndex'] in plan['sourceFamilies'])
check("return import(specifier)" in (HERE/'vm-fixtures/driver.cjs').read_text())
check('module.exports = class MainLoaderClass' in (HERE/'vm-fixtures/target.cjs').read_text())
seam = (HERE/'test-vm-seam.mjs').read_text()
for text in ["assert.equal(result.oldExpectedError?.code,'ERR_VM_DYNAMIC_IMPORT_CALLBACK_MISSING')", "const first=await driver.load('./target.cjs')", "assert.equal(first.default,ordinary)", "assert.notEqual(candidateExport,first.default", "flag:'wx'", "assert.equal(process.argv.length,4"]:
    check(text in seam)
patch = ''.join(''.join(difflib.unified_diff((OLD/name).read_text().splitlines(True),(HERE/name).read_text().splitlines(True),fromfile=OLD.name+'/'+name,tofile=HERE.name+'/'+name))for name in ['run-stock.mjs','run-owned.py'])
patch += ''.join(difflib.unified_diff((BASE/'http-bridge-candidate-v1/module-host-provider.mjs').read_text().splitlines(True),provider.splitlines(True),fromfile='http-bridge-candidate-v1/module-host-provider.mjs',tofile=HERE.name+'/module-host-provider.mjs'))
check(patch==(HERE/'source-delta.patch').read_text())
print(json.dumps(dict(sourceOnly=True,checks=count,actualVmOrDynamicImportFixtureOrActorInvoked=False)))
