"""Independent read/hash/AST and pure Source review. No operational function calls."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,os,re,shlex,stat,struct,sys,time
sys.dont_write_bytecode=True
OWN=Path(__file__).resolve().parent
SOURCE=OWN.parent/'combined-clock-diagnostics-native-integration-candidate-v2'
EXPECTED='a52ee25caa3e026ad8efae1955473bea2a98090811d66cea7be911853b5d7c64'
checks=[]
def check(name,value):assert value,name;checks.append(name)
def reject(name,fn):
 try:fn()
 except(AssertionError,ValueError,KeyError):checks.append(name);return
 raise AssertionError('Accepted negative: '+name)
def desc(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def read(p):return json.loads(Path(p).read_bytes())
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
def load(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
 start=time.monotonic();ix=desc(SOURCE/'index.json');check('exact assigned Source index',ix['sha256']==EXPECTED)
 index=read(ix['path']);check('whole Source membership',set(r['path']for r in index['files'])|{'index.json'}=={p.relative_to(SOURCE).as_posix()for p in SOURCE.rglob('*')if p.is_file()})
 for r in index['files']:
  p=SOURCE/r['path'];check('Source payload '+r['path'],not p.is_symlink()and desc(p)==dict(r,path=str(p)))
 refs=read(SOURCE/'references.json');spec=read(SOURCE/'policy.json')
 check('own controller descriptor',desc(SOURCE/'controller.py')==refs['controller'])
 check('own model descriptor',desc(SOURCE/'native-admission-model.py')==refs['metadataModel'])
 # Inspected modules contain stdlib imports/constants/definitions only at entry;
 # neither authorize nor helper/monitor/build/stage/recipe is invoked here.
 controller=load('independent_clock357_original_context',SOURCE/'controller.py')
 model=load('independent_clock357_pure_model',SOURCE/'native-admission-model.py')
 check('actual module OWN',controller.OWN==SOURCE)
 for key,attr in [('sourceRoot','SOURCE'),('workRoot','WORK'),('freezeRoot','FREEZE'),('stageOutputRoot','STAGE_OUT'),('buildOutputRoot','BUILD_OUT'),('buildResultRoot','BUILD_RESULT'),('stageJournal','JOURNAL')]:check('actual fixed '+attr,str(getattr(controller,attr))==refs['contexts'][key])
 rows={};modes={};families=[]
 def add(r):
  check('consistent current descriptor '+r['path'],r['path']not in rows or rows[r['path']]==r);rows[r['path']]=r
 for family in [ix,*refs['families']]:
  for r in controller.family(family):add(r)
  families.append(family)
 inputs=controller.read(refs['protectedInputs'])
 for ledger in inputs['fileLedgers']:
  add(ledger)
  for r in controller.read(ledger)['files']:add(r)
 add(inputs['frozenCopyInventory'])
 for r in controller.read(inputs['frozenCopyInventory'])['files']:
  add(r['copy']);modes[r['copy']['path']]=r['mode']
  if r['original']is not None:add(r['original'])
 for r in inputs['files']:add(r)
 for r in inputs['modeRows']:add(r['file']);modes[r['file']['path']]=r['mode']
 for k in ['pythonExecutable','bash','git','node']:add(refs[k])
 identities={}
 for p,r in rows.items():
  actual=controller.checked(r);s=actual.stat();identities[p]=controller.identity(s)
  if p in modes:check('mode '+p,stat.S_IMODE(s.st_mode)==modes[p])
 for r in inputs['aliases']:check('explicit alias '+r['path'],Path(r['path']).is_symlink()and os.readlink(r['path'])==r['linkText']and str(Path(r['path']).resolve())==r['resolved'])
 for r in inputs['archiveHardlinks']:
  a=controller.physical(r['path']).stat();b=controller.physical(r['target']).stat();check('declared archive hardlink',(a.st_dev,a.st_ino)==(b.st_dev,b.st_ino))
 for r in refs['hostTools']:
  check('pinned resolved '+r['name'],str(Path(controller.shutil.which(r['name'],path=refs['hostPath'])).resolve())==r['executable']['path']);controller.checked(r['executable'])
 policy=model.assemble_policy(spec,controller.read(spec['basePolicy']))
 check('357 actual source-policy rows',len(policy['expectedNativeSourceManifest'])==357)
 check('82 exact field names',len(set(policy['expectedRawMetadataFields']))==len(policy['expectedRawMetadataFields'])==82)
 check('full11 unchanged',policy['selectedModuleManifests']==controller.read(spec['basePolicy'])['selectedModuleManifests']and len(policy['selectedModuleManifests'])==11)
 plan=controller.read(refs['copyPlan'])['files'];check('1583 distinct overlay paths',len(plan)==len({controller.safe(r['path'])for r in plan})==1583)
 native=[r for r in plan if r['role']=='native'];tools=[r for r in plan if r['role']=='tool']
 check('357+1226 overlay',len(native)==357 and len(tools)==1226)
 check('plan policy whole native equality',[dict(path=r['path'],sha256=r['sha256'])for r in native]==policy['expectedNativeSourceManifest'])
 for r in plan:
  p=controller.checked(r['origin']);check('overlay size/hash/mode '+r['path'],r['sha256']==r['origin']['sha256']and r['bytes']==r['origin']['bytes']and stat.S_IMODE(p.stat().st_mode)==r['mode'])
 for key in refs['contexts']:check('fresh '+key,not Path(refs['contexts'][key]).exists())
 # Genuine new producer afterimages and pure in-memory reversal, never execution.
 deriv=read(SOURCE/'derivations.json');reversed_edits=0
 for item in deriv['files']:
  check('derivation original '+item['path'],desc(item['original']['path'])==item['original']);original=Path(item['original']['path']).read_text();intermediate=original
  for edit in item['edits']:
   check('exact edit count '+item['path'],intermediate.count(edit['before'])==edit['count']);intermediate=intermediate.replace(edit['before'],edit['after']);reversed_edits+=1
  b=intermediate.encode();check('intermediate hash '+item['path'],hashlib.sha256(b).hexdigest()==item['intermediate']['sha256']and len(b)==item['intermediate']['bytes'])
  inverse=intermediate
  for edit in reversed(item['edits']):inverse=inverse.replace(edit['after'],edit['before'])
  check('whole inverse '+item['path'],inverse==original)
  actual=(SOURCE/item['path']).read_text()
  if item['path']=='native-admission-model.py':check('literal pure model extension',actual==intermediate+(SOURCE/'model-extension.template.py').read_text())
  elif item['path']=='build-engine.sh':
   startgate=intermediate.index('# New355-only raw metadata shape gate');end=intermediate.index('before_rustup=',startgate)
   gate=intermediate[startgate:end].replace('New355-only','Own diagnostic357/82').replace('actual_combined355_metadata_shape','actual_clock_diagnostic357_metadata_shape');moved=intermediate[:startgate]+intermediate[end:]
   check('actual final emitter gate relocation',actual==moved.replace("with open(artifact + '.build.json', 'x') as output:",gate+"with open(artifact + '.build.json', 'x') as output:"))
  else:check('whole derived helper',actual==intermediate)
  check('whole final descriptor '+item['path'],desc(SOURCE/item['path'])==item['after'])
 # Own pure operational-contract negatives; no operational function is called.
 root_template=read(SOURCE/'root-authority.template.json')
 for phase in ['stage','build']:
  root=copy.deepcopy(root_template);root.update(phase=phase,sourceIndex=ix,sourceStageAllowed=phase=='stage',nativeBuildAllowed=phase=='build',deadlineSeconds=600 if phase=='stage'else 7200)
  if phase=='build':root.update(actualStageReview={'synthetic':True},actualStageResult={'synthetic':True})
  controller.root_model(root,ix,refs,phase);checks.append('Root pure '+phase)
  for k in ['clockRuntimeAllowed','cryptoAllowed','gcAllowed','engineExecutionAllowed','allSeventeenGatesAccepted']:
   bad=copy.deepcopy(root);bad[k]=True;reject('Root denies '+phase+' '+k,lambda:controller.root_model(bad,ix,refs,phase))
 for key in controller.ENV_POLICY['removeExactNames']+['BASH_FUNC_fake%%']:
  env={'HOME':'original','home':'lowercase','CODEX_HOME':'original-codex',key:'not executed'};clean,removed=controller.clean_environment(env);check('pure clean '+key,key not in clean and removed==[key]and all(clean[k]==env[k]for k in ['HOME','home','CODEX_HOME']))
 env=controller.build_environment({'HOME':'same','NODE_OPTIONS':'bad','RUSTC_WRAPPER':'bad','CARGO_ENCODED_RUSTFLAGS':'bad','GIT_CONFIG_PARAMETERS':'bad'},refs)
 check('build environment wrapper denial',not any(k in env for k in ['NODE_OPTIONS','RUSTC_WRAPPER','CARGO_ENCODED_RUSTFLAGS','GIT_CONFIG_PARAMETERS'])and env['HOME']=='same')
 commands=controller.git_commands(refs['git']['path']);check('baseline-only five argv',len(commands)==5 and commands[1][-1]==controller.BASE and '--depth=1'in commands[1]and '--no-tags'in commands[1])
 server=next(x.split('=',1)[1]for x in commands[1]if x.startswith('--upload-pack='));check('uploadpack argv quoting',shlex.split(server)==controller.git_prefix(refs['git']['path'])+['-c','uploadpack.allowAnySHA1InWant=true','upload-pack'])
 def index_bytes(st=0,oid=b'A'):
  out=b'DIRC'+struct.pack('>II',2,742)
  for n in range(742):
   name=('baseline-%04d.cpp'%n).encode();fields=[0]*10;fields[0]=st;fields[6]=0o100644;item=struct.pack('>10I',*fields)+oid*20+struct.pack('>H',len(name))+name+b'\0';out+=item+b'\0'*((-len(item))%8)
  return out+hashlib.sha1(out).digest()
 def observed(raw):return dict(file=dict(path='/synthetic/index',sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw)),mode=0o600,device=1,inode=2,links=1,parsed=controller.parse_index(raw))
 a=observed(index_bytes());b=observed(index_bytes(7));check('full742 stat-only semantics',controller.index_stat_only(a,b)['statCacheBytesChanged'])
 reject('changed index OID rejected',lambda:controller.index_stat_only(a,observed(index_bytes(7,b'B'))))
 bad=copy.deepcopy(b);bad['mode']=0o644;reject('changed index mode rejected',lambda:controller.index_stat_only(a,bad))
 bad=copy.deepcopy(b);bad['parsed']['extensionsHex']='00';reject('changed index extensions rejected',lambda:controller.index_stat_only(a,bad))
 # Actual same-TU command classifier, exercised on synthetic commands only.
 root=policy['contexts']['configuredSourceRoot'];work=policy['contexts']['workRoot'];shared=policy['diagnosticSourcePolicy']['sharedNativeTUs']
 cpp=[r['path']for r in policy['expectedNativeSourceManifest']if r['path'].endswith('.cpp')and r['path'].startswith(('builtins/','runtime/'))]
 def cmd(p,enabled):return 'clang++ --target=wasm32-wasi -fno-exceptions -O3 -DNDEBUG '+('-DNODE_COMPAT_LIFECYCLE_DIAGNOSTICS=1 'if enabled else'')+'-I'+root+'/include -c '+p
 entries=[dict(file=root+'/'+p,command=cmd(root+'/'+p,p in shared))for p in cpp]
 entries+=[dict(file=root+'/'+p,command=cmd(root+'/'+p,p in shared))for p in ['host-apis/wasi-0.2.0/host_api.cpp','other1.cpp','other2.cpp','other3.cpp','other4.cpp']]
 null=work+'/engine/null.cpp';entries.append(dict(file=null,command=cmd(null,False)));embed=[cmd(work+'/componentize/embedding/embedding.cpp',True)]
 options={k:'ON'for k in ['NODE_COMPAT_LIFECYCLE_DIAGNOSTICS','ENABLE_BUILTIN_DIAGNOSTICS_CLOCK_LIFECYCLE','ENABLE_BUILTIN_WEB_PERFORMANCE']}
 check('69 DB/7 diagnostic commands pure classifier',len(model.classify_diagnostic_commands(policy,entries,embed,options,options))==7)
 for n in range(7):
  es=copy.deepcopy(entries);em=embed[:]
  if n==6:em[0]=em[0].replace('-DNODE_COMPAT_LIFECYCLE_DIAGNOSTICS=1','')
  else:
   row=next(r for r in es if r['file']==root+'/'+shared[n]);row['command']=row['command'].replace('-DNODE_COMPAT_LIFECYCLE_DIAGNOSTICS=1','')
  reject('missing actual shared macro '+str(n),lambda:model.classify_diagnostic_commands(policy,es,em,options,options))
 recipe=(SOURCE/'build-engine.sh').read_text();helper=(SOURCE/'layer-policy.py').read_text();fields=set();blocks=0
 for match in re.finditer(r"<<'([A-Z][A-Z0-9_]*)'\n",recipe):
  end=recipe.index('\n'+match.group(1)+'\n',match.end());tree=ast.parse(recipe[match.end():end]);blocks+=1
  for node in ast.walk(tree):
   if isinstance(node,ast.Assign):
    for target in node.targets:
     if isinstance(target,ast.Name)and target.id=='metadata'and isinstance(node.value,ast.Dict):fields.update(k.value for k in node.value.keys if isinstance(k,ast.Constant)and isinstance(k.value,str))
     if isinstance(target,ast.Subscript)and isinstance(target.value,ast.Name)and target.value.id=='metadata'and isinstance(target.slice,ast.Constant):fields.add(target.slice.value)
 for node in ast.walk(ast.parse(helper)):
  if isinstance(node,ast.Assign):
   for target in node.targets:
    if isinstance(target,ast.Subscript)and isinstance(target.value,ast.Name)and target.value.id=='metadata'and isinstance(target.slice,ast.Constant):fields.add(target.slice.value)
 check('real emitter field-name set82',fields==set(policy['expectedRawMetadataFields'])and len(fields)==82)
 check('actual final field precedes classifier publication',recipe.index("metadata['privateRustupBootstrapPolicy']")<recipe.index('classification=model.validate_metadata(')<recipe.index("with open(artifact + '.build.json', 'x')"))
 for p in SOURCE.glob('*.py'):ast.parse(p.read_bytes());checks.append('active AST '+p.name)
 for p,r in rows.items():check('final identity '+p,controller.identity(controller.physical(p).stat())==identities[p])
 for r in families:controller.family(r)
 check('final Source seal unchanged',desc(SOURCE/'index.json')==ix)
 save('reader-results.json',dict(schemaVersion=1,state='INDEPENDENT_CLOCK357_SOURCE_BOUNDARY_AND_PURE_READER_PASSED',sourceIndex=ix,checks=len(checks),uniqueCurrentInputFiles=len(rows),logicalBytes=sum(r['bytes']for r in rows.values()),families=len(families),pureSourceEditsReversed=reversed_edits,pythonHeredocsParsed=blocks,sourceReadOnly=True,ownerOperationalFunctionsInvoked=False,compilerOrHelperOrStageOrBuildOrGuestInvoked=False,elapsedOperationalSeconds=time.monotonic()-start))
 print(json.dumps(read(OWN/'reader-results.json')))
if __name__=='__main__':main()
