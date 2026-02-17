# Data Model: Programmatic Test Fixture Generation

**Feature**: 002-test-fixture-gen  
**Date**: 2026-02-14

## Entities

### 1. TestFixture (pytest fixture 함수)

conftest.py에 정의되는 pytest fixture. 각 포맷별 샘플 파일을 생성하고 `Path` 객체를 반환한다.

| Field        | Type                                           | Description                                                       |
| ------------ | ---------------------------------------------- | ----------------------------------------------------------------- |
| name         | `str`                                          | fixture 함수 이름 (예: `sample_docx`)                             |
| scope        | `Literal["session"]`                           | pytest fixture scope — 항상 session                               |
| format       | `str`                                          | 대상 파일 확장자 (예: `docx`, `xlsx`)                             |
| category     | `Literal["writer", "calc", "impress", "edge"]` | 문서 카테고리                                                     |
| requires_lib | `str \| None`                                  | 필요한 외부 라이브러리 (예: `python-docx`, `None` for text-based) |
| has_image    | `bool`                                         | 인라인 이미지 포함 여부                                           |
| returns      | `Path`                                         | `tmp_path_factory`로 생성된 파일 경로                             |

#### Fixture 목록

| Fixture Name        | Format | Category | Library      | Image | FR                     |
| ------------------- | ------ | -------- | ------------ | ----- | ---------------------- |
| `sample_docx`       | .docx  | writer   | python-docx  | ✅    | FR-004, FR-013, FR-016 |
| `sample_odt`        | .odt   | writer   | odfpy        | ❌    | FR-005                 |
| `sample_rtf`        | .rtf   | writer   | — (str)      | ❌    | FR-006                 |
| `sample_html`       | .html  | writer   | — (str)      | ❌    | FR-006                 |
| `sample_txt`        | .txt   | writer   | — (str)      | ❌    | FR-006                 |
| `sample_xlsx`       | .xlsx  | calc     | openpyxl     | ❌    | FR-007, FR-017         |
| `sample_ods`        | .ods   | calc     | odfpy        | ❌    | FR-008                 |
| `sample_csv`        | .csv   | calc     | csv (stdlib) | ❌    | FR-009                 |
| `sample_tsv`        | .tsv   | calc     | csv (stdlib) | ❌    | FR-009                 |
| `sample_pptx`       | .pptx  | impress  | python-pptx  | ✅    | FR-010, FR-013, FR-018 |
| `sample_odp`        | .odp   | impress  | odfpy        | ❌    | FR-011                 |
| `empty_docx`        | .docx  | edge     | python-docx  | ❌    | FR-015                 |
| `empty_xlsx`        | .xlsx  | edge     | openpyxl     | ❌    | FR-015                 |
| `empty_pptx`        | .pptx  | edge     | python-pptx  | ❌    | FR-015                 |
| `large_xlsx`        | .xlsx  | edge     | openpyxl     | ❌    | FR-015                 |
| `unicode_docx`      | .docx  | edge     | python-docx  | ❌    | FR-015                 |
| `special_chars_txt` | .txt   | edge     | — (str)      | ❌    | FR-015                 |

---

### 2. SampleData (테스트 데이터 세트)

각 문서 카테고리에 맞는 현실적 비즈니스 데이터. fixture_helpers 모듈에서 상수로 관리.

#### 2.1 WriterData — "제품 사양서" 시나리오 (FR-016)

| Field         | Type              | Value                                           |
| ------------- | ----------------- | ----------------------------------------------- |
| title         | `str`             | "LibreFormer 제품 사양"                         |
| paragraphs    | `list[str]`       | 기능 설명 2-3단락 (한국어 + 영어)               |
| table_headers | `list[str]`       | ["기능", "설명", "상태"]                        |
| table_rows    | `list[list[str]]` | 3×3 이상 (문서 변환, 배치 처리, 비동기 지원 등) |
| image         | `bytes`           | Pillow 생성 PNG (200×200, 제품 로고 대용)       |

#### 2.2 CalcData — "월별 매출 보고서" 시나리오 (FR-017)

