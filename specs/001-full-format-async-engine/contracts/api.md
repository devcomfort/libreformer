# API Contracts: Full-Format Async Conversion Engine

**Date**: 2026-02-12
**Feature**: 001-full-format-async-engine

이 문서는 LibreFormer의 Python API 계약을 정의한다. 모든 public 인터페이스의 시그니처, 입출력 타입, 동작 규약을 명시한다.

---

## 1. LibreOfficeEngine (확장)

### 1.1 Constructor

```python
class LibreOfficeEngine(BaseEngine):
    def __init__(
        self,
        auto_install: bool = True,
        max_concurrency: int | None = None,
        timeout: float = 300.0,
    ) -> None: ...
```

| Parameter         | Type          | Default | Description                                                |
| ----------------- | ------------- | ------- | ---------------------------------------------------------- |
| `auto_install`    | `bool`        | `True`  | LibreOffice 미설치 시 자동 설치 (Linux)                    |
| `max_concurrency` | `int \| None` | `None`  | 비동기 최대 동시 변환 수. `None`이면 `os.cpu_count()` 사용 |
| `timeout`         | `float`       | `300.0` | 단일 변환 작업 타임아웃(초)                                |

**Invariants**:

- `max_concurrency`가 제공되면 `>= 1` 이어야 한다.
- `timeout`은 `> 0` 이어야 한다.

---

### 1.2 Sync API (기존 — 변경 없음)

#### `transform`

```python
def transform(self, file_path: str, to: str) -> Succeed | Failed: ...
```

- **Input**: 원본 파일 경로, 대상 포맷 확장자
- **Output**: `Succeed(file_path, output_path)` 또는 `Failed(file_path, error_message)`
- **Side Effects**: 파일시스템에 변환된 파일 생성, 임시 디렉토리 생성/삭제
- **Errors**: 예외를 던지지 않음. 모든 에러는 `Failed`로 반환.

#### `transform_parallel`

```python
@overload
def transform_parallel(
    self, file_paths: Sequence[str], to: str
) -> Iterator[Succeed | Failed]: ...

@overload
def transform_parallel(
    self, file_paths: Sequence[str], to: Sequence[str]
) -> Iterator[Succeed | Failed]: ...
```

- **Input**: 파일 경로 목록, 단일 포맷 문자열 또는 포맷 목록
- **Output**: 완료 순서대로 결과를 yield하는 Iterator
- **Raises**: `ValueError` — `to`가 Sequence이고 길이가 `file_paths`와 다를 때

#### `__call__`

```python
@overload
def __call__(self, file_path: str, to: str) -> Succeed | Failed: ...

@overload
def __call__(
    self, file_paths: Sequence[str], to: str | Sequence[str]
) -> Iterator[Succeed | Failed]: ...
```

- 단일 문자열 → `transform()` 위임
- Sequence → `transform_parallel()` 위임

---

### 1.3 Async API (신규)

#### `async_transform`

```python
async def async_transform(self, file_path: str, to: str) -> Succeed | Failed: ...
```

- **Input**: 동기 `transform`과 동일
- **Output**: 동기 `transform`과 동일 (`Succeed | Failed`)
- **Behavior**:
  - `asyncio.Semaphore`로 동시 실행 수 제한
  - `asyncio.create_subprocess_exec`로 LibreOffice 프로세스 실행
  - `asyncio.wait_for`로 타임아웃 적용
  - 타임아웃 시 프로세스 kill 후 `Failed` 반환
- **Side Effects**: 동기 버전과 동일

#### `async_transform_parallel`

```python
@overload
async def async_transform_parallel(
    self, file_paths: Sequence[str], to: str
) -> AsyncIterator[Succeed | Failed]: ...

@overload
async def async_transform_parallel(
    self, file_paths: Sequence[str], to: Sequence[str]
) -> AsyncIterator[Succeed | Failed]: ...
```

- **Input**: 동기 `transform_parallel`과 동일
- **Output**: `AsyncIterator` — `async for result in engine.async_transform_parallel(...):`
- **Behavior**:
  - 각 파일에 대해 `asyncio.create_task(self.async_transform(...))`
  - `asyncio.as_completed` 패턴으로 완료 순서대로 yield
  - Semaphore가 동시 실행 수를 제한
