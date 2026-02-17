"""LibreOffice 포맷 데이터 상수.

LibreOffice 공식 필터 목록을 기반으로 한 정적 포맷 레지스트리 데이터.
각 카테고리(Writer, Calc, Impress, Draw, Math, Graphic)별로 ``FormatInfo`` 인스턴스를 정의한다.
"""

from __future__ import annotations

from ..schemas.format_info import FormatInfo
from .categories import DocumentCategory

# ---------------------------------------------------------------------------
# Writer formats (T005)
# ---------------------------------------------------------------------------
WRITER_FORMATS: list[FormatInfo] = [
    # --- Native / ODF ---
    FormatInfo(
        "odt",
        "writer8",
        "application/vnd.oasis.opendocument.text",
        DocumentCategory.WRITER,
        True,
        True,
    ),
    FormatInfo(
        "ott",
        "writer8_template",
        "application/vnd.oasis.opendocument.text-template",
        DocumentCategory.WRITER,
        True,
        True,
    ),
    FormatInfo(
        "fodt",
        "OpenDocument Text Flat XML",
        "application/vnd.oasis.opendocument.text-flat-xml",
        DocumentCategory.WRITER,
        True,
        True,
    ),
    # --- Microsoft Word ---
    FormatInfo(
        "doc", "MS Word 97", "application/msword", DocumentCategory.WRITER, True, True
    ),
    FormatInfo(
        "docx",
        "MS Word 2007 XML",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        DocumentCategory.WRITER,
        True,
        True,
    ),
    FormatInfo(
        "dotx",
        "MS Word 2007 XML Template",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.template",
        DocumentCategory.WRITER,
        True,
        False,
    ),
    # --- Rich / Plain text ---
    FormatInfo(
        "rtf",
        "Rich Text Format",
        "application/rtf",
        DocumentCategory.WRITER,
        True,
        True,
    ),
    FormatInfo("txt", "Text", "text/plain", DocumentCategory.WRITER, True, True),
    # --- Web ---
    FormatInfo(
        "html", "HTML (StarWriter)", "text/html", DocumentCategory.WRITER, True, True
    ),
    # --- E-book ---
    FormatInfo(
        "epub", "EPUB", "application/epub+zip", DocumentCategory.WRITER, True, True
    ),
    # --- Portable Document ---
    FormatInfo(
        "pdf",
        "writer_pdf_Export",
        "application/pdf",
        DocumentCategory.WRITER,
        False,
        True,
    ),
    # --- Markdown ---
    FormatInfo("md", "Text", "text/markdown", DocumentCategory.WRITER, True, False),
    # --- Legacy / Other import ---
    FormatInfo("pages", "Apple Pages", None, DocumentCategory.WRITER, True, False),
    FormatInfo("hwp", "writer_MIZI_Hwp_97", None, DocumentCategory.WRITER, True, False),
    FormatInfo(
        "wpd",
        "WordPerfect",
        "application/vnd.wordperfect",
        DocumentCategory.WRITER,
        True,
        False,
    ),
    FormatInfo("wri", "MS Write", None, DocumentCategory.WRITER, True, False),
    FormatInfo(
        "abw", "AbiWord", "application/x-abiword", DocumentCategory.WRITER, True, False
    ),
    FormatInfo("lwp", "Lotus WordPro", None, DocumentCategory.WRITER, True, False),
    FormatInfo("pdb", "AportisDoc (Palm)", None, DocumentCategory.WRITER, True, False),
]

