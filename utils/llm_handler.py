from langchain.prompts import PromptTemplate
from typing import List, Tuple, Generator, Dict
from utils.gpt4_client import GPT4Client
from models.response import Response
from models.document import Chunk
import logging

logger = logging.getLogger(__name__)

class LLMHandler:
    def __init__(self, temperature: float = 0.7):
        self.gpt4_client = GPT4Client()
        self.prompt_template = PromptTemplate(
            input_variables=["query", "context"],
            template="""基于以下内容回答问题:

问题: {query}

相关内容:
{context}

请提供一个完整、准确且信息丰富的回答:"""
        )
        
    def generate_response_stream(self, query: str, chunks: List[Chunk]) -> Generator[Dict, None, None]:
        """
        流式生成回答
        
        Args:
            query: 用户查询
            chunks: 相关的文本块列表
            
        Yields:
            Dict: 包含回答片段或源文档的字典
        """
        try:
            # 首先返回源文档信息
            sources = []
            for chunk in chunks:
                sources.append({
                    'url': chunk.source_url,
                    'title': chunk.title,
                    'score': float(chunk.score) if chunk.score is not None else 0.0
                })
            
            yield {'sources': sources}
            
            # 构建提示词
            context = "\n".join([chunk.text for chunk in chunks])
            prompt = f"基于以下信息回答问题:\n\n{context}\n\n问题: {query}\n\n回答:"
            
            # 使用LLM生成回答
            messages = [
                {"role": "user", "content": prompt}
            ]
            for token in self.gpt4_client.get_completion_stream(messages):
                yield {'content': token}
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            yield {'error': f"生成回答时发生错误: {str(e)}"} 

    def generate_response(self, query: str, chunks: List[Chunk]) -> Tuple[str, List[dict]]:
        """
        生成回答（非流式）
        
        Args:
            query: 用户查询
            chunks: 相关的文本块列表
            
        Returns:
            Tuple[str, List[dict]]: 回答文本和源文档列表
        """
        try:
            # 构建提示词
            context = "\n".join([chunk.text for chunk in chunks])
            prompt = f"基于以下信息回答问题:\n\n{context}\n\n问题: {query}\n\n回答:"
            
            # 生成回答
            answer = self.gpt4_client.generate(prompt)  # 根据具体LLM调整
            
            # 准备源文档信息
            sources = [{
                'url': chunk.source_url,
                'title': chunk.title,
                'score': float(chunk.score) if chunk.score is not None else 0.0
            } for chunk in chunks]
            
            return answer, sources
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise