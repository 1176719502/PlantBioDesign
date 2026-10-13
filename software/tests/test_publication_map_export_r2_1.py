"""R2.1 strict stream and timeout regression; external reviewed samples required."""
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from io import BytesIO
import re
import zlib

from services import publication_map_product as p
from services.publication_map_contract import PublicationMapViewType
from test_publication_map_export import RecordingUI, delivery
from pypdf import PdfReader, PdfWriter
from pypdf.generic import DecodedStreamObject, NameObject


class PdfStrictStreamTests(unittest.TestCase):
    def test_review_samples_rejected(self):
        folder = Path(os.environ['R2_1_DAMAGED_PDF_SAMPLES'])
        expected = {'object-7.pdf':'c02f9c414bcd68af996c56a8b220caa417038954a062988e30c3efe44489f53d',
                    'object-14.pdf':'4daf3460ed92c22c2dea1a9ea6f66b8afaea5c02b7abf9023f8ae0d96389b520',
                    'object-38.pdf':'9460df3af728338c4c7210ef0925146cef3fdcf8b5ce6f4e6c518f6b14f94b36',
                    'actual-browser-download.pdf':'4daf3460ed92c22c2dea1a9ea6f66b8afaea5c02b7abf9023f8ae0d96389b520'}
        for name, sha in expected.items():
            with self.subTest(name=name):
                data = (folder/name).read_bytes()
                self.assertEqual(hashlib.sha256(data).hexdigest(), sha)
                self.assertTrue(data.rstrip().endswith(b'%%EOF'))
                with self.assertRaises(p.PublicationMapExportError) as caught:
                    p._validate_pdf_payload(data)
                self.assertEqual(caught.exception.code,'pdf_structure_invalid')
                self.assertIn('stage=pdf_validation', caught.exception.diagnostic)

    def pdf_with_stream(self, stream):
        writer=PdfWriter(); page=writer.add_blank_page(100,100)
        obj=DecodedStreamObject(); obj.set_data(stream)
        page[NameObject('/Contents')]=writer._add_object(obj.flate_encode())
        output=BytesIO();writer.write(output);return output.getvalue()

    def test_valid_compressed_pdf(self):
        data=self.pdf_with_stream(b'q 1 0 0 1 0 0 cm Q')
        self.assertEqual(p._validate_pdf_payload(data),data)

    def test_checksum_and_truncation_rejected_with_intact_xref(self):
        data=self.pdf_with_stream(b'q 1 0 0 1 0 0 cm Q')
        # Same-length changes inside stream, leaving xref and EOF untouched.
        match=re.search(rb'stream\n(.*?)\nendstream',data,re.S)
        for replacement in (match[1][:-1]+bytes([match[1][-1]^1]),match[1][:-4]+b'\x00'*4):
            damaged=data[:match.start(1)]+replacement+data[match.end(1):]
            self.assertEqual(len(damaged),len(data))
            self.assertEqual(damaged[damaged.index(b'xref'):],data[data.index(b'xref'):])
            with self.assertRaises(p.PublicationMapExportError):p._validate_pdf_payload(damaged)

    def test_decompression_bomb_rejected(self):
        data=self.pdf_with_stream(b' '*(p._PDF_STREAM_LIMIT+1))
        with self.assertRaises(p.PublicationMapExportError) as caught:p._validate_pdf_payload(data)
        self.assertEqual(caught.exception.code,'pdf_structure_invalid')

    def test_validator_timeout_fails_closed(self):
        data=self.pdf_with_stream(b'q Q')
        with patch.object(p.subprocess,'run',side_effect=subprocess.TimeoutExpired('validator',10,output=b'VALIDATION_STDOUT',stderr=b'VALIDATION_STDERR')):
            with self.assertRaises(p.PublicationMapExportError) as caught:p._validate_pdf_payload(data)
        self.assertIn('stage=pdf_validation',caught.exception.diagnostic)
        self.assertIn('stderr=[REDACTED]',caught.exception.diagnostic)


