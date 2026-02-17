# Feature Specification: Programmatic Test Fixture Generation

**Feature Branch**: `002-test-fixture-gen`
**Created**: 2026-02-13
**Status**: Draft
**Input**: User description: "테스트 파일을 재현 가능하게 파이썬 코드로 생성. 이미지 포함. 다양한 포맷(docx, xlsx, pptx, odt, csv, html, rtf 등)을 커버. 어떤 데이터를 넣을지 설계도 포함."

## Clarifications

### Session 2026-02-13

- Q: Fixture의 pytest scope를 function vs session 중 무엇으로 할 것인가? → A: `session` scope 사용. 변환은 원본 파일을 읽기만 하므로 데이터 오염 없음. 성능 최적화.
- Q: 대용량 fixture의 크기 상한이 필요한가? → A: 크기 상한 없음. 변환 테스트만 수행하므로 불필요.
- Q: 이미지 fixture의 용도는 독립 변환인가, 문서 삽입용인가? → A: 문서(docx, pptx) 내 이미지+텍스트 삽입 후 변환 성공 여부 검증이 목적. 독립 이미지 변환 테스트가 아님.

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Writer 계열 테스트 문서 생성 (Priority: P1)

테스트 실행 시 pytest fixture를 통해 Writer 계열 문서(docx, odt, rtf, html, txt)가 프로그래밍 방식으로 생성된다. 각 문서에는 제목, 본문 텍스트, 테이블, 인라인 이미지가 포함되어 변환 후에도 구조가 올바르게 전달되었는지 검증할 수 있다.

**Why this priority**: Writer 포맷은 문서 변환의 가장 기본적이고 빈번한 사용 사례이다. 현재 테스트가 `.txt`만 사용하므로, 실제 구조화된 문서로 변환을 검증하는 것이 가장 시급하다.

**Independent Test**: `sample_docx` fixture를 사용하여 docx→pdf 변환 후 `Succeed`를 확인하고, 출력 파일 크기가 0보다 큰지 검증한다.

**Acceptance Scenarios**:

1. **Given** pytest fixture 호출, **When** `sample_docx` fixture를 요청, **Then** 제목·본문·테이블·이미지가 포함된 유효한 `.docx` 파일이 `tmp_path`에 생성된다.
2. **Given** pytest fixture 호출, **When** `sample_odt` fixture를 요청, **Then** 제목·본문·테이블이 포함된 유효한 `.odt` 파일이 생성된다.
3. **Given** 텍스트 기반 포맷 fixture 호출 (rtf, html, txt), **When** 각 fixture를 요청, **Then** 마크업/텍스트가 포함된 유효한 파일이 생성되고 LibreOffice가 읽을 수 있다.
4. **Given** 이미지가 포함된 docx fixture, **When** pdf로 변환, **Then** 변환이 성공하고 출력 파일 크기가 텍스트만 있는 경우보다 크다.

---

### User Story 2 - Calc 계열 테스트 스프레드시트 생성 (Priority: P1)

테스트 실행 시 Calc 계열 스프레드시트(xlsx, ods, csv, tsv)가 프로그래밍 방식으로 생성된다. 각 스프레드시트에는 헤더 행, 숫자/문자열 데이터 행, 수식이 포함되어 변환 정확성을 검증할 수 있다.

**Why this priority**: 스프레드시트는 Writer와 함께 가장 빈번한 변환 대상이다. 수식과 다양한 데이터 타입을 포함한 파일로 변환을 검증해야 한다.

**Independent Test**: `sample_xlsx` fixture로 xlsx→pdf 변환 후 `Succeed` 확인.

**Acceptance Scenarios**:

1. **Given** pytest fixture 호출, **When** `sample_xlsx` fixture를 요청, **Then** 헤더·숫자·문자열·수식이 포함된 `.xlsx` 파일이 생성된다.
2. **Given** pytest fixture 호출, **When** `sample_ods` fixture를 요청, **Then** 동일한 데이터 구조의 `.ods` 파일이 생성된다.
3. **Given** 텍스트 기반 스프레드시트 fixture (csv, tsv), **When** 각 fixture를 요청, **Then** 적절한 구분자로 포맷된 파일이 생성된다.

---

### User Story 3 - Impress 계열 테스트 프레젠테이션 생성 (Priority: P2)

테스트 실행 시 Impress 계열 프레젠테이션(pptx, odp)이 프로그래밍 방식으로 생성된다. 각 프레젠테이션에는 제목 슬라이드, 내용 슬라이드, 이미지 슬라이드가 포함된다.

**Why this priority**: 프레젠테이션은 Writer/Calc 다음으로 빈번한 변환 대상이지만, 이미지·레이아웃 등 시각적 요소가 많아 변환 검증 가치가 높다.

