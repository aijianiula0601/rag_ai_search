import requests
import json
import os
from typing import Generator, Dict, List, Optional


#添加上级目录到sys.path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import OllamaConfig

class OllamaClient:
    def __init__(self, base_url=None):
        self.base_url = base_url or OllamaConfig.BASE_URL
        if self.base_url.endswith('/'):
            self.base_url = self.base_url[:-1]
        
    def get_models(self) -> List[Dict[str, str]]:
        """获取所有可用的 Ollama 模型"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.ok:
                data = response.json()
                return [
                    {'name': model['name'], 'display_name': model['name'].title()}
                    for model in data['models']
                ]
            else:
                raise Exception(f"Failed to fetch models: {response.text}")
        except Exception as e:
            raise Exception(f"Error getting models: {str(e)}")

    def generate_stream(self, prompt: str, model: str) -> Generator[Dict, None, None]:
        """使用指定模型生成流式响应"""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": True
                },
                stream=True
            )
            
            if not response.ok:
                raise Exception(f"Generation failed: {response.text}")
            
            # 首先yield一个空的sources列表
            yield {'type': 'sources', 'content': []}
            
            # 处理流式响应
            for line in response.iter_lines():
                if line:
                    try:
                        result = json.loads(line)
                        if 'response' in result:
                            yield {'type': 'content', 'content': result['response']}
                    except json.JSONDecodeError:
                        continue
                        
        except Exception as e:
            raise Exception(f"Error in generate_stream: {str(e)}")
    
    def generate(self, prompt: str, model: str) -> str:
        """使用指定模型生成非流式响应"""
        # 添加输入验证
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        if not model or not model.strip():
            raise ValueError("Model name cannot be empty")
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            if response.ok:
                result = response.json()
                return result.get('response', '')
            else:
                raise Exception(f"Generation failed: {response.text}")
                
        except Exception as e:
            raise Exception(f"Error in generate: {str(e)}") 
        
    def test_connection(self) -> bool:
        """测试与 Ollama 服务器的连接"""
        try:
            response = requests.get(f"{self.base_url}/api/version")
            return response.ok
        except Exception as e:
            raise Exception(f"Error in test_connection: {str(e)}")

if __name__ == "__main__":
    client = OllamaClient()
    
    # 测试连接
    if client.test_connection():
        print("Successfully connected to Ollama server")
    else:
        print("Failed to connect to Ollama server")
        exit(1)
        
    # 获取可用模型
    try:
        models = client.get_models()
        print("\nAvailable models:")
        for model in models:
            print(f"- {model['name']}")
    except Exception as e:
        print(f"Error getting models: {e}")
        
    # 测试生成
    test_prompt = "What is Python?"
    test_model = "llama3:8b"  # 使用默认模型
    
    print(f"\nTesting generation with prompt: '{test_prompt}'")
    try:
        response = client.generate(test_prompt, test_model)
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error in generation: {e}")