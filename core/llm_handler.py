from typing import List, Dict, Generator, Optional
from models.response import Response
from models.document import Chunk
from utils.gpt4_client import GPT4Client
from config.settings import ModelConfig
import logging

logger = logging.getLogger(__name__)

class LLMHandler:
    def __init__(self, llm_type: str = "gpt", model_name: Optional[str] = None):
        """
        初始化 LLMHandler
        
        Args:
            llm_type: 选择使用的客户端类型，可选值："gpt" 或 "ollama"
            model_name: Ollama 模型名称，仅在 client_type 为 "ollama" 时需要
        """
        self.llm_type = llm_type
        if llm_type == "gpt":
            self.client = GPT4Client()
        elif llm_type != "gpt":
            if not model_name:
                raise ValueError("model_name is required when using ollama client")
            from utils.ollama_client import OllamaClient
            self.client = OllamaClient()
            self.model_name = model_name
        else:
            raise ValueError(f"Unsupported client type: {llm_type}")

    def generate_response(self, query: str, relevant_chunks: List[Chunk]) -> Response:
        """
        使用 GPT-4 生成回答
        
        Args:
            query: 用户查询
            relevant_chunks: 相关的文本块列表
            
        Returns:
            Response 对象，包含答案、支持文本块和置信度
        """
        try:
            # 准备上下文
            context = "\n".join([
                f"文档{i+1}：{chunk.text}" 
                for i, chunk in enumerate(relevant_chunks)
            ])
            
            # 构建提示
            messages = [
                {
                    "role": "system",
                    "content": """你是一个专业的问答助手。请基于提供的文档内容，生成准确、连贯且有见地的回答。
                    如果文档内容不足以完全回答问题，请明确指出。回答应该：
                    1. 保持客观准确
                    2. 引用相关文档内容
                    3. 结构清晰
                    4. 易于理解
                    """
                },
                {
                    "role": "user",
                    "content": f"""
                    问题：{query}
                    
                    参考文档：
                    {context}
                    
                    请基于以上文档回答问题，必须采用跟问题相同的语种输出。
                    """
                }
            ]
                        
            # 根据客户端类型调用不同的生成方法
            if self.llm_type == "gpt":
                answer = self.client.get_completion(
                    messages=messages,
                    temperature=ModelConfig.LLM_TEMPERATURE,
                    max_tokens=1000,
                    top_p=0.95,
                    frequency_penalty=0,
                    presence_penalty=0
                )
            else:  # ollama
                answer = self.client.generate(
                    prompt=self._format_messages_for_ollama(messages),
                    model=self.model_name
                )
            
            if not answer:
                raise Exception("Failed to generate response")
            
            # 计算置信度（使用最高的块分数作为整体置信度）
            confidence = max([chunk.score for chunk in relevant_chunks]) if relevant_chunks else 0.0
            
            return Response(
                answer=answer,
                supporting_chunks=relevant_chunks,
                confidence_score=confidence
            )
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return Response(
                answer="抱歉，生成回答时出现错误。",
                supporting_chunks=[],
                confidence_score=0.0
            ) 

    def generate_response_stream(self, query: str, relevant_chunks: List[Chunk]) -> Generator[Dict, None, None]:
        """
        使用 GPT-4 生成流式回答
        
        Args:
            query: 用户查询
            relevant_chunks: 相关的文本块列表
            
        Yields:
            包含答案片段或源文档的字典
        """
        try:
            # 首先返回源文档信息
            yield {
                "sources": [
                    {
                        "url": chunk.source_url,
                        "title": chunk.title,
                        "score": float(chunk.score) if chunk.score is not None else None
                    } for chunk in relevant_chunks
                ]
            }
            
            # 准备上下文
            context = "\n".join([
                f"文档{i+1}：{chunk.text}" 
                for i, chunk in enumerate(relevant_chunks)
            ])
            
            # 构建提示
            messages = [
                {
                    "role": "system",
                    "content": """你是一个专业的问答助手。请基于提供的文档内容，生成准确、连贯且有见地的回答。
                    如果文档内容不足以完全回答问题，请明确指出。回答应该：
                    1. 保持客观准确
                    2. 引用相关文档内容
                    3. 结构清晰
                    4. 易于理解
                    """
                },
                {
                    "role": "user",
                    "content": f"""
                    问题：{query}
                    
                    参考文档：
                    {context}
                    
                    请基于以上文档回答问题，必须采用跟问题相同的语种输出。
                    """
                }
            ]
                        
            # 根据客户端类型调用不同的流式生成方法
            if self.llm_type == "gpt":
                for content in self.client.get_completion_stream(
                    messages=messages,
                    temperature=ModelConfig.LLM_TEMPERATURE,
                    max_tokens=1000
                ):
                    yield {"content": content}
            else:  # ollama
                for response in self.client.generate_stream(
                    prompt=self._format_messages_for_ollama(messages),
                    model=self.model_name
                ):
                    yield response
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            yield {"error": str(e)} 

    def _format_messages_for_ollama(self, messages: List[Dict[str, str]]) -> str:
        """
        将 GPT 格式的消息列表转换为 Ollama 可用的提示文本
        """
        formatted_prompt = ""
        for message in messages:
            role = message["role"]
            content = message["content"]
            if role == "system":
                formatted_prompt += f"System: {content}\n"
            elif role == "user":
                formatted_prompt += f"Human: {content}\n"
            elif role == "assistant":
                formatted_prompt += f"Assistant: {content}\n"
        return formatted_prompt.strip() 