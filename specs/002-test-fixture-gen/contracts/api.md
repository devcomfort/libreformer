# API Contracts: Programmatic Test Fixture Generation

**Feature**: 002-test-fixture-gen  
**Date**: 2026-02-14  
**Type**: Python pytest fixture API (내부 테스트 인프라)

## 1. Fixture Helper Functions (`tests/fixture_helpers/`)

### 1.1 `images.py` — 이미지 생성 헬퍼

```python
def create_test_image(
    width: int = 200,
    height: int = 200,
) -> bytes:
    """문서 삽입용 테스트 PNG 이미지를 프로그래밍 생성한다.

    Args:
        width: 이미지 너비 (픽셀). 최소 100.
        height: 이미지 높이 (픽셀). 최소 100.

    Returns:
        PNG 형식의 이미지 바이너리 데이터.

    Raises:
        ImportError: Pillow가 설치되지 않은 경우.

    Notes:
        - 흰색 배경에 파란색 직사각형, 하늘색 타원, "TEST" 텍스트 포함.
        - 결과 bytes는 python-docx/python-pptx의 add_picture()에 BytesIO로 전달 가능.
    """
```

### 1.2 `writer.py` — Writer 계열 파일 생성

```python
def create_docx(path: Path, image_bytes: bytes | None = None) -> Path:
    """제목, 본문, 테이블, 이미지가 포함된 .docx 파일을 생성한다.

    Args:
        path: 생성할 파일 경로.
        image_bytes: 인라인 삽입할 PNG 이미지 (None이면 이미지 생략).

    Returns:
        생성된 파일의 Path.

    Raises:
        ImportError: python-docx가 설치되지 않은 경우.

    Data: "제품 사양서" 시나리오 (FR-016).
    """

def create_odt(path: Path) -> Path:
    """제목, 본문, 테이블이 포함된 .odt 파일을 생성한다.

    Args:
        path: 생성할 파일 경로.

    Returns:
        생성된 파일의 Path.

    Raises:
        ImportError: odfpy가 설치되지 않은 경우 (pytest.importorskip 처리).
    """

def create_rtf(path: Path) -> Path:
    """RTF 마크업이 포함된 .rtf 파일을 생성한다. 추가 라이브러리 불필요."""

def create_html(path: Path) -> Path:
    """HTML 마크업이 포함된 .html 파일을 생성한다. 추가 라이브러리 불필요."""

def create_txt(path: Path) -> Path:
    """일반 텍스트 .txt 파일을 생성한다. 추가 라이브러리 불필요."""
```

### 1.3 `calc.py` — Calc 계열 파일 생성

```python
def create_xlsx(path: Path) -> Path:
    """헤더, 숫자/문자열 데이터, 수식이 포함된 .xlsx 파일을 생성한다.

    Args:
        path: 생성할 파일 경로.

    Returns:
        생성된 파일의 Path.

    Raises:
        ImportError: openpyxl이 설치되지 않은 경우.

    Data: "월별 매출 보고서" 시나리오 (FR-017).
          12개월 × 3지역, SUM/AVERAGE 수식 포함.
    """

def create_ods(path: Path) -> Path:
    """헤더, 데이터가 포함된 .ods 파일을 생성한다.

    Raises:
        ImportError: odfpy가 설치되지 않은 경우 (pytest.importorskip 처리).
    """

def create_csv(path: Path) -> Path:
    """CSV 포맷 파일을 생성한다. 표준 라이브러리 csv 모듈 사용."""

def create_tsv(path: Path) -> Path:
    """TSV(탭 구분) 포맷 파일을 생성한다. 표준 라이브러리 csv 모듈 사용."""
```

### 1.4 `impress.py` — Impress 계열 파일 생성

```python
def create_pptx(path: Path, image_bytes: bytes | None = None) -> Path:
    """제목/내용/이미지 슬라이드가 포함된 .pptx 파일을 생성한다.

    Args:
        path: 생성할 파일 경로.
        image_bytes: 이미지 슬라이드에 삽입할 PNG (None이면 생략).

    Returns:
        생성된 파일의 Path.

    Raises:
        ImportError: python-pptx가 설치되지 않은 경우.

    Data: "분기 실적 발표" 시나리오 (FR-018).
    """

def create_odp(path: Path) -> Path:
    """제목, 내용 슬라이드가 포함된 .odp 파일을 생성한다.

    Raises:
        ImportError: odfpy가 설치되지 않은 경우 (pytest.importorskip 처리).
    """
```

---

## 2. Pytest Fixtures (`tests/conftest.py`)

### 2.1 공통 패턴

모든 fixture는 다음 패턴을 따른다:

