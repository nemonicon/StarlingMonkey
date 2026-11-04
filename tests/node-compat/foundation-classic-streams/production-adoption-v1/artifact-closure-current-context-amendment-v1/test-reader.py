"""Pure owned-text tests plus selected real archived descriptors; no owner code."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,sys,tempfile
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('owned_archive_context_reader',HERE/'archive-context-reader.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
Reader=module.ArchiveContextReader
sha=lambda raw:hashlib.sha256(raw).hexdigest()
checks=[]
def check(name,callback):callback();checks.append(name)
def reject(callback):
    try:callback()
    except(ValueError,OSError,TypeError):return
    raise AssertionError('Malformed context admitted')
def main():
    actual=json.loads((HERE/'actual-reader-fixtures.json').read_bytes())
    def actual_fixture():
        with Reader((HERE/'reader-fixtures/actual-selected').resolve(),actual['mapPath'],actual['mapSha256'])as reader:
            results=reader.verify_all();assert len(results)==9 and len(reader.contexts)==3
            assert all(not row['originalFilesystemOpened']for row in results)
            assert all(row['coverage']=='selected-rows'for row in reader.contexts.values())
    check('nineActualV8V11V12SelectedDescriptors',actual_fixture)
    with tempfile.TemporaryDirectory(prefix='archive-context-owned-')as temp:
        root=Path(temp).resolve();payload=b'old exact bytes\n';digest=sha(payload)
        (root/'data.bin').write_bytes(payload)
        original='/not-opened-or-required/original.txt'
        manifest={'inputs':[{'path':original,'sha256':digest,'bytes':len(payload)}]}
        def mapping():
            raw=json.dumps(manifest).encode();(root/'manifest.json').write_bytes(raw)
            return{'schemaVersion':1,'state':'EXPLICIT_ARCHIVE_CONTEXT_MAP_V1','contexts':[{'contextId':'fixture/old','format':'input-freeze-v1','coverage':'all-rows','manifest':{'originalPath':'/not-opened/original-manifest.json','archivePath':'manifest.json','sha256':sha(raw),'bytes':len(raw)},'rows':[{'manifestRows':[0],'originalPath':original,'expectedSha256':digest,'bytes':len(payload),'archivePath':'data.bin'}]}]}
        def with_map(value,callback):
            raw=json.dumps(value).encode();(root/'map.json').write_bytes(raw)
            with Reader(root,'map.json',sha(raw))as reader:return callback(reader)
        baseline=mapping()
        check('unavailableOriginalFilesystemNotNeeded',lambda:with_map(baseline,lambda reader:reader.verify('fixture/old',original,digest)))
        for label,key in[('unknownContext',('unknown',original,digest)),('unknownOriginal',('fixture/old','../not-mapped',digest)),('wrongExpectedHash',('fixture/old',original,'0'*64))]:
            check(label,lambda key=key:with_map(baseline,lambda reader:reject(lambda:reader.verify(*key))))
        bad=copy.deepcopy(baseline);bad['contexts'][0]['rows'][0]['archivePath']='../escape.txt'
        check('archiveTraversalRejected',lambda:reject(lambda:with_map(bad,lambda reader:reader.verify_all())))
        for label,path in[('absoluteArchivePath','/etc/passwd'),('noncanonicalArchivePath','a//b'),('backslashArchivePath','a\\b'),('dotArchivePath','./data.bin')]:
            bad_path=copy.deepcopy(baseline);bad_path['contexts'][0]['rows'][0]['archivePath']=path
            check(label,lambda value=bad_path:reject(lambda:with_map(value,lambda reader:reader.verify_all())))
        forged=copy.deepcopy(baseline);forged['contexts'][0]['rows'][0]['originalPath']='/forged'
        check('descriptorMustMatchManifest',lambda:reject(lambda:with_map(forged,lambda reader:reader.verify_all())))
        duplicate=copy.deepcopy(baseline);duplicate['contexts'].append(copy.deepcopy(duplicate['contexts'][0]))
        check('duplicateContextRejected',lambda:reject(lambda:with_map(duplicate,lambda reader:reader.verify_all())))
        bad_bool=copy.deepcopy(baseline);bad_bool['contexts'][0]['rows'][0]['bytes']=True
        check('booleanSizeRejected',lambda:reject(lambda:with_map(bad_bool,lambda reader:reader.verify_all())))
        check('wrongMapPinRejected',lambda:reject(lambda:Reader(root,'map.json','0'*64)))
        (root/'alias.bin').symlink_to('data.bin')
        linked=copy.deepcopy(baseline);linked['contexts'][0]['rows'][0]['archivePath']='alias.bin'
        check('fileSymlinkRejected',lambda:reject(lambda:with_map(linked,lambda reader:reader.verify_all())))
        (root/'real').mkdir();(root/'real/data.bin').write_bytes(payload);(root/'aliasdir').symlink_to('real',target_is_directory=True)
        linked_dir=copy.deepcopy(baseline);linked_dir['contexts'][0]['rows'][0]['archivePath']='aliasdir/data.bin'
        check('ancestorSymlinkRejected',lambda:reject(lambda:with_map(linked_dir,lambda reader:reader.verify_all())))
        (root/'alias-map.json').symlink_to('map.json')
        check('mapSymlinkRejected',lambda:reject(lambda:Reader(root,'alias-map.json',sha((root/'map.json').read_bytes()))))
        root_alias=root/'root-link';root_alias.symlink_to(root,target_is_directory=True)
        check('rootSymlinkRejected',lambda:reject(lambda:Reader(root_alias,'map.json',sha((root/'map.json').read_bytes()))))
        (root/'data.bin').write_bytes(b'X'+payload[1:])
        check('sameSizeUnequalBytesRejected',lambda:with_map(baseline,lambda reader:reject(reader.verify_all)))
        (root/'data.bin').write_bytes(payload)
        # Genuine M2 tuple: old37053-byte hash cannot resolve to the current
        # exclusive38330-byte snapshot. This is an actual-descriptor carrier,
        # not a claim that unavailable old README bytes were recovered.
        snapshot=json.loads((HERE/'mutable-status-snapshot.json').read_bytes())
        row=snapshot['files'][-1];current=(HERE/row['snapshotPath']).read_bytes()
        old_record={'path':row['originalPath'],'sha256':snapshot['oldAdoptionReadmeSha256'],'bytes':snapshot['oldAdoptionReadmeBytes']}
        raw=json.dumps({'inputs':[old_record]}).encode();(root/'manifest-m2.json').write_bytes(raw);(root/'current-readme.data').write_bytes(current)
        m2=copy.deepcopy(baseline);ctx=m2['contexts'][0];ctx['manifest'].update({'archivePath':'manifest-m2.json','sha256':sha(raw),'bytes':len(raw)})
        ctx['rows'][0].update({'originalPath':old_record['path'],'expectedSha256':old_record['sha256'],'bytes':old_record['bytes'],'archivePath':'current-readme.data'})
        check('actualOldREADMEHashNeverMapsToNewSnapshot',lambda:with_map(m2,lambda reader:reject(reader.verify_all)))
        manifest['inputs'].append(dict(manifest['inputs'][0],path='/second'))
        incomplete=mapping()
        check('allRowsCoverageCannotOmitRows',lambda:reject(lambda:with_map(incomplete,lambda reader:reader.verify_all())))
        duplicate_json=b'{"schemaVersion":1,"schemaVersion":1}'
        (root/'duplicate.json').write_bytes(duplicate_json)
        check('duplicateJSONFieldsRejected',lambda:reject(lambda:Reader(root,'duplicate.json',sha(duplicate_json))))
    for name in['archive-context-reader.py','test-reader.py']:ast.parse((HERE/name).read_bytes())
    checks.append('twoOwnedSourceASTParses')
    print(json.dumps({'schemaVersion':1,'state':'DATA_ONLY_ARCHIVE_CONTEXT_READER_TESTS_PASSED','checks':checks,'passed':len(checks),'actualSelectedDescriptors':9,'oldREADMEBytesRecovered':False,'originalFilesystemOpenedByReader':False,'ownerHelperNativeGuestHostOrTimingExecuted':False}))
if __name__=='__main__':main()
