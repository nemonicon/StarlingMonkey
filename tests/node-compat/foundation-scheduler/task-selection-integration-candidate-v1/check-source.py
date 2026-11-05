"""Finite source/data/pure checks only; no owner imports, stage or native action."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import re
import shlex
import types

OWN=Path(__file__).resolve().parent
REPO=OWN.parents[3]
assert REPO==Path('/Users/dan/dev/StarlingMonkey')
checks=0
inputs={}
def check(value):
    global checks
    assert value
    checks+=1
def descriptor(path):
    p=Path(path);check(p.is_absolute()and p.is_file()and not p.is_symlink())
    a=p.stat();raw=p.read_bytes();b=p.stat()
    check((a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns))
    return dict(path=str(p),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
def checked(row):
    check(descriptor(row['path'])==row)
    check(inputs.setdefault(row['path'],row)==row)
def reject(fn):
    global checks
    try:fn()
    except(AssertionError,KeyError,TypeError,ValueError):checks+=1
    else:raise AssertionError('Negative pure case accepted')
def extracted(path,names,scope):
    tree=ast.parse(path.read_bytes())
    nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names]
    check({n.name for n in nodes}==set(names))
    exec(compile(ast.Module(body=nodes,type_ignores=[]),'<source-extracted-pure-functions>','exec'),scope)
    return scope

freeze=json.loads((OWN/'input-freeze.json').read_bytes())
for row in freeze['files']:checked(row)
check(len(freeze['files'])==len({r['path']for r in freeze['files']}))
policy=json.loads((OWN/'policy.json').read_bytes())
baseline=json.loads((OWN/'baseline-pins.json').read_bytes())
parent=Path(baseline['parentPolicy']['path']).parent
old=json.loads(Path(baseline['parentPolicy']['path']).read_bytes())
before={r['path']:r['sha256']for r in old['expectedNativeSourceManifest']}
after={r['path']:r['sha256']for r in policy['expectedNativeSourceManifest']}
check(len(before)==len(after)==342 and set(before)==set(after))
check(sum(before[p]==after[p]for p in before)==339)
changed={p for p in before if before[p]!=after[p]}
check(changed=={'include/extension-api.h','host-apis/wasi-0.2.0/host_api.cpp','runtime/event_loop.cpp'})
check(before['builtins/web/timers.cpp']==after['builtins/web/timers.cpp']=='0024d009d11aab0705789f5d72fd8ec87deec9c44bdd8b913d970257aaadc9e4')
for field in('resourceOwnershipSourcePolicy','classicTraceSourcePolicy','strictPolicyVersion','protectedPolicyVersion','classicPolicyVersion','profileVersion','classicManifest','embedding','nativePatchSha256'):
    check(policy[field]==old[field])
native=json.loads((OWN/'native-inputs.json').read_bytes())
check(len(native['rows'])==342 and len({r['path']for r in native['rows']})==342)
for row in native['rows']:
    checked(row['source']);check(row['source']['sha256']==after[row['path']])
    check((row['path']in changed)==(row['role']=='new-selector-afterimage'))
derivations=json.loads((OWN/'derivations.json').read_bytes())
derived=[]
for name in('helper','recipe','model','stage'):
    d=derivations[name];checked(d['donor']);original=Path(d['donor']['path']).read_text();text=original
    for edit in d['edits']:
        check(text.count(edit['before'])==edit['count']);text=text.replace(edit['before'],edit['after'])
    check(text==(OWN/d['afterimage']).read_text())
    for edit in reversed(d['edits']):
        check(text.count(edit['after'])==edit['count']);text=text.replace(edit['after'],edit['before'])
    check(text==original);derived.append(dict(kind=name,reversibleEdits=len(d['edits'])))
for row in policy['taskSelectionSourcePolicy']['changes']:
    check(before[row['path']]==row['beforeSha256']and after[row['path']]==row['afterSha256'])
    source=Path(baseline['families']['taskSelection']['path']).parent/'afterimages'/row['path']
    check(source.read_bytes()==(OWN/'native'/row['path']).read_bytes())

# Actual expected() bodies, with only their pure policy-map dependencies.
private=OWN.parent/'integration-candidate-v1'
private_policy=json.loads((private/'policy.json').read_bytes())
parent_expected=extracted(private/'layer-policy.py',{'expected'},{'POLICY':private_policy})['expected']
resolved=extracted(OWN/'layer-policy.py',{'expected'},{'POLICY':policy,'PARENT':types.SimpleNamespace(expected=parent_expected)})['expected']
for name,value in after.items():
    layer=private_policy['sourceLayer'].get(name)or policy['sourceLayer'].get(name)
    base=layer['beforeSha256']if layer else value
    check(resolved(name,base)==value)
for name in changed:reject(lambda name=name:resolved(name,'0'*64))

# Exercise the real new command-parser function against the actual old command
# shapes, not a claim that new native compilation happened.
metadata=json.loads(Path(baseline['resourceMetadata']['path']).read_bytes())
dbpath=Path('/private/tmp/starling-node-compat/scheduler-resource-v1-freeze/normal-off-compile_commands.json')
db=descriptor(dbpath);checked(db);entries=json.loads(dbpath.read_bytes())
scope=extracted(OWN/'layer-policy.py',{'_macro','_release','task_selection_commands'},{'Path':Path,'shlex':shlex})
command_check=scope['task_selection_commands'];configured=baseline['parentConfiguredRoot']
commands=command_check(entries,configured,metadata)
check(set(commands)=={'host-apis/wasi-0.2.0/host_api.cpp','runtime/event_loop.cpp'})
host=next(r for r in entries if r['file']==configured+'/host-apis/wasi-0.2.0/host_api.cpp')
caller=next(r for r in entries if r['file']==configured+'/runtime/event_loop.cpp')
negative_cases=0
for bad in ([r for r in entries if r is not host],entries+[host],[r for r in entries if r is not caller],entries+[caller]):
    reject(lambda bad=bad:command_check(bad,configured,metadata));negative_cases+=1
for old_flag,new_flag in(('-O3','-O0'),('-DNDEBUG','-UNDEBUG'),('-c ','-fsyntax-only -c '),('-DNODE_COMPAT_ENTROPY_POLICY=1','-DNODE_COMPAT_ENTROPY_POLICY=0'),('-DNODE_COMPAT_ENTROPY_POLICY=1','-DNODE_COMPAT_ENTROPY_POLICY=1 -DNODE_COMPAT_GC_STRESS=1'),('-DNODE_COMPAT_ENTROPY_POLICY=1','-DNODE_COMPAT_ENTROPY_POLICY=1 -DNODE_COMPAT_CLASSIC_STREAMS=1')):
    bad=copy.deepcopy(entries);row=next(r for r in bad if r['file']==host['file']);check(row['command'].count(old_flag)==1);row['command']=row['command'].replace(old_flag,new_flag)
    reject(lambda bad=bad:command_check(bad,configured,metadata));negative_cases+=1

# Source-map-only classifier is never called with a projected positive receipt.
model=extracted(OWN/'native-admission-model.py',{'validate_metadata'}, {})['validate_metadata']
args=(policy,descriptor(OWN/'policy.json')['sha256'],descriptor(OWN/'layer-policy.py')['sha256'],descriptor(OWN/'proposed/tests/node-compat/build-engine.sh')['sha256'],baseline['externalEmbeddingSources'],'normal-off')
reject(lambda:model(metadata,*args))
reject(lambda:model(metadata,*args[:-1],'gc-off'))
stage=json.loads((OWN/'stage-inputs.json').read_bytes())
check(len(stage['files'])==len({r['target']for r in stage['files']})==533)
by_target={r['target']:r for r in stage['files']}
for row in stage['files']:
    check(row['target']and not row['target'].startswith('/')and all(p not in('','.','..')for p in row['target'].split('/')))
    checked(row['original'])
for row in native['rows']:check(by_target[row['path']]['original']==row['source'])
for family in baseline['families'].values():
    root=Path(family['path']).parent;checked(family)
    members=json.loads(root.joinpath('index.json').read_bytes())['files']
    for row in [dict(path='index.json',sha256=family['sha256'],bytes=family['bytes']),*members]:
        target=str(root.relative_to(REPO)/row['path']);check(by_target[target]['original']==dict(row,path=str(root/row['path'])))
check(by_target['tests/node-compat/build-engine.sh']['original']==descriptor(OWN/'proposed/tests/node-compat/build-engine.sh'))
stage_text=(OWN/'stage.py').read_text()
check(stage_text.index("for d in preparation['files']")<stage_text.index("subprocess.run(['git','clone'"))
check(stage_text.index("passed['state']")<stage_text.index("subprocess.run(['git','clone'"))
check("'--no-local','--no-checkout'"in stage_text and 'nativeReplacements=3'in stage_text)

recipe=(OWN/'proposed/tests/node-compat/build-engine.sh').read_text()
helper=(OWN/'layer-policy.py').read_text()
check(recipe.index('Task-selection source/work context mismatch')<recipe.index('"$node_bin" --version'))
check(recipe.index('complete342 profile')<recipe.index('fetch_checked()'))
check(recipe.index('Generated artifact basename exceeds255bytes')<recipe.index('fetch_checked "https://'))
check(recipe.count(descriptor(OWN/'layer-policy.py')['sha256'])==5 and recipe.count(descriptor(OWN/'policy.json')['sha256'])==2)
check("metadata['taskSelectionPolicy']"in helper and 'selection_commands=task_selection_commands'in helper)
check('PARENT.validate_compilation('in helper and 'PARENT.decorate('not in helper and 'PARENT.validate_sources('not in helper)
check("POLICY['taskSelectionSourcePolicy']"in helper)
check("allNativeDependentsRequireRebuild':True"in helper and "nativeAllInvalidRuntimeValidation':None"in helper)
heredocs=[]
for match in re.finditer(r"<<'(?P<tag>PY[A-Z]*)'\n(?P<code>[\s\S]*?)\n(?P=tag)(?:\n|$)",recipe):
    ast.parse(match['code']);heredocs.append(match['tag'])
check(len(heredocs)==4)
syntax=[]
for file in OWN.glob('*.py'):ast.parse(file.read_bytes());syntax.append(file.name)

# Resolve actual selected-source build registration without inventing a hook.
frozen=Path(baseline['parentFreezeRoot'])/'source'
cmake=(frozen/'CMakeLists.txt').read_text();hostcmake=(frozen/'host-apis/wasi-0.2.10/host_api.cmake').read_text();rust=(frozen/'cmake/build-crates.cmake').read_text()
for literal in('add_library(extension_api INTERFACE include/extension-api.h','runtime/event_loop.cpp','target_link_libraries(starling-raw.wasm PRIVATE host_api extension_api builtins spidermonkey rust-crates)'):check(literal in cmake)
check('${WASI_0_2_0}/host_api.cpp'in hostcmake)
for literal in('corrosion_import_crate(','${RUST_STATICLIB_LOCK_MODE}','add_rust_lib(rust-hooks','add_library(rust-crates STATIC','add_rust_lib(rust-url'):check(literal in rust)
select_names=[]
for row in native['rows']:
    if row['path'].endswith(('.h','.cpp'))and 'AsyncTask::select' in Path(row['source']['path']).read_text():select_names.append(row['path'])
check(sorted(select_names)==['host-apis/wasi-0.2.0/host_api.cpp','runtime/event_loop.cpp'])
check('static std::optional<size_t> select'in(OWN/'native/include/extension-api.h').read_text())
event=(OWN/'native/runtime/event_loop.cpp').read_text()
check(event.index('if (!selected)')<event.index('const size_t task_idx = *selected;')<event.index('tasks->at(task_idx)'))
hosttext=(OWN/'native/host-apis/wasi-0.2.0/host_api.cpp').read_text()
check(hosttext.index('if (tasks.empty())')<hosttext.index('auto count = tasks.size()'))
for name in ('sourceRoot','workRoot','freezeRoot'):
    check(not Path(stage[name]).exists()and not Path(stage[name]).is_symlink())
future=json.loads((OWN/'future-authority.template.json').read_bytes())
for name in('state','phase','sourceIndexSha256','sourceIndependentReview','rootAction','actualSourceStage','actualBuild','actualFreeze','actualNativeReview','actualComponentReview','allInvalidFixtureSource','allInvalidFixtureReview'):check(future[name]is None)
for value in future['nativePins'].values():check(value is None)
for name in('stageAllowed','buildAllowed','componentAllowed','guestAllowed','sourcePromotionAllowed','runtimeAcceptanceClaim','fullResetOrReuse','als'):check(future[name]is False)
for row in list(inputs.values()):checked(row)
result=dict(schemaVersion=1,state='TASK_SELECTION_INTEGRATION_SOURCE_DATA_PURE_CHECKS_PASSED_V1',sourceOnly=True,checks=checks,actualNativeSources=342,unchangedResourceSources=339,nativeReplacements=3,stageRows=533,preparationInputRows=len(freeze['files']),distinctAuthenticatedFiles=len(inputs),expectedFunctionCases=342,commandParserDataPositive=1,commandParserNegatives=negative_cases,oldMetadataRejected=True,positiveNativeMetadataFabricated=False,derivations=derived,pythonAst=sorted(syntax),recipePythonHeredocs=heredocs,ownerHelpersImported=False,stageOrConfigureOrCompilerOrNativeInvoked=False,engineOrGuestOrRuntimeInvoked=False,sourceActionsOnly=True)
with (OWN/'source-check-results.json').open('x')as out:json.dump(result,out,indent=2);out.write('\n')
print(json.dumps(result))
