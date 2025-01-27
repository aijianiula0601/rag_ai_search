from typing import List, Dict
from bs4 import BeautifulSoup
import re

class Preprocessor:
    @staticmethod
    def clean_text(text: str) -> str:
        """清理文本"""
        # 移除HTML标签
        text = BeautifulSoup(text, "html.parser").get_text()
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    @staticmethod
    def create_chunks(text: str, chunk_size: int, overlap: int) -> List[str]:
        """将文本分割成chunks"""
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            if end > text_length:
                end = text_length
            
            chunk = text[start:end]
            chunks.append(chunk)
            
            start = end - overlap
            
        return chunks 