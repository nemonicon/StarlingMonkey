"""Pure authority/scratch/source checks; no activation or genuine verifier."""
from pathlib import Path
import argparse,ast,hashlib,importlib.util,json
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();output=args.output.absolute()
 assert str(output).startswith('/tmp/starling-node-compat/')and not output.exists();output.mkdir(parents=True,exist_ok=False)
 spec=importlib.util.spec_from_file_location('pure_correctness_authority_v2',HERE/'authority.py');authority=importlib.util.module_from_spec(spec);spec.loader.exec_module(authority)
 checks=[]
 def check(name,value=True):assert value,name;checks.append(name)
 def rejected(name,value):
  raw=(json.dumps(value)+'\n').encode();path=output/('case'+str(len(checks))+'.json');path.write_bytes(raw)
  try:authority.load_authority(path,sha(raw),output/'must-not-read-native.json',sha(b'absent'))
  except(AssertionError,KeyError,TypeError):check(name)
  else:raise AssertionError('Unexpected acceptance')
 for name,value in [('null',None),('future template',json.loads((HERE/'future-authority.json').read_bytes())),('unreviewed',{'schemaVersion':1,'state':'UNREVIEWED_CLASSIC_TRACE_BENCHMARK_DIAGNOSTIC_PIN_CANDIDATES_V3'}),('wrong producer generation',{'schemaVersion':1,'state':'ROOT_REVIEWED_CLASSIC_TRACE_BENCHMARK_DIAGNOSTIC_FREEZES_V2'}),('production authority',{'schemaVersion':1,'state':'REVIEWED_REAL_CLASSIC_TRACE_PRODUCTION_FREEZES_V1'}),('ON null',{'schemaVersion':1,'state':'ROOT_REVIEWED_CLASSIC_TRACE_BENCHMARK_DIAGNOSTIC_FREEZES_V3','variants':{'benchmark-classic-on':None,'benchmark-classic-off':None}})]:rejected(name+' refuses before native input/output',value)
 malformed=output/'malformed.json';malformed.write_text('{bad')
 try:authority.document(malformed,sha(b'different bytes'))
 except AssertionError:check('hash precedes malformed authority JSON parsing')
 else:raise AssertionError('Malformed authority was parsed')
 parent=HERE.parent/'measurement-correctness-activation-candidate-v1';amend=HERE.parent/'measurement-correctness-persistence-amendment-v1'
 for root,digest,count in [(parent,'ce2f254f2cf27d44df5f0d23915ca4e09c98ac15b2f88f762d41f57fb8e6048e',19),(amend,'60a8687e9b6bfff4c68df2a36e9dd47ad0f5cd327441f8cf32d63caa67518ba8',35)]:
  raw=(root/'index.json').read_bytes();assert sha(raw)==digest;rows=json.loads(raw)['files'];assert len(rows)==count
  for row in rows:assert sha((root/row['path']).read_bytes())==row['sha256']and(root/row['path']).stat().st_size==row['bytes']
  check('immutable source family rehashed '+root.name)
 for name in ['authority.py','future-authority.json']:check('unchanged native authority/backend schema '+name,(HERE/name).read_bytes()==(parent/name).read_bytes())
 proof=json.loads((HERE/'transformation-proof.json').read_bytes());source=(HERE/'activate.py').read_text();value=source
 for edit in reversed(proof['edits']):
  for at in reversed(edit['afterOffsets']):assert value[at:at+len(edit['new'])]==edit['new'];value=value[:at]+edit['old']+value[at+len(edit['new']):]
 check('six exact activation-only edits reverse to ce2',value==(parent/'activate.py').read_text()and len(proof['edits'])==6)
 check('actual authority hashed before genuine backend import',source.index('load_authority(pin_path')<source.index("spec_from_file_location('benchmark_common'"))
 check('new persistence index authenticated before native verifier import',source.index('persist_rows=indexed(PERSIST,PERSIST_INDEX)')<source.index("spec_from_file_location('benchmark_common'"))
 check('same declared/canonical actual source roots remain bound','DECLARED.resolve(strict=True)==CANONICAL'in source)
 check('genuine v3 source/frozen verification remains direct','backend.require_source_root(CANONICAL)'in source and 'backend.verify_frozen(LABEL)'in source)
 check('same real native tuple compared to Root data','assert pin[key]==value'in source)
 check('both mandatory reporting and persistence afterimages included',"regular(PERSIST/'proposed/component-driver.mjs')"in source and"regular(AMEND/'bounded-comparison.mjs')"in source and"regular(PERSIST/'durable-host.mjs')"in source)
 check('complete original body payload list unchanged',source[source.index("names=['native-provider"):source.index('payload={name:regular(BASE/name)')]==(parent/'activate.py').read_text()[(parent/'activate.py').read_text().index("names=['native-provider"):(parent/'activate.py').read_text().index('payload={name:regular(BASE/name)')])
 check('both parent/new amendment are in consumed index closure','(PREVIOUS,previous_rows,PREVIOUS_INDEX),(PERSIST,persist_rows,PERSIST_INDEX)'in source)
 check('whole actual native/addon/tool/frozen closure preserved',all(x in source for x in ["metadata['sourceManifest']",'backend.capture_addons()','backend.tool_dependencies(CANONICAL)',"receipt['copies']","for root in [BASE,PRODUCER]"]))
 check('tool tree/link membership remains exact',"tool_trees==original['toolTrees']and tool_links==original['toolLinks']"in source)
 check('publication remains exclusive with final authority/source/tool recheck','stage.mkdir(exist_ok=False)'in source and"path.open('xb')"in source and"tool_snapshot(roots)==(tool_trees,tool_links)"in source and source.rfind('load_authority(pin_path')>source.index('stage.mkdir(exist_ok=False)'))
 check('new output only; predecessor is preserved',"OUTPUT=HERE.parent/'measurement-correctness-activated-v2'"in source)
 check('new activation output not created',not(HERE.parent/'measurement-correctness-activated-v2').exists())
 check('new staging not created',not(HERE.parent/'measurement-correctness-activated-v2.staging').exists())
 for path in HERE.glob('*.py'):ast.parse(path.read_text());check('Python AST '+path.name)
 result={'schemaVersion':1,'state':'PURE_CORRECTNESS_V2_ACTIVATION_SOURCE_CHECKS_PASSED','passed':len(checks),'checks':checks,'actionMainOrGenuineVerifierOrPreflightOrGuestOrNativeOrTargetHostInvoked':False,'activationOutputCreated':False}
 (output/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'passed':len(checks),'output':str(output)}))
if __name__=='__main__':main()
