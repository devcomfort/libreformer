from __future__ import annotations

from dataclasses import dataclass

from ..formats.categories import DocumentCategory


@dataclass(frozen=True)
class FormatInfo:
    """단일 파일 포맷의 메타데이터.

    Attributes:
        extension: 파일 확장자 (점 없이, 예: ``"docx"``).
        filter_name: LibreOffice 필터 API 이름.
        mime_type: MIME 타입. 알 수 없으면 ``None``.
        category: 소속 문서 카테고리.
        can_import: 이 포맷을 입력으로 읽을 수 있는지 여부.
        can_export: 이 포맷으로 출력할 수 있는지 여부.
    """

    extension: str
    filter_name: str
    mime_type: str | None
    category: DocumentCategory
    can_import: bool
    can_export: bool
