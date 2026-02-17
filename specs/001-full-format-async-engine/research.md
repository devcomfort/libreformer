# Research: Full-Format Async Conversion Engine

**Date**: 2026-02-12
**Feature**: 001-full-format-async-engine

## R1: asyncio 기반 서브프로세스 관리 패턴

### Decision

`asyncio.create_subprocess_exec`를 사용하여 LibreOffice `soffice` 프로세스를 비동기로 실행한다. `asyncio.Semaphore`로 동시 실행 수를 제한한다.

### Rationale

- `subprocess.run`은 블로킹 호출이므로 asyncio 이벤트 루프를 차단한다.
- `asyncio.create_subprocess_exec`는 네이티브 비동기 서브프로세스 지원을 제공하며, `await process.communicate()`로 stdout/stderr를 비동기 수집한다.
- `asyncio.Semaphore(max_concurrency)`로 동시 프로세스 수를 정밀 제어하여 시스템 과부하를 방지한다.
- `asyncio.wait` + `FIRST_COMPLETED` 또는 `asyncio.as_completed`로 완료 순서대로 결과를 yield 할 수 있다.

### Alternatives Considered

| Alternative                                                       | Rejected Because                                                                            |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| `concurrent.futures.ProcessPoolExecutor` + `loop.run_in_executor` | 진정한 async가 아님. 프로세스 풀 오버헤드 존재. async iterator 패턴과 자연스럽게 결합 불가. |
| `trio` / `anyio`                                                  | 추가 의존성 발생. Python 3.8+ 표준 라이브러리만으로 충분.                                   |
| `asyncio.subprocess` + 무제한 동시 실행                           | 리소스 폭발 위험. Semaphore 필수.                                                           |

### Implementation Pattern

```python
import asyncio
from pathlib import Path

class AsyncLibreOfficeEngine:
    def __init__(self, max_concurrency: int | None = None, timeout: float = 300.0):
        import os
        self._semaphore = asyncio.Semaphore(max_concurrency or os.cpu_count() or 4)
        self._timeout = timeout

    async def transform(self, file_path: str, to: str) -> Succeed | Failed:
        async with self._semaphore:
            # 고유 UserInstallation 디렉토리로 프로세스 격리
            proc = await asyncio.create_subprocess_exec(
                soffice_path,
                f"-env:UserInstallation=file://{unique_dir}",
                "--headless", "--norestore", "--nolockcheck",
                "--convert-to", to,
                "--outdir", output_dir,
                str(input_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(), timeout=self._timeout
                )
            except asyncio.TimeoutError:
                proc.kill()
                return Failed(...)

    async def transform_parallel(self, file_paths, to):
        tasks = [asyncio.create_task(self.transform(fp, t)) for fp, t in ...]
        for coro in asyncio.as_completed(tasks):
            yield await coro
```

---

## R2: LibreOffice 포맷 레지스트리 설계

### Decision

LibreOffice 공식 필터 목록을 기반으로 정적 Python 데이터 구조(dict/dataclass)로 포맷 레지스트리를 구축한다. 런타임 동적 조회가 아닌 코드 내 상수로 관리한다.

### Rationale

- LibreOffice 필터 목록은 버전 간 안정적이며, 주요 포맷은 수년간 변하지 않는다.
- 런타임 조회(`soffice --help` 파싱 등)는 LibreOffice 설치 필수 + 파싱 불안정 + 성능 저하.
- 정적 데이터는 LibreOffice 미설치 환경에서도 포맷 조회/검증이 가능하다(FR-013~FR-016).
- 새 LibreOffice 버전 출시 시 데이터 파일만 업데이트하면 된다.

### Alternatives Considered

| Alternative                  | Rejected Because                              |
| ---------------------------- | --------------------------------------------- |
| 런타임 `soffice --help` 파싱 | LibreOffice 설치 필수, 출력 형식 불안정, 느림 |
| JSON/YAML 외부 파일          | 패키징 복잡성 증가, Python dict가 더 간단     |
| LibreOffice UNO API          | 과도한 복잡성, 추가 의존성, 프로세스 필요     |

### Data Structure

```python
from dataclasses import dataclass
from enum import Enum

class DocumentCategory(str, Enum):
    WRITER = "writer"
    CALC = "calc"
    IMPRESS = "impress"
    DRAW = "draw"
    MATH = "math"
    GRAPHIC = "graphic"

@dataclass(frozen=True)
class FormatInfo:
    extension: str           # e.g., "docx"
    filter_name: str         # e.g., "MS Word 2007 XML"
    mime_type: str | None    # e.g., "application/msword"
    category: DocumentCategory
    can_import: bool         # 입력으로 사용 가능 여부
    can_export: bool         # 출력으로 사용 가능 여부

# Registry: Dict[str, List[FormatInfo]] keyed by extension
```

### Category Coverage (from LibreOffice official filters)

