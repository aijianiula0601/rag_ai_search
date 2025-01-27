from typing import List
from models.document import Document, Chunk
from utils.text_cleaner import TextCleaner
from utils.chunk_manager import ChunkManager
from sentence_transformers import CrossEncoder
from config.settings import ModelConfig, ProcessingConfig
import logging

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        self.text_cleaner = TextCleaner()
        self.chunk_manager = ChunkManager()
        self.reranker = CrossEncoder(ModelConfig.RERANKER_MODEL)
        
    def process_documents(self, search_results: List[dict]) -> List[Document]:
        """
        处理搜索结果，清理文本并创建文档块
        """
        documents = []
        for result in search_results:
            try:
                # 清理文本
                clean_text = self.text_cleaner.clean(result.content)
                
                # 使用 Langchain 进行分块
                chunks = self.chunk_manager.split_and_merge(clean_text)
                
                # 创建文档对象，为每个chunk添加文档信息
                doc = Document(
                    chunks=[Chunk(
                        text=chunk,
                        source_url=result.url,
                        title=result.title
                    ) for chunk in chunks],
                    source_url=result.url,
                    title=result.title
                )
                documents.append(doc)
                
            except Exception as e:
                logger.error(f"Error processing document: {str(e)}")
                continue
                
        return documents
    
    def rerank_chunks(self, query: str, documents: List[Document]) -> List[Chunk]:
        """
        对所有文档的块进行重排序
        返回的每个chunk都包含原始文档的url和title信息
        """
        try:
            # 收集所有块（每个块都包含source_url和title信息）
            all_chunks = []
            for doc in documents:
                all_chunks.extend(doc.chunks)
                
            if not all_chunks:
                return []
                
            # 准备重排序的输入
            pairs = [[query, chunk.text] for chunk in all_chunks]
            scores = self.reranker.predict(pairs)
                        
            # 更新块的分数
            for chunk, score in zip(all_chunks, scores):
                chunk.score = score
                
            # 排序并返回前K个结果（保留每个chunk的source_url和title）
            return sorted(
                all_chunks,
                key=lambda x: x.score if x.score is not None else -float('inf'),
                reverse=True
            )[:ModelConfig.TOP_K_RESULTS]
            
        except Exception as e:
            logger.error(f"Error reranking chunks: {str(e)}")
            return [] 