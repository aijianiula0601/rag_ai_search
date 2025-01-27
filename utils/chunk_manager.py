from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config.settings import ProcessingConfig
import logging

logger = logging.getLogger(__name__)

class ChunkManager:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=ProcessingConfig.CHUNK_SIZE,
            chunk_overlap=ProcessingConfig.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""]
        )
        
    def create_chunks(self, text: str) -> List[str]:
        """
        使用 Langchain 的 RecursiveCharacterTextSplitter 进行文本分块
        
        Args:
            text: 输入文本
            
        Returns:
            分块后的文本列表
        """
        try:
            if not text:
                return []
            if len(text) < ProcessingConfig.MIN_CHUNK_LENGTH:
                return [text]
                
            chunks = self.text_splitter.split_text(text)
            
            # 过滤掉太短的块
            valid_chunks = [
                chunk for chunk in chunks 
                if len(chunk) >= ProcessingConfig.MIN_CHUNK_LENGTH
            ]
            
            # 限制每个文档的最大块数
            if len(valid_chunks) > ProcessingConfig.MAX_CHUNKS_PER_DOC:
                logger.warning(f"Truncating chunks from {len(valid_chunks)} to {ProcessingConfig.MAX_CHUNKS_PER_DOC}")
                valid_chunks = valid_chunks[:ProcessingConfig.MAX_CHUNKS_PER_DOC]
                
            return valid_chunks
            
        except Exception as e:
            logger.error(f"Error creating chunks: {str(e)}")
            return []
            
    def merge_small_chunks(self, chunks: List[str], min_size: int) -> List[str]:
        """
        合并过小的文本块
        
        Args:
            chunks: 文本块列表
            min_size: 最小块大小
            
        Returns:
            合并后的文本块列表
        """
        if not chunks:
            return []
            
        merged = []
        current_chunk = chunks[0]
        
        for chunk in chunks[1:]:
            if len(current_chunk) < min_size:
                current_chunk = current_chunk + " " + chunk
            else:
                merged.append(current_chunk)
                current_chunk = chunk
                
        if current_chunk:
            merged.append(current_chunk)
            
        return merged
        
    def split_and_merge(self, text: str) -> List[str]:
        """
        分块并合并过小的块
        
        Args:
            text: 输入文本
            
        Returns:
            处理后的文本块列表
        """
        chunks = self.create_chunks(text)
        return self.merge_small_chunks(chunks, ProcessingConfig.MIN_CHUNK_LENGTH) 