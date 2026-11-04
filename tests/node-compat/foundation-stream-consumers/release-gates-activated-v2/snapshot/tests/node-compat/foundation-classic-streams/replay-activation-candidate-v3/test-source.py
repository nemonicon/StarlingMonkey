"""Source/owned-text checks only. Never calls activation main or a JS function."""
from pathlib import Path
import ast
import copy
import json
import sys
import tempfile
import unittest
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import authority
import activate

ROOT_DATA = HERE.parent / 'production-adoption-v1'
PIN_BYTES = authority.regular(ROOT_DATA / 'reviewed-runtime-pins-v1.json', authority.PINS_SHA)
REVIEW_BYTES = authority.regular(ROOT_DATA / 'root-pin-review-receipt.json', authority.REVIEW_SHA)


class SourceTests(unittest.TestCase):
    def test_actual_root_authority_data(self):
        pins, review = authority.validate_authority(PIN_BYTES, REVIEW_BYTES)
        self.assertEqual(len(pins['variants']), 4)
        self.assertFalse(review['runtimeAcceptanceClaim'])

    def test_authority_digest_before_json(self):
        with self.assertRaises(AssertionError):
            authority.validate_authority(b'NOT JSON: MUST NOT PARSE', REVIEW_BYTES)
        with self.assertRaises(AssertionError):
            authority.validate_authority(PIN_BYTES, b'NOT JSON: MUST NOT PARSE')

    def test_future_runtime_receipt_shape_and_same_tuples(self):
        pins, review = authority.validate_authority(PIN_BYTES, REVIEW_BYTES)
        index = {'schemaVersion': 1, 'state': 'ACTUAL_REVIEWED_CLASSIC_RUNTIME_SOURCE_FAMILY_NOT_EXECUTED', 'runtimeAcceptanceClaim': False,
            'files': [{'path': name} for name in ['runtime-preflight.mjs', 'runtime-pins.json', 'root-review-receipt.json', 'input-freeze.json', 'source-receipt.json']]}
        receipt = {'schemaVersion': 1, 'state': 'ACTUAL_REVIEWED_CLASSIC_RUNTIME_FAMILY_CREATED_NOT_EXECUTED',
            'pinsSha256': authority.PINS_SHA, 'rootReviewSha256': authority.REVIEW_SHA, 'recipeSha256': authority.RECIPE,
            'engineMetadataRewritten': False, 'componentOrHostExecuted': False, 'runtimeAcceptanceClaim': False,
            'actualArtifacts': {label: {name: pins['variants'][label][name] for name in
                ('engineSha256', 'engineBytes', 'receiptSha256', 'freezeReceiptSha256')} for label in authority.LABELS}}
        self.assertTrue(authority.validate_runtime_receipt(index, receipt, pins, review))
        for change in ('tuple', 'rewritten', 'runtimeAccepted', 'wrongIndexState'):
            i, r = copy.deepcopy(index), copy.deepcopy(receipt)
            if change == 'tuple': r['actualArtifacts']['gc-off']['engineSha256'] = '0' * 64
            if change == 'rewritten': r['engineMetadataRewritten'] = True
            if change == 'runtimeAccepted': r['runtimeAcceptanceClaim'] = True
            if change == 'wrongIndexState': i['state'] = 'UNREVIEWED'
            with self.subTest(change=change), self.assertRaises(AssertionError):
                authority.validate_runtime_receipt(i, r, pins, review)

    def test_index_hash_before_following_rows(self):
        with tempfile.TemporaryDirectory(prefix='classic-replay-owned-source-test-') as directory:
            root = Path(directory)
            raw = b'{"schemaVersion":1,"files":[]}\n'
            (root / 'index.json').write_bytes(raw)
            authority.indexed(root, authority.sha(raw))
            (root / 'index.json').write_text('{"schemaVersion":1,"files":[{"path":"MUST_NOT_FOLLOW"}]}')
            with self.assertRaisesRegex(AssertionError, 'before JSON parsing'):
                authority.indexed(root, authority.sha(raw))

    def test_index_traversal_and_duplicate_refused(self):
        with tempfile.TemporaryDirectory(prefix='classic-replay-owned-source-test-') as directory:
            root = Path(directory)
            for names in (['../MUST_NOT_FOLLOW'], ['duplicate', 'duplicate']):
                raw = (json.dumps({'schemaVersion': 1, 'files': [{'path': name, 'sha256': '1' * 64, 'bytes': 1} for name in names]}) + '\n').encode()
                (root / 'index.json').write_bytes(raw)
                with self.subTest(names=names), self.assertRaises(AssertionError):
                    authority.indexed(root, authority.sha(raw))

    def test_57_of64_bodies_identical_with_seven_exact_host_amendments(self):
        self.assertFalse(activate.OUTPUT.exists())
        index, _ = authority.indexed(activate.PARENT, activate.PARENT_INDEX)
        payload, records = activate.base_payload(index, PIN_BYTES, REVIEW_BYTES, '1' * 64,
            ROOT_DATA / 'reviewed-runtime-pins-v1.json', ROOT_DATA / 'root-pin-review-receipt.json', activate.HERE.parent / 'production-runtime-activated-v2')
        self.assertEqual(len(records), 64)
        for row in records:
            self.assertEqual(authority.sha(payload[row['destinationPath']]),activate.expected_body_hash(row))
        changed=[row['destinationPath']for row in records if payload[row['destinationPath']]!=(activate.PARENT/row['destinationPath']).read_bytes()]
        self.assertEqual(set(changed),set(activate.amendment_images()))
        self.assertEqual(len(changed),7)
        self.assertEqual(len(records)-len(changed),57)
        self.assertIsNone(json.loads(payload['capability/http-component-pins.json'])['component'])
        self.assertNotIn('native-preflight.mjs', payload)
        self.assertIn('native-preflight.template.mjs', payload)
        self.assertFalse(activate.OUTPUT.exists())

    def test_changed_amendment_afterimage_refused_from_owned_tree(self):
        with tempfile.TemporaryDirectory(prefix='classic-amendment-owned-') as directory:
            import shutil
            root=Path(directory)
            shutil.copytree(activate.AMENDMENT,root/'copy')
            original=activate.AMENDMENT
            try:
                activate.AMENDMENT=root/'copy'
                path=activate.AMENDMENT/'proposed/release/runners/path.mjs'
                path.write_bytes(path.read_bytes()+b'\n')
                with self.assertRaises(AssertionError):activate.amendment_images()
            finally:activate.AMENDMENT=original

    def test_mandatory_amendment_and_null_http_contract(self):
        text=(HERE/'activate.py').read_text()
        self.assertIn('indexed(AMENDMENT,AMENDMENT_INDEX)',text)
        self.assertIn('external_file(path,row[\'sha256\'])',text)
        self.assertIn('production-runtime-activated-v3',activate.RUNTIME_NAMES)
        self.assertEqual(activate.OUTPUT.name,'production-regression-activated-v3')
        self.assertFalse(activate.OUTPUT.exists())

    def test_changed_exact_policy_afterimage_refused_from_owned_tree(self):
        with tempfile.TemporaryDirectory(prefix='classic-policy-owned-') as directory:
            import shutil
            root=Path(directory)
            shutil.copytree(activate.POLICY_AMENDMENT,root/'copy')
            original=activate.POLICY_AMENDMENT
            try:
                activate.POLICY_AMENDMENT=root/'copy'
                path=activate.POLICY_AMENDMENT/'proposed/release/runners/events.mjs'
                path.write_bytes(path.read_bytes()+b'\n')
                with self.assertRaises(AssertionError):activate.amendment_images()
            finally:activate.POLICY_AMENDMENT=original

    def test_all64_audit_and_policy_index_are_mandatory(self):
        document=json.loads((activate.POLICY_AMENDMENT/'all64-source-audit.json').read_bytes())
        self.assertEqual(document['bodiesReviewed'],64)
        self.assertEqual(document['oldBodiesByteIdentical'],57)
        self.assertEqual(set(document['changedHostHarnessBodies']),set(activate.amendment_images()))
        text=(HERE/'activate.py').read_text()
        self.assertIn('indexed(POLICY_AMENDMENT,POLICY_AMENDMENT_INDEX)',text)
        self.assertIn('for amendment in [AMENDMENT,POLICY_AMENDMENT]:',text)
        self.assertIn('expected_body_hash(row)',text)

    def test_fixed_index_before_dynamic_import_and_no_native_backend(self):
        text = (HERE / 'native-preflight.template.mjs').read_text()
        self.assertLess(text.index('const index=await indexedRuntime(),pins=await authority(index)'), text.index('await import(pathToFileURL'))
        self.assertIn('const native=await preflight({variant})', text)
        self.assertIn('await nativeRecheck();const index=await indexedRuntime();await authority(index);await ownSeal()', text)
        for forbidden in ('selectedManifestsForEngine', 'cmakeCachePath', 'compileCommandsSha256', 'sourceManifest.length', 'syntheticMetadataOnly='):
            self.assertNotIn(forbidden, text)
        self.assertLess(text.index("const raw=await regular(join(HERE,'input-freeze.json'),INPUTS_SHA)"), text.index('for(const row of document.inputs)'))

    def test_pure_python_modules_do_not_import_tools_or_runners(self):
        for name in ('authority.py', 'activate.py'):
            tree = ast.parse((HERE / name).read_text())
            modules = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
            self.assertFalse(modules & {'subprocess', 'ctypes', 'artifact_common', 'importlib'})

    def test_all_source_placeholders_bound_only_in_memory(self):
        text = (HERE / 'native-preflight.template.mjs').read_text()
        for name in ('AUTHORITY_SHA', 'INPUTS_SHA', 'RUNTIME_INDEX_SHA'):
            self.assertEqual(text.count('@' + name + '@'), 1)
            text = text.replace('@' + name + '@', '1' * 64)
        self.assertEqual(text.count('@RUNTIME_FAMILY@'), 1)
        text = text.replace('@RUNTIME_FAMILY@', 'production-runtime-activated-v2')
        self.assertNotIn('@AUTHORITY_SHA@', text)
        self.assertFalse(activate.OUTPUT.exists())

    def test_explicit_finite_runtime_index_paths(self):
        for name in activate.RUNTIME_NAMES:
            path = activate.HERE.parent / name / 'index.json'
            self.assertEqual(activate.runtime_root(path), path.parent)
        for path in (activate.HERE.parent / 'UNREVIEWED/index.json', Path('/tmp/other/index.json'),
                     activate.HERE.parent / 'production-runtime-activated-v2/not-index.json'):
            with self.subTest(path=path), self.assertRaises(AssertionError):
                activate.runtime_root(path)


if __name__ == '__main__':
    unittest.main()
