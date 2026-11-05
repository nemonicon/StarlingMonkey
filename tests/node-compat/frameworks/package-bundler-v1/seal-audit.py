"""Finite data-only inventory of actual retained host experiments; no reruns."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
TOOL=Path('/private/tmp/starling-node-compat/toolchain/node_modules/rolldown')
def load(p):return json.loads(Path(p).read_bytes())
def row(p,relative=False):
    p=Path(p);assert p.is_file()and not p.is_symlink();b=p.read_bytes()
    return dict(path=p.relative_to(HERE).as_posix()if relative else str(p.absolute()),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def write(name,value):(HERE/name).write_text(json.dumps(value,indent=2)+'\n')
a=load(HERE/'evidence/results.json');b=load(HERE/'additional-evidence/results.json');c=load(HERE/'lifecycle-evidence/results.json');v=load(HERE/'virtual-source-evidence/results.json');d=load(HERE/'conditions-evidence/results.json')
assert a['node']==b['node']==c['node']==v['node']==d['node']=='v22.14.0'
assert a['rolldownVersion']==load(TOOL/'package.json')['version']=='1.2.16'
assert len(a['cases'])==10 and len(b['cases'])==12 and len(c['cases'])==3 and len(d['cases'])==3
processes=[r['host']for r in a['cases']if r.get('generatedBundleExecuted')]+[o for r in c['cases']for o in r['observations'].values()]
assert len(processes)==13 and all(p['status']==0 and p['signal']is None and p['error']is None for p in processes)
for x in a['cases']:
    if x['name'].startswith('official-'):assert x['observed']['sameDefault']is True and x['observed']['hasOwnDefault']is False
assert next(x for x in a['cases']if x['name']=='duplicate-external')['containsResidualRequire']is True
assert next(x for x in a['cases']if x['name']=='manual-default-mixed-cjs')['error']
assert [r['sameStructuredValue']for r in c['cases']]==[True,True,False]
assert len(v['modules'])==1 and v['modules'][0]['bytes']==60
assert v['modules'][0]['sha256']=='4147dd982e935223855a7f312cd8d35dc881e8b165b0ede58ad959ea3278f089'
for r in d['cases']:assert r['branchesPresent']==['require','import']
inputs=[row(TOOL/p)for p in['package.json','dist/index.mjs','dist/plugins-index.mjs','dist/plugins-index.d.mts','dist/shared/constructors-C2I2nhzU.mjs','dist/shared/constructors-viKPej7M.d.mts','dist/shared/define-config-u93KkixF.d.mts','dist/shared/binding-BQxk4mNX.d.mts']]
inputs += [row(TOOL.parent/'@rolldown/binding-darwin-arm64/package.json'),row(TOOL.parent/'@rolldown/binding-darwin-arm64/rolldown-binding.darwin-arm64.node'),row(HERE.parent.parent/'profile-bundler.mjs'),row('/private/tmp/starling-node-compat/production-classic-trace-v1/native-freeze/source/builtins/node-compat/export-manifest.node-v22.14.0.json')]
node=a['nodeBinary'];assert row(node['path'])==node;inputs.append(node)
write('provenance.json',dict(schemaVersion=1,role='PINNED_HOST_TOOL_AND_API_SOURCE_DATA',files=inputs,externalBinariesCopied=False,sourceCitations=[dict(path=str(TOOL/'dist/shared/define-config-u93KkixF.d.mts'),line=1791,topic='transform.define'),dict(path=str(TOOL/'dist/shared/define-config-u93KkixF.d.mts'),line=3630,topic='resolver aliases/conditions/mainFields'),dict(path=str(TOOL/'dist/shared/define-config-u93KkixF.d.mts'),line=745,topic='externalLiveBindings and paths'),dict(path=str(TOOL/'dist/shared/define-config-u93KkixF.d.mts'),line=4020,topic='built-in transform follows plugin hook'),dict(path=str(TOOL/'dist/shared/define-config-u93KkixF.d.mts'),line=10,topic='ModuleInfo.code'),dict(path=str(TOOL/'dist/shared/constructors-C2I2nhzU.mjs'),line=48,topic='official builtin plugin'),dict(path=str(TOOL/'dist/shared/binding-BQxk4mNX.d.mts'),line=1710,topic='plugin external/duplicate options')],officialDocumentation='https://rolldown.rs/builtin-plugins/esm-external-require',actualOptionalFrameworkBundlerReview=None))
attempts=len(a['cases'])+len(b['cases'])+len(c['cases'])+1+len(d['cases']);failures=sum('error'in r for r in a['cases']+b['cases']);assert attempts==29 and failures==4
write('results.json',dict(schemaVersion=1,state='SOURCE_BASED_ROLLDOWN_COMMONJS_PACKAGING_AUDIT_COMPLETED_V1',nodeVersion='v22.14.0',rolldownVersion='1.2.16',hostBundlingInvoked=True,hostToyBuildAttempts=attempts,generatedToyBundles=attempts-failures,retainedExpectedCompileRefusals=failures,hostToyModuleExecutions=13,allHostToyProcessesExitedZero=True,officialNativeDefaultIdentityCases=4,ordinaryLazyAndCycleControlsMatched=True,mutablePackageNamedBindingMismatchRetained=True,genericEsmExternalNamespaceCopyMismatchRetained=True,officialVirtualSourceBytes=60,actualOptionalImplementationReviewed=False,frameworkPackageExecuted=False,nativeEngineExecuted=False,guestExecuted=False,compilerInvoked=False,sourceContract=row(HERE/'source-contract.json'),fixtureSuggestions=row(HERE/'fixture-suggestions.json'),provenance=row(HERE/'provenance.json'),actualEvidence=[row(HERE/n)for n in['evidence/results.json','additional-evidence/results.json','lifecycle-evidence/results.json','virtual-source-evidence/results.json','conditions-evidence/results.json']],rootActionAuthority=None,runtimeAcceptance=False,operationalAdmission=False))
write('result-contract.json',dict(schemaVersion=1,state='ADVISORY_COMMONJS_SOURCE_AND_HOST_TOY_AUDIT_V1',results=row(HERE/'results.json'),sourceContract=row(HERE/'source-contract.json'),sourceReviewOfOptionalImplementation=None,guestArtifactProof=None,rootActionAuthority=None,grantsActionOrRuntimeAuthority=False))
for r in inputs:assert row(r['path'])==r
files=[row(p,True)for p in sorted(HERE.rglob('*'))if p.is_file()and p.name!='index.json']
assert not any(p.is_symlink()for p in HERE.rglob('*'))
write('index.json',dict(schemaVersion=1,state='SEALED_FINITE_COMMONJS_SOURCE_AUDIT_AND_HOST_TOY_EVIDENCE_V1',files=files))
print(json.dumps(dict(index=row(HERE/'index.json'),members=len(files),results=row(HERE/'results.json'),contract=row(HERE/'result-contract.json'),sourceContract=row(HERE/'source-contract.json'),hostBuildAttempts=attempts,hostToyExecutions=13,nativeEngineExecuted=False,guestExecuted=False)))
