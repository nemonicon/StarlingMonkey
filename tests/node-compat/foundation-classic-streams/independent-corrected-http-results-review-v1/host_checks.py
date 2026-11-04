"""Independent persisted-JSON checks mirroring sealed HTTP assertions; no I/O."""
import re

def equal(actual,expected):
    if isinstance(expected,bool) or expected is None or isinstance(expected,str):
        assert type(actual)is type(expected) and actual==expected
    elif isinstance(expected,(int,float)):
        assert type(actual)in[int,float] and actual==expected
    elif isinstance(expected,list):
        assert isinstance(actual,list) and len(actual)==len(expected)
        for a,b in zip(actual,expected):equal(a,b)
    elif isinstance(expected,dict):
        assert isinstance(actual,dict) and set(actual)==set(expected)
        for key,value in expected.items():equal(actual[key],value)
    else:raise AssertionError(type(expected))

def properties(actual,expected):
    for key,value in expected.items():equal(actual[key],value)

def no_failure(value):assert 'failure'not in value

def protected(report,expected,calls):
    no_failure(report);equal(report['calls'],calls)
    equal(expected['counts'],{'public':16,'nested':4,'receivers':9,'total':29})
    for key,size in [('publicCases',16),('nestedOnceCases',4),('receiverCases',9)]:
        assert len(report[key])==size;equal(report[key],expected[key])
    equal(report['namespace'],{'names':expected['names'],'defaultNamed':True,'canonicalCached':True,'aliasValues':True,'defaultAlias':True,'then':'undefined','errorMonitorType':'symbol','captureRejectionSymbol':True,'defaultMaxListeners':10,'captureRejections':False,'usingDomains':False})
    equal(report['commonJS'],{'same':True,'constructorAlias':True,'defaultProperty':'undefined','addAbortListenerType':'function','errorMonitorType':'symbol','rejectedCall':'ERR_SM_NODE_UNSUPPORTED','rejectedConstruction':'ERR_SM_NODE_UNSUPPORTED'})
    properties(report['profileErrors'],{'hooks':0,'ambient':0})
    errors=report['profileErrors']['errors'];equal([e['name']for e in errors],['once-call','once-new','on-call','on-new','async-resource-call','async-resource-new','invalid-signal'])
    for e in errors:
        invalid=e['name']=='invalid-signal'
        operation='once'if e['name'].startswith('once')else'on'if e['name'].startswith('on-')else'EventEmitterAsyncResource'if e['name'].startswith('async-resource')else'addAbortListener'
        properties(e,{'profile':expected['profileVersion'],'module':'node:events','own':True,'type':'TypeError'if invalid else'Error','operation':operation,'code':'ERR_INVALID_ARG_TYPE'if invalid else'ERR_SM_NODE_UNSUPPORTED'})
    equal(report['snapshot'],{'before':0 if calls==1 else 1,'after':1,'signalThis':True,'currentTarget':True,'aborted':False})
    equal(report['symbol']['descriptor'],expected['nodeSymbol']['descriptor'])
    assert isinstance(report['symbol']['description'],str)
    assert report['symbol']['registryKey']is None or isinstance(report['symbol']['registryKey'],str)
    assert type(report['symbol']['sameAsNodeRegistry'])is bool

def stream_web(report,expected,calls):
    no_failure(report);properties(report,{'passed':True,'calls':calls,'names':expected['names'],'constructors':41,'codecs':250,'cancellations':4,'guards':24,'views':12,'controllers':6,'iterations':67,'data':26,'guardDeviations':['min-two','proxy-genuine-receiver','shadowed-view-fields'],'dataDeviations':['released-reader-rejects-before-transfer'],'ownErrors':{'checks':9,'inheritedGets':0,'inheritedSets':0},'aliases':2,'commonJS':True,'snapshotResumption':True,'identities':{'globalNativeConstructors':10,'hiddenNativeConstructors':3,'uninstalledGlobalCodecs':True,'signalMissing':True},'fixtureRegistryUsed':False,'applicationFactoryUsed':False})
    assert len(report['policies']['checks'])==14 and len(report['dataPolicies']['checks'])==6
    for key in['codecIntrinsics','iterationIntrinsics','dataIntrinsics']:equal(report[key]['replacementInvocations'],0)

