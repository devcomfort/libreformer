"""LibreOffice 포맷 메타데이터의 정적 레지스트리."""

from __future__ import annotations

from ..schemas.format_info import FormatInfo
from .categories import DocumentCategory
from .data import ALL_FORMATS


class FormatRegistry:
    """LibreOffice 포맷 메타데이터의 정적 레지스트리.

    모든 메서드는 ``@staticmethod``이다. 인스턴스를 만들 필요 없이
    ``FormatRegistry.all_formats()`` 형태로 사용한다.
    """

    @staticmethod
    def all_formats() -> list[FormatInfo]:
        """등록된 모든 ``FormatInfo`` 객체를 반환한다."""
        return list(ALL_FORMATS)

    @staticmethod
    def supported_input_formats() -> set[str]:
        """``can_import=True``인 모든 확장자의 집합을 반환한다."""
        return {fmt.extension for fmt in ALL_FORMATS if fmt.can_import}

    @staticmethod
    def supported_output_formats() -> set[str]:
        """``can_export=True``인 모든 확장자의 집합을 반환한다."""
        return {fmt.extension for fmt in ALL_FORMATS if fmt.can_export}

    @staticmethod
    def can_convert(from_ext: str, to_ext: str) -> bool:
        """``from_ext`` → ``to_ext`` 변환이 가능한지 여부를 반환한다.

        확장자에 점(``"."``)이 포함되어 있으면 자동 제거한다.
        """
        from_ext = from_ext.lstrip(".").lower()
        to_ext = to_ext.lstrip(".").lower()
        input_ok = any(
            fmt.extension == from_ext and fmt.can_import for fmt in ALL_FORMATS
        )
        output_ok = any(
            fmt.extension == to_ext and fmt.can_export for fmt in ALL_FORMATS
        )
        return input_ok and output_ok

    @staticmethod
    def formats_by_category(
        category: str | DocumentCategory,
    ) -> list[FormatInfo]:
        """지정된 카테고리에 속하는 포맷만 반환한다.

        문자열 입력 시 대소문자를 무시한다 (``"Writer"`` == ``"writer"``).
        유효하지 않은 카테고리는 빈 리스트를 반환한다.
        """
        if isinstance(category, str):
            try:
                category = DocumentCategory(category.lower())
            except ValueError:
                return []
        return [fmt for fmt in ALL_FORMATS if fmt.category == category]

    @staticmethod
    def get_format(extension: str) -> list[FormatInfo]:
        """확장자로 포맷 정보를 조회한다.

        동일 확장자가 여러 카테고리에 존재할 수 있으므로 리스트로 반환한다.
        예: ``"html"`` → Writer HTML + Calc HTML.
        """
        extension = extension.lstrip(".").lower()
        return [fmt for fmt in ALL_FORMATS if fmt.extension == extension]

    @staticmethod
    def get_export_filter(from_ext: str, to_ext: str) -> str | None:
        """변환에 사용할 LibreOffice 필터 이름을 반환한다.

        매핑이 없으면 ``None``.
        """
        from_ext = from_ext.lstrip(".").lower()
        to_ext = to_ext.lstrip(".").lower()

        # 입력 확장자의 카테고리를 먼저 확인
        input_categories = {
            fmt.category
            for fmt in ALL_FORMATS
            if fmt.extension == from_ext and fmt.can_import
        }

        # 출력 확장자 중 입력 카테고리와 동일한 것을 찾기
        for fmt in ALL_FORMATS:
            if (
                fmt.extension == to_ext
                and fmt.can_export
                and fmt.category in input_categories
            ):
                return fmt.filter_name

        # 카테고리 무관하게 출력 가능한 필터 반환
        for fmt in ALL_FORMATS:
            if fmt.extension == to_ext and fmt.can_export:
                return fmt.filter_name

        return None
