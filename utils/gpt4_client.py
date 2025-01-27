from openai import AzureOpenAI
import logging
import os
import sys
from typing import Optional, List, Dict, Any, Generator
import json

logger = logging.getLogger(__name__)

from dotenv import load_dotenv

# 加载 .env 文件设置的key
load_dotenv()  # 这会自动查找当前目录的 .env 文件

# 假设父级目录在 ../parent_folder
parent_path = os.path.abspath('../')
sys.path.append(parent_path)

api_key = os.getenv("gpt4o_mini_api_key")
api_version = os.getenv("gpt4o_mini_api_version")
azure_endpoint = os.getenv("gpt4o_mini_azure_endpoint")

class GPT4Client:
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=azure_endpoint
        )
        self.model_name = 'gpt-4o-mini'
        
    def get_completion_stream(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.5,
        top_p: float = 0.95,
        frequency_penalty: float = 0,
        presence_penalty: float = 0,
        stop: Optional[List[str]] = None
    ) -> Generator[str, None, None]:
        """
        获取 GPT-4 流式响应
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                stop=stop,
                stream=True
            )
            
            # 直接处理流式响应
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"GPT-4 API stream call failed: {str(e)}")
            yield f"Error: {str(e)}"

    def get_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> Optional[str]:
        """
        获取完整响应（向后兼容）
        """
        try:
            full_response = "".join(self.get_completion_stream(messages, **kwargs))
            return full_response
        except Exception as e:
            logger.error(f"GPT-4 API call failed: {str(e)}")
            return None
            
    def get_structured_response(
        self,
        messages: List[Dict[str, str]],
        split_lines: bool = True,
        remove_prefixes: bool = True,
        **kwargs
    ) -> List[str]:
        """
        获取结构化的响应（按行分割并清理）
        
        Args:
            messages: 消息列表
            split_lines: 是否按行分割
            remove_prefixes: 是否移除序号前缀
            **kwargs: 传递给 get_completion 的其他参数
            
        Returns:
            清理后的响应列表
        """
        response = self.get_completion(messages, **kwargs)
        if not response:
            return []
            
        if split_lines:
            # 按行分割并清理空白
            lines = [line.strip() for line in response.split('\n') if line.strip()]
            if remove_prefixes:
                # 移除可能的序号前缀（如 "1.", "2." 等）
                lines = [line.split('. ', 1)[-1] if '. ' in line else line for line in lines]
            return lines
            
        return [response] 