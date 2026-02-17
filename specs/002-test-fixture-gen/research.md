# Research: Programmatic Test Fixture Generation

**Feature**: 002-test-fixture-gen  
**Date**: 2026-02-14  
**Status**: Complete

## Research Topics

### 1. python-docx를 사용한 구조화된 DOCX 생성

**Task**: python-docx로 제목, 본문, 테이블, 인라인 이미지가 포함된 .docx 파일 생성 방법 연구

**Decision**: `python-docx` 라이브러리의 `Document()` API 사용

**Rationale**:

- `Document()` → `add_heading()`, `add_paragraph()`, `add_table()`, `add_picture()` 순서로 호출하여 구조화된 문서 생성
- 이미지 삽입: `document.add_picture(image_stream, width=Inches(2))` — `BytesIO` 스트림을 직접 전달 가능 (파일 저장 불필요)
- 테이블: `document.add_table(rows, cols, style='Table Grid')` 후 cell 단위 텍스트 설정
- 저장: `document.save(path)` — 표준 .docx (OOXML) 형식
- python-docx는 Python 3.8+에서 안정적으로 동작하며, lxml 의존성만 추가됨

**Alternatives Considered**:

- `docx` (다른 패키지): 유지보수 중단, python-docx가 사실상 표준
- LibreOffice UNO API: 복잡하고 LibreOffice 설치 필수 — CI 재현성에 부적합

---

### 2. openpyxl를 사용한 구조화된 XLSX 생성

**Task**: openpyxl로 헤더, 숫자/문자열 데이터, 수식이 포함된 .xlsx 파일 생성 방법 연구

**Decision**: `openpyxl` 라이브러리의 `Workbook()` API 사용

**Rationale**:

- `Workbook()` → `ws = wb.active` → `ws.append([...])` 로 행 단위 데이터 추가
- 수식: `ws['E2'] = '=C2-D2'` 처럼 셀에 직접 수식 문자열 할당
- 헤더 스타일링: `ws['A1'].font = Font(bold=True)` — 선택적 (구조 검증엔 불필요)
- 저장: `wb.save(path)` — 표준 .xlsx (OOXML SpreadsheetML) 형식
- openpyxl은 Python 3.8+에서 안정적, et_xmlfile만 추가 의존

**Alternatives Considered**:

- `xlsxwriter`: 쓰기 전용이라 적합하나 openpyxl이 더 범용적이고 읽기도 지원
- `pandas.DataFrame.to_excel()`: 불필요한 pandas 의존성 추가 — fixture 용도로 과잉

---

### 3. python-pptx를 사용한 구조화된 PPTX 생성

**Task**: python-pptx로 제목 슬라이드, 내용 슬라이드, 이미지 슬라이드가 포함된 .pptx 파일 생성 방법 연구

**Decision**: `python-pptx` 라이브러리의 `Presentation()` API 사용

**Rationale**:

- `Presentation()` → `prs.slide_layouts[0]` (제목 슬라이드), `prs.slide_layouts[1]` (내용 슬라이드)
- 제목 슬라이드: `slide.shapes.title.text = "..."`, `slide.placeholders[1].text = "..."`
- 내용 슬라이드: `tf = slide.shapes.placeholders[1].text_frame` → `tf.add_paragraph()` 로 불릿 추가
- 이미지: `slide.shapes.add_picture(image_stream, left, top, width, height)` — BytesIO 지원
- 저장: `prs.save(path)` — 표준 .pptx (OOXML PresentationML) 형식

**Alternatives Considered**:

- LibreOffice UNO API: 복잡도, 외부 의존성
- 직접 XML 생성: 유지보수 어려움, python-pptx가 이미 잘 추상화

---

### 4. Pillow를 사용한 테스트용 PNG 이미지 생성

**Task**: Pillow로 문서 삽입용 테스트 이미지(100×100+ 픽셀, 단순 도형) 생성 방법 연구

**Decision**: `Pillow`의 `Image.new()` + `ImageDraw` API 사용

**Rationale**:

- `Image.new('RGB', (200, 200), color='white')` → 빈 캔버스 생성
- `ImageDraw.Draw(img)` → `draw.rectangle()`, `draw.ellipse()`, `draw.text()` 로 도형/텍스트 추가
- BytesIO로 저장: `img.save(buffer, format='PNG')` → `buffer.getvalue()` 로 bytes 반환
- python-docx/python-pptx에 `BytesIO(png_bytes)` 를 직접 전달하여 파일 I/O 최소화
- Pillow는 Python 3.8+에서 안정적, CI 환경에서도 pip install로 설치 가능

**Alternatives Considered**:

- 하드코딩된 1×1 PNG bytes: 유효하지만 시각적 검증 불가
- `struct`로 raw PNG 생성: 복잡하고 유지보수 어려움
- cairosvg: SVG→PNG 변환용이나 불필요한 의존성

---

### 5. odfpy를 사용한 ODF 포맷(odt/ods/odp) 생성

**Task**: odfpy로 Writer(odt), Calc(ods), Impress(odp) 파일 생성 방법 연구

**Decision**: `odfpy` 라이브러리 사용, SHOULD 요구사항으로 `pytest.importorskip` 적용

**Rationale**:

- **ODT**: `OpenDocumentText()` → `text.addElement(P(text="..."))` 방식으로 단락 추가
- **ODS**: `OpenDocumentSpreadsheet()` → `Table` → `TableRow` → `TableCell` 구조
- **ODP**: `OpenDocumentPresentation()` → `DrawPage` → `DrawFrame` → `DrawTextBox`
- odfpy API는 XML 노드 기반으로 python-docx/openpyxl보다 저수준이지만, 단순 문서 생성에는 충분
- odfpy에서의 이미지 삽입은 `DrawFrame` + `DrawImage` + `addPicture()` 메서드로 가능하나, API가 복잡함
- SHOULD 요구사항이므로 미설치 시 graceful skip 처리

