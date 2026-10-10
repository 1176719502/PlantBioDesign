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
        import services.formal_report_pdf
        with patch('services.formal_report_pdf.render_formal_report_pdf', side_effect=RuntimeError('Bundled font unavailable')):
            ui = self.render()
        self.assertFalse(ui.downloads[0]['disabled'])
        self.assertTrue(ui.downloads[1]['disabled'])
        self.assertIn('PDF:', ui.errors[0])

    def test_pdf_value_error_preserves_markdown(self):
        import services.formal_report_pdf
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

    def test_saved_source_projection_is_visible_in_both_formats(self):
        markdown = render_formal_report_markdown(self.report).decode('utf-8')
        self.assertIn('NCBI RefSeq NM_000477.7; Homo sapiens; ALB CDS 42..1871 (+)', markdown)
        self.assertIn('AF234296.1', markdown)
        from services import formal_report_pdf
        with patch.object(formal_report_pdf, '_build_story', wraps=formal_report_pdf._build_story) as story:
            self.assertTrue(formal_report_pdf.render_formal_report_pdf(self.report).startswith(b'%PDF-'))
        self.assertEqual(story.call_args.args[0], markdown)

    def test_missing_source_stays_missing(self):
        project = json.loads(json.dumps(self.project))
        project['input_records']['cds'].pop('source_name', None)
        project['input_records']['cds'].pop('source_reference', None)
        project['input_records']['cds']['source_kind'] = 'paste'
        project['source_provenance']['cds']['source_reference'] = ''
        cds = next(item for item in project['runtime']['components'] if item['component_type'] == 'cds')
        cds['provenance_reference'] = ''
        asset = next(item for item in project['runtime']['sequence_assets'] if item['asset_id'] == cds['sequence_asset_id'])
        for field in ('provenance_reference', 'source_name', 'original_record_identifier'):
            asset[field] = ''
        report = build_final_review_report(project)
        self.assertIn('ALB | cds | source: paste | Source reference: Not provided', report['markdown'])
        self.assertIn('Literature citation: Not provided', report['markdown'])
        self.assertNotIn('NM_000477.7', report['markdown'])

    def test_role_only_history_is_not_current_source(self):
        project = json.loads(json.dumps(self.project))
        project['input_records']['cds']['normalized_sequence'] = 'A' * 1830
        project['input_records']['cds']['source_name'] = 'HISTORICAL_DIFFERENT_X.1'
        markdown = build_final_review_report(project)['markdown']
        current = markdown.split('## Component Provenance and Evidence')[1].split('## Saved Input Sources')[0]
        self.assertNotIn('HISTORICAL_DIFFERENT_X.1', current)
        self.assertIn('Recorded provenance: NCBI RefSeq NM_000477.7', current)
        self.assertIn('Current attribution unconfirmed', markdown)
        self.assertIn('Saved input source: HISTORICAL_DIFFERENT_X.1', markdown)

    def test_conflicting_history_with_identical_sequence_is_not_promoted(self):
        project = json.loads(json.dumps(self.project))
        project['input_records']['cds']['source_name'] = 'CONFLICTING_HISTORY_X.1'
        markdown = build_final_review_report(project)['markdown']
        current = markdown.split('## Component Identity and Provenance')[1].split('## Vector Strategy')[0]
        self.assertNotIn('CONFLICTING_HISTORY_X.1', current)
        self.assertIn('Saved input source: CONFLICTING_HISTORY_X.1', markdown)
        self.assertIn('Current attribution unconfirmed', markdown)

    def test_provenance_only_is_not_a_literature_citation(self):
        project = json.loads(json.dumps(self.project))
        project['input_records']['cds']['source_name'] = ''
        comp = next(c for c in project['runtime']['components'] if c['component_type'] == 'cds')
        asset = next(a for a in project['runtime']['sequence_assets'] if a['asset_id'] == comp['sequence_asset_id'])
        comp['provenance_reference'] = asset['provenance_reference'] = 'USER_SAVED_SOURCE_DESCRIPTION'
        asset['original_record_identifier'] = ''
        markdown = build_final_review_report(project)['markdown']
        self.assertIn('Source reference: Not provided; see recorded provenance', markdown)
        self.assertIn('Recorded provenance: USER_SAVED_SOURCE_DESCRIPTION', markdown)
        self.assertIn('Literature citation: Not provided', markdown)
        self.assertNotIn('reference: --', markdown)

    def test_conflicting_bound_provenance_is_explicitly_unconfirmed(self):
        project = json.loads(json.dumps(self.project))
        comp = next(c for c in project['runtime']['components'] if c['component_type'] == 'cds')
        asset = next(a for a in project['runtime']['sequence_assets'] if a['asset_id'] == comp['sequence_asset_id'])
        asset['provenance_reference'] = 'OTHER_BOUND_SOURCE_X.1'
        markdown = build_final_review_report(project)['markdown']
        self.assertIn('Source reference: Unconfirmed', markdown)
        self.assertIn('Source attribution: Unconfirmed; conflicting component-bound records', markdown)
        self.assertIn('Recorded provenance: OTHER_BOUND_SOURCE_X.1', markdown)

    def test_single_reference_conflicting_with_single_provenance_is_unconfirmed(self):
        project = json.loads(json.dumps(self.project))
        comp = next(c for c in project['runtime']['components'] if c['component_type'] == 'cds')
        asset = next(a for a in project['runtime']['sequence_assets'] if a['asset_id'] == comp['sequence_asset_id'])
        asset['original_record_identifier'] = 'OLD_CONFLICTING_ACCESSION_X.1'
        markdown = build_final_review_report(project)['markdown']
        self.assertIn('ALB | cds | source: paste | Source reference: Unconfirmed', markdown)
        self.assertIn('Unconfirmed source reference: OLD_CONFLICTING_ACCESSION_X.1', markdown)
        self.assertIn('Recorded provenance: NCBI RefSeq NM_000477.7', markdown)

    def test_matching_bound_reference_and_provenance_are_visible(self):
        project = json.loads(json.dumps(self.project))
        comp = next(c for c in project['runtime']['components'] if c['component_type'] == 'cds')
        asset = next(a for a in project['runtime']['sequence_assets'] if a['asset_id'] == comp['sequence_asset_id'])
        comp['provenance_reference'] = asset['provenance_reference'] = asset['original_record_identifier'] = 'MATCHED_CURRENT_X.1'
        markdown = build_final_review_report(project)['markdown']
        self.assertIn('ALB | cds | source: paste | Source reference: MATCHED_CURRENT_X.1', markdown)
        self.assertNotIn('Source attribution: Unconfirmed', markdown)


if __name__ == '__main__':
    unittest.main()
