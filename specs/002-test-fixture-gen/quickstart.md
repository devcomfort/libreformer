# Quickstart: Test Fixture Generation

**Feature**: 002-test-fixture-gen

## 1. 의존성 설치

```bash
# rye로 dev-dependencies 설치 (python-docx, openpyxl, python-pptx, Pillow, odfpy)
rye sync
```

## 2. 기존 fixture로 테스트 작성하기

conftest.py에 정의된 fixture를 테스트 함수 파라미터로 받으면 자동으로 샘플 파일이 생성됩니다.

```python
# tests/test_my_conversion.py
import shutil
import pytest
from pathlib import Path
from libreformer import LibreOfficeEngine, Succeed

LIBREOFFICE_INSTALLED = shutil.which("libreoffice") is not None


@pytest.mark.skipif(not LIBREOFFICE_INSTALLED, reason="LibreOffice not installed")
def test_docx_to_pdf(sample_docx: Path):
    """docx → pdf 변환 테스트. sample_docx는 conftest.py에서 자동 제공."""
    engine = LibreOfficeEngine(auto_install=False)
    result = engine.transform(str(sample_docx), "pdf")
    assert isinstance(result, Succeed)
    assert result.output_path.exists()
```

## 3. 사용 가능한 Fixture 목록

| Fixture             | 포맷  | 내용                                       |
| ------------------- | ----- | ------------------------------------------ |
| `sample_docx`       | .docx | 제품 사양서 (제목+본문+테이블+이미지)      |
| `sample_odt`        | .odt  | 제품 사양서 (odfpy 필요, 미설치 시 skip)   |
| `sample_rtf`        | .rtf  | RTF 마크업 텍스트                          |
| `sample_html`       | .html | HTML 마크업 텍스트                         |
| `sample_txt`        | .txt  | 일반 텍스트                                |
| `sample_xlsx`       | .xlsx | 월별 매출 보고서 (헤더+데이터+수식)        |
| `sample_ods`        | .ods  | 매출 보고서 (odfpy 필요, 미설치 시 skip)   |
| `sample_csv`        | .csv  | CSV 데이터                                 |
| `sample_tsv`        | .tsv  | TSV 데이터                                 |
| `sample_pptx`       | .pptx | 분기 실적 발표 (제목+내용+이미지 슬라이드) |
| `sample_odp`        | .odp  | 프레젠테이션 (odfpy 필요, 미설치 시 skip)  |
| `empty_docx`        | .docx | 빈 문서                                    |
| `large_xlsx`        | .xlsx | 1000+행 스프레드시트                       |
| `unicode_docx`      | .docx | 한/중/일/아랍/이모지 텍스트                |
| `special_chars_txt` | .txt  | 특수 문자, 탭, 개행                        |
| `test_image_bytes`  | bytes | PNG 이미지 (200×200, 문서 삽입용)          |

## 4. 여러 포맷 한 번에 테스트하기

```python
import pytest
from pathlib import Path
from libreformer import LibreOfficeEngine, Succeed

FORMATS = ["sample_docx", "sample_xlsx", "sample_pptx", "sample_csv", "sample_html"]

@pytest.mark.skipif(not LIBREOFFICE_INSTALLED, reason="LibreOffice not installed")
@pytest.mark.parametrize("fixture_name", FORMATS, indirect=False)
def test_format_to_pdf(fixture_name, request):
    """다양한 포맷의 pdf 변환 테스트."""
    sample_path = request.getfixturevalue(fixture_name)
    engine = LibreOfficeEngine(auto_install=False)
    result = engine.transform(str(sample_path), "pdf")
    assert isinstance(result, Succeed)
```

## 5. 새로운 fixture 추가 가이드

### Step 1: fixture_helpers에 생성 함수 추가

```python
# tests/fixture_helpers/writer.py

def create_my_format(path: Path) -> Path:
    """새 포맷의 샘플 파일을 생성한다."""
    # ... 파일 생성 로직 ...
    return path
```

### Step 2: conftest.py에 fixture 등록

```python
# tests/conftest.py

@pytest.fixture(scope="session")
def sample_my_format(tmp_path_factory: pytest.TempPathFactory) -> Path:
    tmp_dir = tmp_path_factory.mktemp("fixtures")
    path = tmp_dir / "sample.myformat"
    return create_my_format(path)
```

### Step 3: 테스트 작성

```python
# tests/test_fixture_writer.py (또는 적절한 카테고리 파일)

def test_my_format_to_pdf(sample_my_format: Path):
    engine = LibreOfficeEngine(auto_install=False)
    result = engine.transform(str(sample_my_format), "pdf")
    assert isinstance(result, Succeed)
```

## 6. 주의사항

- **Session scope**: fixture는 전체 테스트 세션에서 한 번만 생성됩니다. 파일을 수정하지 마세요.
- **odfpy 선택적**: odt/ods/odp fixture는 odfpy가 없으면 자동 skip됩니다.
- **LibreOffice 필수**: 변환 테스트는 LibreOffice가 설치된 환경에서만 실행됩니다.
- **기존 테스트 호환**: `test_engine.py`의 `sample_file` fixture는 그대로 유지됩니다.
