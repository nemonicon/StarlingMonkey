"""Benign read/hash guard units only. Never executes a producer/helper entry."""
from pathlib import Path
import ast,hashlib,importlib.util,json,os,re,subprocess
OWN=Path(__file__).resolve().parent;OLD=OWN.with_name('node-crypto-hash-hmac-native-controller-candidate-v2')
def load(p,name):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def row(p):
 b=Path(p).read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
audit=load(OWN/'guard_audit.py','actual_source_only_guard_audit');controller=load(OWN/'controller.py','actual_inert_controller_for_env')
old=audit.audit(OLD,False);new=audit.audit(OWN);assert not old['passed']and len(old['failures'])==2 and all(r['role']=='shell active policy.json'for r in old['failures']);assert new['passed']and len(new['activeLiteralSlots'])==7
checks=4
# Every actual literal slot is bound to its current actual Source bytes, not guessed data.
refs=json.loads((OWN/'references.json').read_bytes());actual={'policy.json':refs['policy']['sha256'],'layer-policy.py':refs['helper']['sha256']}
def exact_slots(slots):
 assert len(slots)==7 and len({(s['kind'],s['line'])for s in slots})==7
 assert sum(s['kind']=='shell'and s['target']=='policy.json'for s in slots)==2
 assert sum(s['kind']=='shell'and s['target']=='layer-policy.py'for s in slots)==2
 assert sum(s['kind']=='python'and s['target']=='layer-policy.py'for s in slots)==3
 assert all(s['digest']==actual[s['target']]for s in slots)
exact_slots(new['activeLiteralSlots']);checks+=1
for i in range(7):
 bad=[dict(s)for s in new['activeLiteralSlots']];bad[i]['digest']='0'*64
 try:exact_slots(bad)
 except AssertionError:checks+=1
 else:raise AssertionError('stale literal accepted')
for bad in [new['activeLiteralSlots'][:-1],new['activeLiteralSlots']+[new['activeLiteralSlots'][0]]]:
 try:exact_slots(bad)
 except AssertionError:checks+=1
 else:raise AssertionError('missing/duplicated guard accepted')
# Retain actual V2 filesystem evidence only because both generic copy functions
# are byte-identical. Do not rerun fixed-root test or any real native cache copy.
for name in ['stream_copy','populate_cache']:
 texts=[]
 for p in [OLD/'build_body.py',OWN/'build_body.py']:
  src=p.read_text();tree=ast.parse(src);n=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name==name);texts.append(ast.get_source_segment(src,n))
 assert texts[0]==texts[1];checks+=1
# Execute ONLY extracted source-authentication guard snippets in a benign unit
# harness. No recipe entry, helper CLI/import, archive/cache/configure/build.
assert row(Path(refs['bash']['path']))==refs['bash'];env,_=controller.clean_environment(dict(os.environ));env['PATH']=refs['hostPath']
for name in ['PYTHONPATH','PYTHONHOME','PYTHONSTARTUP','PYTHONINSPECT']:env.pop(name,None)
records=[]
for generation,report in [('old-v2',old),('new-v3',new)]:
 root=OLD if generation=='old-v2'else OWN;rr=json.loads((root/'references.json').read_bytes());text=Path(rr['recipe']['path']).read_text();lines=text.splitlines();a=text.index('sha256_file() {');b=text.index('\nfetch_checked()',a);hash_function=text[a:b]
 for slot in report['activeLiteralSlots']:
  if slot['kind']!='shell':continue
  original=lines[slot['line']-1]
  variants=[('actual',original)]
  if generation=='new-v3':variants.append(('counterfactual-zero-pin',original.replace(slot['digest'],'0'*64)))
  for variant,line in variants:
   # The extracted hashing function only reads actual Source DATA files.
   script='set -eu\n'+hash_function+'\nconsumers_layer_root='+__import__('shlex').quote(str(root.resolve()/'producer'))+'\n'+line+'\n'
   argv=[refs['bash']['path'],'--noprofile','--norc','-c',script];r=subprocess.run(argv,env=env,cwd=OWN,capture_output=True,timeout=30,check=False)
   expected=1 if variant!='actual'or(generation=='old-v2'and slot['target']=='policy.json')else 0
   assert r.returncode==expected and r.stdout==b''
   if expected and generation=='new-v3':assert b'HASH_HMAC357_'in r.stderr and b'_SHA_MISMATCH:'in r.stderr
   if expected==0:assert r.stderr==b''
   records.append(dict(generation=generation,variant=variant,line=slot['line'],target=slot['target'],argv=argv,rawExitCode=r.returncode,expectedExitCode=expected,stdoutUtf8=r.stdout.decode(),stderrUtf8=r.stderr.decode(),sourceHashGuardOnly=True,producerOrHelperEntryInvoked=False));checks+=1
assert row(Path(refs['bash']['path']))==refs['bash']
result=dict(schemaVersion=1,state='OWNED_PRODUCER_GUARD_REGRESSION_PASSED_V3',checks=checks,oldSourceRoot=str(OLD),newSourceRoot=str(OWN),oldAudit=old,newAudit=new,isolatedSourceGuardCommands=records,retainedActualModeRegression=row(OLD/'benign-copy-test-results.json'),actualCopyFunctionsByteIdentical=True,actualProducerEntryInvoked=False,actualHelperInvoked=False,nativeCacheCopied=False,compilerInvoked=False,engineOrGuestOrCryptoInvoked=False,scope='Actual Source file guard predicates and read-only semantic/AST joins; failed old policy and all new guards; no producer main or helper API')
(OWN/'guard-regression-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(state=result['state'],checks=checks,oldFailures=len(old['failures']),newJoins=len(new['joins']),newFailures=len(new['failures']),isolatedGuardCommands=len(records),nativeActions=False)))