# ---------------------------------------------------------------------------
# Calc formats (T006)
# ---------------------------------------------------------------------------
CALC_FORMATS: list[FormatInfo] = [
    # --- Native / ODF ---
    FormatInfo(
        "ods",
        "calc8",
        "application/vnd.oasis.opendocument.spreadsheet",
        DocumentCategory.CALC,
        True,
        True,
    ),
    FormatInfo(
        "ots",
        "calc8_template",
        "application/vnd.oasis.opendocument.spreadsheet-template",
        DocumentCategory.CALC,
        True,
        True,
    ),
    FormatInfo(
        "fods",
        "OpenDocument Spreadsheet Flat XML",
        "application/vnd.oasis.opendocument.spreadsheet-flat-xml",
        DocumentCategory.CALC,
        True,
        True,
    ),
    # --- Microsoft Excel ---
    FormatInfo(
        "xls",
        "MS Excel 97",
        "application/vnd.ms-excel",
        DocumentCategory.CALC,
        True,
        True,
    ),
    FormatInfo(
        "xlsx",
        "Calc MS Excel 2007 XML",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        DocumentCategory.CALC,
        True,
        True,
    ),
    FormatInfo(
        "xltx",
        "Calc MS Excel 2007 XML Template",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.template",
        DocumentCategory.CALC,
        True,
        False,
    ),
    # --- Delimited text ---
    FormatInfo(
        "csv",
        "Text - txt - csv (StarCalc)",
        "text/csv",
        DocumentCategory.CALC,
        True,
        True,
    ),
    FormatInfo(
        "tsv",
        "Text - txt - csv (StarCalc)",
        "text/tab-separated-values",
        DocumentCategory.CALC,
        True,
        True,
    ),
    # --- Web ---
    FormatInfo(
        "html", "HTML (StarCalc)", "text/html", DocumentCategory.CALC, True, True
    ),
    # --- Portable Document ---
    FormatInfo(
        "pdf", "calc_pdf_Export", "application/pdf", DocumentCategory.CALC, False, True
    ),
    # --- Legacy / Other ---
    FormatInfo("numbers", "Apple Numbers", None, DocumentCategory.CALC, True, False),
    FormatInfo(
        "gnumeric",
        "Gnumeric Spreadsheet",
        "application/x-gnumeric",
        DocumentCategory.CALC,
        True,
        False,
    ),
    FormatInfo("dif", "DIF", None, DocumentCategory.CALC, True, True),
    FormatInfo("dbf", "dBASE", None, DocumentCategory.CALC, True, True),
    FormatInfo("slk", "SYLK", None, DocumentCategory.CALC, True, True),
    FormatInfo("wk1", "Lotus 1-2-3", None, DocumentCategory.CALC, True, False),
]

# ---------------------------------------------------------------------------
# Impress formats (T007)
# ---------------------------------------------------------------------------
IMPRESS_FORMATS: list[FormatInfo] = [
    # --- Native / ODF ---
    FormatInfo(
        "odp",
        "impress8",
        "application/vnd.oasis.opendocument.presentation",
        DocumentCategory.IMPRESS,
        True,
        True,
    ),
    FormatInfo(
        "otp",
        "impress8_template",
        "application/vnd.oasis.opendocument.presentation-template",
        DocumentCategory.IMPRESS,
        True,
        True,
    ),
    FormatInfo(
        "fodp",
        "OpenDocument Presentation Flat XML",
        "application/vnd.oasis.opendocument.presentation-flat-xml",
        DocumentCategory.IMPRESS,
        True,
        True,
    ),
    # --- Microsoft PowerPoint ---
    FormatInfo(
        "ppt",
        "MS PowerPoint 97",
        "application/vnd.ms-powerpoint",
        DocumentCategory.IMPRESS,
        True,
        True,
    ),
    FormatInfo(
        "pptx",
        "Impress MS PowerPoint 2007 XML",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        DocumentCategory.IMPRESS,
        True,
        True,
    ),
    FormatInfo(
        "potx",
        "Impress MS PowerPoint 2007 XML Template",
        "application/vnd.openxmlformats-officedocument.presentationml.template",
        DocumentCategory.IMPRESS,
        True,
        False,
    ),
    FormatInfo(
        "pps",
        "MS PowerPoint 97 AutoPlay",
        "application/vnd.ms-powerpoint",
        DocumentCategory.IMPRESS,
        True,
        True,
    ),
    FormatInfo(
        "ppsx",
        "Impress MS PowerPoint 2007 XML AutoPlay",
        "application/vnd.openxmlformats-officedocument.presentationml.slideshow",
        DocumentCategory.IMPRESS,
        True,
        True,
    ),
    # --- Portable Document ---
    FormatInfo(
        "pdf",
        "impress_pdf_Export",
        "application/pdf",
        DocumentCategory.IMPRESS,
        False,
        True,
    ),
    # --- Legacy ---
    FormatInfo("key", "Apple Keynote", None, DocumentCategory.IMPRESS, True, False),
    FormatInfo(
        "sxi", "StarOffice XML (Impress)", None, DocumentCategory.IMPRESS, True, False
    ),
]

