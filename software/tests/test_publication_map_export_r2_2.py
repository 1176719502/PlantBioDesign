"""R2.2 regression for explicit Flate dispatch and complete diagnostic redaction."""
import io
import os
from pathlib import Path
import subprocess
import tempfile
import traceback
import unittest
from unittest.mock import patch
import zlib

from pypdf import PdfWriter
from pypdf.generic import (ArrayObject, BooleanObject, DictionaryObject, EncodedStreamObject,
                           NameObject, NullObject, NumberObject, TextStringObject)
from services import publication_map_product as p

ABSENT=object()
def stream_pdf(filters=NameObject('/FlateDecode'), params=ABSENT, layers=1, raw=None, indirect=False):
    writer=PdfWriter();page=writer.add_blank_page(100,100)
    data=b'q 1 0 0 1 0 0 cm Q'
    for _ in range(layers):data=zlib.compress(data)
    stream=EncodedStreamObject();stream._data=data if raw is None else raw
    if filters is not ABSENT:
        stream[NameObject('/Filter')]=writer._add_object(filters) if indirect else filters
    if params is not ABSENT:
        stream[NameObject('/DecodeParms')]=writer._add_object(params) if indirect else params
    page[NameObject('/Contents')]=writer._add_object(stream)
    output=io.BytesIO();writer.write(output);return output.getvalue()

class FilterParameterTests(unittest.TestCase):
    def reject(self,data):
        with self.assertRaises(p.PublicationMapExportError) as caught:p._validate_pdf_payload(data)
        self.assertEqual(caught.exception.code,'pdf_structure_invalid')
    def test_empty_decodeparms_never_skips_flate(self):
        self.reject(stream_pdf(params=ArrayObject(),raw=b'q Q'))
        self.reject(stream_pdf(params=ArrayObject()))
    def test_filter_parameter_count_mismatch(self):
        self.reject(stream_pdf(params=ArrayObject([NullObject(),NullObject()])))
        self.reject(stream_pdf(filters=ArrayObject([NameObject('/FlateDecode')]*2),params=ArrayObject([NullObject()]),layers=2))
    def test_illegal_parameter_types(self):
        for params in (NumberObject(1),TextStringObject('invalid'),BooleanObject(True),
                       ArrayObject([NumberObject(1)]),ArrayObject([ArrayObject()])):
            self.reject(stream_pdf(params=params))
    def test_illegal_filter_types(self):
        for filters in (TextStringObject('/FlateDecode'),NumberObject(1),DictionaryObject(),
                        ArrayObject(),ArrayObject([TextStringObject('/FlateDecode')])):
            self.reject(stream_pdf(filters=filters))
    def test_valid_single_filter_parameters(self):
        for params in (ABSENT,NullObject(),DictionaryObject(),
                       DictionaryObject({NameObject('/Predictor'):NumberObject(1)}),
                       ArrayObject([NullObject()]),ArrayObject([DictionaryObject()])):
            data=stream_pdf(params=params);self.assertEqual(p._validate_pdf_payload(data),data)
    def test_valid_array_and_indirect_parameters(self):
        for params in (ABSENT,NullObject(),ArrayObject([NullObject()]),ArrayObject([DictionaryObject()])):
            data=stream_pdf(filters=ArrayObject([NameObject('/FlateDecode')]),params=params,indirect=True)
            self.assertEqual(p._validate_pdf_payload(data),data)
    def test_valid_supported_multiple_flate_filters(self):
        for params in (ABSENT,NullObject(),ArrayObject([NullObject(),DictionaryObject()])):
            data=stream_pdf(filters=ArrayObject([NameObject('/FlateDecode')]*2),params=params,layers=2)
            self.assertEqual(p._validate_pdf_payload(data),data)
    def test_every_layer_requires_real_decoding(self):
        self.reject(stream_pdf(filters=ArrayObject([NameObject('/FlateDecode')]*2),params=ArrayObject([NullObject()]*2),layers=1))
        self.reject(stream_pdf(raw=b''))
    def test_abnormal_parameter_structure(self):
        for params in (DictionaryObject({NameObject('/Predictor'):TextStringObject('1')}),
                       DictionaryObject({NameObject('/Predictor'):BooleanObject(True)}),
                       DictionaryObject({NameObject('/Columns'):NumberObject(0)}),
                       DictionaryObject({NameObject('/BitsPerComponent'):NumberObject(3)}),
                       DictionaryObject({NameObject('/Unknown'):NumberObject(1)})):
            self.reject(stream_pdf(params=params))
        self.reject(stream_pdf(filters=ArrayObject([NameObject('/FlateDecode')]*2),params=DictionaryObject(),layers=2))
        self.reject(stream_pdf(filters=ABSENT,params=DictionaryObject(),raw=b'q Q'))
    def test_scope_and_resource_limits(self):
        self.reject(stream_pdf(filters=NameObject('/ASCII85Decode')))
        self.reject(stream_pdf(filters=ArrayObject([NameObject('/FlateDecode')]*5),layers=5))
        self.reject(stream_pdf(params=DictionaryObject({NameObject('/Predictor'):NumberObject(12)})))
        self.reject(stream_pdf(raw=zlib.compress(b' '*(p._PDF_STREAM_LIMIT+1))))
    def test_exact_independent_review_counterexamples(self):
        folder=Path(os.environ['R2_2_COUNTEREXAMPLES'])
        for name in ('minimal-empty-decodeparms.pdf','real-object14-empty-decodeparms.pdf'):
            self.reject((folder/name).read_bytes())

