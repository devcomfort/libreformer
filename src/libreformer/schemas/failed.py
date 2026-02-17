from dataclasses import dataclass
from pathlib import Path


@dataclass
class Failed:
    file_path: Path
    error_message: str
