# Tasks: Programmatic Test Fixture Generation

**Input**: Design documents from `/specs/002-test-fixture-gen/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/api.md ✅, quickstart.md ✅

**Tests**: 변환 테스트 포함 (spec.md의 각 User Story에 Independent Test가 명시됨)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/libreformer/` (기존), `tests/` (기존 + 신규)
- Fixture 헬퍼: `tests/fixture_helpers/`
- Fixture 등록: `tests/conftest.py`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: dev-dependency 추가 및 fixture_helpers 패키지 초기화

- [x] T001 Add python-docx, openpyxl, python-pptx, Pillow, odfpy to dev-dependencies in pyproject.toml
- [x] T002 Run `rye sync` to install all new dev-dependencies
- [x] T003 [P] Create fixture_helpers package with `tests/fixture_helpers/__init__.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 이미지 생성 헬퍼 — US1(docx), US3(pptx)의 이미지 삽입에 필요한 공유 인프라

**⚠️ CRITICAL**: 이미지가 필요한 fixture(sample_docx, sample_pptx)는 이 단계 완료 후 구현 가능

- [x] T004 Implement `create_test_image()` function in tests/fixture_helpers/images.py (Pillow로 200×200 PNG 생성, BytesIO bytes 반환)
- [x] T005 Register `test_image_bytes` session-scope fixture in tests/conftest.py (create_test_image() 호출, bytes 반환)

**Checkpoint**: 이미지 생성 인프라 완료 — User Story 구현 시작 가능

---

## Phase 3: User Story 4 - 문서 삽입용 이미지 프로그래밍 생성 (Priority: P2, but foundational dependency)

**Goal**: Pillow로 PNG 이미지를 생성하고, 해당 이미지가 docx/pptx에 삽입 가능한지 검증

**Independent Test**: `test_image_bytes` fixture가 100×100 이상 유효한 PNG bytes를 반환하는지 확인

> **Note**: US4는 P2이지만, US1(docx with image)과 US3(pptx with image)의 빌딩 블록이므로 Phase 2에서 이미 구현됨. 이 phase에서는 검증 테스트만 추가.

- [x] T006 [US4] Create test file tests/test_fixture_images.py with test for create_test_image() output validation (PNG header, size >= 100×100)

**Checkpoint**: 이미지 생성 검증 완료

---

## Phase 4: User Story 5 + User Story 1 - conftest.py 통합 관리 & Writer 계열 Fixture (Priority: P1) 🎯 MVP

**Goal**: conftest.py에 Writer 계열 fixture(docx, odt, rtf, html, txt) 등록. 기존 테스트 무결성 유지.

**Independent Test**: `sample_docx` fixture로 docx→pdf 변환 후 `Succeed` 확인, 출력 파일 크기 > 0. 기존 `test_engine.py` 2개 테스트 수정 없이 통과.

### Implementation for US5 + US1

> **[P] 참고**: T007-T011은 모두 `writer.py` 내 독립 함수이므로 논리적으로 병렬 가능하나, 같은 파일을 편집하므로 실제 구현 시 순차 커밋을 권장합니다.

- [x] T007 [P] [US1] Implement `create_docx(path, image_bytes)` in tests/fixture_helpers/writer.py ("제품 사양서" 시나리오: heading, paragraphs, 3×3 table, inline image via python-docx)
- [x] T008 [P] [US1] Implement `create_odt(path)` in tests/fixture_helpers/writer.py (odfpy, pytest.importorskip 사용, heading + paragraphs + table)
- [x] T009 [P] [US1] Implement `create_rtf(path)` in tests/fixture_helpers/writer.py (순수 RTF 마크업 문자열)
- [x] T010 [P] [US1] Implement `create_html(path)` in tests/fixture_helpers/writer.py (HTML 마크업 with heading, paragraph, table)
- [x] T011 [P] [US1] Implement `create_txt(path)` in tests/fixture_helpers/writer.py (일반 텍스트, "제품 사양서" 내용)
- [x] T013 [US5] Register all Writer fixtures in tests/conftest.py (sample_docx, sample_odt, sample_rtf, sample_html, sample_txt — session-scope, tmp_path_factory)
- [x] T014 [US1] Create tests/test_fixture_writer.py with conversion tests: docx→pdf, odt→pdf, rtf→pdf, html→pdf, txt→pdf (skipif LibreOffice not installed, odt uses importorskip)
- [x] T015 [US5] Verify existing tests/test_engine.py passes without modification (run full test suite)

**Checkpoint**: Writer 계열 5종 fixture 완료, conftest.py 통합, 기존 테스트 무결성 확인 — MVP 달성

---

## Phase 5: User Story 2 - Calc 계열 테스트 스프레드시트 생성 (Priority: P1)

**Goal**: Calc 계열 fixture(xlsx, ods, csv, tsv) 구현. "월별 매출 보고서" 데이터.

**Independent Test**: `sample_xlsx` fixture로 xlsx→pdf 변환 후 `Succeed` 확인.

### Implementation for US2

- [x] T016 [P] [US2] Implement `create_xlsx(path)` in tests/fixture_helpers/calc.py ("월별 매출 보고서": headers, 12월×3지역=36행, SUM/AVERAGE 수식 via openpyxl)
- [x] T017 [P] [US2] Implement `create_ods(path)` in tests/fixture_helpers/calc.py (odfpy, pytest.importorskip, 동일 데이터 구조)
- [x] T018 [P] [US2] Implement `create_csv(path)` in tests/fixture_helpers/calc.py (csv.writer, 매출 데이터)
- [x] T019 [P] [US2] Implement `create_tsv(path)` in tests/fixture_helpers/calc.py (csv.writer with delimiter='\t')
- [x] T020 [US2] Register all Calc fixtures in tests/conftest.py (sample_xlsx, sample_ods, sample_csv, sample_tsv — session-scope)
- [x] T021 [US2] Create tests/test_fixture_calc.py with conversion tests: xlsx→pdf, ods→pdf, csv→pdf, tsv→pdf (skipif LibreOffice, ods uses importorskip)

**Checkpoint**: Calc 계열 4종 fixture 완료 — P1 User Stories 모두 완성

---

## Phase 6: User Story 3 - Impress 계열 테스트 프레젠테이션 생성 (Priority: P2)

**Goal**: Impress 계열 fixture(pptx, odp) 구현. "분기 실적 발표" 데이터 + 이미지 슬라이드.

**Independent Test**: `sample_pptx` fixture로 pptx→pdf 변환 후 `Succeed` 확인.

### Implementation for US3

- [x] T022 [P] [US3] Implement `create_pptx(path, image_bytes)` in tests/fixture_helpers/impress.py ("분기 실적 발표": title slide, content slide with bullets, image slide via python-pptx)
- [x] T023 [P] [US3] Implement `create_odp(path)` in tests/fixture_helpers/impress.py (odfpy, pytest.importorskip, title + content slides)
- [x] T024 [US3] Register all Impress fixtures in tests/conftest.py (sample_pptx, sample_odp — session-scope, sample_pptx depends on test_image_bytes)
- [x] T025 [US3] Create tests/test_fixture_impress.py with conversion tests: pptx→pdf, odp→pdf (skipif LibreOffice, odp uses importorskip)

**Checkpoint**: Impress 계열 2종 fixture 완료 — P2 User Stories 모두 완성

---

## Phase 7: User Story 6 - 다양한 데이터 시나리오 Fixture (Priority: P3)

**Goal**: 경계 조건 fixture(empty_docx, empty_xlsx, empty_pptx, large_xlsx, unicode_docx, special_chars_txt) 구현.

**Independent Test**: `empty_docx` fixture로 빈 문서 변환 시 `Succeed` 또는 합리적 `Failed` 반환 확인.

### Implementation for US6

> **[P] 참고**: T026-T031은 서로 다른 파일의 독립 함수이므로 병렬 가능합니다. 단, 같은 파일 내 함수(T026-T028, T030)는 순차 커밋을 권장합니다.

- [x] T026 [P] [US6] Implement empty_docx creation logic in tests/fixture_helpers/writer.py (python-docx Document() with no content, save)
- [x] T027 [P] [US6] Implement empty_xlsx creation logic in tests/fixture_helpers/calc.py (openpyxl Workbook() with empty sheet, save)
- [x] T028 [P] [US6] Implement empty_pptx creation logic in tests/fixture_helpers/impress.py (python-pptx Presentation() with no slides, save)
- [x] T029 [P] [US6] Implement unicode_docx creation logic in tests/fixture_helpers/writer.py (한국어·일본어·아랍어·이모지 텍스트 포함 docx)
- [x] T030 [P] [US6] Implement special_chars_txt creation logic in tests/fixture_helpers/writer.py (특수 문자·탭·개행·제어 문자 포함 txt)
- [x] T031 [P] [US6] Implement large_xlsx creation logic in tests/fixture_helpers/calc.py (1000+행 스프레드시트 via openpyxl)
- [x] T032 [US6] Register all edge case fixtures in tests/conftest.py (empty_docx, empty_xlsx, empty_pptx, large_xlsx, unicode_docx, special_chars_txt — session-scope)
- [x] T033 [US6] Create tests/test_fixture_edge.py with conversion tests: empty_docx→pdf, empty_xlsx→pdf, empty_pptx→pdf, large_xlsx→pdf, unicode_docx→pdf, special_chars_txt→pdf (skipif LibreOffice)

**Checkpoint**: 경계 조건 6종 fixture 완료 — 모든 User Stories 완성

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: 전체 테스트 스위트 검증, 문서 업데이트, 코드 품질 개선

- [x] T034 [P] Run full test suite via `run_tests.sh` (기존 42 tests + 신규 fixture tests) and verify all pass
- [x] T035 [P] Verify SC-001: 최소 10종 포맷 fixture 존재 확인 (docx, odt, xlsx, ods, pptx, odp, csv, tsv, html, rtf, txt = 11종)
- [x] T036 [P] Verify SC-003: 기존 test_engine.py 2개 테스트가 수정 없이 통과
- [x] T037 [P] Verify SC-005: pyproject.toml에 모든 dev-dependency 명시 확인
- [x] T038 [P] Verify SC-006: fixture 생성 시간 < 1초/테스트 (변환 제외) 확인
- [x] T038a [P] Run linting/formatting check (헌법 Development Workflow 준수: `ruff check`, `ruff format --check` 또는 프로젝트의 린터 설정 적용)
- [x] T039 Update README.md with test fixture documentation (사용법, 의존성)
- [x] T040 Run quickstart.md validation (quickstart 예제 코드가 실제 동작하는지 확인)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 (T003 필요) — BLOCKS image-dependent fixtures
- **US4 Verification (Phase 3)**: Depends on Phase 2 (T004, T005)
- **US5+US1 Writer (Phase 4)**: Depends on Phase 2 (image bytes for docx) — **MVP**
- **US2 Calc (Phase 5)**: Depends on Phase 1 only (no image dependency) — can run in parallel with Phase 4
- **US3 Impress (Phase 6)**: Depends on Phase 2 (image bytes for pptx)
- **US6 Edge Cases (Phase 7)**: Depends on Phase 1 only — can run in parallel with Phase 4-6
- **Polish (Phase 8)**: Depends on all previous phases

### User Story Dependencies

- **US4 (이미지)**: 독립적 — Phase 2에서 완료, Phase 3에서 검증
- **US5 (conftest)**: US1과 통합 구현 — fixture 등록은 각 US 구현과 함께
- **US1 (Writer)**: US4 의존 (docx에 이미지 삽입)
- **US2 (Calc)**: 독립적 — US1/US3/US4에 의존하지 않음
- **US3 (Impress)**: US4 의존 (pptx에 이미지 삽입)
- **US6 (Edge Cases)**: 독립적 — 기본 fixture 패턴만 필요

### Within Each User Story

- Helper functions (fixture_helpers/) → conftest.py fixture 등록 → 테스트 파일 작성
- [P] 표시된 helper functions는 병렬 구현 가능

### Parallel Opportunities

- T007-T011: Writer 헬퍼 5개 모두 병렬 (서로 다른 포맷, 같은 파일이지만 독립 함수)
- T016-T019: Calc 헬퍼 4개 모두 병렬
- T022-T023: Impress 헬퍼 2개 병렬
- T026-T031: Edge case 헬퍼 6개 병렬 (서로 다른 파일의 독립 함수)
- Phase 4 (Writer) ↔ Phase 5 (Calc): 병렬 가능 (서로 다른 파일, 독립적)
- T034-T038: 검증 태스크 모두 병렬

---

## Parallel Example: User Story 1 (Writer)

```bash
# Launch all Writer helper functions together (different functions, same file):
Task T007: "create_docx() in tests/fixture_helpers/writer.py"
Task T008: "create_odt() in tests/fixture_helpers/writer.py"
Task T009: "create_rtf() in tests/fixture_helpers/writer.py"
Task T010: "create_html() in tests/fixture_helpers/writer.py"
Task T011: "create_txt() in tests/fixture_helpers/writer.py"

