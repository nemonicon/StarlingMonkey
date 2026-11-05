"""Independent Source/Data models. Never imports/runs owner code or codecs."""
from pathlib import Path
from collections import Counter
import ast,copy,hashlib,json,re
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'node-error-semantics-candidate-v1'
EXPECTED='7d620e00e55a0abcbb84fcaa415f406edf436320583c740ac888de3218b9edb5'
seen={};checks=0


def need(value,message='check'):
    global checks
    checks+=1
    assert value,message


def file(path,sha=None,size=None,force=False):
    p=Path(path);need(p.is_absolute()and p.is_file()and not p.is_symlink(),str(p));a=p.stat();identity=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns);real=str(p.resolve())
    if str(p)not in seen or force:
        h=hashlib.sha256()
        with p.open('rb')as stream:
            for block in iter(lambda:stream.read(4*1024*1024),b''):h.update(block)
        z=p.stat();need(identity(a)==identity(z)and real==str(p.resolve()));row=dict(path=str(p),sha256=h.hexdigest(),bytes=z.st_size)
        if str(p)in seen:need(seen[str(p)]==(row,identity(z),real))
        seen[str(p)]=(row,identity(z),real)
    row,old,resolved=seen[str(p)];need(identity(a)==old and real==resolved)
    if sha is not None:need(row['sha256']==sha,str(p))
    if size is not None:need(row['bytes']==size,str(p))
    return row


def verify(row,force=False):return file(row['path'],row['sha256'],row['bytes'],force)
def read(row):verify(row);return json.loads(Path(row['path']).read_bytes())
def load(path):file(path);return json.loads(Path(path).read_bytes())
def text(path):file(path);return Path(path).read_text()
def write(name,value):(HERE/name).write_text(json.dumps(value,indent=2)+'\n')


def family(index):
    value=read(index);root=Path(index['path']).parent;names={'index.json'};rows=[index]
    for r in value['files']:
        name=r['path'];need(name not in names and not name.startswith('/')and all(x not in['','.','..']for x in name.split('/')));names.add(name);actual=dict(r,path=str(root/name));verify(actual);rows.append(actual)
    need({str(p.relative_to(root))for p in root.rglob('*')if p.is_file()}==names and not any(p.is_symlink()for p in root.rglob('*')))
    return rows


def schema(value,s,root):
    if '$ref'in s:
        need(s['$ref'].startswith('#/'));target=root
        for key in s['$ref'][2:].split('/'):target=target[key.replace('~1','/').replace('~0','~')]
        schema(value,target,root)
    if 'const'in s:need(value==s['const'])
    if 'enum'in s:need(value in s['enum'])
    if 'type'in s:
        kinds=dict(object=dict,array=list,string=str,integer=int,number=(int,float),boolean=bool);need(type(value)is kinds[s['type']]if s['type']!='number'else type(value)in kinds['number'])
    if type(value)is dict:
        for k in s.get('required',[]):need(k in value)
        for k,v in value.items():
            if 'propertyNames'in s:schema(k,s['propertyNames'],root)
            if k in s.get('properties',{}):schema(v,s['properties'][k],root)
            elif s.get('additionalProperties')is False:need(False,'unknown manifest key '+k)
            elif type(s.get('additionalProperties'))is dict:schema(v,s['additionalProperties'],root)
    if type(value)is list:
        if 'minItems'in s:need(len(value)>=s['minItems'])
        if s.get('uniqueItems'):need(len(value)==len(set(value)))
        for v in value:
            if 'items'in s:schema(v,s['items'],root)
    if type(value)is str:
        if 'pattern'in s:need(re.search(s['pattern'],value)is not None)
        if 'minLength'in s:need(len(value)>=s['minLength'])
    if type(value)in[int,float]:
        if 'minimum'in s:need(value>=s['minimum'])
        if 'maximum'in s:need(value<=s['maximum'])


