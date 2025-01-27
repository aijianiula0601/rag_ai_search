import os
import sys
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from core.query_processor import QueryProcessor
from core.search_engine import SearchEngine
from core.document_processor import DocumentProcessor
from core.llm_handler import LLMHandler
from models.query import Query
from models.response import Response
from models.document import Chunk
import logging
from config.settings import LogConfig
from typing import Dict, Generator

def setup_logging():
    """配置日志"""
    logging.basicConfig(
        level=getattr(logging, LogConfig.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LogConfig.LOG_FILE),
            logging.StreamHandler()
        ]
    )

class RAGSearch:
    def __init__(self):
        setup_logging()
        self.logger = logging.getLogger(__name__)
        self.query_processor = QueryProcessor()
        self.search_engine = SearchEngine()
        self.document_processor = DocumentProcessor()
        self.llm_handler = LLMHandler()
        
    def process_query_stream(self, user_query: str, llm_type: str = "ollama", model_name: str = "llama2") -> Generator[Dict, None, None]:
        """
        流式处理用户查询
        
        Args:
            user_query: 用户的查询文本
            llm_type: LLM类型 ("gpt" 或 "ollama")
            model_name: 模型名称 (对于ollama可以是"llama2"等，对于gpt可以是"gpt-4"等)
            
        Yields:
            包含答案片段或源文档的字典
        """
        try:
            # 创建查询对象
            query = Query(original_text=user_query)
            
            # 查询改写
            use_gpt4 = "gpt" in llm_type.lower()
            query = self.query_processor.rewrite_query(query, use_gpt4=use_gpt4, model_name=model_name)
            self.logger.info(f"改写后的查询: {query.rewritten_queries}")
            
            # 搜索结果获取
            all_results = []
            for q in query.rewritten_queries:
                results = self.search_engine.search(q)
                all_results.extend(results)
            self.logger.info(f"获取到 {len(all_results)} 条搜索结果")
            
            # 文档处理
            documents = self.document_processor.process_documents(all_results)
            self.logger.info(f"处理得到 {len(documents)} 个文档")
            
            # 重排序
            ranked_chunks = self.document_processor.rerank_chunks(
                query.original_text,
                documents
            )
            self.logger.info(f"重排序得到 {len(ranked_chunks)} 个相关文本块")
            
            # 使用指定的LLM类型和模型流式生成回答
            self.llm_handler = LLMHandler(llm_type=llm_type, model_name=model_name)
            for response in self.llm_handler.generate_response_stream(
                query.original_text, 
                ranked_chunks
            ):
                yield response
                
        except Exception as e:
            self.logger.error(f"Error processing query: {str(e)}")
            yield {"error": f"处理查询时发生错误: {str(e)}"}
    
    def process_query(self, user_query: str, llm_type: str = "ollama", model_name: str = "llama2") -> str:
        """
        处理用户查询（向后兼容的方法）
        
        Args:
            user_query: 用户的查询文本
            llm_type: LLM类型 ("gpt" 或 "ollama")
            model_name: 模型名称
        """
        try:
            # 收集所有响应
            full_response = {"answer": "", "sources": None}
            for response in self.process_query_stream(user_query, llm_type, model_name):
                if "content" in response:
                    full_response["answer"] += response["content"]
                elif "sources" in response:
                    full_response["sources"] = response["sources"]
                elif "error" in response:
                    return Response(
                        answer=response["error"],
                        supporting_chunks=[],
                        confidence_score=0.0
                    )
            
            # 创建完整的响应对象
            return Response(
                answer=full_response["answer"],
                supporting_chunks=[
                    Chunk(
                        text="",  # 这里可以根据需要添加文本内容
                        source_url=source["url"],
                        title=source["title"],
                        score=source["score"]
                    ) for source in (full_response["sources"] or [])
                ],
                confidence_score=max([s["score"] for s in full_response["sources"]]) if full_response["sources"] else 0.0
            )
            
        except Exception as e:
            self.logger.error(f"Error processing query: {str(e)}")
            return Response(
                answer=f"处理查询时发生错误: {str(e)}",
                supporting_chunks=[],
                confidence_score=0.0
            )

def main():
    rag_search = RAGSearch()
    print("\n欢迎使用 RAG 搜索系统！")
    print("输入您的问题，系统会搜索相关信息并生成回答。")
    print("输入 'quit' 退出系统。")
    
    while True:
        try:
            query = input("\n请输入您的问题: ").strip()
            if not query:
                print("请输入有效的问题！")
                continue
                
            if query.lower() == 'quit':
                print("感谢使用，再见！")
                break
                
            print("\n正在处理您的问题，请稍候...")
            
            # 流式显示结果
            sources_shown = False
            for response in rag_search.process_query_stream(query, llm_type="ollam", model_name="llama3:8b"):
                if "sources" in response and not sources_shown:
                    print("\n支持的文档:")
                    for source in response["sources"]:
                        print(f"- {source['title']} ({source['url']}) 相关度: {source['score']:.3f}")
                    sources_shown = True
                    max_score = max(s["score"] for s in response["sources"])
                    print(f"\n置信度: {max_score:.3f}")
                    print("\n回答:", end=" ", flush=True)
                elif "content" in response:
                    print(response["content"], end="", flush=True)
                elif "error" in response:
                    print(f"\n发生错误: {response['error']}")
            print()  # 打印换行
            
        except KeyboardInterrupt:
            print("\n\n程序被中断，正在退出...")
            break
        except Exception as e:
            print(f"\n发生错误: {str(e)}")
            print("请重试或输入 'quit' 退出")
if __name__ == "__main__":
    main() 