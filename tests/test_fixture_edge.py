"""Edge-case fixture conversion tests (US6).

Tests verify that edge-case fixtures (empty documents, large files,
unicode content, special characters) can be converted to PDF via
LibreOffice. Tests are skipped if LibreOffice is not installed.
"""

import shutil
from pathlib import Path

import pytest
from libreformer import LibreOfficeEngine, Succeed

LIBREOFFICE_INSTALLED = shutil.which("libreoffice") is not None


@pytest.mark.skipif(not LIBREOFFICE_INSTALLED, reason="LibreOffice not installed")
def test_empty_docx_to_pdf(empty_docx: Path):
    """Empty docx → pdf conversion succeeds or fails gracefully."""
    engine = LibreOfficeEngine(auto_install=False)
    result = engine.transform(str(empty_docx), "pdf")
    # Empty documents should still produce a valid (possibly blank) PDF
    assert isinstance(result, Succeed)
    assert result.output_path.exists()


@pytest.mark.skipif(not LIBREOFFICE_INSTALLED, reason="LibreOffice not installed")
def test_empty_xlsx_to_pdf(empty_xlsx: Path):
    """Empty xlsx → pdf conversion succeeds or fails gracefully."""
    engine = LibreOfficeEngine(auto_install=False)
    result = engine.transform(str(empty_xlsx), "pdf")
    assert isinstance(result, Succeed)
    assert result.output_path.exists()


@pytest.mark.skipif(not LIBREOFFICE_INSTALLED, reason="LibreOffice not installed")
def test_empty_pptx_to_pdf(empty_pptx: Path):
    """Empty pptx → pdf conversion succeeds or fails gracefully."""
    engine = LibreOfficeEngine(auto_install=False)
    result = engine.transform(str(empty_pptx), "pdf")
    # Empty pptx (no slides) may produce a valid PDF or fail gracefully
    assert isinstance(result, Succeed)
    assert result.output_path.exists()


@pytest.mark.skipif(not LIBREOFFICE_INSTALLED, reason="LibreOffice not installed")
def test_large_xlsx_to_pdf(large_xlsx: Path):
    """Large xlsx (1000+ rows) → pdf conversion succeeds."""
    engine = LibreOfficeEngine(auto_install=False)
    result = engine.transform(str(large_xlsx), "pdf")
    assert isinstance(result, Succeed)
    assert result.output_path.exists()
    assert result.output_path.stat().st_size > 0


@pytest.mark.skipif(not LIBREOFFICE_INSTALLED, reason="LibreOffice not installed")
def test_unicode_docx_to_pdf(unicode_docx: Path):
    """Unicode docx (multi-language) → pdf conversion succeeds."""
    engine = LibreOfficeEngine(auto_install=False)
    result = engine.transform(str(unicode_docx), "pdf")
    assert isinstance(result, Succeed)
    assert result.output_path.exists()
    assert result.output_path.stat().st_size > 0


@pytest.mark.skipif(not LIBREOFFICE_INSTALLED, reason="LibreOffice not installed")
def test_special_chars_txt_to_pdf(special_chars_txt: Path):
    """Special characters txt → pdf conversion succeeds."""
    engine = LibreOfficeEngine(auto_install=False)
    result = engine.transform(str(special_chars_txt), "pdf")
    assert isinstance(result, Succeed)
    assert result.output_path.exists()
    assert result.output_path.stat().st_size > 0
