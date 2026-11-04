"""Future ordinary build codec witnesses. Importing launches nothing."""
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess

ARCHIVE_SHA='298b85501657189dc66139242abf5aeb4e981b8db7c37cc5a69d1151ec40aacc'
ARCHIVE_BYTES=538170426
HEADERS={'zlib.h':('8a5579af72ea4f427ff00a4150f0ccb3fc5c1e4379f726e101133b1ab9fc600c',96829),
 'zconf.h':('61c756bba04523c333be09e33830ab617b11401d23583569bb94af2057418e14',16600),
 'mozzconf.h':('c16f8894b2d303dd5bae94c4ed9f76ecd4c942ab7346d5c66c1cc7074d3351d9',5855),
 'js-confdefs.h':('841e57a382d7d8219431dc26e1d1307af1649228503d21bcf2eac826fc99acd6',2283)}
SYMBOLS=['zlibVersion','deflateInit2_','deflate','deflateEnd','inflateInit2_','inflate','inflateEnd']
NM_SHA='0f0dfccb3778ec756b3bcbfe69574cdddfb2a6da2ae92c5bc1df1d1d6d3a591c'

def row(path,expected=None,size=None):
 path=Path(path);before=path.lstat();assert path.is_file()and not path.is_symlink()
 digest=hashlib.sha256()
 with path.open('rb')as source:
  for block in iter(lambda:source.read(1024*1024),b''):digest.update(block)
 after=path.lstat();assert(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns)
 if expected is not None:assert digest.hexdigest()==expected,str(path)
 if size is not None:assert after.st_size==size,str(path)
 return{'path':str(path.absolute()),'sha256':digest.hexdigest(),'bytes':after.st_size}

def distribution(root):
 root=Path(root).absolute()
 archive=row(root/'libspidermonkey.a',ARCHIVE_SHA,ARCHIVE_BYTES)
 headers=[row(root/'include'/name,*expected)for name,expected in HEADERS.items()]
 assert '#include "mozzconf.h"'in(root/'include/zconf.h').read_text()
 assert 'zconf.h'in(root/'include/zlib.h').read_text()
 return{'archive':archive,'headers':headers}

def selection_contract(value):
 """Validate an explicitly selected distribution descriptor, not arbitrary bytes."""
 assert value['version']=='sm-selected-moz-z-compile-input-v1'
 root=Path(value['selectedDistribution']);assert root.is_absolute()and '..'not in root.parts
 assert value['archive']=={'path':str(root/'libspidermonkey.a'),'sha256':ARCHIVE_SHA,'bytes':ARCHIVE_BYTES}
 expected=[{'path':str(root/'include'/name),'sha256':digest,'bytes':size}for name,(digest,size)in HEADERS.items()]
 assert value['headers']==expected
 assert value['requiredForcedInclude']==expected[-1]
 return value['requiredForcedInclude']['path']

def selected_compile_input(root):
 """Real file authentication available before layer.decorate is invoked."""
 root=Path(root).absolute();current=distribution(root)
 value={'version':'sm-selected-moz-z-compile-input-v1','selectedDistribution':str(root),**current,'requiredForcedInclude':current['headers'][-1]}
 selection_contract(value);return value

def compile_forced_include(tokens,selection):
 path=selection_contract(selection)
 assert tokens.count('-include')==1,'Exactly one selected SM forced include required'
 at=tokens.index('-include');assert at+1<len(tokens)and tokens[at+1]==path,'Forced include must be the selected distribution js-confdefs.h'
 for token in tokens:
  if token=='-include':continue
  assert not token.startswith(('-include','-imacros')),token
  assert not token.startswith(('-Wp,','-Xpreprocessor','-Xclang')),token
 return path

def cache_install(build):
 lines=(Path(build)/'CMakeCache.txt').read_text().splitlines()
 values=[line.partition('=')[2]for line in lines if line.startswith('INSTALL_BUILTINS:')]
 assert len(values)==1
 path=Path(values[0]);assert path.is_absolute()and path.is_relative_to(Path(build).absolute())
 result=row(path);assert 'builtins::node_compat'in path.read_text()
 return result

def before(root,build,path):
 value={'schemaVersion':1,'state':'CODEC_INPUTS_AUTHENTICATED_BEFORE_NATIVE_BUILD',**distribution(root),'install':cache_install(build)}
 with Path(path).open('x')as out:json.dump(value,out,indent=2);out.write('\n')
 return value

