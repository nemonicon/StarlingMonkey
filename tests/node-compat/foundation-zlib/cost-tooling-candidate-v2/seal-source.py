"""Final source/data seal and benign checks; no future action main is invoked."""
import ast,hashlib,json,os,stat,subprocess
from pathlib import Path
HERE=Path(__file__).parent.resolve();NODE=Path('/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
PEER=HERE.parent/'independent-cost-guest-oracle-v2-source-review-v1';PEER_SHA='259a7a31b972aa30eb5be2f82d5f29da91b4f36d7d5fc7aac3aa0f561d0636ed'
def need(v,m):
    if not v:raise AssertionError(m)
def digest(raw):return hashlib.sha256(raw).hexdigest()
def file_sha(path):
    h=hashlib.sha256()
    with path.open('rb')as f:
        for raw in iter(lambda:f.read(1024*1024),b''):h.update(raw)
    return h.hexdigest()
def exclusive(name,value):
    p=HERE/name;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x')as f:json.dump(value,f,indent=2);f.write('\n')
def rawfile(name,raw):
    p=HERE/name;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb')as f:f.write(raw)
def row(path):
    s=path.lstat();need(stat.S_ISREG(s.st_mode)and not path.is_symlink(),'Source regular only');return{'path':str(path.resolve()),'sha256':file_sha(path),'bytes':s.st_size}
def main():
    need(not(HERE/'index.json').exists(),'Never reseal a frozen source packet')
    # Parent review is a source-only proof, not action authorization.
    ixraw=(PEER/'index.json').read_bytes();need(digest(ixraw)==PEER_SHA,'Exact corrected guest independent source review');peer_index=json.loads(ixraw)
    plan=json.loads((HERE/'publication-plan.json').read_text());inputs=[]
    for r in peer_index['files']+[{'path':'index.json','sha256':PEER_SHA,'bytes':len(ixraw)}]:
        p=PEER/r['path'];raw=p.read_bytes();need(digest(raw)==r['sha256']and len(raw)==r['bytes'],'Peer source member');target=HERE/'image/guest-source-peer'/r['path'];target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():need(target.read_bytes()==raw,'Existing source-only peer snapshot exact')
        else:
            with target.open('xb')as f:f.write(raw)
        inputs.append(row(p));destination='metadata/guest-source-peer/'+r['path']
        if not any(v['destination']==destination for v in plan['objects']):plan['objects'].append({'source':str(target.resolve()),'destination':destination,'sha256':r['sha256'],'bytes':r['bytes'],'mode':stat.S_IMODE(target.stat().st_mode),'role':'independent-corrected-guest-source-proof-only'})
    plan['guestIndependentSourceReviewIndexSha256']=PEER_SHA;plan['context']['guestIndependentSourceReviewIndexSha256']=PEER_SHA
    # The unsealed controls are captured exactly once at final seal. This does
    # not rewrite an old recipe/index, invoke a renderer, or create a publication.
    for r in plan['objects']:
        if Path(r['source']).is_relative_to(HERE):
            p=Path(r['source']);r.update(sha256=file_sha(p),bytes=p.stat().st_size,mode=stat.S_IMODE(p.stat().st_mode))
    plan['logicalCopyBytesBeforeProofCapsules']=sum(r['bytes']for r in plan['objects'])
    (HERE/'publication-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    parent_path=HERE.with_name('cost-tooling-candidate-v1');parent_plan=json.loads((parent_path/'publication-plan.json').read_text().replace(str(parent_path),str(HERE)).replace('/tmp/starling-node-compat/zlib-cost-source-v1','/tmp/starling-node-compat/zlib-cost-source-v2'))
    parent_plan['objects']+=[r for r in plan['objects']if r.get('role')=='historical-parent-source-HOLD-not-current-admission']
    for r in parent_plan['objects']:
        if Path(r['source']).is_relative_to(HERE):
            p=Path(r['source']);r.update(sha256=file_sha(p),bytes=p.stat().st_size,mode=stat.S_IMODE(p.stat().st_mode))
    for key in['historicalToolingSourceHoldIndexSha256','historicalToolingSourceHoldReviewIndexSha256']:parent_plan[key]=plan[key]
    parent_plan['context']['historicalToolingSourceHoldIndexSha256']=plan['context']['historicalToolingSourceHoldIndexSha256'];parent_plan['logicalCopyBytesBeforeProofCapsules']=sum(r['bytes']for r in parent_plan['objects'])
    need(parent_plan==plan,'Exact parent source-plan rebase plus declared HOLD/input/control-hash changes')
    exclusive('plan-derivation.json',{'schemaVersion':1,'state':'EXACT_PARENT_PLAN_REBASE_AND_DECLARED_SOURCE_CORRECTIONS_ONLY','parentPlanSha256':file_sha(parent_path/'publication-plan.json'),'newPlanSha256':file_sha(HERE/'publication-plan.json'),'exactReconstruction':True,'nativeOrGuestOrToolBytesProjected':False})
    env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'};env.pop('PYTHONOPTIMIZE',None)
    commands=[('pure',[str(NODE),str(HERE/'test-pure.mjs')]),('publication',['python3',str(HERE/'test-publication.py')]),('source',['python3',str(HERE/'check-source.py')])];reports={}
    for label,command in commands:
        r=subprocess.run(command,env=env,capture_output=True);rawfile('evidence/'+label+'.stdout.log',r.stdout);rawfile('evidence/'+label+'.stderr.log',r.stderr)
        need(r.returncode==0,'Benign source check failed: '+label);report=json.loads(r.stdout);exclusive('evidence/'+label+'-results.json',{'command':command,'returncode':r.returncode,'report':report});reports[label]=report
    syntax=[]
    for p in sorted(HERE.rglob('*')):
        if not p.is_file()or 'history'in p.relative_to(HERE).parts:continue
        if p.suffix=='.mjs':
            r=subprocess.run([str(NODE),'--check',str(p)],capture_output=True);need(r.returncode==0,'Parse failure: '+str(p));syntax.append({'path':str(p.relative_to(HERE)),'nodeCheckExitCode':r.returncode})
        elif p.suffix=='.py':ast.parse(p.read_text());syntax.append({'path':str(p.relative_to(HERE)),'ASTParsed':True})
    exclusive('evidence/syntax-results.json',{'schemaVersion':1,'state':'SOURCE_PARSE_ONLY_PASSED','checks':len(syntax),'files':syntax,'providerOrLibraryInvoked':False})
    base=json.loads((HERE/'source-preparation-inputs.json').read_text());all_inputs={r['source']:{'path':r['source'],'sha256':r['sha256'],'bytes':r['bytes']}for r in base['files']}
    for r in json.loads((HERE/'guest-intake.json').read_text())['files']+inputs:all_inputs[r['path']]=r
    parent=json.loads((HERE/'parent-inputs.json').read_text())
    for r in parent['files']:all_inputs[r['path']]=r
    for r in json.loads((HERE/'parent-hold-inputs.json').read_text())['files']:all_inputs[r['path']]=r
    facts=json.loads((HERE/'image/metadata/native-facts.json').read_text())
    for item in facts['variants']:
        descriptor=item['metadata'];p=Path(descriptor['path']);r=row(p);need(r['sha256']==descriptor['sha256']and r['bytes']==descriptor['bytes'],'Actual metadata DATA input');all_inputs[r['path']]=r
    r=row(NODE);need(r['sha256']=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0','Pinned actual Node parser');all_inputs[r['path']]=r
    exclusive('input-freeze.json',{'schemaVersion':1,'state':'SOURCE_PREPARATION_INPUTS_NOT_ACTION_CONTEXT','files':sorted(all_inputs.values(),key=lambda r:r['path']),'oldPreparationRowsFollowedAsRuntimeAuthority':False,'sourceOnly':True})
    exclusive('source-receipt.json',{'schemaVersion':1,'state':'FRESH350_COST_TOOLING_SOURCE_IMPLEMENTED_UNREVIEWED','parentSourceHoldIndexSha256':'f5f13bfa0256a3e89d87827ea40d12dfbf617a23c304ba3b8335167c02bc3049','proposalIndexSha256':'e29c596df3c809bab8fd3851b224a7ec4e84177d791c5d1f909072985f047ef8','guestSourceIndexSha256':plan['guestSourceIndexSha256'],'guestSourcePeerIndexSha256':PEER_SHA,'sourceProtocolDecisionSha256':plan['sourceProtocolDecisionSha256'],'publicationPlanSha256':file_sha(HERE/'publication-plan.json'),'publicationObjectsBeforeDynamicProofCapsules':len(plan['objects']),'publicationLogicalBytesBeforeDynamicProofCapsules':plan['logicalCopyBytesBeforeProofCapsules'],'completeToolFiles':4890,'knownNewPublicationToolLinks':22,'pureChecks':reports['pure']['checks'],'ownedTextPublisherChecks':reports['publication']['checks'],'sourceDataChecks':reports['source']['checks'],'parseChecks':len(syntax),'sourceOnly':True,'ownerActionMainsInvoked':False,'codecOrLibraryOrOracleOrBundleOrComponentOrNativeOrGuestOrHostOrPilotOrTimingInvoked':False,'actualSourcePublicationCreated':False,'implementedBodies':['source-publication','node-oracle','bundle-source'],'unimplementedBodies':['component-build','guest-correctness','pilot','timing'],'allPositiveActionAuthorities':None,'operationalAdmission':False,'sourcePromotionAllowed':False,'runtimeAcceptanceClaim':False})
    files=[]
    for p in sorted(HERE.rglob('*')):
        if p.is_dir():continue
        need(not p.is_symlink()and p.is_file(),'Ordinary source packet only');need('__pycache__'not in p.parts,'No interpreter cache in sealed source');r=row(p);files.append({'path':str(p.relative_to(HERE)),'sha256':r['sha256'],'bytes':r['bytes']})
    exclusive('index.json',{'schemaVersion':1,'state':'FRESH350_COST_TOOLING_SOURCE_ONLY_NOT_ACTION_AUTHORITY','files':files,'sourceOnly':True,'actionsAllowed':False,'operationalAdmission':False})
    print(json.dumps({'indexSha256':file_sha(HERE/'index.json'),'files':len(files),'inputRows':len(all_inputs),'sourceOnly':True,'actionsInvoked':False}))
if __name__=='__main__':main()