class RedactionTests(unittest.TestCase):
    def assert_hidden(self,text,*secrets):
        self.assertTrue(all(value not in text for value in secrets),'Sensitive suffix survived redaction')
    def test_raw_diagnostics_are_fully_masked(self):
        for value in ('OUT_MARK password="alpha beta"', b'OUT_MARK token="gamma delta"',
                      'OUT_MARK C:\\Users\\Private Person\\sensitive.txt',
                      'password=[REDACTED]alpha beta', 'x'*70000, None):
            result=p._safe_diagnostic(value)
            self.assertEqual(result, '' if value is None else '[REDACTED]')
            if value is not None:self.assertEqual(p._safe_diagnostic(result),result)
            self.assert_hidden(result,'alpha','beta','gamma','delta','Private','Person','OUT_MARK')
        self.assertLessEqual(len(p._safe_diagnostic('password="alpha beta"',3)),3)

    def test_timeout_all_records_and_exception_receipt(self):
        stdout='OUT_MARK C:\\Users\\Private Person\\Documents\\sensitive.txt password="alpha beta"'
        stderr="ERR_MARK token='gamma delta'; secret=\"theta omega\""
        for value in (stdout,stdout.encode(),None):
            exc=subprocess.TimeoutExpired(['edge','password="command secret"'],45,output=value,stderr=stderr)
            with tempfile.TemporaryDirectory() as tmp,patch.object(p.subprocess,'run',side_effect=exc),self.assertLogs(p._LOGGER,level='ERROR') as logs:
                try:p._run_svg_engine(Path('edge'),profile_directory=Path(tmp),arguments=['--print-to-pdf=x.pdf'])
                except p.PublicationMapExportError as error:
                    receipt=''.join(traceback.format_exception(error))
                    issue=p._issue_for('pdf',error)
            for text in (issue.diagnostic,issue.public_message,receipt,'\n'.join(logs.output)):
                self.assert_hidden(text,'alpha','beta','gamma','delta','theta','omega','command secret','Private Person','sensitive.txt')
            self.assertIn('TimeoutExpired',issue.diagnostic);self.assertIn('pdf_conversion',issue.diagnostic)
            self.assertIn('timeout=45',issue.diagnostic);self.assertIn('stderr=[REDACTED]',issue.diagnostic)
            self.assertNotIn('OUT_MARK',issue.diagnostic)
    def test_validator_timeout_receipt(self):
        timeout=subprocess.TimeoutExpired('password="command secret"',10,output=b'OUT_MARK password="alpha beta"',stderr="ERR_MARK token='gamma delta'")
        with patch.object(p.subprocess,'run',side_effect=timeout):
            try:p._validate_pdf_payload(stream_pdf())
            except p.PublicationMapExportError as error:
                receipt=''.join(traceback.format_exception(error));issue=p._issue_for('pdf',error)
        self.assert_hidden(receipt+issue.diagnostic,'alpha','beta','gamma','delta','command secret')
        self.assertIn('pdf_validation',issue.diagnostic)
    def test_long_timeout_retains_independent_stage_and_stderr(self):
        exc=subprocess.TimeoutExpired('edge',45,output='OUT_MARK password="'+ 'alpha beta '*10000+'"',stderr='ERR_MARK')
        result=p._safe_diagnostic(p._engine_diagnostic('png_conversion',exc))
        self.assertIn('stderr=[REDACTED]',result);self.assertIn('stdout=[REDACTED]',result)
        self.assertIn('png_conversion',result);self.assertLessEqual(len(result),p._DIAGNOSTIC_LIMIT)
        self.assert_hidden(result,'alpha','beta')
    def test_issue_diagnostic_also_sanitizes_unwrapped_timeout(self):
        exc=subprocess.TimeoutExpired('password="alpha beta"',45,stderr="token='gamma delta'")
        with self.assertLogs(p._LOGGER,level='ERROR') as logs:issue=p._issue_for('pdf',exc)
        self.assert_hidden(issue.diagnostic+'\n'.join(logs.output),'alpha','beta','gamma','delta')