**Independent Test**: `sample_pptx` fixture로 pptx→pdf 변환 후 `Succeed` 확인.

**Acceptance Scenarios**:

1. **Given** pytest fixture 호출, **When** `sample_pptx` fixture를 요청, **Then** 제목 슬라이드·내용 슬라이드·이미지 슬라이드가 포함된 `.pptx` 파일이 생성된다.
2. **Given** pytest fixture 호출, **When** `sample_odp` fixture를 요청, **Then** 동일한 슬라이드 구조의 `.odp` 파일이 생성된다.
3. **Given** 이미지가 포함된 pptx fixture, **When** pdf로 변환, **Then** 변환이 성공한다.

---

### User Story 4 - 문서 삽입용 이미지 프로그래밍 생성 (Priority: P2)

테스트 문서(docx, pptx)에 삽입할 이미지(PNG)를 Python 코드로 프로그래밍 생성한다. 이 이미지는 문서 내 콘텐츠로 삽입되어, 이미지가 포함된 문서의 변환이 정상 동작하는지 검증하는 데 사용된다. 독립적인 이미지 포맷 변환 테스트가 아니라, 문서 변환의 일부이다. 외부 파일 의존 없이 CI 환경에서도 완전 재현 가능하다.

**Why this priority**: 실제 비즈니스 문서에는 이미지가 포함되어 있으므로, 이미지+텍스트가 혼합된 문서의 변환을 검증해야 한다. 다른 Writer/Impress fixture의 빌딩 블록이다.

**Independent Test**: 이미지가 삽입된 `sample_docx` fixture의 docx→pdf 변환이 성공하고, 출력 파일 크기가 텍스트만 있는 문서보다 큰지 확인.

**Acceptance Scenarios**:

1. **Given** 이미지 생성 헬퍼 함수 호출, **When** PNG 이미지를 생성, **Then** 100×100 이상 크기의 유효한 PNG 바이트가 반환된다.
2. **Given** 생성된 PNG 이미지, **When** docx 문서에 삽입, **Then** 문서가 정상적으로 저장되고 LibreOffice에서 pdf로 변환된다.
3. **Given** 생성된 PNG 이미지, **When** pptx 슬라이드에 삽입, **Then** 프레젠테이션이 정상적으로 저장되고 LibreOffice에서 pdf로 변환된다.

---

### User Story 5 - 통합 fixture: conftest.py에 모든 fixture 집중 관리 (Priority: P1)

모든 테스트 fixture가 `tests/conftest.py`에 통합 관리되어, 테스트 파일에서 fixture 이름만으로 원하는 포맷의 샘플 파일을 받을 수 있다. 기존 테스트(`test_engine.py`)의 인라인 fixture와 공존하며 깨뜨리지 않는다.

**Why this priority**: fixture가 분산되면 유지보수가 어렵고 중복이 발생한다. 중앙 관리가 테스트 인프라의 기반이다.

**Independent Test**: 기존 `test_engine.py`가 수정 없이 통과하고, 새 테스트가 conftest.py의 fixture를 정상 사용한다.

**Acceptance Scenarios**:

1. **Given** `tests/conftest.py`에 모든 fixture 정의, **When** 임의의 테스트 파일에서 `sample_docx`를 요청, **Then** 유효한 `.docx` 파일 경로가 반환된다.
2. **Given** 기존 `tests/test_engine.py`에 인라인 `sample_file` fixture 존재, **When** 전체 테스트 스위트 실행, **Then** 기존 테스트와 새 테스트가 모두 통과한다.
3. **Given** conftest.py의 fixture, **When** fixture가 반환하는 파일 경로, **Then** 해당 파일이 `tmp_path` 하위에 존재하고 0바이트가 아니다.

---

### User Story 6 - 다양한 데이터 시나리오 Fixture (Priority: P3)

변환 엔진의 견고성을 검증하기 위해 경계 조건 데이터를 포함하는 특수 fixture를 제공한다: 빈 문서, 대용량 데이터(많은 행/페이지), 유니코드/다국어 텍스트, 특수 문자가 포함된 문서.

**Why this priority**: 경계 조건 테스트는 엔진 안정성에 중요하지만, 기본 변환 검증이 먼저 완성되어야 한다.

**Independent Test**: `empty_docx` fixture로 빈 문서 변환 시 `Succeed` 또는 합리적인 `Failed` 반환 확인.

**Acceptance Scenarios**:

