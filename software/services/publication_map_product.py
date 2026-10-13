from __future__ import annotations

import html
import json
import os
import re
import shutil
import subprocess
import sys
import atexit
import logging
import threading
import time
import uuid
import zlib
from functools import wraps
from io import BytesIO
from collections.abc import Mapping
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from tempfile import TemporaryDirectory, gettempdir
from typing import Any
from xml.etree import ElementTree

from services.publication_map_adapter import publication_map_document_from_runtime
from services.publication_map_contract import (
    PUBLICATION_MAP_REVISION_PROVENANCE_FIELD,
    PublicationMapContractError,
    PublicationMapViewType,
)
from services.publication_map_renderer import render_publication_map_svg


PUBLICATION_MAP_SVG_MIME = "image/svg+xml"
PUBLICATION_MAP_PDF_MIME = "application/pdf"
PUBLICATION_MAP_PNG_MIME = "image/png"
_FILENAME_TOKEN_PATTERN = re.compile(r"[^A-Za-z0-9._-]+")
_SVG_CSS_PIXELS_PER_INCH = 96.0
_PUBLICATION_MAP_PNG_WIDTH_PX = 3000
_PUBLICATION_MAP_PNG_DPI = 300
_FIXED_PDF_DATE = b"D:20000101000000+00'00'"
_PDF_DATE_PATTERN = re.compile(rb"/(CreationDate|ModDate)\s*\(D:[^)]*\)")


@dataclass(frozen=True, slots=True)
class PublicationMapSvgArtifact:
    """One identity-bound SVG payload shared by preview and download."""

    svg_bytes: bytes
    file_name: str
    mime: str
    construct_identifier: str
    revision_id: str
    sequence_checksum: str
    view_type: PublicationMapViewType

    @property
    def svg_text(self) -> str:
        return self.svg_bytes.decode("utf-8")


@dataclass(frozen=True, slots=True)
class PublicationMapExportArtifact(PublicationMapSvgArtifact):
    """One frozen canonical map projected into SVG, PDF, and PNG payloads."""

    pdf_bytes: bytes | None
    png_bytes: bytes | None
    pdf_file_name: str
    png_file_name: str
    pdf_issue: "PublicationMapExportIssue | None" = None
    png_issue: "PublicationMapExportIssue | None" = None


@dataclass(frozen=True, slots=True)
class PublicationMapExportIssue:
    """A safe user-facing failure plus private diagnostic detail for tests/logs."""

    format: str
    code: str
    public_message: str
    diagnostic: str = ""
    diagnostic_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])


@dataclass(frozen=True, slots=True)
class PublicationMapConversionResult:
    pdf_bytes: bytes | None
    png_bytes: bytes | None
    pdf_issue: PublicationMapExportIssue | None = None
    png_issue: PublicationMapExportIssue | None = None


_PENDING_TEMP_DIRECTORIES: set[Path] = set()
_CLEANUP_LOCK = threading.RLock()
_CLEANUP_STARTED = False
_LOGGER = logging.getLogger(__name__)
_MANAGED_TEMP_ROOT = Path(gettempdir()) / "biodesign-publication-map-managed"


def _managed_temp_root() -> Path:
    _MANAGED_TEMP_ROOT.mkdir(parents=True, exist_ok=True)
    return _MANAGED_TEMP_ROOT


def _retry_pending_temp_cleanup() -> None:
    with _CLEANUP_LOCK:
        paths = tuple(_PENDING_TEMP_DIRECTORIES)
    for path in paths:
        try:
            shutil.rmtree(path)
        except FileNotFoundError:
            pass
        except OSError:
            continue
        with _CLEANUP_LOCK:
            _PENDING_TEMP_DIRECTORIES.discard(path)


def _cleanup_worker() -> None:
    while True:
        time.sleep(30)
        _retry_pending_temp_cleanup()
        # Recover abandoned directories after a crashed process. Active exports
        # last at most two 45-second engine runs; never touch a recent directory.
        try:
            paths = tuple(_managed_temp_root().glob("biodesign-publication-map-*"))
        except OSError:
            _LOGGER.error("Publication Map managed cleanup root is unavailable; stage=export; code=cleanup_root_unavailable")
            continue
        for path in paths:
            try:
                if path.is_dir() and time.time() - path.stat().st_mtime > 86400:
                    _record_temp_cleanup_state(path)
            except OSError:
                continue


def _start_cleanup_worker() -> None:
    global _CLEANUP_STARTED
    with _CLEANUP_LOCK:
        if not _CLEANUP_STARTED:
            threading.Thread(target=_cleanup_worker, daemon=True, name="publication-map-cleanup").start()
            _CLEANUP_STARTED = True


atexit.register(_retry_pending_temp_cleanup)


