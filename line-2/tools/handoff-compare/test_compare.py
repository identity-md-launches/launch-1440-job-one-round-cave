#!/usr/bin/env python3
"""Offline behavior checks; generated archives stay in scratch or memory."""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
import zipfile

spec = importlib.util.spec_from_file_location('comparison',
    'line-2/tools/handoff-compare/compare_handoff.py')
comparison = importlib.util.module_from_spec(spec)
spec.loader.exec_module(comparison)
producer = comparison.load_workspace_module('comparison_tests_producer',
    'line-2/tools/handoff/handoff.py')
check = comparison.inspector()


def receipt(files):
    return check.inspect_stream(io.BytesIO(producer.build(files)))


class Comparisons(unittest.TestCase):
    def setUp(self):
        self.before = {'keep.txt': b'stable', 'edit.txt': b'old', 'gone.txt': b'bye'}
        self.after = {'keep.txt': b'stable', 'edit.txt': b'new', 'added.txt': b'hello'}

    def test_all_four_categories(self):
        report = comparison.compare_receipts(receipt(self.before), receipt(self.after))
        self.assertEqual(report['counts'], dict(added=1, removed=1, modified=1, unchanged=1))
        self.assertEqual(report['modified'][0]['before']['bytes'], 3)
        self.assertNotEqual(report['modified'][0]['before']['sha256'],
                            report['modified'][0]['after']['sha256'])
        self.assertEqual(report['payload_byte_delta'], 2)
        self.assertFalse(report['same_payload'])

    def test_same_archive(self):
        result = comparison.compare_receipts(receipt(self.before), receipt(self.before))
        self.assertTrue(result['same_payload'])
        self.assertTrue(result['same_archive'])

    def test_same_payload_different_zip_metadata(self):
        first = producer.build(self.before)
        target = io.BytesIO()
        with zipfile.ZipFile(io.BytesIO(first)) as source, zipfile.ZipFile(target, 'w') as output:
            for info in source.infolist():
                info.date_time = (2001, 2, 3, 4, 5, 6)
                output.writestr(info, source.read(info.filename))
        result = comparison.compare_receipts(check.inspect_stream(io.BytesIO(first)),
                    check.inspect_stream(io.BytesIO(target.getvalue())))
        self.assertTrue(result['same_payload'])
        self.assertFalse(result['same_archive'])

    def test_rename_is_remove_add(self):
        result = comparison.compare_receipts(receipt({'a': b'x'}), receipt({'b': b'x'}))
        self.assertEqual(result['counts'], dict(added=1, removed=1, modified=0, unchanged=0))

    def test_deterministic_sorted_report(self):
        a = comparison.compare_receipts(receipt(self.before), receipt(self.after))
        b = comparison.compare_receipts(receipt(dict(reversed(list(self.before.items())))),
                                        receipt(dict(reversed(list(self.after.items())))))
        self.assertEqual(a, b)
        for key in ('added', 'removed', 'modified'):
            self.assertEqual([item['path'] for item in a[key]],
                             sorted(item['path'] for item in a[key]))

    def test_unicode_and_empty_files(self):
        result = comparison.compare_receipts(receipt({'é/a': b''}), receipt({'é/a': b'x'}))
        self.assertEqual(result['modified'][0]['path'], 'é/a')
        self.assertEqual(result['payload_byte_delta'], 1)

    def test_real_source_demo(self):
        result = comparison.demo()
        self.assertEqual(result['counts'], dict(added=1, removed=0, modified=0, unchanged=2))

    def test_real_archive_interoperability(self):
        result = comparison.compare_paths('line-2/handoff.zip', 'line-2/handoff-inspect.zip')
        self.assertTrue(result['verified'])
        self.assertGreater(result['before']['file_count'], 0)
        self.assertGreater(result['after']['file_count'], 0)

    def test_trusted_digest(self):
        data = Path('line-2/handoff.zip').read_bytes()
        expected = hashlib.sha256(data).hexdigest()
        result = comparison.compare_paths('line-2/handoff.zip', 'line-2/handoff.zip',
                                           expected, expected.upper())
        self.assertTrue(result['before']['trusted_digest_matched'])
        self.assertTrue(result['after']['trusted_digest_matched'])

    def test_wrong_digest(self):
        with self.assertRaisesRegex(ValueError, 'trusted digest'):
            comparison.compare_paths('line-2/handoff.zip', 'line-2/handoff.zip',
                                     after_sha256='f' * 64)

    def test_invalid_digest(self):
        with self.assertRaisesRegex(ValueError, '64 hexadecimal'):
            comparison.compare_paths('line-2/handoff.zip', 'line-2/handoff.zip',
                                     before_sha256='no')

    def test_workspace_path_guard(self):
        for path in ('../elsewhere.zip', '/tmp/elsewhere.zip'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                comparison.compare_paths(path, 'line-2/handoff.zip')

    def test_budget(self):
        with self.assertRaisesRegex(ValueError, 'size limit'):
            comparison.compare_paths('line-2/handoff.zip', 'line-2/handoff.zip',
                                     limits=check.Limits(archive_bytes=1))

    def test_tampering_with_valid_crc_is_rejected(self):
        target = io.BytesIO()
        with zipfile.ZipFile(io.BytesIO(producer.build(self.before))) as source, \
                zipfile.ZipFile(target, 'w') as output:
            for info in source.infolist():
                content = source.read(info.filename)
                output.writestr(info, b'NEW' if info.filename == 'edit.txt' else content)
        with self.assertRaisesRegex(ValueError, 'integrity mismatch'):
            check.inspect_stream(io.BytesIO(target.getvalue()))

    def test_cli_no_report_on_invalid_second_archive(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = comparison.main(['compare', 'line-2/handoff.zip',
                                    'line-2/tools/handoff/README.md'])
        self.assertEqual(code, 1)
        self.assertEqual(out.getvalue(), '')
        self.assertIn('handoff-compare:', err.getvalue())

    def test_cli_same_payload_exit_zero(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = comparison.main(['compare', 'line-2/handoff.zip', 'line-2/handoff.zip',
                                    '--fail-on-change'])
        self.assertEqual(code, 0)
        self.assertTrue(json.loads(out.getvalue())['same_payload'])

    def test_cli_changed_payload_exit_two(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = comparison.main(['compare', 'line-2/handoff.zip',
                                    'line-2/handoff-inspect.zip', '--fail-on-change'])
        self.assertEqual(code, 2)
        self.assertFalse(json.loads(out.getvalue())['same_payload'])

    def test_symlink_refused(self):
        directory = Path('test/scratch/handoff-compare')
        directory.mkdir(parents=True, exist_ok=True)
        link = directory / 'link.zip'
        if link.is_symlink():
            link.unlink()
        link.symlink_to('../../../line-2/handoff.zip')
        try:
            with self.assertRaisesRegex(ValueError, 'symlinks'):
                comparison.compare_paths(str(link), 'line-2/handoff.zip')
        finally:
            link.unlink()

    def test_cli_subprocess(self):
        run = subprocess.run([sys.executable, '-B',
            'line-2/tools/handoff-compare/compare_handoff.py', 'demo'],
            capture_output=True, text=True, check=True)
        self.assertTrue(json.loads(run.stdout)['verified'])
        self.assertEqual(run.stderr, '')


if __name__ == '__main__':
    unittest.main(verbosity=2)
