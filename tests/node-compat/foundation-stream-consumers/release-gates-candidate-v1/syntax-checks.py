"""Parse-only selected JS and owned Python source. Never import owner code."""
from pathlib import Path
import ast,hashlib,json,os,subprocess
H=Path(__file__).resolve().parent
node=json.loads((H/'tool-context.json').read_bytes())['invocation']['nodeRealPath']
graph=json.loads((H/'selected-closure.json').read_bytes());names=sorted({row['path']for row in graph['localModulesAndData']if row['path'].endswith(('.mjs','.js','.cjs'))}|{'test-contracts.mjs','native-preflight.mjs'})
rows=[];env={k:v for k,v in os.environ.items()if k not in ['NODE_OPTIONS','NODE_PATH']and not k.startswith('NAPI_RS_')}
for name in names:
 result=subprocess.run([node,'--check',str(H/name)],capture_output=True,text=True,env=env)
 rows.append({'path':name,'argv':[node,'--check',str(H/name)],'code':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'sourceSha256':hashlib.sha256((H/name).read_bytes()).hexdigest()})
 assert result.returncode==0,(name,result.stderr)
template=(H/'native-preflight.template.mjs').read_text().replace('@CONFIG_SHA@','a'*64).replace('@INPUTS_SHA@','b'*64)
result=subprocess.run([node,'--check','--input-type=module'],input=template,capture_output=True,text=True,env=env)
rows.append({'path':'IN_MEMORY_RENDERED_BRIDGE_SYNTAX_ONLY','argv':[node,'--check','--input-type=module'],'code':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'sourceSha256':hashlib.sha256(template.encode()).hexdigest(),'actualAuthority':False});assert result.returncode==0,result.stderr
python=[]
for p in sorted(H.glob('*.py')):ast.parse(p.read_text(),filename=str(p));python.append({'path':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
print(json.dumps({'schemaVersion':1,'state':'passed','javascriptParseOnly':len(rows),'pythonAstOnly':len(python),'javascript':rows,'python':python,'sourcePublisherExecuted':False,'ownerModuleImported':False,'nativeOrGuestExecuted':False}))
