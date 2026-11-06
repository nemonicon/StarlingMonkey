"""Pure Source models only; inert own module, no authorize/stage/main/monitor/Git."""
import copy,hashlib,importlib.util,json
from pathlib import Path
OWN=Path(__file__).resolve().parent;assert not(OWN/'index.json').exists()
spec=importlib.util.spec_from_file_location('genuine_new_hash_hmac_stage_source',OWN/'controller.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
refs=json.loads((OWN/'references.json').read_bytes());source_peer=json.loads(Path(refs['actualIntegrationSourceReview']['result']['path']).read_bytes());records=[]
def ok(name,fn):fn();records.append(dict(name=name,passed=True))
def no(name,fn):
 try:fn()
 except (AssertionError,KeyError,ValueError):records.append(dict(name=name,passed=True,rejected=True));return
 raise AssertionError('Accepted negative: '+name)
ok('Actual genuine module OWN and Source context',lambda:exec("assert m.OWN==OWN and m.SOURCE_FAMILY==OWN.parent/'node-crypto-hash-hmac-native-integration-candidate-v1'",{'m':m,'OWN':OWN}))
ok('Actual independent7c5a Root Source peer fields',lambda:m.source_peer_model(source_peer))
for field,value in [('nativeSourceFiles',355),('retainedParentNativeFiles',348),('changedParentNativeFiles',7),('newNativeFiles',0),('selectedManifestCount',11),('auditedBorrowEnabled',True),('sourceReviewPassed',False),('nativeBuildActionsInvoked',True),('cryptoOperationsInvoked',True),('sourceIndexSha256','0'*64)]:
 bad=copy.deepcopy(source_peer);bad[field]=value;no('Source peer rejects '+field,lambda bad=bad:m.source_peer_model(bad))
row=dict(path='builtins/example.cpp',original='/synthetic-no-action/source.cpp',sha256='a'*64,bytes=3,sourceMode=0o644,targetMode=0o600,roles=['NATIVE_SOURCE'])
merged=m.merge_rows([row,{**row,'roles':['ALSO_TOOL_DATA','NATIVE_SOURCE']}]);assert len(merged)==1 and merged[0]['roles']==['ALSO_TOOL_DATA','NATIVE_SOURCE'];records.append(dict(name='Exact byte/origin/mode duplicate unions all roles once',passed=True))
for field,value in [('original','/another-origin'),('sha256','b'*64),('bytes',4),('sourceMode',0o600),('targetMode',0o644)]:
 no('Conflicting duplicate '+field,lambda field=field,value=value:m.merge_rows([row,{**row,field:value}]))
for path in ['../outside','/absolute','a//b','.git/config','.cache/file','x/.cargo/file','node_modules/x','target/x','a\\b','a\x00b']:
 no('Unsafe/cache destination '+repr(path),lambda path=path:m.merge_rows([{**row,'path':path}]))
root=json.loads((OWN/'root-authority.template.json').read_bytes());own=dict(path=str(OWN/'index.json'),sha256='a'*64,bytes=1)
no('Unissued Root template refuses',lambda:m.root_model(root,own,refs))
root.update(state=root['requiredIssuedState'],sourceStageAllowed=True,stageControllerIndex=own,stageControllerEntry=dict(path=str(OWN/'controller.py'),sha256='b'*64,bytes=1))
ok('Synthetic exact phase shape only, not actual authority',lambda:m.root_model(root,own,refs))
for field,value in [('sourceStageAllowed',False),('nativeSourceFiles',355),('basePlanRows',1581),('expectedSourceCopies',1643),('expectedEmbeddingDataCopies',0),('baselineRevision','0'*40),('externalParentDeadlineSeconds',601),('configuredSourceRoot','/wrong'),('nativeBuildAllowed',True),('borrowAllowed',True),('cryptoOperationsAllowed',True),('actualStageResult',{})]:
 bad=copy.deepcopy(root);bad[field]=value;no('Root rejects '+field,lambda bad=bad:m.root_model(bad,own,refs))
peer=dict(schemaVersion=1,state='INDEPENDENT_NODE_CRYPTO_HASH_HMAC357_STAGE_SOURCE_REVIEW_PASSED_V2',controllerSourceIndexSha256=own['sha256'],integrationSourceIndexSha256=m.SOURCE_SHA,genericMonitorSourceIndexSha256=m.MONITOR_SHA,sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,hostActionsInvoked=False,sourceStageActionsInvoked=False,nativeBuildActionsInvoked=False,cryptoOperationsInvoked=False)
ok('Synthetic future stage peer exact shape',lambda:m.stage_peer_model(peer,own))
for field,value in [('controllerSourceIndexSha256','b'*64),('integrationSourceIndexSha256','b'*64),('genericMonitorSourceIndexSha256','b'*64),('sourceStageActionsInvoked',True)]:
 bad=copy.deepcopy(peer);bad[field]=value;no('Stage peer rejects '+field,lambda bad=bad:m.stage_peer_model(bad,own))
raw=b'100644 blob '+b'a'*40+b'\tbuiltins/example.cpp\0'+b'120000 blob '+b'b'*40+b'\tdocs/src/README.md\0'
tree=m.parse_tree(raw);assert tree['builtins/example.cpp']['mode']=='100644'and tree['docs/src/README.md']['mode']=='120000';records.append(dict(name='Actual ls-tree -z record format parsed as DATA',passed=True))
for label,payload in [('unterminated',raw[:-1]),('duplicate',raw+raw),('traversal',b'100644 blob '+b'a'*40+b'\t../outside\0'),('gitdir',b'100644 blob '+b'a'*40+b'\t.git/config\0'),('bad oid',raw.replace(b'a'*40,b'x'*40))]:no('Tree rejects '+label,lambda payload=payload:m.parse_tree(payload))
assert m.git_blob_id(b'')=='e69de29bb2d1d6434b8b29ae775ad8c2e48c5391';records.append(dict(name='Real Git empty-blob ID rule',passed=True))
plan=json.loads((OWN/'stage-copy-plan.json').read_bytes());assert len(plan['files'])==len({r['path']for r in plan['files']})==1642 and all(r['targetMode']==0o600 for r in plan['files']);assert len(plan['embeddingData'])==3;records.append(dict(name='Actual1642 destination union and separate3 embedding references',passed=True))
# Pure synthetic environment/argv models. No shell or Git command is run.
import shlex
original={'HOME':'/synthetic-home','home':'/synthetic-home-lower','CODEX_HOME':'/synthetic-codex','PATH':'/synthetic-bin','GIT_DIR':'blocked','GIT_CONFIG_PARAMETERS':'blocked','GIT_CONFIG_COUNT':'7','GIT_TEMPLATE_DIR':'blocked','BASH_ENV':'blocked','ENV':'blocked','BASH_FUNC_bad%%':'secret-sentinel','SHELLOPTS':'blocked','BASHOPTS':'blocked','CDPATH':'blocked','GLOBIGNORE':'blocked','DYLD_INSERT_LIBRARIES':'blocked','LD_PRELOAD':'blocked'}
copy_before=dict(original);env=m.git_environment(original);assert original==copy_before
for key in ['HOME','home','CODEX_HOME','PATH']:assert env[key]==original[key]
for key in ['BASH_ENV','ENV','BASH_FUNC_bad%%','SHELLOPTS','BASHOPTS','CDPATH','GLOBIGNORE','DYLD_INSERT_LIBRARIES','LD_PRELOAD']:assert key not in env
assert env['GIT_CONFIG_GLOBAL']==env['GIT_CONFIG_SYSTEM']=='/dev/null'and env['GIT_CONFIG_COUNT']=='0'and'GIT_DIR'not in env and'GIT_TEMPLATE_DIR'not in env
records.append(dict(name='Explicit Git/shell/loader startup cleanup preserves home and original env',passed=True))
fact=m.git_environment_fact(original);assert fact['valuesRecorded']is False and'secret-sentinel'not in json.dumps(fact)and fact['userHomeVariablesPreserved']is True
records.append(dict(name='Names-only cleanup facts never retain removed values',passed=True))
git='/synthetic tool/quote\'name/git';prefix=m.git_prefix(git);server=m.upload_pack_command(git)
assert shlex.split(server)==prefix+['-c','uploadpack.allowAnySHA1InWant=true','upload-pack']
records.append(dict(name='Real upload-pack command-string tokens safely round-trip without execution',passed=True))
commands=m.initial_git_commands(git);assert len(commands)==4
assert commands[0]==prefix+['init','--template='+m.git_policy()['templateRoot'],'--object-format=sha1','--initial-branch=stage-baseline',str(m.DEST)]
assert commands[1][-2:]==[m.REPO.as_uri(),m.BASE]
for flag in ['--no-tags','--depth=1','--no-recurse-submodules','--no-auto-maintenance','--no-write-commit-graph']:assert flag in commands[1]
assert '--upload-pack='+server in commands[1]and not any('clone'==x or x=='--unshallow'or'*'in x for row in commands for x in row)
assert commands[2]==prefix+['-C',str(m.DEST),'checkout','--detach',m.BASE]and commands[3]==prefix+['-C',str(m.DEST),'rev-list','--count','HEAD']
records.append(dict(name='Single exact-OID depth1 no-tags fetch; no full-clone or history fallback',passed=True))
for key,value in [('core.hooksPath',m.git_policy()['hooksRoot']),('core.fsmonitor','false'),('gc.auto','0'),('maintenance.auto','false'),('maintenance.strategy','none'),('protocol.allow','never'),('protocol.file.allow','always')]:
 assert [key,value]in m.git_policy()['clientConfig'];records.append(dict(name='Client/server Git control '+key,passed=True))
assert m.git_policy()['transientPackByteCapClaim']is False and m.git_policy()['reachableHistoryExpected']==1
records.append(dict(name='Reachable depth bound does not pretend to cap transient pack bytes',passed=True))
for field,value in [('fetchDepth',2),('automaticTags',True),('automaticMaintenance',True),('transientPackByteCapClaim',True),('templateRoot','/unowned-template')]:
 bad=copy.deepcopy(root);bad['baselineGitPolicy'][field]=value;no('Root rejects Git policy '+field,lambda bad=bad:m.root_model(bad,own,refs))

result=dict(schemaVersion=1,state='HASH_HMAC357_STAGE_V2_PURE_MODELS_PASSED',checks=len(records),records=records,actualOwnModuleContext=True,globalsOrNamespaceRebound=False,authorizeInvoked=False,stageInvoked=False,monitorInvoked=False,gitInvoked=False,nativeHelperImported=False,nativeBuildInvoked=False,cryptoOperationsInvoked=False)
(OWN/'pure-check-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='records'}))
