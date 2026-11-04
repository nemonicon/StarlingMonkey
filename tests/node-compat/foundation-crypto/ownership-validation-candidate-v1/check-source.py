#!/usr/bin/env python3
"""Read-only SOURCE/data checks, not a crypto, admission or packaging action."""
import base64,hashlib,json,re,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
REPO=BASE.parents[2]
checks=[]
def yes(name,value):
    if not value:raise AssertionError(name)
    checks.append({'name':name,'passed':True})
def sha(raw):return hashlib.sha256(raw).hexdigest()
def source(path):return Path(path).read_text()
def index(path,digest):
    p=Path(path);raw=p.read_bytes();yes('exact index '+str(p),sha(raw)==digest)
    v=json.loads(raw)
    for row in v['files']:
        b=(p.parent/row['path']).read_bytes();yes('unchanged indexed source '+row['path'],len(b)==row['bytes'] and sha(b)==row['sha256'])
    return v
def main():
    producer=BASE/'native-integration-candidate-v2'
    parent=index(producer/'index.json','68b6f2a50174adbf30d8257f8107dd6c5b38beddf0db4b95ad972e3f47e25575')
    policy=json.loads((producer/'policy.json').read_bytes());contract=json.loads((HERE/'integration-contract.json').read_bytes());vector=json.loads((HERE/'vector.json').read_bytes())
    yes('actual355 not a projected old350 lineage',len(policy['expectedNativeSourceManifest'])==355 and policy['cryptoKeyOwnershipSourcePolicy']['unchangedParentFiles']==350)
    changes=policy['cryptoKeyOwnershipSourcePolicy']['changes'];yes('exact five owner/guard sources',len(changes)==5)
    for r in changes:
        raw=Path(r['afterimage']).read_bytes();yes('actual owner/guard bytes '+r['path'],len(raw)==r['bytes'] and sha(raw)==r['afterSha256'])
        yes('changed row is in exact full355 source policy '+r['path'],{'path':r['path'],'sha256':r['afterSha256']} in policy['expectedNativeSourceManifest'])
    guarded=BASE/'prototype-key-guard-candidate-v1/afterimages/builtins/web/crypto'
    subtle=source(guarded/'subtle-crypto.cpp')
    for name in ['sign','verify']:
        start=subtle.index('bool SubtleCrypto::'+name+'(');body=subtle[start:subtle.find('\n}',start)+2]
        yes('new '+name+' prototype guard precedes conversions',body.index('&key_arg.toObject() == CryptoKey::proto_obj.get()')<body.index('validate_crypto_buffer_source(')<body.index('CryptoAlgorithmSignVerify::normalize('))
    cpp=source(guarded/'crypto-key.cpp');header=source(guarded/'crypto-key.h');algorithm=source(guarded/'crypto-algorithm.cpp')
    yes('native owner and foreground policy explicit','JSCLASS_FOREGROUND_FINALIZE' in header and 'SecretByteVectorPtr data' in cpp)
    yes('CryptoKey preserves actual direct global class installation','return BuiltinImpl<CryptoKey, CryptoKeyClassPolicy>::init_class_impl(cx, global);' in cpp)
    yes('normal HMAC source reads owned vector data','CryptoAlgorithmHMAC_Sign_Verify::sign' in algorithm and 'CryptoAlgorithmHMAC_Import::toObject' in algorithm)
    embedding=Path('/tmp/starling-node-compat/production-zlib-v4/native-freeze/componentize-source/embedding/embedding.cpp')
    emb=source(embedding);start=emb.index('export_name("call")');bridge=emb[start:]
    order=['JS_CallFunctionValue','JS::AddPromiseReactions','Runtime.engine->run_event_loop()','JS::GetPromiseState','JS::GetPromiseResult']
    positions=[bridge.index(x) for x in order];yes('actual ordinary scalar Promise/event-loop bridge source',positions==sorted(positions))
    scheduler=source(REPO/'tests/node-compat/foundation-scheduler/diagnostic-link1-driver-v2/main.fixture.mjs')
    yes('existing guest scalar async precedent','export async function run()' in scheduler)
    yes('RFC full SHA256 vector literal and exact20-byte key',vector['keyHex']=='0b'*20 and vector['messageHex']=='4869205468657265' and vector['signatureHex']=='b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7' and len(bytes.fromhex(vector['signatureHex']))==32)
    yes('JWK base64url is pure reversible data',base64.urlsafe_b64decode(vector['keyBase64url']+'=')==bytes.fromhex(vector['keyHex']))
    guest=source(HERE/'guest.UNEXECUTED.mjs');wit=source(HERE/'public-abi.wit')
    yes('same four proposed ordinary scalar exports',re.findall(r'^export (?:async )?function ([a-z]+)\(',guest,re.M)==['inspect','run','clear','validate'] and re.findall(r'export ([a-z]+): func',wit)==['inspect','run','clear','validate'])
    yes('all WIT results string and no imports','import ' not in wit and len(re.findall(r'-> string;',wit))==4)
    yes('guest has no facade/Node/provider imports',not re.search(r'^\s*(?:import|export.*from)\b',guest,re.M))
    top=guest[:guest.index('function check(')]
    yes('no operational key/crypto/async initialization',all(x not in top for x in ['crypto.subtle','await ','new Promise','new globalThis.CryptoKey','getRandomValues','randomUUID']) and 'let rawKey=null,jwkKey=null' in top)
    yes('no private GC, random, weak/finalizer instrumentation or key generation',all(x not in guest for x in ['getRandomValues(', 'randomUUID(', 'generateKey(', 'FinalizationRegistry(', 'WeakRef(', 'node:crypto', 'new Proxy(', '.gc(']))
    yes('no accidental return-number identifiers',not re.search(r'\breturn\d+\b',guest))
    yes('test cases full raw/JWK/retained and guarded-only probes',all(x in guest for x in ["importKey('raw'","importKey('jwk'","caseId===2","else result=await prototypeRefusals()","onlyNewGuardedArtifactAllowed:true"]))
    yes('full earlier tag checked after next provider call','hex(first)===firstHex' in guest and guest.index('const secondBuffer=await sign')<guest.index('hex(first)===firstHex'))
    yes('per-operation small typed returns captured before semantic signature check',guest.index("note('sign','returned',result)")<guest.index('async function prototypeRefusals') and "completed:false,error:errorRecord(error),observations" in guest)
    yes('opaque unexpected values not coerced/serialized','opaque:true,fullOpaqueValueClaim:false' in guest and 'fullBytesRetained:value.byteLength<=1024' in guest)
    yes('fresh WT bridge is same sequence with explicit no-interleaving claim','entryCounters,entryState,before,records,released,after' in guest and 'separateHostCallInterleavingProved:false' in guest)
    yes('configured/frozen native roles remain distinct',contract['nativeConfiguredSourceRoot']!=contract['frozenSourceRoot'] and contract['nativeBootstrapApi']['configuredAndFrozenContextsMustBothRemainAuthenticated'] is True)
    yes('no invented async ABI/new embedding interface',contract['scalarBridge']['witIsOrdinaryScalarNotInventedAsyncAbi'] is True and contract['scalarBridge']['newEmbeddingOrNativeApi'] is False)
    yes('packaging no imports/selected host capabilities',contract['packaging']['options']['selectedInterfaces']==[] and len(contract['packaging']['options']['disableFeatures'])==5)
    authority=json.loads((HERE/'future-authority.template.json').read_bytes())
    yes('all export/key/prototype action flags false',all(authority[k] is False for k in ['actionAllowed','prototypeKeyProbesAllowed','ordinaryKeyHmacCallsAllowed','gcAllowed','cryptoAtSnapshotAllowed','operationalAdmission']))
    yes('all actual proof slots remain null',all(v is None for v in contract['currentPositiveProofs'].values()))
    return {'schemaVersion':1,'state':'STATIC_SOURCE_AND_LITERAL_DATA_CHECKS_PASSED','passed':True,'checks':len(checks),'details':checks,'nativeProducerIndexedFiles':len(parent['files']),'guestOrCryptoOrNodeOracleOrBootstrapOrOwnerActionExecuted':False,'witParserOrActualAbiExecuted':False}
if __name__=='__main__':
    result=main();p=Path(sys.argv[1]);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({k:v for k,v in result.items() if k!='details'}))
