"""Read/hash-only Source checks. No guest/native/Next/packager invocation."""
from pathlib import Path
import hashlib,json,re
HERE=Path(__file__).resolve().parent
refs=json.loads((HERE/'references.json').read_text());checks=0
def need(value,message):
    global checks
    assert value,message;checks+=1
def checked(row):
    raw=Path(row['path']).read_bytes()
    need(len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256'],row['path'])
    return raw
parent=checked(refs['parentAdapter']).decode();edit=refs['adapterDerivation']
need(parent.count(edit['before'])==1,'One adapter seam')
adapter=parent.replace(edit['before'],edit['after'])+edit['appended']
need((HERE/'adapter-descendant.mjs').read_text()==adapter,'Exact adapter descendant')
for row in refs['nativeApis']+refs['nextOptionEvidence']+refs['standaloneCriticalInputs']:checked(row)
checked(refs['fixtureContract']);checked(refs['nativeSourceComposition'])
for row in refs['witDependencies']:
    need(checked(row['source'])==checked(row['copy']),'Whole unchanged WIT dependency')
selection=json.loads((HERE/'component-inputs.json').read_text())
expected=['wasi:cli/environment','wasi:clocks/monotonic-clock','wasi:clocks/wall-clock',
          'wasi:random/random','wasi:filesystem/types','wasi:filesystem/preopens',
          'wasi:io/error','wasi:io/poll','wasi:io/streams','wasi:http/types',
          'wasi:cli/stdout','wasi:cli/stderr','wasi:http/outgoing-handler']
imports=re.findall(r'^  import ([^;]+);$',(HERE/'profile.wit').read_text(),re.M)
need(imports==[x+'@0.2.10' for x in expected],'Exactly thirteen interfaces')
need(selection['selectedInterfaces']==imports and len(set(imports))==13,'Selection equality')
need(selection['worldName']=='next-http' and selection['worldPackage']=='starling:next-component@0.1.0','Real world identity')
need('export wasi:http/incoming-handler@0.2.10;' in (HERE/'profile.wit').read_text(),'Actual resource export')
lifecycle=(HERE/'lifecycle.mjs').read_text().replace('export function ','function ')
common=selection['rawEntryPrefix']
body=adapter.replace('export function createWasiHttpHandler','function createWasiHttpHandler')+'\n'+lifecycle+'\n'
for filename,prepare,prefix,suffix in [('guest-entry.mjs','next-prepare.mjs',common,
  '\nexport const incomingHandler=createNeutralReadyHandler({runNeutralServer,prepareServer,disposeBeforeEntry});\n'),
  ('dependency-entry.mjs','dependency-prepare.mjs',common+selection['dependencyImportPrefix'],
  '\nexport const incomingHandler=createNeutralReadyHandler({runNeutralServer,prepareServer:prepareDependencyServer,disposeBeforeEntry});\n')]:
    text=(HERE/filename).read_text()
    need(text==prefix+body+(HERE/prepare).read_text()+suffix,'Whole raw assembly: '+filename)
    need(re.findall(r'^export (?:const|function) (\w+)',text,re.M)==['incomingHandler'],'No extra ordinary exports')
    need(not re.search(r'^import .*?[\'"]\.',text,re.M),'No operational relative import')
next_source=(HERE/'next-prepare.mjs').read_text()
for needle in ["const process=bootstrap();","process.chdir('/app')","Module.createRequire('/app/server.js')", "const next=require('next')",'await app.prepare();',"const requestHandler=app.getRequestHandler()"]:
    need(needle in next_source,'Genuine API '+needle)
need(next_source.index('await app.prepare();')<next_source.index('createWasiHttpHandler('),'Preparation before resource entry')
need("fs.readFileSync('/app/.next/required-server-files.json','utf8')" in next_source,'Actual config')
need('STARLING_NEXT_ORIGIN' in next_source and 'hostname:routing.hostname,port:routing.port' in next_source,'Configured routing origin')
need('incoming.' not in next_source and 'request.headers' not in next_source,'No first-request configuration')
model=json.loads((HERE/'model-results.json').read_text());need(model['checks']==127 and model['currentNativeSemanticProof'] is False,'Host model result')
need(selection['actualEngineProof'] is None and selection['actualComponentProof'] is None and selection['actualRuntimeProof'] is None,'No self-issued actual proof')
plan=json.loads((HERE/'adapter-feature-plan.json').read_text())
for key in ('packageEntry','privateSplicer','splicerSource','witParserSource','clockOnlyPrunedAdapter','unprunedNormalizedAdapter'):checked(plan[key])
need(plan['decisions']['disableFeatures']==['fetch-event'] and plan['decisions']['enableFeatures']==[],'Retained feature policy')
need(plan['decisions']['clockOnly87777AdmittedForNext'] is False and plan['decisions']['normalized667AdmittedForNext'] is False,'No false adapter admission')
print(json.dumps({'sourceChecks':checks,'rawEntries':2,'selectedInterfaces':13,'nativeOrGuestActions':False}))
