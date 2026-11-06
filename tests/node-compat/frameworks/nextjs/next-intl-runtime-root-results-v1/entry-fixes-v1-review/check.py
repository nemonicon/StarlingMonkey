#!/usr/bin/env python3
"""Portable evidence reader. No engine, compiler, browser or server invocation."""
import base64
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import tarfile

HERE = Path(__file__).resolve().parent
SELECTED = {
    'wasi:cli/environment@0.2.10','wasi:cli/stdout@0.2.10','wasi:cli/stderr@0.2.10',
    'wasi:clocks/monotonic-clock@0.2.10','wasi:clocks/wall-clock@0.2.10',
    'wasi:random/random@0.2.10','wasi:filesystem/types@0.2.10','wasi:filesystem/preopens@0.2.10',
    'wasi:io/error@0.2.10','wasi:io/poll@0.2.10','wasi:io/streams@0.2.10',
    'wasi:http/types@0.2.10','wasi:http/outgoing-handler@0.2.10',
}


def need(value, message):
    if not value:
        raise AssertionError(message)


def digest(data, row):
    need(len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256'], 'bytes/hash: '+row['path'])


def terminal(record, raw):
    need(type(record['rawExitCode']) is int and record['rawExitCode'] == raw, 'terminal raw exit')
    for key in ('timeout','forcedCleanup'):
        need(record[key] is False,key)
    for key in ('parentOwnedGroupGone','allObservedOwnedGroupsGone'):
        need(record[key] is True,key)
    for key in ('errors','signals','interruptedSignals','remainingObservedPids'):
        need(record[key] == [],key)
    need(all(group['alive'] is False for group in record['finalGroups']), 'group remains alive')


def main():
    capsule = json.loads((HERE/'capsule.json').read_bytes())
    digest((HERE/'data.tar.gz').read_bytes(),capsule['archive'])
    rows = capsule['files']
    need(len(rows) == 282 and len({row['path'] for row in rows}) == 282,'finite membership')
    blobs, original = {}, {}
    with tarfile.open(HERE/'data.tar.gz','r:gz') as archive:
        members = archive.getmembers()
        need(sorted(member.name for member in members) == sorted(row['path'] for row in rows),'whole archive membership')
        for member in members:
            path = PurePosixPath(member.name)
            need(member.isfile() and not path.is_absolute() and '..' not in path.parts,'unsafe member')
            blobs[member.name] = archive.extractfile(member).read()
    for row in rows:
        digest(blobs[row['path']],row['original'])
        original.setdefault(row['original']['path'],[]).append(blobs[row['path']])

    def load(name):
        return json.loads(blobs[name])

    def retained(row):
        need(row['path'] in original,'missing retained record '+row['path'])
        for data in original[row['path']]:
            digest(data,row)

    def row_json(row):
        retained(row)
        return json.loads(original[row['path']][0])

    for family in capsule['sourceFamilies']:
        index = row_json(family)
        base = Path(family['path']).parent
        for row in index['files']:
            retained({**row,'path':str(base/row['path'])})
    contract = load('inputs/fixture-contract.json')
    need(len(contract['requests']) == 23,'unchanged base contract')
    summaries = []
    for pair in capsule['runs']:
        label = pair['id']; prefix=label+'/'
        result, construction = load(prefix+'runtime/result.json'), load(prefix+'constructor/result.json')
        authority = load(prefix+'runtime-authority.json')
        constructor_authority = load(prefix+'constructor-authority.json')
        client = load(prefix+'runtime/client/result.json')
        audit = load(prefix+'constructor/component-audit.json')
        for key in ('component','componentAudit','constructionResult','inputEntry','inputSourceIndex'):
            need(result[key] == pair[key] == authority[key],'Root exact runtime input '+key)
        for key in ('component','componentAudit','inputEntry','inputSourceIndex'):
            need(construction['artifacts'][key] == result[key],'construction/runtime join '+key)
        need(authority['constructionCallerIndex'] == construction['callerIndex'],'actual caller family')
        retained(authority['plan']); retained(result['sourceIndex']); retained(construction['callerIndex'])
        retained(construction['rootAuthority']); retained(result['rootAuthority'])
        need(result['passed'] is False and result['adoption'] is False and result['state']=='NEXT_WASMTIME_DEPLOYMENT_FAILED_UNACCEPTED_V2','failed outcome retained')
        need(construction['passed'] is True and construction['entryMode']=='real-next' and construction['error'] is None and construction['finalProtection']['unchanged'] is True,'successful INIT construction')
        for key in ('ordinaryExportsInvoked','httpServed','appMountedAtInit','metadataFrameProjected','productionProfilePromoted'):
            need(construction[key] is False,'constructor temporal scope '+key)
        need(constructor_authority['entryMode']=='real-next','constructor authority mode')
        terminal(load(prefix+'runtime-monitor/terminal.json'),1)
        terminal(load(prefix+'constructor-monitor/terminal.json'),0)
        for monitor in ('runtime-monitor/terminal.json','constructor-monitor/terminal.json'):
            record=load(prefix+monitor)
            for key in ('authority','stdout','stderr'):
                retained(record[key])
        need([row['label'] for row in construction['commands']] == ['componentize-init','component-validate','component-wit'],'three actual commands')
        for command in construction['commands']:
            record=row_json(command['terminal']); terminal(record,0)
            need(command['rawExitCode']==0 and command['clean'] is True,'command outcome')
            for key in ('stdout','stderr'):
                retained(command[key]); retained(record[key]); need(command[key]==record[key],'monitor stream join')
            need(command['stderr']['bytes']==0,'constructor empty stderr')
            started=load(prefix+'constructor/'+command['label']+'/started.json')
            need(started['argv']==command['argv'],'actual started argv')
        need(audit['component']==result['component'] and audit['passed'] is True and audit['allEmittedVersion']=='0.2.10' and audit['noExternalPreview1OrCustomImports'] is True,'actual audit')
        need(len(audit['emittedImports'])==13 and set(audit['emittedImports'])==SELECTED==set(result['emittedImports'])==set(result['selectedInterfaces']),'thirteen exact imports')
        need(audit['exports']==['wasi:http/incoming-handler@0.2.10'] and audit['unusedSelectedInterfaces']==[],'export closure')
        wit=blobs[prefix+'constructor/component-wit/stdout.log'].decode()
        root=wit.split('world root {',1)[1].split('}',1)[0]
        need(set(re.findall(r'^  import ([^;]+);$',root,re.M))==SELECTED,'raw emitted WIT imports')
        need(re.findall(r'^  export ([^;]+);$',root,re.M)==audit['exports'],'raw emitted WIT export')
        need('handle: func(request: incoming-request, response-out: response-outparam);' in wit,'resource-typed incoming handler')
        imports=load(prefix+'constructor/api-return/returned-imports.json')
        need({row[0] for row in imports}==SELECTED and all(len(row)==2 and all(type(item)is str for item in row) for row in imports),'whole actual import tuples')
        shape=load(prefix+'constructor/api-return/returned-own-shape.json')
        props={row['key']['string']:row for row in shape['properties']}
        need(set(props)=={'component','imports','debug'} and props['debug']['value']=={'type':'undefined'},'actual API own shape')
        component=props['component']['value']
        need(component['type']=='Uint8Array' and component['file']==result['component'] and component['sha256']==result['component']['sha256'] and component['byteLength']==result['component']['bytes'],'whole return bytes captured')
        need(client['node']=='v22.14.0' and client['origin']==result['portLease']['origin']==result['server']['readyOrigin'],'actual target origin')
        need(result['server']['command'][-1]==result['component']['path'],'actual server component argument')
        need(result['server']['exit']=={'code':0,'signal':None,'error':None} and result['server']['shutdownRequested'] is True and result['server']['sigintSent'] is True and result['server']['forcedCleanup'] is False,'planned owned server stop')
        need(result['client']['exit']=={'code':1,'signal':None,'error':None},'client failure retained')
        need(result['originalInputsPreserved'] is True and result['readonlyAppPreserved'] is True,'Source-coupled final guards')
        need(result['applicationCopy']=={'files':2218,'bytes':48808299,'byteIdentical':True,'independentInodes':True},'application copy provenance')
        for owner in ('server','client'):
            for key in ('stdout','stderr'):
                retained(result[owner][key])
        retained(result['client']['result'])
        need(client['passed'] is False and client['transportErrors']==[],'client failure/no transport exceptions')
        need([row['id'] for row in client['http'][:23]]==[row['id'] for row in contract['requests']],'full unchanged base request order')
        bodies={}
        for index,row in enumerate(client['http']):
            body=blobs[prefix+'runtime/client/responses/'+row['id']+'.txt']
            need(len(body)==row['bodyBytes'] and hashlib.sha256(body).hexdigest()==row['bodySha256'],'raw HTTP body')
            text=body.decode(); bodies[row['id']]=text
            if index==23:
                need(row['id']=='server-action-submit' and row['passed']==(row['status']==303 and row['headers'].get('location')=='/action-result?value=fixture-action'),'actual server action')
                continue
            item=contract['requests'][index]; failures=[]
            if row['status']!=item['status']: failures.append('status '+str(row['status'])+' != '+str(item['status']))
            for value in item.get('includes',[]):
                if value not in text: failures.append('missing '+json.dumps(value,separators=(',',':')))
            if item.get('location') and row['headers'].get('location')!=item['location']: failures.append('location mismatch')
            if item.get('json'):
                try:
                    parsed=json.loads(text)
                    for key,value in item['json'].items():
                        if parsed.get(key)!=value:failures.append('JSON '+key+' mismatch')
                except (ValueError,AttributeError):
                    need(row['passed'] is False and row['failures'],'invalid JSON refusal')
                    failures.append('invalid JSON')
            for key,value in item.get('responseHeaders',{}).items():
                if row['headers'].get(key)!=value:failures.append('header '+key+' mismatch')
            for key,values in item.get('responseHeaderIncludes',{}).items():
                for value in values:
                    if value not in row['headers'].get(key,''): failures.append('header '+key+' missing '+value)
            if item.get('equalJsonTo') and text!=bodies[item['equalJsonTo']]:failures.append('body differs from '+item['equalJsonTo'])
            need(row['passed']==(len(failures)==0),'independent HTTP semantics '+row['id'])
        need(len(client['http'])==(23 if label=='entry-v1' else 24),'actual HTTP count')
        if label=='entry-v1':
            need(all(row['status']==500 and row['passed'] is False for row in client['http']),'historical all 500')
            need(len(client['errors'])==1 and ':42:10' in client['errors'][0]['stack'],'historical action-ID derivation stop')
            need(all(key not in client for key in ('cacheInvalidation','streaming','browser')),'later stages never reached')
            need('CallSite.getEvalOrigin is outside' in blobs[prefix+'runtime/wasmtime.stderr.log'].decode(),'historical genuine eval refusal')
            outcome={'httpPassed':0,'httpObserved':23,'actionPostReached':False,'cacheReached':False,'strictStreamingReached':False,'browserReached':False}
        else:
            need([(row['id'],row['status']) for row in client['http'] if not row['passed']]==[('json-post',400),('public-asset',500)],'two measured blockers')
            before=json.loads(bodies['cache-first']); after=json.loads(bodies['cache-after-revalidate'])
            need(client['cacheInvalidation']=={'before':before,'after':after,'passed':True} and before['generation']==1 and after['generation']==2,'actual cache generations')
            chunks=load(prefix+'runtime/client/stream-chunks.json'); text=''; shell=ready=-1
            for i,chunk in enumerate(chunks):
                data=base64.b64decode(chunk['base64'],validate=True); need(len(data)==chunk['bytes'],'raw chunk size'); text+=data.decode()
                if shell<0 and 'NEXT_STREAM_SHELL' in text:shell=i
                if ready<0 and 'NEXT_STREAM_READY' in text:ready=i
            need(client['streaming']=={'chunks':5,'shellChunk':0,'readyChunk':2,'complete':True,'incrementalDeliveryObserved':True} and len(chunks)==5 and shell==0 and ready==2,'actual strict stream')
            browser=load(prefix+'runtime/client/browser/result.json')
            need(browser==client['browser'] and browser['origin']==client['origin'],'whole browser return')
            need([(test['id'],test['passed'],test['timedOut']) for test in browser['tests']]==[('client-counter',False,True),('server-action',True,False)],'separate browser functional outcomes')
            need({key:len(browser[key]) for key in ('pageerrors','consoleerrors','failedrequests','errors','trace','responseFinishedObservations')}=={'pageerrors':0,'consoleerrors':12,'failedrequests':12,'errors':12,'trace':97,'responseFinishedObservations':4},'whole browser errors/trace')
            need(all(browser[key] is False for key in ('functionalPassed','browserErrorFree','passed','wasmBrowserRun')),'original browser flags retained')
            need(len(browser['actionPosts'])==1 and base64.b64decode(browser['actionPosts'][0]['bodyBase64'],validate=True).find(b'browser-action')>=0,'actual browser action POST')
            retained(browser['tests'][1]['screenshot'])
            need('node:async_hooks.AsyncResource is deferred' in blobs[prefix+'runtime/wasmtime.stderr.log'].decode(),'actual guest failure retained')
            need(client['errors']==[] and client['browserExit']=={'code':1,'signal':None},'browser phase exit')
            outcome={'httpPassed':22,'httpObserved':24,'actionPostReached':True,'actionPostPassed':True,'cachePassed':True,'cacheGeneration':[1,2],'strictStreamingPassed':True,'streamChunks':5,'browserReached':True,'browserFunctionalPassed':1,'browserFunctionalTotal':2,'browserOverallPassed':False,'browserConsoleErrors':12,'browserFailedRequests':12,'browserCollectorErrors':12}
        summaries.append({'run':label,'component':result['component'],'constructionResult':pair['constructionResult'],'runtimeResult':pair['runtimeResult'],'constructionCommandsRaw0':3,'constructionRootRaw0':True,'runtimeRootRawExitCode':1,'outcome':outcome,'fullNextAccepted':False})
    # Source assembly: exact V1 inline copies, followed by the finite V2 removal.
    parent=blobs['inputs/parent-entry.mjs'].decode()
    v1=blobs['sources/next-component-entry-fixes-v1/guest-entry.mjs'].decode()
    composition=load('sources/next-component-entry-fixes-v1/composition.json')
    blocks='// Pure bounded profile installs; application loading remains deployed-only.\n'
    for facade in composition['facades']:
        source=blobs['sources/next-component-entry-fixes-v1/'+facade['copy']].decode()
        need(source.count('export function ')==2,'finite inlining export count')
        blocks+='{\n'+source.replace('export function ','function ')+'\n'+'\n'.join(facade['calls'])+'\n}\n'
    expected=parent.replace('// UNCOMPILED raw ESM entry. INIT installs only the pure Node global alias.','// Experimental raw ESM entry. INIT installs the bounded guest profile facades.',1)
    expected=expected.replace("import Module from 'node:module';","import {Buffer as __nextBuffer} from 'node:buffer';\nimport {addAbortListener as __nextAbortListener} from 'node:events';\nimport * as __nextWebStreams from 'node:stream/web';\nimport Module from 'node:module';",1)
    expected=expected.replace('installNodeGlobalAlias(globalThis);\n','installNodeGlobalAlias(globalThis);\n'+blocks+'\n',1)
    need(expected==v1,'exact V1 entry assembly')
    start=v1.index('function installNonAsciiCompileFallback(')
    end=v1.index('installNonAsciiCompileFallback(Module);',start)+len('installNonAsciiCompileFallback(Module);')
    corrected=v1[:start]+"const originalFromLength=Object.getOwnPropertyDescriptor(__nextBuffer.from,'length');\ninstallCrossPrototypeBufferFrom(__nextBuffer);\nObject.defineProperty(__nextBuffer.from,'length',originalFromLength);"+v1[end:]
    need(corrected==blobs['sources/next-component-entry-fixes-v2/guest-entry.mjs'].decode(),'exact V2 removal/arity preservation')
    return {'schemaVersion':1,'state':'ACTUAL_NEXT_ENTRY_FIXES_RUNTIME_FAILURES_DATA_REVIEW_PASSED_V1','verifiedEvidence':True,'retainedFiles':len(rows),'runs':summaries,'currentApplicationReadbacks':capsule['currentApplicationReadbacks'],'sourceAuthorRelationship':'Reviewer authored ALS, pipeTo facade and constructor/limited-build tooling; actual DATA readback is separate from Source authoring.','applicationOrHostModifiedByReviewer':False,'targetsRerunByReviewer':False,'allStagesOrFullNextPassed':False,'browserGenericWasmBrowserRunFalsePreserved':True,'actualWasmtimeTargetEstablishedByParentCommandComponentOriginAndOwnedTerminal':True,'originalProtectionScope':'Source-coupled operation-time guards plus separate current copied-source/application reads, not an all-time filesystem/process attestation','binaryPayloadsRemainExternal':True}


if __name__ == '__main__':
    print(json.dumps(main(),indent=2))
