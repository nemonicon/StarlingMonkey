"""Pure synthetic NetLog DATA checks; no files, browser or network fixtures."""
import copy
import importlib.util
from pathlib import Path

path = Path(__file__).with_name('analyze.py')
spec = importlib.util.spec_from_file_location('netlog_pure_data', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
origin = 'http://127.0.0.1:34567'
base = dict(constants=dict(logEventTypes={'URL_REQUEST_START_JOB': 1, 'DEPENDENCY': 2, 'FAILED': 3},
    logSourceType={'URL_REQUEST': 1, 'HTTP_STREAM_JOB': 2},
    logEventPhase={'PHASE_BEGIN': 1, 'PHASE_END': 2, 'PHASE_NONE': 0},
    netError={'OK': 0, 'ERR_ABORTED': -3, 'IO_PENDING': -1}), events=[
    dict(time='1', type=1, phase=1, source=dict(id=7, type=1), params=dict(url=origin+'/actions', method='POST')),
    dict(time='2', type=2, phase=0, source=dict(id=7, type=1), params=dict(source_dependency=dict(id=9, type=2))),
    dict(time='3', type=3, phase=2, source=dict(id=9, type=2), params=dict(net_error=-3)),
])
checks = 0


def need(value):
    global checks
    assert value
    checks += 1


def refuses(data, selected_origin=origin):
    try:
        module.classify(data, selected_origin)
    except ValueError:
        return True
    return False


report = module.classify(base, origin)
need(report['candidateCount'] == 1)
need(report['candidates'][0]['witnessEventIndexes'] == [0])
need(report['explicitDependencyEdges'][0]['dependencySourceId'] == 9)
need(report['explicitNetErrors'][0]['name'] == 'ERR_ABORTED')
need(report['explicitNetErrors'][0]['eventIndex'] == 2)
need(report['negativeNetErrorObserved'] is True)
need([event['time'] for event in report['selectedEvents']] == ['1', '2', '3'])
need(report['historyCompleteProved'] is False and report['completeRequestLifecycleProved'] is False)
need(report['netlogSourceIdIsNativeStoreIdentity'] is False and report['uniqueCauseProved'] is False)
for mutation in ['GET', 'wrong-origin', 'missing-method', 'not-url-request']:
    data = copy.deepcopy(base)
    if mutation == 'GET': data['events'][0]['params']['method'] = 'GET'
    elif mutation == 'wrong-origin': data['events'][0]['params']['url'] = 'http://127.0.0.1:34568/actions'
    elif mutation == 'missing-method': del data['events'][0]['params']['method']
    else: data['events'][0]['source']['type'] = 2
    absent = module.classify(data, origin)
    need(absent['candidateCount'] == 0 and absent['postObservation'] == 'not observed in retained events')
    need(absent['browserStrictGateAccepted'] is False)
data = copy.deepcopy(base); data['events'][2]['params']['net_error'] = -999
need(module.classify(data, origin)['explicitNetErrors'][0]['name'] == 'UNKNOWN_NET_ERROR')
data = copy.deepcopy(base); data['events'][2]['params']['net_error'] = 0
need(module.classify(data, origin)['negativeNetErrorObserved'] is False)
data = copy.deepcopy(base); data['events'][2]['params']['net_error'] = -1
pending = module.classify(data, origin)['explicitNetErrors'][0]
need(pending['name'] == 'IO_PENDING' and pending['isNegativeCode'] is True)
need('isFailure' not in pending)
data = copy.deepcopy(base); data['events'][2]['params']['net_error'] = True
need(refuses(data))
data = copy.deepcopy(base); data['events'][0]['time'] = 'NaN'
need(refuses(data))
data = copy.deepcopy(base); del data['constants']['logSourceType']
need(refuses(data))
need(refuses(base, 'http://127.0.0.1:34567/'))
data = copy.deepcopy(base); data['events'] = []
need(module.classify(data, origin)['postObservation'] == 'not observed in retained events')
print({'passed': True, 'pureSyntheticDataChecks': checks, 'browserOrNetworkInvoked': False})