**Alternatives Considered**:

- LibreOffice에서 docx→odt 변환: 순환 의존성 (LibreOffice 필요)
- 직접 ZIP+XML 생성: 유지보수 불가

---

### 6. pytest session-scope fixture 패턴 with tmp_path_factory

**Task**: session-scope fixture에서 tmp_path_factory를 사용하여 파일을 한 번만 생성하고 전 세션에서 재사용하는 패턴 연구

**Decision**: `@pytest.fixture(scope="session")` + `tmp_path_factory.mktemp()` 패턴 사용

**Rationale**:

```python
@pytest.fixture(scope="session")
def sample_docx(tmp_path_factory: pytest.TempPathFactory) -> Path:
    tmp_dir = tmp_path_factory.mktemp("fixtures")
    path = tmp_dir / "sample.docx"
    # ... 파일 생성 로직 ...
    return path
```

- `tmp_path_factory`는 session-scope에서 사용 가능 (반면 `tmp_path`는 function-scope 전용)
- `mktemp("fixtures")`는 고유한 임시 디렉토리를 생성 (pytest가 세션 종료 시 정리)
- session-scope로 인해 fixture는 전체 테스트 세션에서 **한 번만** 실행되어 성능 최적화
- 변환은 원본 파일을 읽기만 하므로 session-scope가 안전 (clarification에서 확인됨)
- function-scope인 기존 `sample_file` fixture와 이름 충돌 없도록 `sample_docx`, `sample_xlsx` 등 포맷별 이름 사용

**Alternatives Considered**:

- function-scope: 매 테스트마다 파일 재생성 — 10종 이상 포맷에서 성능 저하
- module-scope: 모듈 단위 재사용이나 cross-module 공유 불가
- `conftest.py` 외부 파일에 fixture 정의: pytest의 fixture discovery 규칙에 의해 작동하나, conftest.py가 표준

---

### 7. 텍스트 기반 포맷 생성 (RTF, HTML, CSV, TSV, TXT)

**Task**: 추가 라이브러리 없이 순수 문자열로 생성 가능한 포맷들의 생성 패턴 연구

**Decision**: Python 내장 모듈(`csv`, `pathlib`, `textwrap`)만으로 생성

**Rationale**:

- **RTF**: `r"{\rtf1\ansi {\b Title}\par Body text\par}"` 형식의 문자열 직접 작성
- **HTML**: `f"<html><body><h1>{title}</h1><p>{body}</p><table>...</table></body></html>"` 형식
- **CSV**: `csv.writer()` 사용, 표준 라이브러리
- **TSV**: `csv.writer(f, delimiter='\t')` 사용
- **TXT**: `Path.write_text()` 직접 사용
- 모두 추가 라이브러리 불필요, CI 재현성 100%

**Alternatives Considered**:

- `jinja2` 템플릿: 불필요한 의존성
- `python-rtf` 등 전용 라이브러리: 유지보수 중단 다수

---

### 8. 기존 테스트와의 fixture 이름 충돌 방지

**Task**: conftest.py의 session-scope fixture가 기존 test_engine.py의 function-scope `sample_file` fixture와 충돌하지 않는 방법 연구

**Decision**: 포맷별 고유 이름 사용 (`sample_docx`, `sample_xlsx` 등), `sample_file`은 기존 유지

**Rationale**:

- pytest fixture scoping 규칙: 같은 이름의 fixture가 conftest.py와 테스트 파일 모두에 있을 경우, **가장 가까운 scope** (테스트 파일 내부)가 우선
- 그러나 이름 충돌 자체를 피하는 것이 가장 안전
- 기존 `test_engine.py`의 `sample_file`과 `test_async_engine.py`의 `sample_file`, `sample_files` fixture는 그대로 유지
- 새 fixture는 모두 포맷 확장자를 포함하여 명명: `sample_docx`, `sample_xlsx`, `sample_pptx`, `sample_odt`, `sample_ods`, `sample_odp`, `sample_csv`, `sample_tsv`, `sample_html`, `sample_rtf`, `sample_txt`
- 경계 조건: `empty_docx`, `large_xlsx`, `unicode_docx`, `special_chars_txt`

**Alternatives Considered**:

- conftest.py에 `sample_file`도 정의: 기존 테스트의 동작 변경 위험
- fixture prefix (`fixture_docx`): 직관성 떨어짐

## Summary of Decisions

| #   | Topic         | Decision                           | Risk                                 |
| --- | ------------- | ---------------------------------- | ------------------------------------ |
| 1   | DOCX 생성     | python-docx `Document()` API       | Low — 안정적 라이브러리              |
| 2   | XLSX 생성     | openpyxl `Workbook()` API          | Low — 안정적 라이브러리              |
| 3   | PPTX 생성     | python-pptx `Presentation()` API   | Low — 안정적 라이브러리              |
| 4   | 이미지 생성   | Pillow `Image.new()` + `ImageDraw` | Low — CI 환경 호환                   |
| 5   | ODF 생성      | odfpy + `pytest.importorskip`      | Medium — API 저수준, SHOULD 요구사항 |
| 6   | Fixture scope | session + `tmp_path_factory`       | Low — 변환은 읽기 전용               |
| 7   | 텍스트 포맷   | 내장 모듈만 사용                   | Low — 의존성 없음                    |
| 8   | 이름 충돌     | 포맷별 고유 이름 (`sample_*`)      | Low — pytest 표준 패턴               |
