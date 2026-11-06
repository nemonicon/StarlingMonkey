"""Source-only V2 derivation. Never invoke Git or a stage/controller phase."""
import ast,hashlib,json,re
from pathlib import Path
OWN=Path(__file__).resolve().parent;V1=OWN.parent/'node-crypto-hash-hmac-stage-candidate-v1';assert not(OWN/'index.json').exists()
text=(V1/'controller.py').read_text();edits=[]
def edit(old,new):
 global text
 positions=[m.start()for m in re.finditer(re.escape(old),text)];assert positions,old[:90]
 edits.append(dict(before=old,after=new,count=len(positions),afterPositions=[p+i*(len(new)-len(old))for i,p in enumerate(positions)]));text=text.replace(old,new)
edit("import hashlib,importlib.util,json,os,shutil,stat,subprocess,sys","import hashlib,importlib.util,json,os,shutil,stat,subprocess,sys,shlex")
edit("OWN=REPO/'tests/node-compat/foundation-crypto/node-crypto-hash-hmac-stage-candidate-v1'","OWN=REPO/'tests/node-compat/foundation-crypto/node-crypto-hash-hmac-stage-candidate-v2'")
edit('node-crypto-hash-hmac-v1-stage-external-root','node-crypto-hash-hmac-v1-stage-v2-external-root')
edit('node-crypto-hash-hmac-v1-stage.json','node-crypto-hash-hmac-v1-stage-v2.json')
for name in ['INDEPENDENT_NODE_CRYPTO_HASH_HMAC357_STAGE_SOURCE_REVIEW_PASSED_V1','ROOT_REVIEWED_NODE_CRYPTO_HASH_HMAC357_SOURCE_STAGE_V1','NODE_CRYPTO_HASH_HMAC357_STAGE_CONFIG_V1','NODE_CRYPTO_HASH_HMAC357_SOURCE_STAGE_RAW_ZERO_UNREVIEWED_V1']:edit(name,name.removesuffix('_V1')+'_V2')
for name in ['NODE_CRYPTO_HASH_HMAC357_SOURCE_STAGE_STARTED','NODE_CRYPTO_HASH_HMAC357_SOURCE_STAGED_NOT_BUILT','NODE_CRYPTO_HASH_HMAC357_SOURCE_STAGE_FAILED_OR_PARTIAL_RETAINED']:edit(name,name+'_V2')
# Replace exact own V1 environment definition, not an imported module namespace.
tree=ast.parse(text);node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='git_environment');edit(ast.get_source_segment(text,node),'')
edit('ownedFreshCloneOnly=True','ownedFreshBaselineCheckoutOnly=True')
edit('fresh-clone, Git-byte-identical','fresh-checkout, Git-byte-identical')
edit('def safe(name):',(OWN/'git-policy.py.txt').read_text()+'\n\n\ndef safe(name):')
edit("    record=dict(argv=argv,timeoutSeconds=120,returncode=None,timedOut=False)","    assert_private_git_policy()\n    record=dict(argv=argv,cwd=git_policy()['commandCwd'],environmentPolicy=git_environment_fact(dict(os.environ)),timeoutSeconds=120,returncode=None,timedOut=False)")
edit("child=subprocess.run(argv,capture_output=True,timeout=120,env=git_environment())","child=subprocess.run(argv,cwd=git_policy()['commandCwd'],capture_output=True,timeout=120,env=git_environment())")
edit("    assert value['phase']=='source-stage-only'and value['sourceStageAllowed']is True","    assert value['phase']=='source-stage-only'and value['sourceStageAllowed']is True\n    assert value['baselineGitPolicy']==refs['baselineGitPolicy']==git_policy()")
edit("    captured=list(unique.values());indices=list({r['path']:r for r in indices}.values())","    source_config=descriptor(REPO/'.git/config');assert source_config['path']not in unique or unique[source_config['path']]==source_config;unique[source_config['path']]=source_config\n    captured=list(unique.values());indices=list({r['path']:r for r in indices}.values())")
edit("copies=plan['files'],embedding=plan['embeddingData'])","copies=plan['files'],embedding=plan['embeddingData'],originalRepositoryConfig=source_config)")
edit("        recheck(frame);result['originalProtection']=durable", "        policy=git_policy();policy_root=Path(policy['commandCwd']);absent(policy_root);policy_root.mkdir(mode=0o700)\n        for key in ['templateRoot','hooksRoot']:Path(policy[key]).mkdir(mode=0o700)\n        assert_private_git_policy();result['baselineGitPolicy']=policy;result['originalRepositoryConfig']=frame['originalRepositoryConfig']\n        recheck(frame);result['originalProtection']=durable")
old="""        run([git,'clone','--no-local','--no-checkout',str(REPO),str(DEST)])
        run([git,'-C',str(DEST),'checkout','--detach',BASE])"""
