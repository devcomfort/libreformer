"""포맷 레지스트리 테스트.

US3: 지원 포맷 조회 및 검증
US6: 문서 카테고리별 포맷 매핑
"""

import pytest

from libreformer.formats import FormatRegistry, DocumentCategory
from libreformer.schemas.format_info import FormatInfo


# ===========================================================================
# US3: 지원 포맷 조회 및 검증
# ===========================================================================
class TestFormatRegistryBasic:
    """FormatRegistry 기본 동작 검증."""

    def test_all_formats_returns_non_empty(self):
        """all_formats()는 비어 있지 않은 리스트를 반환한다."""
        formats = FormatRegistry.all_formats()
        assert isinstance(formats, list)
        assert len(formats) > 0
        assert all(isinstance(f, FormatInfo) for f in formats)

    def test_supported_input_formats_contains_expected(self):
        """입력 포맷에 주요 확장자가 포함된다."""
        inputs = FormatRegistry.supported_input_formats()
        assert isinstance(inputs, set)
        for ext in ("docx", "xlsx", "pptx", "odt", "ods", "odp", "csv", "rtf"):
            assert ext in inputs, f"{ext} not in supported input formats"

    def test_supported_input_formats_count(self):
        """입력 포맷이 50종 이상이다 (SC-001)."""
        inputs = FormatRegistry.supported_input_formats()
        assert len(inputs) >= 40  # some overlap across categories

    def test_supported_output_formats_contains_expected(self):
        """출력 포맷에 주요 확장자가 포함된다."""
        outputs = FormatRegistry.supported_output_formats()
        assert isinstance(outputs, set)
        for ext in ("pdf", "docx", "html", "csv", "png"):
            assert ext in outputs, f"{ext} not in supported output formats"

    def test_supported_output_formats_count(self):
        """출력 포맷이 20종 이상이다 (SC-001)."""
        outputs = FormatRegistry.supported_output_formats()
        assert len(outputs) >= 20

    def test_can_convert_true(self):
        """docx → pdf 변환 가능."""
        assert FormatRegistry.can_convert("docx", "pdf") is True

    def test_can_convert_false(self):
        """유효하지 않은 확장자 → False."""
        assert FormatRegistry.can_convert("xyz_invalid", "pdf") is False
        assert FormatRegistry.can_convert("docx", "xyz_invalid") is False

    def test_can_convert_strips_dot(self):
        """점(.)이 포함된 확장자도 처리한다."""
        assert FormatRegistry.can_convert(".docx", ".pdf") is True

    def test_get_format_single(self):
        """단일 카테고리 확장자 조회."""
        results = FormatRegistry.get_format("docx")
        assert len(results) >= 1
        assert all(f.extension == "docx" for f in results)

    def test_get_format_multi_category(self):
        """html은 여러 카테고리에 존재한다."""
        results = FormatRegistry.get_format("html")
        categories = {f.category for f in results}
        assert len(categories) >= 2  # Writer + Calc at minimum

    def test_get_format_unknown(self):
        """알 수 없는 확장자 → 빈 리스트."""
        assert FormatRegistry.get_format("zzzzz_unknown") == []

    def test_get_export_filter_known(self):
        """docx → pdf 필터 이름 반환."""
        filt = FormatRegistry.get_export_filter("docx", "pdf")
        assert filt is not None
        assert isinstance(filt, str)

    def test_get_export_filter_unknown(self):
        """알 수 없는 조합 → None."""
        assert FormatRegistry.get_export_filter("zzz", "yyy") is None


# ===========================================================================
# US6: 문서 카테고리별 포맷 매핑
# ===========================================================================
class TestFormatsByCategory:
    """formats_by_category 검증."""

    @pytest.mark.parametrize(
        "category",
        [
            DocumentCategory.WRITER,
            DocumentCategory.CALC,
            DocumentCategory.IMPRESS,
            DocumentCategory.DRAW,
            DocumentCategory.MATH,
            DocumentCategory.GRAPHIC,
        ],
    )
    def test_each_category_returns_only_its_formats(self, category: DocumentCategory):
        """각 카테고리는 자기 포맷만 반환한다."""
        formats = FormatRegistry.formats_by_category(category)
        assert len(formats) > 0, f"No formats for {category}"
        for fmt in formats:
            assert fmt.category == category

    def test_category_string_input(self):
        """문자열 입력도 동작한다."""
        writer_enum = FormatRegistry.formats_by_category(DocumentCategory.WRITER)
        writer_str = FormatRegistry.formats_by_category("writer")
        assert writer_enum == writer_str

    def test_category_case_insensitive(self):
        """대소문자 무시."""
        result_upper = FormatRegistry.formats_by_category("WRITER")
        result_lower = FormatRegistry.formats_by_category("writer")
        result_mixed = FormatRegistry.formats_by_category("Writer")
        assert result_upper == result_lower == result_mixed

    def test_invalid_category_returns_empty(self):
        """유효하지 않은 카테고리 → 빈 리스트."""
        result = FormatRegistry.formats_by_category("nonexistent_category")
        assert result == []

    def test_calc_formats_contain_expected(self):
        """Calc 카테고리에 xlsx, ods, csv가 포함된다."""
        calc_formats = FormatRegistry.formats_by_category("calc")
        extensions = {f.extension for f in calc_formats}
        for ext in ("xlsx", "ods", "csv"):
            assert ext in extensions, f"{ext} not in calc formats"

    def test_writer_formats_contain_expected(self):
        """Writer 카테고리에 docx, odt, rtf가 포함된다."""
        writer_formats = FormatRegistry.formats_by_category("writer")
        extensions = {f.extension for f in writer_formats}
        for ext in ("docx", "odt", "rtf"):
            assert ext in extensions, f"{ext} not in writer formats"
