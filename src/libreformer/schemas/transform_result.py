from dataclasses import dataclass
from typing import Sequence
from .succeed import Succeed
from .failed import Failed


@dataclass
class TransformResult:
    succeeds: Sequence[Succeed]
    failed: Sequence[Failed]
