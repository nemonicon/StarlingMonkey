"""Independent source/data review. Never invokes pin actions or native helpers."""
from pathlib import Path
import ast
import copy
import hashlib
import importlib.util
import json
import sys

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'resource-pin-tooling-candidate-v1'
EXPECTED='c55fd0fc10854b853dc57eee77c276857399a4e086d7bac23730b95a1ce66238'
SEED=HERE.parents[1]/'foundation-crypto/independent-ownership-secret-integration-source-review-v1'


def row(p):
    p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))


def main():
    assert __debug__ and sys.dont_write_bytecode
    assert row(SEED/'index.json')['sha256']=='8665997e4edab561a0e0e63235104b8e358072995725002704f25e4499dfca45'
    for r in json.loads((SEED/'index.json').read_bytes())['files']:assert row(SEED/r['path'])==dict(r,path=str(SEED/r['path']))
    spec=importlib.util.spec_from_file_location('genuine_independent_read_hash_only',SEED/'read-source.py');reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
    own=row(SOURCE/'index.json');reader.need(own['sha256']==EXPECTED,'exact c55f seal');reader.family(own)
    freeze=json.loads((SOURCE/'input-freeze.json').read_bytes());refs=json.loads((SOURCE/'references.json').read_bytes())
    reader.need(len(freeze['files'])==1254 and freeze['configuredCopies']==501 and freeze['frozenCopies']==666,'finite source roles')
    for r in freeze['files']:reader.regular(r)
    for r in [refs['resourceSourceIndex'],refs['freezerIndex'],refs['freezerSourceReview']['index'],refs['actualArtifactReview']['index']]:reader.family(r)
    deriv=json.loads((SOURCE/'derivations.json').read_bytes());donor=reader.regular(deriv['donor']).read_text()
    segments={n.name:ast.get_source_segment(donor,n)for n in ast.parse(donor).body if isinstance(n,ast.FunctionDef)}
    parts=[]
    for r in deriv['functions']:
        reader.need(segments[r['name']]==r['text']and hashlib.sha256(r['text'].encode()).hexdigest()==r['sha256'],'genuine f88 function bytes');parts.append(r['text'])
    reader.need(deriv['header']+'\n\n'.join(parts)+'\n'==(SOURCE/'data_io.py').read_text(),'whole exact data-I/O derivation')
    guard=(SOURCE/'guard.py').read_text();nodes={n.name:ast.get_source_segment(guard,n)for n in ast.parse(guard).body if isinstance(n,ast.FunctionDef)}
    reader.need(all(nodes[r['name']]==r['text']for r in deriv['functions']),'actual inline guards same functions')
    receipt=reader.load(refs['freezeReceipt']);metadata=reader.load(refs['metadata']);artifact=reader.load(refs['actualArtifactReview']['result'])
    pure=ast.parse((SOURCE/'pin_model.py').read_bytes());env={'copy':copy}
    for n in pure.body:
        if isinstance(n,ast.Assign):
            reader.need(len(n.targets)==1 and isinstance(n.targets[0],ast.Name),'pure constant binding');env[n.targets[0].id]=ast.literal_eval(n.value)
    exec(compile(ast.Module(body=[n for n in pure.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'<independent actual pin DATA functions>','exec'),env)
    pin=env['candidate'](receipt,metadata,refs,own);candidate=env['unreviewed_document'](pin)
    reader.need(len(pin['frozenFiles'])==666 and len(pin['sourceManifest'])==342 and len(pin['componentizeSourceManifest'])==3 and len(pin['selectedModuleManifests'])==9,'actual full candidate roles')
    reader.need(all(candidate['variants'][k]is None for k in ['normal-runtime','gc-off','disabled-off']),'only normal-off selected')
    reviewed=copy.deepcopy(candidate);reviewed.update(state='ROOT_REVIEWED_SCHEDULER_RESOURCE342_NORMAL_OFF_VALIDATION_PINS_V1',reviewRequired=False);reviewed['variants']['normal-off'].update(state='reviewed-scheduler-resource342-normal-off-freeze-v1',reviewRequired=False)
    export=dict(path='/synthetic/export.json',sha256='a'*64,bytes=1);pair=dict(index={'synthetic':True},result={'synthetic':True})
    review=json.loads((SOURCE/'future-root-pin-review.template.json').read_bytes());review.update(reviewedPinsSha256='b'*64,toolingIndex=own,actualExportCandidate=export,independentExportReview=pair)
    def select(doc,r=review):return env['select_reviewed'](doc,r,pin,'b'*64,export,pair)
    reader.need(select(reviewed)==reviewed['variants']['normal-off'],'whole reviewed-pin pure equivalence')
    def refuses(fn):
        try:fn()
        except (AssertionError,TypeError,KeyError):reader.need(True,'invalid DATA refused')
        else:reader.need(False,'invalid DATA accepted')
    for k in ['engineSha256','metadataSha256','sourceRoot','buildRecipeSha256']:
        bad=copy.deepcopy(reviewed);bad['variants']['normal-off'][k]='wrong';refuses(lambda:select(bad))
    bad=copy.deepcopy(reviewed);bad['variants']['normal-off']['frozenFiles'].pop();refuses(lambda:select(bad))
    bad=copy.deepcopy(reviewed);bad['variants']['gc-off']={};refuses(lambda:select(bad))
    bad=copy.deepcopy(reviewed);bad['runtimeAcceptanceClaim']=True;refuses(lambda:select(bad))
    g=dict(Path=Path,SOURCE=Path(refs['configuredSourceRoot']),FROZEN=Path(refs['freezeRoot']),EXPORT_FILE=Path('/private/tmp/starling-node-compat/scheduler-resource-v1-pin-tooling/export-normal-off-UNREVIEWED.json'),RESOURCE_SHA=refs['resourceSourceIndex']['sha256'],FREEZER_SHA=refs['freezerIndex']['sha256'])
    exec(compile(ast.Module(body=[n for n in ast.parse(guard).body if isinstance(n,ast.FunctionDef)and n.name in ['descriptor','root_model','source_peer_model','artifact_model']],type_ignores=[]),'<independent phase DATA guards>','exec'),g)
    g['artifact_model'](artifact,refs);reader.need(True,'actual80b artifact model')
    template=json.loads((SOURCE/'future-root-authority.template.json').read_bytes());config={'toolingIndex':own}
    refuses(lambda:g['root_model'](template,config,'export'))
    root=copy.deepcopy(template);root.update(state='ROOT_REVIEWED_SCHEDULER_RESOURCE342_PIN_TOOLING_PHASE_V1',phase='export',toolingIndex=own,exportAllowed=True,candidateOutput=str(g['EXPORT_FILE']))
    g['root_model'](root,config,'export');reader.need(True,'finite export phase only')
    refuses(lambda:g['root_model'](root,config,'bootstrap'))
    for k in ['componentAllowed','engineExecutionAllowed','gcReconfigureAllowed','runtimeAcceptanceClaim','sourcePromotionAllowed','metadataProjectionAllowed']:
        bad=dict(root,**{k:True});refuses(lambda:g['root_model'](bad,config,'export'))
    for p in SOURCE.glob('*.py'):ast.parse(p.read_bytes(),filename=str(p));reader.need(True,'actual Python AST')
    reader.need(guard.index("frame['reviewedPin']=pin_model.select_reviewed")<guard.index("model=load_exact(refs['metadataModel']")<guard.index("verifier=load_exact(refs['frozenVerifier']"),'bootstrap gates before genuine helpers')
    reader.need("Path(verifier.__file__).resolve()==Path(refs['frozenVerifier']['path'])and verifier.FREEZE==FROZEN"in guard,'genuine exact verifier context')
    action=(SOURCE/'action.py').read_text();api=(SOURCE/'bootstrap.mjs').read_text()
    reader.need(action.index("names|{'index.json'}")<action.index("spec_from_file_location('resource_pin_phase_guard'"),'complete own source before guard import')
    reader.need('await recheck();return Object.freeze({...deepFreeze(actual),recheck})'in api and 'Whole actual bootstrap frame changed'in api,'whole returned frame stable recheck')
    reader.family(own)
    result=dict(schemaVersion=1,state='INDEPENDENT_SCHEDULER_RESOURCE342_PIN_TOOLING_SOURCE_REVIEW_PASSED_V1',toolingSourceIndexSha256=EXPECTED,resourceSourceIndexSha256=g['RESOURCE_SHA'],freezerSourceIndexSha256=g['FREEZER_SHA'],sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,hostActionsInvoked=False,exportOrBootstrapActionsInvoked=False,checks=reader.checks,uniqueReadHashInputs=len(reader.checked),sourceIndex=own,normalOnly=True,operationalAdmission=False,runtimeAcceptanceClaim=False,limits=['Independent read/hash/AST/pure DATA inspection only; no genuine guard/action/helper/verifier/export/bootstrap call.','Actual exporter, independent export review, validation-only pins, actual bootstrap and independent result review remain required.','No engine/component/guest/timer/resource runtime or adoption proof follows.'])
    (HERE/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    (HERE/'input-hashes.json').write_text(json.dumps(dict(schemaVersion=1,files=[{k:v for k,v in r.items()if k!='identity'}for r in reader.checked.values()]),indent=2)+'\n')
    print(json.dumps(dict(checks=reader.checks,inputs=len(reader.checked),state=result['state'])))


if __name__=='__main__':main()
