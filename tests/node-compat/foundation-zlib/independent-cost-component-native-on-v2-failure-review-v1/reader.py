#!/usr/bin/env python3
"""Stored-data failure audit only; no JS/owner/tool/Wasm execution."""
import hashlib,json,re,stat
from pathlib import Path
HERE=Path(__file__).resolve().parent
Z=HERE.parent
O=Path('/private/tmp/starling-node-compat/zlib-cost-component-v2-native-on')
seen={}
def need(v,m):
    if not v: raise AssertionError(m)
def row(p,e=None):
    p=Path(p);s=p.lstat();need(stat.S_ISREG(s.st_mode),'ordinary final file '+str(p));h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''): h.update(b)
    r=dict(path=str(p),sha256=h.hexdigest(),bytes=s.st_size)
    if e: need(all(r[k]==e[k] for k in ('sha256','bytes')),'exact tuple '+str(p))
    seen[str(p)]=r;return r
def data(p): return json.loads(Path(p).read_text())
def nested(v):
    if isinstance(v,dict):
        if {'path','sha256','bytes'}<=v.keys(): row(v['path'],v)
        for x in v.values(): nested(x)
    elif isinstance(v,list):
        for x in v:nested(x)
def indexed(p,pin):
    need(row(p)['sha256']==pin,'pinned index');d=data(p);names=set()
    for x in d['files']:
        n=x['path'];need(not Path(n).is_absolute() and all(v not in ('','.','..') for v in n.split('/')),'safe index member');need(n not in names,'unique source member');names.add(n);row(Path(p).parent/n,x)
    return d