class TimeoutDiagnosticTests(unittest.TestCase):
    def test_timeout_bytes_str_none_preserved_and_redacted(self):
        for value in (b'OUTPUT_MARK C:\\private\\machine\\file token=secret123\x1b',
                      'OUTPUT_MARK /private/machine/file password=secret123',None):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as tmp:
                timeout=subprocess.TimeoutExpired(['edge','C:\\private\\engine','token=cmdsecret'],45,output=value,stderr=value)
                with patch.object(p.subprocess,'run',side_effect=timeout):
                    with self.assertRaises(p.PublicationMapExportError) as caught:
                        p._run_svg_engine(Path('edge'),profile_directory=Path(tmp),arguments=['--print-to-pdf=map.pdf'])
                issue=p._issue_for('pdf',caught.exception)
                self.assertEqual(issue.code,'engine_timeout')
                self.assertIn('type=TimeoutExpired',issue.diagnostic)
                self.assertIn('stage=pdf_conversion',issue.diagnostic)
                self.assertIn('stdout=',issue.diagnostic); self.assertIn('stderr=',issue.diagnostic)
                self.assertNotIn('OUTPUT_MARK',issue.diagnostic)
                for secret in ('secret123','cmdsecret','C:\\private','/private','\x1b'):
                    self.assertNotIn(secret,issue.diagnostic);self.assertNotIn(secret,issue.public_message)

    def test_private_logs_redacted_and_bounded(self):
        with tempfile.TemporaryDirectory() as tmp:
            timeout=subprocess.TimeoutExpired(['edge','C:\\private\\engine','token=cmdsecret'],45,
                        output=b'STDOUT_MARK token=secret123 '+b'x'*100000,
                        stderr='STDERR_MARK /private/system/file Authorization: Bearer authsecret')
            with patch.object(p.subprocess,'run',side_effect=timeout), self.assertLogs(p._LOGGER,level='ERROR') as logs:
                try:p._run_svg_engine(Path('edge'),profile_directory=Path(tmp),arguments=['--screenshot=map.png'])
                except p.PublicationMapExportError as exc:issue=p._issue_for('png',exc)
            self.assertIn('stdout=[REDACTED]',issue.diagnostic);self.assertIn('stderr=[REDACTED]',issue.diagnostic)
            self.assertNotIn('STDOUT_MARK',issue.diagnostic);self.assertNotIn('STDERR_MARK',issue.diagnostic)
            self.assertLessEqual(len(issue.diagnostic),p._DIAGNOSTIC_LIMIT)
            self.assertLess(len(logs.output[0]),21000)
            for secret in ('cmdsecret','secret123','authsecret','C:\\private','/private'):
                self.assertNotIn(secret,logs.output[0])


@unittest.skipUnless(os.environ.get('PLANTBIODESIGN_REPORT_TEST_PROJECT'),'Real backup required')
class FormatBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import json
        cls.project=json.loads(Path(os.environ['PLANTBIODESIGN_REPORT_TEST_PROJECT']).read_text('utf-8'))
        cls.base=p.build_publication_map_svg_artifact(cls.project['runtime'],view_type=PublicationMapViewType.COMPLETE_CIRCULAR_PLASMID)
        cls.valid=p.convert_publication_map_svg_artifact(cls.base)
        assert cls.valid.pdf_bytes and cls.valid.png_bytes

    def test_reviewed_damage_blocks_pdf_download_keeps_png(self):
        sample=(Path(os.environ['R2_1_DAMAGED_PDF_SAMPLES'])/'actual-browser-download.pdf').read_bytes()
        def engine(_,*,profile_directory,arguments):
            for a in arguments:
                if a.startswith('--print-to-pdf=') or a.startswith('--screenshot='):
                    Path(a.split('=',1)[1]).write_bytes(sample if a.startswith('--print-to-pdf=') else self.valid.png_bytes)
        p._build_publication_map_converted_exports.cache_clear()
        ui=RecordingUI()
        with patch.object(p,'_run_svg_engine',side_effect=engine):
            ok=delivery(ui)({'runtime':self.project['runtime']},view_type='complete_circular_plasmid',display_name='',download_key='r2-1')
        self.assertTrue(ok)
        self.assertEqual([d.get('disabled',False) for d in ui.downloads],[False,True,False])
        self.assertIn('damaged',ui.warnings[0])

    def test_single_format_timeout_keeps_other_download(self):
        for fail_pdf in (True,False):
            with self.subTest(fail_pdf=fail_pdf):
                original=p._run_svg_engine
                def engine(engine,*,profile_directory,arguments):
                    pdf=any(a.startswith('--print-to-pdf=') for a in arguments)
                    if pdf==fail_pdf:
                        timeout=subprocess.TimeoutExpired(['edge'],45,output=b'FORMAT_STDOUT',stderr='FORMAT_STDERR token=sensitive')
                        with patch.object(p.subprocess,'run',side_effect=timeout):return original(engine,profile_directory=profile_directory,arguments=arguments)
                    for a in arguments:
                        if a.startswith('--print-to-pdf=') or a.startswith('--screenshot='):
                            Path(a.split('=',1)[1]).write_bytes(self.valid.pdf_bytes if pdf else self.valid.png_bytes)
                p._build_publication_map_converted_exports.cache_clear();ui=RecordingUI()
                with patch.object(p,'_run_svg_engine',side_effect=engine):
                    ok=delivery(ui)({'runtime':self.project['runtime']},view_type='complete_circular_plasmid',display_name='',download_key='r2-1')
                self.assertTrue(ok)
                self.assertEqual([d.get('disabled',False) for d in ui.downloads],[False,fail_pdf,not fail_pdf])
                self.assertNotIn('sensitive',' '.join(ui.warnings))
