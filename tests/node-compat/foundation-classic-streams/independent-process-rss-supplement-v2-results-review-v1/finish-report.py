"""Read-only arithmetic/report formatting; writes only this new review packet."""
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
OUT = Path('/tmp/starling-node-compat/production-common-byte-process-rss-supplement-v2')
ADOPTION = HERE.parent / 'production-adoption-v1'
COMPARISONS = [
    ('same-engine-binding', ['native-on', 'canonical-on']),
    ('whole-profile', ['canonical-on', 'canonical-off']),
    ('different-stock-provider', ['canonical-on', 'stock-on']),
]


def put(name, value):
    with (HERE / name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def main():
    report = json.loads((OUT / 'results.json').read_bytes())
    phase = json.loads((ADOPTION / 'reviewed-composed-timing-phase-v1.json').read_bytes())
    outer = json.loads(Path('/tmp/starling-node-compat/common-byte-process-rss-supplement-v2.terminal.json').read_bytes())
    root = json.loads((ADOPTION / 'process-rss-supplement-v2-root-results.json').read_bytes())
    controls = []
    for observation in report['observations']:
        terminal = json.loads(Path(observation['terminalPath']).read_bytes())
        assert observation['wholeProcessElapsedMs'] == terminal['operationalElapsedMs'] > 0
    assert outer['elapsedSeconds'] == root['elapsedSecondsOperationalOnly']
    completion = json.loads((OUT / 'completion.json').read_bytes())
    assert completion['state'] == 'PROCESS_RSS_SUPPLEMENT_FILES_SEALED_EXTERNAL_EXIT_ZERO_REQUIRED'
    assert completion['sourceIndexSha256'] == report['sourceIndexSha256'] == root['sourceIndexSha256']
    assert completion['authoritySha256'] == report['authority']['sha256'] == root['authoritySha256']
    assert completion['workerCount'] == 18
    assert completion['result']['path'] == str(OUT / 'results.json')
    assert completion['result']['sha256'] == '606346356502ed8824b54677f825cdccec2bc8d48a4e23c34558384e18b8367f'
    assert completion['result']['bytes'] == 159786
    assert report['runtimeAcceptanceClaim'] is False and completion['runtimeAcceptanceClaim'] is False
    for arm in ['native-on', 'canonical-on', 'canonical-off', 'stock-on']:
        records = [item['actual'] for item in report['observations'] if item['arm'] == arm]
        for actual in records:
            identity = json.loads(actual['rawReturns'][0]['rawReturn'])
            probes = [json.loads(actual['rawReturns'][index]['rawReturn']) for index in [1, 6]]
            assert identity == phase['components'][arm]['identity']
            assert probes == [phase['components'][arm]['checkpointProbe']] * 2
            assert all(value['queueDepthObserved'] is False and value['terminalQueueEmptyObserved'] is False for value in probes)
        controls.append({
            'arm': arm, 'freshProcessesAcrossComparisons': len(records),
            'identity': phase['components'][arm]['identity'],
            'beforeAfterCheckpointProbe': phase['components'][arm]['checkpointProbe'],
            'queueEmptyInference': False,
        })
    data = json.loads((HERE / 'numeric-reconstruction.json').read_bytes())

    def metric(comparison, arm, name):
        return next(item for item in data['summary'] if item['comparison'] == comparison
                    and item['arm'] == arm and item['metric'] == name and item['kind'] == 'raw')

    def formatted(item, scale=1):
        return '{:.2f} ({:.2f}–{:.2f})'.format(
            item['median'] / scale, item['min'] / scale, item['max'] / scale)

    lines = [
        'Independent actual process RSS supplement v2: **PASS within this bounded observation scope**. Root17254/parent11856 observed raw0 in98.196s. The599-file closure,18 distinct fresh PIDs,18 zero terminals with owned-group cleanup, all126 typed returns and the final10348-row source audit record match. Nothing was rerun by this reader. Source22/input10348 provenance is bound to prior source proof73fa; a second full input audit was not executed. Initial parent audit completion follows authenticated source control flow and completed execution; the final audit is a retained explicit pass record.',
        '',
        'Both setup calls returned exact signed32 numbers151852933 and-1502831163 in all18 workers. The other90 values are whole JSON strings matching the phase and independent Python reconstruction of the pinned Node compact oracle. All7 call arguments/order,7 raw files,17 progress records, stdout/result/parent-observed replicas, identity/probe controls and snapshot/stage sequences were checked. Capacity, grow-count and guest-heap fields remain null.',
        '',
        'Instantaneous process RSS is bytes; public maxRSS is KiB on Darwin. Node documents the [RSS byte unit](https://nodejs.org/download/release/v22.14.0/docs/api/process.html#processmemoryusage) and [maximum-RSS API](https://nodejs.org/download/release/v22.14.0/docs/api/process.html#processresourceusage). Its pinned [libuv Darwin branch](https://raw.githubusercontent.com/nodejs/node/v22.14.0/deps/uv/src/unix/core.c) divides OS bytes by1024. Tables convert to MiB for display; raw units remain in CSV/JSON.',
        '',
        'Cells are median (min–max), **three independent processes per arm/comparison**. Stages within one worker are correlated, not extra independent samples.',
        '',
        '| Comparison | Arm | Instantiate MiB | After small MiB | After large MiB | Max before final hash MiB | Terminal max MiB |',
        '| --- | --- | ---: | ---: | ---: | ---: | ---: |',
    ]
    rss_names = ['rss.after-instantiate', 'rss.after-small', 'rss.after-large',
                 'maxRSS.beforeFinalHash', 'maxRSS.terminal']
    for comparison, pair in COMPARISONS:
        for arm in pair:
            cells = [formatted(metric(comparison, arm, name),
                               1048576 if name.startswith('rss.') else 1024)
                     for name in rss_names]
            lines.append('| ' + ' | '.join([comparison, arm] + cells) + ' |')
    lines += [
        '',
        'Paired ratios are A/B within one repetition, retaining AB, BA, AB. Below1 means smaller A for that metric, without significance or causal inference.',
        '',
        '| Comparison (A/B) | Pre-final max A/B, median (min–max) | Terminal max A/B, median (min–max) |',
        '| --- | ---: | ---: |',
    ]
    for comparison, pair in COMPARISONS:
        cells = []
        for name in ['maxRSS.beforeFinalHash', 'maxRSS.terminal']:
            item = next(item for item in data['pairedRatioSummary']
                        if item['comparison'] == comparison and item['metric'] == name)
            cells.append('{:.4f} ({:.4f}–{:.4f})'.format(
                item['medianAoverB'], item['minAoverB'], item['maxAoverB']))
        lines.append('| ' + ' | '.join([comparison + ' (' + '/'.join(pair) + ')'] + cells) + ' |')
    lines += [
        '',
        'Operational stage time stays separate. Compile-and-binding-load includes both activities, not physical cold startup or throughput.',
        '',
        '| Comparison | Arm | Compile+binding ms | Instantiate ms | First identity ms | Whole worker ms |',
        '| --- | --- | ---: | ---: | ---: | ---: |',
    ]
    for comparison, pair in COMPARISONS:
        for arm in pair:
            cells = [formatted(metric(comparison, arm, name))
                     for name in ['stage.compile-and-binding-load', 'stage.instantiate',
                                  'stage.first-identity-export', 'worker.elapsed']]
            lines.append('| ' + ' | '.join([comparison, arm] + cells) + ' |')
    lines += [
        '',
        'All13 snapshot RSS/cumulative times,9 stage times,7 call-time RSS values,2 maxima and whole-worker time are reconstructed in all-raw-metrics.csv and summary.csv (312 raw/control summaries). All396 defined raw paired ratios remain; the identically-zero bootstrap cumulative time has no ratio. Interval deltas remain in controls-not-subtracted.csv. They are differences between observations, not isolated guest allocation or causal hash cost.',
        '',
        'Initial hash-interval RSS changes were about16.5–19.8MiB; final hash-interval changes about8.7–13.7MiB. Native same-engine large-after-small RSS fell about3.2MiB; no cause is identified. Sampled byte RSS is consistent with lifetime KiB maxima. Validation, streaming and allocator effects matter; no controls were subtracted or net guest-memory number inferred.',
        '',
        'Same-engine pre-final maximum ratios cross1 across three pairs, so this does not establish a universal native memory reduction. Whole-profile ON maxima are slightly above OFF in this sample. Stock has a different provider/Buffer/scheduler, so that comparison cannot isolate one native mechanism. These are bounded process-cost observations of diagnostic engines and existing components, not production-engine performance, guest heap/capacity/growth, unique pages, worst-case memory, reset/reuse or universal superiority.',
        '',
        'The large4MiB case follows small8KiB on one instance. Node/V8, glue, compilation cache, hashes, prior allocations and parent/shared-machine pressure affect observations. AB/BA/AB has2:1 first-arm imbalance and n=3 is small. No forced GC, allocator trimming or private memory inspection occurred.',
        '',
        'Failed v1 e511 remains raw1 with zero measured workers; its source-review miss is retained. This18-worker supplement is separate from the old168-worker throughput batch and does not replace or reanalyse it. Old-Root context dependencies, archive/promotion holds, known Node/GC/HTTP limits and latest accepted checkpointv12 remain unchanged.',
    ]
    put('additional-integrity-and-controls.json', {
        'schemaVersion': 1, 'state': 'ADDITIONAL_TERMINAL_TIME_AND_FUNCTIONAL_GUARDS_CHECKED',
        'checks': ['all18WholeWorkerTimesMatchTerminals', 'parentTimeMatchesExternalTerminal',
                   'completionSourceAuthorityAndReportTupleExact', 'runtimeAcceptanceNotIssued'],
        'functionalControls': controls, 'timingRawControlsReexecuted': False,
        'RSSIntervalControlsSubtracted': False,
    })
    put('units.json', {
        'schemaVersion': 1, 'nodeVersion': 'v22.14.0',
        'RSS': {'rawUnit': 'bytes', 'displayMiBDivisor': 1048576,
                'primarySource': 'https://nodejs.org/download/release/v22.14.0/docs/api/process.html#processmemoryusage'},
        'maxRSS': {'rawUnit': '1024-byte KiB on Darwin', 'displayMiBDivisor': 1024,
                   'primaryDocumentation': 'https://nodejs.org/download/release/v22.14.0/docs/api/process.html#processresourceusage',
                   'DarwinNormalizationSource': 'https://raw.githubusercontent.com/nodejs/node/v22.14.0/deps/uv/src/unix/core.c'},
        'pairedRatio': 'A/B in identical raw units; no baseline subtraction',
        'guestMemoryOrThroughputConversion': False,
    })
    with (HERE / 'README.md').open('x') as stream:
        stream.write('\n'.join(lines) + '\n')
    print(json.dumps({'additionalChecks': 4, 'functionalArms': 4,
                      'reportBytes': (HERE / 'README.md').stat().st_size, 'reruns': False}))


if __name__ == '__main__':
    main()
