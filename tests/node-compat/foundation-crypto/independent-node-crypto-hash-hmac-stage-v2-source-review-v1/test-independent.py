"""Independent inert real context and pure models only; never Git/stage/authorize."""
from pathlib import Path
import importlib.util,json,copy,shlex,ast
P=Path(__file__).resolve().parent;S=P.parent/'node-crypto-hash-hmac-stage-candidate-v2'
assert json.loads((P/'source-authentication.json').read_text())['state']=='INDEPENDENT_STAGE_V2_SOURCE_AUTHENTICATION_PASSED'
spec=importlib.util.spec_from_file_location('independent_actual_stage_source_context',S/'controller.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
checks=0
def ok(fn):
 global checks
 fn();checks+=1

def reject(fn):
 global checks
 try:fn()
 except (AssertionError,KeyError,ValueError):checks+=1;return
 raise AssertionError('unexpectedly accepted model')
assert m.OWN==S and m.REPO==Path('/Users/dan/dev/StarlingMonkey')and m.SOURCE_FAMILY==S.parent/'node-crypto-hash-hmac-native-integration-candidate-v1'and m.TIMEOUT==600;checks+=1
refs=json.loads((S/'references.json').read_text());peer=json.loads(Path(refs['actualIntegrationSourceReview']['result']['path']).read_text());ok(lambda:m.source_peer_model(peer))
for key,value in [('nativeSourceFiles',355),('retainedParentNativeFiles',355),('changedParentNativeFiles',0),('newNativeFiles',0),('externalEmbeddingSources',0),('selectedManifestCount',11),('auditedBorrowEnabled',True),('cryptoOperationsInvoked',True),('sourceReviewPassed',False)]:
 v=copy.deepcopy(peer);v[key]=value;reject(lambda v=v:m.source_peer_model(v))
for bad in ['../escape','/absolute','a//b','a\\b','a\0b','.git/config','.cargo/x','x/node_modules/a','target/object.o']:
 reject(lambda bad=bad:m.copy_safe(bad))
row=dict(path='builtins/example.cpp',original='/synthetic-data-only/original.cpp',sha256='a'*64,bytes=3,sourceMode=0o644,targetMode=0o600,roles=['first']);merged=m.merge_rows([row,{**row,'roles':['second']}]);assert len(merged)==1 and merged[0]['roles']==['first','second'];checks+=1
for key,value in [('original','/different'),('sha256','b'*64),('bytes',4),('sourceMode',0o600),('targetMode',0o644)]:reject(lambda key=key,value=value:m.merge_rows([row,{**row,key:value}]))
original={'HOME':'/synthetic-home','home':'/synthetic-lower','CODEX_HOME':'/synthetic-codex','PATH':'/synthetic-path','GIT_DIR':'sentinel','GIT_OBJECT_DIRECTORY':'sentinel','GIT_ALTERNATE_OBJECT_DIRECTORIES':'sentinel','GIT_CONFIG_PARAMETERS':'sentinel','GIT_EXEC_PATH':'sentinel','GIT_CONFIG_COUNT':'9','GIT_TEMPLATE_DIR':'sentinel','BASH_FUNC_injected%%':'not-a-real-secret','BASH_ENV':'sentinel','ENV':'sentinel','SHELLOPTS':'sentinel','BASHOPTS':'sentinel','CDPATH':'sentinel','GLOBIGNORE':'sentinel','LD_PRELOAD':'sentinel','DYLD_INSERT_LIBRARIES':'sentinel'};before=copy.deepcopy(original);env=m.git_environment(original);assert original==before;checks+=1
for key in ['HOME','home','CODEX_HOME','PATH']:assert env[key]==original[key];checks+=1
for key in original:
 if key.startswith(('GIT_','BASH_FUNC_'))or key in ['BASH_ENV','ENV','SHELLOPTS','BASHOPTS','CDPATH','GLOBIGNORE','LD_PRELOAD','DYLD_INSERT_LIBRARIES']:assert key not in env or key=='GIT_CONFIG_COUNT'and env[key]=='0';checks+=1
assert env['GIT_CONFIG_GLOBAL']==env['GIT_CONFIG_SYSTEM']=='/dev/null'and env['GIT_CONFIG_NOSYSTEM']=='1';checks+=1
fact=m.git_environment_fact(original);assert fact['valuesRecorded']is False and'not-a-real-secret'not in json.dumps(fact)and fact['userHomeVariablesPreserved']is True;checks+=1
# The actual upload-pack API accepts a single shell command string, so every
# token must round-trip shlex including spaces/quotes/metacharacters. No shell.
for git in ['/synthetic/bin/git',"/synthetic path/quoted'name/$literal`not-run`/git"]:
 server=m.upload_pack_command(git);assert shlex.split(server)==m.git_prefix(git)+['-c','uploadpack.allowAnySHA1InWant=true','upload-pack'];checks+=1
 commands=m.initial_git_commands(git);assert len(commands)==4 and commands[1][-2:]==[m.REPO.as_uri(),m.BASE]and'--upload-pack='+server in commands[1]and'--depth=1'in commands[1]and'--no-tags'in commands[1];checks+=1
 assert commands[2]==m.git_prefix(git)+['-C',str(m.DEST),'checkout','--detach',m.BASE]and commands[3]==m.git_prefix(git)+['-C',str(m.DEST),'rev-list','--count','HEAD'];checks+=1
 assert not any(x in ['clone','--unshallow','--tags']for command in commands for x in command);checks+=1
policy=m.git_policy();assert policy==refs['baselineGitPolicy']and policy['reachableHistoryExpected']==1 and policy['transientPackByteCapClaim']is False and policy['originalRepositoryConfigurationModified']is False;checks+=1
for key,value in [('core.hooksPath',policy['hooksRoot']),('core.fsmonitor','false'),('core.attributesFile','/dev/null'),('core.excludesFile','/dev/null'),('gc.auto','0'),('maintenance.auto','false'),('fetch.writeCommitGraph','false'),('submodule.recurse','false'),('protocol.allow','never'),('protocol.file.allow','always')]:assert [key,value]in policy['clientConfig'];checks+=1
root=json.loads((S/'root-authority.template.json').read_text());own=json.loads((P/'source-authentication.json').read_text())['sourceIndex'];reject(lambda:m.root_model(root,own,refs));root.update(state=root['requiredIssuedState'],sourceStageAllowed=True,stageControllerIndex=own,stageControllerEntry={'path':str(S/'controller.py'),'sha256':'b'*64,'bytes':1});ok(lambda:m.root_model(root,own,refs))
for key,value in [('nativeSourceFiles',355),('expectedSourceCopies',1645),('expectedEmbeddingDataCopies',0),('baselineRevision','0'*40),('externalParentDeadlineSeconds',601),('nativeBuildAllowed',True),('borrowAllowed',True),('cryptoOperationsAllowed',True),('metadataProjectionAllowed',True)]:
 bad=copy.deepcopy(root);bad[key]=value;reject(lambda bad=bad:m.root_model(bad,own,refs))
raw=b'100644 blob '+b'a'*40+b'\tbuiltins/example.cpp\0';assert m.parse_tree(raw)['builtins/example.cpp']['object']=='a'*40;checks+=1
for value in [raw[:-1],raw+raw,raw.replace(b'builtins/example.cpp',b'../escape'),raw.replace(b'a'*40,b'x'*40)]:reject(lambda value=value:m.parse_tree(value))
assert m.git_blob_id(b'')=='e69de29bb2d1d6434b8b29ae775ad8c2e48c5391';checks+=1
# Grammar inspection alone, never exec owner self-writing test/check/preparer.
for f in S.glob('*.py'):ast.parse(f.read_text(),filename=str(f));checks+=1
print(json.dumps(dict(schemaVersion=1,checks=checks,passed=True,actualOwnContextTested=True,namespaceOrGlobalsRebound=False,ownerSelfWritingChecksInvoked=False,gitOrAuthorizeOrStageOrHelperOrMonitorOrNativeOrCryptoInvoked=False,syntheticRootShapeOnlyNotAuthority=True)))
