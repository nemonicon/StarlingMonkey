"""Source/data and extracted-pure checks only. No owner helper, Node, Git or compiler action."""
import ast
import copy
import difflib
import hashlib
import json
from pathlib import Path
import re
import types
import sys

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
inputs={};checks=0
def check(value):
 global checks
 assert value
 checks+=1
def descriptor(path):
 path=Path(path);physical=path.resolve(strict=True);before=physical.stat();check(physical.is_file());raw=physical.read_bytes();after=physical.stat()
 check((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns))
 return dict(path=str(path),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
def checked(row):
 check(descriptor(row['path'])==row);inputs[row['path']]=row
def rejects(fn):
 global checks
 try:fn()
 except(AssertionError,KeyError,TypeError):checks+=1
 else:raise AssertionError('invalid source/metadata model accepted')
policy=json.loads((HERE/'policy.json').read_bytes());pins=json.loads((HERE/'baseline-pins.json').read_bytes())
for value in pins.values():
 if isinstance(value,dict)and set(value)=={'path','sha256','bytes'}:checked(value)
api=json.loads((HERE/'api-sources.json').read_bytes())
for row in api['files']:checked(row)
stage=json.loads((HERE/'stage-inputs.json').read_bytes());check(stage['nativeCount']==342 and len(stage['nativeAfterimageReplacements'])==2)
check(len(stage['files'])==len({r['target']for r in stage['files']})==467)
for row in stage['files']:checked(row['original'])
old=json.loads(Path(pins['parentPolicy']['path']).read_bytes());before={r['path']:r['sha256']for r in old['expectedNativeSourceManifest']};after={r['path']:r['sha256']for r in policy['expectedNativeSourceManifest']}
check(len(before)==len(after)==342 and set(before)==set(after));check(sum(before[k]==after[k]for k in before)==340)
for change in stage['nativeAfterimageReplacements']:
 check(before[change['path']]==change['beforeSha256']and after[change['path']]==change['afterSha256'])
 check(descriptor(HERE/'native'/change['path'])['sha256']==change['afterSha256'])
 check(descriptor(REPO/change['path'])['sha256']==change['beforeSha256'])
resource=REPO/'tests/node-compat/foundation-scheduler/resource-ownership-candidate-v1'
for change in stage['nativeAfterimageReplacements']:check((resource/'afterimages'/change['path']).read_bytes()==(HERE/'native'/change['path']).read_bytes())
proof=json.loads((HERE/'derivations.json').read_bytes());exact=[]
for kind in ('helper','recipe'):
 checked(proof[kind+'Donor']);text=Path(proof[kind+'Donor']['path']).read_text();edits=proof[kind+'Edits']
 for edit in edits:
  check(text.count(edit['before'])==edit.get('count',1));text=text.replace(edit['before'],edit['after'])
 check(text==(HERE/proof[kind+'Afterimage']).read_text())
 for edit in reversed(edits):
  check(text.count(edit['after'])==edit.get('count',1));text=text.replace(edit['after'],edit['before'])
 check(text==Path(proof[kind+'Donor']['path']).read_text());exact.append(dict(kind=kind,edits=len(edits),forwardAndReverseExact=True))
# Exercise actual expected() bodies with only pure descriptor-map dependencies.
parent=REPO/'tests/node-compat/foundation-scheduler/integration-candidate-v1'
parent_policy=json.loads((parent/'policy.json').read_bytes())
def extracted(path,name,scope):
 tree=ast.parse(path.read_bytes());node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name==name)
 exec(compile(ast.Module(body=[node],type_ignores=[]),'<actual-extracted-pure-'+name+'>','exec'),scope);return scope[name]
parent_expected=extracted(parent/'layer-policy.py','expected',{'POLICY':parent_policy})
new_expected=extracted(HERE/'layer-policy.py','expected',{'POLICY':policy,'PARENT':types.SimpleNamespace(expected=parent_expected)})
for path,expected in after.items():
 private=parent_policy['sourceLayer'].get(path);layer=policy['sourceLayer'].get(path)
 base=private['beforeSha256']if private else(layer['beforeSha256']if layer else expected)
 check(new_expected(path,base)==expected)
for path in ('builtins/web/timers.cpp','runtime/event_loop.cpp'):
 private=parent_policy['sourceLayer'].get(path);base=private['beforeSha256']if private else before[path]
 check(new_expected(path,base)!=before[path]);rejects(lambda path=path:new_expected(path,'0'*64))
model_scope={};code=ast.parse((HERE/'native-admission-model.py').read_bytes());exec(compile(code,'<pure-native-metadata-shape-model>','exec'),model_scope)
recipe=descriptor(HERE/'proposed/tests/node-compat/build-engine.sh');helper=descriptor(HERE/'layer-policy.py');policy_row=descriptor(HERE/'policy.json')
metadata=json.loads(Path(pins['acceptedMetadata']['path']).read_bytes())
for r in metadata['sourceManifest']:
 d=descriptor(REPO/r['path']);check(d['sha256']==r['sha256']);inputs[d['path']]=d
