"""Read-only verification of retained guard predicates/results. No snippets run."""
from pathlib import Path
import ast,hashlib,json,re,shlex,collections
P=Path(__file__).resolve().parent;S=P.parent/'node-crypto-hash-hmac-native-controller-candidate-v3';refs=json.loads((S/'references.json').read_bytes());record=json.loads((S/'guard-regression-results.json').read_bytes());ind=json.loads(Path('/private/tmp/hashhmac357-controller-v3-semantic.stdout').read_bytes());checks=0

def yes(v,m='guard evidence'):
 global checks
 checks+=1;assert v,m

def pins(text):
 c=collections.Counter(re.findall(r'(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])',text));removed=[]
 for rx in [r'\$\(sha256_file "\$consumers_layer_root/(?:layer-policy\.py|policy\.json)"\)" == ([0-9a-f]{64})',r"assert digest\(layer_file\) == '([0-9a-f]{64})'"]:
  for h in re.findall(rx,text):c[h]-=1;removed.append(h)
 return +c,removed
old=Path(refs['parentControllerIndex']['path']).parent;or_=json.loads((old/'references.json').read_bytes());oldtext=Path(or_['recipe']['path']).read_text();newtext=Path(refs['recipe']['path']).read_text();a,aa=pins(oldtext);b,bb=pins(newtext);yes(a==b and len(aa)==len(bb)==7,'every non-owned SHA pin preserved')
yes(ind['passed']and len(ind['joins'])==50 and len(ind['activeLiteralSlots'])==7);yes(record['newAudit']['passed']and len(record['newAudit']['joins'])==56);yes(record['newAudit']['activeLiteralSlots']==ind['activeLiteralSlots']);yes(not record['oldAudit']['passed']and len(record['oldAudit']['failures'])==2 and all(x['role']=='shell active policy.json'for x in record['oldAudit']['failures']))
# Current independent source slots reject any altered digest/missing/duplicated slot.
expected=ind['activeLiteralSlots']
def exact(slots):
 assert len(slots)==7 and len({(s['kind'],s['line'])for s in slots})==7
 for s in slots:
  actual=refs['helper'if s['target']=='layer-policy.py'else'policy']['sha256'];assert s['digest']==actual
for n in range(7):
 bad=[dict(x)for x in expected];bad[n]['digest']='0'*64
 try:exact(bad)
 except AssertionError:checks+=1
 else:raise AssertionError('mutant accepted')
for bad in [expected[:-1],expected+[expected[0]]]:
 try:exact(bad)
 except AssertionError:checks+=1
 else:raise AssertionError('slot shape accepted')
seen=set()
for r in record['isolatedSourceGuardCommands']:
 root=old if r['generation']=='old-v2'else S;rr=json.loads((root/'references.json').read_bytes());text=Path(rr['recipe']['path']).read_text();lines=text.splitlines();function=text[text.index('sha256_file() {'):text.index('\nfetch_checked()',text.index('sha256_file() {'))];slot=next(x for x in (record['oldAudit']if root==old else ind)['activeLiteralSlots']if x['kind']=='shell'and x['line']==r['line']);line=lines[r['line']-1]
 if r['variant']=='counterfactual-zero-pin':line=line.replace(slot['digest'],'0'*64)
 script='set -eu\n'+function+'\nconsumers_layer_root='+shlex.quote(str(root.resolve()/'producer'))+'\n'+line+'\n';yes(r['argv']==[refs['bash']['path'],'--noprofile','--norc','-c',script]);yes(r['stdoutUtf8']=='');expectedExit=1 if r['variant']!='actual'or(root==old and r['target']=='policy.json')else 0;yes(r['rawExitCode']==r['expectedExitCode']==expectedExit)
 if root==S and expectedExit:yes('HASH_HMAC357_'+('HELPER'if r['target']=='layer-policy.py'else'POLICY')+'_SHA_MISMATCH:'in r['stderrUtf8'])
 if not expectedExit:yes(r['stderrUtf8']=='')
 yes(r['sourceHashGuardOnly']and r['producerOrHelperEntryInvoked']is False);key=(r['generation'],r['variant'],r['line']);yes(key not in seen);seen.add(key)
yes(len(seen)==12);yes(sum(r['generation']=='new-v3'and r['variant']=='actual'and r['rawExitCode']==0 for r in record['isolatedSourceGuardCommands'])==4)
for name in ['stream_copy','populate_cache']:
 source=[]
 for p in [old/'build_body.py',S/'build_body.py']:
  text=p.read_text();tree=ast.parse(text);fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name==name);source.append(ast.get_source_segment(text,fn))
 yes(source[0]==source[1],'actual retained mode function identical '+name)
ctl=(S/'controller.py').read_text();yes("load(frame,'guard_audit.py').audit(OWN)"in ctl);yes(ctl.index("load(frame,'guard_audit.py').audit(OWN)")<ctl.index('def launcher('));yes('len(guard_report[\'activeLiteralSlots\'])==7'in ctl)
value=dict(schemaVersion=1,passed=True,checks=checks,independentSemanticJoins=50,sourceSemanticJoins=56,activeLiteralHashSites=7,allOtherShaLiteralPinsUnchanged=True,retainedGuardSnippetCommands=12,allNewActualShellPredicatesPassed=4,allNewZeroPinPredicatesRefused=4,oldActualPolicyFailures=2,modeFunctionsExactV2=True,sourceRuntimeAuditBeforePhase=True,snippetOrProducerOrHelperRerun=False,evidenceScope='Authenticated retained source/outcome/script records plus current file semantic joins; not new Bash/syscall/producer execution')
(P/'guard-evidence-review.json').write_text(json.dumps(value,indent=2)+'\n');print(json.dumps(value))