def foundations(report,expected,calls,events_oracle):
    properties(report,{'schema':5,'calls':calls})
    aliases=report['aliases'];properties(aliases,{'phase':'deployed','firstDeployedCall':calls==1,'canonicalStaticLoaded':True,'computedBareImports':True,'rejectedCall':'ERR_SM_NODE_UNSUPPORTED','rejectedConstruction':'ERR_SM_NODE_UNSUPPORTED','typedConstants':{'pathSep':'string','eventErrorMonitor':'symbol','captureRejections':'boolean','defaultMaxListeners':'number'}})
    equal([x['id']for x in aliases['aliases']],expected['dynamicBareAliases'])
    defaults=['object','object','object','object','object','function','object','function','function','object','object','object','object','object']
    assert len(defaults)==len(aliases['aliases'])
    for row,kind in zip(aliases['aliases'],defaults):
        properties(row,{'namespaceType':'object','defaultType':kind,'cache':True,'exportValues':True,'defaultIdentity':True,'thenType':'undefined'})
        assert type(row['exportCount'])is int and row['exportCount']>0
    equal(aliases['newDeferred'],[{'operation':name,'code':'ERR_SM_NODE_UNSUPPORTED'}for name in['string_decoder.encoding','assert.deepStrictEqual','assert.CallTracker','querystring.unescapeBuffer.nonstring','util.inspect','util/types.isProxy','sys.callbackify','stream/web.CompressionStream','stream/web.DecompressionStream']])
    path=report['path'];properties(path,{'calls':calls,'invalid':12,'snapshotPure':True,'identities':True,'mutableDefaults':True,'noEntropy':True})
    for key in['lexical','globs','budgets','acceptedAdversarial']:equal(path[key],expected['path'][key])
    events=report['events'];no_failure(events)
    properties(events,{'calls':calls,'snapshotTicks':calls+1,'namespaceIdentity':True,'cases':events_oracle['cases'],'nativeCases':events_oracle['nativeCases'],'profile':expected['events']['profile'],'commonJS':{'same':True,'constructorAlias':True,'defaultProperty':'undefined','errorMonitorType':'symbol','rejectedCall':'ERR_SM_NODE_UNSUPPORTED','rejectedConstruction':'ERR_SM_NODE_UNSUPPORTED'}})
    decoder=report['stringDecoder'];no_failure(decoder)
    properties(decoder,{'calls':calls,'mutationChecks':2,'detachedInternalStateChecks':5,'primordialReplacementCalls':0,'nativeAliases':2,'commonJS':True,'snapshotResumption':True,'identities':True,'noGlobalPollution':True,'passed':True})
    for key in['sequences','writes','genericCases','preservedOrderingDeviations']:equal(decoder[key],expected['stringDecoder'][key])
    assert decoder['shared']in['unavailable in guest','explicitly rejected by private candidate']
    assertion=report['assert'];no_failure(assertion)
    properties(assertion,{'calls':calls,'snapshotCount':calls,'snapshotIdentity':True,'namespaceIdentity':True,'cases':expected['assert']['cases'],'profile':expected['assert']['profile'],'aliases':{'names':expected['assert']['cases'][0]['result'],'strictNames':expected['assert']['cases'][0]['result'],'canonicalNamespaceStable':True,'bareCache':True,'rootValues':True,'strictValues':True,'moduleTag':'[object Module]','nullNamespacePrototype':True,'thenType':'undefined','sharedMutation':True},'commonJS':{'rootType':'function','strictType':'function','same':True,'strictGraph':True,'aliasOverrides':True,'defaultProperty':'undefined','rejectedCall':'ERR_SM_NODE_UNSUPPORTED','rejectedConstruction':'ERR_SM_NODE_UNSUPPORTED'}})
    qs=report['querystring'];no_failure(qs)
    properties(qs,{'calls':calls,'snapshotByte':65+calls,'snapshotValues':2+calls,'snapshotIdentity':True,'namespaceIdentity':True,'cases':expected['querystring']['cases'],'profile':expected['querystring']['profile'],'aliases':{'names':expected['querystring']['cases'][0]['result']['names'],'canonicalNamespaceStable':True,'bareCache':True,'sharedValues':True,'moduleTag':'[object Module]','nullNamespacePrototype':True,'thenType':'undefined','sharedMutation':True,'privateBuffer':True},'commonJS':{'type':'object','same':True,'encodeAlias':True,'decodeAlias':True,'nullParsePrototype':True,'defaultProperty':'undefined','rejectedCall':'ERR_SM_NODE_UNSUPPORTED','rejectedConstruction':'ERR_SM_NODE_UNSUPPORTED'}})
    util=report['util'];no_failure(util);equal(util['calls'],calls)
    variants=[x for x in expected['util']['variants']if x['features']==util['cases']['features']];assert len(variants)==1
    properties(util,{'cases':variants[0],'exports':expected['util']['expectedExports'],'snapshotIdentity':True,'noFacadeBundled':True,'aliases':{'bareCanonicalNamespaces':True,'cachedDynamicNamespaces':True,'sysNamespaceDistinct':True,'sharedDefault':True,'sharedTypes':True,'thenType':'undefined','namespacePrototypeNull':True},'common':{'same':True,'textIdentity':True,'customSymbol':True,'defaultProperty':'undefined'},'hardening':{'unsupportedCode':'ERR_SM_NODE_UNSUPPORTED','invalidCode':'ERR_INVALID_ARG_TYPE','setterCalls':0,'depth':4}})
    assert len(util['deferred'])==108
    for row in util['deferred']:properties(row,{'code':'ERR_SM_NODE_UNSUPPORTED','profile':'sm-node-22.14.0-m0.7'})
    stream_web(report['streamWeb'],expected['streamWeb'],calls)
    protected(report['protectedAbort'],expected['protectedAbort'],calls)

