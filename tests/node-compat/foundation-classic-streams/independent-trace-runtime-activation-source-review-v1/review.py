"""Read-only source, hash, derivation and saved-evidence checks only."""
from pathlib import Path
import hashlib
import json
import stat

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
REPO=HERE.parents[3]
OWNER=BASE/'trace-runtime-activation-candidate-v1'
EXPECTED='693057a3f90e911e331d8e79f7242816e8f09b354fb78ba4c79f7c18f69649ab'

def sha(data):return hashlib.sha256(data).hexdigest()
def regular(path,digest=None,size=None):
    assert stat.S_ISREG(path.lstat().st_mode) and not path.is_symlink(),path
    h=hashlib.sha256();count=0
    with path.open('rb')as stream:
        while block:=stream.read(1024*1024):h.update(block);count+=len(block)
    assert digest is None or h.hexdigest()==digest,path
    assert size is None or count==size,path
    return {'sha256':h.hexdigest(),'bytes':count}
def load(path):return json.loads(path.read_bytes())
def indexed(root,digest):
    raw=(root/'index.json').read_bytes();assert sha(raw)==digest
    rows=json.loads(raw)['files'];assert len(rows)==len({row['path']for row in rows})
    for row in rows:
        p=Path(row['path']);assert not p.is_absolute()and'..'not in p.parts
        regular(root/p,row['sha256'],row['bytes'])
    return {'sha256':digest,'files':len(rows)}

