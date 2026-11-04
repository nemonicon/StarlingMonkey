"""Fixed-index/source verification only. Never invokes a native/guest action."""
import argparse,hashlib,importlib.util,json
from pathlib import Path
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def checked(path,expected):
 path=Path(path);assert path.is_file()and not path.is_symlink()and sha(path)==expected,str(path)
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--index-sha256',required=True);parser.add_argument('--source-root',type=Path);args=parser.parse_args()
 checked(HERE/'index.json',args.index_sha256);index=json.loads((HERE/'index.json').read_bytes())
 for row in index['files']:checked(HERE/row['path'],row['sha256']);assert(HERE/row['path']).stat().st_size==row['bytes']
 policy=json.loads((HERE/'policy.json').read_bytes());assert len(policy['expectedNativeSourceManifest'])==350
 if args.source_root:
  root=args.source_root.resolve(strict=True)
  spec=importlib.util.spec_from_file_location('verified_bounded_zlib_source_layer',HERE/'layer-policy.py');layer=importlib.util.module_from_spec(spec);spec.loader.exec_module(layer)
  layer.validate_sources(root)
  tools=json.loads((HERE/'artifact-tools/tool-pins.json').read_bytes())
  for row in tools['toolDependencies']:checked(root/row['path'],row['sha256']);assert(root/row['path']).stat().st_size==row['bytes']
 print(json.dumps({'state':'REVIEWED_SOURCE_INDEX_AND_OPTIONAL350_ROOT_VERIFIED','indexedFiles':len(index['files']),'nativeSourcePaths':350,'sourceRootVerified':str(args.source_root)if args.source_root else None,'nativeOrGuestOrCompilerExecuted':False}))
if __name__=='__main__':main()