def response(body,audit,tag,classic_expected,events_oracle,ownership):
    no_failure(body);properties(body,{'schema':1,'requestTag':tag,'snapshotMarker':'HTTP module initialized during componentization'})
    count=body['componentInstanceRequestCount'];assert type(count)is int and count>=1
    native=body['native'];no_failure(native);equal(native['combinedSchema'],1)
    classic=native['classic'];no_failure(classic)
    properties(classic,{'schema':1,'calls':count,'ordinary':classic_expected,'identity':{'esmAliases':True,'rootDefault':True,'promises':True,'globalBuffer':True}})
    base=native['baseline'];no_failure(base)
    core=audit['coreExpectations'];assert core['coreVersion']=='sm-node-22.14.0-m0.11'
    properties(base,{'coreVersion':core['coreVersion'],'allocUnsafePolicy':core['allocUnsafePolicy'],'allocUnsafePrimordialCalls':{'integerCalls':0,'finiteCalls':0,'truncatedLength':3},'strings':381,'bytes':250,'stubCalls':9,'stubConstructors':9,'unavailableMethods':91,'globalBufferIdentity':True,'staticCommonJS':True})
    for field,operation in[('unsupported','spawn'),('unsupportedConstructor','ChildProcess')]:equal(body[field],{'code':'ERR_SM_NODE_UNSUPPORTED','module':'node:child_process','operation':operation,'profile':core['coreVersion']})
    entropy=base['entropyIntegration'];properties(entropy,{'policy':'runtime-only','snapshotHash':'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad','ownership':ownership})
    assert len(entropy['snapshot'])==4 and all(row['code']=='ERR_SM_ENTROPY_INITIALIZATION'for row in entropy['snapshot'])
    equal(entropy['secure']['policy'],'runtime-only');assert re.fullmatch('[a-f0-9]{64}',entropy['secure']['bytes'])
    properties(entropy['rsa'],{'type':'public','modulusLength':2048})
    foundations(base['foundations'],audit['foundationOracles'],count,events_oracle)
    equal(base['foundations']['calls'],classic['calls'])
    return {'counter':count,'randomBytes':entropy['secure']['bytes'],'classicGroups':len(classic['ordinary']),'protectedGroups':sum(len(base['foundations']['protectedAbort'][key])for key in['publicCases','nestedOnceCases','receiverCases']),'symbol':base['foundations']['protectedAbort']['symbol'],'classicIdentity':classic['identity']}
