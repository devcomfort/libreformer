import pytest
from pathlib import Path
from libreformer import LibreOfficeEngine, Succeed, Failed
import shutil
import os

# LibreOffice가 설치되어 있는지 확인
LIBREOFFICE_INSTALLED = shutil.which("libreoffice") is not None


@pytest.fixture
def sample_file(tmp_path):
    d = tmp_path / "test.txt"
    d.write_text("Hello LibreOffice")
    return d


@pytest.mark.skipif(not LIBREOFFICE_INSTALLED, reason="LibreOffice not installed")
def test_transform_txt_to_pdf(sample_file):
    engine = LibreOfficeEngine(auto_install=False)
    result = engine.transform(str(sample_file), "pdf")

    if isinstance(result, Failed):
        pytest.fail(f"Transformation failed: {result.error_message}")

    assert isinstance(result, Succeed)
    assert result.output_path.exists()
    assert result.output_path.suffix == ".pdf"


@pytest.mark.skipif(not LIBREOFFICE_INSTALLED, reason="LibreOffice not installed")
def test_batch_transform(tmp_path):
    files = []
    for i in range(3):
        f = tmp_path / f"test_{i}.txt"
        f.write_text(f"Content {i}")
        files.append(str(f))

    # 병렬 변환 테스트
    engine = LibreOfficeEngine(auto_install=False)
    results = list(engine.transform_parallel(files, "pdf"))

    assert len(results) == 3
    for res in results:
        if isinstance(res, Failed):
            pytest.fail(
                f"Batch transformation failed for {res.file_path}: {res.error_message}"
            )
        assert isinstance(res, Succeed)
        assert res.output_path.exists()
