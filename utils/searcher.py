import requests
from typing import List, Dict
from config import Config

class Searcher:
    def __init__(self, base_url: str):
        self.base_url = base_url
        
    def search(self, query: str) -> List[Dict]:
        """使用SearxNG进行搜索"""
        params = {
            'q': query,
            'format': 'json',
            'engines': 'google,bing,duckduckgo',
            'max_results': Config.MAX_QUERY_RESULTS
        }
        
        response = requests.get(f"{self.base_url}/search", params=params)
        results = response.json().get('results', [])
        
        return [
            {
                'title': result.get('title', ''),
                'snippet': result.get('snippet', ''),
                'url': result.get('url', '')
            }
            for result in results
        ] 