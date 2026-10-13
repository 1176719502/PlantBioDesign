"""B02 end-to-end synthetic adversarial samples; failures report booleans only."""
import io
import json
import logging
import os
from pathlib import Path
import subprocess
import tempfile
import traceback
import unittest
from unittest.mock import patch

from services import publication_map_product as p
from services.publication_map_contract import PublicationMapViewType
from test_publication_map_export import RecordingUI, delivery


def samples():
    return [
        ('sentinel', 'password=[REDACTED]alpha beta; token=[REDACTED]gamma delta', ('alpha beta','alpha','beta','gamma delta','gamma','delta')),
        ('double_quote', 'password="alpha beta"', ('alpha beta','alpha','beta')),
        ('single_quote', "password='alpha beta'", ('alpha beta','alpha','beta')),
        ('windows_spaces', r'"C:\Users\Private Person\Documents\sensitive file.txt"', ('Private Person','Private','Person','sensitive file.txt','sensitive')),
        ('multiple', 'password="alpha beta"; token=\'gamma delta\'; api_key="theta omega"; Authorization: Bearer epsilon zeta', ('alpha','beta','gamma','delta','theta','omega','epsilon','zeta')),
        ('bytes', b'password=[REDACTED]alpha beta\xff', ('alpha','beta')),
        ('none', None, ()),
        ('long', 'X'*70000+' password="alpha beta"', ('alpha','beta','XXXXXXXX')),
        ('truncated', 'password="alpha beta', ('alpha','beta')),
        ('incomplete', 'unrecognized field alpha beta; password=', ('alpha','beta')),
        ('multiline', 'password=[REDACTED]\nalpha beta\ntoken=gamma delta', ('alpha','beta','gamma','delta')),
        ('unlabelled', 'alpha beta', ('alpha','beta')),
    ]


class Capture(logging.Handler):
    def __init__(self):
        super().__init__(); self.records=[]
    def emit(self, record):
        self.records.append(record)


class SecurityBoundaryTests(unittest.TestCase):
    def hidden(self, surfaces, fragments):
        # No failure message/parameter includes original values or raw output.
        self.assertTrue(all(fragment not in surface for surface in surfaces for fragment in fragments), 'Unsafe residual detected')

    def exercise(self, name, value, fragments, png=False):
        holder=Capture(); p._LOGGER.addHandler(holder)
        args=['--screenshot=x.png'] if png else ['--print-to-pdf=x.pdf']
        try:
            try:
                raise ValueError('nested alpha beta C:\\Users\\Private Person\\file')
            except ValueError as nested:
                error=subprocess.TimeoutExpired(['edge','password="command secret"'],45,output=value,stderr=value)
                error.__cause__=nested
            with tempfile.TemporaryDirectory() as tmp, patch.object(p.subprocess,'run',side_effect=error):
                try:p._run_svg_engine(Path('edge'),profile_directory=Path(tmp),arguments=args)
                except p.PublicationMapExportError as caught:
                    receipt=''.join(traceback.format_exception(caught))
                    issue=p._issue_for('png' if png else 'pdf',caught)
                    private=json.dumps(vars(caught),default=lambda x:x.render() if type(x) is p._SafeExportDiagnostic else '[REDACTED]')
        finally:p._LOGGER.removeHandler(holder)
        self.assertTrue(bool(holder.records),'Missing ERROR diagnostic')
        logs='\n'.join(logging.Formatter().format(record) for record in holder.records)
        raw_log_args=repr([record.args for record in holder.records])
        self.hidden((issue.diagnostic,issue.public_message,receipt,private,logs,raw_log_args),
                    (*fragments,'command secret','nested alpha beta','Private Person'))
        self.assertTrue(all(record.exc_info is None and record.stack_info is None for record in holder.records))
        self.assertTrue(all(not any(isinstance(arg, BaseException) for arg in record.args) for record in holder.records))
        for marker in ('type=TimeoutExpired','timeout=45','timed_out=True','stdout=[REDACTED]','stderr=[REDACTED]'):
            self.assertTrue(marker in issue.diagnostic,'Safe diagnostic missing')
        self.assertTrue(('stage=png_conversion' if png else 'stage=pdf_conversion') in issue.diagnostic)
        self.assertEqual(issue.code,'engine_timeout')

    def test_all_timeout_surfaces_pdf_and_png(self):
        for name,value,fragments in samples():
            for png in (False,True):
                with self.subTest(case=name,format='png' if png else 'pdf'):
                    self.exercise(name,value,fragments,png)

    def test_non_timeout_and_raw_exceptions_do_not_format_text(self):
        class HostileError(Exception):
            def __str__(self):raise AssertionError('Exception text must not be accessed')
        errors=(HostileError(),PermissionError(13,'alpha beta',r'C:\Private Person\file'),
                ImportError('alpha beta'),ValueError('alpha beta'),
                subprocess.TimeoutExpired('alpha beta','alpha beta',output=b'alpha beta'))
        for i,error in enumerate(errors):
            with self.subTest(case=i),self.assertLogs(p._LOGGER,level='ERROR') as logs:
                issue=p._issue_for('pdf',error)
            self.hidden((issue.diagnostic,issue.public_message,'\n'.join(logs.output)),('alpha','beta','Private Person'))

    def test_forged_structured_fields_and_pre_redacted_strings(self):
        diagnostic=p._SafeExportDiagnostic('alpha beta','alpha beta',timeout='alpha beta',returncode='alpha beta',errno='alpha beta',winerror='alpha beta')
        for value in ('[REDACTED]alpha beta', diagnostic):
            error=p.PublicationMapExportError('alpha beta',code='alpha beta',diagnostic=value)
            with self.assertLogs(p._LOGGER,level='ERROR') as logs:issue=p._issue_for('alpha beta',error)
            self.hidden((issue.diagnostic,issue.public_message,str(error),repr(error.diagnostic_fields),'\n'.join(logs.output)),('alpha','beta'))

    def test_nonzero_engine_output_is_fully_masked(self):
        for name,value,fragments in samples():
            with self.subTest(case=name),tempfile.TemporaryDirectory() as tmp:
                result=subprocess.CompletedProcess(['alpha beta'],23,value,value)
                with patch.object(p.subprocess,'run',return_value=result),self.assertLogs(p._LOGGER,level='ERROR') as logs:
                    try:p._run_svg_engine(Path('edge'),profile_directory=Path(tmp),arguments=[])
                    except p.PublicationMapExportError as error:
                        receipt=''.join(traceback.format_exception(error));issue=p._issue_for('png',error)
                self.hidden((issue.diagnostic,issue.public_message,receipt,'\n'.join(logs.output)),fragments)
                self.assertTrue('returncode=23' in issue.diagnostic)

    def test_pdf_validator_timeout_final_records(self):
        for name,value,fragments in samples():
            with self.subTest(case=name),patch.object(p.subprocess,'run',side_effect=subprocess.TimeoutExpired('alpha beta',10,output=value,stderr=value)),self.assertLogs(p._LOGGER,level='ERROR') as logs:
                try:p._validate_pdf_payload(b'%PDF-1.7 synthetic')
                except p.PublicationMapExportError as error:
                    receipt=''.join(traceback.format_exception(error));issue=p._issue_for('pdf',error)
            self.hidden((issue.diagnostic,issue.public_message,receipt,'\n'.join(logs.output)),(*fragments,'alpha','beta'))
            self.assertTrue('stage=pdf_validation' in issue.diagnostic and 'timeout=10' in issue.diagnostic)


