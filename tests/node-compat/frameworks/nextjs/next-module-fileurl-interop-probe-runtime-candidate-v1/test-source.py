"""Read-only Source/selector checks. No JavaScript/helper/owner/fixture action."""
from pathlib import Path
import ast, hashlib, json, re

HERE = Path(__file__).resolve().parent
DONOR = HERE.parent / 'next-module-fileurl-probe-runtime-candidate-v1'


def row(p):
    b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))


def main():
    checks=0
    def need(v,why):
        nonlocal checks
        assert v is True,why
        checks+=1
    p=json.loads((HERE/'plan.json').read_bytes());before=json.loads((DONOR/'plan.json').read_bytes())
    actor=(HERE/'collect.mjs').read_text();owner=(HERE/'run-owned.py').read_text();comparison=(HERE/'comparison.mjs').read_text()
    for key in ['node','wasmtime','monitor','outerSeconds','listenerSeconds','requestSeconds','shutdownSeconds','startFreeBytes','responseByteCap','reuseCount','idleInstanceTimeout','requests','method','path','query','probeSourceIndex','worldSourceIndex','witDirectory','worldName','selectedInterfaces','adapter','fixtures','fixtureGuestRoot','fixtureCopyPolicy']:
        need(p[key]==before[key],'Unchanged role/cap: '+key)
    need(p['mode']=='interop'and p['actionsAllowed']is False and p['prospectiveActualBindingsPending']is False,'Dormant interop selector')
    for key in ['actualRootAuthority','actualComponent','actualConstructionResult','actualConstructionDataReview','actualResults','actualNodeControl']:
        need(p[key]is None,'No invented actual artifact: '+key)
    ctor=json.loads(Path(p['expectedConstructionDataReview']['path']).read_bytes())
    for key,name in [('expectedComponent','component'),('expectedComponentAudit','componentAudit'),('expectedConstructionResult','actualResult')]:
        need(p[key]==ctor[name],'GenuineacceptedINITrole:'+key)
    need(ctor['verifiedPassed']is True and row(Path(p['expectedConstructionDataReview']['path']))==p['expectedConstructionDataReview'],'GenuineacceptedINITreview')
    need(p['probeEntry']['sha256']=='a53ed6f28ecc5104668e31afd9bb6fab5acb1eda4a99853446b7cecb0e8be372','Sealed interop guest only')
    need(p['constructionCallerIndex']['sha256']=='cf088b5eb1a08dabc5f333f8ece0acb0a225bd98ae7db1dae55bd85511453a99','Future sealed interop constructor only')
    build=json.loads(Path(p['fullBuildReview']['path']).read_bytes())
    need(build['verifiedPassed']is True,'Actual fullbuild DATA accepted')
    need(p['expectedEngine']==build['engine'],'Expectedengine is genuine accepted artifact')
    need(p['expectedNativeMetadata']==build['metadata'],'Expectedmetadata is genuine accepted artifact')
    need(p['interopLoaderAfterimage']['sha256']=='40eeb699d87b30dd3c146421f189a99848715a19b2efc83b081f0d61d3832d67','Corrected rooted loader Source')
    need(row(Path(p['probeEntry']['path']))==p['probeEntry']and row(Path(p['interopLoaderAfterimage']['path']))==p['interopLoaderAfterimage'],'Exact declared Source bytes')
    need((HERE/'native-model.mjs').read_bytes()==(DONOR/'native-model.mjs').read_bytes(),'Generic metadata fixed-field consumer unchanged')
    need(len(p['expectedCaseIds'])==len(set(p['expectedCaseIds']))==16,'Exact distinct16-case inventory')
    ids=re.search(r'const IDS = Object.freeze\(\[(.*?)\]\);',comparison,re.S).group(1)
    need(re.findall(r"'([^']+)'",ids)==p['expectedCaseIds'],'Independent comparator order agrees Source case contract')
    need(actor.count('await fetch(')==1 and "url: origin + '/probe'"in actor and "method: 'GET', redirect: 'error'"in actor,'One GET expression/no retry request')
    need(actor.count('spawn(plan.wasmtime.path')==1 and "'--dir', root + '::/probe'"in actor and '::/app'not in actor,'Same stock host/probe-only mount')
    need(actor.index('handles.push(stdout)')<actor.index('const stderr = await open')<actor.index('handles.push(stderr)'),'Each acquired log immediately owned')
    need(actor.index('await save(); // Raw bytes/partial failure')<actor.index('validateInteropResponse(payload)'),'Raw partial bytes/errors saved before comparison')
    need('response.complete || kept > 0'in actor and 'readerCleanupErrors.push'in actor,'Partial response/error retention preserved')
    need('assert.deepEqual(await fixtureRecords(), result.fixtures)'in actor and 'stat.dev !== original.dev || stat.ino !== original.ino'in actor,'Same final fixture identity and Source separation')
    need("host.kill('SIGINT')"in actor and 'result.server?.forcedCleanup === false'in actor and 'hostExit?.code === 0'in actor,'Same strict owned shutdown')
    need('plan.prospectiveActualBindingsPending, false'in actor and "p['prospectiveActualBindingsPending'] is False"in owner,'Both entrypoints block provisional artifact pins')
    need("free_bytes >= p['startFreeBytes'] == 1073741824"in owner and owner.index('free_bytes >=')<owner.index('outer.mkdir'),'Same1GiB prewrite floor')
    need('expectedPrimitive'in comparison and "thenReads, 0"in comparison and "rejectedNull: true"in comparison,'Primitive/thenable/nullthrow independent gates present')
    need("assert.deepEqual(e.module, {type: 'string', value: specifier.slice(0, 512)})"in comparison and 'moduleMatchesActualSpecifier, true'in comparison,'Bounded serialized prefix and full native boolean distinct')
    for path in HERE.glob('*.py'):ast.parse(path.read_bytes())
    print(json.dumps(dict(sourceOnly=True,passed=True,checks=checks,interopCases=16,actualBuildAndConstructorDataBound=True,javascriptParsedOrExecuted=False,actorOwnerHelperOrFixtureInvoked=False)))


if __name__=='__main__':main()
