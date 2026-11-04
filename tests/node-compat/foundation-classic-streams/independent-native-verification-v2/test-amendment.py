"""Pure source/token checks for the embedding-only reader correction."""
from pathlib import Path
import importlib.util
import unittest
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('independent_reader_amended', HERE / 'verify.py')
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


class AmendmentChecks(unittest.TestCase):
    def test_native_still_requires_thin_lto(self):
        base = self.command('/not-executed/native.cpp')
        with self.assertRaises(AssertionError):
            reader.command_words(base, '/not-executed/native.cpp', False, False, False)
        reader.command_words(base + ' -flto=thin', '/not-executed/native.cpp', False, False, False)

    def test_embedding_does_not_require_thin_lto(self):
        reader.command_words(self.command('/not-executed/embedding/embedding.cpp'),
                             '/not-executed/embedding/embedding.cpp', False, False, False, require_thin_lto=False)

    def test_embedding_target_o3_and_macros_remain_required(self):
        command = self.command('/not-executed/embedding/embedding.cpp')
        for bad in (command.replace('--target=wasm32-wasi', ''), command.replace('-O3', '-O0'),
                    command + ' -DNODE_COMPAT_CLASSIC_STREAMS=1', command + ' -DNODE_COMPAT_GC_STRESS=1'):
            with self.subTest(command=bad), self.assertRaises(AssertionError):
                reader.command_words(bad, '/not-executed/embedding/embedding.cpp', False, False, False, require_thin_lto=False)

    def test_exact_three_source_substitutions(self):
        original = (HERE / 'history/attempt1/verify.py').read_text()
        expected = original.replace('def command_words(command, source, runtime, classic, gc):',
            'def command_words(command, source, runtime, classic, gc, require_thin_lto=True):')
        expected = expected.replace("    assert '-flto=thin' in words and '--target=wasm32-wasi' in words",
            "    assert '--target=wasm32-wasi' in words\n    if require_thin_lto:\n        assert '-flto=thin' in words")
        expected = expected.replace('    embedding_words = command_words(embedding[0], source, runtime, False, False)',
            '    embedding_words = command_words(embedding[0], source, runtime, False, False, require_thin_lto=False)')
        self.assertNotEqual(expected, original)
        self.assertEqual((HERE / 'verify.py').read_text(), expected)

    @staticmethod
    def command(source):
        return '/not-executed/clang++ --target=wasm32-wasi -O3 -DNDEBUG ' + ' '.join(
            '-D' + name + '=1' for name in ('NODE_COMPAT_INTERNAL_TICKS', 'NODE_COMPAT_STRICT_INITIALIZATION',
                'NODE_COMPAT_EVENTS_ADD_ABORT_LISTENER', 'NODE_COMPAT_ENTROPY_POLICY')) + ' -c ' + source + ' -o /not-executed/a.o'


if __name__ == '__main__':
    unittest.main()
