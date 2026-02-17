# Tasks: Full-Format Async Conversion Engine

**Input**: Design documents from `/specs/001-full-format-async-engine/`
**Prerequisites**: plan.md (✅), spec.md (✅), research.md (✅), data-model.md (✅), contracts/api.md (✅)

**Tests**: 테스트 태스크를 포함한다 — spec에서 pytest 기반 테스트가 명시적으로 요구됨.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/libreformer/`, `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: 프로젝트 구조 확장 및 새로운 의존성 추가

- [ ] T001 Add `pytest-asyncio` to dev-dependencies in `pyproject.toml`
- [ ] T002 [P] Create `src/libreformer/formats/` package directory with `src/libreformer/formats/__init__.py`
- [ ] T003 [P] Create `DocumentCategory` enum in `src/libreformer/formats/categories.py`
- [ ] T004 [P] Create `FormatInfo` dataclass in `src/libreformer/schemas/format_info.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 포맷 레지스트리 및 비동기 로깅 — 모든 User Story가 의존하는 핵심 인프라

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Populate LibreOffice Writer format data constants in `src/libreformer/formats/data.py` (all Writer import/export FormatInfo entries per research.md)
- [ ] T006 Populate LibreOffice Calc format data constants in `src/libreformer/formats/data.py` (append Calc entries)
- [ ] T007 Populate LibreOffice Impress format data constants in `src/libreformer/formats/data.py` (append Impress entries)
- [ ] T008 Populate LibreOffice Draw format data constants in `src/libreformer/formats/data.py` (append Draw entries)
- [ ] T009 Populate LibreOffice Math format data constants in `src/libreformer/formats/data.py` (append Math entries)
- [ ] T010 Populate GraphicFilter export format data constants in `src/libreformer/formats/data.py` (append Graphic entries: jpg, png, svg, webp)
- [ ] T011 Implement `FormatRegistry` class with `all_formats()`, `supported_input_formats()`, `supported_output_formats()`, `can_convert()`, `formats_by_category()`, `get_format()`, `get_export_filter()` in `src/libreformer/formats/registry.py`
- [ ] T012 Export `FormatRegistry` and `DocumentCategory` from `src/libreformer/formats/__init__.py`
- [ ] T013 Export `FormatInfo` from `src/libreformer/schemas/__init__.py`
- [ ] T014 Add async elapsed time logging decorator `async_log_elapsed_time` in `src/libreformer/logging.py`
- [ ] T015 Extend `LibreOfficeEngine.__init__` to accept `max_concurrency` and `timeout` parameters in `src/libreformer/engine.py` (preserve backward compatibility — both params optional with defaults)

**Checkpoint**: FormatRegistry 동작, 엔진 생성자 확장 완료 — User Story 구현 가능

---

## Phase 3: User Story 1 — 단일 문서 비동기 변환 (Priority: P1) 🎯 MVP

**Goal**: `await engine.async_transform(file, "pdf")` 로 단일 파일을 비동기 변환하여 `Succeed | Failed` 반환

**Independent Test**: `.txt` 파일을 PDF로 비동기 변환 → `Succeed` 확인, 존재하지 않는 파일 → `Failed` 확인

### Tests for User Story 1

- [ ] T016 [P] [US1] Write async single-file conversion tests in `tests/test_async_engine.py` — test success case (txt→pdf), file-not-found case, unsupported format case, timeout case. Tests must FAIL before implementation.

### Implementation for User Story 1

- [ ] T017 [US1] Implement `async_transform(file_path: str, to: str) -> Succeed | Failed` method in `src/libreformer/engine.py` using `asyncio.create_subprocess_exec`, `asyncio.Semaphore`, `asyncio.wait_for` with timeout, unique UserInstallation directory per process
- [ ] T018 [US1] Apply `async_log_elapsed_time` decorator to `async_transform` in `src/libreformer/engine.py`
- [ ] T019 [US1] Verify US1 tests pass by running `tests/test_async_engine.py`

**Checkpoint**: 단일 비동기 변환 동작 확인 — MVP의 핵심

---

## Phase 4: User Story 2 — 대량 문서 비동기 병렬 변환 (Priority: P1)

**Goal**: `async for result in engine.async_transform_parallel(files, "pdf"):` 로 대량 파일을 비동기 병렬 변환, 완료 순서대로 결과 yield

**Independent Test**: 10개 텍스트 파일을 비동기 병렬 변환 → 10개 결과 수신, 파일별 다른 포맷 변환, 길이 불일치 시 ValueError 확인

### Tests for User Story 2

- [ ] T020 [P] [US2] Write async batch conversion tests in `tests/test_async_engine.py` — test batch same-format, batch mixed-format, length mismatch ValueError. Tests must FAIL before implementation.

### Implementation for User Story 2

- [ ] T021 [US2] Implement `async_transform_parallel(file_paths, to) -> AsyncIterator[Succeed | Failed]` method in `src/libreformer/engine.py` using `asyncio.create_task` + `asyncio.as_completed` pattern, with Semaphore concurrency control
- [ ] T022 [US2] Add overload type signatures for `async_transform_parallel` (single `str` to, `Sequence[str]` to) in `src/libreformer/engine.py`
- [ ] T023 [US2] Verify US2 tests pass by running `tests/test_async_engine.py`

**Checkpoint**: 비동기 병렬 변환 동작 확인

---

## Phase 5: User Story 3 — 지원 포맷 조회 및 검증 (Priority: P2)

**Goal**: `engine.supported_input_formats()`, `engine.can_convert("docx", "pdf")` 등으로 포맷 조회/검증 가능

**Independent Test**: `supported_input_formats()` → 50+ 확장자, `can_convert("docx", "pdf")` → True, `can_convert("xyz", "pdf")` → False 확인

### Tests for User Story 3

- [ ] T024 [P] [US3] Write format registry tests in `tests/test_formats.py` — test `all_formats()` returns non-empty, `supported_input_formats()` contains expected extensions (docx, xlsx, pptx, odt, ods, odp), `supported_output_formats()` contains (pdf, docx, html, csv, png), `can_convert()` true/false cases, `formats_by_category()` writer/calc/impress filtering, `get_format("html")` returns multiple categories, `get_export_filter()` returns filter name or None. Tests must FAIL before implementation.

### Implementation for User Story 3

- [ ] T025 [US3] Add format convenience methods to `LibreOfficeEngine` class as static delegations to `FormatRegistry` in `src/libreformer/engine.py`: `supported_input_formats()`, `supported_output_formats()`, `can_convert()`, `formats_by_category()`
- [ ] T026 [US3] Update `src/libreformer/__init__.py` to export `FormatRegistry`, `DocumentCategory`, `FormatInfo`
- [ ] T027 [US3] Verify US3 tests pass by running `tests/test_formats.py`

**Checkpoint**: 포맷 조회/검증 API 동작 확인

---

## Phase 6: User Story 4 — 동기 API 하위 호환성 유지 (Priority: P2)

**Goal**: 기존 `transform()`, `transform_parallel()`, `__call__` 동기 API가 변경 없이 동작

**Independent Test**: 기존 `tests/test_engine.py`가 수정 없이 통과

### Tests for User Story 4

- [ ] T028 [P] [US4] Write backward compatibility regression tests in `tests/test_backward_compat.py` — verify `engine.transform()` sync signature, `engine.transform_parallel()` sync signature, `engine(file, to)` callable interface, constructor with only `auto_install` param still works. Tests must FAIL before implementation.

### Implementation for User Story 4

- [ ] T029 [US4] Verify existing `tests/test_engine.py` passes without any modifications after all engine.py changes
- [ ] T030 [US4] Verify `tests/test_backward_compat.py` passes confirming all legacy interfaces work

**Checkpoint**: 하위 호환성 100% 확인

---

## Phase 7: User Story 5 — 동시성 제한 및 리소스 관리 (Priority: P3)

**Goal**: `max_concurrency=N` 설정으로 동시 LibreOffice 프로세스 수를 제한

**Independent Test**: `max_concurrency=2`로 10파일 변환 시 동시 프로세스 ≤ 2 확인

### Tests for User Story 5

- [ ] T031 [P] [US5] Write concurrency control tests in `tests/test_async_engine.py` — test that `max_concurrency=2` limits concurrent execution count, test default `max_concurrency` uses CPU count, test `max_concurrency` parameter validation (>= 1). Tests must FAIL before implementation.

### Implementation for User Story 5

- [ ] T032 [US5] Add `max_concurrency` validation in `LibreOfficeEngine.__init__` in `src/libreformer/engine.py` (raise `ValueError` if < 1)
- [ ] T033 [US5] Add `timeout` validation in `LibreOfficeEngine.__init__` in `src/libreformer/engine.py` (raise `ValueError` if <= 0)
- [ ] T034 [US5] Verify US5 tests pass by running concurrency tests in `tests/test_async_engine.py`

**Checkpoint**: 동시성 제어 동작 확인

---

## Phase 8: User Story 6 — 문서 카테고리별 포맷 매핑 (Priority: P3)

**Goal**: `engine.formats_by_category("calc")` 로 카테고리별 포맷 조회

**Independent Test**: `formats_by_category("calc")` → Calc 포맷만 반환, 유효하지 않은 카테고리 → 빈 리스트

### Tests for User Story 6

- [ ] T035 [P] [US6] Write category-based format tests in `tests/test_formats.py` — test each category (writer, calc, impress, draw, math, graphic) returns only its formats, test invalid category returns empty list, test string and enum input both work. Tests must FAIL before implementation.

### Implementation for User Story 6

- [ ] T036 [US6] Ensure `formats_by_category` in `FormatRegistry` handles both `str` and `DocumentCategory` input with case-insensitive matching in `src/libreformer/formats/registry.py` (should already be done in T011, verify/fix)
- [ ] T037 [US6] Verify US6 tests pass by running `tests/test_formats.py`

**Checkpoint**: 카테고리별 포맷 조회 동작 확인

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: 문서화, 정리, 전체 검증

- [ ] T038 [P] Update `README.md` with async usage examples, format query API, new constructor parameters
- [ ] T039 [P] Update `src/libreformer/__init__.py` `__all__` to include all new public exports
- [ ] T040 Code cleanup — remove unused imports, ensure consistent code style across all modified files
- [ ] T041 Run full test suite (`rye run pytest -v`) and verify all tests pass
- [ ] T042 Run quickstart.md validation — manually test each code snippet from `specs/001-full-format-async-engine/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 (T002-T004 for package structure)
- **US1 (Phase 3)**: Depends on Phase 2 (FormatRegistry, engine constructor, async logging)
- **US2 (Phase 4)**: Depends on US1 (async_transform must exist for async_transform_parallel)
- **US3 (Phase 5)**: Depends on Phase 2 only (FormatRegistry)
- **US4 (Phase 6)**: Depends on Phase 2 (engine constructor changes must preserve compatibility)
- **US5 (Phase 7)**: Depends on US1 (Semaphore behavior tested via async_transform)
- **US6 (Phase 8)**: Depends on Phase 2 only (FormatRegistry)
- **Polish (Phase 9)**: Depends on all user stories

