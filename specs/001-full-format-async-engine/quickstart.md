# Quickstart: Full-Format Async Conversion Engine

**Date**: 2026-02-12
**Feature**: 001-full-format-async-engine

## 설치

```bash
git clone <repository-url>
cd libreformer
rye sync
```

## 기본 사용법 (동기 — 기존과 동일)

```python
from libreformer import LibreOfficeEngine, Succeed, Failed

engine = LibreOfficeEngine(auto_install=True)

# 단일 파일 변환
result = engine.transform("document.docx", "pdf")

if isinstance(result, Succeed):
    print(f"변환 완료: {result.output_path}")
else:
    print(f"변환 실패: {result.error_message}")
```

## 비동기 변환 (신규)

```python
import asyncio
from libreformer import LibreOfficeEngine, Succeed

engine = LibreOfficeEngine(max_concurrency=4, timeout=300.0)

async def convert_single():
    result = await engine.async_transform("report.xlsx", "pdf")
    if isinstance(result, Succeed):
        print(f"변환 완료: {result.output_path}")

asyncio.run(convert_single())
```

## 비동기 배치 변환 (신규)

```python
import asyncio
from libreformer import LibreOfficeEngine, Succeed, Failed

engine = LibreOfficeEngine(max_concurrency=4)

async def convert_batch():
    files = ["doc1.docx", "doc2.pptx", "doc3.xlsx"]

    # 모두 PDF로 변환
    async for result in engine.async_transform_parallel(files, "pdf"):
        if isinstance(result, Succeed):
            print(f"✓ {result.file_path.name} → {result.output_path.name}")
        else:
            print(f"✗ {result.file_path.name}: {result.error_message}")

asyncio.run(convert_batch())
```

### 파일별 다른 포맷으로 변환

```python
async def convert_mixed():
    files = ["report.docx", "data.xlsx", "slides.pptx"]
    formats = ["pdf", "csv", "pdf"]

    async for result in engine.async_transform_parallel(files, formats):
        print(result)

asyncio.run(convert_mixed())
```

## 포맷 조회 및 검증 (신규)

```python
from libreformer import LibreOfficeEngine, FormatRegistry, DocumentCategory

# 변환 가능 여부 사전 확인
print(LibreOfficeEngine.can_convert("docx", "pdf"))   # True
print(LibreOfficeEngine.can_convert("xyz", "pdf"))     # False

# 지원 포맷 목록 확인
input_formats = LibreOfficeEngine.supported_input_formats()
output_formats = LibreOfficeEngine.supported_output_formats()
print(f"입력 가능: {len(input_formats)}종")
print(f"출력 가능: {len(output_formats)}종")

# 카테고리별 포맷 조회
calc_formats = FormatRegistry.formats_by_category("calc")
for fmt in calc_formats:
    print(f"  {fmt.extension}: {fmt.filter_name} (import={fmt.can_import}, export={fmt.can_export})")

# 특정 확장자 정보 조회
docx_info = FormatRegistry.get_format("docx")
print(docx_info)
```

## 동기 배치 변환 (기존과 동일)

```python
from libreformer import LibreOfficeEngine

engine = LibreOfficeEngine()

files = ["a.txt", "b.txt", "c.txt"]
for result in engine.transform_parallel(files, "pdf"):
    print(result)
```

## Callable 인터페이스 (기존과 동일)

```python
engine = LibreOfficeEngine()

# 단일 파일
result = engine("file.docx", "pdf")

# 배치
results = engine(["a.doc", "b.doc"], "pdf")
```
