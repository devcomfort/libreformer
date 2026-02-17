# Feature Specification: Full-Format Async Conversion Engine

**Feature Branch**: `001-full-format-async-engine`
**Created**: 2026-02-12
**Status**: Draft
**Input**: User description: "다른 프로젝트에서 작성했던 코드들이 있는데, 이 부분을 강화할 뿐만 아니라 libreoffice에서 호환되는 모든 문서에 대해 처리할 수 있도록 libreformer 라이브러리를 확장하고싶어. 문서 변환 인터페이스와 호환성, 기능을 모두 명세화해줄 수 있을까? asyncio를 통한 병렬화도 매우 중요해"

## User Scenarios & Testing _(mandatory)_

### User Story 1 - 단일 문서 비동기 변환 (Priority: P1)

사용자가 임의의 문서 파일(예: docx, pptx, xlsx, odt, hwp 등)을 원하는 출력 포맷으로 비동기 변환한다. `await engine.transform(file, "pdf")` 형태로 호출하면 결과를 `Succeed` 또는 `Failed` 객체로 돌려받는다.

**Why this priority**: 단일 파일 변환은 라이브러리의 가장 기본적인 기능이자 모든 상위 기능의 기반이다.

**Independent Test**: 하나의 .docx 파일을 PDF로 변환하고, `Succeed` 객체에 출력 경로가 포함되어 있는지 확인하면 된다.

**Acceptance Scenarios**:

1. **Given** LibreOffice가 설치된 환경, **When** 사용자가 `.docx` 파일을 `pdf`로 비동기 변환 요청, **Then** `Succeed` 객체에 유효한 출력 파일 경로가 포함된다.
2. **Given** 존재하지 않는 파일 경로, **When** 변환을 요청, **Then** `Failed` 객체에 "File not found" 에러 메시지가 포함된다.
3. **Given** LibreOffice가 지원하지 않는 출력 포맷, **When** 변환을 요청, **Then** `Failed` 객체에 포맷 미지원 에러 메시지가 포함된다.

---

### User Story 2 - 대량 문서 비동기 병렬 변환 (Priority: P1)

사용자가 수십~수백 개의 문서 파일 목록과 대상 포맷을 지정하면, asyncio 기반 비동기 병렬 처리로 빠르게 변환한다. 완료되는 순서대로 결과를 `async for` 이터레이션으로 받을 수 있다.

**Why this priority**: 대량 변환은 사용자가 가장 시간을 절약할 수 있는 핵심 기능이며, asyncio 도입의 주된 이유이다.

**Independent Test**: 10개의 텍스트 파일을 비동기 병렬로 PDF 변환하고, 모두 `Succeed`인지 확인 및 순차 처리 대비 소요 시간이 감소하는지 측정한다.

**Acceptance Scenarios**:

1. **Given** 10개의 문서 파일 목록, **When** 비동기 병렬 변환 요청, **Then** 10개의 결과가 모두 반환되며 각각 `Succeed` 또는 `Failed`이다.
2. **Given** 파일 목록과 동일 길이의 포맷 목록, **When** 파일별 다른 포맷으로 변환, **Then** 각 파일이 지정된 포맷으로 변환된다.
3. **Given** 파일 목록 길이와 포맷 목록 길이가 다른 경우, **When** 변환 요청, **Then** `ValueError`가 발생한다.

---

### User Story 3 - 지원 포맷 조회 및 검증 (Priority: P2)

사용자가 LibreOffice에서 지원하는 입력/출력 포맷 목록을 프로그래밍 방식으로 조회한다. 특정 입력→출력 변환 경로가 유효한지 사전에 검증할 수 있다.

**Why this priority**: 포맷 검증 없이 변환하면 실행 시점에서야 에러를 알 수 있다. 사전 검증은 사용자 경험을 크게 향상시킨다.

**Independent Test**: `engine.supported_input_formats()`, `engine.supported_output_formats()`, `engine.can_convert("docx", "pdf")` 호출 결과가 올바른지 확인한다.

**Acceptance Scenarios**:

