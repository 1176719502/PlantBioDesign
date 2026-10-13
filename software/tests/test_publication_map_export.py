"""Map transport regression using an externally supplied real ALB backup."""
import ast
import builtins
import copy
import json
import os
from pathlib import Path
import re
import unittest
import tempfile
from typing import Any, Mapping
from unittest.mock import patch
from io import BytesIO

from services import publication_map_product as product
from services.publication_map_contract import PublicationMapContractError, PublicationMapViewType


class RecordingUI:
    def __init__(self):
        self.downloads = []
        self.warnings = []
        self.errors = []
    def columns(self, count):
        return [self] * count
    def expander(self, *args, **kwargs):
        return self
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def download_button(self, label, **kwargs):
        self.downloads.append(kwargs)
    def error(self, message):
        self.errors.append(message)
    def warning(self, message):
        self.warnings.append(message)
    def __getattr__(self, name):
        return lambda *args, **kwargs: None


def delivery(ui):
    path = Path(__file__).resolve().parents[1] / 'app.py'
    node = next(n for n in ast.parse(path.read_text('utf-8')).body
                if isinstance(n, ast.FunctionDef) and n.name == '_render_publication_map_svg')
    namespace = {'Mapping': Mapping, 'Any': Any, 'st': ui, 'components': ui, 're': re,
                 '_t': lambda key, **kwargs: f'{key} {kwargs}'}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), 'exec'), namespace)
    return namespace['_render_publication_map_svg']


