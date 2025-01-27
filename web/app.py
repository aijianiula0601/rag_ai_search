from flask import Flask, render_template, request, jsonify, Response, stream_with_context
import sys
import os
import json

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from main import RAGSearch
from utils.ollama_client import OllamaClient

app = Flask(__name__)
rag_search = RAGSearch()
ollama_client = OllamaClient()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/models', methods=['GET'])
def get_models():
    try:
        # 获取 Ollama 模型列表并添加 GPT-4
        ollama_models = ollama_client.get_models()
        all_models = [{'name': 'gpt', 'display_name': 'GPT'}] + ollama_models
        
        return jsonify({
            'success': True,
            'models': all_models
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error fetching models: {str(e)}'
        })

@app.route('/search', methods=['POST'])
def search():
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        model = data.get('model', 'gpt')
        
        if not query:
            return jsonify({
                'success': False,
                'error': '请输入有效的问题'
            })

        def generate():
            try:
                if model == "gpt":
                    llm_type = "gpt"
                else:
                    llm_type = "ollama"                    
                for response in rag_search.process_query_stream(query, llm_type=llm_type, model_name=model):
                    if 'sources' in response:
                        # 确保返回完整的来源信息
                        sources = [{
                            'url': source['url'],
                            'title': source['title'],
                            'score': source['score']
                        } for source in response['sources']]
                        yield f"data: {json.dumps({'sources': sources})}\n\n"
                    else:
                        yield f"data: {json.dumps(response)}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream'
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'处理查询时发生错误: {str(e)}'
        })

if __name__ == '__main__':
    app.run(host='202.168.100.165', debug=True, port=5000) 