from dataclasses import dataclass
from typing import List
from .document import Chunk

@dataclass
class Response:
    answer: str
    supporting_chunks: List[Chunk]
    confidence_score: float 