1. **Given** 엔진 인스턴스, **When** 지원 입력 포맷 목록을 조회, **Then** LibreOffice Writer/Calc/Impress/Draw가 지원하는 모든 확장자가 포함된 목록이 반환된다.
2. **Given** 엔진 인스턴스, **When** `can_convert("docx", "pdf")`를 호출, **Then** `True`가 반환된다.
3. **Given** 엔진 인스턴스, **When** `can_convert("xyz_invalid", "pdf")`를 호출, **Then** `False`가 반환된다.

---

### User Story 4 - 동기 API 하위 호환성 유지 (Priority: P2)

기존 `transform()` 및 `transform_parallel()` 동기 API를 그대로 사용할 수 있다. 새로운 asyncio API는 추가 제공이며, 기존 코드가 깨지지 않는다.

**Why this priority**: 기존 사용자의 코드를 보호하면서 점진적으로 async로 이전할 수 있게 하는 것은 라이브러리 신뢰성의 핵심이다.

**Independent Test**: 기존 테스트 코드(`test_engine.py`)가 변경 없이 통과하는지 확인한다.

**Acceptance Scenarios**:

1. **Given** 기존 동기 `engine.transform()` 호출 코드, **When** 새 엔진 버전에서 실행, **Then** 동일한 `Succeed`/`Failed` 결과가 반환된다.
2. **Given** 기존 `engine.transform_parallel()` 코드, **When** 새 엔진 버전에서 실행, **Then** 동일한 Iterator 결과가 반환된다.
3. **Given** 기존 `engine("file.docx", "pdf")` callable 인터페이스, **When** 새 버전에서 호출, **Then** 동일하게 동작한다.

---

### User Story 5 - 동시성 제한 및 리소스 관리 (Priority: P3)

사용자가 동시 변환 작업 수를 제한하여 시스템 리소스(CPU, 메모리, LibreOffice 프로세스 수)를 관리할 수 있다. 예: `engine = LibreOfficeEngine(max_concurrency=4)`.

**Why this priority**: 대규모 일괄 변환 시 시스템 과부하를 방지하는 것은 안정성에 중요하지만, 기본 변환 기능이 먼저 완성되어야 한다.

**Independent Test**: `max_concurrency=2`로 설정 후 10개 파일을 변환할 때, 동시에 2개 이상의 LibreOffice 프로세스가 실행되지 않는지 확인한다.

**Acceptance Scenarios**:

1. **Given** `max_concurrency=2`로 설정된 엔진, **When** 10개 파일을 비동기 병렬 변환, **Then** 동시 실행 프로세스 수가 2를 초과하지 않는다.
2. **Given** `max_concurrency`를 지정하지 않은 엔진, **When** 병렬 변환 실행, **Then** CPU 코어 수 기반의 합리적인 기본값이 적용된다.

---

### User Story 6 - 문서 카테고리별 포맷 매핑 (Priority: P3)

사용자가 문서 유형(Writer, Calc, Impress, Draw, Math 등)별로 지원 포맷을 분류하여 확인할 수 있다. 이를 통해 "스프레드시트를 PDF로 변환" 같은 도메인 수준 작업을 안전하게 수행할 수 있다.

**Why this priority**: 포맷 매핑은 사용자가 올바른 변환 경로를 선택하도록 돕지만, 변환 자체가 먼저 동작해야 한다.

**Independent Test**: `engine.formats_by_category("writer")` 호출 시 Writer 관련 포맷만 반환되는지 확인한다.

**Acceptance Scenarios**:

1. **Given** 엔진 인스턴스, **When** `formats_by_category("calc")` 호출, **Then** xlsx, xls, ods, csv 등 Calc 관련 포맷만 반환된다.
2. **Given** 엔진 인스턴스, **When** 유효하지 않은 카테고리를 전달, **Then** 빈 결과 또는 명확한 에러가 반환된다.

---

### Edge Cases