@unittest.skipUnless(os.environ.get('PLANTBIODESIGN_REPORT_TEST_PROJECT'),'Real backup required')
class DownloadIsolationTests(unittest.TestCase):
    hidden = SecurityBoundaryTests.hidden
    @classmethod
    def setUpClass(cls):
        cls.project=json.loads(Path(os.environ['PLANTBIODESIGN_REPORT_TEST_PROJECT']).read_text('utf-8'))
        cls.base=p.build_publication_map_svg_artifact(cls.project['runtime'],view_type=PublicationMapViewType.COMPLETE_CIRCULAR_PLASMID)
        p._build_publication_map_converted_exports.cache_clear()
        cls.valid=p.convert_publication_map_svg_artifact(cls.base)
        assert cls.valid.pdf_bytes and cls.valid.png_bytes, 'Valid formats unavailable'

    def test_timeout_download_ui_and_private_issue(self):
        for fail_pdf in (True,False):
            for name,value,fragments in samples():
                with self.subTest(case=name,failed_format='pdf' if fail_pdf else 'png'):
                    original=p._run_svg_engine;holder={}
                    def engine(engine,*,profile_directory,arguments):
                        pdf=any(a.startswith('--print-to-pdf=') for a in arguments)
                        if pdf==fail_pdf:
                            timeout=subprocess.TimeoutExpired('password="command secret"',45,output=value,stderr=value)
                            with patch.object(p.subprocess,'run',side_effect=timeout):return original(engine,profile_directory=profile_directory,arguments=arguments)
                        for arg in arguments:
                            if arg.startswith('--print-to-pdf=') or arg.startswith('--screenshot='):
                                Path(arg.split('=',1)[1]).write_bytes(self.valid.pdf_bytes if pdf else self.valid.png_bytes)
                    convert=p.convert_publication_map_svg_artifact
                    def recording(*args,**kwargs):
                        holder['artifact']=convert(*args,**kwargs);return holder['artifact']
                    p._build_publication_map_converted_exports.cache_clear();ui=RecordingUI()
                    with patch.object(p,'_run_svg_engine',side_effect=engine),patch.object(p,'convert_publication_map_svg_artifact',side_effect=recording),self.assertLogs(p._LOGGER,level='ERROR') as logs:
                        ok=delivery(ui)({'runtime':self.project['runtime']},view_type='complete_circular_plasmid',display_name='',download_key='r2-3')
                    self.assertTrue(ok)
                    self.assertEqual([d.get('disabled',False) for d in ui.downloads],[False,fail_pdf,not fail_pdf])
                    self.assertEqual(ui.downloads[0]['data'],self.base.svg_bytes)
                    self.assertEqual(ui.downloads[2 if fail_pdf else 1]['data'],self.valid.png_bytes if fail_pdf else self.valid.pdf_bytes)
                    issue=holder['artifact'].pdf_issue if fail_pdf else holder['artifact'].png_issue
                    # Download payloads above must equal clean control bytes.
                    # Do not confuse legitimate map labels (e.g. alpha) with
                    # an injected secret fragment in a repr of those payloads.
                    receipts=repr([{k:v for k,v in d.items() if k!='data'} for d in ui.downloads])
                    self.hidden((issue.diagnostic,issue.public_message,repr(ui.warnings),repr(ui.errors),receipts,'\n'.join(logs.output)),(*fragments,'command secret'))
