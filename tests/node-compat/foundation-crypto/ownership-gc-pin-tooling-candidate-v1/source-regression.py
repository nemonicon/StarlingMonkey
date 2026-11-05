"""Data/pure AST checks only; no helper, process, export, bootstrap or engine calls."""
from pathlib import Path
import ast,copy,hashlib,json,types
O=Path(__file__).resolve().parent;K=O.parent;N=K/'ownership-gc-native-candidate-v2';H=K/'ownership-gc-freezer-helper-amendment-v1'
checks=[]
def ok(name,v):assert v,name;checks.append(dict(name=name,passed=True))
def no(name,fn):
 try:fn()
 except (AssertionError,KeyError,TypeError,ValueError):ok(name,True)
 else:raise AssertionError('accepted '+name)
def extract(path,names,extra):
 tree=ast.parse(path.read_bytes());nodes=[]
 for n in tree.body:
  if isinstance(n,ast.FunctionDef)and n.name in names:nodes.append(n)
  if isinstance(n,ast.Assign)and isinstance(n.value,ast.Constant)and all(isinstance(x,ast.Name)for x in n.targets):nodes.append(n)
 env=dict(extra);exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),env);return env
const=dict(OWN=O,NATIVE_SHA='ed0665046ec293b846069df0c050a388b1d717abbf4a0e56c64d8bd17d9a6d05',SOURCE='/private/tmp/starling-node-compat/crypto-owner355-gc-v2-source',WORK='/private/tmp/starling-node-compat/crypto-owner355-gc-v2-build',FREEZE='/private/tmp/starling-node-compat/crypto-owner355-gc-v2-freeze',TOOLS='/private/tmp/starling-node-compat/crypto-owner355-gc-v2-source/tests/node-compat/foundation-crypto/native-integration-candidate-v2/artifact-tools',BUILD_OUTPUT='/private/tmp/starling-node-compat/crypto-owner355-gc-v2-build-root')
ni=dict(path=str(N/'index.json'),sha256=const['NATIVE_SHA'],bytes=4777);ti=dict(path=str(O/'index.json'),sha256='a'*64,bytes=1);nr=dict(path='new-native-root',sha256='b'*64,bytes=1);tr=dict(path='new-tooling-root',sha256='c'*64,bytes=1)
entry=dict(path=str(O/'action.py'),sha256='d'*64,bytes=1);ctrl=dict(path=str(O/'controller.py'),sha256='e'*64,bytes=1);pair=dict(index=dict(path='future/index.json'),result=dict(path='future/result.json'))
config=dict(sourceIndex=ni,rootAuthority=nr,toolingIndex=ti,toolingRootAuthority=tr)
family=lambda row:[entry,ctrl]
e=extract(O/'guard.py',{'validate_phase','validate_artifact','validate_export_proof','select_helper','provenance','recheck_frame','protect_output'},{'Path':Path,'family':family,**const})
for phase in ('export','bootstrap'):
 value=json.loads((O/('future-'+phase+'-tooling-root.template.json')).read_bytes())
 value.update(state='ROOT_REVIEWED_CRYPTO_OWNER355_GC_PIN_TOOLING_PHASE_V1',nativeSourceIndexed=ni,toolingIndexed=ti,nativeRootAuthority=nr,nativePhaseEntry=entry,externalControllerIndex=ti,externalControllerEntry=ctrl,independentSourceReview=pair,artifactReview=pair)
 value[phase+'Allowed']=True
 native=json.loads((O/('future-'+phase+'-native-root.template.json')).read_bytes());native.update(pinToolingEntry=entry,pinToolingSourceIndex=ti,pinToolingReview=pair,independentGcNativeReview=pair);native[phase+'Allowed']=True
 if phase=='export':value['pinCandidateOutput']=native['pinCandidateOutput']=const['BUILD_OUTPUT']+'/gc-pin.UNREVIEWED.json'
 else:
  value['reviewedGcPins']=native['reviewedGcPins']=dict(path='future-gc-only-pins');value['gcNativeRootReview']=native['gcNativeRootReview']=dict(path='future-root-gc-only-review');value['actualExportReview']=pair
 e['validate_phase'](value,config,native,phase);ok('valid separate phase fixture '+phase,True)
 for key in ('toolingIndexed','nativeSourceIndexed','nativeRootAuthority','artifactReview','externalControllerIndex','externalControllerEntry','configuredSourceRoot','freezeRoot','nativePhaseEntry'):
  v=copy.deepcopy(value);v[key]={};no(phase+' mismatched '+key,lambda v=v:e['validate_phase'](v,config,native,phase))
 v=copy.deepcopy(value);v['guestAllowed']=True;no(phase+' no guest grant',lambda:e['validate_phase'](v,config,native,phase))
 v=copy.deepcopy(value);v['engineExecutionAllowed']=True;no(phase+' no engine grant',lambda:e['validate_phase'](v,config,native,phase))
 v=copy.deepcopy(value);v['bootstrapAllowed']=v['exportAllowed']=True;no(phase+' rejects joint phase grant',lambda:e['validate_phase'](v,config,native,phase))
 n=copy.deepcopy(native);n['phase']='freeze';no(phase+' cannot relabel old native freeze grant',lambda:e['validate_phase'](value,config,n,phase))
 n=copy.deepcopy(native);n['pinToolingSourceIndex']=ni;no(phase+' old native index cannot be tooling index',lambda:e['validate_phase'](value,config,n,phase))
 if phase=='export':
  v=copy.deepcopy(value);v['actualExportReview']=pair;no('export not a reviewed export',lambda:e['validate_phase'](v,config,native,phase))
 else:
  v=copy.deepcopy(value);v['actualExportReview']=None;no('bootstrap requires actual export review',lambda:e['validate_phase'](v,config,native,phase))