| Field    | Type              | Value                                          |
| -------- | ----------------- | ---------------------------------------------- |
| headers  | `list[str]`       | ["월", "지역", "매출액", "비용", "순이익"]     |
| regions  | `list[str]`       | ["서울", "부산", "대구"]                       |
| months   | `list[str]`       | ["1월" ... "12월"]                             |
| rows     | `list[list[Any]]` | 12개월 × 3지역 = 36행, 숫자 데이터             |
| formulas | `dict[str, str]`  | {"합계": "=SUM(...)", "평균": "=AVERAGE(...)"} |

#### 2.3 ImpressData — "분기 실적 발표" 시나리오 (FR-018)

| Field             | Type   | Value                                                        |
| ----------------- | ------ | ------------------------------------------------------------ |
| company_name      | `str`  | "LibreFormer Inc."                                           |
| presentation_date | `str`  | "2026 Q1"                                                    |
| title_slide       | `dict` | {"title": company_name, "subtitle": presentation_date}       |
| content_slide     | `dict` | {"title": "핵심 지표", "bullets": ["매출 성장률: 25%", ...]} |
| image_slide       | `dict` | {"title": "실적 차트", "image": bytes (PNG)}                 |

---

### 3. GeneratedImage (Python 생성 테스트 이미지)

Pillow로 프로그래밍 생성되는 PNG 이미지. 문서 삽입 전용.

| Field   | Type             | Description              |
| ------- | ---------------- | ------------------------ |
| width   | `int`            | 이미지 너비 (기본 200px) |
| height  | `int`            | 이미지 높이 (기본 200px) |
| format  | `Literal["PNG"]` | 항상 PNG                 |
| content | `bytes`          | 이미지 바이너리 데이터   |

#### 생성 로직

```
create_test_image(width=200, height=200) -> bytes:
    1. Image.new('RGB', (width, height), color='white')
    2. ImageDraw.Draw(img)
    3. draw.rectangle([20, 20, width-20, height-20], outline='blue', width=3)
    4. draw.ellipse([40, 40, width-40, height-40], fill='lightblue')
    5. draw.text((width//2-30, height//2-10), "TEST", fill='black')
    6. img.save(BytesIO(), format='PNG') -> bytes
```

---

## Relationships

```
conftest.py
  ├── uses → fixture_helpers.images.create_test_image() → GeneratedImage (bytes)
  ├── uses → fixture_helpers.writer.create_docx(image_bytes) → Path
  ├── uses → fixture_helpers.writer.create_odt() → Path
  ├── uses → fixture_helpers.writer.create_rtf() → Path
  ├── uses → fixture_helpers.writer.create_html() → Path
  ├── uses → fixture_helpers.writer.create_txt() → Path
  ├── uses → fixture_helpers.writer.create_md() → Path
  ├── uses → fixture_helpers.calc.create_xlsx() → Path
  ├── uses → fixture_helpers.calc.create_ods() → Path
  ├── uses → fixture_helpers.calc.create_csv() → Path
  ├── uses → fixture_helpers.calc.create_tsv() → Path
  ├── uses → fixture_helpers.impress.create_pptx(image_bytes) → Path
  ├── uses → fixture_helpers.impress.create_odp() → Path
  └── defines → 16 pytest fixtures (session-scope) → Path

test_fixture_writer.py → uses → sample_docx, sample_odt, ... fixtures
test_fixture_calc.py   → uses → sample_xlsx, sample_ods, ... fixtures
test_fixture_impress.py→ uses → sample_pptx, sample_odp fixtures
test_fixture_edge.py   → uses → empty_docx, large_xlsx, ... fixtures
```

## Validation Rules

1. 모든 fixture가 반환하는 `Path`는 실제 파일을 가리켜야 함 (`path.exists() == True`)
2. 생성된 파일 크기 > 0 bytes
3. 이미지가 포함된 문서(docx, pptx)의 파일 크기 > 텍스트만 포함된 동일 포맷 파일 크기
4. PNG 이미지: width >= 100, height >= 100
5. odfpy 미설치 시 odt/ods/odp fixture는 `pytest.skip()` 발생

## State Transitions

해당 없음 — fixture는 생성 후 읽기 전용 (session-scope).