- **Raises**: `ValueError` — `to`가 Sequence이고 길이 불일치 시

---

## 2. FormatRegistry (신규)

```python
class FormatRegistry:
    """LibreOffice 포맷 메타데이터의 정적 레지스트리."""
```

### 2.1 Class Methods / Static Methods

#### `all_formats`

```python
@staticmethod
def all_formats() -> list[FormatInfo]: ...
```

- 등록된 모든 `FormatInfo` 객체 반환.

#### `supported_input_formats`

```python
@staticmethod
def supported_input_formats() -> set[str]: ...
```

- `can_import=True`인 모든 확장자의 집합 반환.

#### `supported_output_formats`

```python
@staticmethod
def supported_output_formats() -> set[str]: ...
```

- `can_export=True`인 모든 확장자의 집합 반환.

#### `can_convert`

```python
@staticmethod
def can_convert(from_ext: str, to_ext: str) -> bool: ...
```

- `from_ext`가 입력 가능하고 `to_ext`가 출력 가능하면 `True`.
- 확장자에 점(`.`)이 포함되어 있으면 자동 제거.

#### `formats_by_category`

```python
@staticmethod
def formats_by_category(category: str | DocumentCategory) -> list[FormatInfo]: ...
```

- 지정된 카테고리에 속하는 포맷만 반환.
- 문자열 입력 시 대소문자 무시 (`"Writer"` == `"writer"`).
- 유효하지 않은 카테고리는 빈 리스트 반환.

#### `get_format`

```python
@staticmethod
def get_format(extension: str) -> list[FormatInfo]: ...
```

- 동일 확장자가 여러 카테고리에 존재할 수 있으므로 리스트 반환.
- 예: `"html"` → Writer HTML + Calc HTML + 기타.

#### `get_export_filter`

```python
@staticmethod
def get_export_filter(from_ext: str, to_ext: str) -> str | None: ...
```

- 변환에 사용할 LibreOffice 필터 이름 반환.
- 매핑이 없으면 `None`.

---

## 3. Engine → FormatRegistry 통합

`LibreOfficeEngine`에 다음 편의 메서드를 추가하여 엔진에서 직접 포맷 조회 가능:

```python
class LibreOfficeEngine(BaseEngine):
    # ... 기존 메서드 ...

    @staticmethod
    def supported_input_formats() -> set[str]:
        return FormatRegistry.supported_input_formats()

    @staticmethod
    def supported_output_formats() -> set[str]:
        return FormatRegistry.supported_output_formats()

    @staticmethod
    def can_convert(from_ext: str, to_ext: str) -> bool:
        return FormatRegistry.can_convert(from_ext, to_ext)

    @staticmethod
    def formats_by_category(
        category: str | DocumentCategory,
    ) -> list[FormatInfo]:
        return FormatRegistry.formats_by_category(category)
```

---

## 4. Schema Contracts (기존 유지)

### Succeed

```python
@dataclass
class Succeed:
    file_path: Path
    output_path: Path
```

### Failed

```python
@dataclass
class Failed:
    file_path: Path
    error_message: str
```

### TransformResult

```python
@dataclass
class TransformResult:
    succeeds: Sequence[Succeed]
    failed: Sequence[Failed]
```

### FormatInfo (신규)

```python
@dataclass(frozen=True)
class FormatInfo:
    extension: str
    filter_name: str
    mime_type: str | None
    category: DocumentCategory
    can_import: bool
    can_export: bool
```

---

## 5. Public Exports (`__init__.py`)

```python
from .engine import LibreOfficeEngine
from .schemas import Succeed, Failed, TransformResult, FormatInfo
from .formats import FormatRegistry, DocumentCategory

__all__ = [
    "LibreOfficeEngine",
    "Succeed",
    "Failed",
    "TransformResult",
    "FormatInfo",
    "FormatRegistry",
    "DocumentCategory",
]
```