@unittest.skipUnless(os.environ.get('PLANTBIODESIGN_REPORT_TEST_PROJECT'), 'Real backup required')
class PublicationMapExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project = json.loads(Path(os.environ['PLANTBIODESIGN_REPORT_TEST_PROJECT']).read_text('utf-8'))
        cls.view = PublicationMapViewType.COMPLETE_CIRCULAR_PLASMID
        cls.base = product.build_publication_map_svg_artifact(cls.project['runtime'], view_type=cls.view)

    def render(self, runtime=None):
        ui = RecordingUI()
        ok = delivery(ui)({'runtime': self.project['runtime'] if runtime is None else runtime},
                          view_type=self.view.value, display_name='', download_key='test-map')
        return ui, ok

    def test_missing_engine_keeps_exact_svg(self):
        product._build_publication_map_converted_exports.cache_clear()
        with patch.object(product, '_publication_map_svg_engine', side_effect=product.PublicationMapExportError('Microsoft Edge SVG engine missing', code='engine_missing')):
            ui, ok = self.render()
        self.assertTrue(ok)
        self.assertEqual(ui.downloads[0]['data'], self.base.svg_bytes)
        self.assertFalse(ui.downloads[0].get('disabled', False))
        self.assertTrue(all(d['disabled'] for d in ui.downloads[1:]))
        self.assertIn('Edge', ui.warnings[0])

    def test_conversion_failure_keeps_svg(self):
        with patch.object(product, '_build_publication_map_converted_exports', side_effect=OSError('conversion failed')):
            ui, ok = self.render()
        self.assertTrue(ok)
        self.assertEqual(ui.downloads[0]['data'], self.base.svg_bytes)
        self.assertTrue(all(d['disabled'] for d in ui.downloads[1:]))
        self.assertIn('file or device error', ui.warnings[0])

    def test_missing_pillow_keeps_svg(self):
        original = builtins.__import__
        def missing(name, *args, **kwargs):
            if name == 'PIL' or name.startswith('PIL.'):
                raise ModuleNotFoundError("No module named 'PIL'", name='PIL')
            return original(name, *args, **kwargs)
        product._build_publication_map_converted_exports.cache_clear()
        with patch('builtins.__import__', side_effect=missing):
            ui, ok = self.render()
        self.assertTrue(ok)
        self.assertEqual(ui.downloads[0]['data'], self.base.svg_bytes)
        self.assertTrue(any('dependency' in warning for warning in ui.warnings))

    def test_conversion_receives_preview_svg(self):
        with patch.object(product, '_build_publication_map_converted_exports', return_value=product.PublicationMapConversionResult(b'%PDF-test', b'PNG-test')) as convert:
            ui, ok = self.render()
        self.assertTrue(ok)
        self.assertEqual(convert.call_args.args[0], ui.downloads[0]['data'])
        self.assertEqual(convert.call_args.kwargs['sequence_checksum'], self.base.sequence_checksum)
        self.assertTrue(all(not d.get('disabled', False) for d in ui.downloads))

    def _render_result(self, *, pdf=b'%PDF-valid', png=b'PNG-valid', pdf_issue=None, png_issue=None):
        converted = product.PublicationMapConversionResult(pdf, png, pdf_issue, png_issue)
        with patch.object(product, '_build_publication_map_converted_exports', return_value=converted):
            return self.render()

    def test_all_formats_valid(self):
        ui, ok = self._render_result()
        self.assertTrue(ok)
        self.assertEqual([d.get('disabled', False) for d in ui.downloads], [False, False, False])

    def test_pdf_failure_keeps_png_and_svg(self):
        issue = product.PublicationMapExportIssue('pdf', 'pdf_structure_invalid', 'PDF conversion produced a damaged or incomplete PDF.', 'PdfStreamError')
        ui, ok = self._render_result(pdf=None, pdf_issue=issue)
        self.assertTrue(ok)
        self.assertEqual([d.get('disabled', False) for d in ui.downloads], [False, True, False])
        self.assertEqual(ui.downloads[2]['data'], b'PNG-valid')
        self.assertIn('PDF', ui.warnings[0])

    def test_png_failure_keeps_pdf_and_svg(self):
        issue = product.PublicationMapExportIssue('png', 'png_content_invalid', 'PNG conversion produced a damaged or incomplete PNG.', 'UnidentifiedImageError')
        ui, ok = self._render_result(png=None, png_issue=issue)
        self.assertTrue(ok)
        self.assertEqual([d.get('disabled', False) for d in ui.downloads], [False, False, True])
        self.assertEqual(ui.downloads[1]['data'], b'%PDF-valid')

    def test_both_conversion_failures_keep_svg_only(self):
        pdf_issue = product.PublicationMapExportIssue('pdf', 'engine_failed', 'Conversion engine failed (exit code 23).', 'stderr=Access denied')
        png_issue = product.PublicationMapExportIssue('png', 'engine_failed', 'Conversion engine failed (exit code 23).', 'stderr=Access denied')
        ui, ok = self._render_result(pdf=None, png=None, pdf_issue=pdf_issue, png_issue=png_issue)
        self.assertTrue(ok)
        self.assertEqual([d.get('disabled', False) for d in ui.downloads], [False, True, True])
        self.assertEqual(ui.downloads[0]['data'], self.base.svg_bytes)

    def test_corrupt_pdf_is_rejected_by_structure_parser(self):
        with self.assertRaisesRegex(product.PublicationMapExportError, 'damaged'):
            product._validate_pdf_payload(b'%PDF-1.7\n' + b'x' * 1200)

    def test_corrupt_png_is_rejected_by_content_parser(self):
        with self.assertRaisesRegex(product.PublicationMapExportError, 'damaged'):
            path = Path(self.id().replace('.', '_') + '.png')
            try:
                path.write_bytes(b'not-a-png')
                product._validate_png_payload(path, expected_size=(3000, 2000))
            finally:
                path.unlink(missing_ok=True)

    def test_engine_failure_retains_status_and_stderr_diagnostics(self):
        completed = product.subprocess.CompletedProcess(['edge'], 23, b'', b'Access denied to output directory')
        with patch.object(product.subprocess, 'run', return_value=completed):
            with self.assertRaises(product.PublicationMapExportError) as caught:
                product._run_svg_engine(Path('edge'), profile_directory=Path('profile'), arguments=[])
        self.assertEqual(caught.exception.code, 'engine_failed')
        self.assertIn('23', caught.exception.diagnostic)
        self.assertIn('stderr=[REDACTED]', caught.exception.diagnostic)
        self.assertEqual(caught.exception.public_message, 'Conversion engine failed.')

    def test_missing_parser_disables_only_pdf(self):
        issue = product.PublicationMapExportIssue('pdf', 'pdf_parser_missing', 'PDF validation is unavailable because the PDF parser is not installed.', 'ModuleNotFoundError')
        ui, ok = self._render_result(pdf=None, pdf_issue=issue)
        self.assertTrue(ok)
        self.assertEqual([d.get('disabled', False) for d in ui.downloads], [False, True, False])

    def test_cleanup_retry_does_not_discard_payloads(self):
        path = Path(self.id().replace('.', '_') + '_temp')
        path.mkdir(exist_ok=True)
        try:
            original = product.shutil.rmtree
            calls = {'count': 0}
            def flaky(target):
                calls['count'] += 1
                if calls['count'] == 1:
                    raise PermissionError(32, 'locked')
                return original(target)
            with patch.object(product.shutil, 'rmtree', side_effect=flaky):
                product._record_temp_cleanup_state(path)
                self.assertIn(path, product._PENDING_TEMP_DIRECTORIES)
                product._retry_pending_temp_cleanup()
            self.assertFalse(path.exists())
        finally:
            if path.exists():
                original(path)

    def test_stale_or_corrupt_runtime_blocks_all_downloads(self):
        for field, value in (('input_signature', 'stale-input'), ('sequence_checksum', '0' * 64)):
            runtime = copy.deepcopy(self.project['runtime'])
            plasmid = next(p for p in runtime['complete_plasmid_constructs']
                           if p['plasmid_id'] == runtime['active_complete_plasmid_id'])
            plasmid[field] = value
            ui, ok = self.render(runtime)
            self.assertFalse(ok)
            self.assertFalse(ui.downloads)
            self.assertTrue(ui.errors)

    def test_conversion_rejects_mismatched_svg_identity(self):
        product._build_publication_map_converted_exports.cache_clear()
        with self.assertRaisesRegex(PublicationMapContractError, 'identity'):
            product._build_publication_map_converted_exports(
                self.base.svg_bytes, title='map', construct_identifier='wrong-project',
                revision_id=self.base.revision_id, sequence_checksum=self.base.sequence_checksum)