def symbols(raw):
 lines=raw.decode().splitlines();selected={}
 for name in SYMBOLS:
  found=[line for line in lines if re.search(r'(?:^|\s)MOZ_Z_'+re.escape(name)+r'\s+[Tt]\s',line)]
  assert len(found)==1,(name,found)
  assert not any(re.search(r'(?:^|\s)(?:z_)?'+re.escape(name)+r'\s+[A-Za-z]\s',line)for line in lines)
  selected[name]=found[0]
 return selected

def no_second_codec(tokens,compile_selection=None):
 if compile_selection is not None:compile_forced_include(tokens,compile_selection)
 flattened=[]
 for token in tokens:
  flattened.extend(token[4:].split(',')if token.startswith('-Wl,')else[token])
 for index,word in enumerate(flattened):
  assert word not in ['-lz','-lzlib','-l:libz.a','-l:libzlib.a','--library=z','--library=zlib'],word
  if word in ['-l','--library']:
   assert index+1<len(flattened)and flattened[index+1]not in ['z','zlib',':libz.a',':libzlib.a'],word
 for word in tokens:
  assert word not in ['-D','-U','-imacros'],word
  if word=='-include'and compile_selection is not None:continue
  assert not word.startswith(('-include','-imacros')),word
  assert not any(word==prefix+name or word.startswith(prefix+name+'=')for name in ['Z_PREFIX','Z_PREFIX_SET']for prefix in ['-D','-U']),word
  assert word not in ['-lz','-lzlib','-l:libz.a','-l:libzlib.a']and not re.search(r'(?:^|/)libz(?:lib)?\.(?:a|so|dylib)$',word),word

def kernel_headers(command,dist,selection):
 assert selection['selectedDistribution']==str(Path(dist).absolute());selection_contract(selection)
 words=shlex.split(command);no_second_codec(words,selection);includes=[];i=0
 while i<len(words):
  word=words[i]
  if word in ['-I','-isystem']:
   i+=1;assert i<len(words);includes.append(Path(words[i]))
  elif word.startswith('-I')and len(word)>2:includes.append(Path(word[2:]))
  elif word.startswith('-isystem')and len(word)>8:includes.append(Path(word[8:]))
  i+=1
 candidates=[path/'zlib.h'for path in includes if(path/'zlib.h').is_file()]
 assert candidates and candidates[0].resolve()==(Path(dist)/'include/zlib.h').resolve(),'Actual first zlib.h search must select the authenticated SM distribution'
 return[str(path)for path in includes]

