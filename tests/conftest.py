"""Central pytest fixtures for all test file generation.

All fixtures use session scope and tmp_path_factory for efficient
one-time file generation across the entire test session.
"""

import pytest
from pathlib import Path
import sys
import os

# Ensure tests/ directory is on the path for fixture_helpers imports
sys.path.insert(0, os.path.dirname(__file__))

from fixture_helpers.images import create_test_image
from fixture_helpers.writer import (
    create_docx,
    create_odt,
    create_rtf,
    create_html,
    create_txt,
    create_empty_docx,
    create_unicode_docx,
    create_special_chars_txt,
)
from fixture_helpers.calc import (
    create_xlsx,
    create_ods,
    create_csv_file,
    create_tsv,
    create_empty_xlsx,
    create_large_xlsx,
)
from fixture_helpers.impress import (
    create_pptx,
    create_odp,
    create_empty_pptx,
)


# ---------------------------------------------------------------------------
# Image bytes fixture (foundational — used by docx, pptx fixtures)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def test_image_bytes() -> bytes:
    """Session-scope PNG image bytes for embedding in documents."""
    return create_test_image(200, 200)


# ---------------------------------------------------------------------------
# Writer fixtures (US1 + US5)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def sample_docx(
    tmp_path_factory: pytest.TempPathFactory, test_image_bytes: bytes
) -> Path:
    """Session-scope .docx sample with heading, paragraphs, table, image."""
    tmp_dir = tmp_path_factory.mktemp("fixtures")
    path = tmp_dir / "sample.docx"
    return create_docx(path, test_image_bytes)


@pytest.fixture(scope="session")
def sample_odt(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Session-scope .odt sample. Skips if odfpy not installed."""
    import pytest

    pytest.importorskip("odf")
    tmp_dir = tmp_path_factory.mktemp("fixtures")
    path = tmp_dir / "sample.odt"
    return create_odt(path)


@pytest.fixture(scope="session")
def sample_rtf(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Session-scope .rtf sample."""
    tmp_dir = tmp_path_factory.mktemp("fixtures")
    path = tmp_dir / "sample.rtf"
    return create_rtf(path)


@pytest.fixture(scope="session")
def sample_html(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Session-scope .html sample."""
    tmp_dir = tmp_path_factory.mktemp("fixtures")
    path = tmp_dir / "sample.html"
    return create_html(path)


@pytest.fixture(scope="session")
def sample_txt(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Session-scope .txt sample."""
    tmp_dir = tmp_path_factory.mktemp("fixtures")
    path = tmp_dir / "sample.txt"
    return create_txt(path)


# ---------------------------------------------------------------------------
# Calc fixtures (US2)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def sample_xlsx(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Session-scope .xlsx sample with headers, data, formulas."""
    tmp_dir = tmp_path_factory.mktemp("fixtures")
    path = tmp_dir / "sample.xlsx"
    return create_xlsx(path)


@pytest.fixture(scope="session")
def sample_ods(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Session-scope .ods sample. Skips if odfpy not installed."""
    import pytest

    pytest.importorskip("odf")
    tmp_dir = tmp_path_factory.mktemp("fixtures")
    path = tmp_dir / "sample.ods"
    return create_ods(path)


@pytest.fixture(scope="session")
def sample_csv(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Session-scope .csv sample."""
    tmp_dir = tmp_path_factory.mktemp("fixtures")
    path = tmp_dir / "sample.csv"
    return create_csv_file(path)


@pytest.fixture(scope="session")
def sample_tsv(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Session-scope .tsv sample."""
    tmp_dir = tmp_path_factory.mktemp("fixtures")
    path = tmp_dir / "sample.tsv"
    return create_tsv(path)


# ---------------------------------------------------------------------------
# Impress fixtures (US3)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def sample_pptx(
    tmp_path_factory: pytest.TempPathFactory, test_image_bytes: bytes
) -> Path:
    """Session-scope .pptx sample with title, content, and image slides."""
    tmp_dir = tmp_path_factory.mktemp("fixtures")
    path = tmp_dir / "sample.pptx"
    return create_pptx(path, test_image_bytes)


@pytest.fixture(scope="session")
def sample_odp(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Session-scope .odp sample. Skips if odfpy not installed."""
    import pytest

    pytest.importorskip("odf")
    tmp_dir = tmp_path_factory.mktemp("fixtures")
    path = tmp_dir / "sample.odp"
    return create_odp(path)


# ---------------------------------------------------------------------------
# Edge case fixtures (US6)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def empty_docx(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Session-scope empty .docx with no content."""
    tmp_dir = tmp_path_factory.mktemp("fixtures")
    path = tmp_dir / "empty.docx"
    return create_empty_docx(path)


@pytest.fixture(scope="session")
def empty_xlsx(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Session-scope empty .xlsx with no data."""
    tmp_dir = tmp_path_factory.mktemp("fixtures")
    path = tmp_dir / "empty.xlsx"
    return create_empty_xlsx(path)


@pytest.fixture(scope="session")
def empty_pptx(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Session-scope empty .pptx with no slides."""
    tmp_dir = tmp_path_factory.mktemp("fixtures")
    path = tmp_dir / "empty.pptx"
    return create_empty_pptx(path)


@pytest.fixture(scope="session")
def large_xlsx(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Session-scope large .xlsx with 1000+ rows."""
    tmp_dir = tmp_path_factory.mktemp("fixtures")
    path = tmp_dir / "large.xlsx"
    return create_large_xlsx(path)


@pytest.fixture(scope="session")
def unicode_docx(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Session-scope .docx with multi-language unicode content."""
    tmp_dir = tmp_path_factory.mktemp("fixtures")
    path = tmp_dir / "unicode.docx"
    return create_unicode_docx(path)


@pytest.fixture(scope="session")
def special_chars_txt(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Session-scope .txt with special characters."""
    tmp_dir = tmp_path_factory.mktemp("fixtures")
    path = tmp_dir / "special_chars.txt"
    return create_special_chars_txt(path)
