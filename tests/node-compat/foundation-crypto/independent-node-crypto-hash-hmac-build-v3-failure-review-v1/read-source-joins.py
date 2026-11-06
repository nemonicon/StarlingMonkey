"""Static cross-file literal joins only, never Bash/helper/recipe execution."""
from pathlib import Path
import ast,hashlib,json,re
P=Path(__file__).resolve().parent;K=P.parent;SOURCE=K/'node-crypto-hash-hmac-native-controller-candidate-v2';checks=0;rows={}
def need(v,m):
 global checks
 assert v,m;checks+=1

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def desc(p):p=Path(p);return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def checked(d):
 p=Path(d['path']);need(p.is_absolute()and p.is_file()and not p.is_symlink()and p.stat().st_size==d['bytes']and sha(p)==d['sha256'],'immutable whole Source/peerrole');rows[str(p)]=d;return p

def read(d):return json.loads(checked(d).read_bytes())
def family(ix):
 v=read(ix);root=Path(ix['path']).parent;names={'index.json'}
 for x in v['files']:
  n=x['path'];need(n not in names and n and not n.startswith('/')and all(p not in('','.','..')for p in n.split('/')),'unique confined family member');names.add(n);checked(dict(x,path=str(root/n)))
 need(not any(p.is_symlink()for p in root.rglob('*'))and {p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==names,'whole exact Sourcefamily')
ix=desc(SOURCE/'index.json');need(ix['sha256']=='e8b47cc8eac2decb8822f0aded016594fcc10f9d997b5f2461d251bb98d4953a','original held Sourcee8b');family(ix)
peerbase=K/'independent-node-crypto-hash-hmac-native-controller-v2-source-review-v1';peerix=desc(peerbase/'index.json');need(peerix['sha256']=='552b65afb52f2b24e60436ba850b7b71c96098ced45c142cd5357d954e6b5809','actual552 Sourcepeer');family(peerix);peer=read(desc(peerbase/'results.json'));contract=read(desc(peerbase/'result-contract.json'));need(peer['controllerSourceIndexSha256']==ix['sha256']and peer['sourceOnly']is peer['sourceReviewPassed']is True and peer['state']==contract['requiredReviewState'],'original Sourcepeer held unchanged')
for group in ['requiredFixedValues','requiredExactDescriptors']:
 for n,v in contract.get(group,{}).items():need(peer[n]==v,'whole Sourcepeercontract '+n)
refs=json.loads((SOURCE/'references.json').read_bytes());recipe=checked(refs['recipe']);helper=checked(refs['helper']);policyfile=checked(refs['policy']);text=recipe.read_text();pol=json.loads(policyfile.read_bytes());actual={'layer-policy.py':sha(helper),'policy.json':sha(policyfile)}
need(actual['policy.json']=='b2421527506774820551e448b8536e43e0a4e402cc6788dc62409c161debdf91'and actual['layer-policy.py']=='8bd80bb637929f13717df8afa29839bcf677f35cc6af42feceeaf769f3f0b4cd','actual new producer tuples')
joins=[]
for lineno,line in enumerate(text.splitlines(),1):
 m=re.search(r'sha256_file "\$consumers_layer_root/(layer-policy\.py|policy\.json)"\)" == ([0-9a-f]{64})',line)
 if m:joins.append(dict(kind='shell-entry-guard',line=lineno,target=m[1],expectedLiteral=m[2],actualSha256=actual[m[1]],matches=m[2]==actual[m[1]]))
need(len(joins)==4 and [x['line']for x in joins]==[193,194,203,204],'both actual guard pairs')
old=desc(K/'node-crypto-hash-hmac-native-integration-candidate-v1/policy.json');checked(old);need(old['sha256']=='99f15d4a8f39a3eefeeec738597e57218f2a0dbc8d9febc55ed32f40405402d0','literal is unchanged old policy identity')
need(all(x['matches']is(x['target']=='layer-policy.py')for x in joins),'exactly stale policy guards, helpers correct')
ht=ast.parse(helper.read_text());const={n.targets[0].id:ast.literal_eval(n.value)for n in ht.body if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)and n.targets[0].id in ['POLICY_SHA256','AUTH_SHA256']}
joins.append(dict(kind='helper-policy-literal',target='policy.json',expectedLiteral=const['POLICY_SHA256'],actualSha256=actual['policy.json'],matches=const['POLICY_SHA256']==actual['policy.json']))
post=re.findall(r"assert digest\(layer_file\) == '([a-f0-9]{64})'",text);need(len(post)==3,'all three Python helper guards');joins.extend(dict(kind='python-helper-literal',occurrence=i+1,target='layer-policy.py',expectedLiteral=v,actualSha256=actual['layer-policy.py'],matches=v==actual['layer-policy.py'])for i,v in enumerate(post))
for n,key in [('hash-hmac-model.py','hashHmacModelSha256'),('native-admission-model.py','admissionModelSha256')]:
 d=desc(policyfile.parent/n);checked(d);joins.append(dict(kind='policy-model-literal',target=n,expectedLiteral=pol[key],actualSha256=d['sha256'],matches=pol[key]==d['sha256']))
need("assert digest(layer_file.parent / 'policy.json') == layer.POLICY_SHA256"in text,'postbuild policy uses correct actual helper constant')
need(len([x for x in joins if not x['matches']])==2,'exact bounded join mismatches')
first=next(x['line']for x in joins if not x['matches']);lines=text.splitlines();helper_cli=next(i for i,l in enumerate(lines,1)if l=='python3 "$consumers_layer_root/layer-policy.py" "$repo_root"');fetch=next(i for i,l in enumerate(lines,1)if l.startswith('fetch_checked "https://codeload'))
fresh_record=next(i for i,l in enumerate(lines,1)if l=='PYFRESH');mkdir=next(i for i,l in enumerate(lines,1)if l=='mkdir -p "$source_dir/lib"');need(fresh_record<mkdir<first<helper_cli<fetch,'actual prefix order: fresh record/lib then refusal before helper/fetch')
value=dict(schemaVersion=1,state='SEALED_E8B_PRODUCER_CROSSFILE_POLICY_GUARD_MISMATCH_VALIDATED',sourceIndex=ix,sourcePeer=dict(index=peerix,result=desc(peerbase/'results.json')),recipe=refs['recipe'],helper=refs['helper'],policy=refs['policy'],oldPolicy=old,joins=joins,mismatchedPolicyGuardCount=2,firstBadGuardLine=first,secondBadGuardLine=204,helperCliLine=helper_cli,firstFetchLine=fetch,freshAbiRecordCompletionLine=fresh_record,sourceLibMkdirLine=mkdir,helperPolicyLiteralMatchesActual=True,original552SourcePeerMissedLiteralJoin=True,checks=checks,currentSourceAndPeerHashFiles=len(rows),nativeSourceOrStageChanged=False,recipeHelperOrBashExecuted=False,actualFailureReport=None)
(P/'source-joins-summary.json').write_text(json.dumps(value,indent=2)+'\n');(P/'source-input-hashes.json').write_text(json.dumps(dict(schemaVersion=1,files=list(rows.values())),indent=2)+'\n');print(json.dumps({k:value[k]for k in ['state','checks','currentSourceAndPeerHashFiles','mismatchedPolicyGuardCount','firstBadGuardLine','secondBadGuardLine']}))
