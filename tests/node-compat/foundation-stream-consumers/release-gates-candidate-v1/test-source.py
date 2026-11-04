"""Owned source/byte/physical checks. No owner imports or action mains."""
from pathlib import Path
import ast,hashlib,json,re
H=Path(__file__).resolve().parent;S=H/'snapshot';checks=[]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def check(name,value):assert value,name;checks.append(name)
def doc(name):return json.loads((H/name).read_bytes())
for name in ['capture-sources.py','prepare-afterimages.py','prepare-binding-hardening.py','prepare-data.py','audit-closure.py','publish.py','test-source.py','seal.py']:
 p=H/name
 if p.exists():ast.parse(p.read_text(),filename=name);checks.append('AST '+name)
proof=doc('afterimage-proof.json');origins={row['relativePath']:row for row in doc('snapshot-origins.json')['files']};current={name:(S/name).read_bytes()for name in{row['path']for row in proof['edits']}}
for row in reversed(proof['edits']):
 check('afterimage after '+row['path'],sha(current[row['path']])==row['afterSha256'])
 raw=(H/row['preimage']).read_bytes();check('afterimage preimage '+row['path'],sha(raw)==row['beforeSha256']);current[row['path']]=raw
for name,raw in current.items():check('complete reversal '+name,sha(raw)==origins[name]['sha256'])
for row in doc('lineage.json')['native355']:check('unchanged actual native355 '+row['path'],sha((S/row['path']).read_bytes())==row['sha256'])
body=doc('inherited-body-audit.json')
for row in body['unchangedCaseOracleFixtureData']:check('unchanged case/oracle '+row['path'],sha((S/row['path']).read_bytes())==row['sha256'])
graph=doc('selected-closure.json')
for row in graph['localModulesAndData']:check('physical selected module/data '+row['path'],sha((H/row['path']).read_bytes())==row['sha256'])
for edge in graph['localEdges']:check('literal edge '+edge['importer']+' '+edge['request'],((H/edge['importer']).parent/edge['request']).resolve()==(H/edge['target']).resolve()and(H/edge['target']).is_file())
check('HTTP excluded from selected scopes',not any('http' in name for name in graph['entries']))
check('full native core selected by genuine admit',"sourceAdmission=await admit(native.metadata,variant,native.sourceRoot)"in(H/'native-preflight.template.mjs').read_text())
check('unknown genuine frames refuse','assertFrame(metadata,sourceRoot,frame)'in(H/'native-preflight.template.mjs').read_text())
check('ordinary selector stays closed',sha((S/'tests/node-compat/module-selection.mjs').read_bytes())==origins['tests/node-compat/module-selection.mjs']['sha256']and'validateStreamConsumersSourceAdmission(metadata' in(S/'tests/node-compat/module-selection.mjs').read_text())
template=(H/'native-preflight.template.mjs').read_text();check('exactly two render primitives',template.count('@CONFIG_SHA@')==template.count('@INPUTS_SHA@')==1)
rendered=template.replace('@CONFIG_SHA@','a'*64).replace('@INPUTS_SHA@','b'*64)
check('render preserves template reconstruction logic',"replaceAll('@'+'CONFIG_SHA'+'@',CONFIG_SHA)"in rendered)
check('candidate preflight held','throw new Error' in(H/'native-preflight.mjs').read_text()and'await import('not in(H/'native-preflight.mjs').read_text())
authority=doc('runtime-authority.template.json');check('every future action remains NULL',all(row['approved']is None and row['output']is None and row['deadlineMs']is None for row in authority['scopes'].values())and authority['familyIndexSha256']is None)
pub=(H/'publish.py').read_text();check('publisher authenticates before output',pub.index('own()')<pub.index('output.mkdir()')and pub.index('source_review=')<pub.index('output.mkdir()'))
check('publisher imports no owner helper',not any(token in pub for token in ['importlib','subprocess','exec_file_location','exec_module','eval(','exec(']))
common=(S/'tests/node-compat/foundation-classic-streams/production-trace-regression-activated-v1/common/preflight.mjs').read_text();check('action authority precedes native gate',common.index('await assertActionContext({variant})')<common.index('await validationPreflight({variant})'))
for row in doc('payload-files.json')['files']:check('payload physical basename '+row,(H/row).is_file()and all(len(part.encode())<=255 for part in Path(row).parts))
check('six exact historical control records',len(doc('historical-controls.sealed.json')['controls'])==6)
check('four native freeze inventories present',len(doc('native-frozen-inputs.json')['rows'])==4*1164)
check('all inherited body data remain data not passes',body['sourceResultsAdopted']is False)
check('generic report writes stay in fresh output',"writeFile(join(here, 'native-component-results.json')"not in(S/'tests/node-compat/foundations/native-scalar-harness.mjs').read_text())
check('safety guards retained before manifests',(S/'tests/node-compat/foundation-stream-web/production-candidate/native-preflight.mjs').read_text().index('for(const entry of contract.nativeGuardSources)')<(S/'tests/node-compat/foundation-stream-web/production-candidate/native-preflight.mjs').read_text().index('builtinManifests=selectedManifestsForValidation'))
check('getter counterexample remains explicit','nodeCompatibilityPassed:false'in(S/'tests/node-compat/foundation-classic-streams/production-trace-regression-activated-v1/capability/focused/run-callback-return.mjs').read_text())
check('prepared reader mistakes retained',all((H/name).exists()for name in ['preparation-history/attempt1-late-selector-assumption/failure.json','preparation-history/attempt2-report-label-case/failure.json','preparation-history/attempt3-preparation-syntax.py']))
print(json.dumps({'schemaVersion':1,'state':'passed','checks':len(checks),'groups':{'afterimageEdits':len(proof['edits']),'nativeSourceFiles':355,'caseOracleFixtureFiles':len(body['unchangedCaseOracleFixtureData']),'physicalSelectedModuleAndData':len(graph['localModulesAndData']),'physicalLocalEdges':len(graph['localEdges']),'payloadFiles':len(doc('payload-files.json')['files'])},'names':checks,'ownerImports':False,'actionsExecuted':False,'nativeOrGuestExecuted':False}))
