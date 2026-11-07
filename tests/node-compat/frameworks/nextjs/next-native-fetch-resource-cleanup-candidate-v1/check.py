"""Read-only afterimage/patch/public API joins; never compile or execute C++."""
from pathlib import Path
import argparse
import ast
import difflib
import hashlib
import json

HERE = Path(__file__).resolve().parent

def row(path):
    path = Path(path); body = path.read_bytes()
    return dict(path=str(path),sha256=hashlib.sha256(body).hexdigest(),bytes=len(body))

def check(value, label):
    if value is not True:
        raise ValueError(label)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--current',action='store_true',help='also read exact selected original Source/API witnesses, no binary/tree scan')
    args=parser.parse_args()
    manifest=json.loads((HERE/'afterimages.json').read_bytes())
    plan=json.loads((HERE/'ownership-plan.json').read_bytes())
    expected={'include/host_api.h','host-apis/wasi-0.2.0/host_api.cpp','host-apis/wasi-0.2.0/handles.h','builtins/web/fetch/fetch-api.cpp','builtins/web/fetch/request-response.h','builtins/web/fetch/request-response.cpp'}
    check({r['relativePath'] for r in manifest['files']}==expected and len(manifest['files'])==6,'six existing files only')
    patch=''; text={}
    for item in manifest['files']:
        rel=item['relativePath']
        for phase in ['before','after']:
            ref=item[phase];path=HERE/ref['path'];check(row(path)==dict(ref,path=str(path)),'afterimage bytes')
        before=(HERE/item['before']['path']).read_text();after=(HERE/item['after']['path']).read_text();text[rel]=after
        patch+=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
        if args.current:check(row(item['actualCompiledBefore']['path'])==item['actualCompiledBefore'],'current before Source')
    check(patch==(HERE/'resource-cleanup.patch').read_text(),'whole deterministic patch reproduction')
    body=text['builtins/web/fetch/request-response.cpp'];api=text['host-apis/wasi-0.2.0/host_api.cpp'];head=text['include/host_api.h']
    task_cancel=body.split('[[nodiscard]] bool cancel(api::Engine*) override {',1)[1].split('}',1)[0]
    check('retire_subscription();' in task_cancel and 'terminal_body' not in task_cancel,'task retirement is not body terminal')
    check(body.index('retire_subscription(); // A single read task') < body.index('if (chunk.done)'),'retire subscription before EOF disposal')
    check('if (!ENGINE->cancel_async_task(keep_alive))' in body and 'body->request_cancel();' in body,'queued and running cancellation')
    check('std::optional<mozilla::WeakPtr<api::AsyncTask>> pending_read_' in head,'weak association not rooted cycle/global map')
    check(api.index('unsubscribe();',api.index('HttpIncomingBody::retire')) < api.index('wasi_io_streams_input_stream_drop_own',api.index('HttpIncomingBody::retire')),'child subscription first')
    check('if (pending_read() || native_append_selected_) return Result<Void>::err(154);' in api,'no active read or deferred append blind drop')
    check('other->defer_read_cleanup_for_native_append();' in api,'real append entry marks exclusion')
    cancel_hook=body.split('bool RequestOrResponse::body_source_cancel_algorithm',1)[1].split('bool write_all_finish_callback',1)[0]
    check(cancel_hook.index('if (body->native_append_selected())') < cancel_hook.index('body->request_cancel();'),'append exclusion precedes cancel state change')
    check('future_->subscribe()' in body and 'future_(std::move(future))' in body,'future uses moved-to owner')
    check('engine->queue_async_task(this);' in body.split('if(!maybe_response.has_value())',1)[1].split('auto *response',1)[0],'not-ready is not terminal')
    check('std::unique_ptr<host_api::FutureHttpIncomingResponse> future_' in text['builtins/web/fetch/request-response.h'],'unique future ownership')
    changed=''.join(line[1:] for line in patch.splitlines(True) if line.startswith('+') and not line.startswith('+++'))
    check('_drop_borrow(' not in changed,'never borrow-drop as release')
    for signature in plan['publicWasiApiSignatures'].values():
        name=signature.split('(')[0].split()[-1]
        check(name+'(' in changed,'declared actual public owned API used')
    check(all(manifest[k] is None for k in ['futureMaterialization','futureGenerators','futureNativeBuild','futureComponent','futureReturnedImportFunctionCount','futureNormalRuntime']),'actual slots null')
    check(plan['allHttpCleanupClaim'] is False and len(plan['deferred'])==7,'bounded scope')
    for p in HERE.glob('*.py'):ast.parse(p.read_text())
    witnesses=json.loads((HERE/'api-witnesses.json').read_bytes())
    for part in witnesses['excerpts']:
        check(hashlib.sha256(part['text'].encode()).hexdigest()==part['sha256'],'retained excerpt hash')
    check(witnesses['newOwnedApiDeclarations']['localHostApi020']==witnesses['newOwnedApiDeclarations']['linkedBindings0210'],'six new declarations agree across actual local/linked headers')
    if args.current:
        for ref in witnesses['sources']:
            check(row(ref['path'])==ref,'current selected API Source witness')
    print(json.dumps(dict(sourceOnly=True,afterimages=6,beforeBytes=sum(r['before']['bytes']for r in manifest['files']),afterBytes=sum(r['after']['bytes']for r in manifest['files']),currentSelectedSource=args.current,compilerOrCMakeOrCargoOrGuestExecuted=False)))

if __name__=='__main__':main()
