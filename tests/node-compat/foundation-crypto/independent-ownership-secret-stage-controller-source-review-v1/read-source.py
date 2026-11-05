"""Independent read/hash/pure review of the dormant owned source-stage caller."""
from pathlib import Path
import ast
import copy
import hashlib
import importlib.util
import json
import stat
import sys

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'ownership-secret-stage-controller-candidate-v1'
EXPECTED='7758e1a722043a3ecc0ba6d3e95eb3a6f53ddf1dcfaa684460c801cf10e60a12'
SEED=HERE.parent/'independent-ownership-secret-integration-source-review-v1'


def row(p):
    p=Path(p); b=p.read_bytes()
    return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))


def main():
    assert __debug__ and sys.dont_write_bytecode
    # Authenticate the genuine finite read/hash helper in its original context.
    ix=row(SEED/'index.json')
    assert ix['sha256']=='8665997e4edab561a0e0e63235104b8e358072995725002704f25e4499dfca45'
    for r in json.loads((SEED/'index.json').read_bytes())['files']:
        assert row(SEED/r['path'])==dict(r,path=str(SEED/r['path']))
    spec=importlib.util.spec_from_file_location('genuine_independent_secret_source_reader',SEED/'read-source.py')
    reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
    own=row(SOURCE/'index.json');reader.need(own['sha256']==EXPECTED,'exact controller seal');reader.family(own)
    refs=json.loads((SOURCE/'references.json').read_bytes())
    for entry in refs['families']:reader.family(entry['index'])
    reader.family(refs['actualIntegrationSourceReview']['index'])
    peer=reader.load(refs['actualIntegrationSourceReview']['result'])
    reader.regular(refs['actualIntegrationSourceReviewContract'])
    for r in json.loads((SOURCE/'checked-inputs.json').read_bytes())['files']:reader.regular(r)
    text=(SOURCE/'controller.py').read_text();tree=ast.parse(text)
    names=['validate_root','validate_integration_peer','validate_controller_peer','expected_copies','validate_terminal','validate_journal']
    defs=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names]
    reader.need(len(defs)==6,'six exact source guard/merger definitions')
    literals={}
    for n in tree.body:
        if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name):
            try:literals[n.targets[0].id]=ast.literal_eval(n.value)
            except ValueError:pass
    repo=Path('/Users/dan/dev/StarlingMonkey');integration=SOURCE.parent/'ownership-secret-integration-candidate-v1';monitor=SOURCE.parent/'ownership-gc-build-controller-candidate-v1'
    env=dict(literals,Path=Path,stat=stat,checked=reader.regular,REPO=repo,OWN=SOURCE,INTEGRATION=integration,MONITOR=monitor,JOURNAL=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-v1-stage.json'),OUT=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-v1-stage-external-root'))
    exec(compile(ast.Module(body=defs,type_ignores=[]),'<independent pure controller definitions>','exec'),env)
    reader.need(env['validate_integration_peer'](peer),'actual integration peer DATA exact shape')
    controller_peer=dict(schemaVersion=1,state='INDEPENDENT_CRYPTO_OWNER355_SECRET_STAGE_CONTROLLER_SOURCE_REVIEW_PASSED_V1',controllerSourceIndexSha256=EXPECTED,integrationSourceIndexSha256=refs['integrationIndex']['sha256'],genericMonitorSourceIndexSha256=refs['monitorIndex']['sha256'],sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,hostActionsInvoked=False,sourceStageActionsInvoked=False)
    reader.need(env['validate_controller_peer'](controller_peer,own),'prospective pure controller peer model')
    def refuses(fn):
        try:fn()
        except (AssertionError,KeyError,TypeError):reader.need(True,'invalid pure model refused')
        else:reader.need(False,'invalid pure model accepted')
    for k,v in [('controllerSourceIndexSha256','f'*64),('integrationSourceIndexSha256','f'*64),('genericMonitorSourceIndexSha256','f'*64),('sourceOnly',False),('ownerActionsInvoked',True),('hostActionsInvoked',True),('sourceStageActionsInvoked',True)]:
        bad=dict(controller_peer,**{k:v});refuses(lambda:env['validate_controller_peer'](bad,own))
    template=json.loads((SOURCE/'root-authority.template.json').read_bytes())
    irefs=json.loads((integration/'references.json').read_bytes())
    refuses(lambda:env['validate_root'](template,own,irefs['sourcePeer']))
    synthetic=dict(template,state='ROOT_REVIEWED_CRYPTO_OWNER355_SECRET_SOURCE_STAGE_V1',sourceIndexSha256=refs['integrationIndex']['sha256'],payloadSourceReview=irefs['sourcePeer'],externalControllerIndex=own,externalControllerEntry=row(SOURCE/'controller.py'),stageEntry=row(integration/'stage.py'),genericMonitorIndex=refs['monitorIndex'],genericMonitorEntry=refs['monitorEntry'],sourceStageAllowed=True)
    reader.need(env['validate_root'](synthetic,own,irefs['sourcePeer']),'prospective pure Root fields only')
    for k in ['nativeBuildAllowed','freezeAllowed','engineExecutionAllowed','keyOperationsAllowed','guestAllowed','gcAllowed','operationalAdmission','runtimeAcceptanceClaim','pinsAdopted','normalMutationAllowed','metadataProjectionAllowed','timingAllowed']:
        bad=dict(synthetic,**{k:True});refuses(lambda:env['validate_root'](bad,own,irefs['sourcePeer']))
    native=json.loads((integration/'native-origins.json').read_bytes())['files'];tools=json.loads((integration/'tool-origins.json').read_bytes())['files']
    family_rows=[refs['integrationIndex'],*[dict(r,path=str(integration/r['path']))for r in json.loads((integration/'index.json').read_bytes())['files']]]
    copies=env['expected_copies'](native,tools,family_rows)
    reader.need(len(copies)==1424 and len({r['path']for r in copies})==1424,'actual source/mode merger1424')
    authority=dict(path='/synthetic/authority.json',sha256='f'*64,bytes=1)
    terminal=dict(schemaVersion=1,authority=authority,rawExitCode=0,parentOwnedGroupGone=True,allObservedOwnedGroupsGone=True,forcedCleanup=False,timeout=False,remainingObservedPids=[],errors=[],interruptedSignals=[],signals=[],stderr={'bytes':0},observedProcesses=[{'syntheticOnly':True}],finalGroups=[{'alive':False}])
    reader.need(env['validate_terminal'](terminal,authority),'pure terminal model only')
    for k,v in [('rawExitCode',1),('allObservedOwnedGroupsGone',False),('forcedCleanup',True),('timeout',True),('signals',['SIGTERM']),('errors',['x']),('remainingObservedPids',[123]),('stderr',{'bytes':1})]:
        bad=dict(terminal,**{k:v});refuses(lambda:env['validate_terminal'](bad,authority))
    reader.need(text.index('frame=authorize(config_row)')<text.index('spec.loader.exec_module(module)')<text.index('OUT.mkdir(mode=0o700)')<text.index('terminal=module.monitor('),'authentication before actual custom import/output/action')
    reader.need("[sys.executable,'-B','-I',str(INTEGRATION/'stage.py'),INTEGRATION_SHA,json.dumps(frame['config']['rootAuthority'],separators=(',',':'))]"in text,'exact genuine stage CLI')
    reader.need("finally:\n        recheck(frame)"in text,'final failure source/protection recheck')
    reader.need("terminal['stdout'],terminal['stderr']"in text and 'journal=descriptor(JOURNAL)'in text,'raw streams before journal validation')
    reader.need("setattr("not in text and '__dict__'not in text and 'module.monitor(argv,str(REPO)'in text,'no old module/global interception')
    monitor_text=reader.regular(refs['monitorEntry']).read_text();monitor_ast=ast.parse(monitor_text)
    monitor_fn=next(n for n in monitor_ast.body if isinstance(n,ast.FunctionDef)and n.name=='monitor')
    reader.need([a.arg for a in monitor_fn.args.args]==json.loads((SOURCE/'api-bindings.json').read_bytes())['monitorPositionalParameters'],'actual generic monitor API')
    for p in SOURCE.rglob('*.py'):ast.parse(p.read_bytes(),filename=str(p));reader.need(True,'actual controller Python AST')
    for key in ['SOURCE','WORK','FREEZE']:reader.need(not Path(literals[key]).exists(),'actual future phase path absent')
    reader.need(not env['OUT'].exists() and not env['JOURNAL'].exists(),'no actual stage output/journal')
    reader.family(own)
    result=dict(controller_peer,controllerSourceIndex=own,checks=reader.checks,uniqueReadHashInputs=len(reader.checked),dynamicStageCopies=1424,baseStageRows=1403,nativeSourceFiles=355,unchangedParentNativeFiles=352,changedNativeFiles=3,normalFrozenMembers=1391,normalOriginalReferences=1387,operationalAdmission=False,helperImported=False,genericMonitorImported=False,processesStarted=False,compilerInvoked=False,engineExecuted=False,limits=['Read/hash/AST and extracted pure contracts only; no positive actual authorization or stage.','Synthetic Root/peer/terminal data are never action authorities.','Future actual staging requires fresh Root config, full genuine admission and independent raw result review before any build.'])
    (HERE/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    (HERE/'input-hashes.json').write_text(json.dumps(dict(schemaVersion=1,files=[{k:v for k,v in r.items()if k!='identity'}for r in reader.checked.values()]),indent=2)+'\n')
    print(json.dumps(dict(checks=reader.checks,inputs=len(reader.checked),dynamicStageCopies=1424)))


if __name__=='__main__':main()