1. **Given** `empty_docx` fixture 호출, **When** pdf로 변환, **Then** 변환이 성공하거나, 의미 있는 에러 메시지가 반환된다.
2. **Given** `large_xlsx` fixture 호출 (1000행 이상), **When** pdf로 변환, **Then** 타임아웃 내에 변환이 완료된다.
3. **Given** `unicode_docx` fixture 호출 (한국어·일본어·아랍어·이모지 포함), **When** pdf로 변환, **Then** 변환이 성공한다.
4. **Given** `special_chars_txt` fixture 호출 (특수 문자·개행·탭 포함), **When** pdf로 변환, **Then** 변환이 성공한다.
5. **Given** `empty_xlsx` fixture 호출 (빈 스프레드시트), **When** pdf로 변환, **Then** 변환이 성공하거나, 의미 있는 에러 메시지가 반환된다.
6. **Given** `empty_pptx` fixture 호출 (빈 프레젠테이션), **When** pdf로 변환, **Then** 변환이 성공하거나, 의미 있는 에러 메시지가 반환된다.

---

### Edge Cases

- ~~이미지 생성 라이브러리(Pillow 등)가 설치되지 않은 환경에서 이미지가 포함된 문서 fixture가 어떻게 동작하는가?~~ → Pillow는 필수 dev-dependency로 확정. `rye sync`로 항상 설치되므로 해당 없음.
- ODF 파일 생성 라이브러리(odfpy)가 선택적 의존성인 경우, 미설치 시 관련 fixture를 건너뛰는가? → 예, `pytest.importorskip("odf")`로 graceful skip 처리.
- session scope fixture 파일이 테스트 세션 종료 전까지 디스크에 남아 있는 것이 문제가 되는가? → 아니오, pytest `tmp_path_factory`가 세션 종료 시 자동 정리함.
- Windows/macOS 환경에서 파일 경로의 인코딩이 달라 fixture 생성이 실패하는가? → `pathlib.Path`를 사용하여 크로스 플랫폼 경로 처리. 주요 CI는 Linux.

## Requirements _(mandatory)_

### Functional Requirements

#### Fixture 인프라

- **FR-001**: 시스템은 `tests/conftest.py`에 모든 테스트 fixture를 중앙 집중 관리해야 한다(MUST). 각 fixture는 pytest `@pytest.fixture(scope="session")` 데코레이터를 사용하고, `tmp_path_factory`를 통해 파일을 생성한 뒤 `Path` 객체를 반환한다. 변환은 원본 파일을 읽기만 하므로 session scope가 안전하다.
- **FR-002**: 새로운 fixture는 기존 `tests/test_engine.py`의 인라인 fixture와 충돌하지 않아야 한다(MUST). 기존 테스트가 수정 없이 통과해야 한다.
- **FR-003**: 모든 fixture가 생성하는 파일은 외부 리소스(네트워크, 로컬 파일시스템의 사전 준비된 파일) 없이 Python 코드만으로 생성되어야 한다(MUST). CI 환경 완전 재현성을 보장한다.

#### Writer 계열 Fixture

- **FR-004**: 시스템은 `.docx` 파일을 생성하는 fixture를 제공해야 한다(MUST). 문서에는 제목(heading), 본문 단락(paragraph), 테이블(최소 3×3), 인라인 이미지가 포함된다.
- **FR-005**: 시스템은 `.odt` 파일을 생성하는 fixture를 제공해야 한다(SHOULD). ODF 네이티브 포맷으로 Writer의 기본 변환 경로를 검증한다.
- **FR-006**: 시스템은 텍스트 기반 Writer 포맷(`.rtf`, `.html`, `.txt`) 파일을 생성하는 fixture를 제공해야 한다(MUST). 순수 문자열/마크업으로 생성하며 추가 라이브러리가 필요 없다. (`.md`는 LibreOffice가 기본 지원하지 않으므로 제외)

#### Calc 계열 Fixture

- **FR-007**: 시스템은 `.xlsx` 파일을 생성하는 fixture를 제공해야 한다(MUST). 스프레드시트에는 헤더 행, 숫자/문자열 데이터 행(최소 10행), 수식(SUM 등)이 포함된다.
- **FR-008**: 시스템은 `.ods` 파일을 생성하는 fixture를 제공해야 한다(SHOULD). ODF 스프레드시트 포맷의 변환을 검증한다.
- **FR-009**: 시스템은 텍스트 기반 Calc 포맷(`.csv`, `.tsv`) 파일을 생성하는 fixture를 제공해야 한다(MUST). 내장 모듈만으로 생성한다.

#### Impress 계열 Fixture

- **FR-010**: 시스템은 `.pptx` 파일을 생성하는 fixture를 제공해야 한다(MUST). 프레젠테이션에는 제목 슬라이드, 내용 슬라이드(불릿 리스트), 이미지 슬라이드가 포함된다.
- **FR-011**: 시스템은 `.odp` 파일을 생성하는 fixture를 제공해야 한다(SHOULD). ODF 프레젠테이션 포맷의 변환을 검증한다.

#### 이미지 생성 (문서 삽입용)

