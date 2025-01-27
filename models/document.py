from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Chunk:
    text: str
    score: Optional[float] = None
    metadata: Optional[dict] = None
    source_url: str = None
    title: str = None
    
@dataclass
class Document:
    chunks: List[Chunk]
    source_url: str
    title: str 