def link_commands(raw,build,archive,resolve_path=lambda path:path):
 """Parse finite captured direct-link or compiler/cd/optimizer forms; never run."""
 build=Path(build).absolute();archive=Path(archive).absolute();responses={};selected=[]
 def ordinary_path(word,base):
  path=Path(word);assert '..'not in path.parts
  path=path if path.is_absolute()else base/path
  assert path.is_relative_to(build),'Link output/cd must stay in its actual build'
  return path
 def no_shell_words(words):
  for word in words:assert not any(char in word for char in ['&',';','|','<','>','$','`','#','(',')','\n','\r']),word
 def shell_form(line):
  # Split the shell grammar before response expansion. Response tokens are only
  # compiler arguments and can never become a synthetic shell stage.
  assert not any(char in line for char in [';','|','<','>','$','`','#','(',')',"'",'"','\\','\n','\r'])
  words=shlex.split(line);groups=[[]]
  for word in words:
   if word=='&&':groups.append([])
   else:groups[-1].append(word)
  assert all(groups)
  for group in groups:no_shell_words(group)
  if len(groups)==1:
   assert Path(groups[0][0]).name in ['clang++','clang','cxx-wrapper'],'Direct shape must be a compiler command'
   return 'direct-compiler-link-v1',groups[0],None,None
  assert len(groups)==4 and groups[0]==[':'],'Only observed leading-colon compiler/cd/optimizer chain is allowed'
  compiler,cd,optimizer=groups[1:]
  assert compiler[0]==str(build/'cxx-wrapper')
  assert len(cd)==2 and cd[0]=='cd'and Path(cd[1]).is_absolute()
  assert len(optimizer)==6 and optimizer[0]==str(build.parent/'cache/binaryen/1b13/bin/wasm-opt')
  assert optimizer[1:4]==['--strip-debug','-O3','-o']
  return 'compiler-cd-inplace-wasm-opt-v1',compiler,cd,optimizer
 def expand(words,depth=0):
  assert depth<=4;result=[]
  for word in words:
   if word.startswith('@'):
    path=Path(word[1:]);assert '..'not in path.parts and '.'not in path.parts
    path=path if path.is_absolute()else build/path
    assert path.is_relative_to(build)
    captured=Path(resolve_path(path));assert not captured.is_symlink()and captured.is_file()
    if captured==path:
     cursor=path.parent
     while cursor!=build.parent:
      assert cursor.is_dir()and not cursor.is_symlink(),str(cursor)
      if cursor==build:break
      cursor=cursor.parent
    data=captured.read_bytes();assert len(data)<=4*1024*1024
    tokens=shlex.split(data.decode());no_shell_words(tokens)
    responses[str(path)]={**row(captured),'path':str(path)};result.extend(expand(tokens,depth+1))
   else:result.append(word)
  return result
 for line in raw.decode().splitlines():
  if ' -c 'in line:continue
  words=shlex.split(line);no_second_codec(words)
  if 'libspidermonkey.a'not in line and not any(word.startswith('@')for word in words):continue
  kind,compiler,cd,optimizer=shell_form(line);expanded=expand(compiler);no_shell_words(expanded);no_second_codec(expanded)
  names=[Path(x)if Path(x).is_absolute()else build/x for x in expanded if x.endswith('/libspidermonkey.a')or x=='libspidermonkey.a']
  if any(x.resolve()==archive.resolve()for x in names):
   assert expanded.count('-o')==1
   at=expanded.index('-o');assert at+1<len(expanded)and expanded[at+1].endswith('.wasm'),'Selected archive must occur in an actual output-Wasm link command'
   output=ordinary_path(expanded[at+1],build)
   record={'rawCommand':line,'expandedArguments':expanded,'kind':kind,'compilerArguments':compiler,'compilerExpandedArguments':expanded,'compilerOutputPath':str(output)}
   if optimizer is not None:
    cwd=ordinary_path(cd[1],build);assert cwd==output.parent
    optimized_output=ordinary_path(optimizer[4],cwd);optimized_input=ordinary_path(optimizer[5],cwd)
    assert optimized_input==optimized_output==output,'Compiler output and optimizer input/output must name exactly the same Wasm'
    assert optimizer[4]==optimizer[5]==output.name
    record.update(postOptimizerArguments=optimizer,postOptimizerWorkingDirectory=str(cwd),postOptimizerInputPath=str(optimized_input),postOptimizerOutputPath=str(optimized_output),sameWasmOutputProved=True)
   selected.append(record)
 assert len(selected)==1,'Need exactly one actual final link command selecting the authenticated archive; unknown response/link shapes fail closed'
 return{'commands':selected,'responseFiles':list(responses.values())}

def after(repo,dist,build,before_path,evidence_root,metadata,expected_before_sha):
 row(before_path,expected_before_sha)
 before_bytes=Path(before_path).read_bytes();assert hashlib.sha256(before_bytes).hexdigest()==expected_before_sha
 before_value=json.loads(before_bytes);assert before_value['state']=='CODEC_INPUTS_AUTHENTICATED_BEFORE_NATIVE_BUILD'
 current=distribution(dist);assert current['archive']==before_value['archive']and current['headers']==before_value['headers']
 selected=selected_compile_input(dist);assert metadata['zlibSelectedCodecInput']==selected
 assert cache_install(build)==before_value['install']
 build=Path(build).absolute();evidence_root=Path(evidence_root).absolute();evidence_root.mkdir(exist_ok=False)
 db=json.loads((build/'compile_commands.json').read_bytes());kernels=[entry['command']for entry in db if entry['file']==str(Path(repo)/'builtins/node-compat/zlib/kernel.cpp')]
 assert len(kernels)==int(metadata['zlibEnabled'])
 search=[kernel_headers(command,dist,selected)for command in kernels]
 raw=subprocess.check_output(['ninja','-C',str(build),'-t','commands','starlingmonkey_embedding'])
 (evidence_root/'link.after.commands.txt').write_bytes(raw)
 linked=link_commands(raw,build,current['archive']['path'])
 nm=Path(dist).parent/'cache/wasi-sdk/85e6/bin/llvm-nm'
 row(nm,NM_SHA)
 command=[str(nm),'--defined-only','--extern-only','--format=posix','--print-file-name',current['archive']['path']]
 child=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=55,check=True)
 (evidence_root/'nm.stdout.txt').write_bytes(child.stdout);(evidence_root/'nm.stderr.txt').write_bytes(child.stderr)
 selected_symbols=symbols(child.stdout)
 assert distribution(dist)==current and cache_install(build)==before_value['install']
 witnesses=[row(before_path),row(evidence_root/'link.after.commands.txt'),row(evidence_root/'nm.stdout.txt'),row(evidence_root/'nm.stderr.txt'),before_value['install'],*current['headers'],*linked['responseFiles']]
 return{'version':'sm-selected-moz-z-codec-source-link-witness-v1','selectedDistribution':str(Path(dist).absolute()),'selectedCompileInput':selected,'beforeManifestPath':str(Path(before_path).absolute()),'beforeManifestSha256':expected_before_sha,
  'archive':current['archive'],'archiveStorage':'External hash reference, rechecked; no duplicate archive copy or extent claim',
  'headers':current['headers'],'actualKernelCompileCommands':kernels,'actualHeaderSearchDirectories':search,
  'postBuildLinkEvidence':{**linked,'command':['ninja','-C',str(build),'-t','commands','starlingmonkey_embedding'],'path':str(evidence_root/'link.after.commands.txt'),'sha256':row(evidence_root/'link.after.commands.txt')['sha256'],'beforeBuildCaptureExists':False},
  'archiveSymbolEvidence':{'command':command,'nm':row(nm,NM_SHA),'selectedDefinitions':selected_symbols,'exitCode':child.returncode},
  'sourceInputsCheckedBeforeAndAfterBuild':True,'install':before_value['install'],'witnessFiles':witnesses,
  'runtimeBackendProof':{'verified':False,'version':None,'vernum':None},'guestExecuted':False}