def _record_temp_cleanup_state(path: Path) -> None:
    try:
        shutil.rmtree(path)
    except FileNotFoundError:
        pass
    except OSError:
        with _CLEANUP_LOCK:
            _PENDING_TEMP_DIRECTORIES.add(path)
        _LOGGER.warning("Publication Map temporary directory retained for managed retry; stage=export; code=cleanup_pending")
        return
    with _CLEANUP_LOCK:
        _PENDING_TEMP_DIRECTORIES.discard(path)


@contextmanager
def _managed_conversion_directory():
    directory = TemporaryDirectory(
        prefix="biodesign-publication-map-", dir=_managed_temp_root(), ignore_cleanup_errors=True
    )
    temp_name = directory.__enter__()
    try:
        yield temp_name
    finally:
        try:
            directory.__exit__(None, None, None)
        except OSError:
            _LOGGER.error("Publication Map temporary cleanup failed; scheduling retry; stage=export; code=cleanup_retry")
        _record_temp_cleanup_state(Path(temp_name))


def _cache_successful_exports(function):
    """Never cache failures, so a repaired dependency/engine can recover."""
    cache = {}
    lock = threading.RLock()
    @wraps(function)
    def wrapped(svg_bytes, **kwargs):
        _retry_pending_temp_cleanup()
        key = (svg_bytes, tuple(sorted(kwargs.items())))
        with lock:
            cached = cache.get(key)
        if cached is not None:
            return cached
        result = function(svg_bytes, **kwargs)
        if result.pdf_bytes is not None and result.png_bytes is not None:
            with lock:
                if len(cache) >= 8:
                    cache.pop(next(iter(cache)))
                cache[key] = result
        return result
    def cache_clear():
        with lock:
            cache.clear()
    wrapped.cache_clear = cache_clear
    return wrapped


# Only typed, allowlisted fields cross the logging boundary. Untrusted engine
# output, exception text, commands and traceback chains are never diagnostics.
_DIAGNOSTIC_FIELD_LIMIT = 4000
_DIAGNOSTIC_LIMIT = 12000
_DIAGNOSTIC_STAGES = frozenset(("export", "pdf_conversion", "png_conversion", "pdf_validation", "png_validation"))
_DIAGNOSTIC_TYPES = frozenset(("TimeoutExpired", "PermissionError", "FileNotFoundError", "OSError", "ImportError", "PublicationMapContractError", "PublicationMapExportError", "ValueError", "Exception", "ProcessExit"))
_EXPORT_MESSAGES = {
    "engine_missing": "PDF/PNG conversion requires the installed Microsoft Edge SVG engine.",
    "engine_timeout": "Conversion engine timed out.",
    "engine_unavailable": "Conversion engine could not start.",
    "engine_failed": "Conversion engine failed.",
    "pdf_signature_invalid": "PDF conversion produced an invalid PDF signature.",
    "pdf_parser_missing": "PDF validation is unavailable because the PDF parser is not installed.",
    "pdf_structure_invalid": "PDF conversion produced a damaged or incomplete PDF.",
    "png_content_invalid": "PNG conversion produced a damaged or incomplete PNG.",
    "png_canvas_invalid": "PNG conversion produced an unexpected canvas.",
    "pdf_payload_missing": "PDF conversion produced no usable file.",
    "png_payload_missing": "PNG conversion produced no usable file.",
    "contract_error": "Export contract validation failed.",
    "dependency_missing": "Conversion dependency is unavailable.",
    "access_denied": "Access to the conversion output was denied.",
    "io_error": "Conversion failed because of a file or device error.",
    "conversion_error": "Conversion failed.",
}


