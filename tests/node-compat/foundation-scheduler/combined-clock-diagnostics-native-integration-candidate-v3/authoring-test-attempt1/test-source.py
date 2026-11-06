"""Pure exact manifest-order/guard/context regressions. No helper or operational calls."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,re,sys
sys.dont_write_bytecode=True
OWN=Path(__file__).resolve().parent
PARENT=OWN.parent/'combined-clock-diagnostics-native-integration-candidate-v2'
def read(p):return json.loads(Path(p).read_bytes())
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
checks=[]
def check(n,v):assert v,n;checks.append(n)
def reject(n,fn):
 try:fn()
 except(AssertionError,ValueError,KeyError):checks.append(n);return
 raise AssertionError('Accepted '+n)
def pure_load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
 refs=read(OWN/'references.json');policy=read(OWN/'policy.json');old=read(PARENT/'policy.json')
 check('only source manifest ordering changes policy',{k:v for k,v in policy.items()if k!='expectedNativeSourceManifest'}=={k:v for k,v in old.items()if k!='expectedNativeSourceManifest'})
 before=old['expectedNativeSourceManifest'];after=policy['expectedNativeSourceManifest']
 check('canonical357 actual path/hash rows',after==sorted(before,key=lambda r:r['path'])and len(after)==len({r['path']for r in after})==357 and before!=after)
 check('entire native path/hash map unchanged',{r['path']:r['sha256']for r in before}=={r['path']:r['sha256']for r in after})
 helper=(OWN/'layer-policy.py').read_text();tree=ast.parse(helper)
 manifest_fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='source_manifest')
 assignment=next(n for n in manifest_fn.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='rows'for t in n.targets))
 returned=next(n for n in manifest_fn.body if isinstance(n,ast.Return)).value
 validation=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='validate_sources')
 predicate=next(n for n in ast.walk(validation)if isinstance(n,ast.Assert)).test
 # These are isolated expressions over actual authenticated policy DATA, not
 # source_manifest/validate_sources/helper execution or namespace replacement.
 def emitted(value):
  rows=eval(compile(ast.Expression(assignment.value),'<actual-source-rows-expression>','eval'),{'__builtins__':{}},dict(POLICY=value))
  return eval(compile(ast.Expression(returned),'<actual-source-return-expression>','eval'),{'__builtins__':{}},dict(copy=copy,rows=rows))
 def accepted(provided,actual):return eval(compile(ast.Expression(predicate),'<actual-validate-expression>','eval'),{'__builtins__':dict(sorted=sorted,all=all,set=set)},dict(manifest=provided,actual=actual))
 old_output=emitted(old);new_output=emitted(policy)
 check('old actual emission fails actual validation',accepted(old_output,old_output)is False)
 check('new actual emission accepts actual validation',accepted(new_output,new_output)is True)
 check('retained prebuild JSON roundtrip keeps exact new ordering',json.loads(json.dumps(new_output))==new_output)
 check('recipe metadata sourceManifest is same passed list',accepted(dict(sourceManifest=new_output)['sourceManifest'],emitted(policy))is True)
 bad=copy.deepcopy(new_output);bad[0]['sha256']='0'*64;check('source hash mutation refused',accepted(bad,new_output)is False)
 check('duplicate source row refused',accepted(new_output+[new_output[0]],new_output)is False)
 check('missing source row refused',accepted(new_output[:-1],new_output)is False)
 bad=copy.deepcopy(new_output);bad[0]['extra']=1;check('extra source field refused',accepted(bad,new_output)is False)
 check('old unsorted provided list still refused',accepted(old_output,new_output)is False)
 recipe=(OWN/'build-engine.sh').read_text()
 check('real prebuild capture unchanged',"json.dump(layer.source_manifest(repo),open(sys.argv[2],'w'),indent=2)"in recipe)
 check('real postbuild source call precedes metadata publication',recipe.index('manifest = layer.source_manifest(repo)')<recipe.index('layer.validate_sources(repo,manifest)')<recipe.index("'sourceManifest': manifest")<recipe.index("with open(artifact + '.build.json', 'x')"))
 joins=re.findall(r"(?:sha256_file \"\$consumers_layer_root/(layer-policy\.py|policy\.json)\"\)\" == |digest\(layer_file\) == ')([0-9a-f]{64})",recipe)
 check('all seven active digest guard slots',len(joins)==7)
 for n,(name,want)in enumerate(joins):check('actual current guard '+str(n),digest(OWN/(name or'layer-policy.py'))==want)
 check('helper policy selfhash',re.search(r"POLICY_SHA256='([0-9a-f]{64})'",helper).group(1)==digest(OWN/'policy.json'))
 check('helper model selfhash',policy['admissionModelSha256']==digest(OWN/'native-admission-model.py')and "assert digest(model_path)==SPEC['admissionModelSha256']"in helper)
 check('direct82 model and embedding patch unchanged',digest(OWN/'native-admission-model.py')==digest(PARENT/'native-admission-model.py')and digest(OWN/'embedding-diagnostic.UNAPPLIED.patch')==digest(PARENT/'embedding-diagnostic.UNAPPLIED.patch'))
 model=pure_load('clock357_v3_direct82_pure_model',OWN/'native-admission-model.py');base=read(policy['basePolicy']['path']);assembled=model.assemble_policy(policy,base)
 check('real pure model gets canonical new357',assembled['expectedNativeSourceManifest']==after)
 check('full11 and82 unchanged',assembled['selectedModuleManifests']==base['selectedModuleManifests']and len(assembled['selectedModuleManifests'])==11 and len(assembled['expectedRawMetadataFields'])==82)
 controller=pure_load('clock357_v3_inert_controller',OWN/'controller.py')
 check('genuine new controller module context',controller.OWN==OWN)
 for k,a in [('sourceRoot','SOURCE'),('workRoot','WORK'),('freezeRoot','FREEZE')]:check('genuine untouched future '+k,str(getattr(controller,a))==refs['contexts'][k]and not Path(refs['contexts'][k]).exists())
 check('active producer separate from historical shared plan label',refs['activeProducerContext']==str(OWN)and read(refs['copyPlan']['path'])['activeProducerContext']==str(PARENT))
 template=read(OWN/'root-authority.template.json');own=dict(path=str(OWN/'index.json'),sha256='0'*64,bytes=1)
 for phase in ['stage','build']:
  root=copy.deepcopy(template);root.update(phase=phase,sourceIndex=own,sourceStageAllowed=phase=='stage',nativeBuildAllowed=phase=='build',deadlineSeconds=600 if phase=='stage'else 7200)
  if phase=='build':root.update(actualStageReview={'synthetic':True},actualStageResult={'synthetic':True})
  controller.root_model(root,own,refs,phase);checks.append('real pure V3 Root '+phase)
  for k in ['clockRuntimeAllowed','cryptoAllowed','gcAllowed','debugAllowed']:
   bad=copy.deepcopy(root);bad[k]=True;reject('Root denies '+phase+' '+k,lambda:controller.root_model(bad,own,refs,phase))
 # Preserved explicit permission restoration and Git index semantics are data
 # ancestry, not rerun tiny filesystem copies or real Git commands.
 old_tree=ast.parse((PARENT/'controller.py').read_text());new_tree=ast.parse((OWN/'controller.py').read_text())
 for n in ['copy_regular','parse_index','index_stat_only','git_commands','git_environment','build_environment']:
  a=next(x for x in old_tree.body if isinstance(x,ast.FunctionDef)and x.name==n);b=next(x for x in new_tree.body if isinstance(x,ast.FunctionDef)and x.name==n)
  check('preserved actual function '+n,ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False))
 check('genuine own recipe path guards',recipe.count(str(OWN))==2 and str(PARENT)not in recipe)
 for p in OWN.glob('*.py'):ast.parse(p.read_bytes());checks.append('active AST '+p.name)
 result=dict(schemaVersion=1,state='CLOCK_DIAGNOSTIC357_CANONICAL_MANIFEST_DELTA_PURE_PASSED_V3',checks=len(checks),checkNames=checks,exactSourceExpressionsEvaluated=True,oldFailNewPass=True,helperOrStageOrBuildOrCompilerOrGuestInvoked=False,nativeOrEmbeddingSourceChanges=False,fullNativeLedgerOrTooltreeAuthoringReplay=False)
 (OWN/'test-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
