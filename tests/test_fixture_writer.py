"""Writer-category fixture conversion tests (US1).

Tests verify that generated Writer fixtures can be converted to PDF
via LibreOffice. Tests are skipped if LibreOffice is not installed.
"""

import shutil
from pathlib import Path

import pytest
from libreformer import LibreOfficeEngine, Succeed

LIBREOFFICE_INSTALLED = shutil.which("libreoffice") is not None


@pytest.mark.skipif(not LIBREOFFICE_INSTALLED, reason="LibreOffice not installed")
def test_docx_to_pdf(sample_docx: Path):
    """docx → pdf conversion succeeds with image-embedded document."""
    engine = LibreOfficeEngine(auto_install=False)
    result = engine.transform(str(sample_docx), "pdf")
    assert isinstance(result, Succeed)
    assert result.output_path.exists()
    assert result.output_path.stat().st_size > 0


@pytest.mark.skipif(not LIBREOFFICE_INSTALLED, reason="LibreOffice not installed")
def test_odt_to_pdf(sample_odt: Path):
    """odt → pdf conversion succeeds."""
    engine = LibreOfficeEngine(auto_install=False)
    result = engine.transform(str(sample_odt), "pdf")
    assert isinstance(result, Succeed)
    assert result.output_path.exists()
    assert result.output_path.stat().st_size > 0


@pytest.mark.skipif(not LIBREOFFICE_INSTALLED, reason="LibreOffice not installed")
def test_rtf_to_pdf(sample_rtf: Path):
    """rtf → pdf conversion succeeds."""
    engine = LibreOfficeEngine(auto_install=False)
    result = engine.transform(str(sample_rtf), "pdf")
    assert isinstance(result, Succeed)
    assert result.output_path.exists()
    assert result.output_path.stat().st_size > 0


@pytest.mark.skipif(not LIBREOFFICE_INSTALLED, reason="LibreOffice not installed")
def test_html_to_pdf(sample_html: Path):
    """html → pdf conversion succeeds."""
    engine = LibreOfficeEngine(auto_install=False)
    result = engine.transform(str(sample_html), "pdf")
    assert isinstance(result, Succeed)
    assert result.output_path.exists()
    assert result.output_path.stat().st_size > 0


@pytest.mark.skipif(not LIBREOFFICE_INSTALLED, reason="LibreOffice not installed")
def test_txt_to_pdf(sample_txt: Path):
    """txt → pdf conversion succeeds."""
    engine = LibreOfficeEngine(auto_install=False)
    result = engine.transform(str(sample_txt), "pdf")
    assert isinstance(result, Succeed)
    assert result.output_path.exists()
    assert result.output_path.stat().st_size > 0


@pytest.mark.skipif(not LIBREOFFICE_INSTALLED, reason="LibreOffice not installed")
def test_docx_with_image_has_larger_output(sample_docx: Path, sample_txt: Path):
    """docx with image produces larger PDF than plain text."""
    engine = LibreOfficeEngine(auto_install=False)
    docx_result = engine.transform(str(sample_docx), "pdf")
    txt_result = engine.transform(str(sample_txt), "pdf")

    assert isinstance(docx_result, Succeed)
    assert isinstance(txt_result, Succeed)
    assert (
        docx_result.output_path.stat().st_size > txt_result.output_path.stat().st_size
    )