edit(old,"        for argv in initial_git_commands(git):last=run(argv)\n        result['baselineGitObservation']=baseline_git_observation(last)\n        assert_private_git_policy()")
edit("tree_record=run([git,'-C',str(DEST),'ls-tree','-r','-z','--full-tree',BASE])","tree_record=run(git_prefix(git)+['-C',str(DEST),'ls-tree','-r','-z','--full-tree',BASE])")
edit("record=run([git,'-C',str(DEST),'cat-file','blob',item['object']])","record=run(git_prefix(git)+['-C',str(DEST),'cat-file','blob',item['object']])")
edit("        actual_links={str(p.relative_to(DEST)):os.readlink(p)for p in DEST.rglob('*')if p.is_symlink()}","        assert_private_git_policy()\n        result['stagedGitObjects']=git_objects(DEST);result['stagedGitObjectBytes']=sum(r['bytes']for r in result['stagedGitObjects'])\n        actual_links={str(p.relative_to(DEST)):os.readlink(p)for p in DEST.rglob('*')if p.is_symlink()}")
old="""    git=frame['root']['gitBinary']['path'];expected=[[git,'clone','--no-local','--no-checkout',str(REPO),str(DEST)],[git,'-C',str(DEST),'checkout','--detach',BASE],[git,'-C',str(DEST),'ls-tree','-r','-z','--full-tree',BASE]]
    expected += [[git,'-C',str(DEST),'cat-file','blob',r['gitObject']]for r in value['baselineDocumentationLinks']]
    assert [r['argv']for r in value['commands']]==expected and len(expected)==6"""
new="""    assert value['baselineGitPolicy']==git_policy() and value['baselineGitObservation']['reachableCommits']==1
    assert value['baselineGitObservation']['tagAndRemoteRefs']==[]
    assert value['originalRepositoryConfig']==frame['originalRepositoryConfig']
    git=frame['root']['gitBinary']['path'];expected=initial_git_commands(git)+[git_prefix(git)+['-C',str(DEST),'ls-tree','-r','-z','--full-tree',BASE]]
    expected += [git_prefix(git)+['-C',str(DEST),'cat-file','blob',r['gitObject']]for r in value['baselineDocumentationLinks']]
    assert [r['argv']for r in value['commands']]==expected and len(expected)==8
    assert all(r['cwd']==git_policy()['commandCwd']and r['environmentPolicy']['userHomeVariablesPreserved']is True for r in value['commands'])"""
edit(old,new)
edit("        checked(value['progress'])","        assert_private_git_policy()\n        observation=value['baselineGitObservation'];checked(observation['fetchHead']);checked(observation['privateConfig']);checked(observation['countRaw'])\n        if observation['shallowBoundary']is not None:checked(observation['shallowBoundary'])\n        assert git_objects(DEST)==value['stagedGitObjects']\n        checked(value['progress'])")
(OWN/'controller.py').write_text(text)
def d(p):p=Path(p).absolute();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
(OWN/'v2-derivation.json').write_text(json.dumps(dict(schemaVersion=1,donorController=d(V1/'controller.py'),donorIndex=d(V1/'index.json'),edits=edits,outputController=d(OWN/'controller.py'),sourceOnly=True,donorNamespaceOrGlobalsRebound=False),indent=2)+'\n')
print(json.dumps(dict(state='SOURCE_DERIVATION_ONLY',edits=len(edits),gitInvoked=False,stageInvoked=False)))
