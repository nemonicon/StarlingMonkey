"""Finite Python text/JSON/AST checks; no JS, helper, guard, host or target load."""
from pathlib import Path
import ast
import difflib
import hashlib
import json
import re
import stat

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
DONOR=BASE/'wasmcloud-cold-candidate-v5'


def main():
    checks=0
    def require(value):
        nonlocal checks
        assert value
        checks+=1
    def row(path):
        path=Path(path);s=path.lstat();before=(s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
        require(path.resolve()==path and stat.S_ISREG(s.st_mode) and s.st_nlink==1 and s.st_size<=2*1024*1024)
        b=path.read_bytes();s=path.lstat();require(before==(s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns))
        return dict(path=str(path),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
    def read(path):return json.loads(Path(path).read_bytes())
    manifest=read(HERE/'afterimages.json');plan=read(HERE/'plan.json');old=read(DONOR/'plan.json');template=read(HERE/'root-authority-template.json')
    require(row(DONOR/'index.json')==manifest['parentSourceIndex'])
    patch=[]
    for f in manifest['files']:
        require(row(DONOR/f['path'])==f['before'] and row(HERE/f['path'])==f['after'])
        require(((DONOR/f['path']).read_bytes()==(HERE/f['path']).read_bytes())==f['byteIdentical'])
        patch.extend(difflib.unified_diff((DONOR/f['path']).read_text().splitlines(True),(HERE/f['path']).read_text().splitlines(True),fromfile='before/'+f['path'],tofile='after/'+f['path']))
    require(''.join(patch)==(HERE/'cold-to-full.patch').read_text())
    require((DONOR/'app-policy.mjs').read_bytes()==(HERE/'app-policy.mjs').read_bytes())
    ast.parse((HERE/'run-owned.py').read_text(),filename='run-owned.py')
    require(plan['expectedArtifacts']==old['expectedArtifacts'])
    for key in ['fixedWit','worldFamily','selectedInterfaces','applicationInputs','applicationRootIdentity','applicationSchema','applicationBuildResult','applicationSource','node','monitor','outerSeconds','configSeconds','listenerSeconds','gracefulStopMilliseconds']:
        require(plan[key]==old[key])
    require(all(value is None for key,value in plan.items() if key.startswith('actual')))
    require(plan['outerSeconds']==600 and plan['hostLogScope'].startswith('Cold donor direct-fd logs;'))
    require(plan['outputPrefix']=='/private/tmp/starling-node-compat/next-wasmtime-deployment')
    require(row(plan['clientSource']['path'])==plan['clientSource'])
    client=Path(plan['clientSource']['path']).read_text()
    literal=re.search(r"assert\.equal\(root,'([^']+)'-?",client)
    require(literal is not None and literal.group(1)==plan['outputPrefix']+'-')
    require("assert.equal(process.argv.length,6)" in client)
    require("join(here, '../next-browser-netlog-candidate-v1/browser-check.mjs')" in client)
    require(plan['browserSource']['path']==str(BASE/'next-browser-netlog-candidate-v1/browser-check.mjs'))
    require(row(plan['browserSource']['path'])==plan['browserSource'])
    for family in plan['runtimeSourceFamilies']:
        require(row(family['path'])==family)
        root=Path(family['path']).parent;index=read(family['path'])
        require({x.relative_to(root).as_posix() for x in root.rglob('*') if x.is_file()}=={'index.json'}|{r['path'] for r in index['files']})
        for r in index['files']:require(row(root/r['path'])==dict(r,path=str(root/r['path'])))
    for r in plan['protectedSourceReferences']:
        # Source refs and existing finite JSON only; no expectedArtifacts/tool binaries.
        require(row(r['path'])==r)
    models=(HERE/'models.mjs').read_text();deploy=(HERE/'deploy.mjs').read_text();owner=(HERE/'run-owned.py').read_text()
    require("assert.equal(a.selfOrigin,u.origin)" in models and "assert(u.port&&Number(u.port)>0)" in models)
    require("allowedHosts:[u.href]" in models and "assert.deepEqual(e.workload.allowedHosts,want.workload.allowedHosts)" in models)
    require("assert.equal(want.workload.allowedHosts.length,1)" in models)
    require("STARLING_NEXT_ORIGIN:origin" in models and "allowedIpNameLookups:[],allowedHostLoopbackPorts:[]" in models)
    require("port:Number(new URL(a.selfOrigin).port),exclusive:true" in deploy and 'port:0' not in deploy)
    require(deploy.index("validateEffective(shown.data,configured)")<deploy.index('lease.close(')<deploy.index("'wash-dev'"))
    require(deploy.index("registrationFromLogs(logs,origin)")<deploy.index('const client=await launch('))
    require("plan.clientSource.path,origin,join(output,'client'),plan.browserTools,a.runId" in deploy)
    require(deploy.index("result.client.result=await row(join(output,'client/result.json'))")<deploy.index('result.contractsPassed=result.clientRawExitAccepted&&observed.passed===true'))
    require("['config-show','wash-dev','full-contract-client']" in deploy and 'children.length===2' not in deploy)
    require('handles.push(out);const err=await open(' in deploy and 'handles.push(err);' in deploy)
    require("child.record.label==='full-contract-client'&&(child.record.forcedCleanup||child.status===null||![0,1].includes(child.status.code)||child.status.signal!==null||child.status.error!==null)" in deploy and 'child.record.rawStreamDigestsUnavailable=true' in deploy)
    require("fullContractClientAllowed:true" in models and 'browserAllowed:true' in models)
    require(template['selfOrigin'] is template['fullContractClientAllowed'] is template['browserAllowed'] is None)
    require(all(template[k] is False for k in ['compilerAllowed','componentConstructionAllowed','externalNetworkAllowed','newServicesAllowed','hostMutationAllowed','retainedContractAcceptanceAllowed','fullNextAcceptanceAllowed','adoptionAllowed']))
    require("'browserAllowed','fullContractClientAllowed']" in owner and 'outer,600,authority)' in owner)
    require("const deadline=Date.now()+plan.listenerSeconds*1000" in deploy and "if(registered.registered&&await tcpReady(address.port))" in deploy)
    require('cold-contract.json' not in deploy and "await fetch(" not in deploy)
    # Native selection/world and unchanged original full client preserve their own checks.
    donor_models=(DONOR/'models.mjs').read_text()
    require(models[models.index('export function validateSelection'):models.index('export function evaluate')]==donor_models[donor_models.index('export function validateSelection'):donor_models.index('export function evaluate')])
    print(json.dumps(dict(state='SOURCE_TEXT_JSON_AST_CHECKS_PASSED_V1',checks=checks,pythonAstFiles=1,javascriptGrammarChecked=False,javascriptOrProducerEvaluated=False,originalHelpersOrGuardsLoaded=False,toolsOrTargetsInvoked=False,actualAuthority=None)))


if __name__=='__main__':main()
