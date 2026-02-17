from dataclasses import dataclass
from pathlib import Path


@dataclass
class Succeed:
    file_path: Path
    output_path: Path
