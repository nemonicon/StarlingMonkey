"""Ordinary llvm-nm/read/hash audit only. No compilation, linking or guest."""
from pathlib import Path
import hashlib,json,re,subprocess
HERE=Path(__file__).resolve().parent
ROOT=Path('/tmp/starling-node-compat/zlib-static-archive-audit-v1')
ARCHIVE=Path('/tmp/starling-node-compat/improved-build/spidermonkey-dist-release/libspidermonkey.a')
INCLUDES=ARCHIVE.parent/'include'
NM=Path('/tmp/starling-node-compat/improved-build/cache/wasi-sdk/85e6/bin/llvm-nm')
def row(path):
    before=path.stat();h=hashlib.sha256()
    with path.open('rb')as f:
        for data in iter(lambda:f.read(1024*1024),b''):h.update(data)
    after=path.stat();assert(before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_ino,after.st_size,after.st_mtime_ns)
    return{'path':str(path),'realPath':str(path.resolve()),'sha256':h.hexdigest(),'bytes':before.st_size}
def main():
    ROOT.mkdir(exist_ok=False)
    inputs=[row(path)for path in [NM,ARCHIVE,INCLUDES/'zlib.h',INCLUDES/'zconf.h',INCLUDES/'js-confdefs.h']]
    command=[str(NM),'--defined-only','--extern-only','--format=posix','--print-file-name',str(ARCHIVE)]
    child=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=55)
    (ROOT/'nm.stdout.txt').write_bytes(child.stdout);(ROOT/'nm.stderr.txt').write_bytes(child.stderr)
    required=['zlibVersion','deflateInit2_','deflate','deflateEnd','inflateInit2_','inflate','inflateEnd']
    lines=child.stdout.decode().splitlines();selected=[];counts={}
    for name in required:
        for symbol in [name,'z_'+name]:
            matches=[line for line in lines if re.search(r'(?:^|\s)'+re.escape(symbol)+r'\s+[A-Za-z]\s',line)]
            counts[symbol]=len(matches);selected.extend(matches)
    assert [row(Path(value['path']))for value in inputs]==inputs
    headers={}
    for name in ['zlib.h','zconf.h','js-confdefs.h']:
        text=(INCLUDES/name).read_text();headers[name]=[{'line':i+1,'text':line}for i,line in enumerate(text.splitlines())if re.search(r'\b(?:Z_PREFIX|Z_PREFIX_SET|ZLIB_VERSION|ZLIB_VERNUM|MOZ_ZLIB|zlibVersion|deflateInit2_|inflateInit2_)\b',line)]
    result={'schemaVersion':1,'state':'READ_ONLY_SELECTED_SM147_ZLIB_HEADER_ARCHIVE_SYMBOL_OBSERVATIONS','command':command,'exitCode':child.returncode,
      'inputs':inputs,'outputs':[row(ROOT/'nm.stdout.txt'),row(ROOT/'nm.stderr.txt')],'requiredSymbolDefinitionCounts':counts,'selectedLines':selected,'headerSourceLines':headers,
      'symbolVisibilityAndImportResolutionProved':False,'linkedNewModule':False,'runtimeZlibVersionCalled':False,'guestExecuted':False,
      'scope':'Static name/definition witness for this archive/header only. Actual selected compilation macros, linker extraction/resolution and runtime zlibVersion() identity remain future gates.'}
    (HERE/'evidence/archive-symbol-audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'exitCode':child.returncode,'counts':counts,'archiveSha256':inputs[1]['sha256'],'linkedOrGuestExecuted':False}))
if __name__=='__main__':main()
