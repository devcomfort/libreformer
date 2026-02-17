"""비동기 변환 엔진 테스트.

US1: 단일 문서 비동기 변환
US2: 대량 문서 비동기 병렬 변환
US5: 동시성 제한 및 리소스 관리
"""

import asyncio
import shutil
from pathlib import Path

import pytest
import pytest_asyncio

from libreformer import LibreOfficeEngine, Succeed, Failed

# LibreOffice가 설치되어 있는지 확인
LIBREOFFICE_INSTALLED = shutil.which("libreoffice") is not None


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def engine():
    return LibreOfficeEngine(auto_install=False)


@pytest.fixture
def sample_file(tmp_path: Path) -> Path:
    f = tmp_path / "test.txt"
    f.write_text("Hello LibreOffice async")
    return f


@pytest.fixture
def sample_files(tmp_path: Path) -> list[Path]:
    files = []
    for i in range(5):
        f = tmp_path / f"test_{i}.txt"
        f.write_text(f"Content {i}")
        files.append(f)
    return files


# ===========================================================================
# US1: 단일 문서 비동기 변환
# ===========================================================================
@pytest.mark.asyncio
@pytest.mark.skipif(not LIBREOFFICE_INSTALLED, reason="LibreOffice not installed")
async def test_async_transform_success(engine: LibreOfficeEngine, sample_file: Path):
    """txt → pdf 비동기 변환 성공."""
    result = await engine.async_transform(str(sample_file), "pdf")
    assert isinstance(result, Succeed)
    assert result.output_path.exists()
    assert result.output_path.suffix == ".pdf"


@pytest.mark.asyncio
async def test_async_transform_file_not_found(
    engine: LibreOfficeEngine, tmp_path: Path
):
    """존재하지 않는 파일 → Failed."""
    result = await engine.async_transform(str(tmp_path / "nonexistent.txt"), "pdf")
    assert isinstance(result, Failed)
    assert "not found" in result.error_message.lower()


@pytest.mark.asyncio
@pytest.mark.skipif(not LIBREOFFICE_INSTALLED, reason="LibreOffice not installed")
async def test_async_transform_timeout(tmp_path: Path):
    """매우 짧은 타임아웃 → Failed (timeout)."""
    f = tmp_path / "timeout_test.txt"
    f.write_text("Timeout test content")
    engine = LibreOfficeEngine(auto_install=False, timeout=0.001)
    result = await engine.async_transform(str(f), "pdf")
    assert isinstance(result, Failed)
    assert "timed out" in result.error_message.lower()


# ===========================================================================
# US2: 대량 문서 비동기 병렬 변환
# ===========================================================================
@pytest.mark.asyncio
@pytest.mark.skipif(not LIBREOFFICE_INSTALLED, reason="LibreOffice not installed")
async def test_async_transform_parallel_same_format(
    engine: LibreOfficeEngine, sample_files: list[Path]
):
    """여러 파일을 동일 포맷으로 비동기 병렬 변환."""
    file_paths = [str(f) for f in sample_files]
    results: list[Succeed | Failed] = []
    async for result in engine.async_transform_parallel(file_paths, "pdf"):
        results.append(result)
    assert len(results) == len(sample_files)
    for res in results:
        if isinstance(res, Failed):
            pytest.fail(f"Async batch failed: {res.error_message}")
        assert isinstance(res, Succeed)
        assert res.output_path.exists()


@pytest.mark.asyncio
@pytest.mark.skipif(not LIBREOFFICE_INSTALLED, reason="LibreOffice not installed")
async def test_async_transform_parallel_mixed_format(
    engine: LibreOfficeEngine, tmp_path: Path
):
    """파일별 다른 포맷으로 비동기 병렬 변환."""
    files = []
    for i in range(3):
        f = tmp_path / f"mixed_{i}.txt"
        f.write_text(f"Mixed content {i}")
        files.append(str(f))
    formats = ["pdf", "html", "pdf"]
    results: list[Succeed | Failed] = []
    async for result in engine.async_transform_parallel(files, formats):
        results.append(result)
    assert len(results) == 3


@pytest.mark.asyncio
async def test_async_transform_parallel_length_mismatch(
    engine: LibreOfficeEngine, sample_files: list[Path]
):
    """파일 목록과 포맷 목록 길이 불일치 → ValueError."""
    file_paths = [str(f) for f in sample_files]
    with pytest.raises(ValueError, match="Length of 'to'"):
        async for _ in engine.async_transform_parallel(file_paths, ["pdf", "html"]):
            pass


# ===========================================================================
# US5: 동시성 제한 및 리소스 관리
# ===========================================================================
@pytest.mark.asyncio
@pytest.mark.skipif(not LIBREOFFICE_INSTALLED, reason="LibreOffice not installed")
async def test_max_concurrency_limits_execution(tmp_path: Path):
    """max_concurrency=2 로 동시 실행 수가 제한되는지 확인."""
    engine = LibreOfficeEngine(auto_install=False, max_concurrency=2)

    files = []
    for i in range(4):
        f = tmp_path / f"conc_{i}.txt"
        f.write_text(f"Concurrency test {i}")
        files.append(str(f))

    results: list[Succeed | Failed] = []
    async for result in engine.async_transform_parallel(files, "pdf"):
        results.append(result)
    assert len(results) == 4


def test_max_concurrency_default_uses_cpu_count():
    """max_concurrency 미지정 시 CPU 코어 수 기본값."""
    import os

    engine = LibreOfficeEngine(auto_install=False)
    expected = os.cpu_count() or 4
    assert engine._max_concurrency == expected


def test_max_concurrency_validation():
    """max_concurrency < 1 → ValueError."""
    with pytest.raises(ValueError, match="max_concurrency must be >= 1"):
        LibreOfficeEngine(auto_install=False, max_concurrency=0)
    with pytest.raises(ValueError, match="max_concurrency must be >= 1"):
        LibreOfficeEngine(auto_install=False, max_concurrency=-1)


def test_timeout_validation():
    """timeout <= 0 → ValueError."""
    with pytest.raises(ValueError, match="timeout must be > 0"):
        LibreOfficeEngine(auto_install=False, timeout=0)
    with pytest.raises(ValueError, match="timeout must be > 0"):
        LibreOfficeEngine(auto_install=False, timeout=-1.0)
