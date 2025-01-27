from typing import List
from models.query import Query
from config.settings import ModelConfig, ProcessingConfig
from utils.gpt4_client import GPT4Client
from utils.ollama_client import OllamaClient
import logging

logger = logging.getLogger(__name__)

class QueryProcessor:
    def __init__(self):
        self.gpt4_client = GPT4Client()
        self.ollama_client = OllamaClient()
        self.processing_config = ProcessingConfig()
        
    def semantic_rewrite(self, query: str, use_gpt4: bool = False, model_name: str = "llama2") -> List[str]:
        """
        语义改写：生成与原始查询语义相同但表达方式不同的查询
        
        Args:
            query: 原始查询
            use_gpt4: 是否使用GPT-4
            model_name: 使用的模型名称（当use_gpt4为False时使用）
        """
        messages = [
            {
                "role": "system",
                "content": f"你是一个查询改写助手。你的任务是将用户的查询改写成不同的表达方式，但保持相同的语义。请生成{self.processing_config.SEMANTIC_REWRITE_LIMIT}个不同的表达方式，每行一个。"
            },
            {
                "role": "user",
                "content": f"请改写以下查询，保持语义相同但使用不同的表达方式：{query}"
            }
        ]
        
        try:
            if use_gpt4:
                # 使用GPT-4生成改写
                rewrites = self.gpt4_client.get_structured_response(
                    messages,
                    temperature=0.7
                )
            else:
                # 使用Ollama生成改写
                prompt = f"你是一个查询改写助手。请将以下查询改写成{self.processing_config.SEMANTIC_REWRITE_LIMIT}个不同的表达方式，保持语义相同，每行一个：\n\n{query}"
                response = self.ollama_client.generate(prompt, model_name)
                rewrites = [r.strip() for r in response.split('\n') if r.strip()]
            
            # 过滤掉与原始查询完全相同的结果
            return list(set([r for r in rewrites if r != query]))
            
        except Exception as e:
            logger.error(f"查询改写失败: {str(e)}")
            return [query]  # 出错时返回原始查询
        
    def semantic_expansion(self, query: str, use_gpt4: bool = False, model_name: str = "llama2") -> List[str]:
        """
        语义扩展：基于原始查询生成相关的子查询
        
        Args:
            query: 原始查询
            use_gpt4: 是否使用GPT-4
            model_name: 使用的模型名称（当use_gpt4为False时使用）
        """
        messages = [
            {
                "role": "system",
                "content": f"你是一个查询扩展助手。你的任务是基于用户的查询，生成更具体的子查询来探索不同方面。请生成{self.processing_config.SEMANTIC_EXPANSION_LIMIT}个相关的子查询，每行一个。注意：必须采用跟原始查询相同的语种输出。"
            },
            {
                "role": "user",
                "content": f"请基于以下查询生成更具体的子查询，以探索不同方面，原始查询：{query}"
            }
        ]
        
        try:
            if use_gpt4:
                # 使用GPT-4生成扩展
                expansions = self.gpt4_client.get_structured_response(
                    messages,
                    temperature=0.8
                )
            else:
                # 使用Ollama生成扩展
                prompt = f"你是一个查询扩展助手。请基于以下查询生成{self.processing_config.SEMANTIC_EXPANSION_LIMIT}个更具体的子查询，探索不同方面，每行一个，必须采用跟原始查询相同的语种输出：\n\n原始查询：{query}"
                response = self.ollama_client.generate(prompt, model_name)
                expansions = [e.strip() for e in response.split('\n') if e.strip()]
            
            # 过滤掉与原始查询完全相同的结果
            return list(set([e for e in expansions if e != query]))
            
        except Exception as e:
            logger.error(f"查询扩展失败: {str(e)}")
            return [query]  # 出错时返回原始查询
    
    def get_all_queries(self, original_query: str, use_gpt4: bool = False, model_name: str = "llama2") -> Query:
        """
        获取所有查询变体，包括原始查询、语义改写和语义扩展
        
        Args:
            original_query: 原始查询
            use_gpt4: 是否使用GPT-4
            model_name: 使用的模型名称
        """
        all_queries = [original_query]  # 始终包含原始查询
        
        # 获取语义改写的查询
        semantic_rewrites = self.semantic_rewrite(original_query, use_gpt4, model_name)
        if semantic_rewrites:
            all_queries.extend(semantic_rewrites)
            logger.info(f"Generated {len(semantic_rewrites)} semantic rewrites")
            logger.debug(f"Semantic rewrites: {semantic_rewrites}")
        
        # 获取语义扩展的查询
        expanded_queries = self.semantic_expansion(original_query, use_gpt4, model_name)
        if expanded_queries:
            all_queries.extend(expanded_queries)
            logger.info(f"Generated {len(expanded_queries)} query expansions")
            logger.debug(f"Query expansions: {expanded_queries}")
        
        # 创建Query对象
        query = Query(original_text=original_query)
        query.rewritten_queries = list(set(all_queries))  # 去重
        
        logger.info(f"Generated total {len(query.rewritten_queries)} queries")
        return query
    
    def rewrite_query(self, query: Query, use_gpt4: bool = False, model_name: str = "llama2") -> Query:
        """
        主要的查询处理函数，保持向后兼容
        
        Args:
            query: 查询对象
            use_gpt4: 是否使用GPT-4
            model_name: 使用的模型名称
        """
        return self.get_all_queries(query.original_text, use_gpt4, model_name) 