@dataclass(frozen=True, slots=True)
class _SafeExportDiagnostic:
    stage: str = "export"
    exception_type: str = "PublicationMapExportError"
    timed_out: bool = False
    timeout: int | None = None
    returncode: int | None = None
    errno: int | None = None
    winerror: int | None = None

    def __post_init__(self) -> None:
        # The private object itself must be safe, including repr/asdict callers.
        object.__setattr__(self, "stage", self.stage if type(self.stage) is str and self.stage in _DIAGNOSTIC_STAGES else "export")
        object.__setattr__(self, "exception_type", self.exception_type if type(self.exception_type) is str and self.exception_type in _DIAGNOSTIC_TYPES else "Exception")
        object.__setattr__(self, "timed_out", self.timed_out is True)
        object.__setattr__(self, "timeout", self.timeout if type(self.timeout) is int and self.timeout in (10, 45) else None)
        object.__setattr__(self, "returncode", self.returncode if type(self.returncode) is int and -255 <= self.returncode <= 255 else None)
        for key in ("errno", "winerror"):
            value = getattr(self, key)
            object.__setattr__(self, key, value if type(value) is int and value in (1, 2, 5, 13, 32) else None)

    def render(self) -> str:
        # Validate even typed instances; strings and numeric subclasses are not
        # trusted merely because the caller used this dataclass.
        stage = self.stage if type(self.stage) is str and self.stage in _DIAGNOSTIC_STAGES else "export"
        kind = self.exception_type if type(self.exception_type) is str and self.exception_type in _DIAGNOSTIC_TYPES else "Exception"
        fields = [f"type={kind}", f"stage={stage}", f"timed_out={self.timed_out is True}"]
        if type(self.timeout) is int and self.timeout in (10, 45):
            fields.append(f"timeout={self.timeout}")
        if type(self.returncode) is int and -255 <= self.returncode <= 255:
            fields.append(f"returncode={self.returncode}")
        for key, value in (("errno", self.errno), ("winerror", self.winerror)):
            if type(value) is int and value in (1, 2, 5, 13, 32):
                fields.append(f"{key}={value}")
        fields.extend(("stdout=[REDACTED]", "stderr=[REDACTED]", "exception_text=[REDACTED]"))
        return "; ".join(fields)


def _safe_diagnostic(value, limit: int = _DIAGNOSTIC_FIELD_LIMIT) -> str:
    """Fail closed for all raw text, including text that looks pre-redacted."""
    text = value.render() if type(value) is _SafeExportDiagnostic else ("" if value is None else "[REDACTED]")
    return text[:max(0, limit)]


def _engine_diagnostic(stage: str, exc: BaseException) -> _SafeExportDiagnostic:
    kind = "Exception"
    for cls, name in ((subprocess.TimeoutExpired, "TimeoutExpired"), (PermissionError, "PermissionError"),
                      (FileNotFoundError, "FileNotFoundError"), (OSError, "OSError"),
                      (ImportError, "ImportError"), (PublicationMapContractError, "PublicationMapContractError"),
                      (ValueError, "ValueError")):
        if isinstance(exc, cls):
            kind = name
            break
    return _SafeExportDiagnostic(stage, kind, isinstance(exc, subprocess.TimeoutExpired),
                                 getattr(exc, "timeout", None) if isinstance(exc, subprocess.TimeoutExpired) else None,
                                 errno=getattr(exc, "errno", None) if isinstance(exc, OSError) else None,
                                 winerror=getattr(exc, "winerror", None) if isinstance(exc, OSError) else None)


class PublicationMapExportError(PublicationMapContractError):
    """Fixed public receipt and allowlisted private diagnostic fields."""

    def __init__(self, public_message: str, *, code: str, diagnostic="") -> None:
        self.code = code if type(code) is str and code in _EXPORT_MESSAGES else "conversion_error"
        self.public_message = _EXPORT_MESSAGES[self.code]
        self.diagnostic_fields = diagnostic if type(diagnostic) is _SafeExportDiagnostic else _SafeExportDiagnostic(
            stage="pdf_validation" if self.code.startswith("pdf_") else "png_validation" if self.code.startswith("png_") else "export")
        self.diagnostic = _safe_diagnostic(self.diagnostic_fields, _DIAGNOSTIC_LIMIT)
        super().__init__(self.public_message)


def _classify_issue(format_name: str, exc: BaseException) -> PublicationMapExportIssue:
    if isinstance(exc, PublicationMapExportError):
        code = exc.code if type(exc.code) is str and exc.code in _EXPORT_MESSAGES else "conversion_error"
        detail = _safe_diagnostic(exc.diagnostic_fields, _DIAGNOSTIC_LIMIT)
    else:
        code = "engine_timeout" if isinstance(exc, subprocess.TimeoutExpired) else "contract_error" if isinstance(exc, PublicationMapContractError) else "dependency_missing" if isinstance(exc, ImportError) else "access_denied" if isinstance(exc, PermissionError) else "io_error" if isinstance(exc, OSError) else "conversion_error"
        stage = "pdf_conversion" if format_name == "pdf" else "png_conversion" if format_name == "png" else "export"
        detail = _safe_diagnostic(_engine_diagnostic(stage, exc), _DIAGNOSTIC_LIMIT)
    return PublicationMapExportIssue(format_name, code, _EXPORT_MESSAGES[code], detail)


def _issue_for(format_name: str, exc: BaseException) -> PublicationMapExportIssue:
    format_name = format_name if type(format_name) is str and format_name in ("pdf", "png", "export") else "export"
    issue = _classify_issue(format_name, exc)
    # No exc_info, exception object, repr/str, source line, command or chain.
    _LOGGER.error("Publication Map %s export failed [%s, %s]: %s", issue.format,
                  issue.code, issue.diagnostic_id, issue.diagnostic)
    return issue


