from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Query:
    original_text: str
    rewritten_queries: List[str] = None
    timestamp: float = None
    
    def __post_init__(self):
        import time
        self.timestamp = time.time()
        self.rewritten_queries = self.rewritten_queries or [self.original_text]

@dataclass
class SearchResult:
    title: str
    content: str
    url: str
    score: Optional[float] = None 