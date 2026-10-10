"""Targeted transport regression using an externally supplied real project backup.

Set PLANTBIODESIGN_REPORT_TEST_PROJECT to a historical backup JSON; no sequences
or project fixtures are bundled in this test.
"""
import ast
import builtins
import hashlib
import json
import os
from pathlib import Path
import unittest
from typing import Any, Mapping
from unittest.mock import patch

from services.formal_single_gene_final_review import (
    build_final_review_report, render_formal_report_markdown,
)


class RecordingUI:
    def __init__(self):
        self.downloads = []
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
        self.errors.append(str(message))

    def __getattr__(self, name):
        return lambda *args, **kwargs: None


def delivery_function(ui, app_path=None):
    app = Path(app_path) if app_path else Path(__file__).resolve().parents[1] / 'app.py'
    node = next(n for n in ast.parse(app.read_text(encoding='utf-8')).body
                if isinstance(n, ast.FunctionDef) and n.name == '_render_canonical_final_review_delivery')
    namespace = {'Mapping': Mapping, 'Any': Any, 'st': ui,
                 '_t': lambda key, **kwargs: f'{key} {kwargs}' if kwargs else key,
                 '_ui': lambda value: value,
                 '_localized_single_gene_checkpoint_report_preview': lambda value: value,
                 '_localized_formal_report_preview': lambda value: value}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(app), 'exec'), namespace)
    return namespace['_render_canonical_final_review_delivery']


def without_reportlab(name, *args, **kwargs):
    if name == 'services.formal_report_pdf' or name == 'reportlab' or name.startswith('reportlab.'):
        raise ModuleNotFoundError("No module named 'reportlab'", name='reportlab')
    return ORIGINAL_IMPORT(name, *args, **kwargs)


ORIGINAL_IMPORT = builtins.__import__


@unittest.skipUnless(os.environ.get('PLANTBIODESIGN_REPORT_TEST_PROJECT'), 'Real backup path required')
class ReportDownloadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project = json.loads(Path(os.environ['PLANTBIODESIGN_REPORT_TEST_PROJECT']).read_text(encoding='utf-8'))
        cls.report = build_final_review_report(cls.project)

    def render(self, report=None):
        ui = RecordingUI()
        delivery_function(ui)(self.report if report is None else report)
        return ui

    def test_both_transports(self):
        ui = self.render()
        self.assertFalse(ui.errors)
        self.assertTrue(all(not d['disabled'] for d in ui.downloads))
        self.assertEqual(ui.downloads[0]['data'], render_formal_report_markdown(self.report))
        self.assertTrue(ui.downloads[1]['data'].startswith(b'%PDF-'))

    def test_missing_reportlab_preserves_markdown(self):
        with patch('builtins.__import__', side_effect=without_reportlab):
            ui = self.render()
        self.assertFalse(ui.downloads[0]['disabled'])
        self.assertTrue(ui.downloads[1]['disabled'])
        self.assertIn('PDF dependency unavailable', ui.errors[0])
        self.assertEqual(ui.downloads[0]['data'], self.report['data'])

    def test_pdf_runtime_failure_preserves_page_and_markdown(self):
        with patch('services.formal_report_pdf.render_formal_report_pdf', side_effect=RuntimeError('Bundled font unavailable')):
            ui = self.render()
        self.assertFalse(ui.downloads[0]['disabled'])
        self.assertTrue(ui.downloads[1]['disabled'])
        self.assertIn('PDF:', ui.errors[0])

    def test_pdf_value_error_preserves_markdown(self):
        with patch('services.formal_report_pdf.render_formal_report_pdf', side_effect=ValueError('PDF rejected')):
            ui = self.render()
        self.assertFalse(ui.downloads[0]['disabled'])
        self.assertTrue(ui.downloads[1]['disabled'])

    def test_markdown_failure_is_independent(self):
        with patch('services.formal_single_gene_final_review.render_formal_report_markdown', side_effect=RuntimeError('Markdown failed')):
            ui = self.render()
        self.assertTrue(ui.downloads[0]['disabled'])
        self.assertFalse(ui.downloads[1]['disabled'])

    def test_invalid_identity_stays_blocked(self):
        report = dict(self.report, markdown=self.report['markdown'] + '\nchanged')
        ui = self.render(report)
        self.assertTrue(all(d['disabled'] for d in ui.downloads))

    def test_policy_blocker_stays_blocked(self):
        report = build_final_review_report(self.project, delivery_policy_blockers=['Independent review required'])
        ui = self.render(report)
        self.assertTrue(all(d['disabled'] for d in ui.downloads))

    def test_real_record_is_not_mutated(self):
        before = json.dumps(self.project, sort_keys=True)
        self.render()
        self.assertEqual(before, json.dumps(self.project, sort_keys=True))
        self.assertEqual(hashlib.sha256(self.report['data']).hexdigest(), self.report['sha256'])


if __name__ == '__main__':
    unittest.main()
