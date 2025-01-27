import requests
from typing import List

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.query import SearchResult
from config.settings import SearchConfig
import logging

logger = logging.getLogger(__name__)

class SearchEngine:
    def __init__(self):
        self.config = SearchConfig()
        self.base_url = self.config.SEARX_BASE_URL
        self.engines = self.config.ENGINES
        self.max_results = self.config.MAX_RESULTS_PER_QUERY
        
    def search(self, query: str) -> List[SearchResult]:
        try:
            params = {
                'q': query,
                'format': 'json',
                'engines': ','.join(self.engines),
                'max_results': self.max_results
            }
            
            response = requests.get(
                f"{self.base_url}/search",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            results = response.json().get('results', [])
            return [
                SearchResult(
                    title=result.get('title', ''),
                    content=result.get('content', ''),
                    url=result.get('url', '')
                )
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return [] 
        
# 测试
if __name__ == "__main__":
    search_engine = SearchEngine()
    results = search_engine.search("什么是人工智能")
    print(results)