def write(n,d): (HERE/n).write_text(json.dumps(d,indent=2)+'\n')
def main():
    rp=Z/'cost-component-native-on-v2-failure-root-results.json';need(row(rp)['sha256']=='d6f87cbf10f77d8190043c7fafef5f63d236b9389441ab588d2355d9204b1e8b','Root receipt');r=data(rp);nested(r)
    a=data(r['authority']['path']);nested(a)
    source=Z/'cost-component-wit-amendment-v1';indexed(source/'index.json',r['sourceIndexSha256']);indexed(a['componentSourceReview']['index']['path'],r['sourceReviewIndexSha256'])
    indexed(Z/'cost-component-candidate-v1/index.json','a2fa62b3ab63a6aca044aec9a83c1ff5a09edaa208eb615226a13845bf1522f9')
    actual=set();membership=[]
    for p in sorted(O.rglob('*')):
        s=p.lstat();need(not stat.S_ISLNK(s.st_mode),'no output links')
        if stat.S_ISDIR(s.st_mode):need(stat.S_IMODE(s.st_mode)==0o700,'private directory');continue
        need(stat.S_ISREG(s.st_mode) and s.st_nlink==1,'single-link ordinary output');actual.add(p.relative_to(O).as_posix());membership.append({**row(p),'mode':oct(stat.S_IMODE(s.st_mode)),'nlink':s.st_nlink})
    need(actual=={Path(x['path']).relative_to(O).as_posix() for x in r['partialFiles']} and len(actual)==20,'exact20 partial files')
    absent=['results.json','index.json','completion.json','worker/results.json','worker/index.json','worker/completion.json','worker/generated-js-public-exports.json','worker/transpiled/package.json']
    need(all(not (O/x).exists() for x in absent),'no final validation/completion')
    parent=data(r['externalTerminal']['path']);w=data(r['ownedWorkerTerminal']['path']);nested(parent);nested(w)
    need(parent['pid']==30570 and parent['rawExitCode']==1 and not parent['timeout'],'parent1')
    need(w['pid']==30609 and w['status']==1 and w['signal'] is None and w['closed'] and w['ownedGroupGone'] and not w['terminalExitZeroObserved'],'worker1 clean terminal')
    need(w['spawnError'] is None and not w['timedOut'] and w['externalSignal'] is None and not w['outputLimitExceeded'] and not w['signals'] and not w['errors'],'no timeout/signal/collection failure')
    d=data(O/'worker-descriptor.json');row(O/'worker-descriptor.json',json.loads(w['args'][1]));need(d['rootAction']==r['authority'] and d['componentSourceIndexSha256']==r['sourceIndexSha256'],'actual source/Root descriptor')
    need(d['arm']=='native-on' and d['ordinaryGuestExportCallsAllowed'] is False and len(d['criticalFiles'])==78,'actual bounded78 critical tuples')
    for x in d['criticalFiles']:row(x['path'],x)
    for k in ['engine','metadata','adapter','code']:row(d[k]['path'],d[k])
    need(row(w['executable'])['sha256']=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0','actual Node bytes')
    opt=data(O/'worker/component-options.json');need(opt['witWorld']==(source/'public-abi.wit').read_text() and 'record: string' not in opt['witWorld'],'corrected WIT actually used')
    need(opt['selectedInterfaces']==[] and opt['disableFeatures']==['stdio','random','clocks','http','fetch-event'] and opt['env']=={} and opt['enableAot'] is False,'actual finite component options')
    ret=data(O/'worker/component-return-transport.json');need(ret['isUint8Array'] and ret['sha256']==r['component']['sha256'] and ret['bytes']==r['component']['bytes'],'actual returned component tuple')
    audit=data(r['interfaceAudit']['path']);need(audit['componentSha256']==r['component']['sha256'] and audit['emittedImports']==[] and audit['selectedInterfaces']==[],'retained selected interface audit')
    wit=Path(r['emittedWit']['path']).read_text();need(not re.search(r'\bimport\b',wit),'retained WIT imports empty')
    funcs=[]
    for name,params,ret in re.findall(r'export\s+([a-z]+):\s*func\(([^)]*)\)\s*->\s*(string);',wit):funcs.append((name,[s.split(':')[1].strip() for s in params.split(',')] if params else [],ret))
    arities=dict(identity=0,setup=1,observe=1,batch=2,checkpoint=0,stage=1,validate=1)
    need(len(funcs)==7 and {n:len(p) for n,p,_ in funcs}==arities,'retained seven scalar WIT functions')
    need(all(all(t==('string' if n in ('stage','validate') else 'u32') for t in p) for n,p,_ in funcs),'retained scalar WIT parameter types')
    meta=data(r['transpileMetadata']['path']);need(meta['imports']==[] and meta['exports']==[[n,'function'] for n in sorted(arities)] and set(meta['fileNames'])=={'codec_cost.core.wasm','codec_cost.js','codec_cost.d.ts'},'retained Jco seven-function metadata')
    dts=Path(r['generatedDts']['path']).read_text();decls=re.findall(r'^export function ([a-z]+)\(([^)]*)\): string;$',dts,re.M);need(len(decls)==7 and {n:len(p.split(',')) if p else 0 for n,p in decls}==arities,'retained d.ts seven function arities')
    glue=Path(r['generatedJs']['path']).read_text();need(len(re.findall(r'\b_util\b',glue))==1 and re.search(r'export const _util = \{\s*\}\s*$',glue),'raw terminal literal empty helper witness')
    export=re.findall(r'^\s*export \{([^}]+)\}',glue,re.M);need(len(export)==1 and [n.strip() for n in export[0].split(',') if n.strip()]==sorted(arities),'raw same-name seven function export witness')
    decl=re.findall(r'^\s*function (identity|setup|observe|batch|checkpoint|stage|validate)\(([^)]*)\)',glue,re.M);need(len(decl)==7 and {n:len(p.split(',')) if p else 0 for n,p in decl}==arities,'raw seven synchronous function declaration witness')
    component=Path(r['component']['path']).read_bytes();corepath=O/'worker/transpiled/codec_cost.core.wasm';core=corepath.read_bytes();need(component[:8]==b'\0asm\x0d\0\x01\0' and core[:8]==b'\0asm\x01\0\0\0','component/core file headers')
    need(component.count(core)==1,'retained exact core byte sequence appears once in retained component')
    err=Path(r['ownedWorkerStderr']['path']).read_text();need('Actual generated JS exposes exactly the seven declared names' in err and '/cost-component-candidate-v1/abi.mjs:35:2' in err and '/cost-component-wit-amendment-v1/build-worker.mjs:48:102' in err,'actual final static glue predicate failure stack')
    need('checkOwnedTerminal' in Path(r['externalStderr']['path']).read_text(),'parent rejects worker1')
    ws=(source/'build-worker.mjs').read_text();need(ws.index('await selected.componentize(source,options)')<ws.index('await componentWit(component)')<ws.index('await transpile(component,')<ws.index('publicJSExports(toolchain.parseAst(')<ws.index("output.write('generated-js-public-exports.json'"),'actual authenticated failure placement after retained raw artifacts')
    need('await import(' not in ws[ws.index('const glue='):],'worker does not import generated glue')
    result=dict(schemaVersion=1,state='INDEPENDENT_ACTUAL_COST_COMPONENT_V2_GLUE_FAILURE_VERIFIED',disposition='PASS_FAILURE_ATTRIBUTION_NO_COMPONENT_ACCEPTANCE',finding='COST-COMPONENT-GLUE-M2',rootReceipt=row(rp),sourceIndex=row(source/'index.json'),actualPartialFiles=20,actualCriticalTuplesRehashed=78,parentRawExitCode=1,workerRawExitCode=1,workerSignal=None,workerTimeout=False,ownedGroupGone=True,component=r['component'],core=row(corepath),generatedJs=r['generatedJs'],generatedDts=r['generatedDts'],retainedEmittedWitFunctions=7,retainedJcoMetadataFunctions=7,retainedDeclarationFunctions=7,rawJsAbiFunctionWitnesses=7,rawJsAdditionalTerminalEmptyUtilWitness=True,exactRetainedCoreByteSequenceInComponent=True,independentBinaryWitOrJcoToolRerun=False,generatedModuleImportedByReader=False,ordinaryGuestExportsInvoked=False,componentizerAndInitializationCompletedByAuthenticatedPublicMechanism=True,overallBuildAccepted=False,componentArtifactProofIssued=False,oldOutputRetryAllowed=False,sourceCorrectionRequiresFreshAuthorityOutputAndActualRun=True,operationalAdmission=False,timingAllowed=False,liveTerminalObservedByThisReader=False,reviewerOwnerToolNodeParserWasmGuestNativeOrTimingActions=False,uniqueInputsRehashed=len(seen))
    write('partial-membership.json',membership);write('rehashed-inputs.json',[seen[k] for k in sorted(seen)]);write('results.json',result);print(json.dumps({'state':result['state'],'uniqueInputs':len(seen),'partials':20}))
if __name__=='__main__':main()