def apply_patch_model(source,patch,reverse=False):
    old=source.splitlines(keepends=True);lines=patch.splitlines(keepends=True);out=[];cursor=0;i=0
    while i<len(lines):
        match=re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@',lines[i])
        if not match:i+=1;continue
        start=int(match[3]if reverse else match[1])-1;need(start>=cursor);out.extend(old[cursor:start]);cursor=start;i+=1
        while i<len(lines)and not lines[i].startswith('@@'):
            line=lines[i];i+=1
            if line.startswith(('---','+++')):continue
            sign=line[:1];value=line[1:]
            if reverse:sign={'+':'-','-':'+',' ':' '}.get(sign,sign)
            need(sign in[' ','+','-'])
            if sign in[' ','-']:need(old[cursor]==value);cursor+=1
            if sign in[' ','+']:out.append(value)
    return ''.join(out+old[cursor:])


def main():
    need(not(HERE/'index.json').exists());index=file(SOURCE/'index.json',EXPECTED,6366);rows=family(index);need(len(rows)==38)
    declared=load(SOURCE/'input-freeze.json');need(len(declared['files'])==902 and len({r['path']for r in declared['files']})==902)
    for row in declared['files']:verify(row)
    refs=load(SOURCE/'references.json')['roles']
    for row in refs.values():verify(row)
    historical_rows=family(refs['historicalNormalResultIndex']);need(refs['historicalDifferenceLedger']in historical_rows and refs['historicalConstantLedger']in historical_rows)
    historical_result=load(Path(refs['historicalNormalResultIndex']['path']).parent/'results.json');need(historical_result['state']=='INDEPENDENT_ZLIB350_NORMAL_CODEC_V2_BOUNDED_RESULTS_PASSED'and historical_result['operationalAdmission']is historical_result['runtimeAcceptanceClaim']is False)
    deriv=load(SOURCE/'derivations.json');need((deriv['nativeSourceCount'],deriv['changedSourceCount'],deriv['unchangedSourceCount'])==(350,3,347))
    patch=text(SOURCE/'node-error-semantics.UNAPPLIED.patch');patches={part.splitlines()[0][6:]:part for part in re.split(r'(?m)(?=^--- a/)',patch)if part.startswith('--- a/')};need(len(patches)==3)
    for record in deriv['records']:
        verify(record['before']);verify(record['after']);a=text(record['before']['path']);b=text(record['after']['path'])
        need(apply_patch_model(a,patches[record['path']])==b and apply_patch_model(b,patches[record['path']],True)==a)
        if record['edits']:
            forward=a
            for edit in record['edits']:need(forward.count(edit['before'])==edit.get('occurrences',1));forward=forward.replace(edit['before'],edit['after'])
            need(forward==b)
            backward=b
            for edit in reversed(record['edits']):need(backward.count(edit['after'])==edit.get('occurrences',1));backward=backward.replace(edit['after'],edit['before'])
            need(backward==a)
        elif record['path'].endswith('.json'):
            old,new=json.loads(a),json.loads(b);value=copy.deepcopy(new);value['status']=old['status'];value['modules']['node:zlib']['deviations']=old['modules']['node:zlib']['deviations'];need(value==old)
        else:need(a.splitlines(keepends=True)[0]==b.splitlines(keepends=True)[0]and a.splitlines(keepends=True)[2:]==b.splitlines(keepends=True)[2:])
    base=Path(deriv['records'][0]['before']['path']).parents[3];policy=read(refs['source350Policy']);need(len(policy['expectedNativeSourceManifest'])==350)
    receipt=read(refs['actualNormalFreezeReceipt']);frozen=Path(refs['actualNormalFreezeReceipt']['path']).parent;changed={r['path']for r in deriv['records']}
    for row in policy['expectedNativeSourceManifest']:
        file(base/row['path'],row['sha256']);file(frozen/'source'/row['path'],row['sha256'])
    need(len(changed)==3 and len([r for r in policy['expectedNativeSourceManifest']if r['path']not in changed])==347)
    kernel=text(deriv['records'][0]['after']['path']);before=text(deriv['records'][0]['before']['path']);bounded=text(base/'builtins/node-compat/zlib/bounded-codec.h');facade=text(base/'builtins/node-compat/zlib/facade.mjs');constants=text(base/'builtins/node-compat/zlib/constant-data.generated.mjs');generator=text(base/'builtins/node-compat/zlib/generate-factory.mjs')
    need(kernel[kernel.index('// Private factory contract only:'):]==before[before.index('// Private factory contract only:'):])
    formats=re.findall(r'DEF_ERR\((\w+), (JSEXN_\w+), "([^"]+)", (\d+)\)',kernel);need(len(formats)==11 and all(n=='0'for _,_,_,n in formats))
    need('std::optional<int> codec_errno = std::nullopt'in kernel and 'if (codec_errno)'in kernel and 'JS::Int32Value(*codec_errno)'in kernel and 'result.zlib_status'not in kernel)
    fail=kernel[kernel.index('static bool fail('):kernel.index('static bool verify_backend')]
    need(fail.index('JS::RootedValue exception(cx)')<fail.index('JS_GetPendingException')<fail.index('JS_ClearPendingException')<fail.index('JS::RootedObject error')<fail.index('string_property')<fail.index('JS_SetPendingException'))
    need('if (!JS_GetPendingException(cx, &exception)) return false;'in fail and 'if (!JS_DefineProperty(cx, error, "errno", number, JSPROP_ENUMERATE)) return false;'in fail)
    call_args=re.findall(r'fail\(cx, (\w+), "([A-Z0-9_]+)"(?:, ([A-Z0-9_]+))?\)',kernel);need(len(call_args)==16 and sum(bool(v)for _,_,v in call_args)==3)
    need({v for _,_,v in call_args if v}=={'Z_DATA_ERROR','Z_BUF_ERROR','Z_NEED_DICT'})
    helper=text(base/'runtime/builtin.cpp');decl=text(base/'include/errors.h');builtin=text(base/'include/builtin.h');cmake=text(base/'cmake/builtins.cmake');flags=text(base/'cmake/compile-flags.cmake');register=text(base/'builtins/node-compat/register.cpp')
    need('JS_ReportErrorNumberUTF8Array'in helper and 'const char* arg1 = nullptr'in decl and 'JSErrorFormatString name = {#name, format, count, exception}'in builtin)
    need('set(CMAKE_CXX_STANDARD 23)'in flags and 'target_sources(builtin_node_compat PRIVATE builtins/node-compat/zlib/kernel.cpp)'in cmake and '#include "zlib/factories.generated.h"'in register and 'zlib_profile::create_kernel(cx)'in register)
    sdk=Path('/private/tmp/starling-node-compat/zlib-v4-build/spidermonkey-dist-release/include')
    for name in['js/Exception.h','js/RootingAPI.h','js/PropertyAndElement.h','zlib.h']:text(sdk/name)
    zheader=text(sdk/'zlib.h');numbers={name:int(re.search(r'(?m)^#define '+name+r'\s+\(?(-?\d+)\)?\s*$',zheader).group(1))for name in['Z_DATA_ERROR','Z_BUF_ERROR','Z_NEED_DICT']};need(numbers==dict(Z_DATA_ERROR=-3,Z_BUF_ERROR=-5,Z_NEED_DICT=2))
    need('JS_GetPendingException'in text(sdk/'js/Exception.h')and 'JS_SetPendingException'in text(sdk/'js/Exception.h')and 'JS_DefineProperty'in text(sdk/'js/PropertyAndElement.h'))
    switch=kernel[kernel.index('static bool codec_failure'):kernel.index('// Private factory contract only:')];policies={}
    status_map=dict(DictionaryRequired='NeedsDictionary',InternalError='InternalFailure',Ok='InternalFailure')
    for kind,code,errno in re.findall(r'return fail\(cx, (\w+), "([A-Z0-9_]+)"(?:, ([A-Z0-9_]+))?\);',switch):policies[kind]=dict(code=code,errno=numbers[errno]if errno else None)
    need(len(policies)==7 and 'case codec::Status::OutOfMemory:\n    JS_ReportOutOfMemory(cx);\n    return false;'in switch)
    status_cases=[]
    for kind,p in policies.items():
        for sentinel in[-6,-5,-4,-3,-2,-1,0,1,2]:
            out=dict(name='RangeError'if kind in['InputLimit','OutputLimit']else'Error',code=p['code'])
            if p['errno']is not None:out['errno']=p['errno']
            need(('errno'in out)==(kind in['InvalidData','IncompleteData','NeedsDictionary'])and out.get('errno')not in[0,1]);status_cases.append(dict(kind=kind,lastDiagnostic=sentinel,error=out,cppExecuted=False))
    contract=load(SOURCE/'error-contract.proposal.json')
    for row in contract['codecErrors']+contract['profileErrors']:
        kind=status_map.get(row['status'],row['status']);need(policies[kind]==dict(code=row['code'],errno=row['ownErrno']))
    old_manifest=Path(deriv['records'][1]['before']['path']).read_bytes();new_manifest=Path(deriv['records'][1]['after']['path']).read_bytes()
    schema_root=load(base/'builtins/node-compat/manifest.schema.json');schema(json.loads(new_manifest),schema_root,schema_root)
    dependency="import {createZlibData} from './constant-data.generated.mjs';";need(facade.count(dependency)==1)
    need("constants.replace(/^export function /gm,'function ')"in generator and "digest.update(name+'\\0'+source+'\\0')"in generator)
    def factory(manifest):
        h=hashlib.sha256()
        for name,payload in[('constant-data.generated.mjs',constants),('facade.mjs',facade),('export-manifest.zlib.node-v22.14.0.json',manifest.decode())]:h.update((name+'\0'+payload+'\0').encode())
        c=re.sub(r'^export function ','function ',constants,flags=re.M);f=re.sub(r'^export function ','function ',facade.replace(dependency,''),flags=re.M);body="(function(argument){\n'use strict';\n"+c+'\n'+f+'\nreturn createZlibModule(argument.kernel, argument.Buffer);\n})'
        return('// Generated unapplied bounded zlib proposal; do not edit.\n// Canonical-source SHA-256: '+h.hexdigest()+'\nstatic constexpr const char kZlibFactorySource[] = R"SM_NODE_PROFILE('+body+')SM_NODE_PROFILE";\n').encode()
    need(factory(old_manifest)==Path(deriv['records'][2]['before']['path']).read_bytes()and factory(new_manifest)==Path(deriv['records'][2]['after']['path']).read_bytes())
    ledger=read(refs['historicalDifferenceLedger']);oracle=read(refs['nodeOracle']);inventory=load(SOURCE/'complete-case-inventory.json');remediation=load(SOURCE/'difference-remediation.json')
    need(oracle['node']=='v22.14.0'and len(oracle['cases'])==len(inventory['cases'])==61 and [r['index']for r in inventory['cases']]==list(range(61)))
    for row in oracle['dataFiles']:verify(row)
    for a,b in zip(oracle['cases'],inventory['cases']):need(a['index']==b['index']and a['id']==b['id']and a['node']==b['node']and a['profileExpectedKind']==b['historicalProfileExpectedKind']and a['profileExpectedCode']==b['historicalProfileExpectedCode']and a['deviation']==b['historicalDeviation'])
    need(len(ledger['rows'])==len(remediation['rows'])==22 and len(ledger['allErrorComparisons'])==31)
    for a,b in zip(ledger['rows'],remediation['rows']):v=copy.deepcopy(b);del v['remediation'];need(a==v)
    predictions=[];closed=[];remaining=[];raw_count=0;paths=set()
    code_kind=dict(ERR_BUFFER_TOO_LARGE='OutputLimit',ERR_SM_ZLIB_TRAILING_DATA_UNSUPPORTED='TrailingData',ERR_SM_ZLIB_DICTIONARY_UNSUPPORTED='NeedsDictionary',Z_DATA_ERROR='InvalidData',Z_BUF_ERROR='IncompleteData')
    for row in ledger['allErrorComparisons']:
        node=oracle['cases'][row['index']]['node'];need(node==row['nodeOutcomeAndErrorAsRecorded'])
        for citation in row['citations']['guestRawObservations']:
            raw=load(citation['path']);need(raw['index']==row['index']and raw['id']==row['id']and raw['outcome']=='error'and raw['partialOutputPublished']is False and raw['error']==row['profileErrorAsObserved']);raw_count+=1;paths.add(citation['path'])
        profile=copy.deepcopy(row['profileErrorAsObserved']);fields=profile['fields']
        if not fields['operation']['own']:
            p=policies[code_kind[fields['code']['value']]];fields['code']['value']=p['code'];fields['errno']=dict(own=p['errno']is not None,type='number'if p['errno']is not None else'undefined',value=p['errno'])
        diffs=[]
        if node['kind']!='error':diffs=['outcome']
        else:
            if node['name']!=profile['name']:diffs.append('error.name')
            for name in['code','errno']:
                if node[name]!={key:fields[name][key]for key in['type','value']}:diffs.append('error.'+name)
        if row['comparisonDifferences']and not diffs:closed.append(row['index'])
        if diffs:remaining.append(row['index'])
        predictions.append(dict(index=row['index'],id=row['id'],profileModeled=profile,predictedDifferences=diffs,runtimeVerified=False))
    need(raw_count==len(paths)==145 and sum(r['observationCount']for r in ledger['rows'])==100)
    need(closed==[7,10,24,27,41,44,51]and remaining==[12,15,16,29,32,33,46,49,50,52,53,56,58,59,60])
    need(sum(not r['comparisonDifferences']for r in ledger['allErrorComparisons'])==9)
    need(sum(r['sourceDeviationValuePreserved']is None for r in remediation['rows'])==11)
    categories=Counter(r['remediation']['classification']for r in remediation['rows']);need(categories==Counter(dict(FIXABLE_ERROR_FORM=6,OUTPUT_CAP=3,STRICT_MEMBER_OR_TRAILING=6,FIXABLE_CODEC_ERROR_CODE=1,INPUT_CAP=2,FRACTIONAL_OPTION=1,OPTION_ABOVE_PROFILE_CAP=1,UNSUPPORTED_LEVEL_OPTION=1,BYTE_ONLY_INPUT=1)))
    owner_model=load(SOURCE/'model-evidence.json');need(len(owner_model['statusCases'])==63 and len(owner_model['predictedErrorComparisons'])==31)
    for ours,theirs in zip(predictions,owner_model['predictedErrorComparisons']):need(ours['index']==theirs['index']and ours['profileModeled']==theirs['modeledProfileError']and ours['predictedDifferences']==theirs['predictedComparedDifferences']and theirs['runtimeVerified']is False)
    node_js=text(HERE.parent/'source-freeze/node/lib/zlib.js');node_cpp=text(HERE.parent/'source-freeze/node/src/node_zlib.cc');need('genericNodeError(message, { errno, code })'in node_js and 'throw new ERR_BUFFER_TOO_LARGE(self._maxOutputLength)'in node_js and 'value: ObjectFreeze(codes)'in node_js and 'return ErrorForMessage("Missing dictionary")'in node_cpp)
    need(oracle['cases'][51]['node']['message']=='Missing dictionary')
    backend=load(SOURCE/'backend-evidence-protocol.json');need(backend['historicalRuntimeBackendProof']==dict(verified=False,version=None,vernum=None)and backend['evidenceEntryImplemented']is False and backend['actualRawRecord']is None)
    need(re.search(r'#define ZLIB_VERSION\s+"1\.3\.1"',zheader)is not None and int(re.search(r'#define ZLIB_VERNUM\s+(0x[0-9a-fA-F]+)',zheader).group(1),0)==4880)
    need('"ZLIB_VERNUM":backend.vernum'in constants and '"ZLIB_VERNUM":4865'not in constants and receipt['runtimeBackendProof']==dict(verified=False,version=None,vernum=None))
    constants_ledger=read(refs['historicalConstantLedger']);decision=read(refs['costDecision']);need(decision['operationalAdmission']is decision['sourcePromotionAllowed']is False)
    for citation in load(SOURCE/'source-evidence.json')['citations']:need(text(citation['path']).splitlines()[citation['line']-1]==citation['sourceLine']and citation['needle']in citation['sourceLine'])
    for name in['source-results.json','results.json','source-receipt.json','future-source-peer-contract.json','differential-validation-plan.json']:load(SOURCE/name)
    for label in['source-checks','final']:
        terminal=load(SOURCE/'evidence'/label/'terminal.json');need(terminal['rawExitCode']==0 and terminal['sourceDataModelsOnly']is True and terminal['ownerModulesOrActionsInvoked']is False and terminal['argv'][-1]==str(SOURCE/'check-source.py'))
        for row in terminal['streams'].values():verify(row)
        summary=read(terminal['streams']['stdout.json']);current=load(SOURCE/'source-results.json');need(terminal['streams']['stderr.log']['bytes']==0)
        if label=='final':need(summary==current)
        else:need({k:v for k,v in summary.items()if k!='checks'}=={k:v for k,v in current.items()if k!='checks'}and summary['checks']==2085 and current['checks']==2138)
    historical=load(SOURCE/'history/first-reversal-reader/evidence/terminal.json');need(historical['rawExitCode']==1)
    for name,row in historical['streams'].items():file(SOURCE/'history/first-reversal-reader/evidence'/name,row['sha256'],row['bytes'])
    asts=0
    for path in SOURCE.rglob('*.py'):ast.parse(text(path));asts+=1
    ast.parse(Path(__file__).read_text());file(Path(__file__).resolve())
    for row in[v[0]for v in seen.values()]:verify(row,True)
    write('model-review.json',dict(schemaVersion=1,statusCases=status_cases,allStatusModelCases=len(status_cases),predictions=predictions,sevenTargetRows=closed,fifteenRemainingRows=remaining,nineOriginallyMatchingErrorRows=9,nodeOwnAbsenceInferred=False,newGuestMessageObserved=False,rawErrorRecordsAuthenticated=raw_count,factoryBeforeAndAfterReproducedWithoutGenerator=True,factoryExecutableBytesPreserved=True,cppOrJsOrCodecExecuted=False))
    write('input-hashes.json',dict(schemaVersion=1,files=[v[0]for v in seen.values()],initialFinalIdentitiesAndHashesVerified=True))
    write('review-checks.json',dict(schemaVersion=1,readHashDataSourceReviewPassed=True,checks=checks,inputPaths=len(seen),candidateIndexedMembers=37,declaredInputs=902,nativeSourceFiles=350,unchangedNativeFiles=347,changedAfterimages=3,reversibleCppEdits=len(deriv['records'][0]['edits']),unappliedPatchForwardReverseFiles=3,nativeErrorFormats=11,nativeFailCallers=16,explicitCodecErrnoCallers=3,statusCases=63,completeCases=61,errorComparisons=31,historicalDifferences=22,predictedTargetRows=7,remainingDifferences=15,rawErrorRecords=145,ownerPythonAstFiles=asts,manifestSchemaDataValidated=True,ownerSourceTerminalsVerified=2,historicalReaderFailureRetained=True,historicalReaderStreamDescriptorsTreatedAsHistoricalPaths=True,generatorOrFactoryExecuted=False,cppOrSdkHelperOrNodeOrCodecOrGuestExecuted=False,realGcFaultOomExecuted=False,backendRuntimeProofEstablished=False,adoption=False,costTransferred=False))
    print(json.dumps(dict(checks=checks,inputPaths=len(seen),statusModels=len(status_cases),targeted=closed,remaining=remaining,ownerActionsInvoked=False)))


if __name__=='__main__':main()
