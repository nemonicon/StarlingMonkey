"""Check source reversals and execute only an instrumented host selector model."""
from pathlib import Path
import hashlib
import json
import subprocess
import time

HERE = Path(__file__).resolve().parent
WORK = Path('/private/tmp/starling-node-compat/task-selection-source-model-v1')


def row(p):
    p = Path(p); b = p.read_bytes()
    return dict(path=str(p.resolve()), sha256=hashlib.sha256(b).hexdigest(), bytes=len(b))


def extract(text):
    start = text.index('std::optional<size_t> api::AsyncTask::select(') if 'std::optional<size_t> api::AsyncTask::select(' in text else text.index('size_t api::AsyncTask::select(')
    return text[start:text.index('\nnamespace host_api {', start)]


def main():
    assert __debug__
    contract = json.loads((HERE/'source-contract.json').read_bytes())
    for change in contract['changes']:
        assert row(change['original']['path']) == change['original']
        before = (HERE/'before'/change['path']).read_text()
        assert row(HERE/'before'/change['path']) == change['before']
        actual = before
        for e in change['edits']:
            assert actual.count(e['before']) == e['count']
            actual = actual.replace(e['before'],e['after'])
        assert actual == (HERE/'afterimages'/change['path']).read_text()
        assert row(HERE/'afterimages'/change['path']) == change['after']
        for e in reversed(change['edits']):
            assert actual.count(e['after']) == e['count']
            actual = actual.replace(e['after'],e['before'])
        assert actual == before
    host = 'host-apis/wasi-0.2.0/host_api.cpp'
    final = extract((HERE/'afterimages'/host).read_text())
    old = extract((HERE/'before'/host).read_text())
    legacy = old.replace('api::AsyncTask::select', 'api::LegacyAsyncTask::select').replace('RefPtr<AsyncTask>', 'RefPtr<LegacyAsyncTask>')
    runtime = (HERE/'afterimages/runtime/event_loop.cpp').read_text()
    assert runtime.index('if (!selected)') < runtime.index('const size_t task_idx = *selected;') < runtime.index('running.get().task = tasks->at(task_idx);')
    assert 'continue;' in runtime[runtime.index('if (!selected)'):runtime.index('const size_t task_idx = *selected;')]
    assert final.index('if (tasks.empty())') < final.index('std::vector<WASIHandle')
    WORK.mkdir()
    generated = (HERE/'model-prefix.cpp').read_text() + '\n' + final + '\n' + legacy + '\n' + (HERE/'model-suffix.cpp').read_text()
    (WORK/'model.cpp').write_text(generated)
    commands = []
    for argv in [['/usr/bin/clang++','-std=c++20','-O2','-Wall','-Wextra','-Werror',str(WORK/'model.cpp'),'-o',str(WORK/'model')], [str(WORK/'model')]]:
        start = time.monotonic(); r = subprocess.run(argv,capture_output=True,timeout=60)
        commands.append(dict(argv=argv,rawExitCode=r.returncode,stdout=r.stdout.decode(),stderr=r.stderr.decode(),operationalSeconds=time.monotonic()-start))
        assert r.returncode == 0, r.stderr.decode()
    assert json.loads(commands[-1]['stdout'])['allPassed'] is True
    result = dict(schemaVersion=1,exactReversals=3,modelCases=12,generatedModel=row(WORK/'model.cpp'),commands=commands,modelOnly=True,guestExecuted=False,nativeEngineBuilt=False,operationalAdmission=False)
    (HERE/'model-results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(exactReversals=3,modelCases=12,allPassed=True)))


if __name__ == '__main__':
    main()
