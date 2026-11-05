"""Independent data/AST/pure review; never imports the build or lifecycle owner."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import sys

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'ownership-secret-build-controller-candidate-v1'
SEED=HERE.parent/'independent-ownership-secret-integration-source-review-v1'
EXPECTED='c9573e416c76350a6ab169b0d5ddb2938883e9698620759b4285ee7a2fde3643'


def row(p):
    p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))


def main():
    assert __debug__ and sys.dont_write_bytecode
    assert row(SEED/'index.json')['sha256']=='8665997e4edab561a0e0e63235104b8e358072995725002704f25e4499dfca45'
    for r in json.loads((SEED/'index.json').read_bytes())['files']:assert row(SEED/r['path'])==dict(r,path=str(SEED/r['path']))
    spec=importlib.util.spec_from_file_location('genuine_independent_build_source_data_reader',SEED/'read-source.py');reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
    own=row(SOURCE/'index.json');reader.need(own['sha256']==EXPECTED,'exact new source seal');reader.family(own)
    refs=json.loads((SOURCE/'references.json').read_bytes())
    for f in refs['families']:reader.family(f['index'])
    for r in json.loads((SOURCE/'checked-inputs.json').read_bytes())['files']:reader.regular(r)
    for r in refs['files']:reader.regular(r)
    for k in ['integrationSourceReview','actualStageReview']:
        reader.family(refs[k]['index']);reader.load(refs[k]['result'])
    reader.regular(refs['actualStageReviewContract'])
    journal=reader.load(refs['actualStageJournal'])
    reader.need(len(journal['copies'])==1424,'actual stage copy1424')
    for r in journal['copies']:
        original=reader.regular(dict(path=r['original'],sha256=r['sha256'],bytes=r['bytes']))
        target=reader.regular(dict(path='/private/tmp/starling-node-compat/crypto-owner355-secret-v1-source/'+r['path'],sha256=r['sha256'],bytes=r['bytes']))
        reader.need((original.stat().st_dev,original.stat().st_ino)!=(target.stat().st_dev,target.stat().st_ino),'distinct actual source copies')
        reader.need(original.stat().st_mode&0o7777==target.stat().st_mode&0o7777==r['sourceMode'],'actual stage modes')
    text=(SOURCE/'controller.py').read_text();tree=ast.parse(text)
    names=['validate_terminal','validate_root','validate_source_peer','validate_stage','validate_controller_peer','validate_new_metadata']
    funcs=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names]
    reader.need(len(funcs)==6,'six actual typed guard definitions')
    constants={}
    for n in tree.body:
        if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name):
            try:constants[n.targets[0].id]=ast.literal_eval(n.value)
            except ValueError:pass
    repo=Path('/Users/dan/dev/StarlingMonkey')
    env=dict(constants,REPO=repo,OWN=SOURCE,BUILD_OUTPUT=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-v1-normal-off-build-root'),OUT=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-v1-normal-off-build-external-root'))
    exec(compile(ast.Module(body=funcs,type_ignores=[]),'<independent pure build source guards>','exec'),env)
    env['validate_source_peer'](reader.load(refs['integrationSourceReview']['result']));reader.need(True,'actual integration peer DATA')
    env['validate_stage'](reader.load(refs['actualStageReview']['result']),reader.load(refs['stageRootObservation']),refs);reader.need(True,'actual stage peer and literal Rootcaller1 DATA')
    peer=dict(schemaVersion=1,state='INDEPENDENT_CRYPTO_OWNER355_SECRET_BUILD_CONTROLLER_SOURCE_REVIEW_PASSED_V1',controllerSourceIndexSha256=EXPECTED,integrationSourceIndexSha256=refs['integrationIndex']['sha256'],actualStageReviewIndexSha256=refs['actualStageReview']['index']['sha256'],genericMonitorSourceIndexSha256=refs['monitorIndex']['sha256'],sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,hostActionsInvoked=False,nativeBuildActionsInvoked=False)
    env['validate_controller_peer'](peer,own,refs);reader.need(True,'prospective source peer pure seam only')
    def refuses(fn):
        try:fn()
        except (AssertionError,KeyError,TypeError):reader.need(True,'invalid pure guard refused')
        else:reader.need(False,'invalid pure guard accepted')
    for k,v in [('controllerSourceIndexSha256','f'*64),('actualStageReviewIndexSha256','f'*64),('sourceOnly',False),('sourceReviewPassed',False),('ownerActionsInvoked',True),('hostActionsInvoked',True),('nativeBuildActionsInvoked',True)]:
        bad=dict(peer,**{k:v});refuses(lambda:env['validate_controller_peer'](bad,own,refs))
    template=json.loads((SOURCE/'root-authority.template.json').read_bytes());refuses(lambda:env['validate_root'](template,own,refs))
    # Bind actual API AST names from indexed source, never a guessed signature.
    api=json.loads((SOURCE/'api-bindings.json').read_bytes());lifecycle=reader.regular(refs['lifecycleEntry']).read_text();ltree=ast.parse(lifecycle)
    defs={n.name:n for n in ltree.body if isinstance(n,ast.FunctionDef)}
    for entry in api['actualExplicitLifecycleApis']:
        node=defs[entry['name']]
        reader.need([a.arg for a in node.args.args]==entry['positionalParameters'],'actual lifecycle positional API')
        reader.need([a.arg for a in node.args.kwonlyargs]==entry['keywordOnlyParameters'],'actual lifecycle keyword API')
    reader.need(all(not isinstance(n,ast.ImportFrom)or n.module!='artifact_common'for n in ltree.body),'old artifact common not imported at module scope')
    reader.need("lifecycle.RECIPE_SHA256==refs['lifecycleDormantRecipeSha256']"in text and "actualRecipeSha256=refs['recipe']['sha256']"in text,'distinct donor and actual recipe identities')
    reader.need("lifecycle.prepare_output(BUILD_OUTPUT,free)"in text and "lifecycle.monitor_owned_command(command,SOURCE,environment,log,free)"in text and "lifecycle.publish_result(BUILD_OUTPUT,result,writer=write)"in text,'actual explicit lifecycle arguments')
    reader.need("if cleanup.get('events')or cleanup.get('errors')or cleanup.get('complete')is not True:"in text,'inner forced cleanup refuses success')
    reader.need("finally:\n        recheck(frame)  # Includes import/output/pre-launch and result-reader failure paths."in text,'unconditional mode-level recheck')
    assignments=[]
    for n in ast.walk(tree):
        if isinstance(n,(ast.Assign,ast.AugAssign,ast.AnnAssign)):
            targets=n.targets if isinstance(n,ast.Assign)else[n.target]
            assignments += [ast.unparse(x)for x in targets]
    reader.need(not any(t.startswith(('lifecycle.','monitor.'))for t in assignments),'no donor global rebinding')
    reader.need('lifecycle.main('not in text and 'artifact_common'not in '\n'.join(ast.unparse(n)for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom))),'no old main/common calls')
    for p in SOURCE.glob('*.py'):ast.parse(p.read_bytes(),filename=str(p));reader.need(True,'actual Python AST')
    for k in ['WORK','FREEZE']:reader.need(not Path(constants[k]).exists(),'native phase path absent')
    reader.need(not env['BUILD_OUTPUT'].exists()and not env['OUT'].exists(),'no native action outputs')
    reader.family(own)
    result=dict(peer,controllerSourceIndex=own,checks=reader.checks,uniqueReadHashInputs=len(reader.checked),nativeSourceFiles=355,unchangedParentNativeFiles=352,changedNativeFiles=3,stageCopies=1424,normalOnly=True,requiredStartFreeBytes=2147483648,stopBelowFreeBytes=838860800,parallelBuilds=1,operationalAdmission=False,runtimeAcceptanceClaim=False,helperImported=False,monitorOrLifecycleImported=False,nativeBuildExecuted=False,engineExecuted=False,limits=['Read/hash/AST/extracted pure source guards only; no positive actual controller authorization or build.','Native compilation, actual metadata/codec/link/archive evidence, freeze and result reviews remain required.','Source controls do not prove allocation faults, crypto algorithms, frees/wipes, runtime ownership or Node crypto APIs.'])
    (HERE/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    (HERE/'input-hashes.json').write_text(json.dumps(dict(schemaVersion=1,files=[{k:v for k,v in r.items()if k!='identity'}for r in reader.checked.values()]),indent=2)+'\n')
    print(json.dumps(dict(checks=reader.checks,inputs=len(reader.checked),state=result['state'])))


if __name__=='__main__':main()
