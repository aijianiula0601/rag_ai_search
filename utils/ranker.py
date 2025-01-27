from sentence_transformers import CrossEncoder
from typing import List, Tuple
import torch

class Ranker:
    def __init__(self, model_name: str):
        self.model = CrossEncoder(model_name)
        
    def rerank(self, query: str, chunks: List[str], top_k: int) -> List[Tuple[str, float]]:
        """对chunks进行重排序"""
        # 准备交叉编码器的输入
        pairs = [[query, chunk] for chunk in chunks]
        
        # 计算相似度分数
        scores = self.model.predict(pairs)
        
        # 将chunks和分数组合
        chunk_scores = list(zip(chunks, scores))
        
        # 按分数排序并返回top_k结果
        return sorted(chunk_scores, key=lambda x: x[1], reverse=True)[:top_k] 