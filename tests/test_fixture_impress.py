"""Impress-category fixture conversion tests (US3).

Tests verify that generated Impress fixtures can be converted to PDF
via LibreOffice. Tests are skipped if LibreOffice is not installed.
"""

import shutil
from pathlib import Path

import pytest
from libreformer import LibreOfficeEngine, Succeed

LIBREOFFICE_INSTALLED = shutil.which("libreoffice") is not None


@pytest.mark.skipif(not LIBREOFFICE_INSTALLED, reason="LibreOffice not installed")
def test_pptx_to_pdf(sample_pptx: Path):
    """pptx → pdf conversion succeeds."""
    engine = LibreOfficeEngine(auto_install=False)
    result = engine.transform(str(sample_pptx), "pdf")
    assert isinstance(result, Succeed)
    assert result.output_path.exists()
    assert result.output_path.stat().st_size > 0


@pytest.mark.skipif(not LIBREOFFICE_INSTALLED, reason="LibreOffice not installed")
def test_odp_to_pdf(sample_odp: Path):
    """odp → pdf conversion succeeds."""
    engine = LibreOfficeEngine(auto_install=False)
    result = engine.transform(str(sample_odp), "pdf")
    assert isinstance(result, Succeed)
    assert result.output_path.exists()
    assert result.output_path.stat().st_size > 0
