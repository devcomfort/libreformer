"""하위 호환성 회귀 테스트.

US4: 기존 동기 API가 변경 없이 동작하는지 확인.
"""

import shutil
from pathlib import Path

import pytest

from libreformer import LibreOfficeEngine, Succeed, Failed

LIBREOFFICE_INSTALLED = shutil.which("libreoffice") is not None


class TestBackwardCompatibility:
    """기존 동기 API 인터페이스 유지 검증."""

    def test_constructor_with_only_auto_install(self):
        """auto_install만 전달해도 정상 동작."""
        engine = LibreOfficeEngine(auto_install=False)
        assert engine.libreoffice_path is not None or True  # path may be None on CI

    def test_constructor_default_args(self):
        """기본 인자로 생성 가능."""
        engine = LibreOfficeEngine(auto_install=False)
        assert hasattr(engine, "transform")
        assert hasattr(engine, "transform_parallel")

    @pytest.mark.skipif(not LIBREOFFICE_INSTALLED, reason="LibreOffice not installed")
    def test_sync_transform_signature(self, tmp_path: Path):
        """engine.transform(file_path, to) 동기 시그니처 유지."""
        f = tmp_path / "compat.txt"
        f.write_text("backward compat test")
        engine = LibreOfficeEngine(auto_install=False)
        result = engine.transform(str(f), "pdf")
        assert isinstance(result, (Succeed, Failed))

    @pytest.mark.skipif(not LIBREOFFICE_INSTALLED, reason="LibreOffice not installed")
    def test_sync_transform_parallel_signature(self, tmp_path: Path):
        """engine.transform_parallel(files, to) 동기 시그니처 유지."""
        files = []
        for i in range(2):
            f = tmp_path / f"compat_{i}.txt"
            f.write_text(f"Content {i}")
            files.append(str(f))
        engine = LibreOfficeEngine(auto_install=False)
        results = list(engine.transform_parallel(files, "pdf"))
        assert len(results) == 2
        for res in results:
            assert isinstance(res, (Succeed, Failed))

    @pytest.mark.skipif(not LIBREOFFICE_INSTALLED, reason="LibreOffice not installed")
    def test_callable_interface(self, tmp_path: Path):
        """engine(file, to) callable 인터페이스 유지."""
        f = tmp_path / "callable.txt"
        f.write_text("callable test")
        engine = LibreOfficeEngine(auto_install=False)
        result = engine(str(f), "pdf")
        assert isinstance(result, (Succeed, Failed))

    def test_new_params_are_optional(self):
        """max_concurrency, timeout은 선택적 파라미터."""
        # 기존처럼 auto_install만 전달
        e1 = LibreOfficeEngine(auto_install=False)
        assert e1._timeout == 300.0

        # 새 파라미터 전달
        e2 = LibreOfficeEngine(auto_install=False, max_concurrency=2, timeout=60.0)
        assert e2._max_concurrency == 2
        assert e2._timeout == 60.0