# Then sequentially:
Task T013: "Register fixtures in conftest.py" (depends on T007-T011)
Task T014: "Create test_fixture_writer.py" (depends on T013)
Task T015: "Verify existing tests" (depends on T014)
```

## Parallel Example: Phase 4 ↔ Phase 5

```bash
# These two phases can run in parallel:
# Developer A: Phase 4 (Writer fixtures — T007-T015)
# Developer B: Phase 5 (Calc fixtures — T016-T021)

# Phase 6 (Impress) can start after Phase 2, in parallel with Phase 4/5
```

---

## Implementation Strategy

### MVP First (User Story 5 + 1: conftest + Writer)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational — image helper (T004-T005)
3. Complete Phase 4: US5+US1 Writer fixtures (T007-T015)
4. **STOP and VALIDATE**: 기존 42 tests + Writer 변환 tests 모두 통과 확인
5. MVP 달성: 5종 Writer 포맷 fixture + conftest.py 통합 + 기존 테스트 호환

### Incremental Delivery

1. Setup + Foundational → 이미지 인프라 완료
2. US5+US1 Writer → Test → **MVP!** (5종 포맷)
3. US2 Calc → Test → 9종 포맷 (SC-001 달성, 10종 기준 이상)
4. US3 Impress → Test → 11종 포맷
5. US6 Edge Cases → Test → 경계 조건 6종 추가
6. Polish → 전체 검증 + 문서화

### Key Validation Points

- **After Phase 4**: 기존 42 tests 통과 + docx→pdf 변환 성공 = MVP
- **After Phase 5**: SC-001 달성 (10종+ 포맷)
- **After Phase 7**: 전체 17종 fixture 완성 (11종 포맷 + 6종 edge case)
- **After Phase 8**: 모든 SC-001~SC-006 달성

---

## Notes

- [P] tasks = different files/functions, no dependencies
- [Story] label maps task to specific user story for traceability
- odfpy 관련 fixture(odt, ods, odp)는 `pytest.importorskip("odf")` 사용
- LibreOffice 미설치 시 변환 테스트는 `skipif`로 건너뜀
- 기존 test_engine.py, test_async_engine.py, test_formats.py, test_backward_compat.py는 **수정 금지**
- Commit after each phase or logical group
