#!/usr/bin/env python3
"""Pure source/data checks. Does not import or call the publisher/owner code."""
import ast,hashlib,json,os
from pathlib import Path
P=Path(__file__).resolve().parent;S=P.parent;B=S/'release-gates-candidate-v1';C=S/'release-gates-context-amendment-v1';F=S/'release-gates-activated-v2'
checks=[]
def h(b):return hashlib.sha256(b).hexdigest()
def data(p):return json.loads(Path(p).read_text())
def yes(v,label):
 assert v,label;checks.append(label)
def rejects(fn,label):
 try:fn()
 except (AssertionError,KeyError,ValueError):checks.append(label)
 else:raise AssertionError(label+' unexpectedly accepted')
inputs=data(P/'source-inputs.json')['files'];yes(len(inputs)==len({x['path'] for x in inputs}),'unique original source preparation rows')
for x in inputs:
 b=Path(x['path']).read_bytes();assert len(b)==x['bytes'] and h(b)==x['sha256'],x['path']
checks.append('all original source preparation inputs rehashed')
der=data(P/'derivations.json');pub=(P/'publish.py').read_text();reverse=pub
for e in reversed(der['publisherEdits']):assert reverse.count(e['after'])==1;reverse=reverse.replace(e['after'],e['before'])
yes(reverse==(C/'publish.py').read_text() and len(der['publisherEdits'])==14,'fourteen exact publisher reversals to9080')
before=(C/'run-gates.after.mjs').read_bytes();after=(P/'run-gates.after.mjs').read_bytes();yes(after==before.replace(b'production-consumers355-release-gates-v2/',b'production-consumers355-release-gates-v3/'),'one exact runtime-output namespace edit')
for n in ['prepare-source.py','publish.py','test-source.py']:ast.parse((P/n).read_text(),filename=n);checks.append('Python AST only '+n)
yes("output.name=='release-gates-activated-v3'" in pub,'fresh activated-v3 only')
yes("'ROOT_REVIEWED_CONSUMERS355_RELEASE_REPORT_DATA_AMENDMENT_V1'" in pub and "source_review['contextAmendmentIndexSha256']==CONTEXT_SHA" in pub,'new exact source Root authority binds both parents')
yes("for root,index in[(HERE,own),(BASE,base),(CONTEXT,context_parent)]:" in pub,'all parent/own indexed source members rechecked')
yes("for row in load(HERE/'source-inputs.json')['files']:checked" in pub,'original source input hashes checked before copy')
yes(pub.index('recheck();source_review=')<pub.index('output.mkdir();temporary.mkdir()'),'full authorization/source checks before outputs')
yes("for r in load(HERE/'source-inputs.json')['files']:add" in pub and "(CONTEXT,context_parent,CONTEXT_SHA)" in pub,'generated source union preserves original context inputs')
yes("'contextAmendmentRoot':str(CONTEXT)" in pub and "'originalPreparationRoot':str(BASE)" in pub,'three source contexts explicit, not rebased')
yes("'runtimeActionAuthority':None" in pub and "'guestExecuted':False" in pub and "'priorPassReused':False" in pub,'source publication not runtime or partial pass reuse')
yes("source_review['runtimeActionsApproved']is False" in pub and "source_review['operationalAdmission']is False" in pub,'no runtime/operational authority')
yes('2*1024**3' in pub and '800*1024**2' in pub,'inherited2GiB/800MiB source-copy guard')
yes(not any(s in pub for s in ['subprocess','importlib','os.system','exec(','eval(']),'publisher no tool/helper/native/guest invocation path')
target='snapshot/tests/node-compat/foundation-util/run-native-node.mjs';producer=(P/'data/run-native-node.mjs').read_bytes();yes(len(producer)==2251 and h(producer)=='fe48fc8049fffbc7d60010f617369e498608db6e69cce05dbc4e06ed96a3c4ba','producer exact immutable2251-byte source data')
current=(B/'snapshot/tests/node-compat/foundation-util/native-node-results.json').read_bytes();yes(h(current)=='489cb9cf4fbe256201f70e385d4326ea32552d2f2a1f187211d9409e73838816','current Node oracle unchanged')
yes("'"+target+"':HERE/'data/run-native-node.mjs'" in pub,'producer only copied as explicit snapshot datum')
matrix=data(P/'report-data-closure.json');rows=matrix['requiredReads'];yes(len(rows)==69,'sixty-nine required finite report/strict/followon data reads')
yes(len(matrix['oracleBuiltinSourceMappings'])==3 and all(x['readSemantics'].startswith('Metadata sourceManifest') for x in matrix['oracleBuiltinSourceMappings']),'oracle source-key checks distinguished from physical data reads')
yes(matrix['producerDataReadOnly'] and matrix['oracleRegenerated'] is False and matrix['oldOracleSubstituted'] is False,'no producer/oracle execution or substitution')
logical={}
for r in rows:
 b=producer if r['path']==target else (F/r['path']).read_bytes();assert h(b)==r['sha256'] and len(b)==r['bytes'];logical[r['path']]=b