freeze=json.loads((K/'ownership-gc-v2-freeze-helper-v1-root-results.json').read_bytes());receipt=freeze['freezeReceipt']
proof=dict(schemaVersion=1,state='INDEPENDENT_CRYPTO_OWNER355_GC_NATIVE_ARTIFACT_REVIEW_PASSED_V1',verifiedPassed=True,sourceIndexSha256=ni['sha256'],nativeSourceFiles=355,variant='gc-off',engineSha256=freeze['engineSha256'],freezeReceiptSha256=receipt['sha256'])
root=dict(engine=dict(sha256=freeze['engineSha256'],bytes=freeze['engineBytes']),metadata=dict(sha256=freeze['metadataSha256']))
e['validate_artifact'](proof,root,freeze,receipt);ok('full frozen artifact tuple fixture',True)
for key,value in [('state','INDEPENDENT_CRYPTO_OWNER355_GC_NATIVE_BUILD_REVIEW_PASSED_V1'),('sourceIndexSha256',ti['sha256']),('nativeSourceFiles',350),('engineSha256','0'*64),('freezeReceiptSha256','0'*64),('verifiedPassed',False)]:
 p=copy.deepcopy(proof);p[key]=value;no('artifact refuses wrong '+key,lambda p=p:e['validate_artifact'](p,root,freeze,receipt))
export=dict(schemaVersion=1,state='INDEPENDENT_CRYPTO_OWNER355_GC_PIN_EXPORT_REVIEW_PASSED_V1',verifiedPassed=True,sourceIndexSha256=ti['sha256'],nativeSourceIndexSha256=ni['sha256'],independentNativeArtifactReview=pair,candidate=dict(path=const['BUILD_OUTPUT']+'/gc-pin.UNREVIEWED.json'),engineExecuted=False,operationalAdmission=False,pinsAdopted=False)
e['validate_export_proof'](export,ti,pair);ok('future independent export proof finite fixture',True)
for key,value in [('state','UNREVIEWED_CRYPTO_OWNER355_ISOLATED_GC_PIN_CANDIDATE_V1'),('sourceIndexSha256',ni['sha256']),('pinsAdopted',True),('engineExecuted',True),('independentNativeArtifactReview',{})]:
 p=copy.deepcopy(export);p[key]=value;no('bootstrap refuses export '+key,lambda p=p:e['validate_export_proof'](p,ti,pair))