- 파일이 0바이트(빈 파일)인 경우 어떻게 처리하는가?
- 변환 도중 LibreOffice 프로세스가 비정상 종료되면 어떻게 처리하는가?
- 동일 파일을 동시에 여러 포맷으로 변환 요청하면 충돌이 발생하는가?
- 매우 큰 파일(수백 MB)의 변환 시 타임아웃 처리는 어떻게 하는가?
- LibreOffice가 설치되지 않은 환경에서 포맷 조회 API는 어떻게 동작하는가?
- 입력 파일의 확장자와 실제 내용이 다른 경우(예: .docx 확장자지만 실제로 txt) 어떻게 처리하는가?
- asyncio 이벤트 루프가 이미 실행 중인 환경(예: Jupyter Notebook)에서의 호환성

## Requirements _(mandatory)_

### Functional Requirements

#### 비동기 변환 인터페이스

- **FR-001**: 시스템은 단일 파일에 대한 비동기 변환 메서드(`async transform`)를 제공해야 한다(MUST). `Succeed` 또는 `Failed` 객체를 반환한다.
- **FR-002**: 시스템은 복수 파일에 대한 비동기 병렬 변환 메서드(`async transform_parallel`)를 제공해야 한다(MUST). `AsyncIterator[Succeed | Failed]`를 반환하며, 완료 순서대로 결과를 yield 한다.
- **FR-003**: 비동기 병렬 변환 시, 각 파일별로 서로 다른 출력 포맷을 지정할 수 있어야 한다(MUST). 파일 목록과 포맷 목록의 길이가 다르면 `ValueError`를 발생시킨다.

#### 동기 API 하위 호환

- **FR-004**: 기존 동기 `transform(file_path: str, to: str) -> Succeed | Failed` 인터페이스를 유지해야 한다(MUST).
- **FR-005**: 기존 동기 `transform_parallel(file_paths, to) -> Iterator[Succeed | Failed]` 인터페이스를 유지해야 한다(MUST).
- **FR-006**: 기존 callable 인터페이스(`engine(file, to)`)를 유지해야 한다(MUST).

#### 포맷 호환성

- **FR-007**: 시스템은 LibreOffice Writer가 지원하는 모든 입출력 포맷을 지원해야 한다(MUST). 주요 포맷: odt, doc, docx, rtf, txt, html, pdf, epub, markdown, fodt, pages, hwp.
- **FR-008**: 시스템은 LibreOffice Calc가 지원하는 모든 입출력 포맷을 지원해야 한다(MUST). 주요 포맷: ods, xls, xlsx, csv, tsv, html, pdf, fods, numbers, parquet, gnumeric, dif, dbf, slk.
- **FR-009**: 시스템은 LibreOffice Impress가 지원하는 모든 입출력 포맷을 지원해야 한다(MUST). 주요 포맷: odp, ppt, pptx, pdf, fodp, key, pps, ppsx, potx.
- **FR-010**: 시스템은 LibreOffice Draw가 지원하는 모든 입출력 포맷을 지원해야 한다(MUST). 주요 포맷: odg, pdf, fodg, svg, vsd, vsdx, pub, cdr, wpg.
- **FR-011**: 시스템은 LibreOffice Math가 지원하는 입출력 포맷을 지원해야 한다(MUST). 주요 포맷: odf, mml, pdf.
- **FR-012**: 시스템은 그래픽 내보내기 필터를 지원해야 한다(MUST). jpg, png, svg, webp 등 이미지 형식으로의 변환을 포함한다.

#### 포맷 조회 및 검증

- **FR-013**: 시스템은 지원하는 입력 포맷 전체 목록을 반환하는 메서드를 제공해야 한다(MUST).
- **FR-014**: 시스템은 지원하는 출력 포맷 전체 목록을 반환하는 메서드를 제공해야 한다(MUST).
- **FR-015**: 시스템은 특정 입력→출력 변환 쌍의 유효성을 사전 검증하는 메서드를 제공해야 한다(MUST). 예: `can_convert(from_ext, to_ext) -> bool`.
- **FR-016**: 시스템은 문서 카테고리(writer, calc, impress, draw, math)별로 지원 포맷을 분류하여 반환하는 메서드를 제공해야 한다(SHOULD).

#### 동시성 제어

