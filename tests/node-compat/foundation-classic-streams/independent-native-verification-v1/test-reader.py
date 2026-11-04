"""Pure parser/anchor checks only; never reads a future engine or runs tools."""
from pathlib import Path
import ast
import importlib.util
import json
import tempfile
import unittest
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('independent_classic_reader', HERE / 'verify.py')
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


class ContractTests(unittest.TestCase):
    def test_source_has_no_producer_or_execution_import(self):
        tree = ast.parse((HERE / 'verify.py').read_text())
        names = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
        self.assertFalse(names & {'subprocess', 'artifact_common', 'ctypes', 'runpy', 'importlib'})

    def test_null_pins_refused(self):
        path = HERE / 'actual-pins.json'
        with self.assertRaisesRegex(AssertionError, 'not been reviewed'):
            reader.reviewed_pin(reader.Reader(), path, reader.digest(path.read_bytes()), 'normal-off')

    def test_unreviewed_producer_state_refused(self):
        with tempfile.TemporaryDirectory(prefix='classic-reader-owned-text-') as directory:
            path = Path(directory) / 'pins.json'
            path.write_text(json.dumps({'schemaVersion': 1, 'state': 'UNREVIEWED_CLASSIC_PRODUCTION_PIN_CANDIDATES_V1'}))
            with self.assertRaisesRegex(AssertionError, 'not been reviewed'):
                reader.reviewed_pin(reader.Reader(), path, reader.digest(path.read_bytes()), 'normal-off')

    def test_reviewed_shape_only(self):
        with tempfile.TemporaryDirectory(prefix='classic-reader-owned-text-') as directory:
            path = Path(directory) / 'pins.json'
            pin = {'engineSha256': '1' * 64, 'engineBytes': 100, 'metadataSha256': '2' * 64,
                   'freezeReceiptSha256': '3' * 64, 'launcherResultSha256': '4' * 64}
            document = {'schemaVersion': 1, 'state': 'REVIEWED_ACTUAL_CLASSIC_FREEZE_INPUTS_V1',
                        'variants': dict.fromkeys(reader.LABELS)}
            document['variants']['normal-off'] = pin
            path.write_text(json.dumps(document))
            self.assertEqual(reader.reviewed_pin(reader.Reader(), path, reader.digest(path.read_bytes()), 'normal-off'), pin)
            with self.assertRaisesRegex(AssertionError, 'still null'):
                reader.reviewed_pin(reader.Reader(), path, reader.digest(path.read_bytes()), 'gc-off')

    def test_relative_and_inventory(self):
        self.assertEqual(reader.inventory([{'path': 'runtime/file.cpp', 'sha256': '1' * 64}], 1), {'runtime/file.cpp': '1' * 64})
        for name in ('../file', '/file', 'a//b', 'a/./b', 'a\\b', 'a\0b'):
            with self.subTest(name=name), self.assertRaises(AssertionError):
                reader.relative(name)
        with self.assertRaises(AssertionError):
            reader.inventory([{'path': 'a', 'sha256': '1' * 64}] * 2)

    def test_macro_finite_exact(self):
        reader.macro(['-DFLAG=1'], 'FLAG', True)
        reader.macro([], 'FLAG', False)
        for words, enabled in [(['-DFLAG=0'], True), (['-DFLAG'], True),
                               (['-DFLAG=1', '-DFLAG=1'], True), (['-DFLAG=1'], False),
                               (['-DFLAG=1', '-UFLAG'], True), (['-D', 'FLAG=1'], True)]:
            with self.subTest(words=words), self.assertRaises(AssertionError):
                reader.macro(words, 'FLAG', enabled)

    def test_real_command_contract_variants(self):
        base = '/not-executed/clang++ --target=wasm32-wasi -O3 -DNDEBUG -flto=thin '
        base += ' '.join('-D' + name + '=1' for name in ('NODE_COMPAT_INTERNAL_TICKS', 'NODE_COMPAT_STRICT_INITIALIZATION', 'NODE_COMPAT_EVENTS_ADD_ABORT_LISTENER', 'NODE_COMPAT_ENTROPY_POLICY'))
        for runtime, classic, gc in ((False, True, False), (True, True, False), (False, True, True), (False, False, False)):
            command = base
            for name, enabled in [('NODE_COMPAT_ENTROPY_RUNTIME_ONLY', runtime), ('NODE_COMPAT_CLASSIC_STREAMS', classic), ('NODE_COMPAT_GC_STRESS', gc)]:
                if enabled:
                    command += ' -D' + name + '=1'
            command += ' -c /not-executed/source.cpp -o /not-executed/output.o'
            reader.command_words(command, '/not-executed/source.cpp', runtime, classic, gc)
            for bad in (command + ' -fsyntax-only', command + ' -DNODE_COMPAT_OOM_TESTING=1', command + ' -DDEBUG=1', command.replace('-O3', '-O0')):
                with self.subTest(command=bad), self.assertRaises(AssertionError):
                    reader.command_words(bad, '/not-executed/source.cpp', runtime, classic, gc)


if __name__ == '__main__':
    unittest.main()
