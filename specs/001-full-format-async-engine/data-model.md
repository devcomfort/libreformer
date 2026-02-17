# Data Model: Full-Format Async Conversion Engine

**Date**: 2026-02-12
**Feature**: 001-full-format-async-engine

## Entities

### DocumentCategory (Enum)

문서 카테고리를 나타내는 열거형. LibreOffice 모듈에 대응한다.

| Value     | Description                                |
| --------- | ------------------------------------------ |
| `WRITER`  | 워드프로세서 문서 (Writer)                 |
| `CALC`    | 스프레드시트 (Calc)                        |
| `IMPRESS` | 프레젠테이션 (Impress)                     |
| `DRAW`    | 벡터 드로잉 (Draw)                         |
| `MATH`    | 수식 (Math)                                |
| `GRAPHIC` | 그래픽 내보내기 필터 (jpg, png, svg, webp) |

**Validation**: 값은 소문자 문자열로도 접근 가능해야 한다 (`str` mixin).

---

### FormatInfo (Dataclass, frozen)

단일 파일 포맷의 메타데이터를 나타낸다.

| Field         | Type               | Description                       | Example                   |
| ------------- | ------------------ | --------------------------------- | ------------------------- |
| `extension`   | `str`              | 파일 확장자 (점 없이)             | `"docx"`                  |
| `filter_name` | `str`              | LibreOffice 필터 API 이름         | `"MS Word 2007 XML"`      |
| `mime_type`   | `str \| None`      | MIME 타입 (알 수 없으면 None)     | `"application/msword"`    |
| `category`    | `DocumentCategory` | 소속 문서 카테고리                | `DocumentCategory.WRITER` |
| `can_import`  | `bool`             | 이 포맷을 입력으로 읽을 수 있는지 | `True`                    |
| `can_export`  | `bool`             | 이 포맷으로 출력할 수 있는지      | `True`                    |

**Validation**:

- `extension`은 비어있을 수 없다.
- `can_import`과 `can_export` 중 최소 하나는 `True`여야 한다.

**Relationships**:

- `category` → `DocumentCategory`

---

### FormatRegistry (Class)

포맷 메타데이터의 중앙 저장소. 정적 데이터 기반.

| Method                                | Return Type        | Description                                     |
| ------------------------------------- | ------------------ | ----------------------------------------------- |
| `all_formats()`                       | `list[FormatInfo]` | 등록된 모든 포맷 정보 반환                      |
| `supported_input_formats()`           | `set[str]`         | `can_import=True`인 확장자 집합                 |
| `supported_output_formats()`          | `set[str]`         | `can_export=True`인 확장자 집합                 |
| `can_convert(from_ext, to_ext)`       | `bool`             | 입력→출력 변환 가능 여부                        |
| `formats_by_category(category)`       | `list[FormatInfo]` | 카테고리별 포맷 목록                            |
| `get_format(extension)`               | `list[FormatInfo]` | 확장자로 포맷 정보 조회 (동일 확장자 다수 가능) |
| `get_export_filter(from_ext, to_ext)` | `str \| None`      | 변환에 사용할 필터 이름 반환                    |

**State**: Stateless (모든 데이터는 모듈 로드 시 초기화된 상수).

---

### Succeed (Dataclass) — 기존 유지

| Field         | Type   | Description           |
| ------------- | ------ | --------------------- |
| `file_path`   | `Path` | 원본 파일 경로        |
| `output_path` | `Path` | 변환된 출력 파일 경로 |

변경 없음.

---

### Failed (Dataclass) — 기존 유지

| Field           | Type   | Description                     |
| --------------- | ------ | ------------------------------- |
| `file_path`     | `Path` | 원본 파일 경로                  |
| `error_message` | `str`  | 사람이 읽을 수 있는 에러 메시지 |

변경 없음.

---

### TransformResult (Dataclass) — 기존 유지

| Field      | Type                | Description           |
| ---------- | ------------------- | --------------------- |
| `succeeds` | `Sequence[Succeed]` | 성공한 변환 결과 목록 |
| `failed`   | `Sequence[Failed]`  | 실패한 변환 결과 목록 |

변경 없음.

---

### LibreOfficeEngine (Class) — 확장

기존 필드 + 신규 필드:

| Field              | Type          | Default               | Description                | Status   |
| ------------------ | ------------- | --------------------- | -------------------------- | -------- |
| `auto_install`     | `bool`        | `True`                | LibreOffice 자동 설치 여부 | 기존     |
| `libreoffice_path` | `str \| None` | (auto)                | soffice 실행 파일 경로     | 기존     |
| `max_concurrency`  | `int \| None` | `None` (=CPU 코어 수) | 비동기 최대 동시 변환 수   | **신규** |
| `timeout`          | `float`       | `300.0`               | 단일 변환 타임아웃(초)     | **신규** |

**State Transitions**: 없음 (stateless 변환 엔진).

---

## Entity Relationship Diagram

```text
LibreOfficeEngine
  ├── uses → FormatRegistry (포맷 조회/검증)
  ├── returns → Succeed | Failed (단일 변환 결과)
  └── returns → TransformResult (배치 집계)

FormatRegistry
  ├── contains → FormatInfo[] (포맷 메타데이터)
  └── uses → DocumentCategory (카테고리 분류)

FormatInfo
  └── belongs to → DocumentCategory
```