# ---------------------------------------------------------------------------
# Draw formats (T008)
# ---------------------------------------------------------------------------
DRAW_FORMATS: list[FormatInfo] = [
    # --- Native / ODF ---
    FormatInfo(
        "odg",
        "draw8",
        "application/vnd.oasis.opendocument.graphics",
        DocumentCategory.DRAW,
        True,
        True,
    ),
    FormatInfo(
        "otg",
        "draw8_template",
        "application/vnd.oasis.opendocument.graphics-template",
        DocumentCategory.DRAW,
        True,
        False,
    ),
    FormatInfo(
        "fodg",
        "OpenDocument Drawing Flat XML",
        "application/vnd.oasis.opendocument.graphics-flat-xml",
        DocumentCategory.DRAW,
        True,
        True,
    ),
    # --- Portable Document ---
    FormatInfo(
        "pdf", "draw_pdf_Export", "application/pdf", DocumentCategory.DRAW, False, True
    ),
    # --- Vector ---
    FormatInfo(
        "svg", "draw_svg_Export", "image/svg+xml", DocumentCategory.DRAW, False, True
    ),
    # --- Microsoft / Other import ---
    FormatInfo(
        "vsd",
        "Visio Document",
        "application/vnd.visio",
        DocumentCategory.DRAW,
        True,
        False,
    ),
    FormatInfo(
        "vsdx",
        "Visio Document",
        "application/vnd.ms-visio.drawing.main+xml",
        DocumentCategory.DRAW,
        True,
        False,
    ),
    FormatInfo("pub", "Microsoft Publisher", None, DocumentCategory.DRAW, True, False),
    FormatInfo(
        "cdr",
        "CorelDRAW",
        "application/vnd.corel-draw",
        DocumentCategory.DRAW,
        True,
        False,
    ),
    FormatInfo("wpg", "WordPerfect Graphics", None, DocumentCategory.DRAW, True, False),
    FormatInfo(
        "cmx", "Corel Presentation Exchange", None, DocumentCategory.DRAW, True, False
    ),
    FormatInfo(
        "sxd", "StarOffice XML (Draw)", None, DocumentCategory.DRAW, True, False
    ),
]

# ---------------------------------------------------------------------------
# Math formats (T009)
# ---------------------------------------------------------------------------
MATH_FORMATS: list[FormatInfo] = [
    FormatInfo(
        "odf",
        "math8",
        "application/vnd.oasis.opendocument.formula",
        DocumentCategory.MATH,
        True,
        True,
    ),
    FormatInfo(
        "mml",
        "MathML XML (Math)",
        "application/mathml+xml",
        DocumentCategory.MATH,
        True,
        True,
    ),
    FormatInfo(
        "sxm", "StarOffice XML (Math)", None, DocumentCategory.MATH, True, False
    ),
    FormatInfo(
        "pdf", "math_pdf_Export", "application/pdf", DocumentCategory.MATH, False, True
    ),
]

# ---------------------------------------------------------------------------
# Graphic export formats (T010)
# ---------------------------------------------------------------------------
GRAPHIC_FORMATS: list[FormatInfo] = [
    FormatInfo("jpg", "jpg", "image/jpeg", DocumentCategory.GRAPHIC, False, True),
    FormatInfo("jpeg", "jpeg", "image/jpeg", DocumentCategory.GRAPHIC, False, True),
    FormatInfo("png", "png", "image/png", DocumentCategory.GRAPHIC, False, True),
    FormatInfo("svg", "svg", "image/svg+xml", DocumentCategory.GRAPHIC, False, True),
    FormatInfo("webp", "webp", "image/webp", DocumentCategory.GRAPHIC, False, True),
]

# ---------------------------------------------------------------------------
# Aggregated list of ALL formats
# ---------------------------------------------------------------------------
ALL_FORMATS: list[FormatInfo] = (
    WRITER_FORMATS
    + CALC_FORMATS
    + IMPRESS_FORMATS
    + DRAW_FORMATS
    + MATH_FORMATS
    + GRAPHIC_FORMATS
)