checks.append('all required matrix files present with exact bytes')
def verify_matrix(values):
 for r in rows:
  b=values[r['path']];assert len(b)==r['bytes'] and h(b)==r['sha256']
verify_matrix(logical);checks.append('pure finite matrix validator baseline')
for name in [target,'snapshot/tests/node-compat/foundation-add-abort/runtime-async-observation-results.json','snapshot/tests/node-compat/foundation-stream-web/candidate/codec-node-results.json']:
 changed=dict(logical);changed.pop(name);rejects(lambda:verify_matrix(changed),'missing required datum refused '+name)
changed=dict(logical);changed[target]+=b' ';rejects(lambda:verify_matrix(changed),'changed producer data bytes refused')
old=Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-util/native-source-freeze-v7/native-node-results.json').read_bytes()
rejects(lambda:yes(h(old)==h(current),'old oracle not current'),'older oracle substitution refused')
g=data(P/'selected-closure.after.json');yes(len(g['localModulesAndData'])==160 and len(g['localEdges'])==259,'full explicit160-row259-edge graph')
overrides={'run-gates.mjs':P/'run-gates.after.mjs','native-preflight.template.mjs':C/'native-preflight.template.after.mjs','source-contexts.mjs':C/'source-contexts.mjs',target:P/'data/run-native-node.mjs'}
for r in g['localModulesAndData']:
 b=overrides.get(r['path'],B/r['path']).read_bytes();assert len(b)==r['bytes'] and h(b)==r['sha256'],r['path']
checks.append('all graph module/data rows reconstruct from authenticated source contexts')
for e in g['localEdges']:assert os.path.normpath(os.path.join(os.path.dirname(e['importer']),e['request']))==e['target'],e
checks.append('every source/data edge physically resolves to its exact declared target')
yes(g['entries']==data(C/'selected-closure.after.json')['entries'],'no new executable entry')
yes(all(r['path'] in {x['path'] for x in g['localModulesAndData']} for r in rows),'all69 finite required data rows enforced by existing physical graph verifier')
orig=data(P/'snapshot-origins.after.json');parent=data(B/'snapshot-origins.json');added=[x for x in orig['files'] if x not in parent['files']];yes(len(added)==1 and added[0]['sha256']==h(producer) and added[0]['role']=='IMMUTABLE_V7_PRODUCER_SOURCE_READ_ONLY_DATA_NOT_EXECUTED','one physical snapshot addition with immutable provenance only')
yes(all(x in orig['files'] for x in parent['files']),'all old source origins unchanged')
payload=data(B/'payload-files.json')['files']+[target,'report-data-closure.json'];yes(len(payload)==len(set(payload)),'no duplicate publication payload paths')
yes(all(all(len(c.encode())<=255 and c not in ('','.','..') for c in n.split('/')) for n in payload+['release-gates-activated-v3.partial','native-preflight.mjs','input-freeze.json','source-receipt.json','index.json']),'bounded filenames including publication sidecars')
yes(not (S/'release-gates-activated-v3').exists(),'future activated-v3 absent at source preparation')
report=dict(schemaVersion=1,state='SOURCE_ONLY_REPORT_DATA_CLOSURE_CHECKS_PASSED',checks=len(checks),checkNames=checks,originalSourceInputsRehashed=len(inputs),requiredDataReadRows=69,graphRows=160,graphEdges=259,newPhysicalSnapshotFiles=1,ownerPublisherOrHelperInvoked=False,NodeParserCodecNativeGuestOrHostInvoked=False,sourcePublicationExecuted=False,runtimeActionAuthority=None,partialPassReused=False)
(P/'evidence').mkdir(exist_ok=True)
with(P/'evidence/source-checks.json').open('x')as f:json.dump(report,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in report.items() if k!='checkNames'}))
