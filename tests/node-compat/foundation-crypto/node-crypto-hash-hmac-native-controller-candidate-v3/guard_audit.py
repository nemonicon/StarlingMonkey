"""Read/hash/AST-only actual producer joins, adapted from independent C preinspection.
No producer/helper/model import, program invocation, file write or environment mutation.
"""
from pathlib import Path
import ast,hashlib,json,re
from collections import Counter

def audit(source_root,require_diagnostics=True):
 S=Path(source_root).resolve();refs=json.loads((S/'references.json').read_bytes());recipe=Path(refs['recipe']['path']);helper=Path(refs['helper']['path']);policy=Path(refs['policy']['path']);text=recipe.read_text();lines=text.splitlines();proot=recipe.parent;fail=[];joins=[]
 def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
 def need(ok,role,actual=None,wanted=None,line=None):
  joins.append(dict(role=role,passed=bool(ok),actual=actual,wanted=wanted,line=line))
  if not ok:fail.append(joins[-1])
 for k,p in [('recipe',recipe),('helper',helper),('policy',policy)]:
  d=refs[k];need(d['path']==str(S/'producer'/p.name)and sha(p)==d['sha256']and p.stat().st_size==d['bytes'],'actual refs '+k,dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size),d)
 policy_value=json.loads(policy.read_bytes());htree=ast.parse(helper.read_bytes());assign={}
 for n in htree.body:
  if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name):assign[n.targets[0].id]=n.value
 helper_policy=ast.literal_eval(assign['POLICY_SHA256']);auth=ast.literal_eval(assign['AUTH_SHA256']);need(helper_policy==sha(policy),'helper POLICY_SHA256',helper_policy,sha(policy),assign['POLICY_SHA256'].lineno);need(auth==sha(proot/'donor-inputs.json'),'helper AUTH_SHA256/donor-inputs',auth,sha(proot/'donor-inputs.json'),assign['AUTH_SHA256'].lineno)
 need(ast.unparse(assign['HERE'])=='Path(__file__).resolve().parent','genuine HERE by module location',ast.unparse(assign['HERE']),'Path(__file__).resolve().parent');need(ast.unparse(assign['REPO'])=="Path("+repr(refs['configuredSourceRoot'])+")",'genuine configured REPO literal',ast.unparse(assign['REPO']),refs['configuredSourceRoot'])
 need('assert HERE==Path('+repr(str(proot))+')' in helper.read_text(),'helper exact HERE guard',str(proot),str(proot))
 for key,name in [('hashHmacModelSha256','hash-hmac-model.py'),('admissionModelSha256','native-admission-model.py')]:need(policy_value[key]==sha(proot/name),'policy pure-model '+key,policy_value[key],sha(proot/name))
 for k,name in [('metadataModel','native-admission-model.py'),('hashModel','hash-hmac-model.py')]:need(refs[k]['path']==str(proot/name)and refs[k]['sha256']==sha(proot/name),'controller refs '+k,refs[k],str(proot/name))
 need(sha(S/'metadata_model.py')==sha(proot/'native-admission-model.py'),'same pure83 controller/producer model');need(sha(S/'hash_model.py')==sha(proot/'hash-hmac-model.py'),'same hash model controller/producer')
 for key in ['configuredSourceRoot','workRoot','freezeRoot']:need(policy_value['contexts'][key]==refs[key],'policy/refs '+key,policy_value['contexts'][key],refs[key])
 patterns=[('recipe_path exact',r'^\[\[ "\$recipe_path" == "([^"]+)"',str(recipe)),('work_root default',r'^work_root="\$\{NODE_COMPAT_BUILD_ROOT:-([^}]+)\}"',refs['workRoot']),('work_root allowed',r'^\[\[ "\$work_root" == "([^"]+)"',refs['workRoot']),('consumers_layer_root',r'^consumers_layer_root="([^"]+)"',str(proot)),('configured repo_root',r'^repo_root="([^"]+)"',refs['configuredSourceRoot'])]
 for role,pattern,expected in patterns:
  matches=[(n+1,re.match(pattern,l))for n,l in enumerate(lines)if re.match(pattern,l)];need(len(matches)==1,role+' unique',len(matches),1)
  for n,m in matches:need(m[1]==expected,role,m[1],expected,n)
 slots=[]
 for n,l in enumerate(lines,1):
  m=re.search(r'\$\(sha256_file "\$consumers_layer_root/(layer-policy\.py|policy\.json)"\)" == ([a-f0-9]{64})',l)
  if m:
   target=helper if m[1]=='layer-policy.py'else policy;slots.append(dict(kind='shell',target=target.name,line=n,digest=m[2]));need(m[2]==sha(target),'shell active '+target.name,m[2],sha(target),n)
 need(sum(x['kind']=='shell'and x['target']=='layer-policy.py'for x in slots)==2,'all2 shell helper guards present');need(sum(x['kind']=='shell'and x['target']=='policy.json'for x in slots)==2,'all2 shell policy guards present')
 # Parse actual Python heredocs, never evaluate statements.
 heredocs=[]
 for n,l in enumerate(lines):
  m=re.search(r"<<'([A-Z][A-Z0-9_]*)'",l)
  if not m:continue
  tag=m[1];end=next(j for j in range(n+1,len(lines))if lines[j]==tag);body='\n'.join(lines[n+1:end])+'\n';tree=ast.parse(body);heredocs.append(dict(tag=tag,start=n+2,end=end+1))
  for x in ast.walk(tree):
   if not isinstance(x,ast.Compare)or len(x.ops)!=1 or not isinstance(x.ops[0],ast.Eq):continue
   left=x.left;right=x.comparators[0]
   if isinstance(left,ast.Call)and isinstance(left.func,ast.Name)and left.func.id=='digest'and len(left.args)==1 and isinstance(left.args[0],ast.Name)and left.args[0].id=='layer_file'and isinstance(right,ast.Constant)and isinstance(right.value,str):
    line=n+1+x.lineno;slots.append(dict(kind='python',target=helper.name,line=line,digest=right.value));need(right.value==sha(helper),'Python active helper guard',right.value,sha(helper),line)
 need(sum(x['kind']=='python'for x in slots)==3,'all3 Python helper guards present')
 for needle,role in [("assert digest(layer_file.parent / 'policy.json') == layer.POLICY_SHA256",'postdecorate policy guard'),("assert digest(model_file)==layer.POLICY['admissionModelSha256']",'prepublication pure83 guard'),("assert digest(pathlib.Path(actual_recipe)) == pathlib.Path(recipe_before).read_text().strip()",'recipe before/after selfhash'),("'buildRecipeSha256': digest(pathlib.Path(actual_recipe))",'actual recipe metadata digest'),('sha256_file "$recipe_path" > "$recipe_before"','prebuild selfhash capture'),("classification=model.validate_metadata(metadata,layer.POLICY,layer.POLICY_SHA256,digest(layer_file),digest(pathlib.Path(actual_recipe)),componentize_inputs,'normal-off')",'final model current tuple')]:need(needle in text,role)
 need('"$recipe_path" "$consumers_layer_root/layer-policy.py" <<\'PY\''in text,'metadata CLI passes actual recipe/helper path')
 for d in refs['buildEnvironment'].items():
  if d[0]in ['NODE_COMPAT_BUILD_ROOT','RUSTUP_HOME','CARGO_HOME']:need(d[1].startswith(refs['workRoot']),'environment follows new WORK '+d[0],d[1],refs['workRoot'])
 future=json.loads((S/'future-source-review-contract.json').read_bytes())
 for key,ref in [('producerRecipeSha256','recipe'),('producerHelperSha256','helper'),('producerPolicySha256','policy')]:need(future['requiredFixedValues'][key]==refs[ref]['sha256'],'future Source peer '+key,future['requiredFixedValues'][key],refs[ref]['sha256'])
 result=dict(schemaVersion=1,sourceRoot=str(S),passed=not fail,joins=joins,activeLiteralSlots=slots,heredocsParsed=heredocs,failures=fail,producerHelperOrRecipeImported=False,toolOrNativeAction=False,scope='Static semantic pair inventory; no native/raw83 or Source approval')
 
 if require_diagnostics:
  parent_root=Path(refs['parentControllerIndex']['path']).parent
  parent_refs=json.loads((parent_root/'references.json').read_bytes());parent_text=Path(parent_refs['recipe']['path']).read_text()
  def remaining_pins(value):
   pins=Counter(re.findall(r'(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])',value))
   removed=[]
   for pattern in [r'\$\(sha256_file "\$consumers_layer_root/(?:layer-policy\.py|policy\.json)"\)" == ([0-9a-f]{64})',r"assert digest\(layer_file\) == '([0-9a-f]{64})'"]:
    for h in re.findall(pattern,value):pins[h]-=1;removed.append(h)
   return +pins,removed
  old_pins,old_owned=remaining_pins(parent_text);new_pins,new_owned=remaining_pins(text)
  need(len(old_owned)==len(new_owned)==7,'complete parent/new seven owned literal guard classification',len(new_owned),7)
  need(new_pins==old_pins,'every other producer SHA literal pin unchanged',dict(new_pins),dict(old_pins))
  for slot in slots:
   if slot['kind']=='shell':need('HASH_HMAC357_'+('HELPER'if slot['target']=='layer-policy.py'else'POLICY')+'_SHA_MISMATCH:'in lines[slot['line']-1],'identified shell guard diagnostic',line=slot['line'])
 result.update(passed=not fail,failures=fail)
 return result
