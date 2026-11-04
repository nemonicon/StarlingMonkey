#!/usr/bin/env python3
"""Read/hash/derivation checks only. No owner helper, loader or worker call."""
import hashlib,json,re,difflib,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
checks=[]
def yes(name,v):
    if not v:raise AssertionError(name)
    checks.append({'name':name,'passed':True})
def sha(b):return hashlib.sha256(b).hexdigest()
def exact_file(row):
    p=Path(row['path']);b=p.read_bytes();yes('exact regular source/data '+str(p),p.is_file() and not p.is_symlink() and len(b)==row['bytes'] and sha(b)==row['sha256']);return b
def indexed(path,expected):
    p=Path(path);raw=p.read_bytes();yes('fixed index '+str(p),sha(raw)==expected);v=json.loads(raw)
    for r in v['files']:exact_file({**r,'path':str(p.parent/r['path'])})
    return v
def main():
    prerequisites=json.loads((HERE/'prerequisites.json').read_bytes())
    indexed(prerequisites['correctnessSource']['path'],'0124b94f28b20cea7d85c8e7a2619a33099ee98ed56d4920dd5d5749da28cb8c')
    indexed(prerequisites['donorSource']['path'],'d2516c934df3fa8f3ecd58b187cc2bc0f28fab996ab97ada0854e4988d9befeb')
    review=indexed(prerequisites['review']['index']['path'],'e03bb0db65f6009e86a6d55e4553e820d143c702128976efc5ef47e092548083')
    contract=json.loads(exact_file(prerequisites['review']['contract']));yes('stable completed contract exact254',prerequisites['review']['contract']['sha256']=='25411f2ecb278c1eeda7b27a0aafa47b29cc3d9a53221a327e9e5c94002936f1')
    r=json.loads(exact_file(prerequisites['review']['result']))
    for k,v in contract['requiredFixedValues'].items():yes('real prior fixed property '+k,r[k]==v)
    for k,v in contract['requiredCoverage'].items():yes('real prior complete coverage '+k,r['coverage'][k]==v)
    yes('old actual controls remain zero/nonexecuted',r['controlOperations']==0 and r['executedControlWorkloads'] is False)
    derivations=json.loads((HERE/'source-derivations.json').read_bytes());patch=''
    for row in derivations['files']:
        before=Path(row['origin']).read_text();after=(HERE/row['path']).read_text();yes('before '+row['path'],sha(before.encode())==row['beforeSha256']);yes('after '+row['path'],sha(after.encode())==row['afterSha256']);current=before
        for e in row['edits']:
            offsets=[m.start() for m in re.finditer(re.escape(e['old']),current)];yes('exact edit offsets '+row['path'],offsets==e['beforeOffsetsAtEdit'] and len(offsets)==e['count']);current=current.replace(e['old'],e['new'])
        yes('forward exact '+row['path'],current==after);current=after
        for e in reversed(row['edits']):
            shift=0;positions=[]
            for p in e['beforeOffsetsAtEdit']:positions.append(p+shift);shift+=len(e['new'])-len(e['old'])
            for p in reversed(positions):yes('reverse exact slice '+row['path'],current[p:p+len(e['new'])]==e['new']);current=current[:p]+e['old']+current[p+len(e['new']):]
        yes('reverse exact '+row['path'],current==before)
        patch+=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+Path(row['origin']).name,tofile='b/'+row['path']))
    yes('two narrow afterimages and exact unapplied patch',len(derivations['files'])==2 and patch.encode()==(HERE/'control-only.UNAPPLIED.patch').read_bytes())
    guest=(BASE/'cost-guest-oracle-candidate-v2/runtime.mjs').read_text();start=guest.index("if(selected.kind!=='codec')");end=guest.index('\n  let aggregateFNV',start);branch=guest[start:end]
    yes('actual guest control branch reports direct control without invoke/provider', 'controlOperations++' in branch and 'controls[selected.kind](active.window.input)' in branch and 'invoke(' not in branch and 'provider.methods' not in branch)
    worker=(HERE/'worker.mjs').read_text();loader=(HERE/'loading.mjs').read_text();admit=(HERE/'admission.mjs').read_text();run=(HERE/'run.mjs').read_text()
    yes('fresh three arms but no ordinary codec calls in worker',"for(let index=0;index<30;index++)" in worker and "for(const base of[30,60,90])for(let repeat=0;repeat<2;repeat++)" in worker and not re.search(r"call\('(observe|stage|validate)'",worker))
    yes('all observable controls fit exact242/180 counts', 'sequence===242' in worker and 'counts.codecCalls===0' in worker and 'counts.controlOperations===180' in worker)
    yes('control-only scalar surface and ranges are real guard code',"['identity','setup','batch','checkpoint'].includes(name)" in loader and "args[0]>=30&&args[0]<120&&args[1]===1" in loader)
    yes('parent immutable old authority reused only as genuine read-only guard', 'rootAction:completed.oldAuthority' in admit and "await import('../cost-jco-correctness-candidate-v3/admission.mjs')" in admit and admit.index('await completedProof(')<admit.index('await import('))
    yes('own/peer/Root authority before component guard',admit.index('authorityModel(authority,sourceSha)')<admit.index('await correctnessPreflight(') and 'INDEPENDENT_ZLIB_COST_JCO_CONTROL_SOURCE_REVIEW_PASSED_V1' in admit)
    yes('root/prior/output full captured rechecks remain', 'await completed.recheck();await frame.recheck()' in admit and 'for(const row of outputRows)await regular(row' in admit)
    yes('no static action-parent import before authentication',not re.search(r'^export .* from .*candidate-v3/admission',admit,re.M))
    yes('raw terminal before success checks',run.index('for(const path of registered)')<run.index('checkOwned(status)'))
    yes('owned fresh output and exact same-component guard','DurableOutput.create(admitted.outputRoot)' in run and 'same(frame.frames[arm].artifact.component,completed.contract.requiredComponents[arm])' in admit)
    yes('worker cannot reuse another arm path',"local===item.path" in run and 'child(workerRoot,path)' in run)
    template=json.loads((HERE/'root-authority.template.json').read_bytes())
    yes('new source-peer/Root authority still NULL/false',template['controlSourceIndexSha256'] is None and template['sourceIndependentReview'] is None and template['actionAllowed'] is False and template['ordinaryGuestControlCallsAllowed'] is False)
    yes('codec/WT/timing alwaysclosed in new scope',all(template[k] is False for k in ['codecCallsAllowed','nodeCodecCallsAllowed','observeStageValidateAllowed','wasmtimeAllowed','pilotOrTimingAllowed','operationalAdmission','runtimeAcceptanceClaim']))
    return {'schemaVersion':1,'state':'CONTROL_SUPPLEMENT_SOURCE_DATA_CHECKS_PASSED','passed':True,'checks':len(checks),'details':checks,'completedReviewFilesHashed':len(review['files']),'actualControlOrCodecOrLoaderWorkerPreflightOwnerActionExecuted':False}
if __name__=='__main__':
    value=main();p=Path(sys.argv[1]);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x') as f:json.dump(value,f,indent=2);f.write('\n')
    print(json.dumps({k:v for k,v in value.items() if k!='details'}))
