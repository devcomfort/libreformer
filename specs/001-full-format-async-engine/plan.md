# Implementation Plan: Full-Format Async Conversion Engine

**Branch**: `001-full-format-async-engine` | **Date**: 2026-02-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-full-format-async-engine/spec.md`

## Summary

LibreFormer를 확장하여 (1) LibreOffice가 지원하는 모든 문서 포맷(Writer, Calc, Impress, Draw, Math, GraphicFilter)에 대한 완전한 변환 지원, (2) `asyncio.create_subprocess_exec` 기반 비동기 변환 엔진, (3) 정적 포맷 레지스트리를 통한 사전 검증 API를 추가한다. 기존 동기 API(`transform`, `transform_parallel`, callable)는 100% 하위 호환을 유지한다.

## Technical Context

**Language/Version**: Python >= 3.8 (asyncio 네이티브 지원)
**Primary Dependencies**: loguru (로깅), invoke (시스템 명령), asyncio (표준 라이브러리)
**Storage**: 파일시스템 기반 (입출력 문서 파일), 임시 디렉토리 (/tmp)
**Testing**: pytest, pytest-asyncio (비동기 테스트)
**Target Platform**: Linux (apt 기반 자동설치), macOS/Windows (수동 LibreOffice 설치)
**Project Type**: single (Python 라이브러리)
**Performance Goals**: 100개 파일 일괄 변환 시 동기 순차 대비 코어 수 비례 속도 향상 (4코어에서 ≥2x)
**Constraints**: LibreOffice 프로세스 격리 필수 (UserInstallation 분리), 메모리는 동시 프로세스 수에 비례
**Scale/Scope**: 단일 라이브러리, 50+ 입력 확장자, 20+ 출력 확장자, 6개 문서 카테고리

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

| Principle                       | Status  | Evidence                                                                                    |
| ------------------------------- | ------- | ------------------------------------------------------------------------------------------- |
| I. Simple & Type-Safe Interface | ✅ PASS | `Succeed`/`Failed` 반환 유지, async API도 동일 패턴. `can_convert()` 등 직관적 메서드 추가. |
| II. Robust Automation           | ✅ PASS | `auto_install` 유지, 포맷 레지스트리는 LibreOffice 없이도 조회 가능 (정적 데이터).          |
| III. Performance & Concurrency  | ✅ PASS | asyncio + Semaphore 기반 동시성 제어가 핵심 목표. 기존 ProcessPoolExecutor도 유지.          |
| IV. Modern Python Standards     | ✅ PASS | asyncio, dataclass, typing, rye, pytest-asyncio 활용. Python 3.8+ 호환.                     |
| V. Reliability                  | ✅ PASS | 타임아웃, 프로세스 격리, Failed 객체 반환, 구조화된 로깅.                                   |

모든 게이트 통과 — Phase 0 진행.

## Project Structure

### Documentation (this feature)

```text
specs/001-full-format-async-engine/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── api.md           # Python API contracts
└── checklists/
    └── requirements.md  # Spec quality checklist
```

### Source Code (repository root)

```text
src/libreformer/
├── __init__.py              # Public exports (기존 + 신규)
├── engine.py                # BaseEngine + LibreOfficeEngine (동기 유지 + async 추가)
├── async_engine.py          # AsyncBaseEngine + async LibreOfficeEngine mixin/methods
├── formats/
│   ├── __init__.py          # FormatRegistry public API
│   ├── registry.py          # FormatRegistry 클래스 (정적 포맷 데이터)
│   ├── categories.py        # DocumentCategory enum
│   └── data.py              # 포맷 매핑 상수 (Writer/Calc/Impress/Draw/Math/GraphicFilter)
├── schemas/
│   ├── __init__.py          # 기존 유지
│   ├── succeed.py           # 기존 유지
│   ├── failed.py            # 기존 유지
│   ├── transform_result.py  # 기존 유지
│   └── format_info.py       # FormatInfo dataclass (신규)
├── utils.py                 # 기존 유지
└── logging.py               # 기존 유지 + async 데코레이터 추가

tests/
├── __init__.py
├── test_engine.py           # 기존 동기 테스트 (변경 없음)
├── test_async_engine.py     # 비동기 변환 테스트
├── test_formats.py          # 포맷 레지스트리 테스트
└── test_backward_compat.py  # 하위 호환성 회귀 테스트
```

**Structure Decision**: 단일 프로젝트 구조 유지. 기존 `engine.py`는 수정 최소화하고 `async_engine.py`에 비동기 로직을 분리하여 하위 호환성을 보장한다. 포맷 데이터는 `formats/` 서브패키지로 독립 관리한다.

## Complexity Tracking

해당 없음 — Constitution 위반 사항 없음.