def _svg_canvas_and_metadata(svg_bytes: bytes) -> tuple[int, int, dict[str, Any]]:
    """Read the renderer canvas and identity without reinterpreting its geometry."""

    try:
        root = ElementTree.fromstring(svg_bytes)
        width = float(root.attrib["width"])
        height = float(root.attrib["height"])
    except (ElementTree.ParseError, KeyError, TypeError, ValueError) as exc:
        raise PublicationMapContractError(
            "Publication Map export requires an SVG with a finite pixel canvas."
        ) from exc
    if (
        width <= 0
        or height <= 0
        or not width.is_integer()
        or not height.is_integer()
    ):
        raise PublicationMapContractError(
            "Publication Map export requires positive integer SVG pixel dimensions."
        )
    view_box = root.attrib.get("viewBox", "").split()
    if len(view_box) != 4:
        raise PublicationMapContractError(
            "Publication Map export requires an explicit SVG viewBox."
        )
    try:
        origin_x, origin_y, view_width, view_height = map(float, view_box)
    except ValueError as exc:
        raise PublicationMapContractError(
            "Publication Map export requires a numeric SVG viewBox."
        ) from exc
    if (origin_x, origin_y, view_width, view_height) != (0.0, 0.0, width, height):
        raise PublicationMapContractError(
            "Publication Map export requires canvas and viewBox identity."
        )
    metadata_node = next(
        (
            node
            for node in root.iter()
            if node.tag.rsplit("}", 1)[-1] == "metadata"
            and node.attrib.get("id") == "publication-map-metadata"
        ),
        None,
    )
    try:
        metadata = json.loads(metadata_node.text or "") if metadata_node is not None else {}
    except json.JSONDecodeError as exc:
        raise PublicationMapContractError(
            "Publication Map export requires valid SVG identity metadata."
        ) from exc
    return int(width), int(height), metadata


