from dataclasses import dataclass, field
from typing import List

@dataclass
class SearchConfig:
    SEARX_BASE_URL: str = "http://127.0.0.1:4008"
    ENGINES: List[str] = field(default_factory=lambda: ["google", "bing", "duckduckgo","baidu"])
    MAX_RESULTS_PER_QUERY: int = 5

class OllamaConfig:
    
    BASE_URL = "http://127.0.0.1:11434"
    DEFAULT_MODEL = "llama3:8b"  # 或其他默认模型
    TIMEOUT = 30  # 请求超时时间（秒）

@dataclass
class ProcessingConfig:
    CHUNK_SIZE: int = 100
    CHUNK_OVERLAP: int = 20
    MIN_CHUNK_LENGTH: int = 50
    MAX_CHUNKS_PER_DOC: int = 10
    SEMANTIC_REWRITE_LIMIT: int = 1
    SEMANTIC_EXPANSION_LIMIT: int = 1
@dataclass
class ModelConfig:
    RERANKER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    EMBEDDING_MODEL: str = "sentence-transformers/all-mpnet-base-v2"
    QUERY_REWRITE_MODEL: str = "facebook/bart-large"
    LLM_TEMPERATURE: float = 0.7
    TOP_K_RESULTS: int = 5
    LLM_MAX_TOKENS = 1000
    
    # 模型类型
    MODEL_TYPE_GPT4 = 'gpt4'
    MODEL_TYPE_OLLAMA = 'ollama'
    
    # 默认模型
    DEFAULT_MODEL = MODEL_TYPE_GPT4

@dataclass
class LogConfig:
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "rag_search.log" 