def validate_before_manifest(value,before):
 assert before['schemaVersion']==1 and before['state']=='CODEC_INPUTS_AUTHENTICATED_BEFORE_NATIVE_BUILD'
 assert before['archive']==value['archive']and before['headers']==value['headers']and before['install']==value['install']
 assert len(value['headers'])==4 and {Path(header['path']).name for header in value['headers']}==set(HEADERS)
 assert len({header['path']for header in value['headers']})==4
 return True

def validate_witness(value,build,resolve_path=lambda path:path):
 """Authenticate original or frozen witnesses; metadata paths are never rewritten."""
 assert value['version']=='sm-selected-moz-z-codec-source-link-witness-v1'
 before_path=Path(resolve_path(Path(value['beforeManifestPath'])))
 row(before_path,value['beforeManifestSha256']);before_bytes=before_path.read_bytes()
 assert hashlib.sha256(before_bytes).hexdigest()==value['beforeManifestSha256'];before=json.loads(before_bytes)
 validate_before_manifest(value,before)
 selected=value['selectedCompileInput'];selection_contract(selected)
 assert selected['selectedDistribution']==value['selectedDistribution']and selected['archive']==value['archive']and selected['headers']==value['headers']
 archive=value['archive'];row(archive['path'],ARCHIVE_SHA,ARCHIVE_BYTES)
 assert archive['sha256']==ARCHIVE_SHA and archive['bytes']==ARCHIVE_BYTES
 for header in value['headers']:
  expected=HEADERS[Path(header['path']).name]
  assert(header['sha256'],header['bytes'])==expected
  row(resolve_path(Path(header['path'])),*expected)
 for witness in value['witnessFiles']:row(resolve_path(Path(witness['path'])),witness['sha256'],witness['bytes'])
 assert len({witness['path']for witness in value['witnessFiles']})==len(value['witnessFiles'])
 install=value['install'];row(resolve_path(Path(install['path'])),install['sha256'],install['bytes'])
 assert 'builtins::node_compat'in Path(resolve_path(Path(install['path']))).read_text()
 link=value['postBuildLinkEvidence'];assert link['beforeBuildCaptureExists']is False
 actual=link_commands(Path(resolve_path(Path(link['path']))).read_bytes(),build,archive['path'],resolve_path)
 assert actual['commands']==link['commands']and actual['responseFiles']==link['responseFiles']
 nm=next(w for w in value['witnessFiles']if Path(w['path']).name=='nm.stdout.txt')
 assert symbols(Path(resolve_path(Path(nm['path']))).read_bytes())==value['archiveSymbolEvidence']['selectedDefinitions']
 assert value['runtimeBackendProof']=={'verified':False,'version':None,'vernum':None}
 assert value['guestExecuted']is False and value['sourceInputsCheckedBeforeAndAfterBuild']is True
 return True

if __name__=='__main__':
 import sys
 assert len(sys.argv)==5 and sys.argv[1]=='before'
 print(json.dumps(before(*sys.argv[2:])))