# Exact11-row selector with byte-identical reviewed09 function source.
def source(p,name):return next(ast.get_source_segment(p.read_text(),n)for n in ast.parse(p.read_bytes()).body if isinstance(n,ast.FunctionDef)and n.name==name)
ok('selector byte-identical to reviewed09 API',source(O/'guard.py','select_helper')==source(H/'amendment-guard.py','select_helper'))
inputs=json.loads((N/'stage-inputs.json').read_bytes());selected=e['select_helper'](inputs,const['SOURCE'],const['TOOLS'],'/private/tmp/starling-node-compat/crypto-owner-source-v2')
ok('selected actual crypto helper digest',selected['sha256']=='fff7bed72aec0c592e7a788060a5c1ecf6a0b0694ca519dbfa00e230584123ab'and selected['bytes']==19299)
ok('all eleven suffix matches remain',len([r for r in inputs['files']if r['path'].endswith('/artifact-tools/artifact_common.py')])==11)
row=next(r for r in inputs['files']if r['path']==e['NATIVE_RELATIVE'])
for files,label in [([r for r in inputs['files']if r!=row],'missing'),(inputs['files']+[row],'duplicate')]:no('selector refuses '+label,lambda f=files:e['select_helper'](dict(files=f),const['SOURCE'],const['TOOLS'],'/private/tmp/starling-node-compat/crypto-owner-source-v2'))
# Genuine candidate body unchanged; thin bootstrap bodies reverse exactly.
ok('export candidate entire bytes unchanged',(O/'export-body.py').read_bytes()==(N/'export-body.py').read_bytes())
for name,donor,proofname in [('bootstrap-body.py',N/'bootstrap.py','bootstrap-body-derivation.json'),('bootstrap.mjs',N/'bootstrap.mjs','bootstrap-js-derivation.json')]:
 text=(O/name).read_text();d=json.loads((O/proofname).read_bytes())
 for r in reversed(d['changes']):assert text.count(r['after'])==1;text=text.replace(r['after'],r['before'])
 ok('exact reversal '+name,text==donor.read_text())
# Dual frame rechecks are exact source functions with mock guards only.
calls=[];native=types.SimpleNamespace(recheck=lambda f:calls.append('native'))
tool=dict(index=ti,rootAuthority=tr,captured=[dict(path='config')],families=[],protection={},expectedCandidate=None,phase='export',independentSourceReview=pair,artifactReview=pair,actualExportReview=None)
f=dict(sourceIndex=ni,rootAuthority=nr,toolingFrame=tool,_nativeGuard=native,selectedCommonHelper=selected)
r=extract(O/'guard.py',{'recheck_frame','provenance'},{'read':lambda row:config,'recheck':lambda a,b:calls.append('tooling'),'protect_output':lambda a,b:calls.append('protected'),**const})
r['recheck_frame'](f);ok('native tooling and output protection all rechecked',calls==['native','tooling','protected'])
p=r['provenance'](f);ok('separate native and tooling provenance',p['nativeSourceIndexed']==ni and p['toolingIndexed']==ti and p['nativeRootAuthority']==nr and p['toolingRootAuthority']==tr)
ok('provenance does not adopt pins',p['engineExecuted']is False and p['operationalAdmission']is False)
f2=copy.copy(f);f2['sourceIndex']=ti;no('frame cannot retarget native source to tooling',lambda:r['recheck_frame'](f2))
# Build-output membership model has only fake Path/checked, no real file writes.
protection=json.loads((O/'build-output-protection.json').read_bytes())
class P:
 names={'build.log','launch.json','result.json'}
 def __init__(self,path):self.p=Path(path)
 @property
 def name(self):return self.p.name
 @property
 def parent(self):return P(self.p.parent)
 def __str__(self):return str(self.p)
 def is_file(self):return True
 def is_symlink(self):return False
 def iterdir(self):return[P(self.p/x)for x in self.names]