validate=model_scope['validate_metadata'];args=(policy,policy_row['sha256'],helper['sha256'],recipe['sha256'],pins['externalEmbeddingSources'],'normal-off')
rejects(lambda:validate(metadata,*args))
for field,value in [('diagnosticOnly',True),('syntheticMetadataOnly',True),('sourceManifest',metadata['sourceManifest']+[{}])]:
 changed=copy.deepcopy(metadata);changed[field]=value;rejects(lambda changed=changed:validate(changed,*args))
# No positive metadata record is fabricated from an old engine receipt.
recipe_text=(HERE/'proposed/tests/node-compat/build-engine.sh').read_text()
check('/private/tmp/starling-node-compat/scheduler-resource-v1-build' in recipe_text and 'resource-v1.$entropy_mode' in recipe_text)
check('Resource source candidate requires one build job' in recipe_text)
check('-DENABLE_BUILTIN_WEB_TIMERS=ON' in recipe_text)
check(helper['sha256']in recipe_text and policy_row['sha256']in recipe_text)
check("metadata['resourceOwnershipPolicy']"in(HERE/'layer-policy.py').read_text())
check("NS_DEF(builtins::web::timers)"in(HERE/'layer-policy.py').read_text())
heredocs=[]
for match in re.finditer(r"<<'(?P<tag>PY[A-Z]*)'\n(?P<code>[\s\S]*?)\n(?P=tag)(?:\n|$)",recipe_text):ast.parse(match['code']);heredocs.append(match['tag'])
check(len(heredocs)>=3)
contract=json.loads((HERE/'runtime/contract.json').read_bytes());check(contract['ordinaryCaseIds']==list(range(7))and contract['retainedRotations']==3)
check(contract['selectedTimerInterfaces']==['wasi:clocks/monotonic-clock@0.2.10','wasi:io/poll@0.2.10'])
check(contract['pureExpectedImports']==[]and contract['rootExportAuthority']is None)
guest=(HERE/'runtime/guest.UNEXECUTED.mjs').read_text();driver=(HERE/'runtime/driver.template.mjs').read_text()
check(re.findall(r"^import .* from '([^']+)';",guest,re.M)==['node:buffer'])
check("Buffer.from('c3a92201','hex')"in guest and 'i<8' in guest)
check('ownPendingNativeHandleCountInstrumented:false' in guest)
check('const ACTIVATION=null' in driver and driver.index("assert(ACTIVATION")<driver.index('await import('))
check(driver.index('await persistRaw(')<driver.index("assert.equal(typeof raw,'string')"))
check('Object.entries(lowered.files)' in driver and 'generatedModuleImported:false'in driver)
check('setTimeout(()=>{},0)'in(HERE/'runtime/init-fatal.UNEXECUTED.mjs').read_text())
check('RESOURCE_UNHANDLED_TIMER_CALLBACK'in(HERE/'runtime/fatal.UNEXECUTED.mjs').read_text())
# Existing real APIs establish the async/initialization and coarse clock seams.
embedding=Path('/tmp/starling-node-compat/production-classic-trace-v1/native-freeze/componentize-source/embedding/embedding.cpp').read_text()
check('JS::AddPromiseReactions'in embedding and 'Runtime.engine->run_event_loop()'in embedding)
splicer=Path('/tmp/starling-node-compat/import-abi-clock-v2-build/source/crates/spidermonkey-embedding-splicer/src/stub_wasi.rs').read_text()
check('if !features.contains(&Feature::Clocks)'in splicer and 'let has_io = features.contains(&Feature::Clocks)'in splicer)
check('wasi:clocks/wall-clock'in splicer and 'wasi:io/streams'in splicer)
check('EngineState::Initialized'in(REPO/'include/builtin.h').read_text())
syntax=[]
for file in sorted(HERE.glob('*.py')):ast.parse(file.read_bytes());syntax.append(file.name)
for row in list(inputs.values()):checked(row)
value=dict(schemaVersion=1,state='RESOURCE342_UNAPPLIED_SOURCE_DATA_CHECKS_PASSED',checks=checks,inputs=list(inputs.values()),stageRows=467,nativeRows=342,nativeReplacements=2,unchangedNative=340,actualExpectedFunctionCases=342,oldReceiptRejections=4,positiveNativeMetadataFabricated=False,derivations=exact,pythonAst=syntax,recipePythonHeredocs=heredocs,nodeOrJsOrWitParserInvoked=False,jsAndWitSyntaxStillUnexecuted=True,ownerHelpersImported=False,stageOrNativeOrGuestInvoked=False,sourceOnly=True)
if len(sys.argv)==2:
 with Path(sys.argv[1]).open('x')as out:json.dump(value,out,indent=2);out.write('\n')
else:assert len(sys.argv)==1
print(json.dumps(dict(checks=checks,inputs=len(inputs),stageRows=467,pythonAst=len(syntax),noOwnerActions=True)))