def _publication_map_svg_engine() -> Path:
    candidates: list[Path] = []
    discovered = shutil.which("msedge")
    if discovered:
        candidates.append(Path(discovered))
    for root_name in ("PROGRAMFILES(X86)", "PROGRAMFILES"):
        root = os.environ.get(root_name)
        if root:
            candidates.append(
                Path(root) / "Microsoft" / "Edge" / "Application" / "msedge.exe"
            )
    candidates.extend(
        (
            Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
            Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
        )
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise PublicationMapExportError(
        "PDF/PNG conversion requires the installed Microsoft Edge SVG engine.",
        code="engine_missing",
    )


def _run_svg_engine(
    engine: Path,
    *,
    profile_directory: Path,
    arguments: list[str],
) -> None:
    profile_directory.mkdir(parents=True, exist_ok=True)
    command = [
        str(engine),
        "--headless",
        "--no-sandbox",
        "--disable-background-networking",
        "--disable-component-update",
        "--disable-extensions",
        "--disable-sync",
        "--no-default-browser-check",
        "--no-first-run",
        "--hide-scrollbars",
        "--force-color-profile=srgb",
        "--enable-unsafe-swiftshader",
        f"--user-data-dir={profile_directory}",
        *arguments,
    ]
    run_options: dict[str, Any] = {
        "capture_output": True,
        "check": False,
        "timeout": 45,
    }
    if sys.platform == "win32":
        run_options["creationflags"] = subprocess.CREATE_NO_WINDOW
    stage = "pdf_conversion" if any(a.startswith("--print-to-pdf=") for a in arguments) else "png_conversion"
    try:
        completed = subprocess.run(command, **run_options)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise PublicationMapExportError(
            "Conversion engine timed out." if isinstance(exc, subprocess.TimeoutExpired) else "Conversion engine could not start.",
            code="engine_timeout" if isinstance(exc, subprocess.TimeoutExpired) else "engine_unavailable",
            diagnostic=_engine_diagnostic(stage, exc),
        ) from None
    if completed.returncode != 0:
        detail = _SafeExportDiagnostic(stage, "ProcessExit", returncode=completed.returncode)
        raise PublicationMapExportError(
            "Conversion engine failed.",
            code="engine_failed",
            diagnostic=detail,
        )


def _normalize_pdf_metadata(pdf_bytes: bytes) -> bytes:
    """Freeze Chromium's clock-only fields while preserving its vector payload."""

    def replace_date(match: re.Match[bytes]) -> bytes:
        return b"/" + match.group(1) + b" (" + _FIXED_PDF_DATE + b")"

    return _PDF_DATE_PATTERN.sub(replace_date, pdf_bytes)


# Narrow validation contract for Edge vector export and bounded Flate chains. Unknown filters
# fail closed rather than entering pypdf's tolerant/external-image decoder paths.
_PDF_INPUT_LIMIT = 32 * 1024 * 1024
_PDF_STREAM_LIMIT = 16 * 1024 * 1024
_PDF_DECODED_TOTAL_LIMIT = 64 * 1024 * 1024
_PDF_OBJECT_LIMIT = 4096
_PDF_VALIDATION_TIMEOUT = 10

def _strict_pdf_parse(pdf_bytes: bytes) -> None:
    """Run only in the isolated validator process; never patch the app parser."""
    from pypdf import PdfReader, filters
    from pypdf.generic import (ArrayObject, DictionaryObject, IndirectObject,
                               NameObject, NullObject, NumberObject, StreamObject)
    if len(pdf_bytes) > _PDF_INPUT_LIMIT:
        raise ValueError("PDF input size limit exceeded")
    decoded_total = 0
    def strict_decompress(data: bytes) -> bytes:
        nonlocal decoded_total
        decoder = zlib.decompressobj()
        decoded = decoder.decompress(data, _PDF_STREAM_LIMIT + 1)
        if len(decoded) > _PDF_STREAM_LIMIT or decoder.unconsumed_tail:
            raise ValueError("PDF decoded stream size limit exceeded")
        # eof checks the real compressed terminator and Adler checksum. No tail
        # trimming, bytewise recovery, empty fallback or gzip auto-detection.
        if not decoder.eof or decoder.unused_data:
            raise ValueError("PDF compressed stream is truncated or has trailing data")
        decoded_total += len(decoded)
        if decoded_total > _PDF_DECODED_TOTAL_LIMIT:
            raise ValueError("PDF total decoded size limit exceeded")
        return decoded
    def strict_decode(stream):
        def resolve(value):
            return value.get_object() if isinstance(value, IndirectObject) else value
        filter_value = resolve(stream.get('/Filter'))
        if filter_value is None or isinstance(filter_value, NullObject):
            stream_filters = []
        elif isinstance(filter_value, NameObject):
            stream_filters = [filter_value]
        elif isinstance(filter_value, ArrayObject) and 1 <= len(filter_value) <= 4:
            stream_filters = [resolve(value) for value in filter_value]
        else:
            raise ValueError('Invalid PDF Filter type or count')
        if any(not isinstance(value, NameObject) or value != '/FlateDecode' for value in stream_filters):
            raise ValueError('Unsupported PDF export stream filter')
        parameters = resolve(stream.get('/DecodeParms'))
        if parameters is None or isinstance(parameters, NullObject):
            parameters = [None] * len(stream_filters)
        elif isinstance(parameters, DictionaryObject) and not isinstance(parameters, StreamObject):
            if len(stream_filters) != 1 or isinstance(filter_value, ArrayObject):
                raise ValueError('PDF DecodeParms dictionary requires a single Filter name')
            parameters = [parameters]
        elif isinstance(parameters, ArrayObject):
            if len(parameters) != len(stream_filters):
                raise ValueError('PDF Filter and DecodeParms count mismatch')
            parameters = [resolve(value) for value in parameters]
        else:
            raise ValueError('Invalid PDF DecodeParms type')
        for params in parameters:
            if params is None or isinstance(params, NullObject):
                continue
            if not isinstance(params, DictionaryObject) or isinstance(params, StreamObject):
                raise ValueError('Invalid PDF filter parameter entry')
            # Current vector exports use no prediction. Other legal predictor
            # modes are outside this validator's supported export scope.
            defaults = {'/Predictor':1, '/Columns':1, '/Colors':1, '/BitsPerComponent':8}
            if any(key not in defaults for key in params):
                raise ValueError('Unsupported PDF Flate parameter')
            for key, default in defaults.items():
                value = resolve(params.get(key, NumberObject(default)))
                if not isinstance(value, NumberObject) or value <= 0 or value > _PDF_STREAM_LIMIT:
                    raise ValueError('Invalid PDF Flate parameter value')
                if key == '/Predictor' and value != 1:
                    raise ValueError('Unsupported PDF Flate predictor')
                if key == '/BitsPerComponent' and value not in (1,2,4,8,16):
                    raise ValueError('Invalid PDF Flate bit depth')
        if len(stream._data) > _PDF_STREAM_LIMIT:
            raise ValueError("PDF encoded stream size limit exceeded")
        data = stream._data
        # Explicit iteration proves every filter executes, including empty raw
        # streams. No pypdf zip/empty-data fallback can skip decompression.
        for _ in stream_filters:
            data = strict_decompress(data)
        return data
    class RejectParserWarning(logging.Handler):
        def emit(self, record):
            raise ValueError("PDF parser warning: " + record.getMessage()[:1000])
    logging.getLogger("pypdf").addHandler(RejectParserWarning(logging.WARNING))
    # pypdf 6.10.0 uses these module functions for Flate, xref and ObjStm streams.
    # Process isolation contains this strict override and the wall-clock limit.
    filters.decompress = strict_decompress
    filters.decode_stream_data = strict_decode
    if not pdf_bytes.rstrip().endswith(b"%%EOF"):
        raise ValueError("PDF end-of-file marker is missing or truncated")
    reader = PdfReader(BytesIO(pdf_bytes), strict=True)
    if reader.is_encrypted:
        raise ValueError("Unexpected encrypted PDF")
    indexed = [(oid, gen) for gen, objects in reader.xref.items() if gen != 65535
               for oid in objects if oid != 0]
    indexed += [(oid, 0) for oid in reader.xref_objStm]
    if len(indexed) > _PDF_OBJECT_LIMIT:
        raise ValueError("PDF object count limit exceeded")
    for oid, gen in indexed:
        obj = reader.get_object(IndirectObject(oid, gen, reader))
        if obj is None:
            raise ValueError("Missing PDF object")
        if isinstance(obj, StreamObject):
            # DecodedStreamObject.get_data() bypasses decode_stream_data; check
            # its structure and size explicitly too.
            strict_decode(obj)
            obj.get_data()
    pages = list(reader.pages)
    if not pages or len(pages) > 16:
        raise ValueError("PDF page count outside export limits")
    for page in pages:
        _ = page.mediabox
        contents = page.get_contents()
        if contents is None or not contents.operations:
            raise ValueError("PDF page is missing readable content")
        page.extract_text()

def _pdf_validator_main() -> None:
    try:
        _strict_pdf_parse(sys.stdin.buffer.read(_PDF_INPUT_LIMIT + 1))
    except Exception as exc:
        sys.stdout.write(_safe_diagnostic(_engine_diagnostic("pdf_validation", exc)))
        raise SystemExit(1)
    sys.stdout.write("VALID")

def _validate_pdf_payload(pdf_bytes: bytes) -> bytes:
    """Validate all indexed objects/streams with bounded strict decoding."""
    if not pdf_bytes.startswith(b"%PDF-"):
        raise PublicationMapExportError(
            "PDF conversion produced an invalid PDF signature.",
            code="pdf_signature_invalid", diagnostic="missing %PDF- header",
        )
    try:
        import pypdf  # Check in caller too, so missing dependency fails locally.
    except ImportError as exc:
        raise PublicationMapExportError(
            "PDF validation is unavailable because the PDF parser is not installed.",
            code="pdf_parser_missing", diagnostic=_engine_diagnostic("pdf_validation", exc),
        ) from None
    try:
        if len(pdf_bytes) > _PDF_INPUT_LIMIT:
            raise ValueError("PDF input size limit exceeded")
        options = {"creationflags": subprocess.CREATE_NO_WINDOW} if sys.platform == "win32" else {}
        completed = subprocess.run(
            [sys.executable, "-c", "from services.publication_map_product import _pdf_validator_main; _pdf_validator_main()"],
            cwd=Path(__file__).resolve().parents[1], input=pdf_bytes,
            capture_output=True, timeout=_PDF_VALIDATION_TIMEOUT, check=False, **options,
        )
        if completed.returncode != 0 or completed.stdout != b"VALID":
            raise ValueError("PDF parser rejected output")
    except Exception as exc:
        raise PublicationMapExportError(
            "PDF conversion produced a damaged or incomplete PDF.",
            code="pdf_structure_invalid", diagnostic=_engine_diagnostic("pdf_validation", exc),
        ) from None
    return pdf_bytes


def _validate_png_payload(
    raw_png_path: Path, *, expected_size: tuple[int, int]
) -> Any:
    from PIL import Image

    try:
        with Image.open(raw_png_path) as raw_image:
            raw_image.verify()
    except Exception as exc:
        raise PublicationMapExportError(
            "PNG conversion produced a damaged or incomplete PNG.",
            code="png_content_invalid",
            diagnostic=_engine_diagnostic("png_validation", exc),
        ) from None
    with Image.open(raw_png_path) as raw_image:
        raw_image.load()
        if raw_image.size != expected_size:
            raise PublicationMapExportError(
                "PNG conversion produced an unexpected canvas.",
                code="png_canvas_invalid",
                diagnostic=f"actual_size={raw_image.size}; expected_size={expected_size}",
            )
        if raw_image.mode == "RGBA":
            image = Image.new("RGB", raw_image.size, "white")
            image.paste(raw_image, mask=raw_image.getchannel("A"))
        else:
            image = raw_image.convert("RGB")
    return image


@_cache_successful_exports
def _build_publication_map_converted_exports(
    svg_bytes: bytes,
    *,
    title: str,
    construct_identifier: str,
    revision_id: str,
    sequence_checksum: str,
) -> PublicationMapConversionResult:
    """Convert PDF and PNG independently, retaining each validated payload."""

    width, height, svg_metadata = _svg_canvas_and_metadata(svg_bytes)
    try:
        sequence_length = int(svg_metadata.get("sequence_length", 0))
    except (TypeError, ValueError) as exc:
        raise PublicationMapContractError(
            "Publication Map export requires numeric SVG sequence-length metadata."
        ) from exc
    if (
        svg_metadata.get("construct_identifier") != construct_identifier
        or svg_metadata.get("revision") != revision_id
        or svg_metadata.get("sequence_checksum") != sequence_checksum
        or sequence_length <= 0
    ):
        raise PublicationMapContractError(
            "Publication Map export identity does not match the final SVG metadata."
        )
    try:
        engine = _publication_map_svg_engine()
    except Exception as exc:
        issue = _issue_for("export", exc)
        return PublicationMapConversionResult(
            None,
            None,
            pdf_issue=PublicationMapExportIssue("pdf", issue.code, issue.public_message, issue.diagnostic, issue.diagnostic_id),
            png_issue=PublicationMapExportIssue("png", issue.code, issue.public_message, issue.diagnostic, issue.diagnostic_id),
        )
    scale = _PUBLICATION_MAP_PNG_WIDTH_PX / width
    png_height_px = max(1, round(height * scale))
    page_width_inches = width / _SVG_CSS_PIXELS_PER_INCH
    page_height_inches = height / _SVG_CSS_PIXELS_PER_INCH
    export_title = (
        f"{title}; construct={construct_identifier}; revision={revision_id}; "
        f"length={sequence_length} bp"
    )
    # Windows may retain a Chromium profile lock briefly after process exit.
    # Best-effort cleanup must not discard already validated conversion bytes.
    _retry_pending_temp_cleanup()
    pdf_bytes: bytes | None = None
    png_bytes: bytes | None = None
    pdf_issue: PublicationMapExportIssue | None = None
    png_issue: PublicationMapExportIssue | None = None
    temp_root: Path | None = None
    _start_cleanup_worker()
    with _managed_conversion_directory() as temp_name:
        temp_root = Path(temp_name)
        svg_path = temp_root / "publication-map.svg"
        html_path = temp_root / "publication-map.html"
        pdf_path = temp_root / "publication-map.pdf"
        raw_png_path = temp_root / "publication-map.png"
        svg_path.write_bytes(svg_bytes)
        wrapper = (
            "<!doctype html><html><head><meta charset=\"utf-8\">"
            f"<title>{html.escape(export_title)}</title><style>"
            f"@page{{size:{page_width_inches:.8f}in {page_height_inches:.8f}in;margin:0}}"
            f"html,body{{width:{width}px;height:{height}px;margin:0;overflow:hidden;"
            "background:#fff;-webkit-print-color-adjust:exact;print-color-adjust:exact}}"
            f"img{{display:block;width:{width}px;height:{height}px}}"
            "</style></head><body>"
            '<img src="publication-map.svg" alt="Publication Map">'
            "</body></html>"
        )
        html_path.write_text(wrapper, encoding="utf-8", newline="")
        document_uri = html_path.resolve().as_uri()
        try:
            _run_svg_engine(
                engine,
                profile_directory=temp_root / "pdf-profile",
                arguments=[
                    f"--print-to-pdf={pdf_path}",
                    "--print-to-pdf-no-header",
                    document_uri,
                ],
            )
            if not pdf_path.is_file() or pdf_path.stat().st_size < 1000:
                raise PublicationMapExportError(
                    "PDF conversion produced no usable file.",
                    code="pdf_payload_missing",
                    diagnostic=f"path_exists={pdf_path.is_file()}",
                )
            pdf_bytes = _validate_pdf_payload(
                _normalize_pdf_metadata(pdf_path.read_bytes())
            )
        except Exception as exc:
            pdf_issue = _issue_for("pdf", exc)

        try:
            from PIL import PngImagePlugin

            _run_svg_engine(
                engine,
                profile_directory=temp_root / "png-profile",
                arguments=[
                    f"--window-size={width},{height}",
                    f"--force-device-scale-factor={scale:.12f}",
                    "--run-all-compositor-stages-before-draw",
                    f"--screenshot={raw_png_path}",
                    document_uri,
                ],
            )
            if not raw_png_path.is_file() or raw_png_path.stat().st_size < 1000:
                raise PublicationMapExportError(
                    "PNG conversion produced no usable file.",
                    code="png_payload_missing",
                    diagnostic=f"path_exists={raw_png_path.is_file()}",
                )
            image = _validate_png_payload(
                raw_png_path, expected_size=(_PUBLICATION_MAP_PNG_WIDTH_PX, png_height_px)
            )
            png_metadata = PngImagePlugin.PngInfo()
            png_metadata.add_text("Title", title)
            png_metadata.add_text("Software", "BioDesign Studio Publication Map export")
            png_metadata.add_text("Construct", construct_identifier)
            png_metadata.add_text("Revision", revision_id)
            png_metadata.add_text("Sequence-Length", str(sequence_length))
            png_metadata.add_text("Sequence-SHA256", sequence_checksum)
            png_output = BytesIO()
            image.save(
                png_output,
                format="PNG",
                dpi=(_PUBLICATION_MAP_PNG_DPI, _PUBLICATION_MAP_PNG_DPI),
                pnginfo=png_metadata,
                compress_level=9,
            )
            png_bytes = png_output.getvalue()
        except Exception as exc:
            png_issue = _issue_for("png", exc)
    _retry_pending_temp_cleanup()
    return PublicationMapConversionResult(pdf_bytes, png_bytes, pdf_issue, png_issue)


def _file_token(value: str, *, fallback: str) -> str:
    token = _FILENAME_TOKEN_PATTERN.sub("-", value.strip()).strip("-._")
    return token[:80] or fallback


def build_publication_map_svg_artifact(
    runtime_payload: Mapping[str, Any],
    *,
    view_type: PublicationMapViewType,
    display_name: str = "",
) -> PublicationMapSvgArtifact:
    """Project the current canonical runtime once and freeze its exact SVG bytes."""

    if not isinstance(runtime_payload, Mapping):
        raise PublicationMapContractError(
            "Publication Map product wiring requires a canonical runtime mapping."
        )
    from services.canonical_construct_runtime import CanonicalConstructRuntimeError

    try:
        document = publication_map_document_from_runtime(
            runtime_payload,
            view_type=view_type,
            display_name=display_name,
        )
    except CanonicalConstructRuntimeError as exc:
        raise PublicationMapContractError(
            f"Canonical runtime is not eligible for Publication Map projection: {exc}"
        ) from exc
    revision_id = dict(document.provenance).get(
        PUBLICATION_MAP_REVISION_PROVENANCE_FIELD, ""
    )
    if not revision_id:
        raise PublicationMapContractError(
            "Publication Map product wiring requires canonical revision identity."
        )
    render_options = None
    if document.topology.value == "circular":
        from services.publication_map_renderer import PublicationMapRenderOptions
        render_options = PublicationMapRenderOptions(width=1800, height=1200)
    svg_bytes = render_publication_map_svg(document, render_options).encode("utf-8")
    construct_token = _file_token(
        document.construct_identifier, fallback="canonical-construct"
    )
    revision_token = _file_token(revision_id, fallback="revision")
    view_token = _file_token(view_type.value, fallback="publication-map")
    return PublicationMapSvgArtifact(
        svg_bytes=svg_bytes,
        file_name=f"{construct_token}_{revision_token}_{view_token}.svg",
        mime=PUBLICATION_MAP_SVG_MIME,
        construct_identifier=document.construct_identifier,
        revision_id=revision_id,
        sequence_checksum=document.sequence_checksum,
        view_type=view_type,
    )


def build_publication_map_export_artifact(
    runtime_payload: Mapping[str, Any], *, view_type: PublicationMapViewType, display_name: str = ""
) -> PublicationMapExportArtifact:
    base = build_publication_map_svg_artifact(runtime_payload, view_type=view_type, display_name=display_name)
    return convert_publication_map_svg_artifact(base, display_name=display_name)


def convert_publication_map_svg_artifact(
    base: PublicationMapSvgArtifact, *, display_name: str = ""
) -> PublicationMapExportArtifact:
    """Convert the exact validated SVG already used for preview and download."""
    title = f"{display_name or base.construct_identifier} publication map"
    stem = base.file_name[:-4]
    converted = _build_publication_map_converted_exports(
        base.svg_bytes,
        title=title,
        construct_identifier=base.construct_identifier,
        revision_id=base.revision_id,
        sequence_checksum=base.sequence_checksum,
    )
    return PublicationMapExportArtifact(
        **{field: getattr(base, field) for field in ("svg_bytes", "file_name", "mime", "construct_identifier", "revision_id", "sequence_checksum", "view_type")},
        pdf_bytes=converted.pdf_bytes,
        png_bytes=converted.png_bytes,
        pdf_file_name=f"{stem}.pdf",
        png_file_name=f"{stem}.png",
        pdf_issue=converted.pdf_issue,
        png_issue=converted.png_issue,
    )