- **FR-017**: 시스템은 동시에 실행 가능한 변환 작업 수를 제한하는 설정을 제공해야 한다(MUST). asyncio Semaphore 기반으로 구현하며, 기본값은 시스템 CPU 코어 수이다.
- **FR-018**: 각 병렬 변환 작업은 고유한 LibreOffice 사용자 설치 디렉토리를 사용하여 프로세스 간 잠금 충돌을 방지해야 한다(MUST).

#### 에러 처리

- **FR-019**: 변환 실패 시 예외를 던지지 않고 `Failed` 객체를 반환해야 한다(MUST). `Failed` 객체는 원본 파일 경로와 사람이 읽을 수 있는 에러 메시지를 포함한다.
- **FR-020**: 변환 프로세스가 지정된 시간 내에 완료되지 않으면 타임아웃으로 처리하고 `Failed` 객체를 반환해야 한다(SHOULD). 기본 타임아웃은 설정 가능하다.

#### 로깅

- **FR-021**: 모든 변환 작업의 시작/완료/실패를 구조화된 로그로 기록해야 한다(MUST). 소요 시간(ms)을 포함한다.

### Key Entities

- **LibreOfficeEngine**: 변환 엔진의 메인 인스턴스. `auto_install`, `max_concurrency`, `timeout` 설정을 포함한다.
- **Succeed**: 변환 성공 결과. 원본 경로(`file_path`)와 출력 경로(`output_path`)를 포함한다.
- **Failed**: 변환 실패 결과. 원본 경로(`file_path`)와 에러 메시지(`error_message`)를 포함한다.
- **TransformResult**: 배치 변환 결과의 집계 객체. 성공/실패 목록을 포함한다.
- **FormatInfo**: 포맷 메타데이터. 확장자, 필터 이름, MIME 타입, 소속 카테고리(writer/calc/impress/draw/math) 정보를 포함한다.
- **DocumentCategory**: 문서 카테고리 열거형. Writer, Calc, Impress, Draw, Math, GraphicFilter를 포함한다.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: 사용자는 LibreOffice가 지원하는 모든 주요 문서 포맷(최소 50종 이상의 입력 확장자, 20종 이상의 출력 확장자)에 대해 변환을 수행할 수 있다.
- **SC-002**: 100개 문서의 일괄 비동기 변환이 동기 순차 변환 대비 CPU 코어 수에 비례하여 빠르게 완료된다(예: 4코어에서 최소 2배 이상 빨라야 한다).
- **SC-003**: 기존 동기 API를 사용하는 코드가 변경 없이 정상 동작한다(하위 호환성 100% 유지).
- **SC-004**: 지원 포맷 조회 API를 통해 사용자가 변환 전에 유효성을 검증할 수 있으며, 잘못된 포맷 조합 시 변환 실행 전에 `False`를 반환한다.
- **SC-005**: 동시 변환 수가 `max_concurrency` 설정을 초과하지 않으며, 시스템 리소스 사용이 예측 가능하다.
- **SC-006**: 변환 실패 시 사용자가 원인을 파악할 수 있는 명확한 에러 메시지가 `Failed` 객체에 포함된다.

## Assumptions

- LibreOffice가 시스템에 설치되어 있거나, Linux 환경에서 `apt`를 통해 자동 설치가 가능하다.
- `soffice --headless --convert-to` 커맨드라인 인터페이스가 변환의 기반이 된다.
- asyncio 기반 비동기 병렬 처리는 `asyncio.create_subprocess_exec`를 통해 LibreOffice 프로세스를 비동기로 관리하는 방식으로 구현된다.
- 포맷 매핑 데이터는 LibreOffice 공식 필터 목록 기준으로 코드 내에 정적으로 정의된다(런타임 동적 조회가 아님).
- Python 3.8 이상을 지원하며, asyncio가 기본 제공되는 환경을 전제한다.
- 기존 `ProcessPoolExecutor` 기반 동기 병렬 처리는 하위 호환을 위해 유지하되, 새로운 asyncio API가 권장된다.
- 변환 타임아웃 기본값은 300초(5분)로 설정하며, 사용자가 재정의할 수 있다.