### User Story Dependencies

- **US1 (P1)**: Phase 2 → US1 (no other story dependency)
- **US2 (P1)**: Phase 2 → US1 → US2 (needs async_transform)
- **US3 (P2)**: Phase 2 → US3 (independent of US1/US2)
- **US4 (P2)**: Phase 2 → US4 (independent, tests existing sync API)
- **US5 (P3)**: Phase 2 → US1 → US5 (tests concurrency via async API)
- **US6 (P3)**: Phase 2 → US6 (independent, tests FormatRegistry)

### Parallel Opportunities

- **Phase 1**: T002, T003, T004 can run in parallel
- **Phase 2**: T005-T010 (format data) can run in parallel within `data.py`; T014 (async logging) is independent
- **After Phase 2**: US3, US4, US6 can start in parallel (all independent of async engine)
- **After US1**: US2, US5 can start (both depend on async_transform)
- **Within each story**: Tests and implementation tasks are sequential (TDD)

---

## Parallel Example: Post-Foundation

```text
# After Phase 2 completes, these can run in parallel:

Thread A (P1 critical path):
  US1: T016 → T017 → T018 → T019
  US2: T020 → T021 → T022 → T023

Thread B (P2 independent):
  US3: T024 → T025 → T026 → T027

Thread C (P2 independent):
  US4: T028 → T029 → T030

Thread D (P3 independent):
  US6: T035 → T036 → T037
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup → pyproject.toml 업데이트, 패키지 구조 생성
2. Complete Phase 2: Foundational → FormatRegistry 완성, 엔진 생성자 확장
3. Complete Phase 3: US1 → 단일 비동기 변환 동작
4. **STOP and VALIDATE**: `await engine.async_transform("file.txt", "pdf")` 동작 확인
5. 이 시점에서 MVP 배포/데모 가능

### Incremental Delivery

1. Setup + Foundational → 포맷 레지스트리 동작 (Phase 1-2)
2. US1 → 단일 비동기 변환 (Phase 3) → **MVP!**
3. US2 → 배치 비동기 변환 (Phase 4) → 핵심 완성
4. US3 + US4 → 포맷 조회 + 하위 호환 검증 (Phase 5-6)
5. US5 + US6 → 동시성 제어 + 카테고리 매핑 (Phase 7-8)
6. Polish (Phase 9) → 문서화 및 전체 검증

### Parallel Team Strategy

1. Team completes Setup + Foundational together (Phase 1-2)
2. Once Foundational is done:
   - Developer A: US1 → US2 → US5 (async critical path)
   - Developer B: US3 → US6 (format registry path)
   - Developer C: US4 (backward compat verification)
3. All converge for Phase 9: Polish

---

## Notes

- [P] tasks = different files, no dependencies
- TDD approach: Write tests first → verify they FAIL → implement → verify they PASS
- 기존 `tests/test_engine.py`는 절대 수정하지 않음 (하위 호환성 증명)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- `src/libreformer/formats/data.py`는 LibreOffice 공식 필터 문서 기반으로 작성 (research.md 참조)

## Summary

| Metric                 | Value                               |
| ---------------------- | ----------------------------------- |
| Total Tasks            | 42                                  |
| Phase 1 (Setup)        | 4                                   |
| Phase 2 (Foundational) | 11                                  |
| US1 (P1)               | 4                                   |
| US2 (P1)               | 4                                   |
| US3 (P2)               | 4                                   |
| US4 (P2)               | 3                                   |
| US5 (P3)               | 4                                   |
| US6 (P3)               | 3                                   |
| Phase 9 (Polish)       | 5                                   |
| Parallel Opportunities | 3 independent threads after Phase 2 |
| MVP Scope              | Phase 1 + Phase 2 + US1 (19 tasks)  |
