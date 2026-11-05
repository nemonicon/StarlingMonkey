#!/usr/bin/env python3
"""Finite source/data/hash checker. Never imports an owner action/helper."""
import hashlib,json,os,stat,difflib,ast
from pathlib import Path
D=Path(__file__).resolve().parent;checks=[]
def need(v,m):
 if not v:raise AssertionError(m)
 checks.append(m)
def h(path):
 v=hashlib.sha256()
 with Path(path).open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):v.update(b)
 return v.hexdigest()
p=json.loads((D/'prerequisites.json').read_bytes());c=json.loads((D/'closure.json').read_bytes());need(c['state']=='FINITE_ORIGINAL_CONTEXT_355_HTTP_PHYSICAL_CLOSURE'and len(c['files'])==len({r['path']for r in c['files']}),'unique complete closure')
for r in c['files']:
 s=Path(r['path']).lstat();need(stat.S_ISREG(s.st_mode)and not stat.S_ISLNK(s.st_mode)and s.st_size==r['bytes']and h(r['path'])==r['sha256'],'actual finite closure '+r['path'])
for r in c['toolLinks']:need(Path(r['path']).is_symlink()and os.readlink(r['path'])==r['linkText']and str(Path(r['path']).resolve())==r['resolvedTarget'],'exact actual npm link')
need(len(c['liveInputs'])==8 and sum('/wit/deps/'in r['name']for r in c['liveInputs'])==7,'complete live8 WIT/adapter capture')
for r in json.loads((D/'copied-mechanisms.json').read_bytes())['rows']:need((D/r['afterimage']).read_bytes()==Path(r['origin']['path']).read_bytes()and h(r['origin']['path'])==r['origin']['sha256'],'byte-identical mechanism/probe '+r['afterimage'])
need(Path(p['baselineSource']['path']).read_bytes()==Path(p['actualAcceptedBaselineSource']['path']).read_bytes(),'unchanged actual accepted baseline guest body')
v=json.loads((D/'virtual-data-derivation.json').read_bytes());source=Path(v['origin']['path']).read_text();block=source[v['originStartUtf16Offset']:v['originEndUtf16Offset']];need(hashlib.sha256(block.encode()).hexdigest()==v['exactOriginalSemanticBlockSha256']and block in(D/'virtual-data.mjs').read_text(),'exact old full fixture/oracle semantic block reused')
guard=(D/'admission.mjs').read_text();worker=(D/'worker.mjs').read_text();parent=(D/'run.mjs').read_text();need("import(pathToFileURL(bridge))"in guard and "validationPreflight({variant:'normal-runtime'})"in guard and 'selectedManifestsForEngine('not in worker and 'selectCoreExpectations('not in worker and 'verifyProductionTicks('not in worker,'actual inner355 bridge/manifests/core replace old guards')
need('d.frame.selectedManifests'in worker and 'd.frame.coreExpectations'in worker and 'sourceManifest.length===355'in worker,'full actual355 frame, not subset')
need(parent.index("mkdir(join(output.root,'processes'),{mode:0o700})")<parent.index('await runOwnedCommand('),'processes0700 caller precondition before unchanged lifecycle')
need('createConsumersHTTPPlugin(paths)'in worker and 'selectedInterfaces:expected.outerImports'in worker and 'componentizeSelectedHTTP('in worker and 'componentNew(core,[],false)'in worker,'real actual HTTP bundler/stubber/final-wrap seams')
need('await output.write(\'http.bundle.mjs\''in worker and worker.index("await output.write('http.bundle.mjs'")<worker.index("Exact18 native/standard imports"),'full bundle data before graph checks')
need('verifyLiveInputs(closure)'in worker and 'wit/deps/'in worker and "componentizerInvoked:d.action==='component-build'"in worker,'explicit bundle/build split and full live8 check')
need('if(d.action===\'bundle-source\')'in worker and 'd.actualBundle?.bundle'in worker and 'Separate actual reviewed whole-entry bundle required'in guard,'actual bundle review mandatory before package')
need('old342'not in(D/'future-construction-action.template.json').read_text()and json.loads((D/'future-construction-action.template.json').read_bytes())['actionAllowed']is False,'new action/template remains closed')
# Genuine Python source authority model only: extract this pure definition, no
# module import (and no publisher/copy main or dependencies are executed).
text=(D/'publish.py').read_text();tree=ast.parse(text);function=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='authority_model');namespace={'require':lambda v,m:None if v else(_ for _ in()).throw(ValueError(m)),'OUTPUT':'/private/tmp/starling-node-compat/consumers355-http-source-v1'};exec(compile(ast.Module(body=[function],type_ignores=[]),'<pure-authority-model>','exec'),namespace)
a={'schemaVersion':1,'state':'ROOT_REVIEWED_CONSUMERS355_HTTP_SOURCE_PUBLICATION_V1','sourceIndexSha256':'a'*64,'sourcePublicationAllowed':True,'outputRoot':namespace['OUTPUT'],'runtimeActionsAllowed':False,'operationalAdmission':False,'sourcePromotionAllowed':False,'sourceIndependentReview':{}}
need(namespace['authority_model'](a,'a'*64),'pure finite source authority positive DATA')
for k,value in [('state','OLD_RELEASE_SCOPE'),('sourcePublicationAllowed',False),('runtimeActionsAllowed',True),('outputRoot','/tmp/arbitrary'),('sourceIndependentReview',None)]:
 try:namespace['authority_model']({**a,k:value},'a'*64)
 except ValueError:checks.append('pure source authority refusal '+k)
 else:raise AssertionError(k)
print(json.dumps({'schemaVersion':1,'state':'HTTP355_SOURCE_DATA_CHECKS_PASSED','checks':len(checks),'fullClosureFiles':len(c['files']),'genuineHelpersInvoked':False,'publisherMainInvoked':False,'bundleComponentGuestOrHostInvoked':False}))