@unittest.skipUnless(os.environ.get('PLANTBIODESIGN_REPORT_TEST_PROJECT'), 'Real backup required')
class PublicationMapEngineBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project = json.loads(Path(os.environ['PLANTBIODESIGN_REPORT_TEST_PROJECT']).read_text('utf-8'))
        cls.base = product.build_publication_map_svg_artifact(cls.project['runtime'], view_type=PublicationMapViewType.COMPLETE_CIRCULAR_PLASMID)
        cls.valid = product.convert_publication_map_svg_artifact(cls.base)
        assert cls.valid.pdf_bytes and cls.valid.png_bytes, cls.valid

    def setUp(self):
        product._build_publication_map_converted_exports.cache_clear()

    def injected(self, pdf_mode='valid', png_mode='valid'):
        def engine(_, *, profile_directory, arguments):
            for arg in arguments:
                if arg.startswith('--print-to-pdf=') or arg.startswith('--screenshot='):
                    is_pdf = arg.startswith('--print-to-pdf=')
                    mode = pdf_mode if is_pdf else png_mode
                    path = Path(arg.split('=', 1)[1])
                    if mode == 'fail':
                        raise PermissionError(13, 'Access denied: C:\\private\\machine\\output')
                    data = self.valid.pdf_bytes if is_pdf else self.valid.png_bytes
                    if mode == 'corrupt':
                        data = b'%PDF-1.7\n' + b'x' * 1200 if is_pdf else b'\x89PNG\r\n\x1a\n' + b'x' * 1200
                    if mode == 'truncated':
                        data = data[:-200]
                    path.write_bytes(data)
        with patch.object(product, '_run_svg_engine', side_effect=engine):
            artifact = product.convert_publication_map_svg_artifact(self.base)
        return artifact

    def test_real_normal_conversion_validates_both(self):
        artifact = product.convert_publication_map_svg_artifact(self.base)
        self.assertIsNone(artifact.pdf_issue)
        self.assertIsNone(artifact.png_issue)
        self.assertEqual(product._validate_pdf_payload(artifact.pdf_bytes), artifact.pdf_bytes)

    def test_broken_xref_with_valid_signature_and_eof_is_rejected(self):
        for damaged in (re.sub(rb'startxref\s+\d+', b'startxref\n1', self.valid.pdf_bytes),
                        self.valid.pdf_bytes.replace(b'\nxref\n', b'\nxxxx\n', 1)):
            self.assertTrue(damaged.startswith(b'%PDF-'))
            self.assertTrue(damaged.rstrip().endswith(b'%%EOF'))
            with self.assertRaises(product.PublicationMapExportError) as caught:
                product._validate_pdf_payload(damaged)
            self.assertEqual(caught.exception.code, 'pdf_structure_invalid')

    def test_shared_engine_failure_preserves_log_diagnostic_identity(self):
        with patch.object(product, '_publication_map_svg_engine', side_effect=product.PublicationMapExportError('Edge missing', code='engine_missing')):
            with self.assertLogs(product._LOGGER, level='ERROR') as logs:
                artifact = product.convert_publication_map_svg_artifact(self.base)
        self.assertEqual(artifact.pdf_issue.diagnostic_id, artifact.png_issue.diagnostic_id)
        self.assertIn(artifact.pdf_issue.diagnostic_id, logs.output[0])

    def test_setup_failure_is_registered_for_managed_cleanup(self):
        holder = {}
        class RecordedDirectory(tempfile.TemporaryDirectory):
            def __enter__(self):
                name = super().__enter__()
                holder['path'] = Path(name)
                return name
        with patch.object(product, 'TemporaryDirectory', RecordedDirectory):
            with patch.object(Path, 'write_bytes', side_effect=PermissionError('write denied')):
                with self.assertRaises(PermissionError):
                    product.convert_publication_map_svg_artifact(self.base)
        self.assertFalse(holder['path'].exists())
        self.assertNotIn(holder['path'], product._PENDING_TEMP_DIRECTORIES)

    def test_format_failure_matrix_and_corrupt_outputs(self):
        for pdf_mode, png_mode in [('fail','valid'),('valid','fail'),('fail','fail'),('corrupt','valid'),('valid','corrupt'),('truncated','valid'),('valid','truncated')]:
            with self.subTest(pdf=pdf_mode, png=png_mode):
                product._build_publication_map_converted_exports.cache_clear()
                artifact = self.injected(pdf_mode, png_mode)
                self.assertEqual(artifact.svg_bytes, self.base.svg_bytes)
                self.assertEqual(artifact.pdf_bytes is not None, pdf_mode == 'valid')
                self.assertEqual(artifact.png_bytes is not None, png_mode == 'valid')
                for issue in [artifact.pdf_issue, artifact.png_issue]:
                    if issue:
                        self.assertNotIn('C:\\private', issue.public_message)

    def test_missing_pdf_parser_keeps_real_png(self):
        original = builtins.__import__
        def missing(name, *args, **kwargs):
            if name == 'pypdf' or name.startswith('pypdf.'):
                raise ModuleNotFoundError("No module named 'pypdf'", name='pypdf')
            return original(name, *args, **kwargs)
        with patch('builtins.__import__', side_effect=missing):
            artifact = self.injected()
        self.assertIsNone(artifact.pdf_bytes)
        self.assertEqual(artifact.pdf_issue.code, 'pdf_parser_missing')
        self.assertIsNotNone(artifact.png_bytes)

    def test_missing_pillow_keeps_real_pdf(self):
        original = builtins.__import__
        def missing(name, *args, **kwargs):
            if name == 'PIL' or name.startswith('PIL.'):
                raise ModuleNotFoundError("No module named 'PIL'", name='PIL')
            return original(name, *args, **kwargs)
        with patch('builtins.__import__', side_effect=missing):
            artifact = self.injected()
        self.assertIsNotNone(artifact.pdf_bytes)
        self.assertIsNone(artifact.png_bytes)
        self.assertEqual(artifact.png_issue.code, 'dependency_missing')

    @unittest.skipUnless(os.name == 'nt', 'Windows file-lock behavior')
    def test_real_windows_lock_retains_valid_bytes_and_cleans_after_release(self):
        holder = {}
        class LockedDirectory(tempfile.TemporaryDirectory):
            def __enter__(self):
                name = super().__enter__()
                holder['path'] = Path(name)
                holder['lock'] = (Path(name) / 'lockfile').open('wb')
                return name
        try:
            with patch.object(product, 'TemporaryDirectory', LockedDirectory):
                artifact = self.injected()
            self.assertIsNotNone(artifact.pdf_bytes)
            self.assertIsNotNone(artifact.png_bytes)
            self.assertIn(holder['path'], product._PENDING_TEMP_DIRECTORIES)
            with self.assertRaises(PermissionError) as caught:
                product.shutil.rmtree(holder['path'])
            self.assertEqual(caught.exception.winerror, 32)
        finally:
            holder['lock'].close()
            product._retry_pending_temp_cleanup()
        self.assertFalse(holder['path'].exists())
        self.assertNotIn(holder['path'], product._PENDING_TEMP_DIRECTORIES)


if __name__ == '__main__':
    unittest.main()