c=[];pe=extract(O/'guard.py',{'protect_output'},{'Path':P,'checked':lambda row:c.append(row),**const})
pe['protect_output'](protection);ok('existing three build files protected',len(c)==3)
P.names|={'gc-pin.UNREVIEWED.json'}
no('export refuses preexisting candidate',lambda:pe['protect_output'](protection))
pe['protect_output'](protection,dict(path=const['BUILD_OUTPUT']+'/gc-pin.UNREVIEWED.json'));ok('only explicit named candidate addition allowed',True)
P.names|={'extra'};no('unexpected additional build file refused',lambda:pe['protect_output'](protection,dict(path=const['BUILD_OUTPUT']+'/gc-pin.UNREVIEWED.json')))
# Static whole caller graph and actual contracts; no owner function imports.
g=(O/'guard.py').read_text();a=(O/'action.py').read_text();b=(O/'bootstrap-body.py').read_text();j=(O/'bootstrap.mjs').read_text();c=(O/'controller.py').read_text()
for name,value in [
 ('genuine native guard imported only after full recheck',g.index('recheck(captured,families)')<g.index("spec_from_file_location('genuine_crypto_gc_native_guard'")),
 ('genuine old broken loader never called','native.load_common'not in g and 'guard.load_common'not in b),
 ('actual common path checked before import',g.index('row=select_helper(')<g.index("'genuine_staged_crypto_pin_tooling_common'")),
 ('genuine common context asserted without rebinding','common.HERE=='in g and 'common.REPO=='in g and 'common.OUTPUT=='in g and 'common.HERE='not in g.replace('common.HERE==','') and 'common.REPO='not in g.replace('common.REPO==','') and 'common.OUTPUT='not in g.replace('common.OUTPUT==','')),
 ('native source frame not reassigned',not any(isinstance(n,ast.Assign)and any(isinstance(t,ast.Subscript)and isinstance(t.value,ast.Name)and t.value.id=='frame'and isinstance(t.slice,ast.Constant)and t.slice.value=='sourceIndex'for t in n.targets)for n in ast.walk(ast.parse(g)))),
 ('export is exclusive genuine data_io write','from data_io import write'in a and 'created=write(output,document)'in a),
 ('candidate remains native unreviewed document',"UNREVIEWED_CRYPTO_OWNER355_ISOLATED_GC_PIN_CANDIDATE_V1"in a and 'requiresIndependentReviewAndNewRootNativeReview=True'in a),
 ('both action phases finally recheck','finally:\n        guard.recheck_frame(frame)'in a),
 ('bootstrap genuine native pin model import','from pin_model import select'in b),
 ('bootstrap genuine frozen verification before and after','common.verify_frozen_variant'in b and 'Full actual GC freeze changed during selector/manifest reads'in b),
 ('full actual body metadata and manifests returned','metadata=metadata,selectedManifests=manifests'in b and 'toolingProvenance=tooling_guard.provenance(frame)'in b),
 ('JS native index does not equal tooling HERE','config.sourceIndex'in j and 'config.toolingIndex'in j and 'v.sourceIndexSha256,nativeIx.sha256'in j),
 ('JS API correct no-guest direct bootstrap action',"action.py'),'bootstrap'"in j and '120000'in j and 'maxBuffer:16*1024*1024'in j),
 ('JS recheck reruns whole actual frame','JSON.stringify(await execute()),stable'in j),
 ('outer monitor after full phase guard',c.index('frame=guard.authorize(config_row,phase)')<c.index("'reviewed_gc_pin_owned_monitor'")),
 ('outer monitor genuine2400 lifecycle',',out,2400,config[\'rootAuthority\']'in c and "terminal['remainingObservedPids']==[]"in c and "terminal['forcedCleanup']is False"in c),
 ('new external roots per explicit phase','crypto-owner355-gc-pin-tooling-v1-'+"'+phase+'-external-root'"in g)
]:ok(name,value)
syntax=[]
for path in sorted(O.glob('*.py')):ast.parse(path.read_bytes());syntax.append(path.name)
result=dict(schemaVersion=1,state='PURE_SOURCE_DATA_GC_PIN_TOOLING_REGRESSION_PASSED_V1',checks=checks,count=len(checks),pythonAst=syntax,sourceOnly=True,ownerModulesImported=False,allNativeCallsMockedOrStatic=True,processesSpawned=False,helpersInvoked=False,exportInvoked=False,bootstrapInvoked=False,engineExecuted=False)
(O/'source-regression-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(checks=len(checks),pythonAst=len(syntax))))