- **FR-012**: 시스템은 문서(docx, pptx)에 삽입할 테스트용 PNG 이미지를 Python 코드로 생성하는 헬퍼 함수를 제공해야 한다(MUST). 이미지는 최소 100×100 픽셀이며, 단순 도형(그라데이션, 직사각형 등)을 포함한다.
- **FR-013**: 생성된 이미지는 Writer(docx) 및 Impress(pptx) fixture에서 문서 내 인라인 이미지로 삽입되어야 한다(MUST). odt/odp는 odfpy 이미지 삽입 API의 복잡성으로 인해 텍스트만 포함한다. 이미지가 포함된 문서의 변환 성공이 검증 대상이다.
- **FR-014**: _(Reserved — 향후 Draw/Math 계열 fixture 확장 시 사용)_

#### 경계 조건 Fixture

- **FR-015**: 시스템은 빈 문서(내용 없는 docx/xlsx/pptx), 대용량 데이터(1000행 이상 xlsx), 유니코드 텍스트(한/중/일/아랍/이모지), 특수 문자 텍스트 fixture를 제공해야 한다(SHOULD).

#### 데이터 설계

- **FR-016**: Writer 문서의 테스트 데이터는 "제품 사양서" 시나리오를 반영해야 한다(SHOULD). 제목("LibreFormer 제품 사양"), 본문(기능 설명 2-3 단락), 사양 비교 테이블, 제품 이미지를 포함한다.
- **FR-017**: Calc 스프레드시트의 테스트 데이터는 "월별 매출 보고서" 시나리오를 반영해야 한다(SHOULD). 헤더(월, 지역, 매출액, 비용, 순이익), 12개월 × 3개 지역 데이터, 합계/평균 수식을 포함한다.
- **FR-018**: Impress 프레젠테이션의 테스트 데이터는 "분기 실적 발표" 시나리오를 반영해야 한다(SHOULD). 제목 슬라이드(회사명, 발표일), 핵심 지표 슬라이드, 차트 대용 이미지 슬라이드를 포함한다.

### Key Entities

- **TestFixture**: pytest fixture 함수. `tmp_path_factory`를 통해 특정 포맷의 파일을 생성하고 `Path` 객체를 반환한다.
- **SampleData**: 각 문서 카테고리에 맞는 테스트 데이터 세트(텍스트, 숫자, 이미지). 현실적인 비즈니스 시나리오를 반영한다.
- **GeneratedImage**: Python으로 생성된 테스트용 이미지. PNG 포맷. 문서(docx, pptx) 삽입에 사용된다.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: 최소 10종 이상의 서로 다른 파일 포맷(docx, odt, xlsx, ods, pptx, odp, csv, html, rtf, txt 등)에 대한 fixture가 제공되어, 각 fixture로 생성된 파일이 LibreOffice 변환을 통과한다.
- **SC-002**: 모든 fixture가 외부 파일 의존 없이 순수 Python 코드만으로 파일을 생성하여, CI 환경에서 100% 재현 가능하다.
- **SC-003**: 기존 `tests/test_engine.py`의 2개 테스트가 변경 없이 통과하며, 새로운 fixture와 충돌이 없다.
- **SC-004**: 이미지+텍스트가 혼합된 문서(docx, pptx) fixture가 존재하며, 해당 문서의 pdf 변환이 성공한다.
- **SC-005**: fixture 생성에 필요한 Python 라이브러리가 dev-dependency로 명시되어, `rye sync`만으로 모든 의존성이 설치된다.
- **SC-006**: 전체 테스트 스위트 실행 시 fixture 생성 시간이 테스트당 1초 미만이다 (변환 시간 제외).

## Assumptions

- Python 3.8+ 환경에서 동작하며, pytest가 이미 dev-dependency로 설정되어 있다.
- `python-docx`, `openpyxl`, `python-pptx`를 dev-dependency로 추가한다 (docx, xlsx, pptx 생성용).
- `Pillow`를 dev-dependency로 추가한다 (PNG, JPEG 이미지 프로그래밍 생성용).
- `odfpy`를 dev-dependency로 추가한다 (odt, ods, odp ODF 포맷 생성용). 미설치 시 해당 fixture는 `pytest.importorskip`으로 건너뛴다.
- SVG, RTF, HTML, TXT, CSV, TSV는 순수 문자열로 생성하므로 추가 라이브러리 불필요.
- LibreOffice가 설치되지 않은 환경에서는 fixture 생성 자체는 성공하지만, 변환 테스트는 `skipif`로 건너뛴다.
- `tests/conftest.py`에 fixture를 추가하되, 기존 `test_engine.py`의 인라인 `sample_file` fixture는 그대로 유지한다 (pytest의 fixture scoping 규칙에 의해 인라인이 우선).
