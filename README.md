# LibreFormer

LibreFormer is a Python library that provides a convenient wrapper around LibreOffice for document conversion. It includes features for batch processing, **async parallel execution**, format registry, and automatic installation of LibreOffice on supported Linux systems.

## Features

- **Simple Interface**: Easy-to-use Python API for document conversion.
- **Async Parallel Processing**: `asyncio`-based async conversion with concurrency control.
- **Sync Parallel Processing**: `ProcessPoolExecutor`-based parallel batch conversion.
- **Format Registry**: Query 50+ input and 20+ output formats across Writer, Calc, Impress, Draw, Math, and Graphic categories.
- **Auto Installation**: Can automatically install LibreOffice via `apt` if missing (Linux only).
- **Type Enhancements**: Returns structured `Succeed` or `Failed` objects.

## Installation

This project is managed by `rye`.

```bash
git clone https://github.com/devcomfort/libreformer.git
cd libreformer
rye sync
```

## Usage

### Basic Conversion (Sync)

```python
from libreformer import LibreOfficeEngine, Succeed, Failed

# Initialize engine (auto_install=True tries to install LibreOffice if missing)
engine = LibreOfficeEngine(auto_install=True)

# Convert a single file
result = engine.transform("example.docx", "pdf")

if isinstance(result, Succeed):
    print(f"Success! Output saved to: {result.output_path}")
else:
    print(f"Failed: {result.error_message}")
```

### Async Conversion

```python
import asyncio
from libreformer import LibreOfficeEngine, Succeed

engine = LibreOfficeEngine(auto_install=False, max_concurrency=4, timeout=120.0)

# Single async conversion
result = await engine.async_transform("document.docx", "pdf")

# Batch async conversion (results stream as they complete)
files = ["doc1.txt", "doc2.md", "report.docx"]
async for result in engine.async_transform_parallel(files, "pdf"):
    if isinstance(result, Succeed):
        print(f"Converted → {result.output_path}")
```

### Sync Batch Processing

You can process multiple files in parallel:

```python
files = ["doc1.txt", "doc2.md", "presentation.pptx"]

# Convert all to PDF
results = engine.transform_parallel(files, "pdf")

for res in results:
    if isinstance(res, Succeed):
        print(f"Converted {res.file_path.name}")
    else:
        print(f"Error converting {res.file_path.name}: {res.error_message}")
```

### Format Query API

```python
from libreformer import FormatRegistry, DocumentCategory

# Check supported formats
inputs = FormatRegistry.supported_input_formats()   # {'docx', 'xlsx', 'pptx', ...}
outputs = FormatRegistry.supported_output_formats()  # {'pdf', 'html', 'csv', ...}

# Validate a conversion path
FormatRegistry.can_convert("docx", "pdf")  # True
FormatRegistry.can_convert("xyz", "pdf")   # False

# Browse by category
calc_formats = FormatRegistry.formats_by_category("calc")
for fmt in calc_formats:
    print(f"{fmt.extension} ({fmt.filter_name}) import={fmt.can_import} export={fmt.can_export}")

# Get export filter name for LibreOffice CLI
FormatRegistry.get_export_filter("docx", "pdf")  # "writer_pdf_Export"
```

### Callable Interface

The engine instance is also callable:

```python
# Same as transform()
result = engine("single_file.docx", "pdf")

# Same as transform_parallel()
results = engine(["file1.doc", "file2.doc"], "pdf")
```

### Constructor Parameters

| Parameter         | Type          | Default | Description                                           |
| ----------------- | ------------- | ------- | ----------------------------------------------------- |
| `auto_install`    | `bool`        | `True`  | Auto-install LibreOffice if missing (Linux)           |
| `max_concurrency` | `int \| None` | `None`  | Max concurrent async conversions (`None` = CPU count) |
| `timeout`         | `float`       | `300.0` | Per-conversion timeout in seconds                     |

## Testing

To run the tests:

```bash
rye run pytest -v
```

### Test Fixtures

The test suite includes programmatically generated test fixtures for all supported document categories. No external sample files are needed — all fixtures are generated at test time using Python libraries.

**Fixture Categories:**

| Category   | Fixtures                                                                                    | Libraries                          |
| ---------- | ------------------------------------------------------------------------------------------- | ---------------------------------- |
| Writer     | `sample_docx`, `sample_odt`, `sample_rtf`, `sample_html`, `sample_txt`                      | python-docx, odfpy                 |
| Calc       | `sample_xlsx`, `sample_ods`, `sample_csv`, `sample_tsv`                                     | openpyxl, odfpy                    |
| Impress    | `sample_pptx`, `sample_odp`                                                                 | python-pptx, odfpy                 |
| Edge Cases | `empty_docx`, `empty_xlsx`, `empty_pptx`, `large_xlsx`, `unicode_docx`, `special_chars_txt` | python-docx, openpyxl, python-pptx |

All fixtures are **session-scoped** — created once per test session for fast execution.

**Dev Dependencies** (installed automatically via `rye sync`):

- `python-docx>=1.1.0` — DOCX generation
- `openpyxl>=3.1.0` — XLSX generation
- `python-pptx>=0.6.23` — PPTX generation
- `Pillow>=10.0.0` — PNG image generation for document embedding
- `odfpy>=1.4.1` — ODF (ODT, ODS, ODP) generation
