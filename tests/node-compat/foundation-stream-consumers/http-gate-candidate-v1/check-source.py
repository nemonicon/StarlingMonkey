#!/usr/bin/env python3
"""Source/data analysis only: no owner modules/helpers/oracles/actions are imported."""
from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parent;checks=[]
def need(v,m):
 if not v:raise AssertionError(m)
 checks.append(m)
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=json.loads((D/'prerequisites.json').read_bytes())
for key,row in p['references'].items():need(digest(row['path'])==row['sha256'] and Path(row['path']).stat().st_size==row['bytes'],'exact scoped reference '+key)
for item in json.loads((D/'source-citations.json').read_bytes())['files']:
 row=item['source'];b=Path(row['path']).read_bytes();need(hashlib.sha256(b).hexdigest()==row['sha256'] and len(b)==row['bytes'],'exact actual source '+row['path']);lines=b.decode().splitlines()
 for cite in item['citations']:need(cite['lines'] and all(cite['symbolOrText'] in lines[n-1] for n in cite['lines']),'actual source citation '+cite['symbolOrText'])
root=Path(p['nativeConfiguredSourceRoot']);facade=(root/'builtins/node-compat/stream-consumers/facade.mjs').read_text();body=(root/'builtins/web/fetch/request-response.cpp').read_text();handler=Path(next(v['source']['path'] for v in json.loads((D/'source-citations.json').read_bytes())['files'] if v['source']['path'].endswith('/wasmcloud/http.mjs'))).read_text()
need('for await (const chunk of stream)' in facade and 'Parse(await text(stream))' in facade,'genuine supported iterable text/json domain');need('async handle(incomingRequest, responseOutparam)' in handler and 'await runNativeChecks()' in handler and 'incomingRequest[Symbol.dispose]()' in handler,'actual WASI handler shape; no Fetch request bridge')
need('body_source_cancel_algorithm' in body and 'TODO: implement or add a comment' in body,'native cancellation source gap retained')
pins=json.loads(Path(p['references']['reviewedFourPins']['path']).read_bytes());runtime=pins['variants']['normal-runtime'];need(runtime['sourceFiles']==355 and runtime['streamConsumersEnabled'] and runtime['engineSha256']==p['actualRuntimeOnlyNativeData']['engineSha256'],'genuine actual355 RuntimeOnly data')
need(p['nativeConfiguredSourceRoot']!=p['nativeFrozenSourceRoot'] and p['componentToolRoot'] not in [p['nativeConfiguredSourceRoot'],p['nativeFrozenSourceRoot']],'three distinct contexts')
iface=json.loads((D/'expected-interface.template.json').read_bytes());need(len(iface['outerImports'])==6 and all(v.endswith('@0.2.10') for v in iface['outerImports']) and iface['clockDurationTypeOnlyRequired'],'finite six standard capability expectation');need(len(iface['oldBundleImports'])==17 and len(iface['expectedNewBundleImports'])==18,'actual17 plus explicit consumers import expectation')
need((D/'consumer-probes.template.mjs').read_bytes()==(D.parent/'release-host-plan-v1/consumer-http-probe.template.mjs').read_bytes(),'exact existing tiny request-fixture proposal')
need(json.loads((D/'future-authorities.template.json').read_bytes())['actionAllowed'] is False,'all actions closed');need(json.loads((D/'reader-adapter-contract.template.json').read_bytes())['executableAdapterProvided'] is False,'no unsupported cleanup adapter fabricated')
print(json.dumps({'schemaVersion':1,'state':'CONSUMERS355_HTTP_FOCUSED_SOURCE_ANALYSIS_PASSED','checks':len(checks),'ownerHelpersInvoked':False,'oracleInvoked':False,'guestOrHostActionsInvoked':False}))
