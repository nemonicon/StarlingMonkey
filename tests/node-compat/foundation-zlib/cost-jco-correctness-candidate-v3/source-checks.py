#!/usr/bin/env python3
"""Data-only exact derivation/closure checks; no owner modules/actions run."""
import hashlib,json,os,re,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
PARENT=BASE/'cost-jco-correctness-candidate-v2'
checks=[]
def check(name,value):
    if not value: raise AssertionError(name)
    checks.append({'name':name,'passed':True})
def digest(raw):return hashlib.sha256(raw).hexdigest()
def read(row):
    p=Path(row['path']);check('regular no-symlink input '+str(p),p.is_file() and not p.is_symlink())
    b=p.read_bytes();check('full hash/size '+str(p),len(b)==row['bytes'] and digest(b)==row['sha256']);return b
def index(path,expected):
    raw=Path(path).read_bytes();check('pinned source index '+str(path),digest(raw)==expected)
    v=json.loads(raw);names=set()
    for row in v['files']:
        n=row['path'];check('finite unique indexed member '+n,n not in names and n and not n.startswith('/') and '\\' not in n and all(x not in ('','.','..') for x in n.split('/')));names.add(n)
        read({**row,'path':str(Path(path).parent/n)})
    return v
def main():
    parent=index(PARENT/'index.json','d2516c934df3fa8f3ecd58b187cc2bc0f28fab996ab97ada0854e4988d9befeb')
    check('old donor still has51 indexed files',len(parent['files'])==51)
    old_inputs=json.loads((PARENT/'input-freeze.json').read_bytes())
    for row in old_inputs['files']:read(row)
    check('all493 original-context donor preparation rows remain exact',len(old_inputs['files'])==493)
    hold=index(BASE/'independent-cost-jco-correctness-v2-source-review-v1/index.json','751147af6cda28a9f32b6c8e16ec22db9dc3a2b4592d38a32342f0bb99e28ecd')
    hr=json.loads((BASE/'independent-cost-jco-correctness-v2-source-review-v1/results.json').read_bytes())
    check('M1 historical HOLD remains exact and non-admitting',hr['hold'] is True and hr['sourceReviewPassed'] is False and len(hr['findings'])==1 and hr['findings'][0]['id']=='ZLIB-JCO-CORRECTNESS-V2-M1')
    derivatives=json.loads((HERE/'source-derivations.json').read_bytes())
    check('only3 host source afterimages',len(derivatives['files'])==3)
    import difflib
    patch=''
    for row in derivatives['files']:
        before=Path(row['origin']).read_text();after=(HERE/row['path']).read_text();current=before
        check('derivation before hash '+row['path'],digest(before.encode())==row['beforeSha256'])
        check('derivation after hash '+row['path'],digest(after.encode())==row['afterSha256'])
        for edit in row['edits']:
            offsets=[m.start() for m in re.finditer(re.escape(edit['old']),current)]
            check('actual exact edit locations '+row['path'],offsets==edit['beforeOffsetsAtEdit'] and len(offsets)==edit['count'])
            current=current.replace(edit['old'],edit['new'])
        check('forward exact '+row['path'],current==after)
        current=after
        for edit in reversed(row['edits']):
            shift=0;positions=[]
            for p in edit['beforeOffsetsAtEdit']:positions.append(p+shift);shift+=len(edit['new'])-len(edit['old'])
            for p in reversed(positions):
                check('offset reverse slice '+row['path'],current[p:p+len(edit['new'])]==edit['new'])
                current=current[:p]+edit['old']+current[p+len(edit['new']):]
        check('offset reverse exact '+row['path'],current==before)
        patch+=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+row['path'],tofile='b/'+row['path']))
    check('full unapplied patch exact',patch.encode()==(HERE/'host-retention.UNAPPLIED.patch').read_bytes())
    run=(HERE/'run.mjs').read_text();admit=(HERE/'admission.mjs').read_text();edges=(HERE/'node-edges.mjs').read_text()
    check('new callback actually wired into edge loop',edges.count('const retain=createNodeRetention({Buffer,write,writeBytes,retained,name});')==1)
    check('no legacy Buffer-only callback remains',"const binary=Buffer.isBuffer(value)" not in edges)
    check('snapshot before writer await',edges.index('snapshot.set(new Uint8Array(buffer,offset,length))')<edges.index('row=await(binary?writeBytes(path,snapshot)'))
    check('new actual16MiB full binary bound', 'MAX_NODE_RETAINED_BINARY_BYTES=16*1024*1024' in edges)
    check('new V3 Root and peer states only',"v.state==='ROOT_REVIEWED_ZLIB_COST_JCO_CORRECTNESS_V3'" in admit and "state:'INDEPENDENT_ZLIB_COST_JCO_CORRECTNESS_SOURCE_REVIEW_PASSED_V3'" in admit)
    check('donor and HOLD authenticated before component loader',admit.index("'cost-jco-correctness-candidate-v2':'d251")<admit.index('await componentPreflight(') and admit.index("'independent-cost-jco-correctness-v2-source-review-v1':'751147")<admit.index('await componentPreflight('))
    check('new output namespace exact',"OUTPUT='/private/tmp/starling-node-compat/zlib-cost-jco-correctness-v3'" in admit)
    check('donor worker/cases used with actual own+parent critical closure',"join(DONOR,'worker.mjs')" in run and "join(DONOR,'cases.json')" in run and 'const criticalFiles=[...admitted.criticalSourceFiles,admitted.rootAction]' in run)
    check('held donor run/admission/node-edge action path never imported',not any("../cost-jco-correctness-candidate-v2/"+n in (admit+run+edges) for n in ['run.mjs','admission.mjs','node-edges.mjs']))
    check('donor worker wire unchanged, actual new sourceSHA still passed',"state:'PARENT_AUDITED_ZLIB_COST_JCO_WORKER_V2'" in run and 'correctnessSourceIndexSha256:admitted.sourceSha' in run)
    template=json.loads((HERE/'root-authority.template.json').read_bytes())
    check('new Root action remainsfalse and source/peer/oracleNULL',template['actionAllowed'] is False and all(template[k] is None for k in ['correctnessSourceIndexSha256','sourceIndependentReview','oracle']))
    check('all3 component action/review slots stillNULL',all(v is None for k in ['componentBuildAuthorities','actualComponentReviews'] for v in template[k].values()))
    data=json.loads((HERE/'available-artifact-reviews.json').read_bytes())
    for arm,p in data['arms'].items():
        ix=index(p['index']['path'],p['index']['sha256']);r=json.loads(read(p['result']))
        check('current actual artifact proof DATA '+arm,r['arm']==arm and r['state']=='INDEPENDENT_ZLIB_COST_COMPONENT_ARTIFACT_REVIEW_PASSED_V1' and r['ordinaryGuestExportsInvoked'] is False)
        check('actual result indexed once '+arm,len([x for x in ix['files'] if x['path']=='results.json' and x['sha256']==p['result']['sha256'] and x['bytes']==p['result']['bytes']])==1)
    for name in ['test-retention-pure.mjs','node-edges.mjs']:
        text=(HERE/name).read_text()
        check('pure retention source no codec import '+name,'from \'node:zlib\'' not in text and 'await import(' not in text)
    freeze=json.loads((HERE/'input-freeze.json').read_bytes())
    for row in freeze['files']:read(row)
    check('new preparation manifest explicitly original-context-only',freeze['runtimeActivationOrActionSeal'] is False)
    result={'schemaVersion':1,'state':'SOURCE_DATA_CORRECTION_AND_CLOSURE_CHECKS_PASSED_V3','passed':True,'checks':len(checks),'details':checks,'donorIndexedFiles':51,'inheritedOriginalContextPreparationInputs':493,'hostAfterimages':3,'actualArtifactsOnlyReadAsProofData':True,'ownerHelpersActionsCodecsProvidersGuestsWorkersPreflightsInvoked':False}
    return result
if __name__=='__main__':
    result=main();destination=Path(sys.argv[1]);destination.parent.mkdir(parents=True,exist_ok=True)
    with destination.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({k:v for k,v in result.items() if k!='details'}))
