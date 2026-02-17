"""Calc-category fixture conversion tests (US2).

Tests verify that generated Calc fixtures can be converted to PDF
via LibreOffice. Tests are skipped if LibreOffice is not installed.
"""

import shutil
from pathlib import Path

import pytest
from libreformer import LibreOfficeEngine, Succeed

LIBREOFFICE_INSTALLED = shutil.which("libreoffice") is not None


@pytest.mark.skipif(not LIBREOFFICE_INSTALLED, reason="LibreOffice not installed")
def test_xlsx_to_pdf(sample_xlsx: Path):
    """xlsx → pdf conversion succeeds."""
    engine = LibreOfficeEngine(auto_install=False)
    result = engine.transform(str(sample_xlsx), "pdf")
    assert isinstance(result, Succeed)
    assert result.output_path.exists()
    assert result.output_path.stat().st_size > 0


@pytest.mark.skipif(not LIBREOFFICE_INSTALLED, reason="LibreOffice not installed")
def test_ods_to_pdf(sample_ods: Path):
    """ods → pdf conversion succeeds."""
    engine = LibreOfficeEngine(auto_install=False)
    result = engine.transform(str(sample_ods), "pdf")
    assert isinstance(result, Succeed)
    assert result.output_path.exists()
    assert result.output_path.stat().st_size > 0


@pytest.mark.skipif(not LIBREOFFICE_INSTALLED, reason="LibreOffice not installed")
def test_csv_to_pdf(sample_csv: Path):
    """csv → pdf conversion succeeds."""
    engine = LibreOfficeEngine(auto_install=False)
    result = engine.transform(str(sample_csv), "pdf")
    assert isinstance(result, Succeed)
    assert result.output_path.exists()
    assert result.output_path.stat().st_size > 0


@pytest.mark.skipif(not LIBREOFFICE_INSTALLED, reason="LibreOffice not installed")
def test_tsv_to_pdf(sample_tsv: Path):
    """tsv → pdf conversion succeeds."""
    engine = LibreOfficeEngine(auto_install=False)
    result = engine.transform(str(sample_tsv), "pdf")
    assert isinstance(result, Succeed)
    assert result.output_path.exists()
    assert result.output_path.stat().st_size > 0