```python
@pytest.fixture(scope="session")
def sample_{format}(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """session-scope {format} 샘플 파일 fixture.

    Returns:
        생성된 {format} 파일의 Path (tmp_path_factory 하위).
    """
```

### 2.2 Fixture 목록

#### Writer 계열

| Fixture                                                   | Returns    | Dependencies | FR     |
| --------------------------------------------------------- | ---------- | ------------ | ------ |
| `test_image_bytes() -> bytes`                             | PNG bytes  | Pillow       | FR-012 |
| `sample_docx(tmp_path_factory, test_image_bytes) -> Path` | .docx 경로 | python-docx  | FR-004 |
| `sample_odt(tmp_path_factory) -> Path`                    | .odt 경로  | odfpy (skip) | FR-005 |
| `sample_rtf(tmp_path_factory) -> Path`                    | .rtf 경로  | —            | FR-006 |
| `sample_html(tmp_path_factory) -> Path`                   | .html 경로 | —            | FR-006 |
| `sample_txt(tmp_path_factory) -> Path`                    | .txt 경로  | —            | FR-006 |

#### Calc 계열

| Fixture                                 | Returns    | Dependencies | FR     |
| --------------------------------------- | ---------- | ------------ | ------ |
| `sample_xlsx(tmp_path_factory) -> Path` | .xlsx 경로 | openpyxl     | FR-007 |
| `sample_ods(tmp_path_factory) -> Path`  | .ods 경로  | odfpy (skip) | FR-008 |
| `sample_csv(tmp_path_factory) -> Path`  | .csv 경로  | —            | FR-009 |
| `sample_tsv(tmp_path_factory) -> Path`  | .tsv 경로  | —            | FR-009 |

#### Impress 계열

| Fixture                                                   | Returns    | Dependencies | FR     |
| --------------------------------------------------------- | ---------- | ------------ | ------ |
| `sample_pptx(tmp_path_factory, test_image_bytes) -> Path` | .pptx 경로 | python-pptx  | FR-010 |
| `sample_odp(tmp_path_factory) -> Path`                    | .odp 경로  | odfpy (skip) | FR-011 |

#### 경계 조건

| Fixture                                       | Returns       | Dependencies | FR     |
| --------------------------------------------- | ------------- | ------------ | ------ |
| `empty_docx(tmp_path_factory) -> Path`        | 빈 .docx      | python-docx  | FR-015 |
| `empty_xlsx(tmp_path_factory) -> Path`        | 빈 .xlsx      | openpyxl     | FR-015 |
| `empty_pptx(tmp_path_factory) -> Path`        | 빈 .pptx      | python-pptx  | FR-015 |
| `large_xlsx(tmp_path_factory) -> Path`        | 1000+행 .xlsx | openpyxl     | FR-015 |
| `unicode_docx(tmp_path_factory) -> Path`      | 다국어 .docx  | python-docx  | FR-015 |
| `special_chars_txt(tmp_path_factory) -> Path` | 특수문자 .txt | —            | FR-015 |

---

## 3. Test Files

### 3.1 공통 패턴

```python
import shutil
import pytest
from pathlib import Path
from libreformer import LibreOfficeEngine, Succeed, Failed

LIBREOFFICE_INSTALLED = shutil.which("libreoffice") is not None

@pytest.mark.skipif(not LIBREOFFICE_INSTALLED, reason="LibreOffice not installed")
def test_{format}_to_pdf(sample_{format}: Path):
    engine = LibreOfficeEngine(auto_install=False)
    result = engine.transform(str(sample_{format}), "pdf")
    assert isinstance(result, Succeed)
    assert result.output_path.exists()
    assert result.output_path.stat().st_size > 0
```

### 3.2 Test File 목록

| File                      | Fixtures Used                                                                   | Test Count (예상) |
| ------------------------- | ------------------------------------------------------------------------------- | ----------------- |
| `test_fixture_writer.py`  | sample_docx, sample_odt, sample_rtf, sample_html, sample_txt                    | 5-7               |
| `test_fixture_calc.py`    | sample_xlsx, sample_ods, sample_csv, sample_tsv                                 | 4-5               |
| `test_fixture_impress.py` | sample_pptx, sample_odp                                                         | 3-4               |
| `test_fixture_edge.py`    | empty_docx, empty_xlsx, empty_pptx, large_xlsx, unicode_docx, special_chars_txt | 6-7               |

---

## 4. Dependencies (`pyproject.toml`)

```toml
[tool.rye]
dev-dependencies = [
    "pytest>=9.0.2",
    "pytest-asyncio>=0.23.0",
    # Feature 002 additions:
    "python-docx>=1.1.0",
    "openpyxl>=3.1.0",
    "python-pptx>=0.6.23",
    "Pillow>=10.0.0",
    "odfpy>=1.4.1",
]
```