| Category              | Import Extensions (주요)                                                             | Export Extensions (주요)                                 |
| --------------------- | ------------------------------------------------------------------------------------ | -------------------------------------------------------- |
| Writer                | odt, doc, docx, rtf, txt, html, epub, fodt, pages, hwp, wpd, wri, md, abw, lwp, pdb  | odt, doc, docx, rtf, txt, html, pdf, epub, fodt, md      |
| Calc                  | ods, xls, xlsx, csv, tsv, html, fods, numbers, gnumeric, dif, dbf, slk, wk1, parquet | ods, xls, xlsx, csv, tsv, html, pdf, fods, dif, dbf, slk |
| Impress               | odp, ppt, pptx, fodp, key, pps, ppsx, sxi                                            | odp, ppt, pptx, pdf, fodp, pps, ppsx                     |
| Draw                  | odg, fodg, vsd, vsdx, pub, cdr, wpg, cmx, sxd                                        | odg, pdf, fodg, svg                                      |
| Math                  | odf, mml, sxm                                                                        | odf, mml, pdf                                            |
| Graphic (export only) | —                                                                                    | jpg, png, svg, webp                                      |

---

## R3: 하위 호환성 전략

### Decision

기존 `BaseEngine` + `LibreOfficeEngine` 클래스를 보존하고, 비동기 메서드를 별도 mixin 또는 동일 클래스 내 `async_transform` / `async_transform_parallel` 메서드로 추가한다.

### Rationale

- 기존 `engine.transform()`은 동기 `subprocess.run` 기반이므로 시그니처 변경 없이 유지 가능.
- 새로운 async 메서드는 `async_transform`, `async_transform_parallel` 이름으로 추가하여 기존 메서드와 이름 충돌을 회피.
- `__call__` 인터페이스도 그대로 유지 (동기 디스패치).
- `FormatRegistry`는 독립 모듈이므로 기존 코드에 영향 없음.

### Alternatives Considered

| Alternative                                    | Rejected Because                             |
| ---------------------------------------------- | -------------------------------------------- |
| `transform()`을 async로 변경                   | 모든 기존 호출 코드가 깨짐 (breaking change) |
| 별도 `AsyncLibreOfficeEngine` 클래스           | 코드 중복, 설정 동기화 복잡                  |
| `transform()`이 이벤트 루프 감지하여 자동 분기 | 암묵적 동작, 디버깅 어려움, 예측 불가        |

### Migration Path

```
기존 코드 (변경 없음):
  engine.transform("file.docx", "pdf")           # 동기
  engine.transform_parallel(files, "pdf")         # 동기 병렬

신규 코드 (추가):
  await engine.async_transform("file.docx", "pdf")          # 비동기
  async for result in engine.async_transform_parallel(...):  # 비동기 병렬
```

---

## R4: 타임아웃 및 프로세스 격리

### Decision

- 타임아웃: `asyncio.wait_for(proc.communicate(), timeout=N)` 사용. 기본 300초.
- 프로세스 격리: 기존 `uuid4` 기반 `/tmp/libreoffice_conversion_{uuid}` 패턴 유지.
- 정리: `finally` 블록에서 `shutil.rmtree` (동기) / `asyncio.to_thread(shutil.rmtree, ...)` (비동기) 호출.

### Rationale

- LibreOffice는 단일 UserInstallation에서 동시 실행 시 잠금 충돌 발생 (기존 코드에서 이미 해결).
- 타임아웃은 대용량 파일이나 LibreOffice 행(hang) 시 필수.
- `asyncio.wait_for`는 표준 라이브러리에서 제공하는 가장 깔끔한 타임아웃 패턴.

### Alternatives Considered

| Alternative           | Rejected Because                                      |
| --------------------- | ----------------------------------------------------- |
| 타임아웃 없음         | 대용량 파일에서 무한 대기 위험                        |
| `signal.alarm`        | 비동기 환경 비호환, Unix 전용                         |
| UserInstallation 풀링 | 구현 복잡성 대비 이점 미미 (uuid 생성 비용 무시 가능) |

---

## R5: pytest-asyncio 통합

### Decision

`pytest-asyncio`를 dev-dependency로 추가하고, `@pytest.mark.asyncio` 데코레이터로 비동기 테스트를 작성한다.

### Rationale

- pytest는 기본적으로 async 테스트를 지원하지 않음.
- `pytest-asyncio`는 가장 널리 사용되는 pytest async 플러그인.
- 기존 동기 테스트(`test_engine.py`)에 영향 없음.

### Alternatives Considered

| Alternative               | Rejected Because                       |
| ------------------------- | -------------------------------------- |
| `anyio` + `pytest-anyio`  | 불필요한 추가 의존성                   |
| 수동 `asyncio.run()` 래핑 | 보일러플레이트 증가, fixture 지원 부족 |
