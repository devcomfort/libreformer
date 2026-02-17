# Implementation Plan: Programmatic Test Fixture Generation

**Branch**: `002-test-fixture-gen` | **Date**: 2026-02-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-test-fixture-gen/spec.md`

## Summary

LibreFormer의 테스트 인프라를 확장하여 (1) `tests/conftest.py`에 10종 이상의 문서 포맷(docx, odt, xlsx, ods, pptx, odp, csv, tsv, html, rtf, txt, md)에 대한 프로그래밍 방식의 session-scoped pytest fixture를 제공하고, (2) Pillow를 사용한 이미지 생성 헬퍼로 docx/pptx에 인라인 이미지를 삽입하며, (3) 현실적인 비즈니스 데이터 시나리오(제품 사양서, 월별 매출 보고서, 분기 실적 발표)를 포함한 테스트 데이터를 설계한다. 모든 fixture는 외부 파일 의존 없이 순수 Python 코드로 생성되어 CI 환경에서 100% 재현 가능하다.

## Technical Context

**Language/Version**: Python >= 3.8  
**Primary Dependencies**: python-docx (docx 생성), openpyxl (xlsx 생성), python-pptx (pptx 생성), Pillow (PNG 이미지 생성), odfpy (odt/ods/odp 생성 — SHOULD)  
**Storage**: `tmp_path_factory` 기반 임시 디렉토리 (pytest session-scope)  
**Testing**: pytest >= 9.0.2, pytest-asyncio >= 0.23.0  
**Target Platform**: Linux (CI), macOS/Windows (로컬 개발)  
**Project Type**: single (Python 라이브러리 — 테스트 인프라 확장)  
**Performance Goals**: fixture 생성 시간 테스트당 1초 미만 (변환 시간 제외, SC-006)  
**Constraints**: 외부 파일/네트워크 의존 불가 (FR-003), 기존 테스트 무결성 유지 (FR-002)  
**Scale/Scope**: 10+ 파일 포맷, 4+ 경계 조건 fixture, 1개 conftest.py 파일

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

| Principle                       | Status  | Evidence                                                                                                 |
| ------------------------------- | ------- | -------------------------------------------------------------------------------------------------------- |
| I. Simple & Type-Safe Interface | ✅ PASS | fixture는 `Path` 객체를 반환하여 기존 `engine.transform(str(path), ...)` 패턴과 자연스럽게 통합.         |
| II. Robust Automation           | ✅ PASS | 외부 파일 없이 Python 코드만으로 생성 (FR-003). odfpy 미설치 시 `pytest.importorskip`으로 graceful skip. |
| III. Performance & Concurrency  | ✅ PASS | session-scope로 fixture 재생성 방지. 테스트 실행 성능에 영향 최소화.                                     |
| IV. Modern Python Standards     | ✅ PASS | pytest fixture, tmp_path_factory, typing 활용. rye dev-dependency로 관리.                                |
| V. Reliability                  | ✅ PASS | 모든 fixture가 CI 재현 가능. LibreOffice 미설치 시 fixture 생성은 성공, 변환 테스트만 skip.              |

모든 게이트 통과 — Phase 0 진행.

### Post-Design Re-check (Phase 1 완료 후)

| Principle                       | Status  | Evidence                                                                                         |
| ------------------------------- | ------- | ------------------------------------------------------------------------------------------------ |
| I. Simple & Type-Safe Interface | ✅ PASS | fixture 함수는 `Path`를 반환하고 헬퍼 함수도 `Path`를 반환. 타입 어노테이션 일관적.              |
| II. Robust Automation           | ✅ PASS | odfpy `pytest.importorskip`, LibreOffice 미설치 시 `skipif` — graceful degradation 보장.         |
| III. Performance & Concurrency  | ✅ PASS | session-scope로 16개 fixture를 세션당 1회만 생성. SC-006 (테스트당 < 1초) 달성 예상.             |
| IV. Modern Python Standards     | ✅ PASS | rye dev-dependency 관리, pytest fixture 패턴, typing, pathlib 사용.                              |
| V. Reliability                  | ✅ PASS | 모든 fixture가 외부 파일 없이 Python 코드만으로 생성 (FR-003). 기존 테스트 무결성 유지 (FR-002). |

Post-design 게이트 통과 — 설계 확정.

## Project Structure

### Documentation (this feature)

```text
specs/002-test-fixture-gen/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── api.md           # Fixture API contracts
└── checklists/
    └── requirements.md  # Spec quality checklist (이미 존재)
```

### Source Code (repository root)

```text
tests/
├── __init__.py              # 기존 유지
├── conftest.py              # 신규: 모든 fixture 중앙 관리
├── fixture_helpers/         # 신규: fixture 생성 헬퍼 모듈
│   ├── __init__.py
│   ├── images.py            # PNG 이미지 생성 (Pillow)
│   ├── writer.py            # Writer 계열 fixture 생성 (docx, odt, rtf, html, txt)
│   ├── calc.py              # Calc 계열 fixture 생성 (xlsx, ods, csv, tsv)
│   └── impress.py           # Impress 계열 fixture 생성 (pptx, odp)
├── test_engine.py           # 기존 동기 테스트 (변경 없음)
├── test_async_engine.py     # 기존 비동기 테스트 (변경 없음)
├── test_formats.py          # 기존 포맷 레지스트리 테스트 (변경 없음)
├── test_backward_compat.py  # 기존 하위 호환성 테스트 (변경 없음)
├── test_fixture_writer.py   # 신규: Writer 계열 변환 테스트
├── test_fixture_calc.py     # 신규: Calc 계열 변환 테스트
├── test_fixture_impress.py  # 신규: Impress 계열 변환 테스트
├── test_fixture_images.py   # 신규: 이미지 생성 검증 테스트
└── test_fixture_edge.py     # 신규: 경계 조건 변환 테스트
```

**Structure Decision**: 기존 `tests/` 디렉토리에 `conftest.py`와 `fixture_helpers/` 서브패키지를 추가하는 구조. fixture 생성 로직을 `fixture_helpers/` 모듈에 분리하여 conftest.py를 간결하게 유지하고, 각 카테고리(Writer/Calc/Impress)의 생성 로직을 독립 관리한다. 기존 4개 테스트 파일은 변경하지 않는다.

## Complexity Tracking

해당 없음 — Constitution 위반 사항 없음.
