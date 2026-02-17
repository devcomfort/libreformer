from enum import Enum


class DocumentCategory(str, Enum):
    """LibreOffice 문서 카테고리 열거형.

    각 값은 LibreOffice 모듈에 대응한다.
    ``str`` mixin을 사용하므로 문자열 비교가 가능하다.
    """

    WRITER = "writer"
    CALC = "calc"
    IMPRESS = "impress"
    DRAW = "draw"
    MATH = "math"
    GRAPHIC = "graphic"