def main():
    owner=indexed(OWNER,EXPECTED);assert owner['files']==34
    raw=(OWNER/'input-freeze.json').read_bytes();inputs=json.loads(raw)['inputs'];seen=set();total=0
    for row in inputs:
        path=Path(row['path']);assert path.is_absolute()
        assert str(path)not in seen;seen.add(str(path));total+=regular(path,row['sha256'],row['bytes'])['bytes']
    assert len(inputs)==6828
    source=indexed(BASE/'trace-integration-candidate-v1','224fba889e72283d68e5ad01008c91ccfb7970e743a249019856aa43e7422d0b')
    parent=indexed(BASE/'production-runtime-activated-v3','7e9520e0859b939a8586e6d0cfa1fe376a3ace75a2624dd777d5825bbf91cf66')
    trace=indexed(BASE/'stream-trace-regression-candidate-v2','5b40a987b3a2bba08b3192c8a3e3b80a16a32d8de2019c4ecdc9406d3733ef30')
    proof=load(OWNER/'derivations.json');assert len(proof['files'])==3
    reversals=[]
    for row in proof['files']:
        before=(REPO/row['origin']).read_text();after=(OWNER/row['path']).read_text()
        assert sha(before.encode())==row['beforeSha256']and sha(after.encode())==row['afterSha256']
        text=before
        for edit in row['edits']:
            assert text.count(edit['before'])==edit['count'];text=text.replace(edit['before'],edit['after'])
        assert text==after
        for edit in reversed(row['edits']):
            assert text.count(edit['after'])==edit['count'];text=text.replace(edit['after'],edit['before'])
        assert text==before
        reversals.append({'path':row['path'],'edits':len(row['edits']),'forwardAndReverseExact':True})
    inherited=[]
    for path in sorted((OWNER/'payload/harness').iterdir()):
        if path.name!='component-driver.mjs':
            assert path.read_bytes()==(BASE/'production-runtime-activated-v3/harness'/path.name).read_bytes();inherited.append(path.name)
    assert len(inherited)==9
    for name in ['cases.mjs','guest.mjs','node-results.json']:
        assert (OWNER/'payload/trace'/name).read_bytes()==(BASE/'stream-trace-regression-candidate-v2'/name).read_bytes()
    pins=load(OWNER/'runtime-pins.json')
    assert all(value is None for value in pins['variants'].values()) and len(pins['variants'])==4
    assert pins['runtimeAcceptanceClaim']is False
    evidence={name:load(OWNER/'evidence'/name)for name in ['source-tests.json','node-tests.json','syntax-results.json']}
    assert evidence['source-tests.json']['passed']==51 and evidence['node-tests.json']['passed']==12
    syntax=evidence['syntax-results.json'];assert syntax['checks'] and len(syntax['checks'])==18
    assert all(row['exitCode']==0 for row in syntax['checks'])
    gates=load(OWNER/'fresh-gates.json');assert len(gates['gates'])==8 and gates['oldPassReuseAllowed']is False
    for name in ['production-trace-runtime-activated-v1','production-trace-runtime-activated-v1.staging']:
        assert not(BASE/name).exists()and not(BASE/name).is_symlink()
    regular(OWNER/'index.json',EXPECTED)
    result={
      'schemaVersion':1,'state':'INDEPENDENT_CORRECTED_TRACE_RUNTIME_ACTIVATION_SOURCE_REVIEW_PASSED_NO_ACTION_MAINS',
      'owner':owner,'correctedSourceAuthority':source,'inheritedRuntimeSource':parent,'inheritedElevenCaseSource':trace,
      'inputClosure':{'sha256':sha(raw),'files':len(inputs),'bytes':total,'allHashesAndSizesMatch':True},
      'derivations':reversals,'unchangedHarnessFiles':inherited,'unchangedTracePayloadFiles':['cases.mjs','guest.mjs','node-results.json'],
      'manualSourceFindings':{
        'authority':'Caller-supplied expected pin/review digests checked on exact bytes before JSON. Distinct new source states, recipe3694/policy891/helper43b/fix59c and four mode tuples required; old tuple relabelling, null, diagnostic and unreviewed input cannot authorize activation.',
        'genuineArtifactComparison':'Corrected checkout159/342/tool92 are authenticated before importing its exporter function. Each genuine frozen candidate field is compared to reviewed pins except explicit review-state fields; no metadata projection/stripping or exporter main.',
        'twoContexts':'Copied proposal159 is compared byte-exact; preparation1175 is not followed after relocation. Runtime consumed seal maps actual corrected canonical/helper bytes and keeps labelled historical controls separate.',
        'consumedSeal':'Manifest primitive SHA checked before parsing/rows; full selected two-root file membership and22 link bindings inherited with exact target bytes, plus LIVE adapter and new four frozen inventories. Six compiled preflight constants are reconstructed.',
        'runtime':'Pins first, then Root review/whole seal/frozen config+61 native and after-only embedding1. Corrected selector/admission/core imports use the validated stage, not original old repository. Recheck retains private primitive paths/digests and independent frozen-row copies despite mutable returned pin/metadata copies.',
        'publication':'Fresh destination and staging reject existing/symlink paths; every staged payload is exclusively created and rehashed. Authority and external source bytes are rechecked before rename; partial staging is preserved on failure.',
        'harness':'Only reviewed helper/path/provenance changes plus intentional exact Node11 parity gate. Full mismatch report is retained before throw. Nine inherited19/48/17/3/65/GC/fatal/completion semantic files and three trace payload/oracle files are byte-identical.',
        'futureScope':'Fresh full classic and trace gates are required; regression/followon/HTTP and measurement are declared separate future wiring, never silently reused.'},
      'savedEvidenceNotRerun':{'sourceChecks':51,'pureNodeNullAndScratchChecks':12,'syntaxChecks':18},
      'blockers':[],
      'limitations':['All four new runtime pins remain null; output family remains absent.','No activation main, genuine artifact verifier/exporter, positive preflight, Node guest, packager, componentizer, native/compiler/build, target host or timing was executed by this review.','Independent future Root authority and actual freezer verification remain necessary; pure negative/scratch tests are not artifact success.','Reset/ALS/cancellation/failed-instance reuse, VM root isolation and known then-getter/Symbol deviations remain outside the claim.'],
      'runtimeAcceptanceClaim':False,'performanceClaim':False}
    with(HERE/'results.json').open('x')as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps({'state':result['state'],'indexedFiles':34,'consumedInputs':len(inputs),'blockers':0}))

if __name__=='__main__':main()
