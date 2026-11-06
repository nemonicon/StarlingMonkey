"""Bounded independent Source delta DATA/AST/pure checks; no operational imports."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,os,re,sys
sys.dont_write_bytecode=True
S=Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-scheduler');SOURCE=S/'combined-clock-diagnostics-native-integration-candidate-v3';PARENT=S/'combined-clock-diagnostics-native-integration-candidate-v2';seen={};checks=[]
def need(n,x):assert x,n;checks.append(n)
def row(p):
 p=Path(p);b=p.read_bytes();r=dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b));seen[str(p)]=r;return r

def verify(r):need('hash '+r['path'],row(r['path'])==r)
def read(p):return json.loads(Path(p).read_bytes())
def family(index):
 verify(index);base=Path(index['path']).parent;ix=read(index['path']);names=['index.json']
 for r in ix['files']:
  need('safe member '+r['path'],r['path']not in names and not Path(r['path']).is_absolute()and'..'not in Path(r['path']).parts);names.append(r['path']);verify(dict(r,path=str(base/r['path'])))
 need('closed family '+str(base),sorted(str(p.relative_to(base))for p in base.rglob('*')if p.is_file())==sorted(names));return ix
own=row(SOURCE/'index.json');need('actual V3 pin',own['sha256']=='3beebcf7a52d0bcf92ce7da16846993c38fea14ce3a1827c27796777ecc2f1ac');ix=family(own);refs=read(SOURCE/'references.json');parent=refs['parentProducerIndex'];px=family(parent);hold=refs['manifestOrderHoldIndex'];hx=family(hold);need('shared original parent',refs['sharedDataIndex']==parent and parent in refs['families']and hold in refs['families'])
for k in ['copyPlan','cachePlan','protectedInputs']:
 verify(refs[k]);need('shared exactly indexed '+k,sum(dict(r,path=str(PARENT/r['path']))==refs[k]for r in px['files'])==1)
for k in ['controller','recipe','helper','policy','metadataModel']:
 verify(refs[k]);need('own exactly indexed '+k,sum(dict(r,path=str(SOURCE/r['path']))==refs[k]for r in ix['files'])==1)
d=read(SOURCE/'derivations.json');editgroups=0
for f in d['files']:
 verify(f['before']);verify(f['after']);old=Path(f['before']['path']).read_bytes();new=Path(f['after']['path']).read_bytes();work=old
 for e in f['edits']:
  a=e['before'].encode();b=e['after'].encode();need('forward count '+f['path'],work.count(a)==e['count']);work=work.replace(a,b);editgroups+=1
 need('whole forward '+f['path'],work==new)
 for e in reversed(f['edits']):
  a=e['before'].encode();b=e['after'].encode();need('inverse count '+f['path'],work.count(b)==e['count']);work=work.replace(b,a)
 need('whole inverse '+f['path'],work==old)
policy=read(SOURCE/'policy.json');oldpolicy=read(PARENT/'policy.json');before=oldpolicy['expectedNativeSourceManifest'];after=policy['expectedNativeSourceManifest'];need('only ordering changed policy',{k:v for k,v in policy.items()if k!='expectedNativeSourceManifest'}=={k:v for k,v in oldpolicy.items()if k!='expectedNativeSourceManifest'});need('actual canonical357',after==sorted(before,key=lambda r:r['path'])and after!=before and len(after)==len({r['path']for r in after})==357);need('native paths hashes unchanged',{r['path']:r['sha256']for r in after}=={r['path']:r['sha256']for r in before})
ht=(SOURCE/'layer-policy.py').read_text();hast=ast.parse(ht);sm=next(n for n in hast.body if isinstance(n,ast.FunctionDef)and n.name=='source_manifest');assignment=next(n for n in sm.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='rows'for t in n.targets));ret=next(n.value for n in sm.body if isinstance(n,ast.Return));vs=next(n for n in hast.body if isinstance(n,ast.FunctionDef)and n.name=='validate_sources');predicate=next(n.test for n in ast.walk(vs)if isinstance(n,ast.Assert))
def emitted(p):
 rows=eval(compile(ast.Expression(assignment.value),'<actual assignment>','eval'),{'__builtins__':{}},dict(POLICY=p));return eval(compile(ast.Expression(ret),'<actual return>','eval'),{'__builtins__':{}},dict(rows=rows,copy=copy))
def accepted(a,b):return eval(compile(ast.Expression(predicate),'<actual validator>','eval'),{'__builtins__':dict(sorted=sorted,all=all,set=set)},dict(manifest=a,actual=b))
old_emitted=emitted(oldpolicy);new_emitted=emitted(policy);need('old actual expressions refuse',accepted(old_emitted,old_emitted)is False);need('new actual expressions accept',accepted(new_emitted,new_emitted)is True);need('prebuild JSON preserves exact array',json.loads(json.dumps(new_emitted))==new_emitted)
for n,bad in [('missing',new_emitted[:-1]),('duplicate',new_emitted+[new_emitted[0]]),('hash-change',[{**new_emitted[0],'sha256':'0'*64},*new_emitted[1:]]),('extra-field',[{**new_emitted[0],'extra':1},*new_emitted[1:]])]:need('actual validator rejects '+n,accepted(bad,new_emitted)is False)
modeltext=(SOURCE/'native-admission-model.py').read_text();mast=ast.parse(modeltext);mv=next(n for n in mast.body if isinstance(n,ast.FunctionDef)and n.name=='validate_metadata');expr=next(n.test for n in mv.body if isinstance(n,ast.Assert)and ast.unparse(n.test)=="metadata['sourceManifest'] == policy['expectedNativeSourceManifest']")
for name,value,want in [('canonical',new_emitted,True),('unsorted',old_emitted,False)]:need('actual raw-model array '+name,eval(compile(ast.Expression(expr),'<exact raw-model equality>','eval'),{'__builtins__':{}},dict(metadata={'sourceManifest':value},policy=policy))is want)
recipe=(SOURCE/'build-engine.sh').read_text();hh=refs['helper']['sha256'];ph=refs['policy']['sha256'];mh=refs['metadataModel']['sha256'];slots=re.findall(r"(?:sha256_file \"\$consumers_layer_root/(layer-policy\.py|policy\.json)\"\)\" == |digest\(layer_file\) == ')([0-9a-f]{64})",recipe);need('all seven active literal slots',len(slots)==7)
for n,(name,digest)in enumerate(slots):need('literal guard actual '+str(n),row(SOURCE/(name or'layer-policy.py'))['sha256']==digest)
need('helper own policy pin',re.search(r"POLICY_SHA256='([0-9a-f]{64})'",ht).group(1)==ph);need('own model pin',policy['admissionModelSha256']==mh and "assert digest(model_path)==SPEC['admissionModelSha256']"in ht);need('recipe actual OWN',recipe.count(str(SOURCE))==2 and str(PARENT)not in recipe);need('no stale literal hashes',refs['helper']['sha256']!=d['files'][0]['before']['sha256']and d['files'][0]['before']['sha256']not in recipe and d['policyBefore']['sha256']not in recipe)
need('model unchanged',(SOURCE/'native-admission-model.py').read_bytes()==(PARENT/'native-admission-model.py').read_bytes());need('embedding patch unchanged',(SOURCE/'embedding-diagnostic.UNAPPLIED.patch').read_bytes()==(PARENT/'embedding-diagnostic.UNAPPLIED.patch').read_bytes());need('actual recipe source-emission order',recipe.index('manifest = layer.source_manifest(repo)')<recipe.index('layer.validate_sources(repo,manifest)')<recipe.index("'sourceManifest': manifest")<recipe.index("with open(artifact + '.build.json', 'x')"));need('seven-arg own raw82 model',"model.validate_metadata(metadata,layer.POLICY,layer.POLICY_SHA256,digest(layer_file),digest(pathlib.Path(actual_recipe)),componentize_inputs,'normal-off')"in recipe)
# Inert definitions only: no authorize/stage/build/helper/monitor calls.
def pure_load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
controller=pure_load('independent_clock357_v3_controller',SOURCE/'controller.py');model=pure_load('independent_clock357_v3_model',SOURCE/'native-admission-model.py');need('actual module OWN',controller.OWN==SOURCE);base=read(policy['basePolicy']['path']);assembled=model.assemble_policy(policy,base);need('actual pure assembly canonical',assembled['expectedNativeSourceManifest']==after and len(assembled['expectedRawMetadataFields'])==82 and len(assembled['selectedModuleManifests'])==11)
need('active own producer context',refs['activeProducerContext']==str(SOURCE));need('shared plan historical label',read(refs['copyPlan']['path'])['activeProducerContext']==str(PARENT));ct=(SOURCE/'controller.py').read_text();need('shared captured before action and on final',"shared_rows=family(refs['sharedDataIndex'])"in ct and refs['sharedDataIndex']in refs['families']and"for ix in refs['families']:"in ct and"frame['families'].append(ix)"in ct);need('stage receipt owns V3 context',"activeProducerContext=str(OWN),sharedSourcePlanData=frame['refs']['copyPlan']"in ct)
for k,v in refs['contexts'].items():need('retained future path absent '+k,not Path(v).exists())
rawindex=dict(path=str(SOURCE/'index.json'),sha256='0'*64,bytes=1);template=read(SOURCE/'root-authority.template.json');rootcases=0
for phase in ['stage','build']:
 root=copy.deepcopy(template);root.update(phase=phase,sourceIndex=rawindex,sourceStageAllowed=phase=='stage',nativeBuildAllowed=phase=='build',deadlineSeconds=600 if phase=='stage' else 7200)
 if phase=='build':root.update(actualStageReview={'synthetic':True},actualStageResult={'synthetic':True})
 controller.root_model(root,rawindex,refs,phase);rootcases+=1
 for k in ['clockRuntimeAllowed','cryptoAllowed','gcAllowed','oomAllowed','debugAllowed','engineExecutionAllowed']:
  bad=copy.deepcopy(root);bad[k]=True
  try:controller.root_model(bad,rawindex,refs,phase)
  except AssertionError:rootcases+=1
  else:raise AssertionError('accepted '+k)
for p in SOURCE.glob('*.py'):ast.parse(p.read_bytes())
for r in list(seen.values()):verify(r)
family(own)
print(json.dumps(dict(schemaVersion=1,passed=True,sourceIndex=own,parentSourceIndex=parent,holdIndex=hold,checks=len(checks),checkNames=checks,filesAuthenticated=len(seen),closedSourceFamilies=3,sourcePayloads=len(ix['files']),parentPayloads=len(px['files']),exactEditGroups=editgroups,activeHashSlots=7,pureRootCases=rootcases,sourceAuthorOwnsDiagnosticPayload=True,reviewerAuthoredNeitherPayloadNorProducer=True,oldActualPredicateFails=True,newActualPredicatePasses=True,rawModelOrderGateVerified=True,helperOrStageBuildOrCompilerGuestInvoked=False,ledgerOrTooltreeReplay=False),indent=2))
